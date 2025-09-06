"""
系統管理器
統一管理所有系統設定和模組整合
"""

import sys
import os
from typing import Dict, Optional

# 添加 stateMachineControl 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'stateMachineControl', 'src'))

try:
    from state_machine import ModeDial
except ImportError:
    ModeDial = None

from settings import (
    CameraSettings, 
    DisplaySettings, 
    DialSettings, 
    PowerSettings, 
    StorageSettings
)

class SystemManager:
    """系統管理器 - 整合所有子系統"""
    
    def __init__(self):
        """初始化系統管理器"""
        # 初始化各設定模組
        self.camera_settings = CameraSettings()
        self.display_settings = DisplaySettings() 
        self.dial_settings = DialSettings()
        self.power_settings = PowerSettings()
        self.storage_settings = StorageSettings()
        
        # 初始化狀態機 (如果可用)
        self.mode_dial = None
        if ModeDial:
            self.mode_dial = ModeDial()
            self._setup_dial_callbacks()
        
        # 系統狀態
        self.system_initialized = False
        self.current_mode = "photo"  # photo, video, manual
        
    def initialize_system(self) -> bool:
        """初始化整個系統"""
        try:
            # 載入所有設定
            self._load_all_settings()
            
            # 初始化硬體 (預留)
            self._initialize_hardware()
            
            # 設定雙轉盤配置
            if self.mode_dial and self.dial_settings:
                profile = self.dial_settings.current_profile
                self._load_dial_profile(profile)
            
            self.system_initialized = True
            return True
            
        except Exception as e:
            print(f"系統初始化失敗: {e}")
            return False
    
    def shutdown_system(self):
        """關閉系統"""
        try:
            # 儲存所有設定
            self._save_all_settings()
            
            # 安全關機程序
            self.power_settings.safe_shutdown()
            
        except Exception as e:
            print(f"系統關機錯誤: {e}")
    
    def switch_mode(self, mode: str) -> bool:
        """切換系統模式 (拍照/錄影/手動)"""
        if mode not in ["photo", "video", "manual"]:
            return False
            
        self.current_mode = mode
        
        # 載入對應的轉盤配置
        if self.dial_settings:
            profile_name = f"{mode}.json" if mode != "photo" else "default.json"
            return self._load_dial_profile(profile_name)
        
        return True
    
    def get_system_status(self) -> Dict:
        """取得系統狀態"""
        status = {
            "initialized": self.system_initialized,
            "current_mode": self.current_mode,
            "battery_level": None,
            "storage_info": None,
            "temperature": None
        }
        
        # 取得電池狀態
        if self.power_settings:
            status["battery_level"] = self.power_settings.get_battery_status()
        
        # 取得儲存資訊  
        if self.storage_settings:
            status["storage_info"] = self.storage_settings.get_storage_info()
            
        return status
    
    def _setup_dial_callbacks(self):
        """設定轉盤回調函數"""
        if not self.mode_dial:
            return
            
        self.mode_dial.set_callbacks(
            on_mode_changed=self._on_dial_mode_changed,
            on_value_changed=self._on_dial_value_changed,
            on_binding_triggered=self._on_dial_binding_triggered
        )
    
    def _on_dial_mode_changed(self, mode_index: int, mode: Dict):
        """轉盤模式變更回調"""
        # TODO: 處理模式變更事件
        pass
    
    def _on_dial_value_changed(self, mode_id: str, old_value, new_value):
        """轉盤值變更回調"""
        # TODO: 處理數值變更事件
        pass
    
    def _on_dial_binding_triggered(self, mode_id: str, bindings: Dict, value):
        """轉盤綁定觸發回調"""
        # 處理特殊動作
        if bindings.get("action") == "enter_settings":
            self._show_settings_menu()
        elif bindings.get("control"):
            # 處理相機控制綁定
            self._apply_camera_control(bindings["control"], value)
    
    def _load_dial_profile(self, profile_name: str) -> bool:
        """載入轉盤配置檔案"""
        # TODO: 實作轉盤配置載入
        return True
    
    def _show_settings_menu(self):
        """顯示設定選單"""
        # TODO: 實作設定選單顯示
        pass
    
    def _apply_camera_control(self, control: str, value):
        """套用相機控制"""
        # TODO: 實作相機控制套用
        pass
    
    def _load_all_settings(self):
        """載入所有設定"""
        self.camera_settings.load_settings()
        self.display_settings.load_settings()
        self.dial_settings.load_profile(self.dial_settings.current_profile)
        self.power_settings.load_settings()
        self.storage_settings.load_settings()
    
    def _save_all_settings(self):
        """儲存所有設定"""
        self.camera_settings.save_settings()
        self.display_settings.save_settings()
        self.dial_settings.save_profile(self.dial_settings.current_profile)
        self.power_settings.save_settings()
        self.storage_settings.save_settings()
    
    def _initialize_hardware(self):
        """初始化硬體 (預留)"""
        # TODO: 初始化相機、螢幕、感測器等硬體
        pass