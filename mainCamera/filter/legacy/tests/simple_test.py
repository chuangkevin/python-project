"""
Simple test for preset manager
"""

import sys
from pathlib import Path
import numpy as np

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

try:
    from preset_manager import FilmPresetManager
    print("Import successful")

    # Create manager
    manager = FilmPresetManager()
    print("Manager created")

    # List presets
    presets = manager.list_presets()
    print(f"Found {len(presets)} presets:")

    for preset in presets:
        print(f"  - {preset['name']} ({preset['manufacturer']})")

    # Test categories
    categories = manager.get_categories()
    print(f"Categories: {list(categories.keys())}")

    # Test manufacturers
    manufacturers = manager.get_manufacturers()
    print(f"Manufacturers: {list(manufacturers.keys())}")

    # Test specific preset
    if presets:
        first_preset = presets[0]
        preset_data = manager.get_preset(first_preset['id'])
        print(f"Got preset: {first_preset['name']}")

        # Create processor
        processor = manager.create_processor(first_preset['id'])
        print(f"Created processor: {type(processor).__name__}")

        # Test image processing
        test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        result = processor.process_image(test_img)
        print(f"Processed image: {test_img.shape} -> {result.shape}")

    print("All tests passed!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()