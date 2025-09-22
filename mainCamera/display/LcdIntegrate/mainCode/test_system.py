#!/usr/bin/env python3
"""
RD-1 雙螢幕系統測試腳本
Test Script for RD-1 Dual Screen System

用於測試各個組件是否正常工作
"""

import sys
import time
import numpy as np
from pathlib import Path

# 添加路徑
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_dual_screen_manager():
    """測試雙螢幕管理器"""
    print("🧪 測試雙螢幕管理器...")

    try:
        from dual_screen_manager import start_dual_screen_system, stop_dual_screen_system

        # 啟動系統
        renderer = start_dual_screen_system()
        print("✅ 雙螢幕渲染器啟動成功")

        # 測試主螢幕渲染
        for i in range(10):
            main_image = np.random.randint(0, 255, (320, 240, 3), dtype=np.uint8)
            main_image[100:120, 100:120] = [255, 0, 0]  # 紅色方塊
            renderer.render_main_screen(main_image, {'test_frame': i})

            # 測試圓形螢幕渲染
            gauge_image = np.random.randint(0, 255, (160, 160, 3), dtype=np.uint8)
            gauge_image[70:90, 70:90] = [0, 255, 0]  # 綠色方塊
            renderer.render_gauge_screen(gauge_image, {'gauge_value': i})

            time.sleep(0.1)

        # 獲取效能統計
        stats = renderer.get_performance_stats()
        print(f"   主螢幕佇列: {stats['main_queue_size']}")
        print(f"   圓形螢幕佇列: {stats['gauge_queue_size']}")
        print(f"   丟幀數: {stats['dropped_frames']}")

        stop_dual_screen_system()
        print("✅ 雙螢幕管理器測試完成")
        return True

    except Exception as e:
        print(f"❌ 雙螢幕管理器測試失敗: {e}")
        return False

def test_camera_preview():
    """測試相機預覽優化器"""
    print("\\n🧪 測試相機預覽優化器...")

    try:
        from dual_screen_manager import start_dual_screen_system, stop_dual_screen_system
        from camera_preview_optimizer import CameraPreviewOptimizer, PreviewQuality

        # 啟動渲染器
        renderer = start_dual_screen_system()

        # 啟動相機預覽
        preview = CameraPreviewOptimizer(renderer)
        preview.start_preview()
        print("✅ 相機預覽啟動成功")

        # 測試品質調整
        qualities = [PreviewQuality.LOW, PreviewQuality.MEDIUM, PreviewQuality.HIGH]
        for quality in qualities:
            preview.set_quality(quality)
            print(f"   設置品質: {quality.name}")
            time.sleep(1)

        # 測試零延遲模式
        preview.enable_zero_latency(True)
        print("   啟用零延遲模式")
        time.sleep(1)

        preview.enable_zero_latency(False)
        print("   禁用零延遲模式")

        # 獲取統計
        stats = preview.get_preview_stats()
        print(f"   當前FPS: {stats['fps']:.1f}")
        print(f"   當前品質: {stats['quality']}")

        preview.stop_preview()
        stop_dual_screen_system()
        print("✅ 相機預覽測試完成")
        return True

    except Exception as e:
        print(f"❌ 相機預覽測試失敗: {e}")
        return False

