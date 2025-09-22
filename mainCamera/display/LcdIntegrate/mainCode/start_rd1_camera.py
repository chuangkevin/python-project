#!/usr/bin/env python3
"""
RD-1 相機系統快速啟動腳本
Quick Start Script for RD-1 Camera System

這是最簡單的啟動方式，一鍵啟動完整的雙螢幕相機系統
"""

import sys
import time
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

def main():
    """主函數"""
    print("🎬 RD-1 雙螢幕相機系統")
    print("=" * 50)
    print("正在啟動系統組件...")

    try:
        # 導入主系統
        from rd1_camera_system import start_rd1_camera, stop_rd1_camera

        # 啟動系統
        print("🚀 啟動 RD-1 相機系統...")
        camera_system = start_rd1_camera()

        print("\n✅ 系統啟動完成！")
        print("\n🎮 控制說明:")
        print("  Enter - 拍照")
        print("  f - 切換軟片模擬 (PROVIA→VELVIA→ASTIA...)")
        print("  m - 切換相機模式 (auto→manual→aperture_priority...)")
        print("  + - 增加曝光補償 (+0.3 EV)")
        print("  - - 減少曝光補償 (-0.3 EV)")
        print("  s - 顯示系統統計")
        print("  q - 退出系統")
        print("\n" + "=" * 50)

        # 主控制循環
        while True:
            try:
                user_input = input("\nRD-1> ").strip().lower()

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
                    print("\n📊 系統統計:")
                    stats = camera_system.get_system_stats()

                    print(f"  相機狀態:")
                    print(f"    模式: {stats['camera_state']['mode']}")
                    print(f"    軟片: {stats['camera_state']['film_simulation']}")
                    print(f"    曝光補償: {stats['camera_state']['ev_compensation']:+.1f} EV")
                    print(f"    電池: {stats['camera_state']['battery_level']}%")
                    print(f"    剩餘拍攝: {stats['camera_state']['shots_remaining']}")

                    if 'preview' in stats:
                        print(f"  預覽效能:")
                        print(f"    FPS: {stats['preview']['fps']:.1f}")
                        print(f"    品質: {stats['preview']['quality']}")
                        print(f"    零延遲模式: {stats['preview']['zero_latency']}")

                    if 'renderer' in stats:
                        print(f"  渲染器效能:")
                        print(f"    主螢幕佇列: {stats['renderer']['main_queue_size']}")
                        print(f"    圓形螢幕佇列: {stats['renderer']['gauge_queue_size']}")
                        print(f"    丟幀數: {stats['renderer']['dropped_frames']}")

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

                else:
                    print(f"❓ 未知命令: '{user_input}'")
                    print("   輸入 'help' 查看所有可用命令")

            except KeyboardInterrupt:
                print("\n\n💻 偵測到 Ctrl+C，正在退出...")
                break
            except EOFError:
                print("\n\n📝 輸入結束，正在退出...")
                break

    except ImportError as e:
        print(f"❌ 模組載入失敗: {e}")
        print("\n🔧 請檢查:")
        print("  1. 是否已安裝所有依賴: pip install opencv-python pillow numpy PyQt5")
        print("  2. 檔案路徑是否正確")
        print("  3. analogGauge 和 filter 模組是否存在")
        return 1

    except Exception as e:
        print(f"❌ 系統啟動失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        print("\n⏹️ 正在停止系統...")
        try:
            stop_rd1_camera()
        except:
            pass
        print("👋 再見！")

    return 0

if __name__ == "__main__":
    sys.exit(main())