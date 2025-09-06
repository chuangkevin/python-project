"""
相機參數設定模組
管理相機的拍攝參數、影像品質等設定
"""

import json
import os
from typing import Dict, List, Optional, Union

class CameraSettings:
    """相機設定管理器"""
    
    def __init__(self, config_path: str = "config/camera_settings.json"):
        """初始化相機設定"""
        self.config_path = os.path.abspath(config_path)
        
        # 影像設定
        self.image_quality = "high"  # high, medium, low
        self.capture_format = "jpeg"  # jpeg, raw, both
        self.jpeg_quality = 95       # JPEG 品質 (1-100)
        self.image_size = "full"     # full, large, medium, small
        
        # 錄影設定
        self.video_resolution = "1080p"  # 4k, 1080p, 720p, 480p
        self.video_framerate = 30        # 24, 30, 60
        self.video_bitrate = "auto"      # auto, high, medium, low
        self.video_format = "mp4"        # mp4, mov
        
        # 對焦設定
        self.autofocus_mode = "continuous"  # single, continuous, manual
        self.focus_area = "center"          # center, wide, spot, tracking
        self.manual_focus_position = 0.5    # 0.0 (近) ~ 1.0 (遠)
        
        # 曝光設定
        self.metering_mode = "center"    # center, matrix, spot
        self.exposure_mode = "auto"      # auto, manual, aperture_priority, shutter_priority
        self.iso_mode = "auto"           # auto, manual
        self.iso_range = (100, 3200)    # (min, max)
        self.exposure_compensation = 0.0 # -3.0 ~ +3.0 EV
        
        # 白平衡設定
        self.white_balance_mode = "auto"  # auto, daylight, cloudy, incandescent, etc.
        self.white_balance_gains = (1.0, 1.0)  # (red, blue) gains
        
        # 特殊功能
        self.hdr_enabled = False
        self.noise_reduction = "auto"    # auto, off, low, medium, high
        self.sharpness = 0               # -2 ~ +2
        self.contrast = 0                # -2 ~ +2
        self.saturation = 0              # -2 ~ +2
        
        # 載入設定
        self.load_settings()
        
    def get_image_settings(self) -> Dict:
        """取得影像設定"""
        return {
            "quality": self.image_quality,
            "format": self.capture_format,
            "jpeg_quality": self.jpeg_quality,
            "size": self.image_size,
            "hdr_enabled": self.hdr_enabled,
            "noise_reduction": self.noise_reduction,
            "sharpness": self.sharpness,
            "contrast": self.contrast,
            "saturation": self.saturation
        }
    
    def set_image_quality(self, quality: str) -> bool:
        """設定影像品質"""
        if quality in ["high", "medium", "low"]:
            self.image_quality = quality
            
            # 根據品質調整其他參數
            quality_settings = {
                "high": {"jpeg_quality": 95, "noise_reduction": "low"},
                "medium": {"jpeg_quality": 85, "noise_reduction": "medium"},
                "low": {"jpeg_quality": 70, "noise_reduction": "high"}
            }
            
            settings = quality_settings[quality]
            self.jpeg_quality = settings["jpeg_quality"]
            self.noise_reduction = settings["noise_reduction"]
            
            print(f"影像品質已設定為: {quality}")
            return True
        else:
            print(f"無效的影像品質: {quality}")
            return False
    
    def set_capture_format(self, format_type: str) -> bool:
        """設定拍攝格式"""
        if format_type in ["jpeg", "raw", "both"]:
            self.capture_format = format_type
            print(f"拍攝格式已設定為: {format_type}")
            return True
        else:
            print(f"無效的拍攝格式: {format_type}")
            return False
    
    def get_video_settings(self) -> Dict:
        """取得錄影設定"""
        return {
            "resolution": self.video_resolution,
            "framerate": self.video_framerate,
            "bitrate": self.video_bitrate,
            "format": self.video_format
        }
    
    def set_video_resolution(self, resolution: str) -> bool:
        """設定錄影解析度"""
        valid_resolutions = ["4k", "1080p", "720p", "480p"]
        if resolution in valid_resolutions:
            self.video_resolution = resolution
            
            # 根據解析度調整位元率
            bitrate_settings = {
                "4k": "high",
                "1080p": "medium", 
                "720p": "medium",
                "480p": "low"
            }
            
            if self.video_bitrate == "auto":
                self.video_bitrate = bitrate_settings.get(resolution, "medium")
            
            print(f"錄影解析度已設定為: {resolution}")
            return True
        else:
            print(f"無效的錄影解析度: {resolution}")
            return False
    
    def set_video_framerate(self, framerate: int) -> bool:
        """設定錄影幀率"""
        if framerate in [24, 30, 60]:
            self.video_framerate = framerate
            print(f"錄影幀率已設定為: {framerate} fps")
            return True
        else:
            print(f"無效的錄影幀率: {framerate}")
            return False
    
    def set_autofocus_mode(self, mode: str) -> bool:
        """設定自動對焦模式"""
        if mode in ["single", "continuous", "manual"]:
            self.autofocus_mode = mode
            print(f"對焦模式已設定為: {mode}")
            return True
        else:
            print(f"無效的對焦模式: {mode}")
            return False
    
    def set_exposure_mode(self, mode: str) -> bool:
        """設定曝光模式"""
        valid_modes = ["auto", "manual", "aperture_priority", "shutter_priority"]
        if mode in valid_modes:
            self.exposure_mode = mode
            print(f"曝光模式已設定為: {mode}")
            return True
        else:
            print(f"無效的曝光模式: {mode}")
            return False
    
    def set_iso_range(self, min_iso: int, max_iso: int) -> bool:
        """設定 ISO 範圍"""
        if 50 <= min_iso <= max_iso <= 12800:
            self.iso_range = (min_iso, max_iso)
            print(f"ISO 範圍已設定為: {min_iso} - {max_iso}")
            return True
        else:
            print(f"無效的 ISO 範圍: {min_iso} - {max_iso}")
            return False
    
    def set_exposure_compensation(self, ev: float) -> bool:
        """設定曝光補償"""
        if -3.0 <= ev <= 3.0:
            self.exposure_compensation = ev
            print(f"曝光補償已設定為: {ev:+.1f} EV")
            return True
        else:
            print(f"無效的曝光補償值: {ev}")
            return False
    
    def set_white_balance_mode(self, mode: str) -> bool:
        """設定白平衡模式"""
        valid_modes = ["auto", "daylight", "cloudy", "incandescent", "fluorescent", "shade", "manual"]
        if mode in valid_modes:
            self.white_balance_mode = mode
            print(f"白平衡模式已設定為: {mode}")
            return True
        else:
            print(f"無效的白平衡模式: {mode}")
            return False
    
    def enable_hdr(self, enabled: bool):
        """啟用/關閉 HDR"""
        self.hdr_enabled = enabled
        print(f"HDR 已{'啟用' if enabled else '關閉'}")
    
    def set_image_enhancement(self, sharpness: int = None, contrast: int = None, saturation: int = None) -> bool:
        """設定影像增強參數"""
        success = True
        
        if sharpness is not None:
            if -2 <= sharpness <= 2:
                self.sharpness = sharpness
                print(f"銳利度已設定為: {sharpness}")
            else:
                print(f"無效的銳利度值: {sharpness}")
                success = False
        
        if contrast is not None:
            if -2 <= contrast <= 2:
                self.contrast = contrast
                print(f"對比度已設定為: {contrast}")
            else:
                print(f"無效的對比度值: {contrast}")
                success = False
        
        if saturation is not None:
            if -2 <= saturation <= 2:
                self.saturation = saturation
                print(f"飽和度已設定為: {saturation}")
            else:
                print(f"無效的飽和度值: {saturation}")
                success = False
        
        return success
    
    def get_all_settings(self) -> Dict:
        """取得所有設定"""
        return {
            "image": self.get_image_settings(),
            "video": self.get_video_settings(),
            "focus": {
                "mode": self.autofocus_mode,
                "area": self.focus_area,
                "manual_position": self.manual_focus_position
            },
            "exposure": {
                "mode": self.exposure_mode,
                "metering": self.metering_mode,
                "iso_mode": self.iso_mode,
                "iso_range": self.iso_range,
                "compensation": self.exposure_compensation
            },
            "white_balance": {
                "mode": self.white_balance_mode,
                "gains": self.white_balance_gains
            }
        }
    
    def save_settings(self) -> bool:
        """儲存相機設定"""
        try:
            # 確保配置目錄存在
            config_dir = os.path.dirname(self.config_path)
            os.makedirs(config_dir, exist_ok=True)
            
            settings_data = self.get_all_settings()
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(settings_data, f, ensure_ascii=False, indent=2)
            
            print(f"相機設定已儲存至: {self.config_path}")
            return True
            
        except Exception as e:
            print(f"儲存相機設定失敗: {e}")
            return False
    
    def load_settings(self) -> bool:
        """載入相機設定"""
        try:
            if not os.path.exists(self.config_path):
                print(f"設定檔案不存在，使用預設設定: {self.config_path}")
                return True
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                settings_data = json.load(f)
            
            # 載入影像設定
            if "image" in settings_data:
                image = settings_data["image"]
                self.image_quality = image.get("quality", self.image_quality)
                self.capture_format = image.get("format", self.capture_format)
                self.jpeg_quality = image.get("jpeg_quality", self.jpeg_quality)
                self.image_size = image.get("size", self.image_size)
                self.hdr_enabled = image.get("hdr_enabled", self.hdr_enabled)
                self.noise_reduction = image.get("noise_reduction", self.noise_reduction)
                self.sharpness = image.get("sharpness", self.sharpness)
                self.contrast = image.get("contrast", self.contrast)
                self.saturation = image.get("saturation", self.saturation)
            
            # 載入錄影設定
            if "video" in settings_data:
                video = settings_data["video"]
                self.video_resolution = video.get("resolution", self.video_resolution)
                self.video_framerate = video.get("framerate", self.video_framerate)
                self.video_bitrate = video.get("bitrate", self.video_bitrate)
                self.video_format = video.get("format", self.video_format)
            
            # 載入對焦設定
            if "focus" in settings_data:
                focus = settings_data["focus"]
                self.autofocus_mode = focus.get("mode", self.autofocus_mode)
                self.focus_area = focus.get("area", self.focus_area)
                self.manual_focus_position = focus.get("manual_position", self.manual_focus_position)
            
            # 載入曝光設定
            if "exposure" in settings_data:
                exposure = settings_data["exposure"]
                self.exposure_mode = exposure.get("mode", self.exposure_mode)
                self.metering_mode = exposure.get("metering", self.metering_mode)
                self.iso_mode = exposure.get("iso_mode", self.iso_mode)
                self.iso_range = tuple(exposure.get("iso_range", self.iso_range))
                self.exposure_compensation = exposure.get("compensation", self.exposure_compensation)
            
            # 載入白平衡設定
            if "white_balance" in settings_data:
                wb = settings_data["white_balance"]
                self.white_balance_mode = wb.get("mode", self.white_balance_mode)
                self.white_balance_gains = tuple(wb.get("gains", self.white_balance_gains))
            
            print(f"相機設定已載入: {self.config_path}")
            return True
            
        except Exception as e:
            print(f"載入相機設定失敗: {e}")
            return False
    
    def reset_to_defaults(self):
        """重置為預設設定"""
        # 儲存原始配置路徑
        config_path = self.config_path
        
        # 重置所有參數為預設值
        self.image_quality = "high"
        self.capture_format = "jpeg"
        self.jpeg_quality = 95
        self.image_size = "full"
        self.video_resolution = "1080p"
        self.video_framerate = 30
        self.video_bitrate = "auto"
        self.video_format = "mp4"
        self.autofocus_mode = "continuous"
        self.focus_area = "center"
        self.manual_focus_position = 0.5
        self.metering_mode = "center"
        self.exposure_mode = "auto"
        self.iso_mode = "auto"
        self.iso_range = (100, 3200)
        self.exposure_compensation = 0.0
        self.white_balance_mode = "auto"
        self.white_balance_gains = (1.0, 1.0)
        self.hdr_enabled = False
        self.noise_reduction = "auto"
        self.sharpness = 0
        self.contrast = 0
        self.saturation = 0
        
        # 恢復配置路徑
        self.config_path = config_path
        print("相機設定已重置為預設值")