"""
PyQt-based circular screen that implements the CircularScreenAPI contract.

This module provides the main circular screen UI implementation. The controls are mapped
to the keyboard for testing:

- **Left Encoder (Mode):**
  - Rotate: Up/Down Arrow Keys
  - Press: Spacebar (resets to EV mode)

- **Right Encoder (Value):**
  - Rotate: Left/Right Arrow Keys

Run with: python -m analogGauge.circular_screen
"""
from __future__ import annotations

import json
import os
import math
import time
import sys
from typing import Callable, Dict, Any, Optional
from pathlib import Path
import traceback

# PyQt imports
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QLabel, QPushButton, QComboBox, QFrame)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QPixmap, QFont, QPalette
from PIL import Image

# Import RD1Gauge from same directory
try:
    from .rd1_gauge import RD1Gauge
except ImportError:
    # Fallback for direct execution
    try:
        from rd1_gauge import RD1Gauge
    except ImportError as e:
        print('Warning: failed to import RD1Gauge:', e)
        RD1Gauge = None


def _load_config_direct() -> Dict[str, Any]:
    """Load circular modes configuration.

    First tries to load from analogGauge's own config, then falls back to systemControl.
    """
    # Try analogGauge's own config first
    local_cfg_path = Path(__file__).parent / 'config' / 'circular_modes.json'
    if local_cfg_path.exists():
        cfg_path = local_cfg_path
    else:
        # Fallback to systemControl config
        cfg_path = Path(__file__).parent.parent / 'systemControl' / 'config' / 'circular_modes.json'
        if not cfg_path.exists():
            # Use default config if neither exists
            return _get_default_config()

    raw = cfg_path.read_text(encoding='utf-8')
    # Tolerate files that accidentally include Markdown code fences
    raw = raw.strip()
    if raw.startswith('```') and raw.endswith('```'):
        # remove the first and last fence line
        parts = raw.splitlines()
        if len(parts) >= 3:
            raw = '\n'.join(parts[1:-1])
    return json.loads(raw)

def _get_default_config() -> Dict[str, Any]:
    """Return default configuration for circular screen demo."""
    return {
        "modes": {
            "default": {"title": "拍攝模式"},
            "shutter": {
                "title": "快門速度",
                "values": ["AUTO", "1/8000", "1/4000", "1/2000", "1/1000", "1/500", "1/250", "1/125", "1/60", "1/30", "1/15", "1/8", "1/4", "1/2", "1", "2"]
            },
            "ev": {
                "title": "曝光補償",
                "values": ["-3.0", "-2.7", "-2.3", "-2.0", "-1.7", "-1.3", "-1.0", "-0.7", "-0.3", "0.0", "+0.3", "+0.7", "+1.0", "+1.3", "+1.7", "+2.0", "+2.3", "+2.7", "+3.0"]
            },
            "iso": {
                "title": "感光度",
                "values": ["AUTO", "100", "200", "400", "800", "1600", "3200", "6400"]
            },
            "focus": {
                "title": "對焦模式",
                "values": ["自動 (連續)", "自動 (單次)", "手動對焦"]
            },
            "wb": {
                "title": "白平衡",
                "values": ["自動", "日光", "陰天", "陰影", "鎢絲燈", "螢光燈", "閃光燈", "自訂"]
            },
            "quality": {
                "title": "影像品質",
                "values": ["RAW", "JPG", "R+J"]
            }
        }
    }


