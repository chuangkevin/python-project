"""
Fujifilm Film Simulation Engine
基於真實 Fujifilm 相機軟片模擬的 Python 實現

支援軟片類型：
- PROVIA (標準專業反轉片)
- Velvia (高飽和度風景片)
- ASTIA (人像柔和片)
- Classic Chrome (20世紀雜誌風格)
- Classic Negative (SUPERIA 底片風格)
- ETERNA (電影膠片風格)
- Nostalgic Negative (復古相冊風格)
- REALA ACE (中性色彩高對比)
- ACROS (細緻黑白片)
- Monochrome (基礎黑白)
- Sepia (復古棕褐色)
"""

import cv2
import numpy as np
from PIL import Image, ImageEnhance
from typing import Union, Tuple
import math

class FujifilmSimulation:
    """Fujifilm 軟片模擬處理器"""
    
    def __init__(self):
        self.simulations = {
            'PROVIA': self._provia,
            'Velvia': self._velvia,
            'ASTIA': self._astia,
            'Classic_Chrome': self._classic_chrome,
            'Classic_Negative': self._classic_negative,
            'ETERNA': self._eterna,
            'Nostalgic_Negative': self._nostalgic_negative,
            'REALA_ACE': self._reala_ace,
            'ACROS': self._acros,
            'Monochrome': self._monochrome,
            'Sepia': self._sepia
        }
    
    def apply(self, image: Union[str, np.ndarray, Image.Image], simulation: str) -> np.ndarray:
        """
        套用軟片模擬效果
        
        Args:
            image: 輸入圖像 (檔案路徑、numpy array 或 PIL Image)
            simulation: 軟片模擬名稱
            
        Returns:
            處理後的圖像 (numpy array, BGR格式)
        """
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
        return self.simulations[simulation](img)
    
    def get_available_simulations(self) -> list:
        """取得所有可用的軟片模擬名稱"""
        return list(self.simulations.keys())
    
    def _adjust_curves(self, img: np.ndarray, shadows: float = 1.0, 
                      midtones: float = 1.0, highlights: float = 1.0) -> np.ndarray:
        """調整色調曲線"""
        img_norm = img.astype(np.float32) / 255.0
        
        # 建立遮罩
        shadow_mask = np.power(1.0 - img_norm, 2)
        highlight_mask = np.power(img_norm, 2)
        midtone_mask = 1.0 - shadow_mask - highlight_mask
        
        # 套用調整
        result = (img_norm * shadow_mask * shadows + 
                 img_norm * midtone_mask * midtones + 
                 img_norm * highlight_mask * highlights)
        
        return np.clip(result * 255, 0, 255).astype(np.uint8)
    
    def _color_grade(self, img: np.ndarray, shadows_color: Tuple[float, float, float], 
                    highlights_color: Tuple[float, float, float], intensity: float = 0.3) -> np.ndarray:
        """色彩分級"""
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # 計算亮度遮罩
        brightness = img_hsv[:, :, 2] / 255.0
        shadow_mask = 1.0 - brightness
        highlight_mask = brightness
        
        # 套用色彩偏移
        for i in range(3):
            shadow_shift = shadows_color[i] * shadow_mask * intensity
            highlight_shift = highlights_color[i] * highlight_mask * intensity
            img_hsv[:, :, i] += (shadow_shift + highlight_shift)
        
        img_hsv = np.clip(img_hsv, 0, 255)
        return cv2.cvtColor(img_hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    
    def _saturation_adjust(self, img: np.ndarray, factor: float) -> np.ndarray:
        """調整飽和度"""
        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        img_hsv[:, :, 1] *= factor
        img_hsv[:, :, 1] = np.clip(img_hsv[:, :, 1], 0, 255)
        return cv2.cvtColor(img_hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    
    def _contrast_adjust(self, img: np.ndarray, factor: float) -> np.ndarray:
        """調整對比度"""
        img_float = img.astype(np.float32)
        mean = np.mean(img_float)
        result = (img_float - mean) * factor + mean
        return np.clip(result, 0, 255).astype(np.uint8)
    
    def _gamma_correct(self, img: np.ndarray, gamma: float) -> np.ndarray:
        """Gamma 校正"""
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype(np.uint8)
        return cv2.LUT(img, table)
    
    # === 軟片模擬實現 ===
    
    def _provia(self, img: np.ndarray) -> np.ndarray:
        """
        PROVIA - 標準專業反轉片
        特色: 平衡自然的色彩再現，適合所有主題，明亮通透
        """
        # 輕微提升亮度
        result = self._gamma_correct(img, 0.92)
        
        # 溫和的對比度提升
        result = self._contrast_adjust(result, 1.08)
        
        # 優化色調曲線
        result = self._adjust_curves(result, shadows=1.1, midtones=1.02, highlights=0.96)
        
        # 保持自然飽和度
        result = self._saturation_adjust(result, 1.06)
        
        # 輕微色彩平衡調整
        result = self._color_grade(result,
                                 shadows_color=(2, 0, -1),
                                 highlights_color=(-1, -1, 2),
                                 intensity=0.08)
        
        return result
    
    def _velvia(self, img: np.ndarray) -> np.ndarray:
        """
        Velvia - 高飽和度風景片
        特色: 鮮豔銳利的色彩，適合風景攝影，明亮通透
        """
        # 大幅提升整體亮度 (解決太暗問題)
        result = self._gamma_correct(img, 0.75)  # 更大幅度提升亮度
        
        # 先提升亮度再調整對比度
        result = self._adjust_curves(result, shadows=1.4, midtones=1.2, highlights=1.0)
        
        # 溫和的對比度增強
        result = self._contrast_adjust(result, 1.1)
        
        # 高飽和度但控制在合理範圍
        result = self._saturation_adjust(result, 1.3)
        
        # 強化特定顏色，並提升亮度
        result_hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # 全局亮度提升
        result_hsv[:, :, 2] = np.minimum(result_hsv[:, :, 2] * 1.15, 255)
        
        # 綠色增強
        green_mask = ((result_hsv[:, :, 0] >= 35) & (result_hsv[:, :, 0] <= 85))
        result_hsv[green_mask, 1] *= 1.15
        
        # 藍色增強
        blue_mask = ((result_hsv[:, :, 0] >= 100) & (result_hsv[:, :, 0] <= 130))
        result_hsv[blue_mask, 1] *= 1.2
        
        # 橙色/紅色增強
        orange_red_mask = ((result_hsv[:, :, 0] >= 0) & (result_hsv[:, :, 0] <= 25)) | \
                          ((result_hsv[:, :, 0] >= 160) & (result_hsv[:, :, 0] <= 180))
        result_hsv[orange_red_mask, 1] *= 1.1
        
        result_hsv = np.clip(result_hsv, 0, 255)
        result = cv2.cvtColor(result_hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # 溫暖色調調整
        result = self._color_grade(result,
                                 shadows_color=(5, 2, -3),
                                 highlights_color=(-1, -2, 2),
                                 intensity=0.12)
        
        return result
    
    def _astia(self, img: np.ndarray) -> np.ndarray:
        """
        ASTIA - 人像柔和片
        特色: 柔和忠實的膚色再現，鮮豔的藍天和綠色
        """
        # 柔和對比度
        result = self._contrast_adjust(img, 0.9)
        
        # 柔和曲線調整
        result = self._adjust_curves(result, shadows=1.1, midtones=1.0, highlights=0.95)
        
        # 暖調色彩分級 (膚色友好)
        result = self._color_grade(result, 
                                 shadows_color=(5, -2, -10),  # 暖調陰影
                                 highlights_color=(-2, -5, 5),  # 冷調高光
                                 intensity=0.2)
        
        # 適中飽和度
        result = self._saturation_adjust(result, 1.1)
        
        return result
    
    def _classic_chrome(self, img: np.ndarray) -> np.ndarray:
        """
        Classic Chrome - 20世紀雜誌風格
        特色: 低飽和度硬調，紀實風格，但保持適當亮度
        """
        # 輕微提升亮度避免過暗
        result = self._gamma_correct(img, 0.95)
        
        # 降低飽和度但不過度
        result = self._saturation_adjust(result, 0.75)
        
        # 適中的對比度
        result = self._contrast_adjust(result, 1.25)
        
        # 調整色調曲線，保持細節
        result = self._adjust_curves(result, shadows=1.15, midtones=1.05, highlights=0.85)
        
        # Classic Chrome 特色的色彩分級
        result = self._color_grade(result,
                                 shadows_color=(3, 2, 8),     # 輕微藍調陰影
                                 highlights_color=(2, -3, -2), # 輕微綠黃調高光
                                 intensity=0.2)
        
        return result
    
    def _classic_negative(self, img: np.ndarray) -> np.ndarray:
        """
        Classic Negative - SUPERIA 底片風格
        特色: 立體表現，深度色調變化
        """
        # 膠片曲線
        result = self._adjust_curves(img, shadows=1.15, midtones=1.05, highlights=0.9)
        
        # 暖調色彩分級
        result = self._color_grade(result,
                                 shadows_color=(10, 5, -5),   # 暖調陰影
                                 highlights_color=(-5, -2, 8), # 冷調高光
                                 intensity=0.3)
        
        # 適中飽和度
        result = self._saturation_adjust(result, 0.9)
        
        # 輕微對比度提升
        result = self._contrast_adjust(result, 1.1)
        
        return result
    
    def _eterna(self, img: np.ndarray) -> np.ndarray:
        """
        ETERNA - 電影膠片風格
        特色: 抑制飽和度，電影感外觀
        """
        # 低飽和度
        result = self._saturation_adjust(img, 0.8)
        
        # 電影曲線
        result = self._adjust_curves(result, shadows=1.1, midtones=0.95, highlights=0.85)
        
        # 輕微暖調
        result = self._color_grade(result,
                                 shadows_color=(8, 2, -8),    # 暖調陰影
                                 highlights_color=(-3, -1, 5), # 冷調高光
                                 intensity=0.2)
        
        # 柔和對比度
        result = self._contrast_adjust(result, 0.95)
        
        return result
    
    def _nostalgic_negative(self, img: np.ndarray) -> np.ndarray:
        """
        Nostalgic Negative - 復古相冊風格
        特色: 琥珀色高光，復古氛圍
        """
        # 復古曲線
        result = self._adjust_curves(img, shadows=1.2, midtones=1.1, highlights=0.9)
        
        # 琥珀色調
        result = self._color_grade(result,
                                 shadows_color=(15, 8, -10),  # 暖調陰影
                                 highlights_color=(20, 10, -15), # 琥珀高光
                                 intensity=0.4)
        
        # 降低飽和度
        result = self._saturation_adjust(result, 0.85)
        
        # 輕微 Gamma 提升
        result = self._gamma_correct(result, 1.05)
        
        return result
    
    def _reala_ace(self, img: np.ndarray) -> np.ndarray:
        """
        REALA ACE - 中性色彩高對比
        特色: 中性色彩再現，高對比度調性，明亮自然
        """
        # 大幅提升整體亮度
        result = self._gamma_correct(img, 0.8)  # 更大幅度提升亮度
        
        # 先提升亮度再調整對比度
        result = self._adjust_curves(result, shadows=1.25, midtones=1.15, highlights=0.98)
        
        # 溫和的對比度增強
        result = self._contrast_adjust(result, 1.05)
        
        # 適度提升飽和度
        result = self._saturation_adjust(result, 1.1)
        
        # 全局亮度增強
        result_hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        
        # 提升所有像素的亮度
        result_hsv[:, :, 2] = np.minimum(result_hsv[:, :, 2] * 1.12, 255)
        
        # 對膚色區域特別優化
        skin_mask = ((result_hsv[:, :, 0] >= 5) & (result_hsv[:, :, 0] <= 25))
        result_hsv[skin_mask, 1] *= 0.95
        result_hsv[skin_mask, 2] *= 1.05
        
        result_hsv = np.clip(result_hsv, 0, 255)
        result = cv2.cvtColor(result_hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # 非常輕微的色彩調整
        result = self._color_grade(result,
                                 shadows_color=(2, 1, -1),
                                 highlights_color=(-1, -1, 2),
                                 intensity=0.08)
        
        return result
    
    def _acros(self, img: np.ndarray) -> np.ndarray:
        """
        ACROS - 細緻黑白片
        特色: 豐富陰影細節，高解析銳利度
        """
        # 轉換為灰階 (保留更多細節)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 增強對比度
        gray = self._contrast_adjust(gray, 1.2)
        
        # 細節增強
        gray = self._adjust_curves(gray, shadows=1.15, midtones=1.0, highlights=0.9)
        
        # 轉回 BGR
        result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        
        return result
    
    def _monochrome(self, img: np.ndarray) -> np.ndarray:
        """
        Monochrome - 基礎黑白
        特色: 標準黑白轉換
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        return result
    
    def _sepia(self, img: np.ndarray) -> np.ndarray:
        """
        Sepia - 復古棕褐色
        特色: 復古懷舊氛圍
        """
        # 棕褐色轉換矩陣
        sepia_filter = np.array([[0.272, 0.534, 0.131],
                                [0.349, 0.686, 0.168],
                                [0.393, 0.769, 0.189]])
        
        result = cv2.transform(img, sepia_filter)
        result = np.clip(result, 0, 255)
        
        return result.astype(np.uint8)


# === 使用範例 ===
if __name__ == "__main__":
    # 建立軟片模擬器
    sim = FujifilmSimulation()
    
    # 顯示可用軟片
    print("可用的 Fujifilm 軟片模擬:")
    for i, name in enumerate(sim.get_available_simulations(), 1):
        print(f"{i:2d}. {name}")
    
    # 測試用法 (需要實際圖像檔案)
    # result = sim.apply("test_image.jpg", "Velvia")
    # cv2.imwrite("velvia_result.jpg", result)
