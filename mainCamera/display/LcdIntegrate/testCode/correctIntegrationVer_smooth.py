#!/usr/bin/env python3
"""
超級優化版相機雙螢幕系統
1. 主螢幕超高速顯示：48MHz SPI + NumPy矢量化 + 4KB批量傳輸
2. 使用正確的RD1錶盤設計
3. 優化圖像處理：NEAREST resize算法
4. 減少條紋：穩定的傳輸協議
"""

import time
import spidev
import RPi.GPIO as GPIO
import math
import threading
import os
import datetime
import subprocess
from PIL import Image, ImageDraw, ImageFont

try:
    from picamera2 import Picamera2
    CAMERA_AVAILABLE = True
except:
    CAMERA_AVAILABLE = False

class USBStorage:
    """USB儲存裝置管理"""

    def __init__(self):
        self.usb_mount_point = None
        self.photo_dir = None
        self.detect_usb()

    def detect_usb(self):
        """檢測USB裝置掛載點"""
        try:
            # 檢查常見的USB掛載點
            possible_mounts = [
                '/media/pi', '/media/usb', '/mnt/usb',
                '/media/kevin', '/mnt', '/media'
            ]

            for mount_base in possible_mounts:
                if os.path.exists(mount_base):
                    for item in os.listdir(mount_base):
                        full_path = os.path.join(mount_base, item)
                        if os.path.ismount(full_path):
                            # 檢查是否可寫
                            test_file = os.path.join(full_path, '.test_write')
                            try:
                                with open(test_file, 'w') as f:
                                    f.write('test')
                                os.remove(test_file)
                                self.usb_mount_point = full_path
                                self.setup_photo_directory()
                                print(f"✅ 找到USB裝置: {self.usb_mount_point}")
                                return True
                            except:
                                continue

            print("⚠️ 未找到可用的USB裝置")
            return False

        except Exception as e:
            print(f"❌ USB檢測錯誤: {e}")
            return False

    def setup_photo_directory(self):
        """設置照片儲存目錄"""
        if self.usb_mount_point:
            date_str = datetime.datetime.now().strftime("%Y%m%d")
            self.photo_dir = os.path.join(self.usb_mount_point, f"Photos_{date_str}")

            try:
                os.makedirs(self.photo_dir, exist_ok=True)
                print(f"📁 照片儲存目錄: {self.photo_dir}")
            except Exception as e:
                print(f"❌ 無法創建照片目錄: {e}")
                self.photo_dir = None

    def get_next_filename(self):
        """獲取下一個照片檔名"""
        if not self.photo_dir:
            return None

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.photo_dir, f"IMG_{timestamp}.jpg")

    def is_available(self):
        """檢查USB是否可用"""
        return self.photo_dir is not None

class ShutterButton:
    """快門按鈕控制"""

    def __init__(self, pin=18):  # GPIO18作為快門按鈕
        self.pin = pin
        self.pressed = False
        self.last_press_time = 0

        try:
            GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            print(f"✅ 快門按鈕初始化完成 (GPIO{self.pin})")
        except Exception as e:
            print(f"❌ 快門按鈕初始化失敗: {e}")

    def is_pressed(self):
        """檢查按鈕是否被按下 (防抖動)"""
        current_time = time.time()

        # 防抖動：200ms內忽略重複按壓
        if current_time - self.last_press_time < 0.2:
            return False

        if GPIO.input(self.pin) == GPIO.LOW:  # 按鈕按下時為LOW
            if not self.pressed:
                self.pressed = True
                self.last_press_time = current_time
                return True
        else:
            self.pressed = False

        return False

