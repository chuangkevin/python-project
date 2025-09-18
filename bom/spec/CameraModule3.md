# Raspberry Pi Camera Module 3 (Standard, 75°)

## 1. Overview

The Raspberry Pi Camera Module 3 is the successor to the Camera Module 2, featuring a higher resolution sensor, High Dynamic Range (HDR) capability, and a powered autofocus system. This document pertains to the standard 75-degree field of view model.

## 2. Key Hardware Specifications

| Feature | Specification | Notes |
| :--- | :--- | :--- |
| **Sensor** | Sony IMX708 | 1/2.43" sensor size |
| **Resolution** | 11.9 Megapixels | 4608 x 2592 pixels |
| **Aperture** | f/1.8 | Fixed, not adjustable |
| **Focal Length** | 4.74mm | |
| **Field of View** | 75° (Diagonal) | 66° (Horizontal), 41° (Vertical) |
| **Focus System** | Phase Detection Autofocus (PDAF) | Powered lens system |
| **Focus Range** | 10cm to Infinity | |
| **HDR Support** | Yes | Hardware-backed High Dynamic Range |
| **IR Cut Filter**| Integrated | Not present on NoIR models |
| **Video Modes** | 1080p50, 720p100, 480p120 | |
| **Output Format**| RAW10 | |
| **Dimensions** | 25 × 24 × 11.5mm | |

## 3. Software-Adjustable Parameters

Based on the hardware capabilities, the following parameters can be controlled via software and should be considered for the UI design:

*   **Focus:** The powered autofocus system allows for programmatic control over the focus position. This can be implemented as a manual focus mode or different autofocus modes (e.g., continuous, single-shot).
*   **Exposure Time (Shutter Speed):** A fundamental parameter for controlling motion blur and brightness.
*   **Gain (ISO):** Controls the sensor's sensitivity to light.
*   **White Balance (WB):** Can be set to automatic or various presets (e.g., Daylight, Cloudy, Tungsten).
*   **Exposure Value (EV):** Digital exposure compensation can be implemented.
*   **HDR Mode:** Can be toggled on or off.