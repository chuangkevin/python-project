#!/usr/bin/env python3
"""
Pi Camera V5647 色彩校正系統
針對戶外拍攝場景自動優化色彩表現
"""

import cv2
import numpy as np
import json
import os
from typing import Dict, Tuple, Optional
from pathlib import Path

class CameraColorCalibration:
    """相機色彩校正系統"""
    
    def __init__(self):
        self.config_path = Path(__file__).parent / "camera_profiles.json"
        self.camera_profiles = self._load_camera_profiles()
        self.current_profile = "pi_camera_v5647"
        
    def _load_camera_profiles(self) -> Dict:
        """載入相機色彩配置檔案"""
        default_profiles = {
            "pi_camera_v5647": {
                "name": "Raspberry Pi Camera V5647 (OV5647)",
                "sensor_type": "OmniVision OV5647",
                "color_correction_matrix": [
                    [1.05, -0.08, 0.03],  # 修正紅色通道
                    [-0.02, 0.92, 0.10],  # 降低綠色優勢
                    [0.05, -0.15, 1.10]   # 增強藍色，修正偏紫問題
                ],
                "white_balance_gains": [1.0, 0.95, 1.08],  # R, G, B 增益
                "saturation_adjustment": 1.05,  # 輕微增加飽和度
                "contrast_curve": "mild_s_curve",
                "outdoor_optimization": {
                    "sky_blue_correction": True,
                    "vegetation_green_enhancement": True,
                    "skin_tone_protection": True
                },
                "exposure_compensation": 0.1,  # EV
                "gamma_correction": 1.1
            },
            "generic_camera": {
                "name": "Generic Camera",
                "color_correction_matrix": [
                    [1.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0],
                    [0.0, 0.0, 1.0]
                ],
                "white_balance_gains": [1.0, 1.0, 1.0],
                "saturation_adjustment": 1.0,
                "contrast_curve": "linear",
                "outdoor_optimization": {
                    "sky_blue_correction": False,
                    "vegetation_green_enhancement": False,
                    "skin_tone_protection": False
                },
                "exposure_compensation": 0.0,
                "gamma_correction": 1.0
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_profiles = json.load(f)
                # 合併預設和載入的配置
                default_profiles.update(loaded_profiles)
            except Exception as e:
                print(f"⚠️  載入配置檔案失敗，使用預設設定: {e}")
        
        return default_profiles
    
    def save_camera_profiles(self):
        """儲存相機配置到檔案"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.camera_profiles, f, indent=2, ensure_ascii=False)
            print(f"✅ 相機配置已儲存到: {self.config_path}")
        except Exception as e:
            print(f"❌ 儲存配置檔案失敗: {e}")
    
    def set_camera_profile(self, profile_name: str) -> bool:
        """設定當前使用的相機配置"""
        if profile_name in self.camera_profiles:
            self.current_profile = profile_name
            print(f"📷 切換到相機配置: {self.camera_profiles[profile_name]['name']}")
            return True
        else:
            print(f"❌ 找不到相機配置: {profile_name}")
            return False
    
    def apply_color_correction(self, image: np.ndarray, 
                             scene_analysis: bool = True) -> np.ndarray:
        """
        套用完整的色彩校正
        
        Args:
            image: 輸入圖像 (BGR)
            scene_analysis: 是否進行場景分析自動調整
        
        Returns:
            校正後的圖像
        """
        if image is None or image.size == 0:
            return image
            
        profile = self.camera_profiles[self.current_profile]
        
        # 1. 基礎色彩矩陣校正
        corrected = self._apply_color_matrix(image, profile["color_correction_matrix"])
        
        # 2. 白平衡調整
        corrected = self._apply_white_balance(corrected, profile["white_balance_gains"])
        
        # 3. 場景自適應調整
        if scene_analysis:
            corrected = self._scene_adaptive_correction(corrected, profile)
        
        # 4. 飽和度調整
        corrected = self._adjust_saturation(corrected, profile["saturation_adjustment"])
        
        # 5. 對比度曲線
        corrected = self._apply_contrast_curve(corrected, profile["contrast_curve"])
        
        # 6. Gamma 校正
        corrected = self._apply_gamma_correction(corrected, profile["gamma_correction"])
        
        # 7. 戶外場景優化
        if profile["outdoor_optimization"]["sky_blue_correction"]:
            corrected = self._correct_sky_blue(corrected)
        
        if profile["outdoor_optimization"]["vegetation_green_enhancement"]:
            corrected = self._enhance_vegetation_green(corrected)
        
        if profile["outdoor_optimization"]["skin_tone_protection"]:
            corrected = self._protect_skin_tones(corrected)
        
        return corrected
    
    def _apply_color_matrix(self, image: np.ndarray, matrix: list) -> np.ndarray:
        """套用色彩校正矩陣"""
        if len(matrix) != 3 or len(matrix[0]) != 3:
            return image
            
        # 轉換為浮點數進行計算
        img_float = image.astype(np.float32) / 255.0
        
        # 重新排列為 (pixel_count, 3) 進行矩陣運算
        h, w, c = img_float.shape
        img_reshaped = img_float.reshape(-1, 3)
        
        # 套用色彩矩陣 (BGR 順序)
        correction_matrix = np.array(matrix, dtype=np.float32)
        img_corrected = img_reshaped @ correction_matrix.T
        
        # 限制範圍並轉回原格式
        img_corrected = np.clip(img_corrected, 0, 1)
        img_corrected = img_corrected.reshape(h, w, c)
        
        return (img_corrected * 255).astype(np.uint8)
    
    def _apply_white_balance(self, image: np.ndarray, gains: list) -> np.ndarray:
        """套用白平衡增益"""
        if len(gains) != 3:
            return image
            
        img_float = image.astype(np.float32)
        
        # 套用 BGR 增益
        img_float[:, :, 0] *= gains[2]  # B
        img_float[:, :, 1] *= gains[1]  # G  
        img_float[:, :, 2] *= gains[0]  # R
        
        return np.clip(img_float, 0, 255).astype(np.uint8)
    
    def _scene_adaptive_correction(self, image: np.ndarray, profile: dict) -> np.ndarray:
        """場景自適應校正"""
        # 分析圖像特徵
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 檢測天空區域（高亮度、藍色調）
        sky_mask = (hsv[:, :, 2] > 180) & (hsv[:, :, 0] > 90) & (hsv[:, :, 0] < 130)
        sky_ratio = np.sum(sky_mask) / (image.shape[0] * image.shape[1])
        
        # 檢測植被（綠色調）
        vegetation_mask = (hsv[:, :, 0] > 35) & (hsv[:, :, 0] < 85) & (hsv[:, :, 1] > 50)
        vegetation_ratio = np.sum(vegetation_mask) / (image.shape[0] * image.shape[1])
        
        corrected = image.copy()
        
        # 戶外場景偵測
        if sky_ratio > 0.2 or vegetation_ratio > 0.3:
            # 戶外場景：增加對比度，輕微降低曝光
            corrected = self._adjust_exposure(corrected, -0.05)
            corrected = self._enhance_contrast(corrected, 1.1)
            
        return corrected
    
    def _adjust_saturation(self, image: np.ndarray, factor: float) -> np.ndarray:
        """調整飽和度"""
        if factor == 1.0:
            return image
            
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] *= factor
        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
        
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    
    def _apply_contrast_curve(self, image: np.ndarray, curve_type: str) -> np.ndarray:
        """套用對比度曲線"""
        if curve_type == "linear":
            return image
        elif curve_type == "mild_s_curve":
            img_float = image.astype(np.float32) / 255.0
            
            # 輕微 S 曲線
            def s_curve(x):
                return np.where(x < 0.5, 
                              2 * x * x, 
                              1 - 2 * (1 - x) * (1 - x))
            
            # 套用到每個通道
            for i in range(3):
                img_float[:, :, i] = s_curve(img_float[:, :, i]) * 0.3 + img_float[:, :, i] * 0.7
            
            return (np.clip(img_float, 0, 1) * 255).astype(np.uint8)
        
        return image
    
    def _apply_gamma_correction(self, image: np.ndarray, gamma: float) -> np.ndarray:
        """套用 Gamma 校正"""
        if gamma == 1.0:
            return image
            
        # 建立 Gamma 查找表
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 
                         for i in np.arange(0, 256)]).astype("uint8")
        
        return cv2.LUT(image, table)
    
    def _correct_sky_blue(self, image: np.ndarray) -> np.ndarray:
        """修正天空藍色偏紫問題"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # 偵測藍天區域
        blue_sky_mask = (hsv[:, :, 0] > 100) & (hsv[:, :, 0] < 130) & \
                       (hsv[:, :, 1] > 50) & (hsv[:, :, 2] > 150)
        
        # 調整色相，減少紫色偏移
        hsv[blue_sky_mask, 0] = hsv[blue_sky_mask, 0] * 0.95
        
        return cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
    
    def _enhance_vegetation_green(self, image: np.ndarray) -> np.ndarray:
        """增強植被綠色"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # 偵測綠色植被
        green_mask = (hsv[:, :, 0] > 35) & (hsv[:, :, 0] < 85) & (hsv[:, :, 1] > 30)
        
        # 輕微增強綠色飽和度
        hsv[green_mask, 1] = hsv[green_mask, 1] * 1.1
        
        return cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
    
    def _protect_skin_tones(self, image: np.ndarray) -> np.ndarray:
        """保護膚色不被過度調整"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # 偵測膚色範圍
        skin_mask1 = (hsv[:, :, 0] >= 0) & (hsv[:, :, 0] <= 25) & \
                    (hsv[:, :, 1] >= 30) & (hsv[:, :, 1] <= 170) & \
                    (hsv[:, :, 2] >= 80) & (hsv[:, :, 2] <= 255)
        
        skin_mask2 = (hsv[:, :, 0] >= 165) & (hsv[:, :, 0] <= 180) & \
                    (hsv[:, :, 1] >= 30) & (hsv[:, :, 1] <= 170) & \
                    (hsv[:, :, 2] >= 80) & (hsv[:, :, 2] <= 255)
        
        skin_mask = skin_mask1 | skin_mask2
        
        # 對膚色區域進行保護性調整
        hsv[skin_mask, 1] = hsv[skin_mask, 1] * 0.95  # 輕微降低飽和度
        
        return cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
    
    def _adjust_exposure(self, image: np.ndarray, ev_compensation: float) -> np.ndarray:
        """曝光補償"""
        if ev_compensation == 0:
            return image
            
        # EV 轉換為增益係數
        gain = 2 ** ev_compensation
        img_float = image.astype(np.float32) * gain
        
        return np.clip(img_float, 0, 255).astype(np.uint8)
    
    def _enhance_contrast(self, image: np.ndarray, factor: float) -> np.ndarray:
        """增強對比度"""
        if factor == 1.0:
            return image
            
        img_float = image.astype(np.float32) / 255.0
        img_float = (img_float - 0.5) * factor + 0.5
        
        return (np.clip(img_float, 0, 1) * 255).astype(np.uint8)
    
    def get_current_profile_info(self) -> dict:
        """取得當前配置資訊"""
        return self.camera_profiles[self.current_profile]
    
    def analyze_image_characteristics(self, image: np.ndarray) -> dict:
        """分析圖像特徵，提供校正建議"""
        if image is None or image.size == 0:
            return {}
            
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # 基本統計
        brightness = np.mean(hsv[:, :, 2])
        saturation = np.mean(hsv[:, :, 1])
        
        # 色彩分布
        blue_ratio = np.sum((hsv[:, :, 0] > 100) & (hsv[:, :, 0] < 130)) / (image.shape[0] * image.shape[1])
        green_ratio = np.sum((hsv[:, :, 0] > 35) & (hsv[:, :, 0] < 85)) / (image.shape[0] * image.shape[1])
        
        # 場景判斷
        scene_type = "unknown"
        if blue_ratio > 0.3:
            scene_type = "outdoor_sky"
        elif green_ratio > 0.4:
            scene_type = "outdoor_vegetation"
        elif brightness < 100:
            scene_type = "low_light"
        elif brightness > 200:
            scene_type = "high_key"
        else:
            scene_type = "balanced"
        
        return {
            "brightness": float(brightness),
            "saturation": float(saturation),
            "blue_ratio": float(blue_ratio),
            "green_ratio": float(green_ratio),
            "scene_type": scene_type,
            "recommended_adjustments": self._get_scene_recommendations(scene_type)
        }
    
    def _get_scene_recommendations(self, scene_type: str) -> dict:
        """根據場景類型提供調整建議"""
        recommendations = {
            "outdoor_sky": {
                "exposure_compensation": -0.1,
                "saturation_boost": 1.1,
                "blue_correction": True
            },
            "outdoor_vegetation": {
                "exposure_compensation": 0.0,
                "saturation_boost": 1.05,
                "green_enhancement": True
            },
            "low_light": {
                "exposure_compensation": 0.2,
                "noise_reduction": True,
                "shadow_lift": 0.1
            },
            "high_key": {
                "exposure_compensation": -0.15,
                "highlight_protection": True,
                "contrast_boost": 1.1
            },
            "balanced": {
                "exposure_compensation": 0.0,
                "saturation_boost": 1.0,
                "standard_processing": True
            }
        }
        
        return recommendations.get(scene_type, recommendations["balanced"])

# 使用範例
if __name__ == "__main__":
    # 建立校正系統
    calibration = CameraColorCalibration()
    
    # 測試圖像處理
    test_image_path = "test_image.jpg"
    if os.path.exists(test_image_path):
        image = cv2.imread(test_image_path)
        
        # 分析圖像特徵
        analysis = calibration.analyze_image_characteristics(image)
        print(f"📊 圖像分析結果: {analysis}")
        
        # 套用色彩校正
        corrected = calibration.apply_color_correction(image, scene_analysis=True)
        
        # 儲存結果
        cv2.imwrite("corrected_image.jpg", corrected)
        print("✅ 色彩校正完成，結果已儲存")
    else:
        print("⚠️  找不到測試圖像，請提供 test_image.jpg")
