"""
軟片模擬設定模組
管理軟片模擬效果的預設值與自訂參數
"""

import json
import os
from typing import Dict, List, Optional, Union

class FilmSettings:
    """軟片模擬設定管理器"""
    
    def __init__(self, config_path: str = "config/film_settings.json"):
        """初始化軟片模擬設定"""
        self.config_path = os.path.abspath(config_path)
        
        # 當前軟片模式
        self.current_film = "standard"
        
        # Fujifilm 軟片模擬效果
        self.fujifilm_films = {
            "standard": {
                "label": "標準",
                "description": "平衡的色彩表現",
                "parameters": {
                    "saturation": 0.0,
                    "contrast": 0.0,
                    "highlights": 0.0,
                    "shadows": 0.0,
                    "grain": 0.0,
                    "vignetting": 0.0
                }
            },
            "vivid": {
                "label": "鮮豔",
                "description": "高飽和度與對比度",
                "parameters": {
                    "saturation": 0.3,
                    "contrast": 0.2,
                    "highlights": -0.1,
                    "shadows": 0.1,
                    "grain": 0.0,
                    "vignetting": 0.1
                }
            },
            "provia": {
                "label": "Provia",
                "description": "自然色彩，適合風景",
                "parameters": {
                    "saturation": 0.1,
                    "contrast": 0.1,
                    "highlights": 0.0,
                    "shadows": 0.0,
                    "grain": 0.05,
                    "vignetting": 0.0
                }
            },
            "velvia": {
                "label": "Velvia", 
                "description": "濃郁色彩，強烈對比",
                "parameters": {
                    "saturation": 0.4,
                    "contrast": 0.3,
                    "highlights": -0.2,
                    "shadows": 0.2,
                    "grain": 0.1,
                    "vignetting": 0.2
                }
            },
            "astia": {
                "label": "Astia",
                "description": "柔和膚色表現",
                "parameters": {
                    "saturation": -0.1,
                    "contrast": -0.1,
                    "highlights": 0.1,
                    "shadows": -0.1,
                    "grain": 0.0,
                    "vignetting": 0.0
                }
            },
            "classic_chrome": {
                "label": "經典Chrome",
                "description": "復古膠片色調",
                "parameters": {
                    "saturation": -0.2,
                    "contrast": 0.2,
                    "highlights": -0.1,
                    "shadows": 0.1,
                    "grain": 0.2,
                    "vignetting": 0.3
                }
            },
            "pro_neg_hi": {
                "label": "Pro Neg. Hi",
                "description": "專業負片，高對比",
                "parameters": {
                    "saturation": 0.0,
                    "contrast": 0.2,
                    "highlights": -0.15,
                    "shadows": 0.15,
                    "grain": 0.15,
                    "vignetting": 0.1
                }
            },
            "pro_neg_std": {
                "label": "Pro Neg. Std",
                "description": "專業負片，標準",
                "parameters": {
                    "saturation": -0.05,
                    "contrast": 0.1,
                    "highlights": -0.1,
                    "shadows": 0.1,
                    "grain": 0.1,
                    "vignetting": 0.05
                }
            },
            "classic_neg": {
                "label": "經典負片",
                "description": "復古負片效果",
                "parameters": {
                    "saturation": -0.1,
                    "contrast": -0.1,
                    "highlights": 0.1,
                    "shadows": -0.1,
                    "grain": 0.25,
                    "vignetting": 0.2
                }
            },
            "eterna": {
                "label": "Eterna",
                "description": "電影感色調",
                "parameters": {
                    "saturation": -0.2,
                    "contrast": -0.2,
                    "highlights": 0.0,
                    "shadows": 0.0,
                    "grain": 0.1,
                    "vignetting": 0.1
                }
            },
            "acros": {
                "label": "Acros",
                "description": "高質感黑白",
                "parameters": {
                    "saturation": -1.0,  # 黑白
                    "contrast": 0.1,
                    "highlights": 0.0,
                    "shadows": 0.0,
                    "grain": 0.2,
                    "vignetting": 0.1
                }
            },
            "monochrome": {
                "label": "單色",
                "description": "經典黑白",
                "parameters": {
                    "saturation": -1.0,  # 黑白
                    "contrast": 0.0,
                    "highlights": 0.0,
                    "shadows": 0.0,
                    "grain": 0.15,
                    "vignetting": 0.0
                }
            }
        }
        
        # 自訂參數調整
        self.custom_adjustments = {
            "saturation_offset": 0.0,    # -0.5 ~ +0.5
            "contrast_offset": 0.0,      # -0.5 ~ +0.5
            "highlights_offset": 0.0,    # -0.5 ~ +0.5
            "shadows_offset": 0.0,       # -0.5 ~ +0.5
            "grain_intensity": 1.0,      # 0.0 ~ 2.0
            "vignetting_strength": 1.0   # 0.0 ~ 2.0
        }
        
        # 載入設定檔案
        self.load_settings()
    
    def get_available_films(self) -> List[str]:
        """取得所有可用的軟片類型"""
        return list(self.fujifilm_films.keys())
    
    def get_film_info(self, film_name: str) -> Optional[Dict]:
        """取得軟片的詳細資訊"""
        return self.fujifilm_films.get(film_name)
    
    def get_current_film_parameters(self) -> Dict[str, float]:
        """取得當前軟片的參數（包含自訂調整）"""
        if self.current_film not in self.fujifilm_films:
            return {}
        
        base_params = self.fujifilm_films[self.current_film]["parameters"].copy()
        
        # 套用自訂調整
        base_params["saturation"] += self.custom_adjustments["saturation_offset"]
        base_params["contrast"] += self.custom_adjustments["contrast_offset"] 
        base_params["highlights"] += self.custom_adjustments["highlights_offset"]
        base_params["shadows"] += self.custom_adjustments["shadows_offset"]
        base_params["grain"] *= self.custom_adjustments["grain_intensity"]
        base_params["vignetting"] *= self.custom_adjustments["vignetting_strength"]
        
        # 限制參數範圍
        base_params["saturation"] = max(-1.0, min(1.0, base_params["saturation"]))
        base_params["contrast"] = max(-1.0, min(1.0, base_params["contrast"]))
        base_params["highlights"] = max(-1.0, min(1.0, base_params["highlights"]))
        base_params["shadows"] = max(-1.0, min(1.0, base_params["shadows"]))
        base_params["grain"] = max(0.0, min(2.0, base_params["grain"]))
        base_params["vignetting"] = max(0.0, min(2.0, base_params["vignetting"]))
        
        return base_params
    
    def set_film(self, film_name: str) -> bool:
        """設定當前軟片類型"""
        if film_name in self.fujifilm_films:
            self.current_film = film_name
            return True
        return False
    
    def adjust_custom_parameter(self, param_name: str, value: float) -> bool:
        """調整自訂參數"""
        if param_name in self.custom_adjustments:
            # 根據參數類型限制範圍
            if param_name in ["saturation_offset", "contrast_offset", "highlights_offset", "shadows_offset"]:
                value = max(-0.5, min(0.5, value))
            elif param_name in ["grain_intensity", "vignetting_strength"]:
                value = max(0.0, min(2.0, value))
            
            self.custom_adjustments[param_name] = value
            return True
        return False
    
    def reset_custom_adjustments(self):
        """重置所有自訂調整"""
        self.custom_adjustments = {
            "saturation_offset": 0.0,
            "contrast_offset": 0.0,
            "highlights_offset": 0.0,
            "shadows_offset": 0.0,
            "grain_intensity": 1.0,
            "vignetting_strength": 1.0
        }
    
    def create_custom_film(self, name: str, label: str, description: str, parameters: Dict[str, float]) -> bool:
        """創建自訂軟片預設"""
        if name not in self.fujifilm_films:
            self.fujifilm_films[name] = {
                "label": label,
                "description": description,
                "parameters": parameters,
                "custom": True
            }
            return True
        return False
    
    def delete_custom_film(self, name: str) -> bool:
        """刪除自訂軟片預設"""
        if name in self.fujifilm_films and self.fujifilm_films[name].get("custom", False):
            del self.fujifilm_films[name]
            if self.current_film == name:
                self.current_film = "standard"
            return True
        return False
    
    def save_settings(self):
        """儲存設定到檔案"""
        try:
            config_dir = os.path.dirname(self.config_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            settings_data = {
                "current_film": self.current_film,
                "custom_adjustments": self.custom_adjustments,
                "custom_films": {
                    name: data for name, data in self.fujifilm_films.items() 
                    if data.get("custom", False)
                }
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"儲存軟片設定失敗: {e}")
    
    def load_settings(self):
        """從檔案載入設定"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    settings_data = json.load(f)
                
                # 載入基本設定
                self.current_film = settings_data.get("current_film", "standard")
                self.custom_adjustments.update(settings_data.get("custom_adjustments", {}))
                
                # 載入自訂軟片
                custom_films = settings_data.get("custom_films", {})
                for name, data in custom_films.items():
                    self.fujifilm_films[name] = data
                    
        except Exception as e:
            print(f"載入軟片設定失敗: {e}")
    
    def get_settings_info(self) -> Dict:
        """取得設定資訊摘要"""
        return {
            "current_film": self.current_film,
            "current_film_label": self.fujifilm_films.get(self.current_film, {}).get("label", "未知"),
            "available_films_count": len(self.fujifilm_films),
            "custom_films_count": sum(1 for data in self.fujifilm_films.values() if data.get("custom", False)),
            "custom_adjustments_active": any(v != 0.0 for v in [
                self.custom_adjustments["saturation_offset"],
                self.custom_adjustments["contrast_offset"],
                self.custom_adjustments["highlights_offset"],
                self.custom_adjustments["shadows_offset"]
            ]) or any(v != 1.0 for v in [
                self.custom_adjustments["grain_intensity"],
                self.custom_adjustments["vignetting_strength"]
            ])
        }