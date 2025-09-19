"""
軟片模擬預設管理器
Film Simulation Preset Manager

模組化管理軟片模擬預設，支援JSON格式的預設檔案
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Union
import cv2
import numpy as np
from PIL import Image
import logging

# 設置日誌
logger = logging.getLogger(__name__)

class PresetValidationError(Exception):
    """預設驗證錯誤"""
    pass

class PresetNotFoundError(Exception):
    """預設不存在錯誤"""
    pass

class FilmPresetManager:
    """軟片預設管理器"""

    def __init__(self, preset_root: str = None):
        """初始化預設管理器

        Args:
            preset_root: 預設檔案根目錄，預設為當前目錄下的preset/systemPreset
        """
        if preset_root is None:
            self.preset_root = Path(__file__).parent / 'preset' / 'systemPreset'
        else:
            self.preset_root = Path(preset_root)

        self.presets: Dict[str, Dict[str, Any]] = {}
        self.categories: Dict[str, List[str]] = {}
        self.manufacturers: Dict[str, List[str]] = {}

        # 載入所有預設
        self.reload_presets()

    def reload_presets(self) -> None:
        """重新載入所有預設檔案"""
        self.presets.clear()
        self.categories.clear()
        self.manufacturers.clear()

        if not self.preset_root.exists():
            logger.warning(f"預設目錄不存在: {self.preset_root}")
            return

        # 掃描所有JSON檔案
        for json_file in self.preset_root.rglob('*.json'):
            # 跳過模板檔案
            if json_file.name.startswith('_'):
                continue

            try:
                preset = self._load_preset_file(json_file)
                preset_id = preset['metadata']['name']

                # 驗證預設格式
                self._validate_preset(preset)

                # 儲存預設
                self.presets[preset_id] = preset

                # 組織分類
                category = preset['metadata']['category']
                manufacturer = preset['metadata']['manufacturer']

                if category not in self.categories:
                    self.categories[category] = []
                self.categories[category].append(preset_id)

                if manufacturer not in self.manufacturers:
                    self.manufacturers[manufacturer] = []
                self.manufacturers[manufacturer].append(preset_id)

                logger.info(f"載入預設: {preset_id}")

            except Exception as e:
                logger.error(f"載入預設檔案失敗 {json_file}: {e}")

    def _load_preset_file(self, file_path: Path) -> Dict[str, Any]:
        """載入預設檔案"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _validate_preset(self, preset: Dict[str, Any]) -> None:
        """驗證預設格式"""
        required_metadata = ['name', 'description', 'manufacturer', 'category']
        required_processing = ['tone_curve', 'saturation', 'contrast']

        # 檢查必要的metadata欄位
        if 'metadata' not in preset:
            raise PresetValidationError("缺少metadata區塊")

        for field in required_metadata:
            if field not in preset['metadata']:
                raise PresetValidationError(f"metadata缺少必要欄位: {field}")

        # 檢查必要的processing欄位
        if 'processing' not in preset:
            raise PresetValidationError("缺少processing區塊")

        for field in required_processing:
            if field not in preset['processing']:
                raise PresetValidationError(f"processing缺少必要欄位: {field}")

    def list_presets(self, category: str = None, manufacturer: str = None) -> List[Dict[str, Any]]:
        """列出預設清單

        Args:
            category: 篩選分類
            manufacturer: 篩選廠商

        Returns:
            預設清單
        """
        result = []

        for preset_id, preset in self.presets.items():
            metadata = preset['metadata']

            # 篩選條件
            if category and metadata['category'] != category:
                continue
            if manufacturer and metadata['manufacturer'] != manufacturer:
                continue

            result.append({
                'id': preset_id,
                'name': metadata['name'],
                'description': metadata['description'],
                'manufacturer': metadata['manufacturer'],
                'category': metadata['category'],
                'icon': metadata.get('icon'),
                'tags': metadata.get('tags', [])
            })

        return sorted(result, key=lambda x: x['name'])

    def get_preset(self, preset_id: str) -> Dict[str, Any]:
        """獲取指定預設

        Args:
            preset_id: 預設ID

        Returns:
            預設資料
        """
        if preset_id not in self.presets:
            raise PresetNotFoundError(f"預設不存在: {preset_id}")

        return self.presets[preset_id].copy()

    def get_categories(self) -> Dict[str, List[str]]:
        """獲取所有分類"""
        return self.categories.copy()

    def get_manufacturers(self) -> Dict[str, List[str]]:
        """獲取所有廠商"""
        return self.manufacturers.copy()

    def create_processor(self, preset_id: str) -> 'FilmProcessor':
        """創建軟片處理器

        Args:
            preset_id: 預設ID

        Returns:
            軟片處理器實例
        """
        preset = self.get_preset(preset_id)
        return FilmProcessor(preset)


