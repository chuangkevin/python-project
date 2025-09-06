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
            profile_name = mode if mode != "photo" else "default"
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
    
    def handle_shutter_press(self, press_type: str):
        """
        處理快門按鈕事件
        
        Args:
            press_type: "half" 或 "full"
        """
        if not self.system_initialized or not self.mode_dial:
            return

        active_mode_id = self.mode_dial.get_current_active_mode_id()

        # 檢查是否處於白卡測光模式
        if active_mode_id == "wb_whitecard":
            if press_type == "full":
                print("📷 觸發白卡測光...")
                self._perform_white_balance_capture()
            return

        # 一般拍照模式
        if press_type == "half":
            print("📷 半按快門：執行自動對焦...")
            # TODO: 呼叫相機執行自動對焦
            # self.camera_settings.trigger_autofocus()
        elif press_type == "full":
            print("📷 全按快門：執行拍攝...")
            # TODO: 呼叫相機執行拍攝
            # self.camera_settings.capture_image()

    def _perform_white_balance_capture(self):
        """執行白卡測光"""
        # TODO: 實作白卡測光邏輯
        # 1. 擷取當前影像
        # 2. 計算中心區域的平均色彩
        # 3. 計算並套用白平衡增益
        print("⚖️ 正在計算白平衡增益...")
        # self.camera_settings.calculate_custom_white_balance()
        print("✅ 白平衡已校準")
    
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
        try:
            # 載入轉盤設定
            if not self.dial_settings.load_profile(profile_name):
                print(f"載入轉盤配置失敗: {profile_name}")
                return False
            
            # 如果有 ModeDial，套用配置
            if self.mode_dial:
                # 取得轉盤特殊配置
                dial_config = self.dial_settings.get_stateMachineControl_config()
                
                if dial_config is not None:
                    # 套用自訂配置 (目前 stateMachineControl 不支援動態配置載入)
                    print(f"注意: 自訂轉盤配置需要重啟應用程式生效")
                else:
                    print(f"使用 stateMachineControl 預設配置")
                
                # 套用轉盤靈敏度設定 (這個可以即時生效)
                profile_info = self.dial_settings.get_current_profile_info()
                print(f"套用轉盤靈敏度 - 左: {profile_info['left_sensitivity']}, 右: {profile_info['right_sensitivity']}")
            
            return True
            
        except Exception as e:
            print(f"載入轉盤配置錯誤: {e}")
            return False
    
    def _show_settings_menu(self):
        """顯示設定選單"""
        # TODO: 實作設定選單顯示
        pass
    
    def _apply_camera_control(self, control: str, value):
        """套用相機控制"""
        try:
            print(f"套用相機控制: {control} = {value}")
            
            # 根據控制類型套用設定
            if control == "ExposureTime":
                # 快門速度控制
                print(f"  設定快門速度: {value}s")
                
            elif control == "AnalogueGain":
                # ISO 控制
                print(f"  設定 ISO 增益: {value}")
                
            elif control == "ExposureValue":
                # EV 曝光補償
                self.camera_settings.set_exposure_compensation(value)
                
            elif control == "AwbMode":
                # 白平衡模式
                self.camera_settings.set_white_balance_mode(value)
                
            elif control == "ColourGains_AB":
                # 色彩增益調整
                print(f"  設定色彩增益: {value}")
                
            elif control == "AfMode":
                # 對焦模式
                af_mode_map = {
                    "single": "single",
                    "continuous": "continuous", 
                    "manual": "manual"
                }
                mapped_mode = af_mode_map.get(value, "continuous")
                self.camera_settings.set_autofocus_mode(mapped_mode)
                
            elif control == "Metering":
                # 測光模式
                print(f"  設定測光模式: {value}")
                
            elif control == "SelfTimer":
                # 自拍計時器
                print(f"  設定自拍計時器: {value}秒")
                
            elif control == "VideoResolution":
                # 錄影解析度
                resolution_map = {
                    "3840x2160": "4k",
                    "1920x1080": "1080p", 
                    "1280x720": "720p"
                }
                mapped_res = resolution_map.get(value, value)
                self.camera_settings.set_video_resolution(mapped_res)
                
            elif control == "VideoFramerate":
                # 錄影幀率
                self.camera_settings.set_video_framerate(value)
                
            else:
                print(f"  未知的控制類型: {control}")
                
        except Exception as e:
            print(f"套用相機控制失敗 {control}: {e}")
    
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