#!/usr/bin/env python3
"""
雙螢幕成功控制範例
可以同時控制兩個螢幕顯示不同顏色

硬體配置:
- 主螢幕 (2.4吋 ILI9341): SPI0.0, CS=GPIO8
- 圓形螢幕 (0.71吋 GC9D01): SPI0.1, CS=GPIO7
- 共用 5V電源, GND, SCLK, MOSI
"""

import time
import spidev
import RPi.GPIO as GPIO

class MainDisplay_ILI9341:
    """2.4吋主螢幕控制類"""

    def __init__(self):
        print("初始化2.4吋主螢幕 (ILI9341)...")

        # GPIO腳位配置
        self.RST_PIN = 27  # Pin 13 -> GPIO27
        self.DC_PIN = 25   # Pin 22 -> GPIO25
        self.CS_PIN = 8    # Pin 24 -> GPIO8 (SPI0_CE0)
        self.LED_PIN = 24  # Pin 18 -> GPIO24

        self.WIDTH = 240
        self.HEIGHT = 320

        # 初始化GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.RST_PIN, GPIO.OUT)
        GPIO.setup(self.DC_PIN, GPIO.OUT)
        GPIO.setup(self.CS_PIN, GPIO.OUT)
        GPIO.setup(self.LED_PIN, GPIO.OUT)

        # 初始化SPI0.0
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)  # SPI0.0
        self.spi.max_speed_hz = 32000000
        self.spi.mode = 0

        # 開啟背光
        GPIO.output(self.LED_PIN, GPIO.HIGH)
        print(f"  腳位: RST={self.RST_PIN}, DC={self.DC_PIN}, CS={self.CS_PIN}, LED={self.LED_PIN}")

        self.init_display()

    def write_cmd(self, cmd):
        """發送命令"""
        GPIO.output(self.DC_PIN, GPIO.LOW)
        GPIO.output(self.CS_PIN, GPIO.LOW)
        self.spi.writebytes([cmd])
        GPIO.output(self.CS_PIN, GPIO.HIGH)

    def write_data(self, data):
        """發送資料"""
        GPIO.output(self.DC_PIN, GPIO.HIGH)
        GPIO.output(self.CS_PIN, GPIO.LOW)
        if isinstance(data, list):
            self.spi.writebytes(data)
        else:
            self.spi.writebytes([data])
        GPIO.output(self.CS_PIN, GPIO.HIGH)

    def reset(self):
        """重置螢幕"""
        GPIO.output(self.RST_PIN, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.RST_PIN, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.RST_PIN, GPIO.HIGH)
        time.sleep(0.12)

    def init_display(self):
        """初始化ILI9341"""
        print("  初始化ILI9341...")
        self.reset()

        # 基本初始化序列
        self.write_cmd(0x11)  # Sleep Out
        time.sleep(0.12)

        self.write_cmd(0x3A)  # Pixel Format
        self.write_data(0x55)  # RGB565

        self.write_cmd(0x36)  # Memory Access Control
        self.write_data(0x00)  # 正確的顏色方向

        self.write_cmd(0x29)  # Display ON
        print("  ILI9341初始化完成")

    def fill_screen(self, r, g, b):
        """填充整個螢幕"""
        # 設置顯示窗口
        self.write_cmd(0x2A)  # Column Address Set
        self.write_data([0x00, 0x00, 0x00, 0xEF])  # 0-239

        self.write_cmd(0x2B)  # Row Address Set
        self.write_data([0x00, 0x00, 0x01, 0x3F])  # 0-319

        self.write_cmd(0x2C)  # Memory Write

        # RGB565轉換
        rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        hi = (rgb565 >> 8) & 0xFF
        lo = rgb565 & 0xFF

        # 發送像素資料
        pixel_pair = [hi, lo]
        GPIO.output(self.DC_PIN, GPIO.HIGH)
        GPIO.output(self.CS_PIN, GPIO.LOW)

        for _ in range(self.WIDTH * self.HEIGHT):
            self.spi.writebytes(pixel_pair)

        GPIO.output(self.CS_PIN, GPIO.HIGH)

    def cleanup(self):
        """清理資源"""
        GPIO.output(self.LED_PIN, GPIO.LOW)
        self.spi.close()

