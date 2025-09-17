"""Circular screen API stubs and integration helpers.

This file defines a minimal interface contract that the rest of the
application can rely on. The actual implementation can live in
`tk_circular_screen.py` (a Tkinter implementation) or reuse
`fixed_dual_screen_system.py` components.
"""
from typing import Callable, Dict, Any, Optional


class CircularScreenAPI:
    """Interface / docstring container for the circular screen component."""

    def __init__(self):
        self.on_apply: Optional[Callable[[str, Any], None]] = None
        self.on_action: Optional[Callable[[str, Dict[str, Any]], None]] = None
        self.current_mode: Optional[str] = None

    def set_on_apply(self, callback: Callable[[str, Any], None]):
        """Register a callback invoked when the UI 'applies' a control.

        callback(control_name, value)
        """
        self.on_apply = callback

    def set_on_action(self, callback: Callable[[str, Dict[str, Any]], None]):
        """Register a callback for UI-triggered actions (whitecard, capture, etc.).

        callback(action_name, payload_dict)
        """
        self.on_action = callback

    def load_mode_config(self, config: Dict[str, Any]):
        """Load a parsed config mapping (from circular_mode_config.load_config())."""
        raise NotImplementedError()

    def switch_mode(self, mode_id: str):
        """Switch displayed mode on the circular screen.

        Should trigger animations and update internal state.
        """
        raise NotImplementedError()

    def rotate_encoder(self, dial: str, direction: int):
        """External call to simulate encoder rotation (dial = 'left'|'right')."""
        raise NotImplementedError()

    def press_encoder(self, dial: str):
        """External call to simulate encoder press/confirm."""
        raise NotImplementedError()

    def update_from_state(self, state: Dict[str, Any]):
        """Update UI elements from system state (battery, mode, storage)."""
        raise NotImplementedError()

    def render(self):
        """Force a redraw (useful for unit tests)."""
        raise NotImplementedError()
