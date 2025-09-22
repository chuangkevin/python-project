#!/usr/bin/env python3
"""
RD-1 相機系統 Windows 模擬器啟動器
Windows Simulator Launcher for RD-1 Camera System

在沒有實體螢幕的 Windows 環境下測試整個相機系統
"""

import sys
import time
import os
from pathlib import Path

# 添加必要的路徑
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# 添加其他必要模組路徑
project_root = current_dir.parents[3]
analog_gauge_path = project_root / 'analogGauge'
filter_path = project_root / 'mainCamera' / 'filter'

sys.path.insert(0, str(analog_gauge_path))
sys.path.insert(0, str(filter_path))

def check_dependencies():
    """檢查依賴"""
    missing_deps = []

    try:
        import cv2
    except ImportError:
        missing_deps.append("opencv-python")

    try:
        import numpy
    except ImportError:
        missing_deps.append("numpy")

    try:
        from PIL import Image
    except ImportError:
        missing_deps.append("pillow")

    if missing_deps:
        print("❌ 缺少依賴:")
        for dep in missing_deps:
            print(f"   {dep}")
        print(f"\n請安裝: pip install {' '.join(missing_deps)}")
        return False

    return True

def start_simulator_only():
    """只啟動模擬器演示"""
    print("RD-1 Dual Screen Windows Simulator")
    print("=" * 50)
    print("Starting simulator demo...")

    try:
        from windows_simulator import demo_simulator
        demo_simulator()

    except ImportError as e:
        print(f"Module loading failed: {e}")
        return False

    except Exception as e:
        print(f"Simulator startup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

def start_full_system_with_simulator():
    """啟動完整系統 + 模擬器"""
    print("RD-1 Full Camera System + Windows Simulator")
    print("=" * 50)
    print("Starting full system...")

    try:
        # 先修補雙螢幕管理器以支援模擬器
        from windows_simulator import patch_dual_screen_manager
        patch_result = patch_dual_screen_manager()

        if not patch_result:
            print("⚠️ 無法修補螢幕管理器，嘗試純模擬器模式")
            return start_simulator_only()

        # 導入主系統
        from rd1_camera_system import start_rd1_camera, stop_rd1_camera

        # 啟動系統
        print("🚀 啟動 RD-1 相機系統 (模擬器模式)...")
        camera_system = start_rd1_camera()

        if camera_system is None:
            print("❌ 相機系統啟動失敗")
            return False

        print("\n✅ 系統啟動完成！")
        print("\n🖥️ Windows 模擬器視窗已開啟")
        print("   - 主螢幕窗口: 顯示相機預覽")
        print("   - 圓形螢幕窗口: 顯示 AnalogGauge 錶盤")
        print("\n🎮 控制說明:")
        print("  Enter - 拍照")
        print("  f - 切換軟片模擬")
        print("  m - 切換相機模式")
        print("  + - 增加曝光補償")
        print("  - - 減少曝光補償")
        print("  s - 顯示系統統計")
        print("  q - 退出系統")
        print("  ⚠️ 在模擬器窗口按 'q' 也可以退出")
        print("\n" + "=" * 50)

        # 主控制循環
        try:
            while True:
                try:
                    user_input = input("\nRD-1-Simulator> ").strip().lower()

                    if user_input == 'q' or user_input == 'quit':
                        break
                    elif user_input == '' or user_input == 'capture':
                        print("📷 拍攝照片...")
                        filename = camera_system.capture_photo()
                        print(f"✅ 照片已保存: {filename}")

                    elif user_input == 'f' or user_input == 'film':
                        camera_system.cycle_film_simulation()

                    elif user_input == 'm' or user_input == 'mode':
                        camera_system.cycle_camera_mode()

                    elif user_input == '+' or user_input == 'ev+':
                        camera_system.adjust_ev_compensation(1)

                    elif user_input == '-' or user_input == 'ev-':
                        camera_system.adjust_ev_compensation(-1)

                    elif user_input == 's' or user_input == 'stats':
                        print("\n📊 系統統計 (模擬器模式):")
                        stats = camera_system.get_system_stats()

                        print(f"  相機狀態:")
                        print(f"    模式: {stats.get('camera_state', {}).get('mode', 'N/A')}")
                        print(f"    軟片: {stats.get('camera_state', {}).get('film_simulation', 'N/A')}")
                        print(f"    曝光補償: {stats.get('camera_state', {}).get('ev_compensation', 0):+.1f} EV")
                        print(f"    電池: {stats.get('camera_state', {}).get('battery_level', 100)}%")

                        if 'preview' in stats:
                            print(f"  預覽效能:")
                            print(f"    FPS: {stats['preview']['fps']:.1f}")

                        # 顯示模擬器統計
                        from windows_simulator import get_simulator
                        simulator = get_simulator()
                        if simulator:
                            sim_stats = simulator.get_performance_stats()
                            print(f"  模擬器效能:")
                            print(f"    主螢幕FPS: {sim_stats['main_screen']['fps']:.1f}")
                            print(f"    圓形螢幕FPS: {sim_stats['gauge_screen']['fps']:.1f}")
                            print(f"    模擬器運行: {sim_stats['simulator_running']}")

                    elif user_input == 'help' or user_input == 'h':
                        print("\n🎮 所有可用命令:")
                        print("  capture, Enter - 拍攝照片")
                        print("  f, film - 切換軟片模擬")
                        print("  m, mode - 切換相機模式")
                        print("  +, ev+ - 增加曝光補償")
                        print("  -, ev- - 減少曝光補償")
                        print("  s, stats - 顯示系統統計")
                        print("  h, help - 顯示幫助")
                        print("  q, quit - 退出系統")
                        print("  💡 提示: 也可以在模擬器窗口按 'q' 退出")

                    else:
                        print(f"❓ 未知命令: '{user_input}'")
                        print("   輸入 'help' 查看所有可用命令")

                except KeyboardInterrupt:
                    print("\n\n💻 偵測到 Ctrl+C，正在退出...")
                    break
                except EOFError:
                    print("\n\n📝 輸入結束，正在退出...")
                    break

        finally:
            print("\n⏹️ 正在停止系統...")
            try:
                stop_rd1_camera()
            except:
                pass

    except ImportError as e:
        print(f"❌ 模組載入失敗: {e}")
        print("\n🔧 建議:")
        print("  1. 確認所有檔案都存在")
        print("  2. 或者嘗試純模擬器演示: python windows_simulator.py")
        return False

    except Exception as e:
        print(f"❌ 系統啟動失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

def main():
    """主函數"""
    print("RD-1 Windows Simulator Selection")
    print("=" * 50)

    # 檢查依賴
    if not check_dependencies():
        return 1

    print("\nSelect Mode:")
    print("  1. Full System + Simulator (Recommended)")
    print("  2. Pure Simulator Demo")
    print("  3. Exit")

    while True:
        try:
            choice = input("\nPlease select (1-3): ").strip()

            if choice == '1':
                success = start_full_system_with_simulator()
                break
            elif choice == '2':
                success = start_simulator_only()
                break
            elif choice == '3':
                print("Goodbye!")
                return 0
            else:
                print("Please enter 1, 2 or 3")

        except KeyboardInterrupt:
            print("\nUser cancelled")
            return 0

    print("\nSimulator finished!")
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())