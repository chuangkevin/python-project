Circular Screen PyQt Interface
===============================

This module provides a PyQt-based circular screen that loads
`systemControl/config/circular_modes.json` and exposes a dual-encoder
interface with RD1Gauge integration.

Controls:
- **Left Encoder (Mode):**
  - Up/Down arrows: cycle through modes
  - Spacebar: reset to EV mode
- **Right Encoder (Value):**
  - Left/Right arrows: adjust values within current mode

Run:

```pwsh
python -m systemControl.ui.circular_screen
```

Features:
- Real-time circular gauge display with animation
- Style switching system (4 available styles)
- Preview overlay for value changes
- Complete RD1Gauge integration
- Keyboard and button controls

The interface prints `APPLY` and `ACTION` messages to stdout when selections or actions occur.
