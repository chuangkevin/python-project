# ILI9341 2.4吋螢幕連接指南

## 硬體規格
- **產品**: 微雪2.4吋彩色LCD模組顯示屏
- **型號**: CZ028
- **控制器**: ILI9341
- **解析度**: 240x320 像素
- **介面**: SPI
- **工作電壓**: 3.3V

## 樹莓派GPIO腳位連接

### SPI連接 (必需)

| 螢幕腳位 | 功能說明 | 樹莓派腳位 | GPIO編號 |
|---------|---------|-----------|----------|
| VCC | 電源正極 5V | Pin 2 | 5V |
| GND | 電源地 | Pin 6 | GND |
| CS | 片選信號 | Pin 24 | GPIO8 (CE0) |
| RESET/RST | 重置信號 | Pin 13 | GPIO27 |
| DC/RS | 資料/命令選擇 | Pin 22 | GPIO25 |
| SDI/MOSI | SPI資料輸入 | Pin 19 | GPIO10 (MOSI) |
| SCK | SPI時鐘 | Pin 23 | GPIO11 (SCLK) |
| LED | 背光控制 | Pin 18 | GPIO24 |
| SDO/MISO | SPI資料輸出 | Pin 21 | GPIO9 (MISO) |

### 連接圖示

```
樹莓派 40-Pin GPIO
┌─────────────────────────┐
│ 3.3V  1 ●─────● 2  5V   │
│ GPIO2 3 ●     ● 4  5V   │
│ GPIO3 5 ●     ● 6  GND──┼──> 螢幕 GND
│ GPIO4 7 ●     ● 8  GPIO14│
│ GND   9 ●     ● 10 GPIO15│
│GPIO17 11 ●     ● 12 GPIO18├──> 螢幕 LED (背光)
│GPIO27 13 ●     ● 14 GND  │
│GPIO22 15 ●     ● 16 GPIO23│
│ 3.3V  17 ●─────● 18 GPIO24├──> 螢幕 DC/RS
│GPIO10 19 ●─────● 20 GND  │──> 螢幕 MOSI
│ GPIO9 21 ●─────● 22 GPIO25├──> 螢幕 MISO
│GPIO11 23 ●─────● 24 GPIO8 │──> 螢幕 SCK & CS
│ GND   25 ●     ● 26 GPIO7 │
└─────────────────────────┘
     ↑               ↑
螢幕 VCC         螢幕 RESET
```

## 連接步驟

### 1. 準備工作
- 關閉樹莓派電源
- 準備杜邦線（母對母）約8-10條
- 確認螢幕模組腳位標示

### 2. 連接電源
```bash
螢幕 VCC → 樹莓派 Pin 1 (3.3V)
螢幕 GND → 樹莓派 Pin 6 (GND)
```
⚠️ **注意**: 必須使用3.3V，不可使用5V！

### 3. 連接SPI通訊線
```bash
螢幕 SCK → 樹莓派 Pin 23 (GPIO11/SCLK)
螢幕 MOSI → 樹莓派 Pin 19 (GPIO10/MOSI)
螢幕 MISO → 樹莓派 Pin 21 (GPIO9/MISO) [可選]
螢幕 CS → 樹莓派 Pin 24 (GPIO8/CE0)
```

### 4. 連接控制線
```bash
螢幕 DC/RS → 樹莓派 Pin 18 (GPIO24)
螢幕 RESET → 樹莓派 Pin 22 (GPIO25)
螢幕 LED → 樹莓派 Pin 12 (GPIO18)
```

## 軟體設定

### 1. 啟用SPI介面
```bash
sudo raspi-config
# 選擇 Interface Options → SPI → Yes
```

或使用命令列：
```bash
sudo raspi-config nonint do_spi 0
```

### 2. 檢查SPI設備
```bash
ls -l /dev/spi*
# 應該看到 /dev/spidev0.0 和 /dev/spidev0.1
```

### 3. 安裝依賴套件
```bash
sudo apt-get update
sudo apt-get install -y python3-spidev python3-rpi.gpio python3-pil
```

### 4. 測試連接
```bash
cd /home/pi/python-project/mainCamera/display
python3 ili9341_setup.py
```

## 故障排除

### 問題1: 螢幕無顯示
- 檢查電源連接（VCC和GND）
- 確認背光是否亮起（LED腳位）
- 測量VCC電壓是否為3.3V

### 問題2: 顯示亂碼或顏色異常
- 檢查SPI連接是否正確
- 降低SPI速度：
  ```python
  self.spi.max_speed_hz = 20000000  # 改為20MHz
  ```

### 問題3: /dev/spidev0.0 不存在
- 確認SPI已啟用：
  ```bash
  sudo raspi-config nonint do_spi 0
  sudo reboot
  ```

### 問題4: Permission denied錯誤
- 將用戶加入spi群組：
  ```bash
  sudo usermod -a -G spi,gpio $USER
  logout  # 重新登入
  ```

## 性能優化

### 1. 提高SPI速度
預設40MHz，可嘗試提高至64MHz：
```python
self.spi.max_speed_hz = 64000000
```

### 2. 增加SPI緩衝區
編輯 `/boot/config.txt`：
```bash
dtparam=spidev.bufsiz=65536
```

### 3. 使用硬體加速
如果支援，可使用DMA傳輸：
```python
# 在初始化時設定
self.spi.no_cs = True
self.spi.max_speed_hz = 80000000
```

## 整合到相機專案

### 與CM4擴展板連接
如果使用CM4-NANO擴展板，SPI腳位可能不同，請參考擴展板手冊。

### 多螢幕配置
本專案使用雙螢幕配置：
1. **主螢幕** (2.4吋): SPI0.0 - Live View顯示
2. **副螢幕** (0.71吋圓形): SPI0.1 - 指針錶盤顯示

確保CS腳位不同：
- 主螢幕: GPIO8 (CE0)
- 副螢幕: GPIO7 (CE1)

## 參考資源
- [ILI9341 Datasheet](https://www.displayfuture.com/Display/datasheet/controller/ILI9341.pdf)
- [樹莓派GPIO腳位圖](https://pinout.xyz/)
- [微雪Wiki](https://www.waveshare.net/)