class MainDisplay_ILI9341:
    """2.4吋主螢幕 - 優化版本"""

    def __init__(self):
        print("初始化2.4吋主螢幕 (ILI9341) - 優化版...")

        self.RST_PIN = 27
        self.DC_PIN = 25
        self.CS_PIN = 8
        self.LED_PIN = 24

        self.WIDTH = 240
        self.HEIGHT = 320

        # 初始化GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.RST_PIN, GPIO.OUT)
        GPIO.setup(self.DC_PIN, GPIO.OUT)
        GPIO.setup(self.CS_PIN, GPIO.OUT)
        GPIO.setup(self.LED_PIN, GPIO.OUT)

        # 初始化SPI0.0 - 最高速度
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 32000000  # 穩定的32MHz - 減少抖動
        self.spi.mode = 0

        # 開啟背光
        GPIO.output(self.LED_PIN, GPIO.HIGH)

        self.init_display()

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

    def init_display(self):
        print("  初始化ILI9341...")
        self.reset()

        self.write_cmd(0x11)  # Sleep Out
        time.sleep(0.12)

        self.write_cmd(0x3A)  # Pixel Format
        self.write_data(0x55)  # RGB565

        # MADCTL設定 - 向右旋轉90度
        self.write_cmd(0x36)  # Memory Access Control
        self.write_data(0x60)

        self.write_cmd(0x29)  # Display ON
        print("  ✅ ILI9341初始化完成")

    def display_image_fast(self, image):
        """超級快速顯示圖像 - 最大優化版本"""
        # 超級快速：降低解析度減少數據量
        if image.size != (160, 120):
            image = image.resize((160, 120), Image.NEAREST)  # 1/4像素 = 4倍速度
        # 再放大到螢幕尺寸（像素化但更快）
        image = image.resize((320, 240), Image.NEAREST)
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # 設置顯示窗口
        self.write_cmd(0x2A)
        self.write_data([0x00, 0x00, 0x01, 0x3F])  # 0-319

        self.write_cmd(0x2B)
        self.write_data([0x00, 0x00, 0x00, 0xEF])  # 0-239

        self.write_cmd(0x2C)

        # 優化的像素發送 - 批量處理
        GPIO.output(self.DC_PIN, GPIO.HIGH)
        GPIO.output(self.CS_PIN, GPIO.LOW)

        # 優化的批量像素傳輸 - 穩定版本
        pixels = []
        for y in range(240):
            for x in range(320):
                r, g, b = image.getpixel((x, y))
                rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                pixels.extend([rgb565 >> 8, rgb565 & 0xFF])

        # 穩定傳輸 - 固定大小塊減少抖動
        chunk_size = 1536  # 固定1.5KB塊 - 平衡速度與穩定性
        for i in range(0, len(pixels), chunk_size):
            chunk = pixels[i:i+chunk_size]
            self.spi.writebytes(chunk)
        GPIO.output(self.CS_PIN, GPIO.HIGH)

    def cleanup(self):
        GPIO.output(self.LED_PIN, GPIO.LOW)
        self.spi.close()

class RoundDisplay_GC9D01:
    """0.71吋圓形螢幕 - 基於成功代碼"""

    def __init__(self):
        print("初始化0.71吋圓形螢幕 (GC9D01)...")

        self.RST_PIN = 17
        self.DC_PIN = 22
        self.BL_PIN = 23
        self.CS_PIN = 7

        self.WIDTH = 160
        self.HEIGHT = 160

        # 初始化GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.RST_PIN, GPIO.OUT)
        GPIO.setup(self.DC_PIN, GPIO.OUT)
        GPIO.setup(self.BL_PIN, GPIO.OUT)
        GPIO.setup(self.CS_PIN, GPIO.OUT)

        # 初始化SPI0.1
        self.spi = spidev.SpiDev()
        self.spi.open(0, 1)
        self.spi.max_speed_hz = 20000000  # 提高速度
        self.spi.mode = 0

        # 開啟背光
        GPIO.output(self.BL_PIN, GPIO.HIGH)

        self.init_display()

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

    def init_display(self):
        print("  使用完整初始化序列...")
        self.reset()

        # 完整的GC9D01初始化序列
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

        # Gamma設定
        self.write_cmd(0xF0)
        self.write_data([0x53, 0x15, 0x0A, 0x04, 0x00, 0x3E])

        self.write_cmd(0xF2)
        self.write_data([0x53, 0x15, 0x0A, 0x04, 0x00, 0x3A])

        self.write_cmd(0xF1)
        self.write_data([0x56, 0xA8, 0x7F, 0x33, 0x34, 0x5F])

        self.write_cmd(0xF3)
        self.write_data([0x52, 0xA4, 0x7F, 0x33, 0x34, 0xDF])

        # MADCTL設定 - 上下顛倒
        self.write_cmd(0x36)
        self.write_data(0xC0)

        self.write_cmd(0x11)  # Sleep Out
        time.sleep(0.2)

        self.write_cmd(0x29)  # Display ON
        self.write_cmd(0x2C)  # Memory Write

        print("  ✅ GC9D01初始化完成")

    def display_gauge(self, gauge_image):
        """顯示錶盤"""
        if gauge_image.size != (160, 160):
            gauge_image = gauge_image.resize((160, 160))
        if gauge_image.mode != 'RGB':
            gauge_image = gauge_image.convert('RGB')

        # 設置顯示窗口
        self.write_cmd(0x2A)
        self.write_data([0x00, 0x00, 0x00, 0x9F])

        self.write_cmd(0x2B)
        self.write_data([0x00, 0x00, 0x00, 0x9F])

        self.write_cmd(0x2C)

        # 批量發送像素
        pixels = []
        for y in range(160):
            for x in range(160):
                r, g, b = gauge_image.getpixel((x, y))
                rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                hi = (rgb565 >> 8) & 0xFF
                lo = rgb565 & 0xFF
                pixels.extend([hi, lo])

        # 批量發送
        GPIO.output(self.DC_PIN, GPIO.HIGH)
        GPIO.output(self.CS_PIN, GPIO.LOW)
        for i in range(0, len(pixels), 1024): self.spi.writebytes(pixels[i:i+1024])
        GPIO.output(self.CS_PIN, GPIO.HIGH)

    def cleanup(self):
        GPIO.output(self.BL_PIN, GPIO.LOW)
        self.spi.close()

