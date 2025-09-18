"""
Tkinter-based circular screen skeleton that implements the CircularScreenAPI contract.

This module provides a demo of the two-encoder UI. The controls are mapped
to the keyboard for testing:

- **Left Encoder (Mode):**
  - Rotate: Up/Down Arrow Keys
  - Press: Spacebar (resets to EV mode)

- **Right Encoder (Value):**
  - Rotate: Left/Right Arrow Keys

Run with: python -m systemControl.ui.tk_circular_screen
"""
from __future__ import annotations

import json
import os
import math
import time
import tkinter as tk
from typing import Callable, Dict, Any, Optional
from pathlib import Path
from PIL import ImageTk
import traceback
import sys

# Add project root to sys.path for module imports
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import RD1Gauge from analogGauge (report errors to help debugging)
try:
    from analogGauge.rd1_gauge import RD1Gauge
except Exception as e:
    print('Warning: failed to import RD1Gauge from analogGauge.rd1_gauge:', e)
    traceback.print_exc()
    RD1Gauge = None
    # Try a fallback: load the module directly from the repository path
    try:
        import importlib.util
        repo_root = Path(__file__).resolve().parents[2]
        alt_path = repo_root / 'analogGauge' / 'rd1_gauge.py'
        if alt_path.exists():
            spec = importlib.util.spec_from_file_location('analogGauge.rd1_gauge', str(alt_path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            RD1Gauge = getattr(module, 'RD1Gauge', None)
            if RD1Gauge:
                print('Loaded RD1Gauge via fallback from', alt_path)
    except Exception:
        pass


def _load_config_direct() -> Dict[str, Any]:
    """Load circular_modes.json directly without importing package-level code.

    This avoids executing `systemControl.__init__` which may import other
    application modules not available in the demo environment.
    """
    cfg_path = Path(__file__).parent.parent / 'config' / 'circular_modes.json'
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config file not found: {cfg_path}")
    raw = cfg_path.read_text(encoding='utf-8')
    # Tolerate files that accidentally include Markdown code fences
    raw = raw.strip()
    if raw.startswith('```') and raw.endswith('```'):
        # remove the first and last fence line
        parts = raw.splitlines()
        if len(parts) >= 3:
            raw = '\n'.join(parts[1:-1])
    return json.loads(raw)


class CircularScreenAPI:
    """Minimal runtime API compatible with `circular_screen_api.CircularScreenAPI`.

    This is a concrete Tkinter implementation used for demos and integration tests.
    """

    def __init__(self, master: tk.Tk, config: Dict[str, Any]):
        self.master = master
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
        self.width = 400
        self.height = 400
        self.canvas = tk.Canvas(master, width=self.width, height=self.height, bg='#111')
        self.canvas.pack()
        self._add_encoder_test_buttons(master)

        # --- Gauge and UI State ---
        self.gauge = None
        self._tk_image = None
        self.selected_index = 0

        # Status variables for fixed sub-dials
        self.current_quality_index = 0
        self.current_shots_index = 5
        self.current_battery_index = 4

        # Preview overlay state
        self._preview_active = False
        self._preview_text = ""
        self._preview_timer = None

        if RD1Gauge is not None:
            try:
                self.gauge = RD1Gauge(width=400, height=400, show_labels=False, reset_on_start=True)
                self._setup_sub_dials()
            except Exception as e:
                self.gauge = None
                print(f"Failed to initialize RD1Gauge: {e}")

        # --- Animation Timing ---
        self._last_tick = time.time()
        self._tick_interval_ms = 20  # ~50 FPS

        # --- Initial Setup ---
        self.switch_mode(self.current_mode_id)
        self.master.after(self._tick_interval_ms, self._tick)

        # --- Key Bindings (for testing) ---
        master.bind('<Up>', lambda e: self.handle_left_encoder_rotate(1))
        master.bind('<Down>', lambda e: self.handle_left_encoder_rotate(-1))
        master.bind('<Left>', lambda e: self.handle_right_encoder_rotate(-1))
        master.bind('<Right>', lambda e: self.handle_right_encoder_rotate(1))
        master.bind('<space>', lambda e: self.handle_left_encoder_press())

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
        value = items[self.selected_index]

        if self.gauge:
            self.gauge.set_value('SHOTS', self.selected_index)
            if self.current_mode_id == 'quality':
                self.gauge.set_value('WB', self.selected_index)
        
        self._start_preview(title, value)
        self._draw()

    # --- Internal Methods ---

    def _add_encoder_test_buttons(self, master):
        """Adds buttons to the UI to simulate the two-encoder hardware."""
        top_frame = tk.Frame(master, bg='#111')
        top_frame.pack(fill='x', pady=(6, 2))
        tk.Label(top_frame, text="Left Encoder (Mode)", fg="white", bg="#111").pack()

        l_frame = tk.Frame(master, bg='#111')
        l_frame.pack(fill='x', pady=(2, 6))
        tk.Button(l_frame, text="⟲ Rot CCW", command=lambda: self.handle_left_encoder_rotate(-1)).pack(side='left', expand=True)
        tk.Button(l_frame, text="Press", command=self.handle_left_encoder_press).pack(side='left', expand=True)
        tk.Button(l_frame, text="Rot CW ⟳", command=lambda: self.handle_left_encoder_rotate(1)).pack(side='left', expand=True)

        tk.Frame(master, height=2, bg="#444").pack(fill='x', padx=20, pady=10)

        bot_frame = tk.Frame(master, bg='#111')
        bot_frame.pack(fill='x', pady=(2, 6))
        tk.Label(bot_frame, text="Right Encoder (Value)", fg="white", bg="#111").pack()
        
        r_frame = tk.Frame(master, bg='#111')
        r_frame.pack(fill='x', pady=(2, 12))
        tk.Button(r_frame, text="⟲ Rot CCW", command=lambda: self.handle_right_encoder_rotate(-1)).pack(side='left', expand=True)
        tk.Button(r_frame, text="Rot CW ⟳", command=lambda: self.handle_right_encoder_rotate(1)).pack(side='left', expand=True)

    def _setup_sub_dials(self):
        if not self.gauge: return
        self.quality_values = self.modes.get('quality', {}).get('values', ['RAW', 'JPG', 'R+J'])
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

        self._start_preview(title, items[self.selected_index] if items else "N/A")
        self._draw()

    def press_encoder(self):
        """This method is now for legacy/testing. The main press action is handle_left_encoder_press."""
        mode = self._current_mode()
        items = self._mode_items(mode)
        if not items:
            if self.on_action: self.on_action('press', {'mode': mode['id']})
            return

        selected_value = items[self.selected_index]

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

    def render(self): self._draw()

    def _current_mode(self) -> Dict[str, Any]: return self.modes[self.current_mode_id]
    def _mode_items(self, mode: Dict[str, Any]):
        return mode.get('values') or mode.get('demo_items', [])

    def _draw(self):
        if not self.canvas or not self.master.winfo_exists(): return
        self.canvas.delete('all')
        cx, cy = self.width // 2, self.height // 2

        if self.gauge:
            try:
                img = self.gauge.draw_integrated_rd1_display()
                self._tk_image = ImageTk.PhotoImage(img)
                self.canvas.create_image(cx, cy, image=self._tk_image)
            except Exception as e:
                self.canvas.create_text(cx, cy, text=f"""Error rendering gauge:\n{e}""", fill='red', font=('Helvetica', 10))
        else:
            self.canvas.create_text(cx, cy, text="RD1Gauge not available.", fill='yellow', font=('Helvetica', 12))

        if self._preview_active:
            self.canvas.create_rectangle(cx - 120, cy - 25, cx + 120, cy + 25, fill="black", stipple="gray50", outline='#888', width=2)
            self.canvas.create_text(cx, cy, text=self._preview_text, fill='#FFF', font=('Helvetica', 16, 'bold'))
        
    def _flash_selection(self):
        if not self.canvas or not self.master.winfo_exists(): return
        border_id = self.canvas.create_oval(5, 5, self.width-5, self.height-5, outline='#0f0', width=4, tag='flash')
        self.master.after(200, lambda: self.canvas.delete(border_id))

    def _start_preview(self, title: str, value: str):
        if self._preview_timer:
            self.master.after_cancel(self._preview_timer)
        self._preview_text = f"{title}: {value}"
        self._preview_active = True
        self._preview_timer = self.master.after(1500, self._hide_preview)

    def _hide_preview(self):
        self._preview_active = False
        self._preview_timer = None
        self._draw()

    def _tick(self):
        try:
            if self.gauge:
                now = time.time()
                dt = now - self._last_tick if hasattr(self, '_last_tick') and self._last_tick else (1/50.0)
                self.gauge.update_animation(dt)
                self._last_tick = now
                self._draw()
        except Exception:
            pass
        finally:
            if self.master.winfo_exists():
                self.master.after(self._tick_interval_ms, self._tick)



def _demo():
    cfg = _load_config_direct()
    root = tk.Tk()
    root.title('Circular Screen Demo')
    app = CircularScreenAPI(root, cfg)

    def on_apply(mode_id, value):
        print(f'APPLY {mode_id} -> {value}')

    def on_action(action, payload):
        print(f'ACTION {action}: {payload}')

    app.set_on_apply(on_apply)
    app.set_on_action(on_action)

    root.mainloop()


if __name__ == '__main__':
    _demo()
