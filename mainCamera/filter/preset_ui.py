"""
軟片預設管理器 GUI
Film Preset Manager GUI

簡單的圖形界面展示模組化軟片模擬系統
"""

import sys
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                                QHBoxLayout, QLabel, QPushButton, QComboBox,
                                QScrollArea, QGroupBox, QTextEdit, QFrame,
                                QGridLayout, QListWidget, QListWidgetItem,
                                QSplitter, QMessageBox, QFileDialog)
    from PyQt5.QtCore import Qt, QTimer, pyqtSignal
    from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor
    from PIL import Image
except ImportError:
    print("錯誤: 需要安裝 PyQt5")
    print("請執行: pip install PyQt5")
    sys.exit(1)

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

try:
    from preset_manager import FilmPresetManager, FilmProcessor
    print("OK: 成功載入預設管理器")
except ImportError as e:
    print(f"ERROR: 載入預設管理器失敗: {e}")
    sys.exit(1)

class FilmPresetUI(QMainWindow):
    """軟片預設管理器主界面"""

    preset_changed = pyqtSignal(str)  # 預設改變信號

    def __init__(self):
        super().__init__()
        self.manager = FilmPresetManager()
        self.current_processor: Optional[FilmProcessor] = None
        self.current_preset_id: Optional[str] = None
        self.current_image: Optional[np.ndarray] = None
        self.processed_image: Optional[np.ndarray] = None

        self.init_ui()
        self.load_presets()

    def init_ui(self):
        """初始化用戶界面"""
        self.setWindowTitle("軟片模擬預設管理器 - Film Simulation Preset Manager")
        self.setGeometry(100, 100, 1200, 800)

        # 設定樣式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QListWidget {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 3px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #555555;
            }
            QListWidget::item:selected {
                background-color: #4a90e2;
            }
            QPushButton {
                background-color: #4a90e2;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2968a3;
            }
            QTextEdit {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 8px;
            }
            QLabel {
                color: #ffffff;
            }
        """)

        # 主容器
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        # 分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # 左側面板 - 預設列表
        self.setup_preset_panel(splitter)

        # 右側面板 - 詳細信息
        self.setup_detail_panel(splitter)

        # 設定分割比例
        splitter.setSizes([400, 800])

    def setup_preset_panel(self, parent):
        """設置預設列表面板"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # 標題
        title_label = QLabel("Film Presets 軟片預設")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(title_label)

        # 分類篩選
        filter_group = QGroupBox("篩選")
        filter_layout = QVBoxLayout(filter_group)

        # 分類選擇
        self.category_combo = QComboBox()
        self.category_combo.addItem("所有分類", "")
        self.category_combo.currentTextChanged.connect(self.filter_presets)
        filter_layout.addWidget(QLabel("分類:"))
        filter_layout.addWidget(self.category_combo)

        # 廠商選擇
        self.manufacturer_combo = QComboBox()
        self.manufacturer_combo.addItem("所有廠商", "")
        self.manufacturer_combo.currentTextChanged.connect(self.filter_presets)
        filter_layout.addWidget(QLabel("廠商:"))
        filter_layout.addWidget(self.manufacturer_combo)

        left_layout.addWidget(filter_group)

        # 預設列表
        preset_group = QGroupBox("預設列表")
        preset_layout = QVBoxLayout(preset_group)

        self.preset_list = QListWidget()
        self.preset_list.itemClicked.connect(self.on_preset_selected)
        preset_layout.addWidget(self.preset_list)

        left_layout.addWidget(preset_group)

        # 統計信息
        self.stats_label = QLabel("載入中...")
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setStyleSheet("color: #888888; font-style: italic;")
        left_layout.addWidget(self.stats_label)

        parent.addWidget(left_widget)

    def setup_detail_panel(self, parent):
        """設置詳細信息面板"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # 預設詳情
        detail_group = QGroupBox("預設詳情")
        detail_layout = QVBoxLayout(detail_group)

        # 預設名稱
        self.preset_name_label = QLabel("請選擇一個預設")
        self.preset_name_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.preset_name_label.setAlignment(Qt.AlignCenter)
        detail_layout.addWidget(self.preset_name_label)

        # 預設信息網格
        info_widget = QWidget()
        self.info_layout = QGridLayout(info_widget)
        detail_layout.addWidget(info_widget)

        # 參數顯示
        params_group = QGroupBox("處理參數")
        params_layout = QVBoxLayout(params_group)

        self.params_text = QTextEdit()
        self.params_text.setReadOnly(True)
        self.params_text.setMaximumHeight(200)
        params_layout.addWidget(self.params_text)

        detail_layout.addWidget(params_group)

        right_layout.addWidget(detail_group)

        # 圖片操作按鈕
        image_group = QGroupBox("圖片操作")
        image_layout = QVBoxLayout(image_group)

        # 第一排按鈕
        image_buttons1 = QHBoxLayout()
        self.load_image_button = QPushButton("Load 載入圖片")
        self.load_image_button.clicked.connect(self.load_image)
        image_buttons1.addWidget(self.load_image_button)

        self.test_button = QPushButton("Process 處理圖片")
        self.test_button.clicked.connect(self.process_image)
        self.test_button.setEnabled(False)
        image_buttons1.addWidget(self.test_button)

        image_layout.addLayout(image_buttons1)

        # 第二排按鈕
        image_buttons2 = QHBoxLayout()
        self.save_button = QPushButton("Save 保存結果")
        self.save_button.clicked.connect(self.save_processed_image)
        self.save_button.setEnabled(False)
        image_buttons2.addWidget(self.save_button)

        self.clear_button = QPushButton("Clear 清除圖片")
        self.clear_button.clicked.connect(self.clear_images)
        image_buttons2.addWidget(self.clear_button)

        image_layout.addLayout(image_buttons2)

        right_layout.addWidget(image_group)

        # 圖片顯示區域
        images_group = QGroupBox("圖片預覽")
        images_layout = QHBoxLayout(images_group)

        # 原圖
        original_frame = QFrame()
        original_layout = QVBoxLayout(original_frame)
        original_layout.addWidget(QLabel("原圖"))
        self.original_image_label = QLabel("尚未載入圖片")
        self.original_image_label.setAlignment(Qt.AlignCenter)
        self.original_image_label.setMinimumSize(300, 200)
        self.original_image_label.setStyleSheet("border: 1px solid #555555; background-color: #2b2b2b;")
        original_layout.addWidget(self.original_image_label)
        images_layout.addWidget(original_frame)

        # 處理後
        processed_frame = QFrame()
        processed_layout = QVBoxLayout(processed_frame)
        processed_layout.addWidget(QLabel("處理後"))
        self.processed_image_label = QLabel("尚未處理圖片")
        self.processed_image_label.setAlignment(Qt.AlignCenter)
        self.processed_image_label.setMinimumSize(300, 200)
        self.processed_image_label.setStyleSheet("border: 1px solid #555555; background-color: #2b2b2b;")
        processed_layout.addWidget(self.processed_image_label)
        images_layout.addWidget(processed_frame)

        right_layout.addWidget(images_group)

        # 其他操作按鈕
        actions_group = QGroupBox("預設操作")
        actions_layout = QHBoxLayout(actions_group)

        self.export_button = QPushButton("Export 匯出設定")
        self.export_button.clicked.connect(self.export_preset)
        self.export_button.setEnabled(False)
        actions_layout.addWidget(self.export_button)

        self.reload_button = QPushButton("Reload 重新載入")
        self.reload_button.clicked.connect(self.reload_presets)
        actions_layout.addWidget(self.reload_button)

        right_layout.addWidget(actions_group)

        # 測試結果
        result_group = QGroupBox("測試結果")
        result_layout = QVBoxLayout(result_group)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(150)
        self.result_text.setPlainText("尚未進行測試...")
        result_layout.addWidget(self.result_text)

        right_layout.addWidget(result_group)

        parent.addWidget(right_widget)

    def load_presets(self):
        """載入所有預設"""
        try:
            # 載入預設列表
            presets = self.manager.list_presets()

            # 更新分類選擇器
            categories = self.manager.get_categories()
            self.category_combo.clear()
            self.category_combo.addItem("所有分類", "")
            for category in sorted(categories.keys()):
                self.category_combo.addItem(f"{category} ({len(categories[category])})", category)

            # 更新廠商選擇器
            manufacturers = self.manager.get_manufacturers()
            self.manufacturer_combo.clear()
            self.manufacturer_combo.addItem("所有廠商", "")
            for manufacturer in sorted(manufacturers.keys()):
                self.manufacturer_combo.addItem(f"{manufacturer} ({len(manufacturers[manufacturer])})", manufacturer)

            # 更新預設列表
            self.update_preset_list(presets)

            # 更新統計
            self.stats_label.setText(f"總計: {len(presets)} 個預設")

        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入預設失敗:\n{e}")

    def update_preset_list(self, presets):
        """更新預設列表顯示"""
        self.preset_list.clear()

        for preset in presets:
            item_text = f"{preset['name']}\n{preset['manufacturer']} | {preset['category']}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, preset['id'])

            # 設定顏色
            if preset['category'] == 'color':
                item.setBackground(QColor(70, 130, 180, 50))
            elif preset['category'] == 'cinema':
                item.setBackground(QColor(220, 20, 60, 50))
            elif preset['category'] == 'special':
                item.setBackground(QColor(255, 165, 0, 50))

            self.preset_list.addItem(item)

    def filter_presets(self):
        """根據選擇篩選預設"""
        category = self.category_combo.currentData()
        manufacturer = self.manufacturer_combo.currentData()

        # 篩選預設
        filtered_presets = self.manager.list_presets(
            category=category if category else None,
            manufacturer=manufacturer if manufacturer else None
        )

        self.update_preset_list(filtered_presets)
        self.stats_label.setText(f"顯示: {len(filtered_presets)} 個預設")

    def on_preset_selected(self, item):
        """當選擇預設時"""
        preset_id = item.data(Qt.UserRole)
        self.current_preset_id = preset_id

        try:
            # 獲取預設詳情
            preset_data = self.manager.get_preset(preset_id)
            self.display_preset_details(preset_data)

            # 創建處理器
            self.current_processor = self.manager.create_processor(preset_id)

            # 啟用按鈕
            self.update_button_states()
            self.export_button.setEnabled(True)

            # 發送信號
            self.preset_changed.emit(preset_id)

        except Exception as e:
            QMessageBox.warning(self, "警告", f"載入預設失敗:\n{e}")

    def display_preset_details(self, preset_data):
        """顯示預設詳情"""
        metadata = preset_data['metadata']
        processing = preset_data['processing']

        # 更新名稱
        self.preset_name_label.setText(f"Film: {metadata['name']}")

        # 清空信息網格
        for i in reversed(range(self.info_layout.count())):
            self.info_layout.itemAt(i).widget().setParent(None)

        # 添加基本信息
        info_items = [
            ("描述", metadata.get('description', 'N/A')),
            ("廠商", metadata.get('manufacturer', 'N/A')),
            ("分類", metadata.get('category', 'N/A')),
            ("標籤", ', '.join(metadata.get('tags', []))),
        ]

        for i, (label, value) in enumerate(info_items):
            label_widget = QLabel(f"{label}:")
            label_widget.setStyleSheet("font-weight: bold;")
            value_widget = QLabel(str(value))
            value_widget.setWordWrap(True)

            self.info_layout.addWidget(label_widget, i, 0)
            self.info_layout.addWidget(value_widget, i, 1)

        # 顯示處理參數
        params_text = "處理參數配置:\n\n"
        for key, value in processing.items():
            if isinstance(value, dict):
                params_text += f"{key}:\n"
                for sub_key, sub_value in value.items():
                    params_text += f"  {sub_key}: {sub_value}\n"
            else:
                params_text += f"{key}: {value}\n"
            params_text += "\n"

        self.params_text.setPlainText(params_text)

    def update_button_states(self):
        """更新按鈕狀態"""
        has_processor = self.current_processor is not None
        has_image = self.current_image is not None
        has_processed = self.processed_image is not None

        self.test_button.setEnabled(has_processor and has_image)
        self.save_button.setEnabled(has_processed)

    def load_image(self):
        """載入圖片"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "選擇圖片",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.tiff *.tif);;All Files (*)"
        )

        if file_path:
            try:
                # 使用PIL載入圖片
                pil_image = Image.open(file_path)

                # 轉換為RGB（如果需要）
                if pil_image.mode != 'RGB':
                    pil_image = pil_image.convert('RGB')

                # 轉換為numpy陣列
                self.current_image = np.array(pil_image)

                # 轉換為BGR（OpenCV格式）
                self.current_image = self.current_image[:, :, ::-1]

                # 顯示縮圖
                self.display_image(self.current_image, self.original_image_label)

                # 更新按鈕狀態
                self.update_button_states()

                # 清除之前的處理結果
                self.processed_image = None
                self.processed_image_label.setText("尚未處理圖片")

                self.result_text.setPlainText(f"OK: 成功載入圖片\n檔案: {file_path}\n尺寸: {self.current_image.shape}")

            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"載入圖片失敗:\n{e}")

    def display_image(self, image_array, label_widget):
        """在QLabel中顯示圖片"""
        try:
            # 轉換BGR到RGB
            rgb_image = image_array[:, :, ::-1]

            # 創建PIL圖片
            pil_image = Image.fromarray(rgb_image)

            # 計算縮放尺寸（保持比例）
            label_size = label_widget.size()
            img_width, img_height = pil_image.size

            # 計算適合的尺寸
            scale_w = label_size.width() / img_width
            scale_h = label_size.height() / img_height
            scale = min(scale_w, scale_h, 1.0)  # 不放大

            new_width = int(img_width * scale)
            new_height = int(img_height * scale)

            # 縮放圖片
            pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)

            # 轉換為QPixmap
            qimage = pil_image.toqpixture() if hasattr(pil_image, 'toqpixture') else None
            if qimage is None:
                # 轉換為bytes然後QPixmap
                import io
                buffer = io.BytesIO()
                pil_image.save(buffer, format='PNG')
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue())
            else:
                pixmap = QPixmap.fromImage(qimage)

            label_widget.setPixmap(pixmap)

        except Exception as e:
            label_widget.setText(f"顯示錯誤: {e}")

    def process_image(self):
        """處理圖片"""
        if not self.current_processor or self.current_image is None:
            return

        try:
            # 處理圖像
            self.processed_image = self.current_processor.process_image(self.current_image)

            # 顯示處理後的圖片
            self.display_image(self.processed_image, self.processed_image_label)

            # 更新按鈕狀態
            self.update_button_states()

            # 顯示結果
            result_text = f"OK: 圖片處理成功!\n\n"
            result_text += f"預設: {self.current_preset_id}\n"
            result_text += f"原圖尺寸: {self.current_image.shape}\n"
            result_text += f"處理後尺寸: {self.processed_image.shape}\n"
            result_text += f"原圖數值範圍: {self.current_image.min():.1f} - {self.current_image.max():.1f}\n"
            result_text += f"處理後數值範圍: {self.processed_image.min():.1f} - {self.processed_image.max():.1f}\n"

            self.result_text.setPlainText(result_text)

        except Exception as e:
            error_text = f"ERROR: 圖片處理失敗!\n\n錯誤: {e}"
            self.result_text.setPlainText(error_text)

    def save_processed_image(self):
        """保存處理後的圖片"""
        if self.processed_image is None:
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存處理後圖片",
            f"{self.current_preset_id}_processed.jpg",
            "JPEG Files (*.jpg);;PNG Files (*.png);;All Files (*)"
        )

        if file_path:
            try:
                # 轉換BGR到RGB
                rgb_image = self.processed_image[:, :, ::-1]
                pil_image = Image.fromarray(rgb_image)
                pil_image.save(file_path)

                self.result_text.setPlainText(f"OK: 圖片保存成功!\n檔案: {file_path}")

            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"保存圖片失敗:\n{e}")

    def clear_images(self):
        """清除所有圖片"""
        self.current_image = None
        self.processed_image = None

        self.original_image_label.clear()
        self.original_image_label.setText("尚未載入圖片")

        self.processed_image_label.clear()
        self.processed_image_label.setText("尚未處理圖片")

        self.update_button_states()
        self.result_text.setPlainText("已清除所有圖片")

    def test_processing(self):
        """測試圖像處理"""
        if not self.current_processor:
            return

        try:
            # 創建測試圖像
            test_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

            # 處理圖像
            result = self.current_processor.process_image(test_img)

            # 顯示結果
            result_text = f"OK: 處理測試成功!\n\n"
            result_text += f"輸入圖像: {test_img.shape}\n"
            result_text += f"輸出圖像: {result.shape}\n"
            result_text += f"數值範圍: {result.min():.1f} - {result.max():.1f}\n"
            result_text += f"平均值: {result.mean():.1f}\n"
            result_text += f"預設: {self.current_preset_id}\n"

            self.result_text.setPlainText(result_text)

        except Exception as e:
            error_text = f"ERROR: 處理測試失敗!\n\n錯誤: {e}"
            self.result_text.setPlainText(error_text)

    def export_preset(self):
        """匯出預設配置"""
        if not self.current_preset_id:
            return

        try:
            preset_data = self.manager.get_preset(self.current_preset_id)

            # 這裡可以實現匯出邏輯
            # 暫時顯示JSON內容
            import json
            json_text = json.dumps(preset_data, indent=2, ensure_ascii=False)

            # 創建顯示窗口
            dialog = QMessageBox()
            dialog.setWindowTitle("預設配置")
            dialog.setText(f"預設 '{self.current_preset_id}' 的配置:")
            dialog.setDetailedText(json_text)
            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"匯出失敗:\n{e}")

    def reload_presets(self):
        """重新載入預設"""
        try:
            self.manager.reload_presets()
            self.load_presets()
            self.result_text.setPlainText("OK: 預設重新載入成功!")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"重新載入失敗:\n{e}")

def main():
    """主函數"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # 使用現代樣式

    # 設定應用程式屬性
    app.setApplicationName("Film Preset Manager")
    app.setApplicationVersion("1.0")

    # 創建主窗口
    window = FilmPresetUI()

    # 顯示窗口
    window.show()

    # 運行應用程式
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()