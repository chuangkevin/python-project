"""
雙轉盤設定模組
管理雙轉盤的行為、靈敏度、配置檔案等
"""

import json
import os
import shutil
from typing import Dict, List, Optional

class DialSettings:
    """雙轉盤設定管理器"""
    
    def __init__(self, config_dir: str = "config/dial_profiles"):
        """初始化轉盤設定"""
        # 設定路徑
        self.config_dir = os.path.abspath(config_dir)
        self.current_profile = "default"
        
        # 轉盤行為設定
        self.left_dial_sensitivity = 1.0    # 左轉盤靈敏度
        self.right_dial_sensitivity = 1.0   # 右轉盤靈敏度
        self.dial_direction_reversed = False # 轉盤方向是否反轉
        self.long_press_threshold = 800     # 長按時間閾值 (毫秒)
        
        # 快捷鍵映射
        self.shortcut_mappings = {}
        
        # 載入的配置資料
        self._profile_data = {}
        
        # 確保配置目錄存在
        os.makedirs(self.config_dir, exist_ok=True)
        
    def load_profile(self, profile_name: str) -> bool:
        """載入轉盤配置檔案"""
        try:
            profile_path = os.path.join(self.config_dir, f"{profile_name}.json")
            
            if not os.path.exists(profile_path):
                print(f"警告: 配置檔案不存在: {profile_path}")
                return False
            
            with open(profile_path, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            # 驗證配置格式
            if not self._validate_profile(profile_data):
                print(f"錯誤: 配置檔案格式無效: {profile_name}")
                return False
            
            # 套用配置
            self._apply_profile_settings(profile_data)
            self.current_profile = profile_name
            self._profile_data = profile_data
            
            print(f"成功載入配置: {profile_name}")
            return True
            
        except Exception as e:
            print(f"載入配置失敗 {profile_name}: {e}")
            return False
    
    def save_profile(self, profile_name: str) -> bool:
        """儲存轉盤配置檔案"""
        try:
            # 建立配置資料
            profile_data = {
                "profile_info": {
                    "name": profile_name,
                    "description": f"{profile_name} 轉盤配置",
                    "version": "1.0.0",
                    "created_date": "2024-01-01",
                    "author": "User"
                },
                "dial_behavior": {
                    "left_sensitivity": self.left_dial_sensitivity,
                    "right_sensitivity": self.right_dial_sensitivity,
                    "direction_reversed": self.dial_direction_reversed,
                    "long_press_threshold": self.long_press_threshold
                },
                "shortcuts": self.shortcut_mappings
            }
            
            # 如果有現有的模式配置，保留它
            if hasattr(self, '_profile_data') and 'mode_configuration' in self._profile_data:
                profile_data['mode_configuration'] = self._profile_data['mode_configuration']
            
            # 儲存檔案
            profile_path = os.path.join(self.config_dir, f"{profile_name}.json")
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, ensure_ascii=False, indent=2)
            
            print(f"成功儲存配置: {profile_name}")
            return True
            
        except Exception as e:
            print(f"儲存配置失敗 {profile_name}: {e}")
            return False
    
    def get_available_profiles(self) -> List[str]:
        """取得可用的配置檔案列表"""
        try:
            if not os.path.exists(self.config_dir):
                return []
            
            profiles = []
            for file in os.listdir(self.config_dir):
                if file.endswith('.json'):
                    profile_name = file[:-5]  # 移除 .json 副檔名
                    profiles.append(profile_name)
            
            return sorted(profiles)
            
        except Exception as e:
            print(f"獲取配置列表失敗: {e}")
            return []
    
    def create_profile(self, profile_name: str, base_profile: str = "default") -> bool:
        """建立新的配置檔案"""
        try:
            # 檢查是否已存在
            if profile_name in self.get_available_profiles():
                print(f"配置已存在: {profile_name}")
                return False
            
            # 載入基礎配置
            if base_profile != profile_name and not self.load_profile(base_profile):
                print(f"基礎配置載入失敗: {base_profile}")
                return False
            
            # 儲存為新配置
            return self.save_profile(profile_name)
            
        except Exception as e:
            print(f"建立配置失敗 {profile_name}: {e}")
            return False
    
    def delete_profile(self, profile_name: str) -> bool:
        """刪除配置檔案"""
        try:
            # 保護預設配置
            if profile_name == "default":
                print("錯誤: 不能刪除預設配置")
                return False
            
            profile_path = os.path.join(self.config_dir, f"{profile_name}.json")
            
            if not os.path.exists(profile_path):
                print(f"配置檔案不存在: {profile_name}")
                return False
            
            os.remove(profile_path)
            print(f"成功刪除配置: {profile_name}")
            
            # 如果刪除的是當前配置，切換到預設配置
            if self.current_profile == profile_name:
                self.load_profile("default")
            
            return True
            
        except Exception as e:
            print(f"刪除配置失敗 {profile_name}: {e}")
            return False
    
    def export_profile(self, profile_name: str, export_path: str) -> bool:
        """匯出配置檔案"""
        try:
            source_path = os.path.join(self.config_dir, f"{profile_name}.json")
            
            if not os.path.exists(source_path):
                print(f"配置檔案不存在: {profile_name}")
                return False
            
            shutil.copy2(source_path, export_path)
            print(f"成功匯出配置: {profile_name} -> {export_path}")
            return True
            
        except Exception as e:
            print(f"匯出配置失敗 {profile_name}: {e}")
            return False
    
    def import_profile(self, import_path: str, profile_name: str) -> bool:
        """匯入配置檔案"""
        try:
            if not os.path.exists(import_path):
                print(f"匯入檔案不存在: {import_path}")
                return False
            
            # 驗證檔案格式
            with open(import_path, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            if not self._validate_profile(profile_data):
                print("匯入檔案格式無效")
                return False
            
            # 複製到配置目錄
            target_path = os.path.join(self.config_dir, f"{profile_name}.json")
            shutil.copy2(import_path, target_path)
            
            print(f"成功匯入配置: {import_path} -> {profile_name}")
            return True
            
        except Exception as e:
            print(f"匯入配置失敗 {profile_name}: {e}")
            return False
    
    def set_dial_sensitivity(self, left: float, right: float):
        """設定轉盤靈敏度"""
        self.left_dial_sensitivity = max(0.1, min(2.0, left))
        self.right_dial_sensitivity = max(0.1, min(2.0, right))
        print(f"轉盤靈敏度已設定: 左={self.left_dial_sensitivity}, 右={self.right_dial_sensitivity}")
    
    def get_current_profile_info(self) -> Dict:
        """取得當前配置檔案資訊"""
        return {
            "name": self.current_profile,
            "left_sensitivity": self.left_dial_sensitivity,
            "right_sensitivity": self.right_dial_sensitivity,
            "direction_reversed": self.dial_direction_reversed,
            "long_press_threshold": self.long_press_threshold,
            "shortcuts": self.shortcut_mappings.copy(),
            "profile_data": self._profile_data.copy() if self._profile_data else {}
        }
    
    def _validate_profile(self, profile_data: Dict) -> bool:
        """驗證配置檔案格式"""
        try:
            # 檢查必要欄位
            required_fields = ["profile_info", "dial_behavior"]
            for field in required_fields:
                if field not in profile_data:
                    return False
            
            # 檢查轉盤行為欄位
            behavior = profile_data["dial_behavior"]
            behavior_fields = ["left_sensitivity", "right_sensitivity", "long_press_threshold"]
            for field in behavior_fields:
                if field not in behavior:
                    return False
            
            return True
            
        except Exception:
            return False
    
    def _apply_profile_settings(self, profile_data: Dict):
        """套用配置設定"""
        try:
            behavior = profile_data["dial_behavior"]
            
            self.left_dial_sensitivity = behavior.get("left_sensitivity", 1.0)
            self.right_dial_sensitivity = behavior.get("right_sensitivity", 1.0)
            self.dial_direction_reversed = behavior.get("direction_reversed", False)
            self.long_press_threshold = behavior.get("long_press_threshold", 800)
            
            # 載入快捷鍵
            self.shortcut_mappings = profile_data.get("shortcuts", {})
            
        except Exception as e:
            print(f"套用配置設定失敗: {e}")
    
    def get_stateMachineControl_config(self) -> Optional[Dict]:
        """取得 stateMachineControl 相容的配置"""
        try:
            if 'mode_configuration' in self._profile_data:
                mode_config = self._profile_data['mode_configuration']
                
                # 如果配置是 "inherit_from_stateMachineControl"，回傳 None 讓系統使用預設
                if mode_config == "inherit_from_stateMachineControl":
                    return None
                
                return mode_config
            
            return None
            
        except Exception as e:
            print(f"取得 stateMachineControl 配置失敗: {e}")
            return None