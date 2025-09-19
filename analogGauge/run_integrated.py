import os
import time
import json
from pathlib import Path

from rd1_gauge import RD1Gauge

def main():
    styles_dir = Path(__file__).parent / 'styles'
    available_styles = []
    if styles_dir.is_dir():
        for style_file in styles_dir.glob('*.json'):
            available_styles.append(style_file.stem)
    available_styles.sort()

    if not available_styles:
        print("No style files found in analogGauge/styles/. Exiting.")
        return

    output_dir = Path(__file__).parent
    os.makedirs(output_dir, exist_ok=True)

    for style_name in available_styles:
        print(f"Generating image for style: {style_name}")
        gauge = RD1Gauge(style=style_name)

        # Set example values
        gauge.set_value("SHOTS", 2)    # Points to "20"
        gauge.set_value("WB", 1)       # Points to "☀"
        gauge.set_value("BATTERY", 3)  # Points to "3/4"
        gauge.set_value("QUALITY", 1)  # Points to "H"

        # Update animation for a few steps to reach target values
        for _ in range(120):
            gauge.update_animation()

        img = gauge.draw()
        out_path = output_dir / f"integrated_{style_name}.png"
        img.save(out_path)
        print(f"Saved integrated image to {out_path}")


if __name__ == '__main__':
    main()
