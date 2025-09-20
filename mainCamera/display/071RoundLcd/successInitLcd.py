import spidev
import RPi.GPIO as GPIO
import time

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
        print('使用官方初始化序列...')

        self.reset()

        # 完全按照官方代碼的初始化序列
        self.write_cmd(0xFE)
        self.write_cmd(0xEF)

        self.write_cmd(0x80)
        self.write_data(0xFF)

        self.write_cmd(0x81)
        self.write_data(0xFF)

        self.write_cmd(0x82)
        self.write_data(0xFF)

        self.write_cmd(0x83)
        self.write_data(0xFF)

        self.write_cmd(0x84)
        self.write_data(0xFF)

        self.write_cmd(0x85)
        self.write_data(0xFF)

        self.write_cmd(0x86)
        self.write_data(0xFF)

        self.write_cmd(0x87)
        self.write_data(0xFF)

        self.write_cmd(0x88)
        self.write_data(0xFF)

        self.write_cmd(0x89)
        self.write_data(0xFF)

        self.write_cmd(0x8A)
        self.write_data(0xFF)

        self.write_cmd(0x8B)
        self.write_data(0xFF)

        self.write_cmd(0x8C)
        self.write_data(0xFF)

        self.write_cmd(0x8D)
        self.write_data(0xFF)

        self.write_cmd(0x8E)
        self.write_data(0xFF)

        self.write_cmd(0x8F)
        self.write_data(0xFF)

        self.write_cmd(0x3A)  # Pixel Format
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

        # 關鍵的MADCTL設定
        self.write_cmd(0x36)
        self.write_data(0x00)  # 官方設定值

        self.write_cmd(0x11)  # Sleep Out
        time.sleep(0.2)  # 200ms延遲

        self.write_cmd(0x29)  # Display ON
        self.write_cmd(0x2C)  # Memory Write

        print('官方初始化完成')

    def set_window(self, x_start, y_start, x_end, y_end):
        self.write_cmd(0x2A)
        self.write_data([x_start >> 8, x_start & 0xFF, x_end >> 8, x_end & 0xFF]                                                                                        )

        self.write_cmd(0x2B)
        self.write_data([y_start >> 8, y_start & 0xFF, y_end >> 8, y_end & 0xFF]                                                                                        )

        self.write_cmd(0x2C)

    def fill_screen(self, r, g, b):
        print(f'填充 RGB({r}, {g}, {b})')

        self.set_window(0, 0, 159, 159)

        rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        hi = (rgb565 >> 8) & 0xFF
        lo = rgb565 & 0xFF

        for i in range(25600):  # 160*160
            self.write_data([hi, lo])

    def cleanup(self):
        GPIO.output(self.BL_PIN, GPIO.LOW)
        self.spi.close()
        GPIO.cleanup()

# 測試官方初始化
if __name__ == '__main__':
    lcd = Official_GC9D01()

    try:
        print('使用官方初始化序列測試...')

        # 測試所有基本顏色
        test_colors = [
            (255, 0, 0),     # 純紅
            (0, 255, 0),     # 純綠
            (0, 0, 255),     # 純藍
            (255, 255, 0),   # 黃色
            (255, 0, 255),   # 紫色
            (0, 255, 255),   # 青色
            (255, 255, 255), # 白色
            (128, 128, 128), # 灰色
            (0, 0, 0)        # 黑色
        ]

        for color in test_colors:
            lcd.fill_screen(*color)
            time.sleep(2)

        print('官方初始化測試完成！')

    except Exception as e:
        print(f'錯誤: {e}')
        import traceback
        traceback.print_exc()
    finally:
        lcd.cleanup()