class RoundDisplay_GC9D01:
    """0.71吋圓形螢幕控制類"""

    def __init__(self):
        print("初始化0.71吋圓形螢幕 (GC9D01)...")

        # GPIO腳位配置 - 按照接線圖
        self.RST_PIN = 17  # Pin 11 -> GPIO17
        self.DC_PIN = 22   # Pin 15 -> GPIO22
        self.BL_PIN = 23   # Pin 16 -> GPIO23
        self.CS_PIN = 7    # Pin 26 -> GPIO7 (SPI0_CE1)

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
        self.spi.open(0, 1)  # SPI0.1
        self.spi.max_speed_hz = 10000000
        self.spi.mode = 0

        # 開啟背光
        GPIO.output(self.BL_PIN, GPIO.HIGH)
        print(f"  腳位: RST={self.RST_PIN}, DC={self.DC_PIN}, CS={self.CS_PIN}, BL={self.BL_PIN}")

        self.init_display()

    def write_cmd(self, cmd):
        """發送命令"""
        GPIO.output(self.DC_PIN, GPIO.LOW)
        GPIO.output(self.CS_PIN, GPIO.LOW)
        self.spi.writebytes([cmd])
        GPIO.output(self.CS_PIN, GPIO.HIGH)

    def write_data(self, data):
        """發送資料"""
        GPIO.output(self.DC_PIN, GPIO.HIGH)
        GPIO.output(self.CS_PIN, GPIO.LOW)
        if isinstance(data, list):
            self.spi.writebytes(data)
        else:
            self.spi.writebytes([data])
        GPIO.output(self.CS_PIN, GPIO.HIGH)

    def reset(self):
        """重置螢幕"""
        GPIO.output(self.RST_PIN, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.RST_PIN, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(self.RST_PIN, GPIO.HIGH)
        time.sleep(0.12)

    def init_display(self):
        """完整的GC9D01官方初始化序列"""
        print("  使用完整官方初始化序列...")
        self.reset()

        # 完整的官方初始化序列
        self.write_cmd(0xFE)
        self.write_cmd(0xEF)

        # 設置0x80-0x8F為0xFF (關鍵步驟)
        for reg in range(0x80, 0x90):
            self.write_cmd(reg)
            self.write_data(0xFF)

        self.write_cmd(0x3A)  # Pixel Format
        self.write_data(0x05)  # RGB565

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
        self.write_data(0x00)  # 必須是0x00

        self.write_cmd(0x11)  # Sleep Out
        time.sleep(0.2)  # 200ms延遲

        self.write_cmd(0x29)  # Display ON
        self.write_cmd(0x2C)  # Memory Write

        print("  GC9D01初始化完成")

    def fill_screen(self, r, g, b):
        """填充整個圓形螢幕"""
        # 設置顯示窗口
        self.write_cmd(0x2A)  # Column Address Set
        self.write_data([0x00, 0x00, 0x00, 0x9F])  # 0-159

        self.write_cmd(0x2B)  # Row Address Set
        self.write_data([0x00, 0x00, 0x00, 0x9F])  # 0-159

        self.write_cmd(0x2C)  # Memory Write

        # RGB565轉換
        rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
        hi = (rgb565 >> 8) & 0xFF
        lo = rgb565 & 0xFF

        # 發送像素資料
        for _ in range(self.WIDTH * self.HEIGHT):
            self.write_data([hi, lo])

    def cleanup(self):
        """清理資源"""
        GPIO.output(self.BL_PIN, GPIO.LOW)
        self.spi.close()

class DualDisplayController:
    """雙螢幕控制器"""

    def __init__(self):
        print("雙螢幕控制器初始化")
        print("=" * 50)

        # 初始化兩個螢幕
        self.main_display = MainDisplay_ILI9341()
        time.sleep(0.5)  # 等待主螢幕穩定

        self.round_display = RoundDisplay_GC9D01()
        time.sleep(0.5)  # 等待圓形螢幕穩定

        print("=" * 50)
        print("✅ 雙螢幕初始化完成!")

    def set_colors(self, main_color, round_color):
        """
        同時設定兩個螢幕的顏色

        Args:
            main_color: 主螢幕顏色 (r, g, b) 元組
            round_color: 圓形螢幕顏色 (r, g, b) 元組
        """
        main_r, main_g, main_b = main_color
        round_r, round_g, round_b = round_color

        print(f"設定顏色:")
        print(f"  主螢幕: RGB({main_r}, {main_g}, {main_b})")
        print(f"  圓形螢幕: RGB({round_r}, {round_g}, {round_b})")

        # 同時填充兩個螢幕
        self.main_display.fill_screen(main_r, main_g, main_b)
        self.round_display.fill_screen(round_r, round_g, round_b)

    def cleanup(self):
        """清理所有資源"""
        print("清理雙螢幕資源...")
        self.main_display.cleanup()
        self.round_display.cleanup()
        GPIO.cleanup()

def demo_color_cycle():
    """顏色循環演示"""
    print("雙螢幕顏色循環演示")
    print("=" * 30)

    try:
        # 初始化雙螢幕控制器
        controller = DualDisplayController()

        # 定義顏色組合
        color_combinations = [
            # (主螢幕顏色, 圓形螢幕顏色)
            ((255, 0, 0), (0, 255, 255)),    # 紅色 vs 青色
            ((0, 255, 0), (255, 0, 255)),    # 綠色 vs 紫色
            ((0, 0, 255), (255, 255, 0)),    # 藍色 vs 黃色
            ((255, 255, 255), (0, 0, 0)),    # 白色 vs 黑色
            ((255, 165, 0), (0, 0, 255)),    # 橙色 vs 藍色
            ((128, 0, 128), (0, 255, 0)),    # 紫色 vs 綠色
            ((255, 192, 203), (255, 0, 0)),  # 粉色 vs 紅色
            ((0, 0, 0), (255, 255, 255))     # 黑色 vs 白色
        ]

        print(f"\n開始顏色循環 ({len(color_combinations)} 組顏色)...")

        for i, (main_color, round_color) in enumerate(color_combinations):
            print(f"\n第 {i+1}/{len(color_combinations)} 組:")
            controller.set_colors(main_color, round_color)
            time.sleep(3)  # 每組顏色顯示3秒

        print("\n🎉 顏色循環演示完成!")

    except KeyboardInterrupt:
        print("\n演示被中斷")
    except Exception as e:
        print(f"\n發生錯誤: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理資源
        if 'controller' in locals():
            controller.cleanup()

def demo_synchronized_colors():
    """同步顏色演示"""
    print("雙螢幕同步顏色演示")
    print("=" * 30)

    try:
        controller = DualDisplayController()

        # 相同顏色同步顯示
        sync_colors = [
            (255, 0, 0),     # 紅色
            (0, 255, 0),     # 綠色
            (0, 0, 255),     # 藍色
            (255, 255, 0),   # 黃色
            (255, 0, 255),   # 紫色
            (0, 255, 255),   # 青色
            (255, 255, 255), # 白色
            (0, 0, 0)        # 黑色
        ]

        print(f"\n開始同步顏色演示 ({len(sync_colors)} 種顏色)...")

        for i, color in enumerate(sync_colors):
            print(f"\n第 {i+1}/{len(sync_colors)} 種顏色: RGB{color}")
            controller.set_colors(color, color)  # 兩個螢幕顯示相同顏色
            time.sleep(2)

        print("\n🎉 同步顏色演示完成!")

    except KeyboardInterrupt:
        print("\n演示被中斷")
    except Exception as e:
        print(f"\n發生錯誤: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'controller' in locals():
            controller.cleanup()

def main():
    """主程式"""
    print("🖥️  雙螢幕控制成功範例")
    print("=" * 60)
    print("硬體配置:")
    print("  主螢幕 (2.4吋): SPI0.0, GPIO8(CS), GPIO27(RST), GPIO25(DC), GPIO24(LED)")
    print("  圓形螢幕 (0.71吋): SPI0.1, GPIO7(CS), GPIO17(RST), GPIO22(DC), GPIO23(BL)")
    print("  共用: 5V電源, GND, GPIO11(SCLK), GPIO10(MOSI)")
    print("=" * 60)

    try:
        print("\n選擇演示模式:")
        print("1. 對比顏色循環 (兩螢幕顯示不同顏色)")
        print("2. 同步顏色循環 (兩螢幕顯示相同顏色)")
        print("3. 自訂顏色測試")

        choice = input("\n請選擇 (1-3) [預設:1]: ").strip()
        if not choice:
            choice = "1"

        if choice == "1":
            demo_color_cycle()
        elif choice == "2":
            demo_synchronized_colors()
        elif choice == "3":
            # 自訂顏色測試
            controller = DualDisplayController()

            print("\n自訂顏色測試")
            print("輸入格式: R,G,B (例如: 255,0,0)")

            main_input = input("主螢幕顏色: ").strip()
            round_input = input("圓形螢幕顏色: ").strip()

            try:
                main_color = tuple(map(int, main_input.split(',')))
                round_color = tuple(map(int, round_input.split(',')))

                controller.set_colors(main_color, round_color)
                print("按 Enter 結束...")
                input()

            except ValueError:
                print("顏色格式錯誤!")
            finally:
                controller.cleanup()
        else:
            print("無效選擇!")

    except KeyboardInterrupt:
        print("\n程式被中斷")
    except Exception as e:
        print(f"\n程式發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()