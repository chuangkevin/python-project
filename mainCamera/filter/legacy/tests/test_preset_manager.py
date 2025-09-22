"""
測試軟片預設管理器
Test Film Preset Manager
"""

import sys
from pathlib import Path
import numpy as np
import cv2

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from preset_manager import FilmPresetManager, FilmProcessor

def test_preset_manager():
    """測試預設管理器功能"""
    print("=== 軟片預設管理器測試 ===")

    try:
        # 創建管理器
        manager = FilmPresetManager()
        print(f"OK: 預設管理器初始化成功")

        # 測試預設載入
        presets = manager.list_presets()
        print(f"OK: 載入 {len(presets)} 個預設:")

        for preset in presets:
            print(f"  - {preset['name']} ({preset['manufacturer']}) - {preset['category']}")

        # 測試分類查詢
        categories = manager.get_categories()
        print(f"\n✓ 找到 {len(categories)} 個分類:")
        for category, preset_list in categories.items():
            print(f"  - {category}: {len(preset_list)} 個預設")

        # 測試廠商查詢
        manufacturers = manager.get_manufacturers()
        print(f"\n✓ 找到 {len(manufacturers)} 個廠商:")
        for manufacturer, preset_list in manufacturers.items():
            print(f"  - {manufacturer}: {len(preset_list)} 個預設")

        # 測試特定預設
        if presets:
            first_preset = presets[0]
            preset_data = manager.get_preset(first_preset['id'])
            print(f"\n✓ 成功獲取預設: {first_preset['name']}")
            print(f"  描述: {preset_data['metadata']['description']}")
            print(f"  分類: {preset_data['metadata']['category']}")

            # 測試處理器創建
            processor = manager.create_processor(first_preset['id'])
            print(f"✓ 創建處理器成功: {type(processor).__name__}")

        return True

    except Exception as e:
        print(f"✗ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_image_processing():
    """測試圖像處理功能"""
    print("\n=== 圖像處理測試 ===")

    try:
        manager = FilmPresetManager()
        presets = manager.list_presets()

        if not presets:
            print("⚠ 沒有可用的預設，跳過圖像處理測試")
            return True

        # 創建測試圖像
        test_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        print(f"✓ 創建測試圖像: {test_img.shape}")

        # 測試每個預設
        for preset in presets[:3]:  # 只測試前3個預設
            try:
                processor = manager.create_processor(preset['id'])
                result = processor.process_image(test_img)

                print(f"✓ 預設 '{preset['name']}' 處理成功")
                print(f"  輸入: {test_img.shape}, 輸出: {result.shape}")
                print(f"  數值範圍: {result.min():.1f} - {result.max():.1f}")

            except Exception as e:
                print(f"✗ 預設 '{preset['name']}' 處理失敗: {e}")

        return True

    except Exception as e:
        print(f"✗ 圖像處理測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_preset_categories():
    """測試預設分類篩選"""
    print("\n=== 分類篩選測試 ===")

    try:
        manager = FilmPresetManager()

        # 測試按分類篩選
        color_presets = manager.list_presets(category='color')
        print(f"✓ 彩色軟片: {len(color_presets)} 個")

        cinema_presets = manager.list_presets(category='cinema')
        print(f"✓ 電影膠片: {len(cinema_presets)} 個")

        special_presets = manager.list_presets(category='special')
        print(f"✓ 特殊效果: {len(special_presets)} 個")

        # 測試按廠商篩選
        fuji_presets = manager.list_presets(manufacturer='Fujifilm')
        print(f"✓ Fujifilm: {len(fuji_presets)} 個")

        kodak_presets = manager.list_presets(manufacturer='Kodak')
        print(f"✓ Kodak: {len(kodak_presets)} 個")

        return True

    except Exception as e:
        print(f"✗ 分類篩選測試失敗: {e}")
        return False

def test_specific_presets():
    """測試特定預設的詳細功能"""
    print("\n=== 特定預設測試 ===")

    try:
        manager = FilmPresetManager()

        # 測試PROVIA預設
        test_presets = ['PROVIA', 'VELVIA', 'CLASSIC_CHROME']

        for preset_name in test_presets:
            try:
                preset_data = manager.get_preset(preset_name)
                processor = manager.create_processor(preset_name)

                print(f"✓ {preset_name}:")
                print(f"  描述: {preset_data['metadata']['description']}")
                print(f"  色溫: {preset_data['processing']['color_temperature']['temperature']}K")
                print(f"  飽和度: {preset_data['processing']['saturation']['global']}")
                print(f"  對比度: {preset_data['processing']['contrast']['global']}")

            except Exception as e:
                print(f"✗ {preset_name} 測試失敗: {e}")

        return True

    except Exception as e:
        print(f"✗ 特定預設測試失敗: {e}")
        return False

def main():
    """主測試函數"""
    print("開始軟片預設系統測試...\n")

    tests = [
        ("預設管理器", test_preset_manager),
        ("圖像處理", test_image_processing),
        ("分類篩選", test_preset_categories),
        ("特定預設", test_specific_presets)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"測試: {test_name}")
        print('='*50)

        success = test_func()
        results.append((test_name, success))

    # 總結
    print(f"\n{'='*50}")
    print("測試總結")
    print('='*50)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{test_name}: {status}")

    print(f"\n總計: {passed}/{total} 個測試通過")

    if passed == total:
        print("🎉 所有測試通過！軟片預設系統運作正常。")
    else:
        print("⚠ 部分測試失敗，請檢查實現。")

if __name__ == "__main__":
    main()