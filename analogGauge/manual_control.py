"""
PyQt版本的RD1Gauge手動控制界面
用於調試和測試指針位置
"""
import sys
from pathlib import Path
from PIL import Image
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QLabel, QSlider, QPushButton, QCheckBox,
                            QFrame, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap

try:
    from .rd1_gauge import RD1Gauge
except ImportError:
    from rd1_gauge import RD1Gauge


class GaugeDisplayWidget(QWidget):
    """顯示RD1Gauge的PyQt widget"""

    def __init__(self, gauge_size=400):
        super().__init__()
        self.gauge_size = gauge_size
        self.setFixedSize(gauge_size, gauge_size)
        self.gauge = None

    def set_gauge(self, gauge):
        self.gauge = gauge
        self.update_display()

    def update_display(self):
        if self.gauge:
            self.update()

    def paintEvent(self, event):
        if self.gauge:
            try:
                img = self.gauge.draw()
                # Convert PIL to QPixmap via bytes buffer
                import io
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue())

                from PyQt5.QtGui import QPainter
                painter = QPainter(self)
                painter.drawPixmap(0, 0, pixmap)
            except Exception as e:
                print(f"Error rendering gauge: {e}")


class ManualControlApp(QMainWindow):
    """PyQt版本的手動控制應用"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("RD-1 Gauge Manual Control (PyQt)")
        self.gauge = None
        self.init_ui()

        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.start(50)  # 20 FPS

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left panel: controls
        controls_frame = QFrame()
        controls_layout = QVBoxLayout(controls_frame)

        # Reset on start checkbox
        self.reset_checkbox = QCheckBox("Reset on start")
        self.reset_checkbox.setChecked(True)
        self.reset_checkbox.stateChanged.connect(self.on_reset_checkbox_changed)
        controls_layout.addWidget(self.reset_checkbox)

        # Initialize gauge
        self.gauge = RD1Gauge(reset_on_start=self.reset_checkbox.isChecked())

        # Sliders for each gauge
        self.create_gauge_controls(controls_layout)

        # Action buttons
        self.create_action_buttons(controls_layout)

        controls_layout.addStretch()
        main_layout.addWidget(controls_frame)

        # Right panel: gauge display
        self.gauge_display = GaugeDisplayWidget(400)
        self.gauge_display.set_gauge(self.gauge)
        main_layout.addWidget(self.gauge_display)

    def create_gauge_controls(self, layout):
        """創建各個指針的控制滑桿"""
        grid_layout = QGridLayout()

        self.sliders = {}
        gauge_configs = self.gauge.GAUGE_CONFIGS

        row = 0
        for gauge_id, config in gauge_configs.items():
            # Label
            label = QLabel(f"{config['name']} ({gauge_id})")
            grid_layout.addWidget(label, row, 0)

            # Slider
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(0)
            slider.setMaximum(len(config['values']) - 1)

            # Set initial value
            if gauge_id == "BATTERY":
                slider.setValue(len(config['values']) - 1)  # Full battery
            else:
                slider.setValue(0)

            slider.valueChanged.connect(lambda value, gid=gauge_id: self.on_slider_changed(gid, value))
            grid_layout.addWidget(slider, row, 1)

            # Value label
            value_label = QLabel(config['values'][slider.value()])
            grid_layout.addWidget(value_label, row, 2)

            self.sliders[gauge_id] = {
                'slider': slider,
                'label': value_label,
                'config': config
            }

            # Set initial gauge value
            self.gauge.set_value(gauge_id, slider.value())

            row += 1

        layout.addLayout(grid_layout)

    def create_action_buttons(self, layout):
        """創建動作按鈕"""
        button_layout = QHBoxLayout()

        save_btn = QPushButton("Save Image")
        save_btn.clicked.connect(self.save_image)
        button_layout.addWidget(save_btn)

        toggle_labels_btn = QPushButton("Toggle Labels")
        toggle_labels_btn.clicked.connect(self.toggle_labels)
        button_layout.addWidget(toggle_labels_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.reset_gauge)
        button_layout.addWidget(reset_btn)

        layout.addLayout(button_layout)

    def on_slider_changed(self, gauge_id, value):
        """滑桿值改變時的處理"""
        self.gauge.set_value(gauge_id, value)

        # Update value label
        config = self.sliders[gauge_id]['config']
        if value < len(config['values']):
            self.sliders[gauge_id]['label'].setText(config['values'][value])

    def on_reset_checkbox_changed(self, state):
        """Reset checkbox狀態改變"""
        if self.gauge:
            # Recreate gauge with new reset setting
            reset_on_start = state == Qt.Checked
            self.gauge = RD1Gauge(reset_on_start=reset_on_start)
            self.gauge_display.set_gauge(self.gauge)

            # Restore slider values
            for gauge_id, slider_info in self.sliders.items():
                value = slider_info['slider'].value()
                self.gauge.set_value(gauge_id, value)

    def save_image(self):
        """保存當前圖像"""
        if self.gauge:
            img = self.gauge.draw()
            output_path = Path(__file__).parent / "manual_control_output.png"
            img.save(output_path)
            print(f"Image saved to {output_path}")

    def toggle_labels(self):
        """切換標籤顯示"""
        if self.gauge:
            self.gauge.show_labels = not self.gauge.show_labels

    def reset_gauge(self):
        """重置指針"""
        if self.gauge:
            self.gauge.reset()

    def update_animation(self):
        """更新動畫"""
        if self.gauge:
            self.gauge.update_animation()
            self.gauge_display.update_display()


def main():
    """主函數"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = ManualControlApp()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()