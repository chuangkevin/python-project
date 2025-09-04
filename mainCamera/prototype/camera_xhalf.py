#!/usr/bin/env python3
"""
Fujifilm X-half 風格相機應用程式
分割螢幕設計：左邊預覽，右邊濾鏡選擇（上下滑動）
"""
import sys
import cv2
import numpy as np
import os
from datetime import datetime
from picamera2 import Picamera2
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import threading
import time

class CameraThread(QThread):
    frameReady = pyqtSignal(np.ndarray)
    
    def __init__(self, picam2):
        super().__init__()
        self.picam2 = picam2
        self.running = True
        self.current_filter = 0
        self.exposure_value = 0
        
    def run(self):
        while self.running:
            try:
                frame = self.picam2.capture_array()
                
                # 應用濾鏡
                frame = self.apply_filter(frame)
                
                # 應用曝光調整
                frame = self.adjust_exposure(frame)
                
                self.frameReady.emit(frame)
                time.sleep(0.033)  # ~30 FPS
            except Exception as e:
                print(f"相機錯誤: {e}")
                time.sleep(0.1)
    
    def apply_filter(self, frame):
        """應用 Fujifilm 風格濾鏡效果"""
        if self.current_filter == 0:  # Provia (標準)
            return self.apply_provia(frame)
        elif self.current_filter == 1:  # Velvia (鮮豔飽和)
            return self.apply_velvia(frame)
        elif self.current_filter == 2:  # Astia (柔和人像)
            return self.apply_astia(frame)
        elif self.current_filter == 3:  # Classic Chrome (復古鉵感)
            return self.apply_classic_chrome(frame)
        elif self.current_filter == 4:  # Pro Neg Hi (專業負片高對比)
            return self.apply_pro_neg_hi(frame)
        elif self.current_filter == 5:  # Pro Neg Std (專業負片標準)
            return self.apply_pro_neg_std(frame)
        elif self.current_filter == 6:  # Classic Neg (經典負片)
            return self.apply_classic_neg(frame)
        elif self.current_filter == 7:  # Eterna (電影感)
            return self.apply_eterna(frame)
        elif self.current_filter == 8:  # Acros (黑白膠片)
            return self.apply_acros(frame)
        elif self.current_filter == 9:  # Monochrome (單色)
            return self.apply_monochrome(frame)
        else:
            return frame
    
    def apply_tone_curve(self, channel, shadows=1.0, midtones=1.0, highlights=1.0):
        """精確的色調曲線調整"""
        normalized = channel / 255.0
        
        # 分區調整：陰影 (0-0.33)、中間調 (0.33-0.66)、高光 (0.66-1.0)
        result = normalized.copy()
        
        # 陰影區調整
        shadow_mask = normalized <= 0.33
        result[shadow_mask] = np.power(result[shadow_mask] / 0.33, 1.0/shadows) * 0.33
        
        # 中間調調整  
        midtone_mask = (normalized > 0.33) & (normalized <= 0.66)
        mid_normalized = (normalized[midtone_mask] - 0.33) / 0.33
        result[midtone_mask] = 0.33 + np.power(mid_normalized, 1.0/midtones) * 0.33
        
        # 高光區調整
        highlight_mask = normalized > 0.66
        high_normalized = (normalized[highlight_mask] - 0.66) / 0.34
        result[highlight_mask] = 0.66 + (1.0 - np.power(1.0 - high_normalized, highlights)) * 0.34
        
        return np.clip(result * 255.0, 0, 255).astype(np.uint8)
    
    def apply_color_grading(self, frame, shadows_rgb=(1.0, 1.0, 1.0), midtones_rgb=(1.0, 1.0, 1.0), highlights_rgb=(1.0, 1.0, 1.0)):
        """精確的色彩分級調整"""
        frame = frame.astype(np.float32) / 255.0
        luminance = 0.299 * frame[:,:,0] + 0.587 * frame[:,:,1] + 0.114 * frame[:,:,2]
        
        # 創建亮度遮罩
        shadow_mask = luminance <= 0.33
        midtone_mask = (luminance > 0.33) & (luminance <= 0.66) 
        highlight_mask = luminance > 0.66
        
        result = frame.copy()
        
        # 應用色彩調整
        for i in range(3):  # R, G, B
            result[:,:,i][shadow_mask] *= shadows_rgb[i]
            result[:,:,i][midtone_mask] *= midtones_rgb[i] 
            result[:,:,i][highlight_mask] *= highlights_rgb[i]
        
        return np.clip(result * 255.0, 0, 255).astype(np.uint8)

    def apply_provia(self, frame):
        """PROVIA - 標準自然色彩，適合日常拍攝"""
        frame = frame.astype(np.float32)
        
        # 1. 輕微的對比度提升
        r, g, b = cv2.split(frame)
        r = self.apply_tone_curve(r.astype(np.uint8), shadows=1.02, midtones=1.05, highlights=0.98)
        g = self.apply_tone_curve(g.astype(np.uint8), shadows=1.02, midtones=1.05, highlights=0.98) 
        b = self.apply_tone_curve(b.astype(np.uint8), shadows=1.02, midtones=1.05, highlights=0.98)
        
        frame = cv2.merge([r, g, b]).astype(np.float32)
        
        # 2. LAB 色彩空間微調飽和度
        lab = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
        lab[:,:,1] = (lab[:,:,1] - 128) * 1.08 + 128  # 輕微增加 A 通道
        lab[:,:,2] = (lab[:,:,2] - 128) * 1.08 + 128  # 輕微增加 B 通道
        
        return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB)
    
    def apply_velvia(self, frame):
        """VELVIA - 鮮豔風景底片，強化天空和植物"""
        frame = frame.astype(np.float32)
        
        # 1. 色彩分級：強化藍綠色調
        frame = self.apply_color_grading(frame,
            shadows_rgb=(0.95, 1.02, 1.08),    # 陰影：略減紅，增強藍綠
            midtones_rgb=(1.0, 1.12, 1.05),    # 中間調：強化綠色
            highlights_rgb=(1.02, 1.08, 1.15)  # 高光：強化天空藍色
        )
        
        # 2. 對比度和色調曲線
        r, g, b = cv2.split(frame)
        r = self.apply_tone_curve(r.astype(np.uint8), shadows=1.05, midtones=1.15, highlights=0.95)
        g = self.apply_tone_curve(g.astype(np.uint8), shadows=1.08, midtones=1.18, highlights=0.92)
        b = self.apply_tone_curve(b.astype(np.uint8), shadows=1.10, midtones=1.20, highlights=0.90)
        
        # 3. LAB 空間飽和度調整
        frame = cv2.merge([r, g, b])
        lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB).astype(np.float32)
        lab[:,:,1] = (lab[:,:,1] - 128) * 1.25 + 128  # 強化綠-紅軸
        lab[:,:,2] = (lab[:,:,2] - 128) * 1.30 + 128  # 強化藍-黃軸
        
        return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB)
    
    def apply_astia(self, frame):
        """ASTIA - 柔和人像底片，優化膚色和肉色調"""
        frame = frame.astype(np.float32)
        
        # 1. 膚色友善的色彩分級
        frame = self.apply_color_grading(frame,
            shadows_rgb=(1.03, 1.01, 0.97),    # 陰影：溫暖色調
            midtones_rgb=(1.08, 1.04, 0.96),   # 中間調：增強膚色紅調
            highlights_rgb=(1.05, 1.02, 0.98)  # 高光：保持自然
        )
        
        # 2. 柔和的對比度曲線
        r, g, b = cv2.split(frame)
        r = self.apply_tone_curve(r.astype(np.uint8), shadows=1.03, midtones=1.02, highlights=1.01)
        g = self.apply_tone_curve(g.astype(np.uint8), shadows=1.02, midtones=1.01, highlights=1.01)
        b = self.apply_tone_curve(b.astype(np.uint8), shadows=1.01, midtones=1.00, highlights=1.02)
        
        # 3. LAB 空間細膩調整
        frame = cv2.merge([r, g, b])
        lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB).astype(np.float32)
        lab[:,:,0] = lab[:,:,0] * 1.03 + 8  # 輕微提亮
        lab[:,:,1] = (lab[:,:,1] - 128) * 1.06 + 128 + 2  # 偏暖紅調
        lab[:,:,2] = (lab[:,:,2] - 128) * 0.94 + 128 - 2  # 減弱藍調
        
        return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB)
    
    def apply_classic_chrome(self, frame):
        """CLASSIC CHROME - 復古銀鹽質感，街拍風格"""
        frame = frame.astype(np.float32)
        
        # 1. 銀鹽特有的色彩分級：偏冷調
        frame = self.apply_color_grading(frame,
            shadows_rgb=(0.98, 1.01, 1.05),    # 陰影：偏冷藍調
            midtones_rgb=(0.96, 1.02, 1.06),   # 中間調：持續冷調
            highlights_rgb=(0.94, 1.01, 1.08)  # 高光：明顯冷調
        )
        
        # 2. Classic Chrome 特有的 S 型對比曲線
        r, g, b = cv2.split(frame)
        r = self.apply_tone_curve(r.astype(np.uint8), shadows=0.95, midtones=1.25, highlights=0.92)
        g = self.apply_tone_curve(g.astype(np.uint8), shadows=0.96, midtones=1.22, highlights=0.94)
        b = self.apply_tone_curve(b.astype(np.uint8), shadows=0.98, midtones=1.20, highlights=0.96)
        
        # 3. LAB 空間降低飽和度
        frame = cv2.merge([r, g, b])
        lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB).astype(np.float32)
        lab[:,:,1] = (lab[:,:,1] - 128) * 0.75 + 128  # 大幅降低飽和度
        lab[:,:,2] = (lab[:,:,2] - 128) * 0.80 + 128
        
        return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB)
    
    def apply_pro_neg_hi(self, frame):
        """PRO Neg. Hi - 專業負片高對比，商業攝影風格"""
        frame = frame.astype(np.float32)
        
        # 1. 負片風格色彩分級
        frame = self.apply_color_grading(frame,
            shadows_rgb=(1.05, 0.98, 0.96),    # 陰影：溫暖紅色
            midtones_rgb=(1.08, 1.02, 0.98),   # 中間調：強化紅色
            highlights_rgb=(1.06, 1.03, 1.00)  # 高光：保持平衡
        )
        
        # 2. 高對比色調曲線
        r, g, b = cv2.split(frame)
        r = self.apply_tone_curve(r.astype(np.uint8), shadows=0.92, midtones=1.35, highlights=0.88)
        g = self.apply_tone_curve(g.astype(np.uint8), shadows=0.94, midtones=1.30, highlights=0.90)
        b = self.apply_tone_curve(b.astype(np.uint8), shadows=0.96, midtones=1.25, highlights=0.92)
        
        # 3. 負片風格的飽和度提升
        frame = cv2.merge([r, g, b])
        lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB).astype(np.float32)
        lab[:,:,1] = (lab[:,:,1] - 128) * 1.15 + 128
        lab[:,:,2] = (lab[:,:,2] - 128) * 1.12 + 128
        
        return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB)
    
    def apply_pro_neg_std(self, frame):
        """PRO Neg. Std - 專業負片標準，平衡自然"""
        frame = frame.astype(np.float32)
        
        # 1. 平衡的色彩分級
        frame = self.apply_color_grading(frame,
            shadows_rgb=(1.02, 0.99, 0.98),    # 陰影：輕微溫暖
            midtones_rgb=(1.04, 1.01, 0.99),   # 中間調：保持平衡
            highlights_rgb=(1.03, 1.02, 1.01)  # 高光：自然
        )
        
        # 2. 温和的對比曲線
        r, g, b = cv2.split(frame)
        r = self.apply_tone_curve(r.astype(np.uint8), shadows=0.98, midtones=1.12, highlights=0.96)
        g = self.apply_tone_curve(g.astype(np.uint8), shadows=0.99, midtones=1.10, highlights=0.97)
        b = self.apply_tone_curve(b.astype(np.uint8), shadows=1.00, midtones=1.08, highlights=0.98)
        
        # 3. 温和的飽和度提升
        frame = cv2.merge([r, g, b])
        lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB).astype(np.float32)
        lab[:,:,1] = (lab[:,:,1] - 128) * 1.08 + 128
        lab[:,:,2] = (lab[:,:,2] - 128) * 1.06 + 128
        
        return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB)
    
    def apply_classic_neg(self, frame):
        """CLASSIC Neg. - 經典負片，溫暖懷舊色調"""
        frame = frame.astype(np.float32)
        
        # 1. 懷舊溫暖色彩分級
        frame = self.apply_color_grading(frame,
            shadows_rgb=(1.06, 1.02, 0.94),    # 陰影：溫暖紅黃色
            midtones_rgb=(1.08, 1.04, 0.92),   # 中間調：持續溫暖
            highlights_rgb=(1.05, 1.03, 0.96)  # 高光：柔和溫色
        )
        
        # 2. 經典負片的柔和曲線
        r, g, b = cv2.split(frame)
        r = self.apply_tone_curve(r.astype(np.uint8), shadows=1.05, midtones=1.08, highlights=1.02)
        g = self.apply_tone_curve(g.astype(np.uint8), shadows=1.03, midtones=1.06, highlights=1.01)
        b = self.apply_tone_curve(b.astype(np.uint8), shadows=1.01, midtones=1.04, highlights=1.00)
        
        # 3. 懷舊色調的 LAB 調整
        frame = cv2.merge([r, g, b])
        lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB).astype(np.float32)
        lab[:,:,0] = lab[:,:,0] * 1.02 + 5  # 輕微提亮
        lab[:,:,1] = (lab[:,:,1] - 128) * 1.10 + 128 + 3  # 偏溫色
        lab[:,:,2] = (lab[:,:,2] - 128) * 0.92 + 128 - 4  # 減弱藍調
        
        return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB)
    
    def apply_eterna(self, frame):
        """ETERNA - 電影質感，低飽和低對比"""
        frame = frame.astype(np.float32)
        
        # 1. 電影風格色彩分級：偏綠色調
        frame = self.apply_color_grading(frame,
            shadows_rgb=(0.96, 1.03, 0.99),    # 陰影：輕微綠色調
            midtones_rgb=(0.98, 1.08, 1.01),   # 中間調：明顯綠色
            highlights_rgb=(0.99, 1.05, 1.02)  # 高光：持續綠調
        )
        
        # 2. 低對比曲線：抬高陰影，壓低高光
        r, g, b = cv2.split(frame)
        r = self.apply_tone_curve(r.astype(np.uint8), shadows=1.15, midtones=0.95, highlights=1.08)
        g = self.apply_tone_curve(g.astype(np.uint8), shadows=1.18, midtones=0.92, highlights=1.05)
        b = self.apply_tone_curve(b.astype(np.uint8), shadows=1.12, midtones=0.98, highlights=1.10)
        
        # 3. 電影風格的低飽和度
        frame = cv2.merge([r, g, b])
        lab = cv2.cvtColor(frame, cv2.COLOR_RGB2LAB).astype(np.float32)
        lab[:,:,1] = (lab[:,:,1] - 128) * 0.82 + 128
        lab[:,:,2] = (lab[:,:,2] - 128) * 0.85 + 128
        
        return cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB)
    
    def apply_acros(self, frame):
        """ACROS - 黑白膠片，柔和陰影和細節"""
        # 1. 轉為黑白（使用加權平均法）
        r, g, b = cv2.split(frame.astype(np.float32))
        # Acros 特有的黑白轉換权重：更注重綠色通道
        gray = 0.25 * r + 0.55 * g + 0.20 * b
        
        # 2. 柔和的對比曲線
        gray = self.apply_tone_curve(gray.astype(np.uint8), 
                                   shadows=1.08,    # 提亮陰影
                                   midtones=1.05,   # 輕微提亮中間調
                                   highlights=0.98) # 輕微壓低高光
        
        # 3. CLAHE 提升局部對比（但保持柔和）
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8,8))
        gray = clahe.apply(gray.astype(np.uint8))
        
        # 4. 輕微提亮整體
        gray = np.clip(gray.astype(np.float32) + 8, 0, 255).astype(np.uint8)
        
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    
    def apply_monochrome(self, frame):
        """MONOCHROME - 單色黑白，高對比細節"""
        # 1. 標準黑白轉換
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY).astype(np.float32)
        
        # 2. 高對比曲線
        gray = self.apply_tone_curve(gray.astype(np.uint8),
                                   shadows=0.90,    # 加深陰影
                                   midtones=1.20,   # 提高中間調對比
                                   highlights=0.95) # 輕微壓低高光
        
        # 3. 稍微提高整體對比
        gray = cv2.convertScaleAbs(gray, alpha=1.08, beta=-3)
        
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    
    def adjust_exposure(self, frame):
        """調整曝光"""
        if self.exposure_value == 0:
            return frame
        
        frame = frame.astype(np.float32)
        exposure_factor = 1.0 + (self.exposure_value / 100.0)
        frame = frame * exposure_factor
        frame = np.clip(frame, 0, 255)
        return frame.astype(np.uint8)
    
    def stop(self):
        self.running = False


