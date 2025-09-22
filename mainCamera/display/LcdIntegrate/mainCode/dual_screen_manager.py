#!/usr/bin/env python3
"""
雙螢幕高效能管理系統
Dual Screen High-Performance Manager

設計理念：
- 主螢幕：專注相機預覽，高幀率 (30fps)
- 圓形螢幕：顯示 analogGauge，低更新率 (10fps)
- 獨立線程：避免互相干擾
- 雙緩衝：防止畫面撕裂
- 優先級管理：相機預覽優先

硬體配置：
- 主螢幕 (2.4吋 ILI9341): SPI0.0, CS=GPIO8
- 圓形螢幕 (0.71吋 GC9D01): SPI0.1, CS=GPIO7
"""

import threading
import time
import queue
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np
from PIL import Image

# 導入顯示驅動
try:
    # 添加項目根路徑
    import sys
    import importlib.util
    from pathlib import Path

    project_root = Path(__file__).parents[4]
    sys.path.insert(0, str(project_root))

    from mainCamera.display.LcdIntegrate.testCode.DualLcdTestSuccess import MainDisplay_ILI9341

    # 動態導入 rd1_gauge_v1 以避免 071version 目錄名稱的語法錯誤
    gauge_module_path = project_root / 'analogGauge' / '071version' / 'rd1_gauge_v1.py'
    spec = importlib.util.spec_from_file_location("rd1_gauge_v1", gauge_module_path)
    gauge_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gauge_module)
    Official_GC9D01 = gauge_module.Official_GC9D01

    HARDWARE_AVAILABLE = True
    print("Hardware drivers loaded successfully")
except ImportError as e:
    print(f"Hardware drivers not found, using simulation mode: {e}")
    HARDWARE_AVAILABLE = False
except Exception as e:
    print(f"Hardware driver loading failed, using simulation mode: {e}")
    HARDWARE_AVAILABLE = False

class ScreenPriority(Enum):
    """螢幕優先級"""
    CRITICAL = 1    # 相機預覽
    NORMAL = 2      # analogGauge
    LOW = 3         # 其他UI元素

@dataclass
class FrameData:
    """幀資料結構"""
    image: np.ndarray
    timestamp: float
    priority: ScreenPriority
    metadata: Dict[str, Any] = None

class DoubleBuffer:
    """雙緩衝區管理"""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.front_buffer = np.zeros((height, width, 3), dtype=np.uint8)
        self.back_buffer = np.zeros((height, width, 3), dtype=np.uint8)
        self.lock = threading.Lock()

    def swap_buffers(self):
        """交換緩衝區"""
        with self.lock:
            self.front_buffer, self.back_buffer = self.back_buffer, self.front_buffer

    def get_back_buffer(self) -> np.ndarray:
        """獲取後緩衝區用於繪製"""
        return self.back_buffer

    def get_front_buffer(self) -> np.ndarray:
        """獲取前緩衝區用於顯示"""
        with self.lock:
            return self.front_buffer.copy()

