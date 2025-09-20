#!/usr/bin/env python3
"""
LCD Gauge Elegant - 優雅動畫 + 完美字體布局
"""

import time
import random
import math
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Optional

# LCD Driver
import spidev
import RPi.GPIO as GPIO

def hex_to_rgb(hex_color: str) -> tuple:
    """Converts a hex color string to an RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

class Official_GC9D01:
    def __init__(self):
        self.RST_PIN = 27
        self.DC_PIN = 25
        self.BL_PIN = 18
        self.CS_PIN = 8
        self.WIDTH = 160
        self.HEIGHT = 160

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.RST_PIN, GPIO.OUT)
        GPIO.setup(self.DC_PIN, GPIO.OUT)
        GPIO.setup(self.BL_PIN, GPIO.OUT)
        GPIO.setup(self.CS_PIN, GPIO.OUT)

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 10000000
        self.spi.mode = 0

        GPIO.output(self.BL_PIN, GPIO.HIGH)
        self.init_official()

    def write_cmd(self, cmd):
        GPIO.output(self.DC_PIN, GPIO.LOW)
        GPIO.output(self.CS_PIN, GPIO.LOW)
        self.spi.writebytes([cmd])
        GPIO.output(self.CS_PIN, GPIO.HIGH)

    def write_data(self, data):
        GPIO.output(self.DC_PIN, GPIO.HIGH)
        GPIO.output(self.CS_PIN, GPIO.LOW)
        if isinstance(data, list):
            self.spi.writebytes(data)
        else:
            self.spi.writebytes([data])
        GPIO.output(self.CS_PIN, GPIO.HIGH)

    def reset(self):
        GPIO.output(self.RST_PIN, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.RST_PIN, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.RST_PIN, GPIO.HIGH)
        time.sleep(0.12)

    def init_official(self):
        self.reset()
        self.write_cmd(0xFE)
        self.write_cmd(0xEF)
        for reg in range(0x80, 0x90):
            self.write_cmd(reg)
            self.write_data(0xFF)
        self.write_cmd(0x3A)
        self.write_data(0x05)
        self.write_cmd(0xEC)
        self.write_data(0x01)
        self.write_cmd(0x74)
        self.write_data([0x02, 0x0E, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.write_cmd(0x98)
        self.write_data(0x3E)
        self.write_cmd(0x99)
        self.write_data(0x3E)
        self.write_cmd(0xB5)
        self.write_data([0x0D, 0x0D])
        self.write_cmd(0x60)
        self.write_data([0x38, 0x0F, 0x79, 0x67])
        self.write_cmd(0x61)
        self.write_data([0x38, 0x11, 0x79, 0x67])
        self.write_cmd(0x64)
        self.write_data([0x38, 0x17, 0x71, 0x5F, 0x79, 0x67])
        self.write_cmd(0x65)
        self.write_data([0x38, 0x13, 0x71, 0x5B, 0x79, 0x67])
        self.write_cmd(0x6A)
        self.write_data([0x00, 0x00])
        self.write_cmd(0x6C)
        self.write_data([0x22, 0x02, 0x22, 0x02, 0x22, 0x22, 0x50])
        self.write_cmd(0x6E)
        self.write_data([0x03, 0x03, 0x01, 0x01, 0x00, 0x00, 0x0F, 0x0F,
                        0x0D, 0x0D, 0x0B, 0x0B, 0x09, 0x09, 0x00, 0x00,
                        0x00, 0x00, 0x0A, 0x0A, 0x0C, 0x0C, 0x0E, 0x0E,
                        0x10, 0x10, 0x00, 0x00, 0x02, 0x02, 0x04, 0x04])
        self.write_cmd(0xBF)
        self.write_data(0x01)
        self.write_cmd(0xF9)
        self.write_data(0x40)
        self.write_cmd(0x9B)
        self.write_data(0x3B)
        self.write_cmd(0x93)
        self.write_data([0x33, 0x7F, 0x00])
        self.write_cmd(0x7E)
        self.write_data(0x30)
        self.write_cmd(0x70)
        self.write_data([0x0D, 0x02, 0x08, 0x0D, 0x02, 0x08])
        self.write_cmd(0x71)
        self.write_data([0x0D, 0x02, 0x08])
        self.write_cmd(0x91)
        self.write_data([0x0E, 0x09])
        self.write_cmd(0xC3)
        self.write_data(0x19)
        self.write_cmd(0xC4)
        self.write_data(0x19)
        self.write_cmd(0xC9)
        self.write_data(0x3C)
        self.write_cmd(0xF0)
        self.write_data([0x53, 0x15, 0x0A, 0x04, 0x00, 0x3E])
        self.write_cmd(0xF2)
        self.write_data([0x53, 0x15, 0x0A, 0x04, 0x00, 0x3A])
        self.write_cmd(0xF1)
        self.write_data([0x56, 0xA8, 0x7F, 0x33, 0x34, 0x5F])
        self.write_cmd(0xF3)
        self.write_data([0x52, 0xA4, 0x7F, 0x33, 0x34, 0xDF])
        self.write_cmd(0x36)
        self.write_data(0x00)
        self.write_cmd(0x11)
        time.sleep(0.2)
        self.write_cmd(0x29)
        self.write_cmd(0x2C)

    def set_window(self, x_start, y_start, x_end, y_end):
        self.write_cmd(0x2A)
        self.write_data([x_start >> 8, x_start & 0xFF, x_end >> 8, x_end & 0xFF])
        self.write_cmd(0x2B)
        self.write_data([y_start >> 8, y_start & 0xFF, y_end >> 8, y_end & 0xFF])
        self.write_cmd(0x2C)

    def display_image(self, image):
        if image.size != (self.WIDTH, self.HEIGHT):
            image = image.resize((self.WIDTH, self.HEIGHT), Image.LANCZOS)
        if image.mode != 'RGB':
            image = image.convert('RGB')

        self.set_window(0, 0, self.WIDTH-1, self.HEIGHT-1)
        for y in range(self.HEIGHT):
            for x in range(self.WIDTH):
                r, g, b = image.getpixel((x, y))
                rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                hi = (rgb565 >> 8) & 0xFF
                lo = rgb565 & 0xFF
                self.write_data([hi, lo])

    def cleanup(self):
        GPIO.output(self.BL_PIN, GPIO.LOW)
        self.spi.close()
        GPIO.cleanup()

class RD1LCDGauge:
    """RD-1 style gauge with elegant animation"""

    GAUGE_CONFIGS = {
        "SHOTS": {
            "name": "SHOTS",
            "values": ["E", "10", "20", "50", "100", "500"],
            "color": (255, 255, 255)
        },
        "WB": {
            "name": "WB",
            "values": ["A", "D", "C", "S", "T", "F"],
            "color": (150, 100, 50)
        },
        "BATTERY": {
            "name": "BAT",
            "values": ["E", "1", "2", "3", "F"],
            "color": (50, 120, 50)
        },
        "QUALITY": {
            "name": "QUAL",
            "values": ["R", "H", "N"],
            "color": (120, 50, 50)
        }
    }

    def __init__(self, width: int = 160, height: int = 160):
        self.width = width
        self.height = height
        self.cx = width // 2
        self.cy = height // 2

        # 改進的動畫系統
        self.current_values = {"SHOTS": 0, "WB": 0, "BATTERY": 4, "QUALITY": 0}
        self.target_values = self.current_values.copy()
        self.animation_values = {k: float(v) for k, v in self.current_values.items()}

        # 更流暢的動畫參數
        self.animation_rate = 8.0  # 提高響應速度
        self._anim_start_values = {k: float(v) for k, v in self.animation_values.items()}
        self._anim_start_time = {k: None for k in self.GAUGE_CONFIGS}
        self._base_step_duration = 0.8  # 延長動畫時間讓動畫更自然
        self._anim_duration = {k: self._base_step_duration for k in self.GAUGE_CONFIGS}
        self.interpolation_steps = 256  # 更多步驟
        self.quantize = True

        # 樣式配置
        self.style_config = {
            "background_color": "#0F0F0F",
            "main_dial": {
                "bg_color": "#191919",
                "outline_color": "#B4B4B4",
                "tick_color": "#C8C8C8",
                "needle_color": "#FFFFFF",
                "needle_width": 6
            },
            "sub_dial": {
                "arc_color": "#969696",
                "tick_color": "#B4B4B4",
                "text_color": "#C8C8C8",
                "needle_width": 3
            },
            "sub_dial_colors": {
                "WB": "#966432",
                "QUALITY": "#783232",
                "BATTERY": "#327832"
            }
        }

        self.font = ImageFont.load_default()

    def set_value(self, gauge_type: str, value: int):
        """設置數值並啟動優雅動畫"""
        if gauge_type not in self.GAUGE_CONFIGS:
            return False

        config = self.GAUGE_CONFIGS[gauge_type]
        if 0 <= value < len(config["values"]):
            start_val = float(self.animation_values[gauge_type])
            self.target_values[gauge_type] = value
            self._anim_start_values[gauge_type] = start_val
            self._anim_start_time[gauge_type] = time.time()

            # 根據距離調整動畫時間，但保持最小時間讓動畫可見
            dist = abs(value - start_val)
            self._anim_duration[gauge_type] = max(0.6, self._base_step_duration * (0.3 + dist * 0.7))
            return True
        return False

    def update_animation(self, dt: float = None):
        """更新動畫狀態 - 移除停格感"""
        if dt is None:
            dt = 1.0 / 60.0  # 降到60fps，更穩定

        if dt <= 0:
            return

        now = time.time()
        eps = 1e-8  # 更小的epsilon

        for gauge_type in self.GAUGE_CONFIGS:
            current = self.animation_values[gauge_type]
            target = float(self.target_values[gauge_type])

            start_t = self._anim_start_time.get(gauge_type)
            if start_t is not None:
                elapsed = max(0.0, now - start_t)
                duration = self._anim_duration.get(gauge_type, self._base_step_duration)
                t = min(1.0, elapsed / duration) if duration > 0 else 1.0

                # 改進的easing function - 更自然的運動曲線
                # 使用 ease-in-out-cubic 取代 ease-out
                if t < 0.5:
                    ease = 4 * t * t * t
                else:
                    ease = 1 - pow(-2 * t + 2, 3) / 2

                start_val = self._anim_start_values.get(gauge_type, current)
                raw_new_val = start_val + (target - start_val) * ease

                # 改進的量化 - 移除停格感
                dist = abs(target - start_val)
                if dist > eps:
                    # 更平滑的量化，減少step感
                    steps = max(1, int(dist * self.interpolation_steps))
                    frac = (raw_new_val - start_val) / (target - start_val) if (target - start_val) != 0 else 1.0

                    # 使用連續函數而非離散步驟
                    smooth_frac = frac + (math.sin(frac * math.pi * 2) * 0.02)  # 加入微小震盪
                    smooth_frac = max(0.0, min(1.0, smooth_frac))
                    new_val = start_val + (target - start_val) * smooth_frac
                else:
                    new_val = raw_new_val

                self.animation_values[gauge_type] = new_val

                if t >= 1.0 - eps:
                    self.animation_values[gauge_type] = target
                    self._anim_start_time[gauge_type] = None
            else:
                # 更平滑的指數平滑
                factor = 1.0 - math.exp(-self.animation_rate * dt)
                diff = target - current
                if abs(diff) > eps:
                    self.animation_values[gauge_type] += diff * factor
                else:
                    self.animation_values[gauge_type] = target

    def _draw_sharp_needle(self, draw, cx, cy, tip_x, tip_y, color, width):
        """Draw sharp needle"""
        angle = math.atan2(tip_y - cy, tip_x - cx)
        perp_angle = angle + math.pi / 2
        half_width = width / 2

        base_left_x = cx + half_width * math.cos(perp_angle)
        base_left_y = cy + half_width * math.sin(perp_angle)
        base_right_x = cx - half_width * math.cos(perp_angle)
        base_right_y = cy - half_width * math.sin(perp_angle)

        tail_length = width * 1.2
        tail_center_x = cx - tail_length * math.cos(angle)
        tail_center_y = cy - tail_length * math.sin(angle)

        draw.polygon([
            (tip_x, tip_y),
            (base_left_x, base_left_y),
            (tail_center_x, tail_center_y),
            (base_right_x, base_right_y)
        ], fill=color)

    def _draw_text_centered(self, draw, x, y, text, color, font):
        """居中繪製文字，避免被壓到"""
        # 估算文字大小
        char_width = 6
        char_height = 8
        text_width = len(text) * char_width
        text_height = char_height

        # 繪製文字
        draw.text((x - text_width // 2, y - text_height // 2), text,
                 fill=color, font=font)

    def draw(self) -> Image.Image:
        """Draw the gauge - 優雅布局"""
        bg_color = hex_to_rgb(self.style_config['background_color'])
        img = Image.new('RGB', (self.width, self.height), bg_color)
        draw = ImageDraw.Draw(img)

        # 調整大小 - 為外圍文字留出更多空間
        main_radius = 68  # 稍微縮小主錶盤

        # --- Main Dial (SHOTS) ---
        main_dial_style = self.style_config['main_dial']
        main_bg_color = hex_to_rgb(main_dial_style['bg_color'])
        main_outline_color = hex_to_rgb(main_dial_style['outline_color'])
        main_tick_color = hex_to_rgb(main_dial_style['tick_color'])

        # 主錶盤背景
        draw.ellipse([
            self.cx - main_radius, self.cy - main_radius,
            self.cx + main_radius, self.cy + main_radius
        ], fill=main_bg_color, outline=main_outline_color, width=2)

        # 主錶盤刻度和標籤 - 修復外圍字體壓到問題
        shots_config = self.GAUGE_CONFIGS["SHOTS"]
        shots_values = shots_config["values"]
        for i, value in enumerate(shots_values):
            angle_deg = -150 + (300 * i / (len(shots_values) - 1))
            angle = math.radians(angle_deg)

            # 刻度線
            tick_start_r = main_radius - 12
            tick_end_r = main_radius - 4
            draw.line([
                (self.cx + tick_start_r * math.cos(angle), self.cy + tick_start_r * math.sin(angle)),
                (self.cx + tick_end_r * math.cos(angle), self.cy + tick_end_r * math.sin(angle))
            ], fill=main_tick_color, width=2)

            # 外圈標籤 - 留出足夠空間防止壓到
            label_r = main_radius + 12  # 增加間距
            text_x = self.cx + label_r * math.cos(angle)
            text_y = self.cy + label_r * math.sin(angle)

            # 邊界檢查 - 確保文字不超出螢幕
            margin = 8
            text_x = max(margin, min(self.width - margin, text_x))
            text_y = max(margin, min(self.height - margin, text_y))

            # 居中繪製文字
            self._draw_text_centered(draw, text_x, text_y, value, (200, 200, 200), self.font)

        # --- Sub Dials - 調整尺寸避免重疊 ---
        sub_dial_style = self.style_config['sub_dial']
        small_radius = 38  # 稍微縮小

        small_gauges = {
            "WB": {
                "center": (self.cx - 50, self.cy - 18),
                "start_angle": -45,
                "range": 90
            },
            "QUALITY": {
                "center": (self.cx + 50, self.cy - 18),
                "start_angle": 135,
                "range": 90
            },
            "BATTERY": {
                "center": (self.cx, self.cy + 45),
                "start_angle": -135,
                "range": 90
            }
        }

        for gauge_type, cfg in small_gauges.items():
            gx, gy = cfg["center"]
            values = self.GAUGE_CONFIGS[gauge_type]["values"]
            num_values = len(values)
            current_index = self.animation_values[gauge_type]

            radius = 35 if gauge_type == "BATTERY" else small_radius

            # 弧線
            arc_color = hex_to_rgb(sub_dial_style['arc_color'])
            for arc_angle in range(int(cfg['start_angle']), int(cfg['start_angle'] + cfg['range']) + 1, 4):
                angle_rad = math.radians(arc_angle)
                arc_x = gx + int(radius * math.cos(angle_rad))
                arc_y = gy + int(radius * math.sin(angle_rad))
                draw.ellipse((arc_x - 1, arc_y - 1, arc_x + 1, arc_y + 1), fill=arc_color)

            # 刻度
            tick_color = hex_to_rgb(sub_dial_style['tick_color'])
            for i, val in enumerate(values):
                angle = math.radians(cfg['start_angle'] + (cfg['range'] * i / (num_values - 1)))

                tick_start_r = radius - 6
                tick_end_r = radius - 2
                draw.line([
                    (gx + tick_start_r * math.cos(angle), gy + tick_start_r * math.sin(angle)),
                    (gx + tick_end_r * math.cos(angle), gy + tick_end_r * math.sin(angle))
                ], fill=tick_color, width=1)

                # 端點標籤
                if i == 0 or i == num_values - 1:
                    label_r = radius - 10
                    text_x = gx + label_r * math.cos(angle)
                    text_y = gy + label_r * math.sin(angle)
                    text_color = hex_to_rgb(sub_dial_style['text_color'])
                    self._draw_text_centered(draw, text_x, text_y, str(val), text_color, self.font)

            # 子錶盤指針 - 使用平滑動畫值
            needle_color = hex_to_rgb(self.style_config['sub_dial_colors'][gauge_type])
            needle_angle = math.radians(cfg['start_angle'] + (cfg['range'] * current_index / (num_values - 1)))
            needle_len = radius - 10

            tip_x = gx + needle_len * math.cos(needle_angle)
            tip_y = gy + needle_len * math.sin(needle_angle)

            self._draw_sharp_needle(draw, gx, gy, tip_x, tip_y, needle_color,
                                   sub_dial_style['needle_width'])

            draw.ellipse((gx - 2, gy - 2, gx + 2, gy + 2), fill=needle_color)

        # --- Main Needle (SHOTS) - 使用平滑動畫值 ---
        main_needle_color = hex_to_rgb(main_dial_style['needle_color'])
        shots_index = self.animation_values["SHOTS"]
        shots_num_values = len(shots_config["values"])
        main_needle_angle = math.radians(-150 + (300 * shots_index / (shots_num_values - 1)))
        main_needle_len = main_radius - 18

        tip_x = self.cx + main_needle_len * math.cos(main_needle_angle)
        tip_y = self.cy + main_needle_len * math.sin(main_needle_angle)

        self._draw_sharp_needle(draw, self.cx, self.cy, tip_x, tip_y, main_needle_color,
                               main_dial_style['needle_width'])

        draw.ellipse((self.cx - 4, self.cy - 4, self.cx + 4, self.cy + 4),
                    fill=main_needle_color)

        return img

class LCDGaugeDemo:
    """優雅動畫Demo"""

    def __init__(self):
        print("Initializing LCD...")
        self.lcd = Official_GC9D01()
        self.gauge = RD1LCDGauge(160, 160)
        self.running = False
        print("LCD ready!")

    def start_demo(self, duration: int = 120):
        """Start elegant animation demo"""
        print(f"Starting elegant gauge demo for {duration} seconds...")
        self.running = True
        start_time = time.time()
        last_change_time = time.time()
        last_frame_time = time.time()

        try:
            while self.running and (time.time() - start_time) < duration:
                current_time = time.time()
                dt = current_time - last_frame_time
                last_frame_time = current_time

                # 每4秒隨機變更一個數值 - 更多時間欣賞動畫
                if current_time - last_change_time > 4.0:
                    gauge_types = list(self.gauge.GAUGE_CONFIGS.keys())
                    selected_gauge = random.choice(gauge_types)
                    max_val = len(self.gauge.GAUGE_CONFIGS[selected_gauge]["values"]) - 1
                    new_value = random.randint(0, max_val)

                    print(f"Setting {selected_gauge} to {new_value} ({self.gauge.GAUGE_CONFIGS[selected_gauge]['values'][new_value]})")
                    self.gauge.set_value(selected_gauge, new_value)
                    last_change_time = current_time

                # 60fps 動畫更新 - 更穩定
                self.gauge.update_animation(dt)

                # 30fps 顯示更新
                if int(current_time * 30) != int((current_time - dt) * 30):
                    image = self.gauge.draw()
                    self.lcd.display_image(image)

                # 60fps timing
                time.sleep(max(0, 1.0/60.0 - (time.time() - current_time)))

        except KeyboardInterrupt:
            print("Demo stopped")
        finally:
            self.running = False
            self.lcd.cleanup()
            print("Demo finished")

def main():
    print("RD-1 LCD Gauge - Elegant Animation Demo")
    try:
        demo = LCDGaugeDemo()
        demo.start_demo(120)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
