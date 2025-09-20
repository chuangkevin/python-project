# Waveshare 0.71寸圓形LCD顯示器

## 硬體規格

- **型號**: Waveshare 0.71inch LCD Module
- **控制器**: GC9D01
- **解析度**: 160x160像素 (圓形顯示)
- **介面**: 4線SPI
- **工作電壓**: 3.3V/5V
- **顏色格式**: RGB565

## 硬體連接

| LCD引腳 | 樹莓派引腳 | GPIO編號 | 說明 |
|---------|------------|----------|------|
| VCC     | 5V         | -        | 電源正極 |
| GND     | Pin 6      | -        | 電源負極 |
| DIN     | Pin 19     | GPIO10   | SPI0_MOSI |
| CLK     | Pin 23     | GPIO11   | SPI0_SCLK |
| CS      | Pin 24     | GPIO8    | SPI0_CE0 |
| DC      | Pin 22     | GPIO25   | 數據/指令控制 |
| RST     | Pin 13     | GPIO27   | 復位 |
| BL      | Pin 12     | GPIO18   | 背光控制 |

## 環境設置

### 1. 啟用SPI
```bash
sudo raspi-config
# 選擇 Interfacing Options -> SPI -> Enable
```

或者手動配置：
```bash
echo "dtparam=spi=on" | sudo tee -a /boot/firmware/config.txt
sudo reboot
```

### 2. 安裝依賴
```bash
sudo apt update
sudo apt install -y python3-spidev python3-pil python3-numpy
```

## 核心驅動程序

### 基礎類別
```python
import spidev
import RPi.GPIO as GPIO
import time

class Waveshare071LCD:
    def __init__(self):
        # GPIO定義
        self.RST_PIN = 27
        self.DC_PIN = 25
        self.BL_PIN = 18
        self.CS_PIN = 8

        # 螢幕尺寸
        self.WIDTH = 160
        self.HEIGHT = 160

        # 初始化GPIO和SPI
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
        self._init_display()

    def _write_cmd(self, cmd):
        GPIO.output(self.DC_PIN, GPIO.LOW)
        GPIO.output(self.CS_PIN, GPIO.LOW)
        self.spi.writebytes([cmd])
        GPIO.output(self.CS_PIN, GPIO.HIGH)

    def _write_data(self, data):
        GPIO.output(self.DC_PIN, GPIO.HIGH)
        GPIO.output(self.CS_PIN, GPIO.LOW)
        if isinstance(data, list):
            self.spi.writebytes(data)
        else:
            self.spi.writebytes([data])
        GPIO.output(self.CS_PIN, GPIO.HIGH)
```

## 關鍵初始化序列 (GC9D01)

```python
def _init_display(self):
    self._reset()

    # 官方初始化序列 - 關鍵步驟
    self._write_cmd(0xFE)
    self._write_cmd(0xEF)

    # 設置0x80-0x8F暫存器為0xFF (重要!)
    for reg in range(0x80, 0x90):
        self._write_cmd(reg)
        self._write_data(0xFF)

    self._write_cmd(0x3A)
    self._write_data(0x05)  # RGB565

    # ... 其他設置 ...

    # 關鍵的MADCTL設置
    self._write_cmd(0x36)
    self._write_data(0x00)  # 必須是0x00而不是0x08!

    self._write_cmd(0x11)  # Sleep Out
    time.sleep(0.2)

    self._write_cmd(0x29)  # Display ON
```

## 顯示功能實現

### 填充顏色
```python
def fill(self, color):
    r, g, b = color
    self.set_window(0, 0, self.WIDTH-1, self.HEIGHT-1)

    rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
    hi = (rgb565 >> 8) & 0xFF
    lo = rgb565 & 0xFF

    for _ in range(self.WIDTH * self.HEIGHT):
        self._write_data([hi, lo])

# 使用例子
lcd = Waveshare071LCD()
lcd.fill((255, 0, 0))  # 紅色
```

### 設置窗口範圍
```python
def set_window(self, x_start, y_start, x_end, y_end):
    self._write_cmd(0x2A)  # Column Address Set
    self._write_data([x_start >> 8, x_start & 0xFF, x_end >> 8, x_end & 0xFF])

    self._write_cmd(0x2B)  # Row Address Set
    self._write_data([y_start >> 8, y_start & 0xFF, y_end >> 8, y_end & 0xFF])

    self._write_cmd(0x2C)  # Memory Write
```

## 故障排除指南

### 常見問題

1. **螢幕顯示條紋**
   - 檢查MADCTL設置為0x00
   - 確認0x80-0x8F暫存器設置為0xFF

2. **顏色顯示異常**
   - 確認使用正確的初始化序列
   - 檢查RGB565格式轉換

3. **背光問題**
   - 檢查背光引腳 (BL引腳)
   - 確認5V電源穩定供應

4. **SPI通訊故障**
   - 確認SPI介面啟用 (`ls /dev/spi*`)
   - 檢查線路連接

### 調試指令
```bash
# 檢查SPI設備
ls -la /dev/spi*

# 檢查GPIO狀態
gpio readall

# 測試螢幕
sudo python3 lcd_test.py
```

## 相關資源

- [Waveshare官方Wiki](https://www.waveshare.net/wiki/0.71inch_LCD_Module)
- [GC9D01數據手冊](https://github.com/waveshare/0.71inch-LCD-Module)
- [樹莓派SPI文檔](https://www.raspberrypi.org/documentation/hardware/raspberrypi/spi/)

## 版本歷史

- **v1.0** - 初始版本，基本螢幕功能
- **v1.1** - 修復顯示問題，優化初始化序列
- **v1.2** - 完善文檔，增加故障排除指南

## 重要備註

- 必須使用官方GC9D01初始化序列
- MADCTL必須設置為0x00
- SPI頻率建議10MHz以下
- 支援5V/3.3V電源供應

---
**特別提醒**: 官方初始化序列中的0x36暫存器設置為0x00是關鍵步驟!