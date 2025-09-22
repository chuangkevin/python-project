#!/usr/bin/env python3
"""
AnalogGauge 整合模組
Analog Gauge Integration Module

將 analogGauge 無縫整合到雙螢幕系統中
- 低延遲更新 (10fps)
- 與主螢幕同步
- 支援所有 RD-1 錶盤功能
"""

import time
import threading
import numpy as np
from typing import Dict, Any, Optional
from PIL import Image, ImageDraw
import sys
from pathlib import Path

# 添加 analogGauge 路徑
analog_gauge_path = Path(__file__).resolve().parents[2] / 'analogGauge'
sys.path.insert(0, str(analog_gauge_path))

try:
    from circular_screen import CircularScreenAPI, _load_config_direct
    from rd1_gauge import RD1Gauge
    ANALOG_GAUGE_AVAILABLE = True
    print("✅ AnalogGauge 模組載入成功")
except ImportError as e:
    print(f"⚠️ AnalogGauge 模組載入失敗: {e}")
    ANALOG_GAUGE_AVAILABLE = False

class AnalogGaugeRenderer:
    """AnalogGauge 渲染器"""

    def __init__(self, dual_screen_renderer):
        self.dual_screen_renderer = dual_screen_renderer
        self.running = False
        self.update_thread = None

        # AnalogGauge 實例
        self.gauge_api = None
        self.gauge = None

        # 狀態資料
        self.current_state = {
            'mode': 'ev',
            'value_index': 9,  # 0.0 EV
            'battery': 4,
            'shots': 5,
            'quality': 0
        }

        # 更新頻率控制
        self.update_interval = 1.0 / 10  # 10fps
        self.last_update = 0

        # 初始化
        self._initialize_gauge()

    def _initialize_gauge(self):
        """初始化 AnalogGauge"""
        if not ANALOG_GAUGE_AVAILABLE:
            print("⚠️ AnalogGauge 不可用，使用模擬模式")
            return

        try:
            # 載入配置
            config = _load_config_direct()

            # 創建 RD1Gauge 實例
            self.gauge = RD1Gauge(
                width=160,
                height=160,
                style='rd1_classic',
                show_labels=False,
                reset_on_start=True
            )

            # 設置初始狀態
            self.gauge.set_value('SHOTS', self.current_state['value_index'])
            self.gauge.set_value('WB', self.current_state['quality'])
            self.gauge.set_value('QUALITY', self.current_state['shots'])
            self.gauge.set_value('BATTERY', self.current_state['battery'])

            print("✅ AnalogGauge 初始化成功")

        except Exception as e:
            print(f"❌ AnalogGauge 初始化失敗: {e}")
            self.gauge = None

    def start(self):
        """啟動 AnalogGauge 渲染"""
        if self.running or not self.gauge:
            return

        self.running = True
        self.update_thread = threading.Thread(
            target=self._update_loop,
            name="AnalogGaugeUpdater",
            daemon=True
        )
        self.update_thread.start()
        print("🎛️ AnalogGauge 渲染已啟動")

    def stop(self):
        """停止 AnalogGauge 渲染"""
        self.running = False
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1.0)
        print("⏹️ AnalogGauge 渲染已停止")

    def _update_loop(self):
        """更新循環"""
        while self.running:
            try:
                current_time = time.time()

                # 控制更新頻率
                if current_time - self.last_update >= self.update_interval:
                    self._render_gauge()
                    self.last_update = current_time

                # 短暫休眠
                time.sleep(0.01)

            except Exception as e:
                print(f"❌ AnalogGauge 更新錯誤: {e}")

    def _render_gauge(self):
        """渲染錶盤"""
        try:
            if not self.gauge:
                # 模擬模式：生成簡單的圓形圖像
                image = self._generate_mock_gauge()
            else:
                # 更新動畫
                dt = self.update_interval
                self.gauge.update_animation(dt)

                # 渲染到圖像
                image = self._gauge_to_image()

            # 發送到雙螢幕渲染器
            if image is not None:
                self.dual_screen_renderer.render_gauge_screen(
                    image,
                    {
                        'mode': self.current_state['mode'],
                        'value': self.current_state['value_index'],
                        'timestamp': time.time()
                    }
                )

        except Exception as e:
            print(f"❌ 錶盤渲染錯誤: {e}")

    def _gauge_to_image(self) -> Optional[np.ndarray]:
        """將錶盤轉換為圖像"""
        try:
            # 創建PIL圖像
            pil_image = Image.new('RGB', (160, 160), (0, 0, 0))
            draw = ImageDraw.Draw(pil_image)

            # 渲染錶盤到PIL圖像
            if hasattr(self.gauge, 'render_to_pil'):
                self.gauge.render_to_pil(pil_image)
            else:
                # 備用渲染方法
                self._render_gauge_fallback(draw)

            # 轉換為NumPy陣列
            return np.array(pil_image)

        except Exception as e:
            print(f"❌ 錶盤圖像轉換錯誤: {e}")
            return None

    def _render_gauge_fallback(self, draw: ImageDraw.Draw):
        """備用錶盤渲染"""
        # 簡單的圓形錶盤
        center = (80, 80)
        radius = 70

        # 外圓
        draw.ellipse(
            [center[0] - radius, center[1] - radius,
             center[0] + radius, center[1] + radius],
            outline=(255, 255, 255), width=2
        )

        # 刻度
        for i in range(12):
            angle = i * 30 * np.pi / 180
            start_radius = radius - 10
            end_radius = radius - 5

            start_x = center[0] + start_radius * np.cos(angle - np.pi/2)
            start_y = center[1] + start_radius * np.sin(angle - np.pi/2)
            end_x = center[0] + end_radius * np.cos(angle - np.pi/2)
            end_y = center[1] + end_radius * np.sin(angle - np.pi/2)

            draw.line([(start_x, start_y), (end_x, end_y)], fill=(255, 255, 255), width=1)

        # 指針
        pointer_angle = (self.current_state['value_index'] / 18) * 2 * np.pi - np.pi/2
        pointer_length = radius - 20

        pointer_x = center[0] + pointer_length * np.cos(pointer_angle)
        pointer_y = center[1] + pointer_length * np.sin(pointer_angle)

        draw.line([center, (pointer_x, pointer_y)], fill=(255, 0, 0), width=3)

    def _generate_mock_gauge(self) -> np.ndarray:
        """生成模擬錶盤"""
        image = np.zeros((160, 160, 3), dtype=np.uint8)

        # 簡單的圓形
        center = (80, 80)
        radius = 70

        # 使用PIL繪製
        pil_image = Image.fromarray(image)
        draw = ImageDraw.Draw(pil_image)

        # 圓形邊框
        draw.ellipse(
            [center[0] - radius, center[1] - radius,
             center[0] + radius, center[1] + radius],
            outline=(0, 255, 0), width=2
        )

        # 中心文字
        draw.text(center, "MOCK", fill=(0, 255, 0), anchor="mm")

        return np.array(pil_image)

    def update_mode(self, mode: str):
        """更新模式"""
        if mode != self.current_state['mode']:
            self.current_state['mode'] = mode
            if self.gauge:
                # 更新錶盤配置
                pass
            print(f"🎛️ 錶盤模式: {mode}")

    def update_value(self, value_index: int):
        """更新數值"""
        if value_index != self.current_state['value_index']:
            self.current_state['value_index'] = value_index
            if self.gauge:
                self.gauge.set_value('SHOTS', value_index)
            print(f"🎛️ 錶盤數值: {value_index}")

    def update_battery(self, battery_level: int):
        """更新電池電量"""
        if battery_level != self.current_state['battery']:
            self.current_state['battery'] = battery_level
            if self.gauge:
                self.gauge.set_value('BATTERY', battery_level)

    def update_shots(self, shots_remaining: int):
        """更新剩餘拍攝數"""
        if shots_remaining != self.current_state['shots']:
            self.current_state['shots'] = shots_remaining
            if self.gauge:
                self.gauge.set_value('QUALITY', shots_remaining)

    def handle_encoder_rotate(self, direction: int):
        """處理編碼器旋轉"""
        # 更新數值索引
        new_index = self.current_state['value_index'] + direction

        # 根據當前模式設定範圍
        if self.current_state['mode'] == 'ev':
            new_index = max(0, min(18, new_index))  # EV: -3.0 到 +3.0
        elif self.current_state['mode'] == 'iso':
            new_index = max(0, min(7, new_index))   # ISO: AUTO 到 6400
        elif self.current_state['mode'] == 'shutter':
            new_index = max(0, min(15, new_index))  # 快門: AUTO 到 2"

        self.update_value(new_index)

    def handle_encoder_press(self):
        """處理編碼器按壓"""
        # 重置到預設模式
        self.update_mode('ev')
        self.update_value(9)  # 0.0 EV

    def get_current_state(self) -> Dict[str, Any]:
        """獲取當前狀態"""
        return self.current_state.copy()