def test_analog_gauge():
    """測試 AnalogGauge 整合"""
    print("\\n🧪 測試 AnalogGauge 整合...")

    try:
        from dual_screen_manager import start_dual_screen_system, stop_dual_screen_system
        from analog_gauge_integration import AnalogGaugeController

        # 啟動渲染器
        renderer = start_dual_screen_system()

        # 啟動錶盤控制器
        gauge = AnalogGaugeController(renderer)
        gauge.start()
        print("✅ AnalogGauge 控制器啟動成功")

        # 測試模式切換
        for i in range(3):
            gauge.cycle_mode()
            time.sleep(0.5)
        print("   模式切換測試完成")

        # 測試數值調整
        for direction in [1, 1, 1, -1, -1]:
            gauge.adjust_value(direction)
            time.sleep(0.3)
        print("   數值調整測試完成")

        # 測試重置
        gauge.reset_to_default()
        print("   重置測試完成")

        # 測試狀態更新
        gauge.update_system_state(battery=3, shots=2)
        print("   狀態更新測試完成")

        # 獲取狀態
        state = gauge.get_current_state()
        print(f"   當前模式: {state['mode']}")
        print(f"   當前數值: {state['value_index']}")

        gauge.stop()
        stop_dual_screen_system()
        print("✅ AnalogGauge 測試完成")
        return True

    except Exception as e:
        print(f"❌ AnalogGauge 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_film_simulation():
    """測試軟片模擬整合"""
    print("\\n🧪 測試軟片模擬整合...")

    try:
        # 添加軟片模擬路徑
        project_root = Path(__file__).parents[4]
        filter_path = project_root / 'mainCamera' / 'filter'
        sys.path.insert(0, str(filter_path))

        from preset_manager import FilmPresetManager

        # 創建管理器
        manager = FilmPresetManager()
        presets = manager.list_presets()
        print(f"✅ 載入 {len(presets)} 個軟片預設")

        # 測試幾個預設
        test_presets = ['PROVIA', 'VELVIA', 'CLASSIC_CHROME']
        for preset_name in test_presets:
            try:
                processor = manager.create_processor(preset_name)
                print(f"   {preset_name}: 處理器創建成功")

                # 測試圖像處理
                test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
                result = processor.process_image(test_image)
                print(f"   {preset_name}: 圖像處理成功 ({result.shape})")

            except Exception as e:
                print(f"   {preset_name}: 測試失敗 - {e}")

        print("✅ 軟片模擬測試完成")
        return True

    except Exception as e:
        print(f"❌ 軟片模擬測試失敗: {e}")
        return False

def test_complete_system():
    """測試完整系統"""
    print("\\n🧪 測試完整 RD-1 系統...")

    try:
        # 添加必要路徑
        project_root = Path(__file__).parents[4]
        analog_gauge_path = project_root / 'analogGauge'
        filter_path = project_root / 'mainCamera' / 'filter'
        sys.path.insert(0, str(analog_gauge_path))
        sys.path.insert(0, str(filter_path))

        from rd1_camera_system import start_rd1_camera, stop_rd1_camera

        # 啟動完整系統
        camera_system = start_rd1_camera()
        print("✅ 完整系統啟動成功")

        # 測試各種功能
        print("   測試拍照功能...")
        filename = camera_system.capture_photo()
        print(f"   拍照成功: {filename}")

        print("   測試軟片模擬切換...")
        for i in range(3):
            camera_system.cycle_film_simulation()
            time.sleep(0.5)

        print("   測試相機模式切換...")
        for i in range(2):
            camera_system.cycle_camera_mode()
            time.sleep(0.5)

        print("   測試曝光補償調整...")
        camera_system.adjust_ev_compensation(1)
        camera_system.adjust_ev_compensation(-2)
        camera_system.adjust_ev_compensation(1)

        # 獲取系統統計
        stats = camera_system.get_system_stats()
        print("   系統統計:")
        print(f"     相機模式: {stats['camera_state']['mode']}")
        print(f"     軟片模擬: {stats['camera_state']['film_simulation']}")
        print(f"     電池電量: {stats['camera_state']['battery_level']}%")

        if 'preview' in stats:
            print(f"     預覽FPS: {stats['preview']['fps']:.1f}")

        # 停止系統
        stop_rd1_camera()
        print("✅ 完整系統測試完成")
        return True

    except Exception as e:
        print(f"❌ 完整系統測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("🧪 RD-1 雙螢幕系統測試")
    print("=" * 50)

    tests = [
        ("雙螢幕管理器", test_dual_screen_manager),
        ("相機預覽優化器", test_camera_preview),
        ("AnalogGauge整合", test_analog_gauge),
        ("軟片模擬整合", test_film_simulation),
        ("完整系統", test_complete_system)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results.append((test_name, success))
        except KeyboardInterrupt:
            print(f"\\n💻 測試被用戶中斷")
            break
        except Exception as e:
            print(f"❌ 測試異常: {e}")
            results.append((test_name, False))

        time.sleep(1)  # 讓系統穩定

    # 總結
    print("\\n" + "=" * 50)
    print("📊 測試總結")
    print("=" * 50)

    passed = 0
    total = len(results)

    for test_name, success in results:
        status = "✅ 通過" if success else "❌ 失敗"
        print(f"{test_name:20s} {status}")
        if success:
            passed += 1

    print(f"\\n總計: {passed}/{total} 個測試通過")

    if passed == total:
        print("🎉 所有測試通過！系統運作正常。")
        return 0
    else:
        print("⚠️ 部分測試失敗，請檢查系統配置。")
        return 1

if __name__ == "__main__":
    sys.exit(main())