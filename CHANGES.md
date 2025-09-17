# CHANGES

This file lists suggested staged commit messages and a short changelog for recent refactors.

## Suggested staged commits

1) docs: add analogGauge notes to README
   - Short: add docs about analogGauge location, public API and examples.

2) feat(analogGauge): keep gauge minimal + expose reset and interpolation controls
   - Short: remove glass/gloss from core, expose `RD1Gauge.reset()`, `interpolation_steps`, `quantize` and `animation_rate` options.

3) feat(analogGauge): add manual_control and run_integrated examples
   - Short: add `manual_control.py` for interactive testing and `run_integrated.py` to render/save integrated dial images.

4) feat(systemControl): add tk circular screen demo with film overlay UX
   - Short: add `systemControl/ui/tk_circular_screen.py` demo implementing film overlay hold+fade, import fallback for RD1Gauge, and reset-on-default behavior.

5) fix(demo): make overlay cancelable and block dial while active
   - Short: ensure film overlay appears before dial, use cancelable timers and apply per-mode overlay timing.

## Short changelog

- Removed glass/gloss overlay from `analogGauge/` core; demo/UI layer handles overlays.
- Exposed reset API and animation tuning parameters on `RD1Gauge`.
- Added examples: `analogGauge/manual_control.py`, `analogGauge/run_integrated.py`.
- Added `systemControl/ui/tk_circular_screen.py` demo and updated `systemControl/config/circular_modes.json` with film overlay timing settings.


