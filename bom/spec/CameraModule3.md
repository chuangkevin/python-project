{
  "CameraModule3": {
    "sensor": {
      "name": "Sony IMX708",
      "type": "BSI Stacked CMOS",
      "resolution": "4608x2592",
      "megapixels": 11.9,
      "pixel_size_um": 1.4,
      "diagonal_mm": 7.4,
      "output_format": "RAW10 Bayer",
      "hdr_max_resolution": "2304x1296 (3MP)"
    },
    "variants": [
      {
        "name": "Standard",
        "focal_length_mm": 4.74,
        "fov_deg": { "diagonal": 75, "horizontal": 66, "vertical": 41 },
        "aperture": "f/1.8",
        "focus_range": "10cm – ∞",
        "ir_cut": true
      },
      {
        "name": "NoIR",
        "focal_length_mm": 4.74,
        "fov_deg": { "diagonal": 75, "horizontal": 66, "vertical": 41 },
        "aperture": "f/1.8",
        "focus_range": "10cm – ∞",
        "ir_cut": false
      },
      {
        "name": "Wide",
        "focal_length_mm": 2.75,
        "fov_deg": { "diagonal": 120, "horizontal": 102, "vertical": 67 },
        "aperture": "f/2.2",
        "focus_range": "5cm – ∞",
        "ir_cut": true
      },
      {
        "name": "Wide NoIR",
        "focal_length_mm": 2.75,
        "fov_deg": { "diagonal": 120, "horizontal": 102, "vertical": 67 },
        "aperture": "f/2.2",
        "focus_range": "5cm – ∞",
        "ir_cut": false
      }
    ],
    "photo_modes": {
      "max_resolution": "4608x2592 (11.9MP)",
      "hdr_resolution": "2304x1296 (3MP)",
      "raw_format": "10-bit Bayer (RAW10)"
    },
    "video_modes": [
      { "resolution": "4608x2592", "fps": 14 },
      { "resolution": "2304x1296", "fps": 56 },
      { "resolution": "1536x864", "fps": 120 },
      { "resolution": "1080p", "fps": 50 },
      { "resolution": "720p", "fps": 100 },
      { "resolution": "480p", "fps": 120 },
      { "resolution": "2304x1296 HDR", "fps": 30 }
    ],
    "module": {
      "dimensions_mm": { "width": 25, "height": 24, "depth": 11.5 },
      "connector": "15-pin MIPI CSI-2",
      "cable_length_mm": 200,
      "lifetime": "at least until Jan 2030"
    }
  }
}
