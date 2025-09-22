#!/usr/bin/env python3
"""
相機預覽優化器
Camera Preview Optimizer

專為主螢幕相機預覽設計的超流暢顯示系統
- 硬體加速
- 自適應幀率
- 動態品質調整
- 零延遲模式
"""

import time
import threading
import numpy as np
from typing import Optional, Callable, Tuple
from PIL import Image, ImageEnhance
import cv2
from dataclasses import dataclass
from enum import Enum

class PreviewQuality(Enum):
    """預覽品質等級"""
    ULTRA_LOW = (80, 60)      # 極低品質，最高幀率
    LOW = (160, 120)          # 低品質
    MEDIUM = (240, 180)       # 中等品質
    HIGH = (320, 240)         # 高品質
    ULTRA_HIGH = (480, 360)   # 極高品質

@dataclass
class CameraFrame:
    """相機幀資料"""
    image: np.ndarray
    timestamp: float
    frame_id: int
    quality: PreviewQuality
    metadata: dict = None

class AdaptiveQualityController:
    """自適應品質控制器"""

    def __init__(self):
        self.target_fps = 30
        self.current_quality = PreviewQuality.HIGH
        self.fps_history = []
        self.quality_adjustment_cooldown = 2.0  # 2秒調整間隔
        self.last_adjustment = 0

    def update_fps(self, current_fps: float):
        """更新FPS並調整品質"""
        self.fps_history.append(current_fps)
        if len(self.fps_history) > 10:
            self.fps_history.pop(0)

        # 每2秒檢查一次是否需要調整品質
        now = time.time()
        if now - self.last_adjustment < self.quality_adjustment_cooldown:
            return

        avg_fps = sum(self.fps_history) / len(self.fps_history)

        # 品質調整邏輯
        if avg_fps < self.target_fps * 0.8:  # FPS低於目標80%
            self._decrease_quality()
        elif avg_fps > self.target_fps * 0.95:  # FPS高於目標95%
            self._increase_quality()

        self.last_adjustment = now

    def _decrease_quality(self):
        """降低品質"""
        qualities = list(PreviewQuality)
        current_index = qualities.index(self.current_quality)
        if current_index > 0:
            self.current_quality = qualities[current_index - 1]
            print(f"📉 降低預覽品質到: {self.current_quality.name}")

    def _increase_quality(self):
        """提高品質"""
        qualities = list(PreviewQuality)
        current_index = qualities.index(self.current_quality)
        if current_index < len(qualities) - 1:
            self.current_quality = qualities[current_index + 1]
            print(f"📈 提高預覽品質到: {self.current_quality.name}")

