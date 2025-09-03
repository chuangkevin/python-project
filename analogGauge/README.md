# Epson RD-1 風格指針錶盤模組

高精度模擬 Epson RD-1 數位相機頂部的四個指針錶盤，提供整合式錶盤渲染和獨立測試UI。

## 🎯 整合式錶盤系統

### 核心特色

- **像素級精確復刻**：基於真實 RD-1 相機照片精確重現錶盤佈局
- **超流暢 120fps 動畫**：微步插值動畫系統，8.3ms 更新間隔
- **整合式顯示**：四個錶盤完美整合在 240x240 圓形顯示器
- **高品質渲染**：反鋸齒線條、精細刻度、專業色彩

### 四個指針錶盤佈局

```text
      [WB]           [QUALITY]
       90°             90°
    (左上角)        (右上角)

           [SHOTS]
            360°
         (中央圓形)

         [BATTERY]
            90°
         (中下方)
```

### 錶盤規格

- **SHOTS (拍攝數)**：360° 圓形錶盤，外圍刻度標示
  - 數值：E → 10 → 20 → 50 → 100 → 500
- **WHITE BALANCE (白平衡)**：90° 扇形錶盤，左上角位置
  - 數值：A(自動) → ☀(晴天) → ⛅(多雲) → ☁(陰天) → 💡(白熾燈) → 💡(螢光燈)
- **BATTERY (電池電量)**：90° 扇形錶盤，中下方位置，向上指向
  - 數值：E(空) → 1/4 → 1/2 → 3/4 → F(滿)
- **QUALITY (影像品質)**：90° 扇形錶盤，右上角位置
  - 數值：R(RAW) → H(高品質JPEG) → N(一般JPEG)

## 🔧 技術架構

### 核心檔案

- **`rd1_gauge.py`** - RD1Gauge 核心類別
  - 整合式錶盤渲染引擎
  - 120fps 微步動畫系統
  - 無 UI 依賴的純圖像生成
- **`test_integrated.py`** - 整合式錶盤完整測試
- **`test_ui.py`** - 傳統 UI 測試介面
- **`requirements.txt`** - 依賴套件清單

### 動畫系統

- **微步插值**：線性插值 + 微步進系統
- **更新頻率**：120fps (8.3ms 間隔)
- **反鋸齒渲染**：多層線條重疊技術
- **流暢度**：支援即時數值變化無卡頓

### 渲染特色

- **像素級精確**：基於真實 RD-1 相機照片測量
- **專業配色**：復古相機風格色彩方案
- **高品質線條**：反鋸齒、多重採樣
- **圓形顯示器最佳化**：240x240 完美適配

## 🚀 快速開始

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 基本使用

```python
from rd1_gauge import RD1Gauge

# 創建整合式錶盤實例
gauge = RD1Gauge()

# 設定數值 (索引方式)
gauge.set_value("SHOTS", 2)    # "20"
gauge.set_value("WB", 1)       # "☀" (晴天)
gauge.set_value("BATTERY", 3)  # "3/4"
gauge.set_value("QUALITY", 1)  # "H" (高品質)

# 更新動畫 (建議 120fps 循環調用)
gauge.update_animation()

# 生成整合錶盤圖像 (主要用法)
img = gauge.draw_integrated_rd1_display()
img.show()  # 或 img.save("rd1_display.png")
```

### 整合式錶盤測試

```bash
# 執行整合式錶盤完整測試
python test_integrated.py

# 執行傳統 UI 測試 (開發/調試用)
python test_ui.py
```

## 📋 API 參考

### RD1Gauge 核心類別

#### 主要方法

- `set_value(gauge_type, value_index)` - 設定指針數值（索引）
- `update_animation()` - 更新動畫狀態（120fps 調用）
- `draw_integrated_rd1_display()` - **生成整合式錶盤圖像**
- `get_gauge_info()` - 取得所有錶盤狀態資訊

#### 錶盤類型常數

- `"SHOTS"` - 剩餘拍攝數錶盤
- `"WB"` - 白平衡錶盤  
- `"BATTERY"` - 電池電量錶盤
- `"QUALITY"` - 影像品質錶盤

## 🔗 整合到主專案

### 在樹莓派相機系統中使用

```python
from analogGauge.rd1_gauge import RD1Gauge
from gc9a01 import GC9A01

# 初始化錶盤和圓形顯示器
gauge = RD1Gauge()
display = GC9A01(port=0, cs=0, dc=25, rst=24)

def update_display_from_camera_state():
    """根據相機狀態更新錶盤顯示"""
    # 取得相機狀態（你的實作）
    shots = get_remaining_shots()    # 0-5 的索引
    wb_mode = get_white_balance()    # 0-5 的索引
    battery = get_battery_level()    # 0-4 的索引
    quality = get_image_quality()    # 0-2 的索引
    
    # 更新錶盤數值
    gauge.set_value("SHOTS", shots)
    gauge.set_value("WB", wb_mode)
    gauge.set_value("BATTERY", battery)
    gauge.set_value("QUALITY", quality)
    
    # 生成並顯示整合式錶盤
    img = gauge.draw_integrated_rd1_display()
    display.display(img)

# 在主迴圈中 120fps 調用
while True:
    gauge.update_animation()  # 流暢動畫
    update_display_from_camera_state()
    time.sleep(1/120)  # 8.3ms 間隔
```

## 📁 檔案結構

```text
analogGauge/
├── rd1_gauge.py           # 核心錶盤渲染引擎
├── test_integrated.py     # 整合式錶盤測試
├── test_ui.py            # 傳統 UI 測試介面
├── requirements.txt      # 依賴套件清單
├── glass_overlay.png     # 玻璃覆蓋層素材
└── README.md            # 技術文檔
```

## ⚙️ 技術規格

- **渲染引擎**: PIL (Pillow) 圖像處理
- **動畫系統**: 120fps 微步插值
- **顯示器支援**: 240x240 圓形 LCD 最佳化
- **輸出格式**: RGB PIL Image 物件
- **相依性**: 最小化依賴，無 UI 框架綁定

## 🛠 開發工具

### 測試程式

- `test_integrated.py` - 專為整合式錶盤設計的完整測試
- `test_ui.py` - 傳統 tkinter UI，適合開發調試

### 除錯建議

1. **動畫不流暢**: 確保 120fps 調用 `update_animation()`
2. **顯示異常**: 檢查 PIL 版本 >= 10.0.0
3. **記憶體問題**: 避免頻繁建立新 RD1Gauge 實例

## 📄 授權

MIT 授權條款 - 詳見專案根目錄 LICENSE 檔案。