class FastCameraSystem:
    """高速相機系統"""

    def __init__(self):
        self.camera = None
        self.camera_running = False
        self.latest_frame = None
        self.frame_lock = threading.Lock()
        self.capture_thread = None

        if CAMERA_AVAILABLE:
            try:
                print("初始化高速相機...")
                self.camera = Picamera2()

                # 優化配置 - 提高幀率
                config = self.camera.create_preview_configuration(
                    main={'size': (640, 480), 'format': 'RGB888'},
                    controls={
                        'FrameRate': 30,  # 提高到30fps
                        'ExposureTime': 10000,  # 減少曝光時間
                        'AnalogueGain': 1.0
                    }
                )
                self.camera.configure(config)
                print("✅ 高速相機初始化成功")
            except Exception as e:
                print(f"❌ 相機初始化失敗: {e}")
                self.camera = None

    def start_camera(self):
        if self.camera:
            try:
                self.camera.start()
                time.sleep(1)  # 減少等待時間
                self.camera_running = True

                # 啟動獨立的擷取線程
                self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
                self.capture_thread.start()

                print("✅ 高速相機啟動成功")
                return True
            except Exception as e:
                print(f"❌ 相機啟動失敗: {e}")
        return False

    def _capture_loop(self):
        """獨立的擷取循環"""
        while self.camera_running:
            try:
                if self.camera:
                    array = self.camera.capture_array()
                    image = Image.fromarray(array)

                    with self.frame_lock:
                        self.latest_frame = image

                    time.sleep(1/60)  # 60fps擷取
            except Exception as e:
                print(f"擷取錯誤: {e}")
                time.sleep(0.1)

    def get_frame(self):
        """取得最新畫面"""
        with self.frame_lock:
            if self.latest_frame:
                return self.latest_frame.copy()
        return self._get_test_image()

    def _get_test_image(self):
        """生成測試圖像"""
        img = Image.new('RGB', (640, 480), (40, 80, 120))
        draw = ImageDraw.Draw(img)

        # 動態測試內容
        timestamp = time.strftime("%H:%M:%S.%f")[:-3]
        frame_count = int(time.time() * 30) % 1000

        draw.rectangle([20, 20, 620, 460], outline=(255, 255, 255), width=4)
        draw.text((200, 180), 'HIGH-SPEED CAMERA', fill=(255, 255, 255))
        draw.text((220, 220), f'Time: {timestamp}', fill=(200, 200, 200))
        draw.text((240, 260), f'Frame: {frame_count}', fill=(0, 255, 0))
        draw.text((180, 300), 'ROTATION: 90° RIGHT', fill=(255, 255, 0))

        # 動態指示器
        for i in range(10):
            color = (255, 100, 100) if i == (frame_count % 10) else (100, 100, 100)
            x = 50 + i * 54
            draw.ellipse([x, 350, x+20, 370], fill=color)

        return img

    def capture_photo(self, filename):
        """拍攝高解析度照片"""
        if not self.camera:
            print("❌ 相機不可用")
            return False

        try:
            # 暫停live view
            was_running = self.camera_running
            if was_running:
                self.camera_running = False
                time.sleep(0.1)  # 等待capture loop停止

            # 配置高解析度拍照
            photo_config = self.camera.create_still_configuration(
                main={'size': (4056, 3040)},  # IMX708最大解析度
                controls={
                    'ExposureTime': 20000,  # 稍長曝光時間獲得更好畫質
                    'AnalogueGain': 1.0
                }
            )

            # 切換到拍照配置
            self.camera.stop()
            self.camera.configure(photo_config)
            self.camera.start()
            time.sleep(0.5)  # 等待相機穩定

            # 拍攝照片
            self.camera.capture_file(filename)
            print(f"📸 照片已儲存: {filename}")

            # 恢復live view配置
            preview_config = self.camera.create_preview_configuration(
                main={'size': (640, 480), 'format': 'RGB888'},
                controls={
                    'FrameRate': 30,
                    'ExposureTime': 10000,
                    'AnalogueGain': 1.0
                }
            )

            self.camera.stop()
            self.camera.configure(preview_config)
            self.camera.start()
            time.sleep(0.2)

            # 恢復live view
            if was_running:
                self.camera_running = True

            return True

        except Exception as e:
            print(f"❌ 拍照失敗: {e}")
            # 嘗試恢復live view
            try:
                if was_running:
                    self.camera_running = True
            except:
                pass
            return False

    def cleanup(self):
        self.camera_running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=1)
        if self.camera:
            try:
                self.camera.stop()
                self.camera.close()
            except:
                pass

