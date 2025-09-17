"""
Tkinter-based circular screen skeleton that implements the CircularScreenAPI contract.

This module loads `systemControl/config/circular_modes.json` via the existing
`circular_mode_config` loader and provides a simple interactive demo. Use arrow
keys to rotate (Left/Right) and Enter to press/select. Press M to cycle modes.

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
        # Normalize config.modes which may be a mapping (id -> mode) or a list
        raw_modes = config.get('modes', {})
        modes_list = []
        if isinstance(raw_modes, dict):
            for mid, m in raw_modes.items():
                # ensure we don't mutate original
                mm = dict(m)
                mm.setdefault('id', mid)
                modes_list.append(mm)
        elif isinstance(raw_modes, list):
            modes_list = [dict(m) for m in raw_modes]
        else:
            modes_list = []

        self.modes = {m['id']: m for m in modes_list}
        self.mode_ids = list(self.modes.keys())
        self.current_mode_index = 0
        self.current_mode_id = self.mode_ids[0] if self.mode_ids else None

        self.on_apply: Optional[Callable[[str, Any], None]] = None
        self.on_action: Optional[Callable[[str, Dict[str, Any]], None]] = None

        self.width = 400
        self.height = 400
        self.radius = min(self.width, self.height) // 2 - 10

        self.canvas = tk.Canvas(master, width=self.width, height=self.height, bg='#111')
        self.canvas.pack()

        # Button frame for mouse users
        btn_frame = tk.Frame(master, bg='#111')
        btn_frame.pack(fill='x', pady=(6, 12))

        btn_prev = tk.Button(btn_frame, text='⟵ Prev', command=lambda: self.rotate_encoder(-1))
        btn_prev.pack(side='left', expand=True, padx=6)

        btn_next = tk.Button(btn_frame, text='Next ⟶', command=lambda: self.rotate_encoder(1))
        btn_next.pack(side='left', expand=True, padx=6)

        btn_select = tk.Button(btn_frame, text='Select', command=lambda: self.press_encoder())
        btn_select.pack(side='left', expand=True, padx=6)

        btn_mode = tk.Button(btn_frame, text='Mode', command=lambda: self._cycle_mode())
        btn_mode.pack(side='left', expand=True, padx=6)

        # RD1Gauge instance for dial rendering (used in default/film modes)
        self.gauge = None
        if RD1Gauge is not None:
            try:
                # For needle-centric UI hide labels
                # Do NOT perform reset-on-start in the demo (prevents reset animation on each mode switch)
                self.gauge = RD1Gauge(width=400, height=400, show_labels=False, reset_on_start=False)
            except Exception:
                self.gauge = None

        # animation / rendering state
        self._tk_image = None  # keep reference to PhotoImage
        self._last_tick = time.time()
        self._tick_interval_ms = 50  # 20 Hz

        # film overlay config (milliseconds) - will be initialized per-mode
        self.film_overlay_ms = 2000
        self.film_fade_steps = 6
        # overlay runtime state
        self._overlay_id = None
        self._overlay_text_id = None
        self._overlay_active = False
        self._overlay_text = None
        self._overlay_fade_remaining = 0
        self._overlay_stipple_index = 0
        # small set of stipple patterns for a coarse fade (Tk doesn't support alpha on canvas)
        self._overlay_stipples = ['gray12', 'gray25', 'gray50', 'gray75']
        # hold/fade timer ids (so we can cancel when switching modes)
        self._overlay_hold_id = None
        self._overlay_fade_id = None
        # restore-on-reset poll id (to restore real values after reset animation)
        self._restore_poll_id = None
        # apply any mode-specific overrides from the provided config
        self._apply_mode_settings(self._current_mode())

        # Start periodic tick
        self.master.after(self._tick_interval_ms, self._tick)

        self.center = (self.width // 2, self.height // 2)

        # UI state
        self.selected_index = 0

        # Draw initial
        self._draw()

        # Key bindings to simulate encoder
        master.bind('<Left>', lambda e: self.rotate_encoder(-1))
        master.bind('<Right>', lambda e: self.rotate_encoder(1))
        master.bind('<Return>', lambda e: self.press_encoder())
        master.bind('m', lambda e: self._cycle_mode())

    # Callback registration
    def set_on_apply(self, cb: Callable[[str, Any], None]):
        self.on_apply = cb

    def set_on_action(self, cb: Callable[[str, Dict[str, Any]], None]):
        self.on_action = cb

    # API methods
    def switch_mode(self, mode_id: str):
        if mode_id not in self.modes:
            raise KeyError(f"Unknown mode_id: {mode_id}")
        # If switching away from film mode, ensure any overlay/timers are canceled
        if getattr(self, 'current_mode_id', None) == 'film' and mode_id != 'film':
            try:
                if getattr(self, '_overlay_hold_id', None):
                    self.master.after_cancel(self._overlay_hold_id)
            except Exception:
                pass
            try:
                if getattr(self, '_overlay_fade_id', None):
                    self.master.after_cancel(self._overlay_fade_id)
            except Exception:
                pass
            # clear overlay state
            self._overlay_active = False
            self._overlay_text = None
            self._overlay_fade_remaining = 0
            self._overlay_stipple_index = 0
            # ensure UI redraw
            try:
                self.canvas.delete('all')
            except Exception:
                pass
        self.current_mode_id = mode_id
        self.current_mode_index = self.mode_ids.index(mode_id)
        self.selected_index = 0
        # apply mode-specific settings (so film can override overlay timings)
        self._apply_mode_settings(self._current_mode())
        # If switching into default mode, perform reset animation then restore values
        if mode_id == 'default' and self.gauge is not None:
            # save current intended targets so we can restore after reset
            try:
                saved_targets = {k: int(self.gauge.target_values.get(k, 0)) for k in self.gauge.GAUGE_CONFIGS}
            except Exception:
                saved_targets = {}
            # trigger reset animation (max -> 0)
            try:
                self.gauge.reset()
            except Exception:
                pass

            # cancel any existing restore poll
            try:
                if self._restore_poll_id:
                    self.master.after_cancel(self._restore_poll_id)
            except Exception:
                pass

            # start polling to detect when reset animation finished
            def _poll_restore():
                all_done = True
                try:
                    for g in self.gauge.GAUGE_CONFIGS:
                        if getattr(self.gauge, '_anim_start_time', {}).get(g) is not None:
                            all_done = False
                            break
                except Exception:
                    all_done = True

                if all_done:
                    # restore saved targets
                    try:
                        for g, v in saved_targets.items():
                            # use set_value to animate to desired value
                            self.gauge.set_value(g, v)
                    except Exception:
                        pass
                    return

                # continue polling
                self._restore_poll_id = self.master.after(self._tick_interval_ms, _poll_restore)

            _poll_restore()
        # If switching into film mode, show overlay first then let dial appear after hold+fade
        if mode_id == 'film':
            mode = self._current_mode()
            items = self._mode_items(mode)
            sel = str(items[self.selected_index]) if items else ''
            self._start_overlay(sel)
            return

        self._draw()

    def rotate_encoder(self, steps: int = 1):
        mode = self._current_mode()
        items = self._mode_items(mode)
        if not items:
            return
        self.selected_index = (self.selected_index + steps) % len(items)
        self._draw()
        # If we're in film mode, show overlay immediately on rotate
        if mode.get('id') == 'film':
            selected = items[self.selected_index]
            self._start_overlay(str(selected))
    def press_encoder(self):
        mode = self._current_mode()
        items = self._mode_items(mode)
        if not items:
            # toggle behavior: call action for modes without items
            if self.on_action:
                self.on_action('press', {'mode': mode['id']})
            return
        selected = items[self.selected_index]
        # If film mode, show overlay then return to dial after a short duration
        if mode['id'] == 'film':
            # call apply immediately then show overlay
            if self.on_apply:
                self.on_apply(mode['id'], selected)
            self._start_overlay(str(selected))
            return

        if self.on_apply:
            self.on_apply(mode['id'], selected)
        # Visual feedback
        self._flash_selection()

    def update_from_state(self, state: Dict[str, Any]):
        # For demo, respond to external state changes (e.g., current mode)
        if 'mode' in state:
            try:
                self.switch_mode(state['mode'])
            except KeyError:
                pass

    def render(self):
        self._draw()

    # Internal helpers
    def _current_mode(self) -> Dict[str, Any]:
        return self.modes[self.current_mode_id]

    def _mode_items(self, mode: Dict[str, Any]):
        # Modes may define `items` inline or `values` for numeric ranges; keep simple mapping
        items = mode.get('items') or mode.get('values') or []
        # If mode declares an items_source (external), the demo can't resolve app settings.
        # Provide a small demo fallback so the film selector and overlay can show in the demo.
        if not items and mode.get('items_source'):
            # allow explicit demo items in config
            demo = mode.get('demo_items')
            if demo:
                return list(demo)
            # sensible defaults for a film selector demo
            return ['Portra 400', 'Ektachrome', 'Tri-X 400', 'Ilford HP5']
        return items

    def _apply_mode_settings(self, mode: Dict[str, Any]):
        """Apply per-mode overrides for overlay timing if present.

        The mode dictionary may include `film_overlay_ms` and `film_fade_steps` to
        override the demo defaults. If not present, fall back to global config keys
        or existing instance defaults.
        """
        if not isinstance(mode, dict):
            return
        # per-mode override
        if 'film_overlay_ms' in mode:
            try:
                self.film_overlay_ms = int(mode['film_overlay_ms'])
            except Exception:
                pass
        elif 'film_overlay_ms' in self.config:
            try:
                self.film_overlay_ms = int(self.config.get('film_overlay_ms'))
            except Exception:
                pass

        if 'film_fade_steps' in mode:
            try:
                self.film_fade_steps = int(mode['film_fade_steps'])
            except Exception:
                pass
        elif 'film_fade_steps' in self.config:
            try:
                self.film_fade_steps = int(self.config.get('film_fade_steps'))
            except Exception:
                pass

    def _draw(self):
        self.canvas.delete('all')
        cx, cy = self.center
        r = self.radius

        # Outer circle
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill='#222', outline='#555', width=4)

        # Mode title
        mode = self._current_mode()
        title = mode.get('title', mode['id']).upper()
        self.canvas.create_text(cx, cy - r + 30, text=title, fill='#fff', font=('Helvetica', 14, 'bold'))
        # If an overlay is active (film preview), draw it exclusively and skip the dial/items.
        # This guarantees the overlay is shown before any dial rendering and blocks the
        # underlying dial while the hold+fade sequence runs.
        if getattr(self, '_overlay_active', False) and getattr(self, '_overlay_text', None):
            stip = getattr(self, '_overlay_stipples', None)
            if stip:
                st = stip[self._overlay_stipple_index]
            else:
                st = 'gray25'
            self._overlay_id = self.canvas.create_oval(cx-120, cy-40, cx+120, cy+40, fill='#000', stipple=st, outline='')
            self._overlay_text_id = self.canvas.create_text(cx, cy, text=self._overlay_text or '', fill='#fff', font=('Helvetica', 16, 'bold'))
            return
        # If in default mode, always render the RD1Gauge (needle-centric)
        if self.current_mode_id == 'default' and self.gauge is not None:
            try:
                now = time.time()
                dt = now - self._last_tick if self._last_tick else None
                self.gauge.update_animation(dt)
                self._last_tick = now
                img = self.gauge.draw_integrated_rd1_display()
                self._tk_image = ImageTk.PhotoImage(img)
                self.canvas.create_image(cx, cy, image=self._tk_image)
            except Exception:
                pass
            return

        # If RD1Gauge not present, draw a simple placeholder needle so Default still shows
        if self.current_mode_id == 'default' and self.gauge is None:
            # Draw a simple needle pointing to a pseudo-value based on time
            angle = (time.time() % 6.28)
            nx = cx + int((r - 80) * math.cos(angle))
            ny = cy + int((r - 80) * math.sin(angle))
            self.canvas.create_line(cx, cy, nx, ny, fill='#f55', width=4)
            self.canvas.create_oval(cx-6, cy-6, cx+6, cy+6, fill='#fff')
            return
            return

        # (overlay handling is done above and returns early if active)

        # Non-default modes: render item arc (or for film, when overlay not active show dial below)
        # For film mode, when overlay not active we want to show the film selector
        # items (rendered below) rather than the integrated dial. Do not draw the
        # gauge here for film mode.

        # Items list rendered around lower half of circle
        items = self._mode_items(mode)
        n = len(items)
        if n == 0:
            # Show short instruction
            self.canvas.create_text(cx, cy, text=mode.get('hint', 'Press Enter'), fill='#ccc', font=('Helvetica', 12))
            return

        # arc start and sweep
        start_angle = -120
        sweep = 240
        angle_step = sweep / max(1, n-1) if n > 1 else 0

        for i, item in enumerate(items):
            angle = math.radians(start_angle + i * angle_step)
            ix = cx + int((r - 70) * math.cos(angle))
            iy = cy + int((r - 70) * math.sin(angle))

            name = str(item)
            color = '#fff' if i == self.selected_index else '#9aa'
            font = ('Helvetica', 12, 'bold') if i == self.selected_index else ('Helvetica', 11)
            self.canvas.create_text(ix, iy, text=name, fill=color, font=font)

        # Draw a small indicator for the selected item
        sel_angle = math.radians(start_angle + self.selected_index * angle_step)
        sx = cx + int((r - 30) * math.cos(sel_angle))
        sy = cy + int((r - 30) * math.sin(sel_angle))
        self.canvas.create_oval(sx-8, sy-8, sx+8, sy+8, fill='#0f0' if n else '#555')
        
    def _flash_selection(self):
        # Simple visual flash when pressing
        orig = self.canvas.itemcget('all', 'fill') if False else None
        self.canvas.create_oval(self.center[0]-20, self.center[1]-20, self.center[0]+20, self.center[1]+20, outline='#0f0', width=3, tag='flash')
        self.master.after(200, lambda: self.canvas.delete('flash'))

    def _cycle_mode(self):
        # Use switch_mode to ensure per-mode settings and film overlay behavior run
        self.current_mode_index = (self.current_mode_index + 1) % len(self.mode_ids)
        next_mode = self.mode_ids[self.current_mode_index]
        self.switch_mode(next_mode)

    # Film overlay helpers
    def _show_film_overlay(self, text: str):
        # Backwards-compatible small helper: use persistent overlay state
        self._start_overlay(text)

    def _fade_overlay(self, steps: int):
        # Persistent overlay fade: when steps reach 0 hide overlay and redraw
        # If overlay has been cancelled (e.g., mode switched), abort
        if not getattr(self, '_overlay_active', False):
            return
        if steps <= 0:
            self._overlay_active = False
            self._overlay_text = None
            self._overlay_fade_remaining = 0
            # ensure canvas cleaned and redraw base
            self.canvas.delete('all')
            self._draw()
            return

        # schedule next fade step
        self._overlay_fade_remaining = steps - 1
        # pick a stipple based on remaining steps (coarse approximation)
        idx = max(0, min(len(self._overlay_stipples)-1, int((steps / max(1, self.film_fade_steps)) * (len(self._overlay_stipples)-1))))
        self._overlay_stipple_index = idx
        # redraw to show faded overlay
        self._draw()
        # schedule next fade step; store id so it can be cancelled if needed
        self._overlay_fade_id = self.master.after(int(self._tick_interval_ms), lambda: self._fade_overlay(steps-1))

    def _start_overlay(self, text: str):
        # Cancel existing hold/fade timers
        try:
            if getattr(self, '_overlay_hold_id', None):
                self.master.after_cancel(self._overlay_hold_id)
                self._overlay_hold_id = None
            if getattr(self, '_overlay_fade_id', None):
                self.master.after_cancel(self._overlay_fade_id)
                self._overlay_fade_id = None
        except Exception:
            pass

        # Only start overlay if we are currently in film mode. This prevents
        # stale timers or accidental calls from other modes (e.g., ISO) from
        # showing the film preview UI.
        if getattr(self, 'current_mode_id', None) != 'film':
            return

        self._overlay_active = True
        self._overlay_text = text
        self._overlay_fade_remaining = self.film_fade_steps
        # force a redraw so overlay appears immediately
        self._draw()
        # schedule fade to start after hold duration
        self._overlay_hold_id = self.master.after(int(self.film_overlay_ms), lambda: self._fade_overlay(self._overlay_fade_remaining))

    # periodic tick to update gauge animation and re-render when required
    def _tick(self):
        try:
            # update gauge animation if present
            if self.gauge is not None:
                now = time.time()
                dt = now - self._last_tick if self._last_tick else None
                self.gauge.update_animation(dt)
                self._last_tick = now
                # only re-render if currently in default mode
                if self.current_mode_id == 'default':
                    self._draw()
        except Exception:
            pass
        finally:
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
