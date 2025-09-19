# analogGauge - Epson RD-1 風格指針錶盤模組

高精度模擬 Epson RD-1 數位相機頂部的四個指針錶盤，提供整合式錶盤渲染和 PyQt 界面。

## 🎯 核心特色

- **像素級精確復刻**：基於真實 RD-1 相機照片精確重現錶盤佈局
- **超流暢動畫**：微步插值動畫系統，支援 120fps 更新
- **整合式顯示**：四個錶盤完美整合在圓形顯示器中
- **高品質渲染**：反鋸齒線條、精細刻度、專業色彩
- **多風格支持**：4種內建風格主題

## 📦 組件架構

### 核心模組
- `rd1_gauge.py` - 核心錶盤渲染引擎
- `circular_screen.py` - PyQt 圓形界面組件（主要UI）
- `manual_control.py` - PyQt 手動控制界面（調試工具）

### 配置與資源
- `styles/` - 風格主題配置文件
- `examples/` - 使用範例（包含 tkinter 示例）
- `sample/` - 範例輸出圖片

## 🚀 快速使用

### 作為獨立組件使用
```bash
# 啟動圓形界面
python -m analogGauge.circular_screen

# 啟動調試控制界面
python -m analogGauge.manual_control

# 生成靜態圖片
python -m analogGauge.run_integrated
```

### 作為模組導入
```python
from analogGauge.rd1_gauge import RD1Gauge
from analogGauge.circular_screen import CircularScreenAPI

# 創建錶盤
gauge = RD1Gauge(style='rd1_classic')
gauge.set_value('SHOTS', 2)
gauge.set_value('BATTERY', 4)

# 渲染圖片
image = gauge.draw()
image.save('output.png')
```

## 🎨 風格主題

- `rd1_classic` - 經典 RD-1 風格
- `mpc15_style` - MPC15 主題
- `specture_dark` - 深色現代風格
- `specture_light` - 淺色現代風格

## 🛠️ 需求

- Python 3.8+
- PyQt5 (`pip install PyQt5`)
- Pillow (`pip install pillow`)

## 📝 API 參考

### RD1Gauge 類

```python
gauge = RD1Gauge(
    width=480,           # 畫布寬度
    height=480,          # 畫布高度
    style='rd1_classic', # 風格主題
    show_labels=True,    # 顯示標籤
    reset_on_start=True  # 啟動重置動畫
)

# 設定指針值
gauge.set_value('SHOTS', value)    # 剩餘拍攝數 (0-5)
gauge.set_value('WB', value)       # 白平衡 (0-5)
gauge.set_value('BATTERY', value)  # 電池電量 (0-4)
gauge.set_value('QUALITY', value)  # 影像品質 (0-2)

# 更新動畫
gauge.update_animation(delta_time)

# 渲染圖片
image = gauge.draw()
```

### CircularScreenAPI 類

```python
from analogGauge.circular_screen import CircularScreenAPI

# 創建界面
api = CircularScreenAPI(config, initial_style='rd1_classic')

# 設定回調
api.set_on_apply(lambda mode, value: print(f'Applied: {mode}={value}'))
api.set_on_action(lambda action, payload: print(f'Action: {action}'))

# 模式控制
api.switch_mode('ev')  # 切換到曝光補償模式
api.handle_left_encoder_rotate(1)   # 左編碼器旋轉
api.handle_right_encoder_rotate(1)  # 右編碼器旋轉
```

## 🔧 整合到其他應用

analogGauge 設計為獨立組件，可輕鬆整合到其他應用中：

```python
# 在 systemControl 中使用
from analogGauge.circular_screen import CircularScreenAPI as AnalogGaugeAPI

class MyApp(AnalogGaugeAPI):
    def __init__(self, config):
        super().__init__(config)
        # 添加自定義功能

    def integrate_with_system(self, system):
        # 系統整合邏輯
        pass
```

## 📈 更新紀錄

### 2025-09-19 - PyQt 升級
- ✅ 從 tkinter 遷移到 PyQt5，提供更好的視覺效果
- ✅ 重構為獨立組件，移除 systemControl 依賴
- ✅ 新增 `manual_control.py` PyQt 版本調試界面
- ✅ 優化圖像渲染，解決 PIL-PyQt 兼容性問題

### 2025-09-17 - 動畫系統優化
- 新增 `Reset on start` 功能與 `Reset` 按鈕
- 調整動畫預設：`animation_rate=5.0`，`_base_step_duration=0.28`
- 啟動動畫約 1.2-1.4 秒完成

## 📄 許可證

此專案為內部開發使用。