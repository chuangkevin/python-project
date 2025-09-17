# analogGauge# Epson RD-1 風格指針錶盤模組



簡要：本目錄包含 RD1-style 模擬儀表核心 (`rd1_gauge.py`)、一個靜態 runner (`run_integrated.py`) 與一個手動控制 GUI (`manual_control.py`)。glass overlay 已停用，舊資源被移到 `../archive/analogGauge_backup_*`。高精度模擬 Epson RD-1 數位相機頂部的四個指針錶盤，提供整合式錶盤渲染和獨立測試UI。


## 更新紀錄 (最近)

- 2025-09-17: 新增 `Reset on start` 勾選與 `Reset` 按鈕到 `manual_control.py`，可由 UI 或程式呼叫 `RD1Gauge.reset()` 觸發從最大值回歸到最小值的啟動動畫。
- 2025-09-17: 調整動畫預設以獲得更自然的指針移動：`animation_rate` 預設調為 `5.0`，`_base_step_duration` 調為 `0.28`，啟動（max→min）動畫約 1.2–1.4 秒完成（視距離而定）。



## 需求## 🎯 整合式錶盤系統

- Python 3.8+

- Pillow (`pip install pillow`)### 核心特色

- Tkinter（Windows 預裝；Linux/macOS 需另行安裝系統套件）

- **像素級精確復刻**：基於真實 RD-1 相機照片精確重現錶盤佈局

## 快速使用- **超流暢 120fps 動畫**：微步插值動畫系統，8.3ms 更新間隔

- 生成靜態整合影像（runner）：- **整合式顯示**：四個錶盤完美整合在 240x240 圓形顯示器

  - 在專案根目錄或任意位置執行：- **高品質渲染**：反鋸齒線條、精細刻度、專業色彩

    ```

    python d:\Projects\python-project\analogGauge\run_integrated.py### 四個指針錶盤佈局

    ```

  - 會在 `analogGauge/` 產生 `integrated_output.png`。```text

      [WB]           [QUALITY]

- 啟動手動控制 GUI（推薦以 module 模式執行）：       90°             90°

  - 在專案根目錄執行：    (左上角)        (右上角)

    ```

    python -m analogGauge.manual_control           [SHOTS]

    ```            360°

  - 或在 `analogGauge` 目錄執行：         (中央圓形)

    ```

    python .\manual_control.py         [BATTERY]

    ```            90°

  - GUI 提供滑桿調整 SHOTS/WB/BATTERY/QUALITY 與儲存影像功能。         (中下方)

```

## 程式化 API 範例

```python### 錶盤規格

from analogGauge.rd1_gauge import RD1Gauge

- **SHOTS (拍攝數)**：360° 圓形錶盤，外圍刻度標示

g = RD1Gauge(width=800, height=400)  - 數值：E → 10 → 20 → 50 → 100 → 500

g.set_shots(0.5)          # 範例：設定數值- **WHITE BALANCE (白平衡)**：90° 扇形錶盤，左上角位置

g.set_white_balance(0.3)  - 數值：A(自動) → ☀(晴天) → ⛅(多雲) → ☁(陰天) → 💡(白熾燈) → 💡(螢光燈)

for _ in range(10):- **BATTERY (電池電量)**：90° 扇形錶盤，中下方位置，向上指向

    g.update_animation()  # 平滑過渡/更新內部狀態  - 數值：E(空) → 1/4 → 1/2 → 3/4 → F(滿)

img = g.draw_integrated_rd1_display()- **QUALITY (影像品質)**：90° 扇形錶盤，右上角位置

img.save("example_output.png")  - 數值：R(RAW) → H(高品質JPEG) → N(一般JPEG)

```

## 🔧 技術架構

## Archive / 還原

- 舊的 glass overlay 與生成器已移到：### 核心檔案

  `D:\Projects\python-project\archive\analogGauge_backup_<timestamp>\`

- 若需要還原某檔案，請複製回 `analogGauge/`。若需要，我可以幫你還原並 commit。- **`rd1_gauge.py`** - RD1Gauge 核心類別

  - 整合式錶盤渲染引擎

## 注意事項  - 120fps 微步動畫系統

- 若在 headless 或 CI 環境執行 GUI，會失敗（沒有圖形環境）。請使用 runner 或程式化 API 以產生影像。  - 無 UI 依賴的純圖像生成

- 若在不同工作目錄執行時發生 import 錯誤，請使用 `python -m analogGauge.manual_control` 或確保父目錄在 `PYTHONPATH` 中。- **`test_integrated.py`** - 整合式錶盤完整測試

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

## 範例：Windows toy (使用 analogGauge)

在 `analogGauge/examples/windows_toy/` 中放了一個簡單的 Windows toy 範例，示範如何把 `RD1Gauge` 用在即時系統監控中（使用 `psutil`）。

執行方式（套件模式，推薦）：

```
python -m analogGauge.examples.windows_toy.monitor_ui
```

或在 `analogGauge/examples/windows_toy/` 目錄直接執行：

```
python .\monitor_ui.py
```

注意：此範例需要 `psutil` 與 `Pillow` 已安裝，請先執行：

```
pip install psutil pillow
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
