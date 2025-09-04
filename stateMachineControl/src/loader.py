"""
配置檔案載入器
負責載入、驗證和解析 JSON 配置檔案
"""

import json
import os
from typing import Dict, Any, Optional, List
try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    print("Warning: jsonschema not available, skipping validation")


class ConfigLoader:
    """JSON 配置檔案載入和驗證器"""
    
    def __init__(self, config_path: Optional[str] = None, schema_path: Optional[str] = None):
        """
        初始化配置載入器
        
        Args:
            config_path: 配置檔案路徑
            schema_path: JSON Schema 檔案路徑
        """
        self.config_path = config_path
        self.schema_path = schema_path
        self.config_data = None
        self.schema_data = None
        
        if config_path:
            self.load_config(config_path)
        if schema_path:
            self.load_schema(schema_path)
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """載入配置檔案"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            self.config_path = config_path
            return self.config_data
        except FileNotFoundError:
            raise FileNotFoundError(f"配置檔案不存在: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 格式錯誤: {e}")
    
    def load_schema(self, schema_path: str) -> Dict[str, Any]:
        """載入 JSON Schema"""
        try:
            with open(schema_path, 'r', encoding='utf-8') as f:
                self.schema_data = json.load(f)
            self.schema_path = schema_path
            return self.schema_data
        except FileNotFoundError:
            raise FileNotFoundError(f"Schema 檔案不存在: {schema_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Schema JSON 格式錯誤: {e}")
    
    def validate_config(self) -> bool:
        """驗證配置檔案是否符合 Schema"""
        if not HAS_JSONSCHEMA:
            print("Warning: jsonschema not available, skipping validation")
            return True
            
        if not self.config_data:
            raise ValueError("尚未載入配置檔案")
        if not self.schema_data:
            raise ValueError("尚未載入 Schema")
        
        try:
            jsonschema.validate(self.config_data, self.schema_data)
            return True
        except jsonschema.ValidationError as e:
            raise ValueError(f"配置檔案驗證失敗: {e.message}")
    
    def get_dial_order(self) -> List[str]:
        """取得左轉盤模式順序"""
        if not self.config_data:
            return []
        return self.config_data.get("dialOrder", [])
    
    def get_modes(self) -> List[Dict[str, Any]]:
        """取得所有模式定義"""
        if not self.config_data:
            return []
        return self.config_data.get("modes", [])
    
    def get_mode_by_id(self, mode_id: str) -> Optional[Dict[str, Any]]:
        """根據 ID 取得特定模式"""
        modes = self.get_modes()
        for mode in modes:
            if mode.get("id") == mode_id:
                return mode
        return None
    
    def get_ui_config(self) -> Dict[str, Any]:
        """取得 UI 配置"""
        if not self.config_data:
            return {}
        return self.config_data.get("ui", {})
    
    def get_icons(self) -> Dict[str, str]:
        """取得圖示對應表"""
        ui_config = self.get_ui_config()
        return ui_config.get("icons", {})
    
    @staticmethod
    def load_default_config() -> 'ConfigLoader':
        """載入預設配置檔案"""
        # 取得當前檔案所在目錄
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        
        config_path = os.path.join(project_root, "configs", "mode_dial.default.json")
        schema_path = os.path.join(project_root, "schema", "mode_dial.schema.json")
        
        loader = ConfigLoader()
        
        if os.path.exists(config_path):
            loader.load_config(config_path)
        
        if os.path.exists(schema_path):
            loader.load_schema(schema_path)
            
        return loader
    
    def __str__(self) -> str:
        """字串表示"""
        return f"ConfigLoader(config='{self.config_path}', modes={len(self.get_modes())})"