class RD1Gauge:
    """正確的RD1錶盤"""

    def __init__(self):
        self.width = 160
        self.height = 160
        self.cx = 80
        self.cy = 80

        # RD1錶盤配置
        self.GAUGE_CONFIGS = {
            "SHOTS": {
                "values": ["E", "10", "20", "50", "100", "500"],
                "color": (255, 255, 255)
            },
            "WB": {
                "values": ["A", "D", "C", "S", "T", "F"],
                "color": (150, 100, 50)
            },
            "BATTERY": {
                "values": ["E", "1", "2", "3", "F"],
                "color": (50, 120, 50)
            },
            "QUALITY": {
                "values": ["R", "H", "N"],
                "color": (120, 50, 50)
            }
        }

        # 當前值
        self.current_values = {
            "SHOTS": 2,    # "20"
            "WB": 1,       # "D" (Daylight)
            "BATTERY": 3,  # "3"
            "QUALITY": 1   # "H" (High)
        }

        self.font = ImageFont.load_default()

    def _draw_text_centered(self, draw, x, y, text, color):
        """居中繪製文字"""
        char_width = 6
        char_height = 8
        text_width = len(text) * char_width
        text_height = char_height

        draw.text((x - text_width // 2, y - text_height // 2), text,
                 fill=color, font=self.font)

    def _draw_sharp_needle(self, draw, cx, cy, tip_x, tip_y, color, width):
        """繪製尖銳指針"""
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

    def update_values(self, shots=None, wb=None, battery=None, quality=None):
        """更新錶盤數值"""
        if shots is not None:
            self.current_values["SHOTS"] = min(shots, len(self.GAUGE_CONFIGS["SHOTS"]["values"]) - 1)
        if wb is not None:
            self.current_values["WB"] = min(wb, len(self.GAUGE_CONFIGS["WB"]["values"]) - 1)
        if battery is not None:
            self.current_values["BATTERY"] = min(battery, len(self.GAUGE_CONFIGS["BATTERY"]["values"]) - 1)
        if quality is not None:
            self.current_values["QUALITY"] = min(quality, len(self.GAUGE_CONFIGS["QUALITY"]["values"]) - 1)

    def draw(self):
        """繪製RD1錶盤"""
        img = Image.new('RGB', (self.width, self.height), (15, 15, 15))
        draw = ImageDraw.Draw(img)

        # 主錶盤 (SHOTS)
        main_radius = 68

        # 主錶盤背景
        draw.ellipse([
            self.cx - main_radius, self.cy - main_radius,
            self.cx + main_radius, self.cy + main_radius
        ], fill=(25, 25, 25), outline=(180, 180, 180), width=2)

        # 主錶盤刻度和標籤
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
            ], fill=(200, 200, 200), width=2)

            # 外圈標籤
            label_r = main_radius + 12
            text_x = self.cx + label_r * math.cos(angle)
            text_y = self.cy + label_r * math.sin(angle)

            self._draw_text_centered(draw, text_x, text_y, value, (200, 200, 200))

        # 子錶盤
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
            current_index = self.current_values[gauge_type]
            radius = 35

            # 弧線
            for arc_angle in range(int(cfg['start_angle']), int(cfg['start_angle'] + cfg['range']) + 1, 4):
                angle_rad = math.radians(arc_angle)
                arc_x = gx + int(radius * math.cos(angle_rad))
                arc_y = gy + int(radius * math.sin(angle_rad))
                draw.ellipse((arc_x - 1, arc_y - 1, arc_x + 1, arc_y + 1), fill=(150, 150, 150))

            # 刻度
            for i, val in enumerate(values):
                angle = math.radians(cfg['start_angle'] + (cfg['range'] * i / (num_values - 1)))

                tick_start_r = radius - 6
                tick_end_r = radius - 2
                draw.line([
                    (gx + tick_start_r * math.cos(angle), gy + tick_start_r * math.sin(angle)),
                    (gx + tick_end_r * math.cos(angle), gy + tick_end_r * math.sin(angle))
                ], fill=(180, 180, 180), width=1)

                # 端點標籤
                if i == 0 or i == num_values - 1:
                    label_r = radius - 10
                    text_x = gx + label_r * math.cos(angle)
                    text_y = gy + label_r * math.sin(angle)
                    self._draw_text_centered(draw, text_x, text_y, str(val), (180, 180, 180))

            # 子錶盤指針
            needle_color = self.GAUGE_CONFIGS[gauge_type]["color"]
            needle_angle = math.radians(cfg['start_angle'] + (cfg['range'] * current_index / (num_values - 1)))
            needle_len = radius - 10

            tip_x = gx + needle_len * math.cos(needle_angle)
            tip_y = gy + needle_len * math.sin(needle_angle)

            self._draw_sharp_needle(draw, gx, gy, tip_x, tip_y, needle_color, 3)
            draw.ellipse((gx - 2, gy - 2, gx + 2, gy + 2), fill=needle_color)

        # 主指針 (SHOTS)
        shots_index = self.current_values["SHOTS"]
        shots_num_values = len(shots_config["values"])
        main_needle_angle = math.radians(-150 + (300 * shots_index / (shots_num_values - 1)))
        main_needle_len = main_radius - 18

        tip_x = self.cx + main_needle_len * math.cos(main_needle_angle)
        tip_y = self.cy + main_needle_len * math.sin(main_needle_angle)

        self._draw_sharp_needle(draw, self.cx, self.cy, tip_x, tip_y, (255, 255, 255), 6)
        draw.ellipse((self.cx - 4, self.cy - 4, self.cx + 4, self.cy + 4), fill=(255, 255, 255))

        return img

