#!/usr/bin/env python3
"""
RD-1 雙螢幕系統 Windows 模擬器
Windows Simulator for RD-1 Dual Screen System

在 Windows 環境下模擬雙螢幕顯示，用於開發和測試
"""

import sys
import time
import threading
import queue
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️ OpenCV 不可用，將使用 PIL 模擬器")

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("❌ PIL 不可用，請安裝: pip install pillow")

# 添加路徑
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

class WindowsScreenSimulator:
    """Windows 螢幕模擬器"""

    def __init__(self, screen_name: str, width: int, height: int, window_title: str):
        self.screen_name = screen_name
        self.width = width
        self.height = height
        self.window_title = window_title
        self.running = False
        self.display_thread = None
        self.frame_queue = queue.Queue(maxsize=5)
        self.stats = {
            'frames_rendered': 0,
            'fps': 0.0,
            'last_fps_time': time.time()
        }

    def start(self):
        """啟動模擬器"""
        if not CV2_AVAILABLE:
            print(f"{self.screen_name} simulator startup failed: OpenCV not available")
            return False

        self.running = True
        self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
        self.display_thread.start()
        print(f"{self.screen_name} simulator started successfully")
        return True

    def stop(self):
        """停止模擬器"""
        self.running = False
        if self.display_thread:
            self.display_thread.join(timeout=1)
        cv2.destroyAllWindows()
        print(f"{self.screen_name} simulator stopped")

    def display_frame(self, frame: np.ndarray, metadata: Optional[Dict] = None):
        """顯示幀到模擬螢幕"""
        if not self.running:
            return

        try:
            # 確保幀格式正確
            if frame.dtype != np.uint8:
                frame = (frame * 255).astype(np.uint8)

            if len(frame.shape) == 3 and frame.shape[2] == 3:
                # BGR -> RGB for display
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # 調整大小到螢幕尺寸
            if frame.shape[:2] != (self.height, self.width):
                frame = cv2.resize(frame, (self.width, self.height))

            # 添加元數據顯示
            if metadata:
                frame = self._add_metadata_overlay(frame, metadata)

            # 發送到顯示佇列
            if not self.frame_queue.full():
                self.frame_queue.put(frame.copy())

        except Exception as e:
            print(f"{self.screen_name} frame processing error: {e}")

    def _add_metadata_overlay(self, frame: np.ndarray, metadata: Dict) -> np.ndarray:
        """添加元數據覆蓋層"""
        overlay = frame.copy()

        # 添加半透明背景
        cv2.rectangle(overlay, (5, 5), (200, 60), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        # 添加文字信息
        y_offset = 20
        for key, value in metadata.items():
            text = f"{key}: {value}"
            cv2.putText(frame, text, (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
            y_offset += 15

        return frame

    def _display_loop(self):
        """顯示循環"""
        fps_counter = 0
        fps_start_time = time.time()

        while self.running:
            try:
                # 獲取幀
                frame = self.frame_queue.get(timeout=0.1)

                # 顯示幀
                cv2.imshow(self.window_title, frame)

                # 更新統計
                fps_counter += 1
                current_time = time.time()
                if current_time - fps_start_time >= 1.0:
                    self.stats['fps'] = fps_counter / (current_time - fps_start_time)
                    fps_counter = 0
                    fps_start_time = current_time

                self.stats['frames_rendered'] += 1

                # 檢查窗口事件
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print(f"{self.screen_name} user requested exit")
                    break

            except queue.Empty:
                # 顯示空白幀
                blank_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
                cv2.putText(blank_frame, f"{self.screen_name} - Waiting...",
                           (10, self.height//2), cv2.FONT_HERSHEY_SIMPLEX,
                           0.7, (128, 128, 128), 2)
                cv2.imshow(self.window_title, blank_frame)
                cv2.waitKey(30)

            except Exception as e:
                print(f"{self.screen_name} display error: {e}")
                break

class DualScreenSimulator:
    """雙螢幕模擬器管理器"""

    def __init__(self):
        # 主螢幕模擬器 (2.4吋 240x320)
        self.main_screen = WindowsScreenSimulator(
            "主螢幕", 480, 640, "RD-1 主螢幕 (2.4吋 240x320)"
        )

        # 圓形螢幕模擬器 (0.71吋 160x160)
        self.gauge_screen = WindowsScreenSimulator(
            "圓形螢幕", 320, 320, "RD-1 圓形螢幕 (0.71吋 160x160)"
        )

        self.running = False

    def start(self):
        """啟動雙螢幕模擬器"""
        print("Starting RD-1 Dual Screen Windows Simulator...")

        if not CV2_AVAILABLE:
            print("Cannot start simulator: Please install OpenCV")
            print("   pip install opencv-python")
            return False

        main_ok = self.main_screen.start()
        gauge_ok = self.gauge_screen.start()

        if main_ok and gauge_ok:
            self.running = True
            print("Dual screen simulator started successfully!")
            print("\nControls:")
            print("  - Press 'q' in any window to exit")
            print("  - Windows can be dragged and repositioned")
            print("  - Main screen shows camera preview")
            print("  - Gauge screen shows AnalogGauge display")
            return True
        else:
            print("Simulator startup failed")
            self.stop()
            return False

    def stop(self):
        """停止模擬器"""
        print("Stopping dual screen simulator...")
        self.running = False
        self.main_screen.stop()
        self.gauge_screen.stop()
        print("Simulator stopped")

    def render_main_screen(self, image: np.ndarray, metadata: Optional[Dict] = None):
        """渲染主螢幕"""
        if self.running:
            self.main_screen.display_frame(image, metadata)

    def render_gauge_screen(self, image: np.ndarray, metadata: Optional[Dict] = None):
        """渲染圓形螢幕"""
        if self.running:
            self.gauge_screen.display_frame(image, metadata)

    def get_performance_stats(self) -> Dict[str, Any]:
        """獲取效能統計"""
        return {
            'main_screen': {
                'fps': self.main_screen.stats['fps'],
                'frames_rendered': self.main_screen.stats['frames_rendered']
            },
            'gauge_screen': {
                'fps': self.gauge_screen.stats['fps'],
                'frames_rendered': self.gauge_screen.stats['frames_rendered']
            },
            'simulator_running': self.running
        }

# 全域模擬器實例
_simulator_instance = None

def start_windows_simulator():
    """啟動 Windows 模擬器"""
    global _simulator_instance

    if _simulator_instance is not None:
        print("Simulator already running")
        return _simulator_instance

    _simulator_instance = DualScreenSimulator()

    if _simulator_instance.start():
        return _simulator_instance
    else:
        _simulator_instance = None
        return None

def stop_windows_simulator():
    """停止 Windows 模擬器"""
    global _simulator_instance

    if _simulator_instance is not None:
        _simulator_instance.stop()
        _simulator_instance = None

def get_simulator():
    """獲取當前模擬器實例"""
    return _simulator_instance

# 修改原始的 dual_screen_manager 以支援模擬器
def patch_dual_screen_manager():
    """修補雙螢幕管理器以支援 Windows 模擬器"""
    try:
        import dual_screen_manager

        # 保存原始函數
        original_start = dual_screen_manager.start_dual_screen_system
        original_stop = dual_screen_manager.stop_dual_screen_system

        def start_with_simulator():
            """啟動帶模擬器的雙螢幕系統"""
            print("Detected Windows environment, starting simulator mode...")
            return start_windows_simulator()

        def stop_with_simulator():
            """停止帶模擬器的雙螢幕系統"""
            stop_windows_simulator()

        # 替換函數
        dual_screen_manager.start_dual_screen_system = start_with_simulator
        dual_screen_manager.stop_dual_screen_system = stop_with_simulator

        print("Dual screen manager patched for simulator mode")
        return True

    except ImportError:
        print("Cannot patch dual_screen_manager, file may not exist")
        return False

def demo_simulator():
    """模擬器演示"""
    print("RD-1 Dual Screen Windows Simulator Demo")
    print("=" * 50)

    # 啟動模擬器
    simulator = start_windows_simulator()
    if not simulator:
        return

    try:
        print("Starting simulation demo...")

        for i in range(100):
            # 生成主螢幕內容 (相機預覽模擬) - 更像真實相機畫面
            main_frame = np.zeros((240, 320, 3), dtype=np.uint8)

            # 背景漸層 (模擬天空)
            for y in range(240):
                intensity = int(180 - y * 0.5)  # 從上到下變暗
                main_frame[y, :] = [intensity, intensity + 20, intensity + 40]

            # 添加動態元素 (模擬移動物體)
            center_x = 160 + int(80 * np.sin(i * 0.05))
            center_y = 120 + int(40 * np.cos(i * 0.03))

            # 主體物件 (圓形，模擬人或物體)
            cv2.circle(main_frame, (center_x, center_y), 25, (50, 150, 200), -1)
            cv2.circle(main_frame, (center_x, center_y), 25, (255, 255, 255), 2)

            # 地平線
            cv2.line(main_frame, (0, 180), (320, 180), (100, 100, 100), 2)

            # 相機UI元素
            cv2.rectangle(main_frame, (10, 10), (100, 40), (0, 0, 0), -1)
            cv2.putText(main_frame, "RD-1 CAM", (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

            main_metadata = {
                'Frame': i,
                'Mode': 'AUTO',
                'Film': 'PROVIA',
                'EV': '+0.3'
            }

            # 生成圓形螢幕內容 (錶盤模擬) - 更精美的錶盤
            gauge_frame = np.zeros((160, 160, 3), dtype=np.uint8)

            # 漸層背景
            center = (80, 80)
            for r in range(80, 0, -1):
                intensity = int(r * 2)
                color = (intensity//4, intensity//4, intensity//3)
                cv2.circle(gauge_frame, center, r, color, -1)

            # 刻度線
            for tick in range(0, 360, 30):
                tick_start_x = 80 + int(65 * np.cos(np.radians(tick - 90)))
                tick_start_y = 80 + int(65 * np.sin(np.radians(tick - 90)))
                tick_end_x = 80 + int(70 * np.cos(np.radians(tick - 90)))
                tick_end_y = 80 + int(70 * np.sin(np.radians(tick - 90)))
                cv2.line(gauge_frame, (tick_start_x, tick_start_y), (tick_end_x, tick_end_y), (255, 255, 255), 2)

            # 主指針 (EV值模擬)
            ev_angle = (i * 2) % 360
            needle_x = 80 + int(50 * np.cos(np.radians(ev_angle - 90)))
            needle_y = 80 + int(50 * np.sin(np.radians(ev_angle - 90)))
            cv2.line(gauge_frame, (80, 80), (needle_x, needle_y), (0, 255, 100), 3)

            # 中心點
            cv2.circle(gauge_frame, (80, 80), 5, (255, 255, 255), -1)

            # 錶盤文字
            cv2.putText(gauge_frame, "EV", (70, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

            gauge_metadata = {
                'EV': f"{(i % 13) - 6:+.1f}",
                'Battery': f"{100 - (i % 100)}%"
            }

            # 渲染到模擬器
            simulator.render_main_screen(main_frame, main_metadata)
            simulator.render_gauge_screen(gauge_frame, gauge_metadata)

            time.sleep(0.033)  # ~30 FPS

            # 每10幀顯示統計
            if i % 10 == 0:
                stats = simulator.get_performance_stats()
                print(f"\rMain: {stats['main_screen']['fps']:.1f}fps | "
                      f"Gauge: {stats['gauge_screen']['fps']:.1f}fps | "
                      f"Frame: {i}", end="", flush=True)

        print(f"\nDemo completed!")

    except KeyboardInterrupt:
        print("\nUser interrupted demo")

    finally:
        stop_windows_simulator()

if __name__ == "__main__":
    # 修補雙螢幕管理器
    patch_dual_screen_manager()

    # 運行演示
    demo_simulator()