class GaugeWidget(QWidget):
    """Custom PyQt widget to display the RD1Gauge."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(480, 480)
        self.gauge = None
        self._tk_image = None
        self._preview_active = False
        self._preview_text = ""
        self._flash_active = False

    def set_gauge(self, gauge):
        """Set the RD1Gauge instance."""
        self.gauge = gauge

    def set_preview(self, active: bool, text: str = ""):
        """Set preview overlay state."""
        self._preview_active = active
        self._preview_text = text
        self.update()

    def set_flash(self, active: bool):
        """Set flash effect state."""
        self._flash_active = active
        self.update()

    def paintEvent(self, event):
        """Custom paint event to render the gauge."""
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.black)

        cx, cy = self.width() // 2, self.height() // 2

        if self.gauge:
            try:
                img = self.gauge.draw()
                # Convert PIL image to QPixmap using bytes buffer
                import io
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                buffer.seek(0)
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.getvalue())
                painter.drawPixmap(0, 0, pixmap)
            except Exception as e:
                painter.setPen(Qt.red)
                painter.setFont(QFont('Arial', 10))
                painter.drawText(self.rect(), Qt.AlignCenter, f"Error rendering gauge:\n{e}")
        else:
            painter.setPen(Qt.yellow)
            painter.setFont(QFont('Arial', 12))
            painter.drawText(self.rect(), Qt.AlignCenter, "RD1Gauge not available.")

        # Draw flash effect
        if self._flash_active:
            painter.setPen(Qt.green)
            painter.drawEllipse(5, 5, self.width()-10, self.height()-10)

        # Draw preview overlay
        if self._preview_active:
            # Create semi-transparent background
            painter.fillRect(cx - 120, cy - 25, 240, 50, Qt.black)
            painter.setPen(Qt.gray)
            painter.drawRect(cx - 120, cy - 25, 240, 50)
            painter.setPen(Qt.white)
            painter.setFont(QFont('Arial', 16, QFont.Bold))
            painter.drawText(cx - 120, cy - 25, 240, 50, Qt.AlignCenter, self._preview_text)


class CircularScreenAPI(QMainWindow):
    """PyQt implementation compatible with `circular_screen_api.CircularScreenAPI`.

    This is a concrete PyQt implementation used for demos and integration tests.
    """

    def __init__(self, config: Dict[str, Any], initial_style: str = 'rd1_classic'):
        super().__init__()
        self.config = config
        # Normalize config.modes
        raw_modes = config.get('modes', {})
        modes_list = [dict(m, id=mid) for mid, m in raw_modes.items()]
        self.modes = {m['id']: m for m in modes_list}
        self.mode_ids = list(self.modes.keys())
        self.current_mode_index = 0
        self.current_mode_id = self.mode_ids[0] if self.mode_ids else None

        # Callbacks
        self.on_apply: Optional[Callable[[str, Any], None]] = None
        self.on_action: Optional[Callable[[str, Dict[str, Any]], None]] = None

        # UI Setup
        self.width = 480  # Fixed size for the gauge display
        self.height = 480
        self.setWindowTitle('Circular Screen Interface')
        self.setStyleSheet("background-color: #111111; color: white;")

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        self._load_styles()

        self._add_encoder_test_buttons(main_layout)
        self._add_style_switcher(main_layout)

        # Add gauge widget
        self.gauge_widget = GaugeWidget()
        main_layout.addWidget(self.gauge_widget, alignment=Qt.AlignCenter)

        # --- Gauge and UI State ---
        self.gauge = None
        self.selected_index = 0

        # Status variables for fixed sub-dials
        self.current_quality_index = 0
        self.current_shots_index = 5
        self.current_battery_index = 4

        # Preview overlay state
        self._preview_timer = QTimer()
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self._hide_preview)

        # Flash effect timer
        self._flash_timer = QTimer()
        self._flash_timer.setSingleShot(True)
        self._flash_timer.timeout.connect(lambda: self.gauge_widget.set_flash(False))

        if RD1Gauge is not None:
            try:
                self.gauge = RD1Gauge(width=self.width, height=self.height, style=initial_style, show_labels=False, reset_on_start=True)
                self.gauge_widget.set_gauge(self.gauge)
                self._setup_sub_dials()
            except Exception as e:
                self.gauge = None
                print(f"Failed to initialize RD1Gauge: {e}")
                traceback.print_exc()

        # --- Animation Timing ---
        self._last_tick = time.time()
        self._animation_timer = QTimer()
        self._animation_timer.timeout.connect(self._tick)
        self._animation_timer.start(20)  # ~50 FPS

        # --- Initial Setup ---
        self.switch_mode(self.current_mode_id)

        # Make window focusable for keyboard events
        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event):
        """Handle keyboard events for encoder simulation."""
        if event.key() == Qt.Key_Up:
            self.handle_left_encoder_rotate(1)
        elif event.key() == Qt.Key_Down:
            self.handle_left_encoder_rotate(-1)
        elif event.key() == Qt.Key_Left:
            self.handle_right_encoder_rotate(-1)
        elif event.key() == Qt.Key_Right:
            self.handle_right_encoder_rotate(1)
        elif event.key() == Qt.Key_Space:
            self.handle_left_encoder_press()
        else:
            super().keyPressEvent(event)

    # --- Public API for Hardware ---

    def handle_left_encoder_rotate(self, direction: int):
        """Cycles through the main modes."""
        self.current_mode_index = (self.current_mode_index + direction) % len(self.mode_ids)
        next_mode_id = self.mode_ids[self.current_mode_index]
        self.switch_mode(next_mode_id)

    def handle_left_encoder_press(self):
        """Resets the mode to Exposure Compensation ('ev')."""
        self.switch_mode('ev')

    def handle_right_encoder_rotate(self, direction: int):
        """Adjusts the value within the current mode."""
        mode = self._current_mode()
        items = self._mode_items(mode)
        if not items: return

        self.selected_index = (self.selected_index + direction) % len(items)
        title = mode.get('title', mode['id'])
        display_text = self._get_item_display_text(mode, self.selected_index)

        if self.gauge:
            self.gauge.set_value('SHOTS', self.selected_index)
            if self.current_mode_id == 'quality':
                self.gauge.set_value('WB', self.selected_index)

        self._start_preview(title, display_text)

    # --- Internal Methods ---

    def _add_encoder_test_buttons(self, layout):
        """Adds buttons to the UI to simulate the two-encoder hardware."""
        top_label = QLabel("Left Encoder (Mode)")
        top_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(top_label)

        l_frame = QWidget()
        l_layout = QHBoxLayout(l_frame)
        l_layout.setContentsMargins(0, 0, 0, 0)

        btn_ccw = QPushButton("⟲ Rot CCW")
        btn_press = QPushButton("Press")
        btn_cw = QPushButton("Rot CW ⟳")

        btn_ccw.clicked.connect(lambda: self.handle_left_encoder_rotate(-1))
        btn_press.clicked.connect(self.handle_left_encoder_press)
        btn_cw.clicked.connect(lambda: self.handle_left_encoder_rotate(1))

        l_layout.addWidget(btn_ccw)
        l_layout.addWidget(btn_press)
        l_layout.addWidget(btn_cw)
        layout.addWidget(l_frame)

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #444444;")
        layout.addWidget(separator)

        bot_label = QLabel("Right Encoder (Value)")
        bot_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(bot_label)

        r_frame = QWidget()
        r_layout = QHBoxLayout(r_frame)
        r_layout.setContentsMargins(0, 0, 0, 0)

        btn_r_ccw = QPushButton("⟲ Rot CCW")
        btn_r_cw = QPushButton("Rot CW ⟳")

        btn_r_ccw.clicked.connect(lambda: self.handle_right_encoder_rotate(-1))
        btn_r_cw.clicked.connect(lambda: self.handle_right_encoder_rotate(1))

        r_layout.addWidget(btn_r_ccw)
        r_layout.addWidget(btn_r_cw)
        layout.addWidget(r_frame)

    def _add_style_switcher(self, layout):
        """Add style selection combo box."""
        style_frame = QWidget()
        style_layout = QHBoxLayout(style_frame)
        style_layout.setContentsMargins(0, 0, 0, 0)

        style_label = QLabel("Select Style:")
        self.style_combobox = QComboBox()
        self.style_combobox.addItems(self.available_styles)
        self.style_combobox.currentTextChanged.connect(self._on_style_change)

        style_layout.addWidget(style_label)
        style_layout.addWidget(self.style_combobox)
        layout.addWidget(style_frame)

    def _load_styles(self):
        """Load available styles."""
        styles_dir = Path(__file__).parent / 'styles'
        self.available_styles = []
        if styles_dir.is_dir():
            for style_file in styles_dir.glob('*.json'):
                self.available_styles.append(style_file.stem)
        self.available_styles.sort()
        if not self.available_styles:
            print("Warning: No style files found in analogGauge/styles/")

    def _on_style_change(self, selected_style: str):
        """Handle style change."""
        if self.gauge:
            try:
                self.gauge.load_style(selected_style)
                self.gauge_widget.update()  # Redraw the gauge with the new style
            except Exception as e:
                print(f"Error loading style {selected_style}: {e}")
                traceback.print_exc()

    def _setup_sub_dials(self):
        """Setup sub-dials."""
        if not self.gauge: return

        # Get quality mode and extract display values
        quality_mode = self.modes.get('quality', {})
        self.quality_values = self._mode_items(quality_mode)
        self.gauge.configure_gauge_dynamic('WB', '品質', self.quality_values)
        self.gauge.set_value('WB', self.current_quality_index)

        original_shots_config = RD1Gauge.GAUGE_CONFIGS.get("SHOTS", {})
        self.gauge.configure_gauge_dynamic('QUALITY', '張數', original_shots_config.get("values", []))
        self.gauge.set_value('QUALITY', self.current_shots_index)

        self.gauge.set_value('BATTERY', self.current_battery_index)

    def set_on_apply(self, cb: Callable[[str, Any], None]): self.on_apply = cb
    def set_on_action(self, cb: Callable[[str, Dict[str, Any]], None]): self.on_action = cb

    def switch_mode(self, mode_id: str):
        if mode_id not in self.modes: raise KeyError(f"Unknown mode_id: {mode_id}")
        self.current_mode_id = mode_id
        self.current_mode_index = self.mode_ids.index(mode_id)
        self.selected_index = 0

        mode = self._current_mode()
        items = self._mode_items(mode)
        title = mode.get('title', mode['id'])

        if self.gauge:
            self.gauge.configure_gauge_dynamic('SHOTS', title, items)
            self.gauge.set_value('SHOTS', self.selected_index)
            self.gauge.set_value('WB', self.current_quality_index)
            self.gauge.set_value('QUALITY', self.current_shots_index)
            self.gauge.set_value('BATTERY', self.current_battery_index)

        display_text = self._get_item_display_text(mode, self.selected_index)
        self._start_preview(title, display_text)

    def press_encoder(self):
        """This method is now for legacy/testing. The main press action is handle_left_encoder_press."""
        mode = self._current_mode()
        items = self._mode_items(mode)
        if not items:
            if self.on_action: self.on_action('press', {'mode': mode['id']})
            return

        selected_value = self._get_item_value(mode, self.selected_index)

        if self.current_mode_id == 'quality':
            self.current_quality_index = self.selected_index

        if self.on_apply:
            self.on_apply(mode['id'], selected_value)

        self._flash_selection()

    def update_from_state(self, state: Dict[str, Any]):
        if not self.gauge: return
        if 'battery' in state and state['battery'] != self.current_battery_index:
            self.current_battery_index = state['battery']
            self.gauge.set_value('BATTERY', self.current_battery_index)

    def render(self):
        """Force a redraw."""
        self.gauge_widget.update()

    def _current_mode(self) -> Dict[str, Any]: return self.modes[self.current_mode_id]
    def _mode_items(self, mode: Dict[str, Any]):
        """Get mode items, supporting both old format (values) and new format (items with alias/displayText)"""
        # New format with items containing value, alias, displayText
        if 'items' in mode:
            items = mode['items']
            # For gauge display, use alias if available, otherwise value
            return [item.get('alias', item.get('value', str(item))) for item in items]

        # Legacy format with simple values array
        return mode.get('values') or mode.get('demo_items', [])

    def _get_item_display_text(self, mode: Dict[str, Any], index: int) -> str:
        """Get display text for item at given index"""
        if 'items' in mode:
            items = mode['items']
            if 0 <= index < len(items):
                item = items[index]
                return item.get('displayText', item.get('value', str(item)))

        # Legacy format - just return the value
        items = mode.get('values') or mode.get('demo_items', [])
        if 0 <= index < len(items):
            return items[index]

        return "N/A"

    def _get_item_value(self, mode: Dict[str, Any], index: int) -> str:
        """Get actual value for item at given index (for backend communication)"""
        if 'items' in mode:
            items = mode['items']
            if 0 <= index < len(items):
                item = items[index]
                return item.get('value', str(item))

        # Legacy format - just return the value
        items = mode.get('values') or mode.get('demo_items', [])
        if 0 <= index < len(items):
            return items[index]

        return "N/A"

    def _flash_selection(self):
        """Flash a green border to indicate selection."""
        self.gauge_widget.set_flash(True)
        self._flash_timer.start(200)

    def _start_preview(self, title: str, value: str):
        self._preview_timer.stop()
        preview_text = f"{title}: {value}"
        self.gauge_widget.set_preview(True, preview_text)
        self._preview_timer.start(1500)

    def _hide_preview(self):
        self.gauge_widget.set_preview(False)

    def _tick(self):
        try:
            if self.gauge:
                now = time.time()
                dt = now - self._last_tick if hasattr(self, '_last_tick') and self._last_tick else (1/50.0)
                self.gauge.update_animation(dt)
                self._last_tick = now
                self.gauge_widget.update()
        except Exception:
            pass


def _demo():
    cfg = _load_config_direct()
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use a modern style

    window = CircularScreenAPI(cfg, initial_style='rd1_classic')

    def on_apply(mode_id, value):
        print(f'APPLY {mode_id} -> {value}')

    def on_action(action, payload):
        print(f'ACTION {action}: {payload}')

    window.set_on_apply(on_apply)
    window.set_on_action(on_action)

    window.show()
    window.setFocus()

    sys.exit(app.exec_())


if __name__ == '__main__':
    _demo()