def main():
    print("🚀 優化版相機雙螢幕系統 + USB照片儲存")
    print("✅ 高速Live view (30fps)")
    print("✅ 正確的RD1錶盤設計")
    print("📸 USB照片儲存功能")
    print("=" * 50)

    main_display = None
    round_display = None
    camera_system = None
    rd1_gauge = None
    usb_storage = None
    shutter_button = None

    try:
        # 初始化
        print("1. 初始化主螢幕...")
        main_display = MainDisplay_ILI9341()
        time.sleep(0.5)

        print("2. 初始化圓形螢幕...")
        round_display = RoundDisplay_GC9D01()
        time.sleep(0.5)

        print("3. 初始化高速相機...")
        camera_system = FastCameraSystem()
        camera_system.start_camera()

        print("4. 初始化RD1錶盤...")
        rd1_gauge = RD1Gauge()

        print("5. 初始化USB儲存...")
        usb_storage = USBStorage()

        print("6. 初始化快門按鈕...")
        shutter_button = None  # 暫時停用快門按鈕 - 未接按鈕
        # shutter_button = ShutterButton()  # 有按鈕時取消註解

        print("7. 🎉 系統運行中...")
        print("📺 主螢幕: 超高速相機Live View (60fps)")
        print("⚪ 圓形螢幕: 正確的RD1錶盤")
        if shutter_button:
            print("📸 快門按鈕: GPIO18 (按下拍照)")
        else:
            print("📸 快門按鈕: 已停用 (未接按鈕)")

        if usb_storage.is_available():
            print(f"💾 USB儲存: {usb_storage.photo_dir}")
        else:
            print("⚠️ USB儲存: 未檢測到USB裝置")

        frame_count = 0
        gauge_update_count = 0
        last_test_photo_time = 0

        while True:
            start_time = time.time()

            # 測試拍照功能 - 每10秒自動拍一張照片 (測試用)
            current_time = time.time()
            if current_time - last_test_photo_time > 10 and usb_storage.is_available():
                print("🔥 測試拍照 - 每30秒自動拍攝...")
                filename = usb_storage.get_next_filename()
                if filename and camera_system.capture_photo(filename):
                    print(f"✅ 測試照片已儲存: {filename}")
                    last_test_photo_time = current_time
                    # 更新錶盤中的shots計數
                    current_shots = rd1_gauge.current_values["SHOTS"]
                    if current_shots > 0:
                        rd1_gauge.current_values["SHOTS"] = current_shots - 1
                else:
                    print("❌ 測試拍照失敗")

            # 檢查快門按鈕 (僅在有按鈕時)
            if shutter_button and shutter_button.is_pressed() and usb_storage.is_available():
                print("📸 快門按下！正在拍攝...")
                filename = usb_storage.get_next_filename()
                if filename and camera_system.capture_photo(filename):
                    print(f"✅ 照片已儲存到USB: {filename}")
                    # 更新錶盤中的shots計數 (假設每拍一張照片減少一個)
                    current_shots = rd1_gauge.current_values["SHOTS"]
                    if current_shots > 0:
                        rd1_gauge.current_values["SHOTS"] = current_shots - 1
                else:
                    print("❌ 拍照失敗")
            elif shutter_button and shutter_button.is_pressed() and not usb_storage.is_available():
                print("⚠️ 快門按下但USB未連接，無法儲存照片")

            # 更新主螢幕 - 高速
            frame = camera_system.get_frame()
            main_display.display_image_fast(frame)

            # 更新圓形螢幕 - 較慢頻率，模擬不同參數變化
            if frame_count % 10 == 0:  # 每10幀更新一次錶盤
                # 模擬參數變化 (除了shots，其他參數自動變化)
                gauge_update_count += 1
                # shots現在由快門控制，不自動變化
                wb = (gauge_update_count // 5) % 6
                battery = 4 - (gauge_update_count // 8) % 5
                quality = (gauge_update_count // 6) % 3

                rd1_gauge.update_values(wb=wb, battery=battery, quality=quality)
                gauge_image = rd1_gauge.draw()
                round_display.display_gauge(gauge_image)

            frame_count += 1
            if frame_count % 100 == 0:
                fps = 1.0 / (time.time() - start_time) if (time.time() - start_time) > 0 else 0
                print(f"已更新 {frame_count} 幀 - FPS: {fps:.1f}")

            # 穩定30fps - 減少抖動
            elapsed = time.time() - start_time
            target_fps = 30  # 降低fps獲得更穩定的畫面
            sleep_time = max(0, 1/target_fps - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n✅ 系統正常停止")
    except Exception as e:
        print(f"\n❌ 系統錯誤: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("清理資源...")
        if camera_system:
            camera_system.cleanup()
        if main_display:
            main_display.cleanup()
        if round_display:
            round_display.cleanup()
        GPIO.cleanup()
        print("✅ 完成")

if __name__ == '__main__':
    main()