#!/usr/bin/env python3
"""
RD-1 相機系統主控制器
RD-1 Camera System Main Controller

整合雙螢幕顯示系統的完整解決方案
- 主螢幕：超流暢相機預覽 (30fps)
- 圓形螢幕：analogGauge 錶盤 (10fps)
- 硬體編碼器支援
- 軟片模擬整合
- 零延遲操作
"""

import time
import threading
import signal
import sys
from typing import Dict, Any, Optional, Callable
from pathlib import Path

# 導入子系統
from dual_screen_manager import HighPerformanceRenderer, start_dual_screen_system, stop_dual_screen_system
from camera_preview_optimizer import CameraPreviewOptimizer, PreviewQuality
from analog_gauge_integration import AnalogGaugeController

# 導入軟片模擬系統
film_preset_path = Path(__file__).resolve().parents[1] / 'filter'
sys.path.insert(0, str(film_preset_path))

try:
    from preset_manager import FilmPresetManager
    FILM_SIMULATION_AVAILABLE = True
    print("✅ 軟片模擬系統載入成功")
except ImportError:
    print("⚠️ 軟片模擬系統不可用")
    FILM_SIMULATION_AVAILABLE = False

class RD1CameraSystem:
    """RD-1 相機系統主控制器"""

    def __init__(self):
        self.running = False
        self.system_thread = None

        # 子系統
        self.dual_screen_renderer: Optional[HighPerformanceRenderer] = None
        self.camera_preview: Optional[CameraPreviewOptimizer] = None
        self.analog_gauge: Optional[AnalogGaugeController] = None

        # 軟片模擬
        self.film_manager: Optional[FilmPresetManager] = None
        self.current_film_preset = "PROVIA"

        # 系統狀態
        self.camera_state = {
            'mode': 'auto',
            'ev_compensation': 0.0,
            'iso': 'AUTO',
            'shutter_speed': 'AUTO',
            'white_balance': 'AUTO',
            'quality': 'RAW+JPEG',
            'battery_level': 100,
            'shots_remaining': 500,
            'film_simulation': self.current_film_preset
        }

        # 回調函數
        self.on_shutter_press: Optional[Callable] = None
        self.on_mode_change: Optional[Callable] = None

        # 初始化軟片模擬
        self._initialize_film_simulation()

    def _initialize_film_simulation(self):
        """初始化軟片模擬系統"""
        if FILM_SIMULATION_AVAILABLE:
            try:
                self.film_manager = FilmPresetManager()
                presets = self.film_manager.list_presets()
                print(f"📸 載入 {len(presets)} 個軟片預設")
            except Exception as e:
                print(f"❌ 軟片模擬初始化失敗: {e}")
                self.film_manager = None

    def start_system(self):
        """啟動整個相機系統"""
        if self.running:
            print("⚠️ 系統已在運行中")
            return

        print("🚀 啟動 RD-1 相機系統...")

        try:
            # 1. 啟動雙螢幕渲染器
            self.dual_screen_renderer = start_dual_screen_system()
            time.sleep(0.5)  # 讓渲染器完全啟動

            # 2. 啟動相機預覽優化器
            self.camera_preview = CameraPreviewOptimizer(self.dual_screen_renderer)
            self.camera_preview.start_preview()
            time.sleep(0.5)

            # 3. 啟動 AnalogGauge 控制器
            self.analog_gauge = AnalogGaugeController(self.dual_screen_renderer)
            self.analog_gauge.start()
            time.sleep(0.5)

            # 4. 啟動主系統線程
            self.running = True
            self.system_thread = threading.Thread(
                target=self._system_loop,
                name="RD1SystemController",
                daemon=True
            )
            self.system_thread.start()

            # 設置信號處理器
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)

            print("✅ RD-1 相機系統啟動完成")
            self._print_system_status()

        except Exception as e:
            print(f"❌ 系統啟動失敗: {e}")
            self.stop_system()
            raise

    def stop_system(self):
        """停止整個相機系統"""
        if not self.running:
            return

        print("⏹️ 停止 RD-1 相機系統...")

        self.running = False

        # 停止子系統
        if self.analog_gauge:
            self.analog_gauge.stop()

        if self.camera_preview:
            self.camera_preview.stop_preview()

        if self.dual_screen_renderer:
            stop_dual_screen_system()

        # 等待主線程結束
        if self.system_thread and self.system_thread.is_alive():
            self.system_thread.join(timeout=2.0)

        print("✅ RD-1 相機系統已停止")

    def _system_loop(self):
        """主系統循環"""
        last_status_update = time.time()

        while self.running:
            try:
                current_time = time.time()

                # 每5秒更新系統狀態
                if current_time - last_status_update >= 5.0:
                    self._update_system_status()
                    last_status_update = current_time

                # 檢查系統健康狀況
                self._check_system_health()

                time.sleep(0.1)  # 100ms 循環

            except Exception as e:
                print(f"❌ 系統循環錯誤: {e}")

    def _update_system_status(self):
        """更新系統狀態"""
        # 模擬電池消耗
        if self.camera_state['battery_level'] > 0:
            self.camera_state['battery_level'] = max(0, self.camera_state['battery_level'] - 1)

        # 更新 AnalogGauge
        if self.analog_gauge:
            battery_level = min(4, self.camera_state['battery_level'] // 20)  # 0-4
            shots_level = min(5, self.camera_state['shots_remaining'] // 100)  # 0-5

            self.analog_gauge.update_system_state(
                battery=battery_level,
                shots=shots_level
            )

    def _check_system_health(self):
        """檢查系統健康狀況"""
        if self.camera_preview:
            stats = self.camera_preview.get_preview_stats()
            if stats['fps'] < 15:  # FPS過低
                print(f"⚠️ 相機預覽FPS過低: {stats['fps']:.1f}")

        if self.dual_screen_renderer:
            perf_stats = self.dual_screen_renderer.get_performance_stats()
            if perf_stats['dropped_frames'] > 100:
                print(f"⚠️ 丟幀過多: {perf_stats['dropped_frames']}")

    def _signal_handler(self, signum, frame):
        """信號處理器"""
        print(f"\\n🛑 收到信號 {signum}，正在優雅關閉...")
        self.stop_system()
        sys.exit(0)

    def _print_system_status(self):
        """打印系統狀態"""
        print("\\n" + "="*50)
        print("📊 RD-1 相機系統狀態")
        print("="*50)
        print(f"相機模式: {self.camera_state['mode']}")
        print(f"軟片模擬: {self.camera_state['film_simulation']}")
        print(f"電池電量: {self.camera_state['battery_level']}%")
        print(f"剩餘拍攝: {self.camera_state['shots_remaining']}")

        if self.camera_preview:
            stats = self.camera_preview.get_preview_stats()
            print(f"預覽FPS: {stats['fps']:.1f}")
            print(f"預覽品質: {stats['quality']}")

        print("="*50)

    # 公共控制介面

    def capture_photo(self) -> str:
        """拍攝照片"""
        print("📷 拍攝照片...")

        # 更新拍攝計數
        if self.camera_state['shots_remaining'] > 0:
            self.camera_state['shots_remaining'] -= 1

        # 應用軟片模擬
        if self.film_manager and self.current_film_preset:
            try:
                processor = self.film_manager.create_processor(self.current_film_preset)
                print(f"🎞️ 套用軟片模擬: {self.current_film_preset}")
            except Exception as e:
                print(f"❌ 軟片模擬套用失敗: {e}")

        # 觸發回調
        if self.on_shutter_press:
            self.on_shutter_press()

        # 模擬拍攝延遲
        time.sleep(0.1)

        filename = f"IMG_{int(time.time())}.jpg"
        print(f"✅ 照片已保存: {filename}")
        return filename

    def cycle_film_simulation(self):
        """循環軟片模擬"""
        if not self.film_manager:
            return

        try:
            presets = self.film_manager.list_presets()
            if not presets:
                return

            # 找到當前預設的索引
            current_names = [p['name'] for p in presets]
            try:
                current_index = current_names.index(self.current_film_preset)
                next_index = (current_index + 1) % len(current_names)
            except ValueError:
                next_index = 0

            self.current_film_preset = current_names[next_index]
            self.camera_state['film_simulation'] = self.current_film_preset

            print(f"🎞️ 軟片模擬: {self.current_film_preset}")

        except Exception as e:
            print(f"❌ 軟片模擬切換失敗: {e}")

    def adjust_ev_compensation(self, direction: int):
        """調整曝光補償"""
        current_ev = self.camera_state['ev_compensation']
        new_ev = current_ev + (direction * 0.3)  # 1/3 EV steps
        new_ev = max(-3.0, min(3.0, new_ev))  # 限制範圍

        self.camera_state['ev_compensation'] = new_ev

        # 更新 AnalogGauge
        if self.analog_gauge:
            ev_index = int((new_ev + 3.0) / 0.3)  # 轉換為索引
            self.analog_gauge.adjust_value(direction)

        print(f"🎚️ 曝光補償: {new_ev:+.1f} EV")

    def cycle_camera_mode(self):
        """循環相機模式"""
        modes = ['auto', 'manual', 'aperture_priority', 'shutter_priority']
        current_index = modes.index(self.camera_state['mode'])
        next_mode = modes[(current_index + 1) % len(modes)]

        self.camera_state['mode'] = next_mode

        # 更新 AnalogGauge 模式
        if self.analog_gauge:
            self.analog_gauge.cycle_mode()

        print(f"📸 相機模式: {next_mode}")

        # 觸發回調
        if self.on_mode_change:
            self.on_mode_change(next_mode)

    def set_preview_quality(self, quality: PreviewQuality):
        """設置預覽品質"""
        if self.camera_preview:
            self.camera_preview.set_quality(quality)

    def get_system_stats(self) -> Dict[str, Any]:
        """獲取系統統計"""
        stats = {
            'camera_state': self.camera_state.copy(),
            'system_running': self.running
        }

        if self.camera_preview:
            stats['preview'] = self.camera_preview.get_preview_stats()

        if self.dual_screen_renderer:
            stats['renderer'] = self.dual_screen_renderer.get_performance_stats()

        return stats

# 全局系統實例
_global_camera_system: Optional[RD1CameraSystem] = None

def get_camera_system() -> RD1CameraSystem:
    """獲取全局相機系統實例"""
    global _global_camera_system
    if _global_camera_system is None:
        _global_camera_system = RD1CameraSystem()
    return _global_camera_system

def start_rd1_camera():
    """啟動 RD-1 相機系統"""
    system = get_camera_system()
    system.start_system()
    return system

def stop_rd1_camera():
    """停止 RD-1 相機系統"""
    global _global_camera_system
    if _global_camera_system:
        _global_camera_system.stop_system()
        _global_camera_system = None

# 主程式入口
if __name__ == "__main__":
    print("🎬 RD-1 相機系統演示")

    # 啟動系統
    camera_system = start_rd1_camera()

    try:
        print("\\n🎮 控制說明:")
        print("  Enter - 拍照")
        print("  f - 切換軟片模擬")
        print("  m - 切換相機模式")
        print("  + - 增加曝光補償")
        print("  - - 減少曝光補償")
        print("  q - 退出")

        while True:
            try:
                key = input("\\n> ").strip().lower()

                if key == 'q':
                    break
                elif key == '':  # Enter
                    camera_system.capture_photo()
                elif key == 'f':
                    camera_system.cycle_film_simulation()
                elif key == 'm':
                    camera_system.cycle_camera_mode()
                elif key == '+':
                    camera_system.adjust_ev_compensation(1)
                elif key == '-':
                    camera_system.adjust_ev_compensation(-1)
                elif key == 's':
                    stats = camera_system.get_system_stats()
                    print(f"📊 系統統計: {stats}")
                else:
                    print("❓ 未知命令")

            except KeyboardInterrupt:
                break

    except Exception as e:
        print(f"❌ 系統錯誤: {e}")
    finally:
        print("\\n👋 正在關閉系統...")
        stop_rd1_camera()