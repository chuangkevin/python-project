#!/usr/bin/env python3
"""
專業相機應用程式
具有濾鏡、曝光調整、拍照按鈕的圖形界面
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
        self.aspect_ratio = 0  # 0: 4:3, 1: 16:9, 2: 1:1
        
    def run(self):
        while self.running:
            try:
                frame = self.picam2.capture_array()
                
                # 應用濾鏡
                frame = self.apply_filter(frame)
                
                # 應用曝光調整
                frame = self.adjust_exposure(frame)
                
                # 應用裁切（根據比例）
                frame = self.apply_aspect_ratio(frame)
                
                self.frameReady.emit(frame)
                time.sleep(0.033)  # ~30 FPS
            except Exception as e:
                print(f"相機錯誤: {e}")
                time.sleep(0.1)
    
    def apply_tone_curve(self, frame, highlights=1.0, shadows=1.0, midtones=1.0):
        """精確的色調映射功能"""
        frame = frame.astype(np.float32) / 255.0
        
        # 創建色調曲線映射
        # 使用 gamma 校正實現高光、陰影、中間調的精確控制
        
        # 分離高光、中間調、陰影區域
        shadow_mask = frame < 0.33
        midtone_mask = (frame >= 0.33) & (frame < 0.66)
        highlight_mask = frame >= 0.66
        
        result = frame.copy()
        
        # 陰影調整
        result[shadow_mask] = np.power(result[shadow_mask], 1.0/shadows)
        
        # 中間調調整
        result[midtone_mask] = np.power(result[midtone_mask], 1.0/midtones)
        
        # 高光調整
        result[highlight_mask] = 1.0 - np.power(1.0 - result[highlight_mask], highlights)
        
        return np.clip(result * 255.0, 0, 255).astype(np.uint8)
    
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
    
    def apply_provia(self, frame):
        """標準 Provia 色彩 - 自然而平衡的色彩表現"""
        frame = frame.astype(np.float32)
        
        # Provia 特色：平衡的對比和自然色彩
        # 輕微的 S 型曲線提升對比
        frame = np.clip(frame * 1.02 + 5, 0, 255)
        
        # LAB 色彩空間調整，避免 HSV 轉換的色彩失真
        lab = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
        lab[:,:,1] = np.clip(lab[:,:,1] * 1.05, 0, 255)  # 輕微增加 A 通道
        lab[:,:,2] = np.clip(lab[:,:,2] * 1.05, 0, 255)  # 輕微增加 B 通道
        frame = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2RGB)
        
        return frame
    
    def apply_velvia(self, frame):
        """鮮豔飽和的 Velvia - 強化風景色彩"""
        frame = frame.astype(np.float32)
        
        # Velvia 特色：高飽和度、強化藍綠色
        # 使用 LAB 色彩空間獲得更好的色彩控制
        lab = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
        
        # 提升對比度（L 通道）
        lab[:,:,0] = np.clip(lab[:,:,0] * 1.08 + 3, 0, 255)
        
        # 大幅增強色彩飽和度（A, B 通道）
        lab[:,:,1] = np.clip((lab[:,:,1] - 128) * 1.35 + 128, 0, 255)  # A 通道（綠-紅）
        lab[:,:,2] = np.clip((lab[:,:,2] - 128) * 1.4 + 128, 0, 255)   # B 通道（藍-黃）
        
        frame = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2RGB).astype(np.float32)
        
        # Velvia 特殊處理：強化天空和植物
        r, g, b = cv2.split(frame)
        # 強化藍色（天空）和綠色（植物）
        g = np.clip(g * 1.12, 0, 255)
        b = np.clip(b * 1.08, 0, 255)
        frame = cv2.merge([r, g, b])
        
        return np.clip(frame, 0, 255).astype(np.uint8)
    
    def apply_astia(self, frame):
        """柔和人像 Astia - 優化膚色表現"""
        frame = frame.astype(np.float32)
        
        # Astia 特色：柔和色調，優化膚色
        # 使用 LAB 色彩空間保護膚色
        lab = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
        
        # 輕微提升亮度（L 通道）
        lab[:,:,0] = np.clip(lab[:,:,0] * 1.05 + 8, 0, 255)
        
        # 調整色彩平衡（A, B 通道）- 偏暖色調
        lab[:,:,1] = np.clip((lab[:,:,1] - 128) * 1.08 + 128 + 2, 0, 255)  # A 通道（偏紅）
        lab[:,:,2] = np.clip((lab[:,:,2] - 128) * 0.95 + 128 - 3, 0, 255)   # B 通道（偏黃）
        
        frame = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2RGB).astype(np.float32)
        
        # Astia 膚色優化：增強紅色和黃色通道
        r, g, b = cv2.split(frame)
        
        # 膚色範圍增強（提升紅色和部分綠色）
        r = np.clip(r * 1.08, 0, 255)  # 增強紅色（血色感）
        g = np.clip(g * 1.03, 0, 255)  # 輕微增強綠色
        b = np.clip(b * 0.98, 0, 255)  # 輕微減弱藍色（減少冷調）
        
        frame = cv2.merge([r, g, b])
        
        # 柔化對比，保持細節
        frame = np.clip(frame * 1.02 + 5, 0, 255)
        
        return frame.astype(np.uint8)
    
    def apply_classic_chrome(self, frame):
        """復古銀鹽感 Classic Chrome - 經典街拍風格"""
        frame = frame.astype(np.float32)
        
        # Classic Chrome 特色：銀鹽質感，低飽和度高對比
        # 使用 LAB 色彩空間精確控制
        lab = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
        
        # 增強對比度（L 通道的 S 型曲線）
        l_channel = lab[:,:,0]
        # 創建更明顯的 S 型曲線
        l_normalized = l_channel / 255.0
        l_curved = np.where(l_normalized < 0.5, 
                           0.5 * np.power(2 * l_normalized, 1.2),
                           1 - 0.5 * np.power(2 * (1 - l_normalized), 1.2))
        lab[:,:,0] = l_curved * 255
        
        # 降低飽和度（A, B 通道）
        lab[:,:,1] = np.clip((lab[:,:,1] - 128) * 0.65 + 128, 0, 255)  # A 通道
        lab[:,:,2] = np.clip((lab[:,:,2] - 128) * 0.7 + 128, 0, 255)   # B 通道
        
        frame = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2RGB).astype(np.float32)
        
        # Classic Chrome 特殊色調：偏冷調，減弱暖色
        r, g, b = cv2.split(frame)
        r = np.clip(r * 0.95, 0, 255)  # 略減紅色
        g = np.clip(g * 1.02, 0, 255)  # 略增綠色
        b = np.clip(b * 1.05, 0, 255)  # 略增藍色
        frame = cv2.merge([r, g, b])
        
        # 增加陰影細節
        frame = np.clip(frame + 8, 0, 255)
        
        return frame.astype(np.uint8)
    
    def apply_pro_neg_hi(self, frame):
        """專業負片高對比"""
        # 高對比，鮮明的色彩
        frame = cv2.convertScaleAbs(frame, alpha=1.15, beta=8)
        
        # 增強紅色和藍色
        r, g, b = cv2.split(frame.astype(np.float32))
        r = np.clip(r * 1.08, 0, 255)
        b = np.clip(b * 1.05, 0, 255)
        frame = cv2.merge([r, g, b]).astype(np.uint8)
        
        return frame
    
    def apply_pro_neg_std(self, frame):
        """專業負片標準"""
        # 略微提高對比，保持自然色彩
        frame = cv2.convertScaleAbs(frame, alpha=1.08, beta=3)
        
        # 略提高飽和度
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[:,:,1] = np.clip(hsv[:,:,1] * 1.05, 0, 255)
        hsv = hsv.astype(np.uint8)
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        
        return frame
    
    def apply_classic_neg(self, frame):
        """經典負片風格"""
        # 柔和的對比和溫暖色調
        r, g, b = cv2.split(frame.astype(np.float32))
        r = np.clip(r * 1.08, 0, 255)  # 溫暖色調
        g = np.clip(g * 1.02, 0, 255)
        b = np.clip(b * 0.95, 0, 255)
        frame = cv2.merge([r, g, b]).astype(np.uint8)
        
        # 柔和對比
        frame = cv2.convertScaleAbs(frame, alpha=1.05, beta=8)
        
        return frame
    
    def apply_eterna(self, frame):
        """電影感 Eterna"""
        # 電影感的低對比、低飽和度
        hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV).astype(np.float32)
        hsv[:,:,1] = np.clip(hsv[:,:,1] * 0.8, 0, 255)  # 降低飽和度
        hsv = hsv.astype(np.uint8)
        frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
        
        # 略微減弱對比
        frame = cv2.convertScaleAbs(frame, alpha=0.95, beta=15)
        
        # 電影色調（略微偏綠）
        r, g, b = cv2.split(frame.astype(np.float32))
        g = np.clip(g * 1.03, 0, 255)
        frame = cv2.merge([r, g, b]).astype(np.uint8)
        
        return frame
    
    def apply_acros(self, frame):
        """黑白膠片 Acros"""
        # 轉為黑白
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        # Acros 特色：柔和的對比和細節
        # 使用 CLAHE 提高局部對比
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
        
        # 軟化陰影
        gray = cv2.add(gray, 5)
        
        # 轉回 RGB
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    
    def apply_monochrome(self, frame):
        """單色黑白"""
        # 簡單的黑白轉換
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        
        # 提高對比
        gray = cv2.convertScaleAbs(gray, alpha=1.1, beta=-5)
        
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    
    def adjust_exposure(self, frame):
        """調整曝光"""
        if self.exposure_value == 0:
            return frame
        
        # 轉換為 float 進行計算
        frame = frame.astype(np.float32)
        
        # 曝光調整 (-100 到 +100)
        exposure_factor = 1.0 + (self.exposure_value / 100.0)
        frame = frame * exposure_factor
        
        # 限制範圍
        frame = np.clip(frame, 0, 255)
        return frame.astype(np.uint8)
    
    def apply_aspect_ratio(self, frame):
        """應用不同的長寬比"""
        h, w = frame.shape[:2]
        
        if self.aspect_ratio == 0:  # 4:3
            return frame
        elif self.aspect_ratio == 1:  # 16:9
            new_h = int(w * 9 / 16)
            if new_h < h:
                crop_top = (h - new_h) // 2
                return frame[crop_top:crop_top + new_h, :]
        elif self.aspect_ratio == 2:  # 1:1 (正方形)
            size = min(h, w)
            crop_h = (h - size) // 2
            crop_w = (w - size) // 2
            return frame[crop_h:crop_h + size, crop_w:crop_w + size]
        
        return frame
    
    def stop(self):
        self.running = False


class CameraApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.picam2 = None
        self.camera_thread = None
        self.current_frame = None
        self.current_resolution = 1  # 0: 640x480, 1: 1296x972, 2: 2592x1944
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
            self.save_directory = "."  # 回退到當前目錄
        
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
        self.setWindowTitle("專業相機")
        self.setGeometry(100, 100, 1024, 600)
        
        # 主要 Widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # 主要佈局 (水平)
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        
        # === 左側控制面板 ===
        left_panel = QWidget()
        left_panel.setMaximumWidth(200)
        left_panel.setStyleSheet("background-color: #2b2b2b;")
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)
        
        # 標題
        title = QLabel("控制面板")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title)
        
        # 濾鏡選擇
        filter_label = QLabel("濾鏡")
        filter_label.setStyleSheet("color: white; padding: 5px;")
        left_layout.addWidget(filter_label)
        
        self.filter_list = QListWidget()
        self.filter_list.setStyleSheet("""
            QListWidget {
                background-color: #3c3c3c;
                color: white;
                border: none;
            }
            QListWidget::item:selected {
                background-color: #0d7377;
            }
            QListWidget::item:hover {
                background-color: #4c4c4c;
            }
        """)
        
        filters = ["Provia", "Velvia", "Astia", "Classic Chrome", "Pro Neg Hi", 
                  "Pro Neg Std", "Classic Neg", "Eterna", "Acros", "Monochrome"]
        self.filter_list.addItems(filters)
        self.filter_list.currentRowChanged.connect(self.change_filter)
        self.filter_list.setCurrentRow(0)
        left_layout.addWidget(self.filter_list)
        
        # 曝光調整
        exposure_label = QLabel("曝光調整")
        exposure_label.setStyleSheet("color: white; padding: 5px; margin-top: 10px;")
        left_layout.addWidget(exposure_label)
        
        self.exposure_slider = QSlider(Qt.Horizontal)
        self.exposure_slider.setRange(-100, 100)
        self.exposure_slider.setValue(0)
        self.exposure_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #4c4c4c;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #0d7377;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -6px 0;
            }
        """)
        self.exposure_slider.valueChanged.connect(self.change_exposure)
        left_layout.addWidget(self.exposure_slider)
        
        self.exposure_value_label = QLabel("0")
        self.exposure_value_label.setStyleSheet("color: white; text-align: center;")
        self.exposure_value_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.exposure_value_label)
        
        # 解析度控制
        resolution_label = QLabel("解析度")
        resolution_label.setStyleSheet("color: white; padding: 5px; margin-top: 10px;")
        left_layout.addWidget(resolution_label)
        
        # 解析度按鈕組
        res_buttons_widget = QWidget()
        res_buttons_layout = QVBoxLayout()
        res_buttons_widget.setLayout(res_buttons_layout)
        
        self.resolution_buttons = []
        resolutions = ["640×480", "1296×972", "2592×1944"]
        
        for i, res_text in enumerate(resolutions):
            btn = QPushButton(res_text)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4c4c4c;
                    color: white;
                    border: none;
                    padding: 8px;
                    margin: 2px;
                    border-radius: 4px;
                }
                QPushButton:checked {
                    background-color: #0d7377;
                }
                QPushButton:hover {
                    background-color: #5c5c5c;
                }
                QPushButton:checked:hover {
                    background-color: #14a0a5;
                }
            """)
            btn.clicked.connect(lambda checked, idx=i: self.change_resolution(idx))
            self.resolution_buttons.append(btn)
            res_buttons_layout.addWidget(btn)
        
        # 預設選中中等解析度
        self.resolution_buttons[1].setChecked(True)
        
        left_layout.addWidget(res_buttons_widget)
        
        # 儲存路徑設定
        save_path_label = QLabel("儲存路徑")
        save_path_label.setStyleSheet("color: white; padding: 5px; margin-top: 10px;")
        left_layout.addWidget(save_path_label)
        
        self.save_path_display = QLabel(self.save_directory)
        self.save_path_display.setStyleSheet("""
            QLabel {
                background-color: #3c3c3c;
                color: white;
                padding: 5px;
                border-radius: 3px;
                font-size: 10px;
            }
        """)
        self.save_path_display.setWordWrap(True)
        left_layout.addWidget(self.save_path_display)
        
        change_path_btn = QPushButton("變更路徑")
        change_path_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                padding: 5px;
                margin: 2px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #14a0a5;
            }
        """)
        change_path_btn.clicked.connect(self.change_save_path)
        left_layout.addWidget(change_path_btn)
        
        # 彈性空間
        left_layout.addStretch()
        
        # === 右側預覽區域 ===
        right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)
        
        # 預覽標籤
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("background-color: black;")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(640, 480)
        
        # 啟用滑鼠滾輪事件
        self.preview_label.wheelEvent = self.wheel_event
        
        right_layout.addWidget(self.preview_label)
        
        # 底部控制按鈕
        bottom_controls = QWidget()
        bottom_controls.setMaximumHeight(80)
        bottom_layout = QHBoxLayout()
        bottom_controls.setLayout(bottom_layout)
        
        # 拍照按鈕
        self.capture_btn = QPushButton()
        self.capture_btn.setIcon(self.create_camera_icon())
        self.capture_btn.setIconSize(QSize(50, 50))
        self.capture_btn.setStyleSheet("""
            QPushButton {
                background-color: #0d7377;
                border-radius: 35px;
                min-width: 70px;
                min-height: 70px;
                max-width: 70px;
                max-height: 70px;
            }
            QPushButton:hover {
                background-color: #14ffec;
            }
            QPushButton:pressed {
                background-color: #0a5a5e;
            }
        """)
        self.capture_btn.clicked.connect(self.capture_photo)
        
        # 比例顯示標籤
        self.ratio_label = QLabel("4:3")
        self.ratio_label.setStyleSheet("""
            QLabel {
                color: #0d7377;
                font-size: 14px;
                font-weight: bold;
                padding: 5px 10px;
                background-color: #f0f0f0;
                border-radius: 15px;
            }
        """)
        
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.ratio_label)
        bottom_layout.addWidget(self.capture_btn)
        bottom_layout.addStretch()
        
        right_layout.addWidget(bottom_controls)
        
        # 加入主佈局
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)
        
        # 設置視窗樣式
        self.setStyleSheet("background-color: #f0f0f0;")
    
    def create_camera_icon(self):
        """創建相機圖標"""
        pixmap = QPixmap(50, 50)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 繪製相機圖標
        painter.setPen(QPen(Qt.white, 3))
        painter.setBrush(Qt.white)
        
        # 相機本體
        painter.drawRoundedRect(10, 15, 30, 25, 5, 5)
        
        # 鏡頭
        painter.drawEllipse(20, 22, 10, 10)
        
        # 快門按鈕
        painter.drawRect(20, 10, 10, 5)
        
        painter.end()
        return QIcon(pixmap)
    
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
            print(f"切換到濾鏡: {self.filter_list.item(index).text()}")
    
    def change_exposure(self, value):
        """改變曝光值"""
        if self.camera_thread:
            self.camera_thread.exposure_value = value
            self.exposure_value_label.setText(str(value))
    
    def wheel_event(self, event):
        """滑鼠滾輪事件 - 改變圖片比例"""
        if self.camera_thread:
            # 獲取滾輪方向
            delta = event.angleDelta().y()
            
            if delta > 0:  # 向上滾動
                self.camera_thread.aspect_ratio = (self.camera_thread.aspect_ratio + 1) % 3
            else:  # 向下滾動
                self.camera_thread.aspect_ratio = (self.camera_thread.aspect_ratio - 1) % 3
            
            # 更新比例標籤
            ratios = ["4:3", "16:9", "1:1"]
            self.ratio_label.setText(ratios[self.camera_thread.aspect_ratio])
            print(f"切換到比例: {ratios[self.camera_thread.aspect_ratio]}")
    
    def change_resolution(self, resolution_index):
        """變更解析度 - 修復版本"""
        # 取消其他按鈕的選中狀態
        for i, btn in enumerate(self.resolution_buttons):
            btn.setChecked(i == resolution_index)
        
        if self.current_resolution == resolution_index:
            return  # 已經是目前解析度，不需要變更
        
        # 解析度對應表
        resolutions = [
            (640, 480),
            (1296, 972),
            (2592, 1944)
        ]
        
        new_size = resolutions[resolution_index]
        
        try:
            print(f"正在變更解析度為: {new_size[0]}x{new_size[1]}...")
            
            # 保存目前設定
            current_filter = self.camera_thread.current_filter if self.camera_thread else 0
            current_exposure = self.camera_thread.exposure_value if self.camera_thread else 0
            current_aspect_ratio = self.camera_thread.aspect_ratio if self.camera_thread else 0
            
            # 安全停止相機線程
            if self.camera_thread:
                self.camera_thread.running = False
                self.camera_thread.wait(timeout=3000)  # 等待 3 秒
                if self.camera_thread.isRunning():
                    print("強制終止相機線程...")
                    self.camera_thread.terminate()
                    self.camera_thread.wait(1000)
                self.camera_thread = None
            
            # 停止相機
            if self.picam2:
                self.picam2.stop()
                time.sleep(1)  # 增加等待時間
            
            # 重新配置相機
            config = self.picam2.create_preview_configuration(
                main={"size": new_size, "format": "RGB888"}
            )
            self.picam2.configure(config)
            self.picam2.start()
            time.sleep(1.5)  # 等待相機完全穩定
            
            # 重新啟動相機線程並恢復設定
            self.camera_thread = CameraThread(self.picam2)
            self.camera_thread.current_filter = current_filter
            self.camera_thread.exposure_value = current_exposure
            self.camera_thread.aspect_ratio = current_aspect_ratio
            self.camera_thread.frameReady.connect(self.update_frame)
            self.camera_thread.start()
            
            # 更新目前解析度
            self.current_resolution = resolution_index
            
            print(f"✓ 解析度已成功變更為: {new_size[0]}x{new_size[1]}")
            
        except Exception as e:
            print(f"解析度變更失敗: {e}")
            QMessageBox.critical(self, "錯誤", f"無法變更解析度: {e}\n\n請重新啟動程式")
            
            # 嘗試恢復到安全的中等解析度
            try:
                print("嘗試恢復到安全解析度...")
                if self.picam2:
                    self.picam2.stop()
                    time.sleep(1)
                    config = self.picam2.create_preview_configuration(
                        main={"size": (1296, 972), "format": "RGB888"}
                    )
                    self.picam2.configure(config)
                    self.picam2.start()
                    time.sleep(1)
                    
                    self.camera_thread = CameraThread(self.picam2)
                    self.camera_thread.frameReady.connect(self.update_frame)
                    self.camera_thread.start()
                    
                    self.current_resolution = 1
                    self.resolution_buttons[1].setChecked(True)
                    print("恢復成功")
            except Exception as recovery_error:
                print(f"恢復失敗: {recovery_error}")
            # 重新啟動相機線程並恢復設定
            self.camera_thread = CameraThread(self.picam2)
            self.camera_thread.current_filter = current_filter
            self.camera_thread.exposure_value = current_exposure
            self.camera_thread.aspect_ratio = current_aspect_ratio
            self.camera_thread.frameReady.connect(self.update_frame)
            self.camera_thread.start()
            
            print(f"解析度已變更為: {new_size[0]}x{new_size[1]}")
            
        except Exception as e:
            QMessageBox.warning(self, "警告", f"無法變更解析度: {e}")
    
    def change_save_path(self):
        """變更儲存路徑"""
        new_path = QFileDialog.getExistingDirectory(
            self,
            "選擇儲存目錄",
            self.save_directory
        )
        
        if new_path:
            self.save_directory = new_path
            self.save_path_display.setText(new_path)
            self.ensure_save_directory()
            print(f"儲存路徑已變更為: {new_path}")
    
    def capture_photo(self):
        """拍照"""
        if self.current_frame is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"photo_{timestamp}.jpg"
            full_path = os.path.join(self.save_directory, filename)
            
            # 轉換 RGB 到 BGR (OpenCV 格式)
            bgr_frame = cv2.cvtColor(self.current_frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(full_path, bgr_frame)
            
            print(f"✓ 照片已儲存: {full_path}")
            
            # 顯示快門效果
            self.preview_label.setStyleSheet("background-color: white;")
            QTimer.singleShot(100, lambda: self.preview_label.setStyleSheet("background-color: black;"))
    
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
    
    window = CameraApp()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
