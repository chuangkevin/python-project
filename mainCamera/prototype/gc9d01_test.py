#!/usr/bin/env python3

import spidev
import RPi.GPIO as GPIO
import time
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# GC9D01 圓形LCD驅動程式
class GC9D01:
    def __init__(self):
        # GPIO腳位配置 (根據0.71寸LCD規格)
        self.DC_PIN = 4    # DC (Data/Command)
        self.RST_PIN = 8   # Reset
        self.CS_PIN = 5    # Chip Select
        
        # SPI設定
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)  # SPI bus 0, device 0
        self.spi.max_speed_hz = 40000000  # 40MHz
        self.spi.mode = 0
        
        # GPIO設定
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.DC_PIN, GPIO.OUT)
        GPIO.setup(self.RST_PIN, GPIO.OUT)
        GPIO.setup(self.CS_PIN, GPIO.OUT)
        
        # 初始化螢幕
        self.init_display()
    
    def write_cmd(self, cmd):
        """發送命令"""
        GPIO.output(self.DC_PIN, GPIO.LOW)  # 命令模式
        GPIO.output(self.CS_PIN, GPIO.LOW)
        self.spi.xfer2([cmd])
        GPIO.output(self.CS_PIN, GPIO.HIGH)
    
    def write_data(self, data):
        """發送數據"""
        GPIO.output(self.DC_PIN, GPIO.HIGH)  # 數據模式
        GPIO.output(self.CS_PIN, GPIO.LOW)
        if isinstance(data, list):
            self.spi.xfer2(data)
        else:
            self.spi.xfer2([data])
        GPIO.output(self.CS_PIN, GPIO.HIGH)
    
    def reset(self):
        """硬體復位"""
        GPIO.output(self.RST_PIN, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.RST_PIN, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(self.RST_PIN, GPIO.HIGH)
        time.sleep(0.1)
    
    def init_display(self):
        """初始化GC9D01顯示器"""
        print("初始化 GC9D01 圓形LCD...")
        
        # 硬體復位
        self.reset()
        
        # GC9D01 初始化序列
        self.write_cmd(0xEF)
        self.write_cmd(0xEB)
        self.write_data(0x14)
        
        self.write_cmd(0xFE)
        self.write_cmd(0xEF)
        
        self.write_cmd(0xEB)
        self.write_data(0x14)
        
        self.write_cmd(0x84)
        self.write_data(0x40)
        
        self.write_cmd(0x85)
        self.write_data(0xFF)
        
        self.write_cmd(0x86)
        self.write_data(0xFF)
        
        self.write_cmd(0x87)
        self.write_data(0xFF)
        
        self.write_cmd(0x88)
        self.write_data(0x0A)
        
        self.write_cmd(0x89)
        self.write_data(0x21)
        
        self.write_cmd(0x8A)
        self.write_data(0x00)
        
        self.write_cmd(0x8B)
        self.write_data(0x80)
        
        self.write_cmd(0x8C)
        self.write_data(0x01)
        
        self.write_cmd(0x8D)
        self.write_data(0x01)
        
        self.write_cmd(0x8E)
        self.write_data(0xFF)
        
        self.write_cmd(0x8F)
        self.write_data(0xFF)
        
        self.write_cmd(0xB6)
        self.write_data([0x00, 0x00])
        
        self.write_cmd(0x36)
        self.write_data(0x18)
        
        self.write_cmd(0x3A)
        self.write_data(0x05)  # 16-bit color
        
        self.write_cmd(0x90)
        self.write_data([0x08, 0x08, 0x08, 0x08])
        
        self.write_cmd(0xBD)
        self.write_data(0x06)
        
        self.write_cmd(0xBC)
        self.write_data(0x00)
        
        self.write_cmd(0xFF)
        self.write_data([0x60, 0x01, 0x04])
        
        self.write_cmd(0xC3)
        self.write_data(0x13)
        
        self.write_cmd(0xC4)
        self.write_data(0x13)
        
        self.write_cmd(0xC9)
        self.write_data(0x22)
        
        self.write_cmd(0xBE)
        self.write_data(0x11)
        
        self.write_cmd(0xE1)
        self.write_data([0x10, 0x0E])
        
        self.write_cmd(0xDF)
        self.write_data([0x21, 0x0c, 0x02])
        
        self.write_cmd(0xF0)
        self.write_data([0x45, 0x09, 0x08, 0x08, 0x26, 0x2A])
        
        self.write_cmd(0xF1)
        self.write_data([0x43, 0x70, 0x72, 0x36, 0x37, 0x6F])
        
        self.write_cmd(0xF2)
        self.write_data([0x45, 0x09, 0x08, 0x08, 0x26, 0x2A])
        
        self.write_cmd(0xF3)
        self.write_data([0x43, 0x70, 0x72, 0x36, 0x37, 0x6F])
        
        self.write_cmd(0xED)
        self.write_data([0x1B, 0x0B])
        
        self.write_cmd(0xAE)
        self.write_data(0x77)
        
        self.write_cmd(0xCD)
        self.write_data(0x63)
        
        self.write_cmd(0x70)
        self.write_data([0x07, 0x07, 0x04, 0x0E, 0x0F, 0x09, 0x07, 0x08, 0x03])
        
        self.write_cmd(0xE8)
        self.write_data(0x34)
        
        self.write_cmd(0x62)
        self.write_data([0x18, 0x0D, 0x71, 0xED, 0x70, 0x70, 0x18, 0x0F, 0x71, 0xEF, 0x70, 0x70])
        
        self.write_cmd(0x63)
        self.write_data([0x18, 0x11, 0x71, 0xF1, 0x70, 0x70, 0x18, 0x13, 0x71, 0xF3, 0x70, 0x70])
        
        self.write_cmd(0x64)
        self.write_data([0x28, 0x29, 0xF1, 0x01, 0xF1, 0x00, 0x07])
        
        self.write_cmd(0x66)
        self.write_data([0x3C, 0x00, 0xCD, 0x67, 0x45, 0x45, 0x10, 0x00, 0x00, 0x00])
        
        self.write_cmd(0x67)
        self.write_data([0x00, 0x3C, 0x00, 0x00, 0x00, 0x01, 0x54, 0x10, 0x32, 0x98])
        
        self.write_cmd(0x74)
        self.write_data([0x10, 0x85, 0x80, 0x00, 0x00, 0x4E, 0x00])
        
        self.write_cmd(0x98)
        self.write_data([0x3e, 0x07])
        
        self.write_cmd(0x35)  # Tearing Effect Line ON
        self.write_cmd(0x21)  # Display Inversion ON
        
        self.write_cmd(0x11)  # Sleep Out
        time.sleep(0.12)
        
        self.write_cmd(0x29)  # Display ON
        time.sleep(0.02)
        
        print("GC9D01 初始化完成！")
    
    def set_windows(self, x_start, y_start, x_end, y_end):
        """設置顯示窗口"""
        self.write_cmd(0x2A)  # Column Address Set
        self.write_data([x_start >> 8, x_start & 0xFF, x_end >> 8, x_end & 0xFF])
        
        self.write_cmd(0x2B)  # Page Address Set
        self.write_data([y_start >> 8, y_start & 0xFF, y_end >> 8, y_end & 0xFF])
        
        self.write_cmd(0x2C)  # Memory Write
    
    def show_image(self, image):
        """顯示圖像"""
        if image.size != (160, 160):
            image = image.resize((160, 160), Image.LANCZOS)
        
        # 轉換為RGB565格式
        img_data = np.array(image.convert('RGB'))
        
        # RGB888 轉 RGB565
        r = (img_data[:, :, 0] >> 3) << 11
        g = (img_data[:, :, 1] >> 2) << 5
        b = img_data[:, :, 2] >> 3
        rgb565 = r | g | b
        
        # 轉換為字節數組
        data = []
        for row in rgb565:
            for pixel in row:
                data.append(pixel >> 8)    # 高字節
                data.append(pixel & 0xFF)  # 低字節
        
        # 設置全屏顯示
        self.set_windows(0, 0, 159, 159)
        
        # 發送圖像數據
        GPIO.output(self.DC_PIN, GPIO.HIGH)  # 數據模式
        GPIO.output(self.CS_PIN, GPIO.LOW)
        
        # 分批發送數據
        chunk_size = 4096
        for i in range(0, len(data), chunk_size):
            self.spi.xfer2(data[i:i+chunk_size])
        
        GPIO.output(self.CS_PIN, GPIO.HIGH)
    
    def cleanup(self):
        """清理資源"""
        GPIO.cleanup()
        self.spi.close()

# 測試程式
def main():
    try:
        # 初始化LCD
        lcd = GC9D01()
        
        # 創建測試圖像
        image = Image.new('RGB', (160, 160), 'BLACK')
        draw = ImageDraw.Draw(image)
        
        # 畫圓形邊框
        draw.ellipse([10, 10, 150, 150], outline='WHITE', width=2)
        
        # 添加文字
        draw.text((50, 70), 'GC9D01', fill='YELLOW')
        draw.text((55, 85), 'Test!', fill='GREEN')
        
        # 畫一些圖形
        draw.rectangle([30, 100, 130, 120], outline='RED', width=1)
        draw.ellipse([60, 25, 100, 65], outline='BLUE', width=2)
        
        print("顯示測試圖像...")
        lcd.show_image(image)
        
        # 保持顯示5秒
        time.sleep(5)
        
        # 創建彩色測試圖案
        for i in range(5):
            image = Image.new('RGB', (160, 160), 'BLACK')
            draw = ImageDraw.Draw(image)
            
            colors = ['RED', 'GREEN', 'BLUE', 'YELLOW', 'CYAN']
            
            # 畫彩色圓環
            for j in range(5):
                radius = 20 + j * 15
                draw.ellipse([80-radius, 80-radius, 80+radius, 80+radius], 
                           outline=colors[(i+j)%5], width=3)
            
            draw.text((65, 75), f'Test {i+1}', fill='WHITE')
            
            lcd.show_image(image)
            time.sleep(1)
        
        print("測試完成！")
        
    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        try:
            lcd.cleanup()
        except:
            pass

if __name__ == '__main__':
    main()