class FilmSimulationWidget(QScrollArea):
    """可滑動的軟片模擬選擇器"""
    filterChanged = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.current_filter = 0
        self.filters = [
            {"name": "PROVIA", "desc": "標準色彩", "color": "#4a90e2"},
            {"name": "VELVIA", "desc": "鮮豔風景", "color": "#e74c3c"},
            {"name": "ASTIA", "desc": "柔和人像", "color": "#f39c12"},
            {"name": "CLASSIC CHROME", "desc": "復古街拍", "color": "#95a5a6"},
            {"name": "PRO NEG Hi", "desc": "專業負片", "color": "#9b59b6"},
            {"name": "PRO NEG Std", "desc": "標準負片", "color": "#8e44ad"},
            {"name": "CLASSIC NEG", "desc": "經典負片", "color": "#d35400"},
            {"name": "ETERNA", "desc": "電影質感", "color": "#27ae60"},
            {"name": "ACROS", "desc": "黑白膠片", "color": "#2c3e50"},
            {"name": "MONOCHROME", "desc": "單色黑白", "color": "#34495e"}
        ]
        self.init_ui()
    
    def init_ui(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        
        # 主容器
        container = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(10, 20, 10, 20)
        container.setLayout(layout)
        
        self.filter_widgets = []
        
        for i, filter_info in enumerate(self.filters):
            filter_widget = self.create_filter_widget(i, filter_info)
            self.filter_widgets.append(filter_widget)
            layout.addWidget(filter_widget)
        
        # 添加底部空間
        layout.addStretch()
        
        container.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
            }
        """)
        
        self.setWidget(container)
        self.update_selection(0)
    
    def create_filter_widget(self, index, filter_info):
        """創建單個濾鏡選項"""
        widget = QWidget()
        widget.setFixedHeight(80)
        widget.setCursor(Qt.PointingHandCursor)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        widget.setLayout(layout)
        
        # 濾鏡名稱
        name_label = QLabel(filter_info["name"])
        name_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Courier New', monospace;
            }
        """)
        layout.addWidget(name_label)
        
        # 濾鏡描述
        desc_label = QLabel(filter_info["desc"])
        desc_label.setStyleSheet("""
            QLabel {
                color: #cccccc;
                font-size: 12px;
                font-family: 'Arial', sans-serif;
            }
        """)
        layout.addWidget(desc_label)
        
        # 點擊事件
        widget.mousePressEvent = lambda event, idx=index: self.select_filter(idx)
        
        return widget
    
    def select_filter(self, index):
        """選擇濾鏡"""
        if self.current_filter != index:
            self.current_filter = index
            self.update_selection(index)
            self.filterChanged.emit(index)
            
            # 滾動到選中的濾鏡
            widget = self.filter_widgets[index]
            self.ensureWidgetVisible(widget)
    
    def update_selection(self, index):
        """更新選中狀態的視覺效果"""
        for i, widget in enumerate(self.filter_widgets):
            if i == index:
                # 選中狀態
                widget.setStyleSheet(f"""
                    QWidget {{
                        background-color: {self.filters[i]['color']};
                        border-radius: 8px;
                        border: 2px solid white;
                    }}
                """)
            else:
                # 未選中狀態
                widget.setStyleSheet("""
                    QWidget {
                        background-color: #2a2a2a;
                        border-radius: 8px;
                        border: 1px solid #444444;
                    }
                    QWidget:hover {
                        background-color: #3a3a3a;
                    }
                """)
    
    def wheelEvent(self, event):
        """處理滾輪事件"""
        # 上下滾動切換濾鏡
        delta = event.angleDelta().y()
        if delta > 0 and self.current_filter > 0:
            self.select_filter(self.current_filter - 1)
        elif delta < 0 and self.current_filter < len(self.filters) - 1:
            self.select_filter(self.current_filter + 1)


