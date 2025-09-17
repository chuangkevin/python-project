Circular Screen Tkinter Demo
=================================

This small demo demonstrates a Tkinter-based circular screen that loads
`systemControl/config/circular_modes.json` and exposes a simple encoder-like
interface.

Controls:
- Left / Right arrows: rotate selection
- Enter: press / apply selected item
- M: cycle to next mode

Run:

```pwsh
python -m systemControl.ui.tk_circular_screen
```

The demo prints `APPLY` and `ACTION` messages to stdout when selections or actions occur.
