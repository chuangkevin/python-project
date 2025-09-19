"""
SystemControl integration wrapper for analogGauge circular screen.

This module provides a wrapper that integrates the analogGauge.circular_screen
component into the systemControl application framework.

Controls:
- **Left Encoder (Mode):**
  - Rotate: Up/Down Arrow Keys
  - Press: Spacebar (resets to EV mode)

- **Right Encoder (Value):**
  - Rotate: Left/Right Arrow Keys

Run with: python -m systemControl.ui.circular_screen
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Any

# Add project root to sys.path for module imports
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from analogGauge.circular_screen import CircularScreenAPI as AnalogGaugeAPI, _load_config_direct
    from PyQt5.QtWidgets import QApplication
except ImportError as e:
    print(f"Failed to import analogGauge components: {e}")
    raise


def _load_systemcontrol_config() -> Dict[str, Any]:
    """Load configuration with systemControl-specific settings."""
    # Load from systemControl's config directory
    cfg_path = Path(__file__).parent.parent / 'config' / 'circular_modes.json'
    if cfg_path.exists():
        import json
        raw = cfg_path.read_text(encoding='utf-8')
        raw = raw.strip()
        if raw.startswith('```') and raw.endswith('```'):
            parts = raw.splitlines()
            if len(parts) >= 3:
                raw = '\n'.join(parts[1:-1])
        return json.loads(raw)
    else:
        # Fallback to analogGauge's config loader
        return _load_config_direct()


class CircularScreenAPI(AnalogGaugeAPI):
    """SystemControl wrapper for analogGauge circular screen."""

    def __init__(self, config: Dict[str, Any] = None, initial_style: str = 'rd1_classic'):
        if config is None:
            config = _load_systemcontrol_config()

        super().__init__(config, initial_style)
        self.setWindowTitle('SystemControl - Circular Interface')

    def integrate_with_systemcontrol(self, system_controller):
        """Integration point for systemControl application."""
        # This method can be implemented to integrate with the main system
        # For now, it's a placeholder for future integration
        pass


def _demo():
    """Demo function for systemControl integration."""
    cfg = _load_systemcontrol_config()
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    window = CircularScreenAPI(cfg, initial_style='rd1_classic')

    def on_apply(mode_id, value):
        print(f'SystemControl APPLY {mode_id} -> {value}')

    def on_action(action, payload):
        print(f'SystemControl ACTION {action}: {payload}')

    window.set_on_apply(on_apply)
    window.set_on_action(on_action)

    window.show()
    window.setFocus()

    sys.exit(app.exec_())


if __name__ == '__main__':
    _demo()