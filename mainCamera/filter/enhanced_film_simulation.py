"""
增強軟片模擬引擎
Enhanced Film Simulation Engine

支援最新的軟片模擬技術和專業攝影師的配方
"""

import cv2
import numpy as np
from PIL import Image
from typing import Union, Tuple, Dict, Any
import random

class EnhancedFilmSimulation:
    """增強版軟片模擬引擎"""
    
    def __init__(self):
        """初始化軟片模擬系統"""
        self.simulations = {
            # === 經典 Fujifilm 軟片 ===
            'PROVIA': self._provia_enhanced,
            'VELVIA': self._velvia_enhanced, 
            'ASTIA': self._astia_enhanced,
            'CLASSIC_CHROME': self._classic_chrome_enhanced,
            'PRO_NEG_HI': self._pro_neg_hi,
            'PRO_NEG_STD': self._pro_neg_std,
            'CLASSIC_NEG': self._classic_neg,
            'ETERNA': self._eterna_enhanced,
            'ACROS': self._acros_enhanced,
            'MONO_CHROME': self._monochrome_enhanced,
            
            # === 經典 Kodak 軟片 ===
            'KODACHROME_64': self._kodachrome_64,
            'KODACHROME_25': self._kodachrome_25,
            'KODAK_PORTRA_400': self._portra_400_v2,
            'KODAK_PORTRA_160': self._portra_160_v2,
            'KODAK_PORTRA_800': self._portra_800_v3,
            'KODAK_GOLD_200': self._kodak_gold_200,
            'KODAK_ULTRAMAX_400': self._ultramax_400,
            'KODAK_EKTAR_100': self._ektar_100,
            'KODAK_TRI_X_400': self._tri_x_400,
            'KODAK_TMAX_100': self._tmax_100,
            'KODAK_TMAX_3200': self._tmax_3200,
            
            # === Fujicolor 系列 ===
            'FUJICOLOR_C200': self._fujicolor_c200,
            'FUJICOLOR_SUPERIA_400': self._superia_400,
            'FUJICOLOR_SUPERIA_1600': self._superia_1600,
            'FUJICOLOR_NATURA_1600': self._natura_1600,
            'FUJICOLOR_REALA_100': self._reala_100,
            'REALA_ACE': self._reala_ace_enhanced,
            
            # === 電影膠片 ===
            'CINESTILL_800T': self._cinestill_800t,
            'CINESTILL_400D': self._cinestill_400d,
            'KODAK_VISION3_250D': self._vision3_250d,
            'KODAK_VISION3_500T': self._vision3_500t,
            
            # === 復古風格 ===
            'VINTAGE_KODACHROME': self._vintage_kodachrome,
            'NOSTALGIC_NEGATIVE': self._nostalgic_negative,
            'SUMMER_1960': self._summer_1960,
            'CALIFORNIA_SUMMER': self._california_summer,
            'PACIFIC_BLUES': self._pacific_blues,
            'VINTAGE_BRONZE': self._vintage_bronze,
            
            # === 特殊效果 ===
            'REDSCALE': self._redscale,
            'CROSS_PROCESS': self._cross_process,
            'BLEACH_BYPASS': self._bleach_bypass,
            'INFRARED_BW': self._infrared_bw
        }
    
    def apply_simulation(self, image: Union[str, Image.Image, np.ndarray], 
                        simulation: str, **kwargs) -> np.ndarray:
        """套用軟片模擬"""
        # 載入圖像
        if isinstance(image, str):
            img = cv2.imread(image)
            if img is None:
                raise ValueError(f"無法載入圖像: {image}")
        elif isinstance(image, Image.Image):
            img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        elif isinstance(image, np.ndarray):
            img = image.copy()
        else:
            raise ValueError("不支援的圖像格式")
        
        # 檢查軟片模擬是否存在
        if simulation not in self.simulations:
            available = ', '.join(self.simulations.keys())
            raise ValueError(f"軟片模擬 '{simulation}' 不存在。可用選項: {available}")
        
        # 套用軟片模擬
        return self.simulations[simulation](img, **kwargs)
    
    def get_available_simulations(self) -> Dict[str, str]:
        """取得所有可用的軟片模擬及其描述"""
        descriptions = {
            'PROVIA': '標準專業反轉片 - 平衡自然色彩',
            'VELVIA': '鮮豔反轉片 - 高飽和度風景片',
            'ASTIA': '柔和人像片 - 膚色優化',
            'CLASSIC_CHROME': '經典紀實 - 復古膠片質感，完美的紀實攝影風格',
            'PRO_NEG_HI': '專業負片高調 - 明亮色彩',
            'PRO_NEG_STD': '專業負片標準 - 自然表現',
            'CLASSIC_NEG': '經典負片 - 復古情懷',
            'ETERNA': '電影膠片 - 柔和色調',
            'ACROS': '黑白銀鹽 - 高質感單色',
            'MONO_CHROME': '單色 - 經典黑白',
            'KODACHROME_64': 'Kodachrome 64 - 經典色彩',
            'KODACHROME_25': 'Kodachrome 25 - 細膩質感',
            'KODAK_PORTRA_400': 'Portra 400 v2 - 專業人像',
            'KODAK_PORTRA_160': 'Portra 160 v2 - 自然膚色',
            'KODAK_PORTRA_800': 'Portra 800 v3 - 高感光人像',
            'KODAK_GOLD_200': 'Gold 200 - 溫暖金黃',
            'KODAK_ULTRAMAX_400': 'Ultramax 400 - 日常拍攝',
            'KODAK_EKTAR_100': 'Ektar 100 - 風景專用',
            'KODAK_TRI_X_400': 'Tri-X 400 - 經典黑白',
            'KODAK_TMAX_100': 'T-Max 100 - 高解析黑白',
            'KODAK_TMAX_3200': 'T-Max P3200 - 高感光黑白',
            'FUJICOLOR_C200': 'C200 - 經濟型彩色',
            'FUJICOLOR_SUPERIA_400': 'Superia 400 - 萬用彩色',
            'FUJICOLOR_SUPERIA_1600': 'Superia 1600 - 高感光',
            'FUJICOLOR_NATURA_1600': 'Natura 1600 - 自然色彩',
            'FUJICOLOR_REALA_100': 'Reala 100 - 真實色彩',
            'REALA_ACE': 'Reala Ace - 增強版真實色彩',
            'CINESTILL_800T': 'CineStill 800T - 鎢絲燈電影',
            'CINESTILL_400D': 'CineStill 400D - 日光電影',
            'KODAK_VISION3_250D': 'Vision3 250D - 專業電影',
            'KODAK_VISION3_500T': 'Vision3 500T - 室內電影',
            'VINTAGE_KODACHROME': '復古 Kodachrome',
            'NOSTALGIC_NEGATIVE': '懷舊負片',
            'SUMMER_1960': '1960夏日',
            'CALIFORNIA_SUMMER': '加州夏日',
            'PACIFIC_BLUES': '太平洋藍調',
            'VINTAGE_BRONZE': '復古青銅',
            'REDSCALE': '紅片效果',
            'CROSS_PROCESS': '交叉沖洗',
            'BLEACH_BYPASS': '漂白跳過',
            'INFRARED_BW': '紅外線黑白'
        }
        return descriptions
    
    # === 工具函數 ===
    
    def _apply_lut(self, img: np.ndarray, lut: np.ndarray) -> np.ndarray:
        """應用查找表"""
        return cv2.LUT(img, lut)
    
    def _film_grain(self, img: np.ndarray, strength: float = 0.1, size: float = 1.0) -> np.ndarray:
        """添加膠片顆粒"""
        grain = np.random.normal(0, strength * 255, img.shape)
        if size != 1.0:
            # 調整顆粒大小
            h, w = img.shape[:2]
            grain_small = cv2.resize(grain, (int(w * size), int(h * size)))
            grain = cv2.resize(grain_small, (w, h))
        
        result = img.astype(np.float32) + grain
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def _color_temperature(self, img: np.ndarray, temp: int) -> np.ndarray:
        """調整色溫 (3000K=暖色, 6500K=中性, 10000K=冷色)"""
        if temp == 6500:
            return img  # 中性色溫
        
        img_float = img.astype(np.float32) / 255.0
        
        if temp < 6500:  # 暖色
            factor = (6500 - temp) / 3500.0
            img_float[:,:,0] *= (1.0 - factor * 0.3)  # 減少藍色
            img_float[:,:,2] *= (1.0 + factor * 0.2)  # 增加紅色
        else:  # 冷色
            factor = (temp - 6500) / 3500.0
            img_float[:,:,0] *= (1.0 + factor * 0.3)  # 增加藍色
            img_float[:,:,2] *= (1.0 - factor * 0.2)  # 減少紅色
        
        return np.clip(img_float * 255, 0, 255).astype(np.uint8)
    
    def _vintage_fade(self, img: np.ndarray, intensity: float = 0.3) -> np.ndarray:
        """復古褪色效果"""
        img_float = img.astype(np.float32) / 255.0
        
        # 提升黑階
        img_float = img_float * (1.0 - intensity * 0.3) + intensity * 0.3
        
        # 降低對比度
        mean = np.mean(img_float)
        img_float = (img_float - mean) * (1.0 - intensity * 0.4) + mean
        
        return np.clip(img_float * 255, 0, 255).astype(np.uint8)
    
    def _split_toning(self, img: np.ndarray, highlight_color: Tuple[float, float, float],
                     shadow_color: Tuple[float, float, float], intensity: float = 0.3) -> np.ndarray:
        """分離調色"""
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # 計算亮度遮罩
        brightness = img_hsv[:, :, 2] / 255.0
        shadow_mask = np.power(1.0 - brightness, 2)
        highlight_mask = np.power(brightness, 2)
        
        # 應用顏色偏移
        for i in range(3):
            shadow_shift = shadow_color[i] * shadow_mask * intensity
            highlight_shift = highlight_color[i] * highlight_mask * intensity
            img_hsv[:, :, i] += (shadow_shift + highlight_shift)
        
        img_hsv = np.clip(img_hsv, 0, 255)
        return cv2.cvtColor(img_hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    
    def _tone_curve(self, img: np.ndarray, curve_type: str = 'film') -> np.ndarray:
        """色調曲線調整"""
        x = np.linspace(0, 255, 256)
        
        if curve_type == 'film':
            # 經典膠片S曲線
            lut = np.clip(255 * np.power(x / 255.0, 0.9), 0, 255).astype(np.uint8)
        elif curve_type == 'vintage':
            # 復古曲線 - 提升黑階，壓縮高光
            normalized = x / 255.0
            lut = np.clip(255 * (normalized * 0.85 + 0.15), 0, 255).astype(np.uint8)
        elif curve_type == 'high_contrast':
            # 高對比度S曲線
            normalized = x / 255.0
            lut = np.clip(255 * (0.5 + 0.5 * np.tanh(4 * (normalized - 0.5))), 0, 255).astype(np.uint8)
        else:
            return img
        
        return cv2.LUT(img, lut)
    
    def _protect_skin_tones(self, img: np.ndarray) -> np.ndarray:
        """膚色保護算法 - 保持膚色自然"""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # 定義膚色範圍（HSV）
        # 膚色通常在 0-30 和 340-360 度（在 OpenCV 中是 0-15 和 170-180）
        h = hsv[:, :, 0]
        s = hsv[:, :, 1] / 255.0
        v = hsv[:, :, 2] / 255.0
        
        # 創建膚色遮罩
        skin_mask1 = (h >= 0) & (h <= 15) & (s >= 0.2) & (s <= 0.8) & (v >= 0.3) & (v <= 0.9)
        skin_mask2 = (h >= 170) & (h <= 180) & (s >= 0.2) & (s <= 0.8) & (v >= 0.3) & (v <= 0.9)
        skin_mask = skin_mask1 | skin_mask2
        
        # 對膚色區域進行保護性調整
        # 減少極端的色相偏移
        h_protected = h.copy()
        h_protected[skin_mask] = h[skin_mask] * 0.95  # 輕微調整色相
        
        # 保護膚色的飽和度
        s_protected = s.copy() * 255
        s_protected[skin_mask] = s[skin_mask] * 255 * 1.05  # 略微增強膚色飽和度
        
        hsv[:, :, 0] = h_protected
        hsv[:, :, 1] = np.clip(s_protected, 0, 255)
        
        return cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
    
    # === Fujifilm 軟片模擬 ===
    
    def _provia_enhanced(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """增強版 Provia"""
        # 基礎色調調整
        result = self._tone_curve(img, 'film')
        
        # Provia 特有的自然飽和度
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 1.05  # 輕微增強飽和度
        hsv[:,:,2] *= 1.02  # 微調亮度
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # 膚色優化
        result = self._split_toning(result, (5, 2, -3), (-2, 1, 3), 0.15)
        
        return result
    
    def _velvia_enhanced(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """增強版 Velvia - 大幅提升亮度的鮮豔風格"""
        # 大幅提升整體亮度
        result = img.astype(np.float32)
        result = np.power(result / 255.0, 0.75) * 255  # 強力 gamma 校正
        
        # Velvia 特有的高飽和度
        hsv = cv2.cvtColor(result.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 1.4   # 大幅增強飽和度
        hsv[:,:,2] *= 1.15  # 增加明度
        
        # 特別增強綠色和藍色
        green_mask = (hsv[:,:,0] >= 40) & (hsv[:,:,0] <= 80)
        blue_mask = (hsv[:,:,0] >= 100) & (hsv[:,:,0] <= 130)
        hsv[green_mask, 1] *= 1.2
        hsv[blue_mask, 1] *= 1.2
        
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # 對比度增強
        result = self._tone_curve(result, 'high_contrast')
        
        return result
    
    def _astia_enhanced(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """增強版 Astia - 柔和人像優化"""
        # 柔和的色調曲線
        result = self._tone_curve(img, 'film')
        
        # 膚色優化
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # 人像膚色範圍優化
        skin_mask = ((hsv[:,:,0] >= 5) & (hsv[:,:,0] <= 25)) & (hsv[:,:,1] >= 30)
        hsv[skin_mask, 1] *= 0.9   # 降低膚色飽和度
        hsv[skin_mask, 2] *= 1.05  # 提亮膚色
        
        # 整體柔和調整
        hsv[:,:,1] *= 0.95  # 略微降低整體飽和度
        
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # 柔和分離調色
        result = self._split_toning(result, (3, 1, -2), (-1, 2, 4), 0.2)
        
        return result
    
    def _classic_chrome_enhanced(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """增強版 Classic Chrome - 經典紀實風格
        
        Classic Chrome 的核心特色：
        1. 紀實攝影風格，中性色調
        2. 獨特的高光卷掃和陰影細節保留
        3. 去飽和但保持色彩分離度
        4. 微妙的冷調偏移
        5. 柔和的對比度曲線
        """
        # 最簡化的處理 - 只降低飽和度和微調色調
        result = img.copy()
        
        # === 飽和度控制 - Classic Chrome 的核心 ===
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # 降低飽和度 - Classic Chrome 的標誌性特徵
        hsv[:, :, 1] = hsv[:, :, 1] * 0.75  # 降低到 75%
        
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # === 輕微冷調調整 ===
        result_float = result.astype(np.float32)
        
        # 微妙的色調平衡 - Classic Chrome 的冷調特色
        result_float[:, :, 0] = np.clip(result_float[:, :, 0] * 1.02, 0, 255)  # 輕微增加藍色
        result_float[:, :, 1] = np.clip(result_float[:, :, 1] * 0.98, 0, 255)  # 輕微減少綠色
        result_float[:, :, 2] = np.clip(result_float[:, :, 2] * 0.99, 0, 255)  # 輕微減少紅色
        
        # === 輕微對比度調整 ===
        # 使用簡單的對比度增強
        result_float = result_float / 255.0
        result_float = (result_float - 0.5) * 1.05 + 0.5  # 輕微增加對比度
        
        result = np.clip(result_float * 255, 0, 255).astype(np.uint8)
        
        return result
    
    def _pro_neg_hi(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Pro Neg Hi - 專業負片高調"""
        # 提升整體亮度
        result = self._tone_curve(img, 'film')
        
        # 負片特有的柔和對比
        result_float = result.astype(np.float32) / 255.0
        result_float = np.power(result_float, 0.85)
        result = (result_float * 255).astype(np.uint8)
        
        # 色彩偏移
        result = self._split_toning(result, (2, 1, -2), (-1, 1, 2), 0.2)
        
        return result
    
    def _pro_neg_std(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Pro Neg Std - 專業負片標準"""
        # 標準負片處理
        result = self._tone_curve(img, 'film')
        
        # 輕微色彩調整
        result = self._split_toning(result, (1, 0, -1), (0, 1, 1), 0.15)
        
        return result
    
    def _classic_neg(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Classic Negative - 經典負片風格"""
        # 復古負片處理
        result = self._vintage_fade(img, 0.2)
        
        # 經典負片的色彩特性
        result = self._split_toning(result, (5, 2, -3), (-2, 3, 5), 0.25)
        
        # 柔和的飽和度
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 0.9
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return result
    
    def _eterna_enhanced(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """增強版 Eterna - 電影膠片風格"""
        # 電影膠片的柔和曲線
        result = self._tone_curve(img, 'film')
        
        # Eterna 特有的色彩特性
        result = self._split_toning(result, (3, -1, -4), (-2, 2, 6), 0.3)
        
        # 降低對比度和飽和度
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 0.8   # 大幅降低飽和度
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # 輕微褪色效果
        result = self._vintage_fade(result, 0.15)
        
        return result
    
    def _acros_enhanced(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """增強版 Acros - 高質感黑白"""
        # 轉換為黑白
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Acros 特有的色調分離
        # 基於原始顏色通道的權重混合
        b, g, r = cv2.split(img.astype(np.float32))
        gray_weighted = (r * 0.3 + g * 0.6 + b * 0.1)  # Acros 權重
        gray = np.clip(gray_weighted, 0, 255).astype(np.uint8)
        
        # 銀鹽質感的對比度調整
        gray = self._tone_curve(gray, 'high_contrast')
        
        # 轉回三通道
        result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        # 輕微的暖調
        result = self._color_temperature(result, 6800)
        
        return result
    
    def _monochrome_enhanced(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """增強版單色"""
        # 標準黑白轉換
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 經典黑白對比度
        gray = self._tone_curve(gray, 'film')
        
        # 轉回三通道
        result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        return result
    
    def _reala_ace_enhanced(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """增強版 Reala Ace - 真實色彩再現"""
        # 大幅提升整體亮度
        result = img.astype(np.float32)
        result = np.power(result / 255.0, 0.8) * 255  # 強力亮度提升
        
        # 真實色彩調整
        hsv = cv2.cvtColor(result.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 1.1   # 適度增強飽和度
        hsv[:,:,2] *= 1.12  # 進一步提升明度
        
        # 膚色優化
        skin_mask = ((hsv[:,:,0] >= 5) & (hsv[:,:,0] <= 25))
        hsv[skin_mask, 1] *= 0.95
        hsv[skin_mask, 2] *= 1.05
        
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # 輕微對比度增強
        result = self._tone_curve(result, 'film')
        
        return result
    
    # === Kodak 軟片模擬 ===
    
    def _kodachrome_64(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Kodachrome 64 - 經典色彩"""
        # Kodachrome 特有的色彩科學
        result = self._color_temperature(img, 5600)  # 略微偏冷
        
        # 特有的飽和度和對比度
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 1.25  # 高飽和度
        
        # Kodachrome 特有的紅色增強
        red_mask = ((hsv[:,:,0] >= 0) & (hsv[:,:,0] <= 20)) | (hsv[:,:,0] >= 160)
        hsv[red_mask, 1] *= 1.2
        
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # 經典對比度
        result = self._tone_curve(result, 'high_contrast')
        
        # 輕微膠片顆粒
        result = self._film_grain(result, 0.02)
        
        return result
    
    def _kodachrome_25(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Kodachrome 25 - 細膩質感"""
        # 基於 Kodachrome 64 但更細膩
        result = self._kodachrome_64(img)
        
        # 更精細的處理
        result = self._film_grain(result, 0.01, 0.5)  # 更細的顆粒
        
        return result
    
    def _portra_400_v2(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Kodak Portra 400 v2 - 專業人像"""
        # Portra 的膚色科學
        result = self._color_temperature(img, 6200)  # 略微偏暖
        
        # 膚色優化
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # 人像膚色範圍優化
        skin_mask = ((hsv[:,:,0] >= 8) & (hsv[:,:,0] <= 25))
        hsv[skin_mask, 1] *= 0.85  # 膚色降低飽和度
        hsv[skin_mask, 2] *= 1.05  # 膚色提亮
        
        # 整體柔和飽和度
        hsv[:,:,1] *= 0.95
        
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # Portra 特有的分離調色
        result = self._split_toning(result, (5, 2, -3), (-2, 1, 4), 0.2)
        
        # 膠片顆粒
        result = self._film_grain(result, 0.03)
        
        return result
    
    def _portra_160_v2(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Kodak Portra 160 v2 - 自然膚色"""
        # 基於 Portra 400 但更柔和
        result = self._portra_400_v2(img)
        
        # 更細的顆粒
        result = self._film_grain(result, 0.015, 0.7)
        
        return result
    
    def _portra_800_v3(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Kodak Portra 800 v3 - 高感光人像"""
        # 基於 Portra 400 但顆粒更明顯
        result = self._portra_400_v2(img)
        
        # 高感光的顆粒感
        result = self._film_grain(result, 0.05, 1.2)
        
        return result
    
    def _kodak_gold_200(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Kodak Gold 200 - 溫暖金黃"""
        # Gold 特有的暖調
        result = self._color_temperature(img, 5200)  # 暖色調
        
        # 金黃色調調整
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,0] = np.clip(hsv[:,:,0] * 0.96 + 3, 0, 179)  # 色相偏金黃
        hsv[:,:,1] *= 1.18  # 增強飽和度
        hsv[:,:,2] *= 1.05  # 微調亮度
        
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # 溫暖分離調色
        result = self._split_toning(result, (10, 5, -5), (-3, 2, 8), 0.25)
        
        # 膠片顆粒
        result = self._film_grain(result, 0.025)
        
        return result
    
    def _ultramax_400(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Kodak Ultramax 400 - 日常拍攝"""
        # 基礎色彩調整
        result = self._color_temperature(img, 6000)
        
        # 適度飽和度
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 1.1
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # 膠片顆粒
        result = self._film_grain(result, 0.04)
        
        return result
    
    def _ektar_100(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Kodak Ektar 100 - 風景專用"""
        # Ektar 的高飽和度
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 1.35  # 高飽和度
        
        # 特別增強自然色彩
        green_mask = (hsv[:,:,0] >= 40) & (hsv[:,:,0] <= 80)
        blue_mask = (hsv[:,:,0] >= 100) & (hsv[:,:,0] <= 130)
        hsv[green_mask, 1] *= 1.15
        hsv[blue_mask, 1] *= 1.15
        
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # 高對比度
        result = self._tone_curve(result, 'high_contrast')
        
        # 細膩顆粒
        result = self._film_grain(result, 0.015, 0.5)
        
        return result
    
    def _tri_x_400(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Kodak Tri-X 400 - 經典黑白"""
        # Tri-X 特有的高對比度黑白
        b, g, r = cv2.split(img.astype(np.float32))
        gray = (r * 0.25 + g * 0.65 + b * 0.1)  # Tri-X 權重
        gray = np.clip(gray, 0, 255).astype(np.uint8)
        
        # 高對比度處理
        gray = self._tone_curve(gray, 'high_contrast')
        
        # Tri-X 特有的顆粒感
        gray = self._film_grain(gray, 0.06, 1.0)
        
        # 轉回三通道
        result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        # 輕微暖調
        result = self._color_temperature(result, 6800)
        
        return result
    
    def _tmax_100(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Kodak T-Max 100 - 高解析黑白"""
        # T-Max 的精細黑白
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 精細的對比度調整
        gray = self._tone_curve(gray, 'film')
        
        # 極細的顆粒
        gray = self._film_grain(gray, 0.01, 0.3)
        
        # 轉回三通道
        result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        return result
    
    def _tmax_3200(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Kodak T-Max P3200 - 高感光黑白"""
        # 基於 T-Max 100 但顆粒明顯
        result = self._tmax_100(img)
        
        # 高感光顆粒
        gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        gray = self._film_grain(gray, 0.08, 1.5)
        result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        return result
    
    # === Fujicolor 系列 ===
    
    def _fujicolor_c200(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Fujicolor C200 - 經濟型彩色"""
        # 基礎色彩處理
        result = self._color_temperature(img, 6200)
        
        # 適度飽和度
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 1.05
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # 膠片顆粒
        result = self._film_grain(result, 0.03)
        
        return result
    
    def _superia_400(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Fujicolor Superia 400 - 萬用彩色"""
        # Superia 特有的色彩特性
        result = self._color_temperature(img, 6100)
        
        # 飽和度調整
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 1.12
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # Fuji 特有的色彩偏移
        result = self._split_toning(result, (3, 1, -2), (-1, 2, 3), 0.2)
        
        # 膠片顆粒
        result = self._film_grain(result, 0.035)
        
        return result
    
    def _superia_1600(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Fujicolor Superia 1600 - 高感光"""
        # 基於 Superia 400
        result = self._superia_400(img)
        
        # 高感光顆粒
        result = self._film_grain(result, 0.065, 1.3)
        
        return result
    
    def _natura_1600(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Fujicolor Natura 1600 - 自然色彩"""
        # Natura 特有的自然色彩還原
        result = self._color_temperature(img, 6300)
        
        # 自然飽和度
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 1.08  # 適度飽和度
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # 高感光顆粒但保持自然
        result = self._film_grain(result, 0.055, 1.1)
        
        return result
    
    def _reala_100(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Fujicolor Reala 100 - 真實色彩"""
        # Reala 特有的真實色彩還原
        result = self._color_temperature(img, 6400)
        
        # 真實色彩調整
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 1.02  # 輕微飽和度
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # 精細顆粒
        result = self._film_grain(result, 0.015, 0.6)
        
        return result
    
    # === 電影膠片 ===
    
    def _cinestill_800t(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """CineStill 800T - 鎢絲燈電影膠片"""
        # 鎢絲燈色溫
        result = self._color_temperature(img, 3200)
        
        # CineStill 特有的暖調和光暈效果
        result = self._split_toning(result, (15, 8, -10), (-5, 3, 10), 0.3)
        
        # 電影膠片的柔和對比度
        result = self._tone_curve(result, 'film')
        
        # 膠片顆粒
        result = self._film_grain(result, 0.045)
        
        return result
    
    def _cinestill_400d(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """CineStill 400D - 日光電影膠片"""
        # 日光色溫
        result = self._color_temperature(img, 5500)
        
        # CineStill 特有的色彩特性
        result = self._split_toning(result, (5, 2, -3), (-2, 2, 5), 0.25)
        
        # 電影膠片質感
        result = self._tone_curve(result, 'film')
        
        # 膠片顆粒
        result = self._film_grain(result, 0.04)
        
        return result
    
    def _vision3_250d(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Kodak Vision3 250D - 專業電影膠片"""
        # 專業電影色溫
        result = self._color_temperature(img, 5500)
        
        # Vision3 特有的色彩科學
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 1.15  # 適度飽和度
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # 專業電影的色彩分級
        result = self._split_toning(result, (8, 3, -5), (-3, 2, 6), 0.2)
        
        # 精細顆粒
        result = self._film_grain(result, 0.02, 0.8)
        
        return result
    
    def _vision3_500t(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """Kodak Vision3 500T - 室內電影膠片"""
        # 基於 Vision3 250D 但偏暖
        result = self._vision3_250d(img)
        result = self._color_temperature(result, 3200)
        
        # 稍微增加顆粒
        result = self._film_grain(result, 0.035, 1.0)
        
        return result
    
    # === 復古風格 ===
    
    def _vintage_kodachrome(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """復古 Kodachrome 風格"""
        # 基於 Kodachrome 64 但加入復古效果
        result = self._kodachrome_64(img)
        
        # 復古褪色
        result = self._vintage_fade(result, 0.3)
        
        # 增加顆粒感
        result = self._film_grain(result, 0.04, 1.2)
        
        return result
    
    def _nostalgic_negative(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """懷舊負片風格"""
        # 復古處理
        result = self._vintage_fade(img, 0.4)
        
        # 懷舊色調
        result = self._split_toning(result, (15, 8, -10), (-5, 5, 12), 0.35)
        
        # 降低飽和度
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 0.75
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # 復古顆粒
        result = self._film_grain(result, 0.05, 1.3)
        
        return result
    
    def _summer_1960(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """1960年夏日風格"""
        # 60年代的色彩特性
        result = self._color_temperature(img, 5800)
        
        # 夏日的溫暖色調
        result = self._split_toning(result, (12, 6, -8), (-3, 4, 8), 0.3)
        
        # 復古飽和度
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 1.2
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # 輕微褪色
        result = self._vintage_fade(result, 0.2)
        
        # 復古顆粒
        result = self._film_grain(result, 0.035, 1.1)
        
        return result
    
    def _california_summer(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """加州夏日風格"""
        # 加州陽光的色調
        result = self._color_temperature(img, 5600)
        
        # 夏日海岸色調
        result = self._split_toning(result, (10, 4, -6), (-2, 3, 8), 0.25)
        
        # 明亮飽和度
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 1.25
        hsv[:,:,2] *= 1.05
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return result
    
    def _pacific_blues(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """太平洋藍調風格"""
        # 藍調色溫
        result = self._color_temperature(img, 7200)
        
        # 太平洋藍色調
        result = self._split_toning(result, (-5, -2, 10), (2, -1, 15), 0.3)
        
        # 增強藍色
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        blue_mask = (hsv[:,:,0] >= 100) & (hsv[:,:,0] <= 130)
        hsv[blue_mask, 1] *= 1.3
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return result
    
    def _vintage_bronze(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """復古青銅風格"""
        # 青銅色調
        result = self._color_temperature(img, 4800)
        
        # 青銅色彩偏移
        result = self._split_toning(result, (20, 10, -15), (-8, 8, 15), 0.4)
        
        # 復古處理
        result = self._vintage_fade(result, 0.35)
        
        # 降低飽和度
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 0.8
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return result
    
    # === 特殊效果 ===
    
    def _redscale(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """紅片效果"""
        # 紅片的色彩反轉效果
        b, g, r = cv2.split(img)
        
        # 通道重新排列模擬紅片效果
        result = cv2.merge([r, g, b])  # 紅藍通道交換
        
        # 增強紅色調
        result = self._color_temperature(result, 3000)
        
        # 紅片特有的飽和度
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 1.4
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return result
    
    def _cross_process(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """交叉沖洗效果"""
        # 交叉沖洗的高對比度和色彩偏移
        result = self._tone_curve(img, 'high_contrast')
        
        # 強烈的色彩偏移
        result = self._split_toning(result, (25, -10, -20), (-15, 10, 25), 0.5)
        
        # 增強飽和度
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:,:,1] *= 1.5
        result = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        return result
    
    def _bleach_bypass(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """漂白跳過效果"""
        # 保留銀鹽的黑白層
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_3ch = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        # 與原圖混合
        result = cv2.addWeighted(img, 0.6, gray_3ch, 0.4, 0)
        
        # 增強對比度
        result = self._tone_curve(result, 'high_contrast')
        
        return result
    
    def _infrared_bw(self, img: np.ndarray, **kwargs) -> np.ndarray:
        """紅外線黑白效果"""
        # 紅外線的色彩權重
        b, g, r = cv2.split(img.astype(np.float32))
        
        # 模擬紅外線感光特性
        gray = (r * 0.7 + g * 0.2 + b * 0.1)  # 紅外線權重
        
        # 反轉植物和天空的色調
        gray = 255 - gray  # 部分反轉
        gray = np.clip(gray, 0, 255).astype(np.uint8)
        
        # 高對比度
        gray = self._tone_curve(gray, 'high_contrast')
        
        # 轉回三通道
        result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        return result


def main():
    """示例用法"""
    # 創建軟片模擬實例
    film_sim = EnhancedFilmSimulation()
    
    # 顯示所有可用的軟片模擬
    print("=== 增強版軟片模擬引擎 ===")
    
    simulations = film_sim.get_available_simulations()
    
    print("📸 經典 Fujifilm 軟片:")
    fuji_sims = [k for k in simulations.keys() if any(x in k for x in ['PROVIA', 'VELVIA', 'ASTIA', 'CLASSIC', 'PRO_NEG', 'ETERNA', 'ACROS', 'MONO'])]
    for sim in fuji_sims:
        print(f"  • {sim}: {simulations[sim]}")
    
    print("\n🎞️ 經典 Kodak 軟片:")
    kodak_sims = [k for k in simulations.keys() if 'KODAK' in k]
    for sim in kodak_sims:
        print(f"  • {sim}: {simulations[sim]}")
    
    print("\n🌈 Fujicolor 系列:")
    fujicolor_sims = [k for k in simulations.keys() if 'FUJICOLOR' in k or 'REALA' in k]
    for sim in fujicolor_sims:
        print(f"  • {sim}: {simulations[sim]}")
    
    print("\n🎬 電影膠片:")
    cinema_sims = [k for k in simulations.keys() if any(x in k for x in ['CINESTILL', 'VISION'])]
    for sim in cinema_sims:
        print(f"  • {sim}: {simulations[sim]}")
    
    print("\n⏳ 復古風格:")
    vintage_sims = [k for k in simulations.keys() if any(x in k for x in ['VINTAGE', 'NOSTALGIC', 'SUMMER', 'CALIFORNIA', 'PACIFIC', 'BRONZE'])]
    for sim in vintage_sims:
        print(f"  • {sim}: {simulations[sim]}")
    
    print("\n✨ 特殊效果:")
    special_sims = [k for k in simulations.keys() if any(x in k for x in ['REDSCALE', 'CROSS', 'BLEACH', 'INFRARED'])]
    for sim in special_sims:
        print(f"  • {sim}: {simulations[sim]}")
    
    print(f"\n總計: {len(simulations)} 種專業軟片模擬效果")
    print("\n使用方法:")
    print("film_sim = EnhancedFilmSimulation()")
    print("result = film_sim.apply_simulation(image, 'KODAK_PORTRA_400')")


if __name__ == "__main__":
    main()