class FilmProcessor:
    """軟片處理器 - 根據預設參數處理圖像"""

    def __init__(self, preset: Dict[str, Any]):
        """初始化處理器

        Args:
            preset: 預設資料
        """
        self.preset = preset
        self.metadata = preset['metadata']
        self.processing = preset['processing']
        self.advanced = preset.get('advanced', {})

    def process_image(self, image: Union[str, Image.Image, np.ndarray]) -> np.ndarray:
        """處理圖像

        Args:
            image: 輸入圖像 (檔案路徑、PIL.Image或numpy陣列)

        Returns:
            處理後的圖像 (numpy陣列，BGR格式)
        """
        # 轉換輸入圖像為numpy陣列
        if isinstance(image, str):
            img = cv2.imread(image)
        elif isinstance(image, Image.Image):
            img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        else:
            img = image.copy()

        if img is None:
            raise ValueError("無法載入圖像")

        # 套用處理步驟
        result = img.astype(np.float32)

        # 1. 色調曲線
        if self.processing['tone_curve']['enabled']:
            result = self._apply_tone_curve(result)

        # 2. 色溫調整
        if self.processing['color_temperature']['enabled']:
            result = self._apply_color_temperature(result)

        # 3. 飽和度調整
        if self.processing['saturation']['enabled']:
            result = self._apply_saturation(result)

        # 4. 對比度調整
        if self.processing['contrast']['enabled']:
            result = self._apply_contrast(result)

        # 5. 亮度調整
        if self.processing['brightness']['enabled']:
            result = self._apply_brightness(result)

        # 6. 分離調色
        if self.processing['split_toning']['enabled']:
            result = self._apply_split_toning(result)

        # 7. 復古褪色
        if self.processing['vintage_fade']['enabled']:
            result = self._apply_vintage_fade(result)

        # 8. 膠片顆粒
        if self.processing['film_grain']['enabled']:
            result = self._apply_film_grain(result)

        # 9. HSL調整
        if self.advanced.get('hsl_adjustments', {}).get('enabled', False):
            result = self._apply_hsl_adjustments(result)

        # 10. 暗角效果
        if self.processing['vignette']['enabled']:
            result = self._apply_vignette(result)

        return np.clip(result, 0, 255).astype(np.uint8)

    def _apply_tone_curve(self, img: np.ndarray) -> np.ndarray:
        """套用色調曲線"""
        tone_settings = self.processing['tone_curve']
        curve_type = tone_settings.get('type', 'linear')
        gamma = tone_settings.get('gamma', 1.0)

        if curve_type == 'linear':
            return img

        # 歸一化到0-1範圍
        img_norm = img / 255.0

        if curve_type == 'film':
            # 經典膠片S曲線
            result = np.power(img_norm, gamma)
        elif curve_type == 'vintage':
            # 復古曲線 - 提升黑階
            result = img_norm * 0.85 + 0.15
        elif curve_type == 'high_contrast':
            # 高對比度S曲線
            result = 0.5 + 0.5 * np.tanh(4 * (img_norm - 0.5))
        else:
            result = img_norm

        return np.clip(result * 255, 0, 255)

    def _apply_color_temperature(self, img: np.ndarray) -> np.ndarray:
        """套用色溫調整"""
        temp_settings = self.processing['color_temperature']
        temperature = temp_settings.get('temperature', 6500)

        if temperature == 6500:
            return img

        img_norm = img / 255.0

        if temperature < 6500:  # 暖色
            factor = (6500 - temperature) / 3500.0
            img_norm[:,:,0] *= (1.0 - factor * 0.3)  # 減少藍色
            img_norm[:,:,2] *= (1.0 + factor * 0.2)  # 增加紅色
        else:  # 冷色
            factor = (temperature - 6500) / 3500.0
            img_norm[:,:,0] *= (1.0 + factor * 0.3)  # 增加藍色
            img_norm[:,:,2] *= (1.0 - factor * 0.2)  # 減少紅色

        return np.clip(img_norm * 255, 0, 255)

    def _apply_saturation(self, img: np.ndarray) -> np.ndarray:
        """套用飽和度調整"""
        sat_settings = self.processing['saturation']
        global_sat = sat_settings.get('global', 1.0)

        # 轉換到HSV
        hsv = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)

        # 調整飽和度
        hsv[:,:,1] *= global_sat

        # 個別顏色通道調整
        if 'red' in sat_settings or 'green' in sat_settings or 'blue' in sat_settings:
            bgr = img / 255.0
            bgr[:,:,0] *= sat_settings.get('blue', 1.0)
            bgr[:,:,1] *= sat_settings.get('green', 1.0)
            bgr[:,:,2] *= sat_settings.get('red', 1.0)
            img = bgr * 255

        hsv = np.clip(hsv, 0, 255)
        return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)

    def _apply_contrast(self, img: np.ndarray) -> np.ndarray:
        """套用對比度調整"""
        contrast_settings = self.processing['contrast']
        global_contrast = contrast_settings.get('global', 1.0)

        # 計算平均值
        mean = np.mean(img)

        # 套用對比度
        result = (img - mean) * global_contrast + mean

        return np.clip(result, 0, 255)

    def _apply_brightness(self, img: np.ndarray) -> np.ndarray:
        """套用亮度調整"""
        brightness_settings = self.processing['brightness']
        gamma = brightness_settings.get('gamma', 1.0)
        exposure = brightness_settings.get('exposure', 0.0)

        # Gamma校正
        img_norm = img / 255.0
        result = np.power(img_norm, gamma) * 255

        # 曝光調整
        if exposure != 0:
            result *= (1.0 + exposure)

        return np.clip(result, 0, 255)

    def _apply_split_toning(self, img: np.ndarray) -> np.ndarray:
        """套用分離調色"""
        # 簡化實現 - 實際可以更複雜
        return img

    def _apply_vintage_fade(self, img: np.ndarray) -> np.ndarray:
        """套用復古褪色效果"""
        fade_settings = self.processing['vintage_fade']
        intensity = fade_settings.get('intensity', 0.3)

        img_norm = img / 255.0

        # 提升黑階
        img_norm = img_norm * (1.0 - intensity * 0.3) + intensity * 0.3

        # 降低對比度
        mean = np.mean(img_norm)
        img_norm = (img_norm - mean) * (1.0 - intensity * 0.4) + mean

        return np.clip(img_norm * 255, 0, 255)

    def _apply_film_grain(self, img: np.ndarray) -> np.ndarray:
        """套用膠片顆粒"""
        grain_settings = self.processing['film_grain']
        strength = grain_settings.get('strength', 0.1)

        if strength <= 0:
            return img

        # 生成雜訊
        noise = np.random.normal(0, strength * 255, img.shape)

        # 套用到圖像
        result = img + noise

        return np.clip(result, 0, 255)

    def _apply_hsl_adjustments(self, img: np.ndarray) -> np.ndarray:
        """套用HSL調整"""
        # 簡化實現 - 實際需要色相範圍檢測
        return img

    def _apply_vignette(self, img: np.ndarray) -> np.ndarray:
        """套用暗角效果"""
        vignette_settings = self.processing['vignette']
        intensity = vignette_settings.get('intensity', 0.3)
        size = vignette_settings.get('size', 0.8)

        h, w = img.shape[:2]

        # 創建徑向遮罩
        center_x, center_y = w // 2, h // 2
        max_dist = np.sqrt(center_x**2 + center_y**2) * size

        y, x = np.ogrid[:h, :w]
        dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)

        # 計算暗角遮罩
        mask = 1.0 - np.clip(dist / max_dist, 0, 1) * intensity
        mask = np.expand_dims(mask, axis=2)

        return img * mask


# 使用範例
if __name__ == "__main__":
    # 創建預設管理器
    manager = FilmPresetManager()

    # 列出所有預設
    presets = manager.list_presets()
    print(f"找到 {len(presets)} 個預設:")
    for preset in presets:
        print(f"  - {preset['name']} ({preset['manufacturer']})")

    # 使用特定預設處理圖像
    if presets:
        processor = manager.create_processor(presets[0]['id'])
        print(f"創建處理器: {presets[0]['name']}")

        # 這裡可以處理實際圖像
        # result = processor.process_image("test_image.jpg")