class HighPerformanceRenderer:
    """高效能渲染器"""

    def __init__(self):
        self.running = False
        self.threads = {}
        self.frame_queues = {}

        # 初始化硬體
        if HARDWARE_AVAILABLE:
            self.main_display = MainDisplay_ILI9341()
            self.gauge_display = Official_GC9D01()
        else:
            self.main_display = None
            self.gauge_display = None

        # 初始化緩衝區
        self.main_buffer = DoubleBuffer(240, 320)  # 主螢幕
        self.gauge_buffer = DoubleBuffer(160, 160)  # 圓形螢幕

        # 幀率控制
        self.main_fps = 30      # 主螢幕 30fps
        self.gauge_fps = 10     # 圓形螢幕 10fps

        # 統計資料
        self.stats = {
            'main_frames': 0,
            'gauge_frames': 0,
            'dropped_frames': 0,
            'last_stats_time': time.time()
        }

    def start(self):
        """啟動雙螢幕渲染系統"""
        if self.running:
            return

        self.running = True

        # 創建幀佇列
        self.frame_queues['main'] = queue.Queue(maxsize=3)    # 主螢幕佇列較小，保持即時性
        self.frame_queues['gauge'] = queue.Queue(maxsize=5)   # 圓形螢幕佇列較大，允許緩衝

        # 啟動渲染線程
        self.threads['main'] = threading.Thread(
            target=self._main_screen_thread,
            name="MainScreenRenderer",
            daemon=True
        )

        self.threads['gauge'] = threading.Thread(
            target=self._gauge_screen_thread,
            name="GaugeScreenRenderer",
            daemon=True
        )

        self.threads['stats'] = threading.Thread(
            target=self._stats_thread,
            name="StatsMonitor",
            daemon=True
        )

        # 設定線程優先級
        self.threads['main'].start()
        self.threads['gauge'].start()
        self.threads['stats'].start()

        print("🚀 雙螢幕渲染系統已啟動")
        print(f"   主螢幕: {self.main_fps}fps")
        print(f"   圓形螢幕: {self.gauge_fps}fps")

    def stop(self):
        """停止渲染系統"""
        self.running = False

        # 等待線程結束
        for thread in self.threads.values():
            if thread.is_alive():
                thread.join(timeout=1.0)

        print("⏹️ 雙螢幕渲染系統已停止")

    def render_main_screen(self, image: np.ndarray, metadata: Dict[str, Any] = None):
        """提交主螢幕幀"""
        frame = FrameData(
            image=image,
            timestamp=time.time(),
            priority=ScreenPriority.CRITICAL,
            metadata=metadata
        )

        try:
            self.frame_queues['main'].put_nowait(frame)
        except queue.Full:
            # 主螢幕佇列滿了，丟棄最舊的幀
            try:
                self.frame_queues['main'].get_nowait()
                self.frame_queues['main'].put_nowait(frame)
                self.stats['dropped_frames'] += 1
            except queue.Empty:
                pass

    def render_gauge_screen(self, image: np.ndarray, metadata: Dict[str, Any] = None):
        """提交圓形螢幕幀"""
        frame = FrameData(
            image=image,
            timestamp=time.time(),
            priority=ScreenPriority.NORMAL,
            metadata=metadata
        )

        try:
            self.frame_queues['gauge'].put_nowait(frame)
        except queue.Full:
            # 圓形螢幕更新不那麼頻繁，可以跳過這幀
            self.stats['dropped_frames'] += 1

    def _main_screen_thread(self):
        """主螢幕渲染線程 - 高優先級"""
        frame_time = 1.0 / self.main_fps
        last_render = time.time()

        while self.running:
            try:
                # 獲取下一幀
                frame = self.frame_queues['main'].get(timeout=0.1)

                # 渲染到後緩衝區
                back_buffer = self.main_buffer.get_back_buffer()
                self._render_main_frame(frame.image, back_buffer)

                # 交換緩衝區
                self.main_buffer.swap_buffers()

                # 發送到硬體顯示
                if self.main_display:
                    front_buffer = self.main_buffer.get_front_buffer()
                    self._display_main_hardware(front_buffer)

                self.stats['main_frames'] += 1

                # 控制幀率
                elapsed = time.time() - last_render
                if elapsed < frame_time:
                    time.sleep(frame_time - elapsed)
                last_render = time.time()

            except queue.Empty:
                # 沒有新幀，短暫休眠
                time.sleep(0.001)
            except Exception as e:
                print(f"❌ 主螢幕渲染錯誤: {e}")

    def _gauge_screen_thread(self):
        """圓形螢幕渲染線程 - 正常優先級"""
        frame_time = 1.0 / self.gauge_fps
        last_render = time.time()

        while self.running:
            try:
                # 獲取下一幀
                frame = self.frame_queues['gauge'].get(timeout=0.1)

                # 渲染到後緩衝區
                back_buffer = self.gauge_buffer.get_back_buffer()
                self._render_gauge_frame(frame.image, back_buffer)

                # 交換緩衝區
                self.gauge_buffer.swap_buffers()

                # 發送到硬體顯示
                if self.gauge_display:
                    front_buffer = self.gauge_buffer.get_front_buffer()
                    self._display_gauge_hardware(front_buffer)

                self.stats['gauge_frames'] += 1

                # 控制幀率
                elapsed = time.time() - last_render
                if elapsed < frame_time:
                    time.sleep(frame_time - elapsed)
                last_render = time.time()

            except queue.Empty:
                # 沒有新幀，較長休眠
                time.sleep(0.01)
            except Exception as e:
                print(f"❌ 圓形螢幕渲染錯誤: {e}")

    def _stats_thread(self):
        """統計監控線程"""
        while self.running:
            time.sleep(5.0)  # 每5秒報告一次

            current_time = time.time()
            elapsed = current_time - self.stats['last_stats_time']

            main_fps = self.stats['main_frames'] / elapsed
            gauge_fps = self.stats['gauge_frames'] / elapsed

            print(f"📊 渲染統計:")
            print(f"   主螢幕: {main_fps:.1f}fps")
            print(f"   圓形螢幕: {gauge_fps:.1f}fps")
            print(f"   丟幀: {self.stats['dropped_frames']}")

            # 重置統計
            self.stats['main_frames'] = 0
            self.stats['gauge_frames'] = 0
            self.stats['dropped_frames'] = 0
            self.stats['last_stats_time'] = current_time

    def _render_main_frame(self, source: np.ndarray, target: np.ndarray):
        """渲染主螢幕幀"""
        # 快速縮放和色彩轉換
        if source.shape[:2] != target.shape[:2]:
            # 使用 PIL 快速縮放
            pil_image = Image.fromarray(source)
            pil_image = pil_image.resize((target.shape[1], target.shape[0]), Image.Resampling.LANCZOS)
            target[:] = np.array(pil_image)
        else:
            target[:] = source

    def _render_gauge_frame(self, source: np.ndarray, target: np.ndarray):
        """渲染圓形螢幕幀"""
        # 圓形遮罩處理
        if source.shape[:2] != target.shape[:2]:
            pil_image = Image.fromarray(source)
            pil_image = pil_image.resize((target.shape[1], target.shape[0]), Image.Resampling.LANCZOS)
            target[:] = np.array(pil_image)
        else:
            target[:] = source

    def _display_main_hardware(self, buffer: np.ndarray):
        """發送主螢幕資料到硬體"""
        try:
            # 轉換為 PIL Image
            pil_image = Image.fromarray(buffer)

            # 發送到硬體顯示
            if hasattr(self.main_display, 'display_image'):
                self.main_display.display_image(pil_image)
            else:
                # 備用顯示方法
                pass

        except Exception as e:
            print(f"❌ 主螢幕硬體顯示錯誤: {e}")

    def _display_gauge_hardware(self, buffer: np.ndarray):
        """發送圓形螢幕資料到硬體"""
        try:
            # 轉換為 PIL Image
            pil_image = Image.fromarray(buffer)

            # 發送到硬體顯示
            if hasattr(self.gauge_display, 'display_image'):
                self.gauge_display.display_image(pil_image)
            else:
                # 備用顯示方法
                pass

        except Exception as e:
            print(f"❌ 圓形螢幕硬體顯示錯誤: {e}")

    def get_performance_stats(self) -> Dict[str, float]:
        """獲取效能統計"""
        return {
            'main_queue_size': self.frame_queues['main'].qsize(),
            'gauge_queue_size': self.frame_queues['gauge'].qsize(),
            'dropped_frames': self.stats['dropped_frames']
        }