class XHalfCameraApp(QMainWindow):
    """Fujifilm X-half 風格相機應用程式"""
    
    def __init__(self):
        super().__init__()
        self.picam2 = None
        self.camera_thread = None
        self.current_frame = None
        self.save_directory = "/home/kevin/Pictures/piCam"
        self.ensure_save_directory()
        self.init_camera()
        self.init_ui()
    
    def ensure_save_directory(self):
        """確保儲存目錄存在"""
        try:
            os.makedirs(self.save_directory, exist_ok=True)
            print(f"照片儲存路徑: {self.save_directory}")
        except Exception as e:
            print(f"無法創建儲存目錄: {e}")
            self.save_directory = "."
        
    def init_camera(self):
        """初始化相機"""
        try:
            self.picam2 = Picamera2()
            config = self.picam2.create_preview_configuration(
                main={"size": (1296, 972), "format": "RGB888"}
            )
            self.picam2.configure(config)
            self.picam2.start()
            
            # 啟動相機線程
            self.camera_thread = CameraThread(self.picam2)
            self.camera_thread.frameReady.connect(self.update_frame)
            self.camera_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法初始化相機: {e}")
            sys.exit(1)
    
    def init_ui(self):
        """初始化使用者介面"""
        self.setWindowTitle("Fujifilm X-half Style Camera")
        self.setGeometry(0, 0, 800, 480)  # 適合 3.5" 觸控螢幕
        self.setStyleSheet("background-color: #000000;")
        
        # 主要 Widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 主要佈局 (水平分割)
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(2)
        main_widget.setLayout(main_layout)
        
        # === 左半邊：軟片模擬選擇 ===
        left_panel = QWidget()
        left_panel.setStyleSheet("background-color: #1a1a1a; border-right: 2px solid #333;")
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_panel.setLayout(left_layout)
        
        # 標題
        title_label = QLabel("FILM SIMULATION")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 15px;
                text-align: center;
                font-family: 'Courier New', monospace;
                background-color: #2a2a2a;
                border-bottom: 1px solid #444;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title_label)
        
        # 軟片模擬選擇器
        self.film_selector = FilmSimulationWidget()
        self.film_selector.filterChanged.connect(self.change_filter)
        left_layout.addWidget(self.film_selector)
        
        # === 右半邊：相機預覽 ===
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: #000000;")
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_panel.setLayout(right_layout)
        
        # 預覽標籤
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("background-color: black; border: 1px solid #333;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(390, 290)
        right_layout.addWidget(self.preview_label)
        
        # 底部控制
        bottom_controls = QWidget()
        bottom_controls.setMaximumHeight(80)
        bottom_layout = QHBoxLayout()
        bottom_controls.setLayout(bottom_layout)
        
        # 快門按鈕
        self.shutter_btn = QPushButton()
        self.shutter_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                border: 4px solid white;
                border-radius: 35px;
                min-width: 70px;
                min-height: 70px;
                max-width: 70px;
                max-height: 70px;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
            QPushButton:pressed {
                background-color: #cc3333;
                border: 4px solid #cccccc;
            }
        """)
        self.shutter_btn.clicked.connect(self.capture_photo)
        
        # 曝光控制
        self.exposure_slider = QSlider(Qt.Horizontal)
        self.exposure_slider.setRange(-50, 50)
        self.exposure_slider.setValue(0)
        self.exposure_slider.setMaximumWidth(200)
        self.exposure_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: #333;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ff4444;
                width: 16px;
                height: 16px;
                border-radius: 8px;
                margin: -6px 0;
            }
        """)
        self.exposure_slider.valueChanged.connect(self.change_exposure)
        
        self.exposure_label = QLabel("EV: 0")
        self.exposure_label.setStyleSheet("color: white; font-size: 12px;")
        
        bottom_layout.addWidget(self.exposure_slider)
        bottom_layout.addWidget(self.exposure_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.shutter_btn)
        bottom_layout.addStretch()
        
        right_layout.addWidget(bottom_controls)
        
        # 組合左右面板
        main_layout.addWidget(left_panel, 1)  # 左邊：軟片模擬選擇
        main_layout.addWidget(right_panel, 1)  # 右邊：相機預覽
        
        # 全螢幕模式
        self.showFullScreen()
    
    def update_frame(self, frame):
        """更新預覽畫面"""
        self.current_frame = frame
        
        # 轉換為 QImage
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # 縮放以適應預覽標籤
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(
            self.preview_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        self.preview_label.setPixmap(scaled_pixmap)
    
    def change_filter(self, index):
        """改變濾鏡"""
        if self.camera_thread:
            self.camera_thread.current_filter = index
            print(f"切換到濾鏡: {self.film_selector.filters[index]['name']}")
    
    def change_exposure(self, value):
        """改變曝光值"""
        if self.camera_thread:
            self.camera_thread.exposure_value = value
            self.exposure_label.setText(f"EV: {value:+d}")
    
    def capture_photo(self):
        """拍照"""
        if self.current_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filter_name = self.film_selector.filters[self.camera_thread.current_filter]['name'].replace(' ', '_')
            filename = f"photo_{timestamp}_{filter_name}.jpg"
            full_path = os.path.join(self.save_directory, filename)
            
            # 轉換 RGB 到 BGR (OpenCV 格式)
            bgr_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(full_path, bgr_frame)
            
            print(f"✓ 照片已儲存: {full_path}")
            
            # 快門效果
            self.preview_label.setStyleSheet("background-color: white; border: 1px solid #333;")
            QTimer.singleShot(100, lambda: self.preview_label.setStyleSheet("background-color: black; border: 1px solid #333;"))
    
    def keyPressEvent(self, event):
        """按鍵事件"""
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Space:
            self.capture_photo()
        elif event.key() == Qt.Key_Up:
            # 上一個濾鏡
            current = self.film_selector.current_filter
            if current > 0:
                self.film_selector.select_filter(current - 1)
        elif event.key() == Qt.Key_Down:
            # 下一個濾鏡
            current = self.film_selector.current_filter
            if current < len(self.film_selector.filters) - 1:
                self.film_selector.select_filter(current + 1)
    
    def closeEvent(self, event):
        """關閉事件"""
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread.wait()
        
        if self.picam2:
            self.picam2.stop()
        
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    # 設置應用程式樣式
    app.setStyle('Fusion')
    
    window = XHalfCameraApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()