# 雙螢幕整合系統

## 硬體配置

本專案使用雙螢幕配置：
- **主螢幕**: 2.4吋 ILI9341 (240x320) - Live View顯示
- **副螢幕**: 0.71吋圓形 GC9D01 (160x160) - 指針錶盤顯示

## 接線配置

### 電源共用
```
樹莓派 5V (Pin 2) ──┬── 主螢幕 VCC
                   └── 圓形螢幕 VCC

樹莓派 GND (Pin 6) ──┬── 主螢幕 GND
                    └── 圓形螢幕 GND
```

### 主螢幕 (2.4吋 ILI9341) - SPI0_CE0

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

### 副螢幕 (0.71吋圓形 GC9D01) - SPI0_CE1

| 螢幕腳位 | 功能說明 | 樹莓派腳位 | GPIO編號 |
|---------|---------|-----------|----------|
| VCC | 電源正極 5V | Pin 2 | 5V (共用) |
| GND | 電源地 | Pin 6 | GND (共用) |
| CLK | SPI時鐘 | Pin 23 | GPIO11 (SCLK) (共用) |
| DIN | SPI資料輸入 | Pin 19 | GPIO10 (MOSI) (共用) |
| CS | 片選信號 | Pin 26 | GPIO7 (CE1) |
| DC | 資料/命令選擇 | Pin 15 | GPIO22 |
| RST | 重置信號 | Pin 11 | GPIO17 |
| BL | 背光控制 | Pin 16 | GPIO23 |

## 接線圖

```
樹莓派 40-Pin GPIO                      主螢幕 (2.4吋)    圓形螢幕 (0.71吋)
┌─────────────────────────┐
│ 3.3V  1 ●     ● 2  5V   │─────────────── VCC ────────── VCC
│ GPIO2 3 ●     ● 4  5V   │
│ GPIO3 5 ●     ● 6  GND  │─────────────── GND ────────── GND
│ GPIO4 7 ●     ● 8  GPIO14│
│ GND   9 ●     ● 10 GPIO15│
│GPIO17 11 ●    ● 12 GPIO18│
│GPIO27 13 ●    ● 14 GND  │
│GPIO22 15 ●    ● 16 GPIO23│──────────────────────────── BL
│ 3.3V  17 ●    ● 18 GPIO24│─────────── LED
│GPIO10 19 ●    ● 20 GND  │─── MOSI ──── DIN
│ GPIO9 21 ●    ● 22 GPIO25│─── MISO ──── DC
│GPIO11 23 ●    ● 24 GPIO8 │─── SCLK ──── CLK ──── CS
│ GND   25 ●    ● 26 GPIO7 │──────────────────── CS
└─────────────────────────┘
          │         │
     RST ─┘    DC ──┘
```

## SPI設備分配

- **SPI0.0** (CE0): 主螢幕 - GPIO8
- **SPI0.1** (CE1): 圓形螢幕 - GPIO7

## 軟體設定

### 1. 啟用SPI介面
```bash
sudo raspi-config nonint do_spi 0
sudo reboot
```

### 2. 檢查SPI設備
```bash
ls -l /dev/spi*
# 應該看到:
# /dev/spidev0.0 - 主螢幕
# /dev/spidev0.1 - 圓形螢幕
```

### 3. 安裝依賴套件
```bash
sudo apt-get update
sudo apt-get install -y python3-spidev python3-rpi.gpio python3-pil python3-numpy
```

## 程式架構

```
LcdIntegrate/
├── readme.md              # 本文件
├── dual_display.py        # 主控制器
├── ili9341_driver.py      # 主螢幕驅動
├── gc9d01_driver.py       # 圓形螢幕驅動
├── display_manager.py     # 顯示管理器
└── tests/
    ├── test_main_lcd.py   # 主螢幕測試
    ├── test_round_lcd.py  # 圓形螢幕測試
    └── test_dual.py       # 雙螢幕測試
```

## 使用範例

```python
from dual_display import DualDisplayManager

# 初始化雙螢幕
display = DualDisplayManager()

# 主螢幕顯示影像
display.main_screen.show_image("live_view.jpg")

# 圓形螢幕顯示指針錶盤
display.round_screen.show_gauge(value=75, max_value=100)

# 同步更新
display.update_all()
```

## 故障排除

### 常見問題
1. **螢幕衝突**: 確認CS腳位不同 (GPIO8 vs GPIO7)
2. **SPI通訊失敗**: 檢查GND是否共用
3. **電源不足**: 確認5V供電穩定

### 調試命令
```bash
# 檢查GPIO狀態
gpio readall

# 測試SPI通訊
python3 tests/test_dual.py

# 查看系統日志
dmesg | grep spi
```

## 性能考量

- **SPI速度**: 主螢幕40MHz，圓形螢幕10MHz
- **更新頻率**: 建議主螢幕30fps，圓形螢幕5fps
- **記憶體使用**: 預估2MB緩衝區

## 版本資訊

- **v1.0**: 初始雙螢幕整合版本
- 支援樹莓派CM4
- 相容Python 3.7+