# 全局渲染器實例
_global_renderer: Optional[HighPerformanceRenderer] = None

def get_renderer() -> HighPerformanceRenderer:
    """獲取全局渲染器實例"""
    global _global_renderer
    if _global_renderer is None:
        _global_renderer = HighPerformanceRenderer()
    return _global_renderer

def start_dual_screen_system():
    """啟動雙螢幕系統"""
    renderer = get_renderer()
    renderer.start()
    return renderer

def stop_dual_screen_system():
    """停止雙螢幕系統"""
    global _global_renderer
    if _global_renderer:
        _global_renderer.stop()
        _global_renderer = None

# 使用範例
if __name__ == "__main__":
    import cv2

    # 啟動系統
    renderer = start_dual_screen_system()

    try:
        # 模擬相機幀
        for i in range(300):  # 10秒測試
            # 主螢幕：模擬相機預覽
            camera_frame = np.random.randint(0, 255, (320, 240, 3), dtype=np.uint8)
            renderer.render_main_screen(camera_frame, {'frame_id': i})

            # 圓形螢幕：每3幀更新一次
            if i % 3 == 0:
                gauge_frame = np.random.randint(0, 255, (160, 160, 3), dtype=np.uint8)
                renderer.render_gauge_screen(gauge_frame, {'gauge_value': i})

            time.sleep(1/30)  # 30fps

    except KeyboardInterrupt:
        print("\\n💻 用戶中斷")
    finally:
        stop_dual_screen_system()