class CameraPreviewOptimizer:
    """相機預覽優化器"""

    def __init__(self, renderer):
        self.renderer = renderer
        self.running = False
        self.preview_thread = None

        # 優化參數
        self.quality_controller = AdaptiveQualityController()
        self.zero_latency_mode = True
        self.hardware_acceleration = True

        # 性能統計
        self.frame_count = 0
        self.last_fps_update = time.time()
        self.current_fps = 0

        # 圖像處理快取
        self.resize_cache = {}
        self.enhancement_cache = {}

        # 相機介面
        self.camera = None
        self._setup_camera()

    def _setup_camera(self):
        """設置相機"""
        try:
            # 嘗試使用 Pi Camera
            import picamera
            import picamera.array
            self.camera_type = "picamera"
            print("📷 使用 Pi Camera")
        except ImportError:
            try:
                # 備用 OpenCV
                self.camera = cv2.VideoCapture(0)
                self.camera_type = "opencv"
                print("📷 使用 OpenCV Camera")
            except:
                print("❌ 無法初始化相機")
                self.camera_type = None

    def start_preview(self):
        """開始預覽"""
        if self.running:
            return

        self.running = True
        self.preview_thread = threading.Thread(
            target=self._preview_loop,
            name="CameraPreviewLoop",
            daemon=True
        )
        self.preview_thread.start()
        print("🎥 相機預覽已啟動")

    def stop_preview(self):
        """停止預覽"""
        self.running = False
        if self.preview_thread and self.preview_thread.is_alive():
            self.preview_thread.join(timeout=1.0)

        if self.camera and self.camera_type == "opencv":
            self.camera.release()

        print("⏹️ 相機預覽已停止")

    def _preview_loop(self):
        """預覽循環 - 在獨立線程中運行"""
        frame_id = 0
        last_fps_time = time.time()

        while self.running:
            try:
                # 捕獲幀
                frame = self._capture_frame()
                if frame is None:
                    time.sleep(0.01)
                    continue

                # 優化處理
                optimized_frame = self._optimize_frame(frame)

                # 發送到渲染器
                self.renderer.render_main_screen(
                    optimized_frame,
                    {
                        'frame_id': frame_id,
                        'quality': self.quality_controller.current_quality.name,
                        'fps': self.current_fps
                    }
                )

                frame_id += 1
                self.frame_count += 1

                # 更新FPS統計
                now = time.time()
                if now - last_fps_time >= 1.0:
                    self.current_fps = self.frame_count / (now - last_fps_time)
                    self.quality_controller.update_fps(self.current_fps)
                    self.frame_count = 0
                    last_fps_time = now

                # 零延遲模式：不等待
                if not self.zero_latency_mode:
                    time.sleep(1/30)  # 30fps

            except Exception as e:
                print(f"❌ 預覽循環錯誤: {e}")
                time.sleep(0.1)

    def _capture_frame(self) -> Optional[np.ndarray]:
        """捕獲一幀"""
        try:
            if self.camera_type == "opencv":
                ret, frame = self.camera.read()
                return frame if ret else None

            elif self.camera_type == "picamera":
                # Pi Camera 實現
                with picamera.array.PiRGBArray(self.camera) as stream:
                    self.camera.capture(stream, format='rgb')
                    return stream.array

            else:
                # 模擬模式
                return np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        except Exception as e:
            print(f"❌ 捕獲幀錯誤: {e}")
            return None

    def _optimize_frame(self, frame: np.ndarray) -> np.ndarray:
        """優化幀處理"""
        target_size = self.quality_controller.current_quality.value

        # 快速縮放
        if frame.shape[:2] != target_size:
            frame = self._fast_resize(frame, target_size)

        # 硬體加速處理
        if self.hardware_acceleration:
            frame = self._hardware_accelerated_enhance(frame)

        return frame

    def _fast_resize(self, image: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """快速縮放 - 使用快取"""
        cache_key = (image.shape, target_size)

        if cache_key not in self.resize_cache:
            # 使用 OpenCV 的快速插值
            resized = cv2.resize(image, target_size, interpolation=cv2.INTER_LINEAR)
            self.resize_cache[cache_key] = resized
            return resized
        else:
            # 直接使用 OpenCV resize，不快取圖像內容
            return cv2.resize(image, target_size, interpolation=cv2.INTER_LINEAR)

    def _hardware_accelerated_enhance(self, image: np.ndarray) -> np.ndarray:
        """硬體加速圖像增強"""
        try:
            # 使用 OpenCV 的優化函數
            # 快速自動對比度
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)

            # CLAHE (對比度限制的自適應直方圖均衡)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l = clahe.apply(l)

            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2RGB)

            return enhanced

        except:
            # 備用：返回原圖
            return image

    def set_quality(self, quality: PreviewQuality):
        """手動設置品質"""
        self.quality_controller.current_quality = quality
        print(f"🎛️ 手動設置預覽品質: {quality.name}")

    def enable_zero_latency(self, enable: bool):
        """啟用/禁用零延遲模式"""
        self.zero_latency_mode = enable
        print(f"⚡ 零延遲模式: {'啟用' if enable else '禁用'}")

    def get_preview_stats(self) -> dict:
        """獲取預覽統計"""
        return {
            'fps': self.current_fps,
            'quality': self.quality_controller.current_quality.name,
            'zero_latency': self.zero_latency_mode,
            'hardware_acceleration': self.hardware_acceleration
        }

class ZeroLatencyMode:
    """零延遲模式優化"""

    @staticmethod
    def optimize_numpy_operations():
        """優化 NumPy 操作"""
        # 設置 NumPy 線程數
        import os
        os.environ['OMP_NUM_THREADS'] = '2'  # Raspberry Pi 通常是4核，預留2核給其他任務

    @staticmethod
    def optimize_opencv():
        """優化 OpenCV"""
        # 啟用 OpenCV 優化
        cv2.setUseOptimized(True)
        cv2.setNumThreads(2)

    @staticmethod
    def apply_system_optimizations():
        """應用系統級優化"""
        ZeroLatencyMode.optimize_numpy_operations()
        ZeroLatencyMode.optimize_opencv()
        print("⚡ 零延遲模式優化已應用")

# 初始化優化
ZeroLatencyMode.apply_system_optimizations()

if __name__ == "__main__":
    from dual_screen_manager import start_dual_screen_system, stop_dual_screen_system

    # 啟動雙螢幕系統
    renderer = start_dual_screen_system()

    # 啟動相機預覽優化器
    preview = CameraPreviewOptimizer(renderer)
    preview.start_preview()

    try:
        # 運行10秒測試
        time.sleep(10)

        # 顯示統計
        stats = preview.get_preview_stats()
        print(f"📊 預覽統計: {stats}")

    except KeyboardInterrupt:
        print("\\n💻 用戶中斷")
    finally:
        preview.stop_preview()
        stop_dual_screen_system()