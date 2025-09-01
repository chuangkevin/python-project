# Epson RD-1 風格指針錶盤模組

模擬 Epson RD-1 數位相機頂部的四個指針錶盤，提供獨立的指針模組和測試UI。

## 功能特色

### 四個指針錶盤
- **剩餘拍攝數** (`SHOTS`): E → 10 → 20 → 50 → 100 → 500
- **白平衡** (`WB`): A(自動) → ☀(晴天) → ⛅(多雲) → ☁(陰天) → 💡(白熾燈) → 💡(螢光燈)
- **電池電量** (`BATTERY`): E(空) → 1/4 → 1/2 → 3/4 → F(滿)
- **影像品質** (`QUALITY`): R(RAW) → H(高品質JPEG) → N(一般JPEG)

### 核心模組 (`rd1_gauge.py`)
- 獨立的指針邏輯，無UI依賴
- 支援單個指針和多指針布局
- 可程式化控制指針數值
- 支援圖像輸出（PNG）

### 測試UI (`test_ui.py`)
- 圖形化測試介面
- 即時指針預覽
- 滑桿和按鈕控制
- 批量操作和動畫演示
- 圖像保存功能

## 安裝需求

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 獨立模組使用

```python
from rd1_gauge import RD1Gauge

# 創建指針實例
gauge = RD1Gauge(width=240, height=240)

# 設置指針數值
gauge.set_value("SHOTS", 3)    # 指向 "50"
gauge.set_value("WB", 1)       # 指向 "☀"
gauge.set_value("BATTERY", 4)  # 指向 "F"
gauge.set_value("QUALITY", 0)  # 指向 "R"

# 繪製單個指針
img = gauge.draw_gauge("SHOTS")
img.save("shots_gauge.png")

# 繪製所有指針（2x2布局）
all_img = gauge.draw_all_gauges("2x2")
all_img.save("all_gauges.png")

# 獲取當前狀態
info = gauge.get_gauge_info()
print(f"剩餘拍攝數: {info['SHOTS']['current_value']}")
```

### 2. 測試UI使用

```bash
python test_ui.py
```

#### UI功能說明:
- **指針類型選擇**: 選擇要調整的指針
- **數值調整**: 滑桿或下拉選單調整數值
- **按鈕控制**: 上一個/下一個/重置
- **即時預覽**: 單個指針和全部指針預覽
- **批量操作**: 全部重置/隨機設置/演示動畫
- **圖像保存**: 保存當前指針狀態為PNG

## API 文檔

### RD1Gauge 類別

#### 初始化
```python
RD1Gauge(width=240, height=240)
```

#### 主要方法
- `set_value(gauge_type, value)`: 設置指針數值
- `get_value(gauge_type)`: 獲取當前指針數值  
- `draw_gauge(gauge_type)`: 繪製單個指針錶盤
- `draw_all_gauges(layout)`: 繪製所有指針（布局: "2x2", "1x4", "4x1"）
- `get_gauge_info()`: 獲取所有指針狀態信息

#### 指針類型
- `"SHOTS"`: 剩餘拍攝數
- `"WB"`: 白平衡
- `"BATTERY"`: 電池電量
- `"QUALITY"`: 影像品質

## 整合到樹莓派項目

將此模組整合到主項目的圓形LCD顯示:

```python
from analogGauge.rd1_gauge import RD1Gauge

# 在 dual_display_cam.py 中
gauge = RD1Gauge(width=240, height=240)

def update_gauge_from_camera(picam2):
    # 根據相機狀態更新指針
    shots_remaining = get_shots_remaining()  # 你的邏輯
    battery_level = get_battery_level()      # 你的邏輯
    
    gauge.set_value("SHOTS", shots_remaining)
    gauge.set_value("BATTERY", battery_level)
    
    return gauge.draw_gauge("SHOTS")  # 或其他指針
```

## 文件結構

```
analogGauge/
├── rd1_gauge.py     # 核心指針模組
├── test_ui.py       # 測試UI
├── requirements.txt # 依賴套件
└── README.md       # 說明文檔
```

## 技術細節

- **圖像庫**: PIL (Pillow)
- **UI框架**: tkinter (測試用)
- **指針渲染**: 基於三角函數的向量計算
- **更新頻率**: 100ms (測試UI)
- **輸出格式**: RGB PNG 圖像

## 擴展功能

### 自訂指針配置
可以修改 `GAUGE_CONFIGS` 來自訂指針:

```python
GAUGE_CONFIGS = {
    "CUSTOM": {
        "name": "自訂指針",
        "values": ["Min", "Mid", "Max"],
        "color": (255, 255, 0)  # 黃色指針
    }
}
```

### 不同布局支援
- `"2x2"`: 2x2 網格布局
- `"1x4"`: 橫向排列  
- `"4x1"`: 縱向排列

## 故障排除

1. **圖像顯示問題**: 確保安裝 Pillow >= 10.0.0
2. **UI響應緩慢**: 調整 `time.sleep(0.1)` 更新間隔
3. **字體顯示異常**: 系統需支援中文字體

## 授權

此項目為開源項目，遵循 MIT 授權條款。