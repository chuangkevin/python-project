#!/usr/bin/env python3
"""
RD-1 Camera Control - 統一設定管理器
整合並管理所有現有的設定模組
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SettingsManager:
    """統一設定管理器"""
    
    def __init__(self):
        self.settings_cache = {}
        self.settings_modules = {}
        self.config_dir = Path(__file__).parent.parent / "configs"
        self.config_dir.mkdir(exist_ok=True)
        
        logger.info("設定管理器初始化")
    
    def load_all_settings(self):
        """載入所有設定模組"""
        try:
            # 載入現有設定模組
            self._load_camera_settings()
            self._load_display_settings()
            self._load_dial_settings()
            self._load_film_settings()
            self._load_power_settings()
            self._load_storage_settings()
            
            logger.info("✅ 所有設定模組載入完成")
            
        except Exception as e:
            logger.error(f"設定載入失敗: {e}")
            # 使用預設設定
            self._load_default_settings()
    
    def _load_camera_settings(self):
        """載入相機設定"""
        try:
            from systemControl.settings.camera_settings import CameraSettings
            self.settings_modules['camera'] = CameraSettings()
            logger.info("✅ 相機設定模組載入完成")
        except Exception as e:
            logger.warning(f"相機設定載入失敗: {e}")
            self.settings_modules['camera'] = None
    
    def _load_display_settings(self):
        """載入顯示設定"""
        try:
            from systemControl.settings.display_settings import DisplaySettings
            self.settings_modules['display'] = DisplaySettings()
            logger.info("✅ 顯示設定模組載入完成")
        except Exception as e:
            logger.warning(f"顯示設定載入失敗: {e}")
            self.settings_modules['display'] = None
    
    def _load_dial_settings(self):
        """載入轉盤設定"""
        try:
            from systemControl.settings.dial_settings import DialSettings
            self.settings_modules['dial'] = DialSettings()
            logger.info("✅ 轉盤設定模組載入完成")
        except Exception as e:
            logger.warning(f"轉盤設定載入失敗: {e}")
            self.settings_modules['dial'] = None
    
    def _load_film_settings(self):
        """載入軟片設定"""
        try:
            from systemControl.settings.film_settings import FilmSettings
            self.settings_modules['film'] = FilmSettings()
            logger.info("✅ 軟片設定模組載入完成")
        except Exception as e:
            logger.warning(f"軟片設定載入失敗: {e}")
            self.settings_modules['film'] = None
    
    def _load_power_settings(self):
        """載入電源設定"""
        try:
            from systemControl.settings.power_settings import PowerSettings
            self.settings_modules['power'] = PowerSettings()
            logger.info("✅ 電源設定模組載入完成")
        except Exception as e:
            logger.warning(f"電源設定載入失敗: {e}")
            self.settings_modules['power'] = None
    
    def _load_storage_settings(self):
        """載入儲存設定"""
        try:
            from systemControl.settings.storage_settings import StorageSettings
            self.settings_modules['storage'] = StorageSettings()
            logger.info("✅ 儲存設定模組載入完成")
        except Exception as e:
            logger.warning(f"儲存設定載入失敗: {e}")
            self.settings_modules['storage'] = None
    
    def _load_default_settings(self):
        """載入預設設定"""
        logger.info("使用預設設定")
        
        self.settings_cache = {
            'camera': {
                'shutter_speed': '1/125',
                'iso': 400,
                'exposure_compensation': 0.0,
                'white_balance': 'Auto',
                'focus_mode': 'Continuous',
                'metering_mode': 'Matrix',
                'image_format': 'JPEG+RAW'
            },
            'display': {
                'main_brightness': 80,
                'sub_brightness': 70,
                'main_timeout': 30,
                'sub_timeout': 10,
                'show_histogram': True,
                'show_grid': False
            },
            'dial': {
                'left_dial_sensitivity': 1.0,
                'right_dial_sensitivity': 1.0,
                'press_timeout': 1000,
                'long_press_timeout': 2000,
                'haptic_feedback': True
            },
            'film': {
                'current_simulation': 'Standard',
                'strength': 100,
                'custom_profiles': {}
            },
            'power': {
                'auto_sleep': True,
                'sleep_timeout': 300,
                'low_battery_warning': 20,
                'battery_saver_mode': False
            },
            'storage': {
                'default_path': '/media/usb0',
                'backup_enabled': False,
                'auto_delete_old': False,
                'max_storage_usage': 90
            }
        }
    
    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """取得設定值"""
        try:
            # 先嘗試從模組取得
            if category in self.settings_modules and self.settings_modules[category]:
                module = self.settings_modules[category]
                if hasattr(module, key):
                    return getattr(module, key)
            
            # 從快取取得
            if category in self.settings_cache:
                return self.settings_cache[category].get(key, default)
            
            return default
            
        except Exception as e:
            logger.error(f"取得設定失敗 {category}.{key}: {e}")
            return default
    
    def update_setting(self, category: str, key: str, value: Any):
        """更新設定值"""
        try:
            # 更新模組設定
            if category in self.settings_modules and self.settings_modules[category]:
                module = self.settings_modules[category]
                if hasattr(module, key):
                    setattr(module, key, value)
                    # 儲存設定
                    if hasattr(module, 'save_settings'):
                        module.save_settings()
            
            # 更新快取
            if category not in self.settings_cache:
                self.settings_cache[category] = {}
            self.settings_cache[category][key] = value
            
            # 儲存到檔案
            self._save_category_to_file(category)
            
            logger.info(f"設定更新: {category}.{key} = {value}")
            
        except Exception as e:
            logger.error(f"設定更新失敗 {category}.{key}: {e}")
    
    def get_category_settings(self, category: str) -> Dict[str, Any]:
        """取得整個類別的設定"""
        try:
            settings = {}
            
            # 從模組取得
            if category in self.settings_modules and self.settings_modules[category]:
                module = self.settings_modules[category]
                # 取得所有公開屬性
                for attr in dir(module):
                    if not attr.startswith('_') and not callable(getattr(module, attr)):
                        settings[attr] = getattr(module, attr)
            
            # 合併快取設定
            if category in self.settings_cache:
                settings.update(self.settings_cache[category])
            
            return settings
            
        except Exception as e:
            logger.error(f"取得類別設定失敗 {category}: {e}")
            return {}
    
    def update_category_settings(self, category: str, settings: Dict[str, Any]):
        """更新整個類別的設定"""
        try:
            for key, value in settings.items():
                self.update_setting(category, key, value)
            
            logger.info(f"類別設定更新完成: {category}")
            
        except Exception as e:
            logger.error(f"類別設定更新失敗 {category}: {e}")
    
    def _save_category_to_file(self, category: str):
        """儲存類別設定到檔案"""
        try:
            config_file = self.config_dir / f"{category}_settings.json"
            settings = self.get_category_settings(category)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"儲存設定檔案失敗 {category}: {e}")
    
    def _load_category_from_file(self, category: str):
        """從檔案載入類別設定"""
        try:
            config_file = self.config_dir / f"{category}_settings.json"
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.settings_cache[category] = settings
                    logger.info(f"從檔案載入設定: {category}")
            
        except Exception as e:
            logger.error(f"從檔案載入設定失敗 {category}: {e}")
    
    def save_all_settings(self):
        """儲存所有設定"""
        try:
            # 儲存模組設定
            for category, module in self.settings_modules.items():
                if module and hasattr(module, 'save_settings'):
                    module.save_settings()
            
            # 儲存快取設定
            for category in self.settings_cache.keys():
                self._save_category_to_file(category)
            
            logger.info("✅ 所有設定儲存完成")
            
        except Exception as e:
            logger.error(f"儲存設定失敗: {e}")
    
    def reset_category_to_default(self, category: str):
        """重置類別設定為預設值"""
        try:
            if category in self.settings_modules and self.settings_modules[category]:
                module = self.settings_modules[category]
                if hasattr(module, 'reset_to_defaults'):
                    module.reset_to_defaults()
            
            # 從快取移除
            if category in self.settings_cache:
                del self.settings_cache[category]
            
            # 重新載入預設值
            self._load_default_settings()
            
            logger.info(f"重置設定為預設值: {category}")
            
        except Exception as e:
            logger.error(f"重置設定失敗 {category}: {e}")
    
    def export_settings(self, file_path: str):
        """匯出設定到檔案"""
        try:
            all_settings = {}
            
            for category in self.settings_modules.keys():
                all_settings[category] = self.get_category_settings(category)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(all_settings, f, indent=2, ensure_ascii=False)
            
            logger.info(f"設定匯出完成: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"設定匯出失敗: {e}")
            return False
    
    def import_settings(self, file_path: str):
        """從檔案匯入設定"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                all_settings = json.load(f)
            
            for category, settings in all_settings.items():
                self.update_category_settings(category, settings)
            
            logger.info(f"設定匯入完成: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"設定匯入失敗: {e}")
            return False
    
    def get_settings_summary(self) -> Dict[str, Any]:
        """取得設定摘要"""
        summary = {
            'categories': list(self.settings_modules.keys()),
            'loaded_modules': {
                category: module is not None 
                for category, module in self.settings_modules.items()
            },
            'config_directory': str(self.config_dir)
        }
        
        return summary