class AnalogGaugeController:
    """AnalogGauge 控制器 - 統一介面"""

    def __init__(self, dual_screen_renderer):
        self.renderer = AnalogGaugeRenderer(dual_screen_renderer)
        self.running = False

    def start(self):
        """啟動控制器"""
        self.renderer.start()
        self.running = True
        print("🎮 AnalogGauge 控制器已啟動")

    def stop(self):
        """停止控制器"""
        self.renderer.stop()
        self.running = False
        print("⏹️ AnalogGauge 控制器已停止")

    def cycle_mode(self):
        """循環模式"""
        modes = ['ev', 'iso', 'shutter', 'wb', 'quality']
        current_mode = self.renderer.current_state['mode']
        current_index = modes.index(current_mode) if current_mode in modes else 0
        next_mode = modes[(current_index + 1) % len(modes)]
        self.renderer.update_mode(next_mode)

    def adjust_value(self, direction: int):
        """調整數值"""
        self.renderer.handle_encoder_rotate(direction)

    def reset_to_default(self):
        """重置到預設"""
        self.renderer.handle_encoder_press()

    def update_system_state(self, **kwargs):
        """更新系統狀態"""
        if 'battery' in kwargs:
            self.renderer.update_battery(kwargs['battery'])
        if 'shots' in kwargs:
            self.renderer.update_shots(kwargs['shots'])

# 測試範例
if __name__ == "__main__":
    from dual_screen_manager import start_dual_screen_system, stop_dual_screen_system

    # 啟動雙螢幕系統
    dual_renderer = start_dual_screen_system()

    # 啟動 AnalogGauge 控制器
    gauge_controller = AnalogGaugeController(dual_renderer)
    gauge_controller.start()

    try:
        # 測試模式切換
        time.sleep(2)
        gauge_controller.cycle_mode()

        time.sleep(2)
        gauge_controller.adjust_value(3)

        time.sleep(2)
        gauge_controller.adjust_value(-5)

        time.sleep(2)
        gauge_controller.reset_to_default()

        # 運行5秒
        time.sleep(5)

    except KeyboardInterrupt:
        print("\\n💻 用戶中斷")
    finally:
        gauge_controller.stop()
        stop_dual_screen_system()