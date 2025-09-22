# RD-1 雙螢幕相機系統
## 超流暢雙螢幕顯示解決方案

這是專為 RD-1 相機設計的高效能雙螢幕系統，提供：
- **主螢幕 (2.4吋)**: 30fps 超流暢相機預覽
- **圓形螢幕 (0.71吋)**: 10fps analogGauge 錶盤顯示

## 📁 檔案結構

```
mainCode/
├── dual_screen_manager.py         # 🚀 雙螢幕核心渲染引擎
├── camera_preview_optimizer.py    # 📹 相機預覽超級優化器
├── analog_gauge_integration.py    # 🎛️ AnalogGauge 錶盤整合器
├── rd1_camera_system.py          # 🎬 主控制系統 (主入口)
└── README.md                      # 📖 使用說明 (本檔案)
```

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install opencv-python pillow numpy PyQt5
```

### 2. 硬體配置確認

確保你的硬體配置符合以下規格：
- **主螢幕 (ILI9341)**: SPI0.0, CS=GPIO8, 240x320像素
- **圓形螢幕 (GC9D01)**: SPI0.1, CS=GPIO7, 160x160像素
- **共用接線**: 5V, GND, SCLK, MOSI

### 3. 基本使用

#### 方法一：一鍵啟動完整系統（推薦）

```bash
cd D:\Projects\python-project\mainCamera\display\LcdIntegrate\mainCode
python rd1_camera_system.py
```

**控制說明：**
```
Enter - 拍照
f     - 切換軟片模擬 (PROVIA→VELVIA→ASTIA...)
m     - 切換相機模式 (auto→manual→aperture_priority...)
+     - 增加曝光補償 (+0.3 EV)
-     - 減少曝光補償 (-0.3 EV)
s     - 顯示系統統計
q     - 退出系統
```

#### 方法二：程式整合使用

```python
import sys
sys.path.append('D:/Projects/python-project/mainCamera/display/LcdIntegrate/mainCode')

from rd1_camera_system import start_rd1_camera, stop_rd1_camera

# 啟動完整系統
camera_system = start_rd1_camera()

# 使用相機功能
filename = camera_system.capture_photo()              # 拍照
camera_system.cycle_film_simulation()                 # 切換軟片
camera_system.adjust_ev_compensation(1)               # +0.3 EV
camera_system.cycle_camera_mode()                     # 切換模式

# 獲取系統狀態
stats = camera_system.get_system_stats()
print(f"當前FPS: {stats['preview']['fps']}")
print(f"軟片模擬: {stats['camera_state']['film_simulation']}")

# 停止系統
stop_rd1_camera()
```

## 🔧 進階使用

### 只使用雙螢幕渲染器

```python
from dual_screen_manager import start_dual_screen_system, stop_dual_screen_system
import numpy as np

# 啟動雙螢幕渲染器
renderer = start_dual_screen_system()

# 發送圖像到主螢幕 (240x320)
main_image = np.random.randint(0, 255, (320, 240, 3), dtype=np.uint8)
renderer.render_main_screen(main_image)

# 發送圖像到圓形螢幕 (160x160)
gauge_image = np.random.randint(0, 255, (160, 160, 3), dtype=np.uint8)
renderer.render_gauge_screen(gauge_image)

# 停止系統
stop_dual_screen_system()
```

### 只使用相機預覽優化器

```python
from dual_screen_manager import start_dual_screen_system
from camera_preview_optimizer import CameraPreviewOptimizer, PreviewQuality

# 啟動渲染器
renderer = start_dual_screen_system()

# 啟動相機預覽
preview = CameraPreviewOptimizer(renderer)
preview.start_preview()

# 調整預覽品質
preview.set_quality(PreviewQuality.HIGH)        # 高品質 (320x240)
preview.set_quality(PreviewQuality.ULTRA_LOW)   # 極低品質 (80x60, 最高FPS)

# 啟用零延遲模式
preview.enable_zero_latency(True)

# 獲取統計
stats = preview.get_preview_stats()
print(f"當前FPS: {stats['fps']}")
print(f"品質: {stats['quality']}")

# 停止預覽
preview.stop_preview()
```

### 只使用 AnalogGauge 控制器

```python
from dual_screen_manager import start_dual_screen_system
from analog_gauge_integration import AnalogGaugeController

# 啟動渲染器
renderer = start_dual_screen_system()

# 啟動錶盤控制器
gauge = AnalogGaugeController(renderer)
gauge.start()

# 控制錶盤
gauge.cycle_mode()                    # 循環模式 (EV→ISO→快門→白平衡→品質)
gauge.adjust_value(3)                 # 向上調整3步
gauge.adjust_value(-2)                # 向下調整2步
gauge.reset_to_default()              # 重置到預設 (EV 0.0)

# 更新系統狀態
gauge.update_system_state(
    battery=3,    # 電池電量 (0-4)
    shots=2       # 剩餘拍攝數等級 (0-5)
)

# 獲取當前狀態
state = gauge.get_current_state()
print(f"當前模式: {state['mode']}")
print(f"當前數值索引: {state['value_index']}")

# 停止控制器
gauge.stop()
```

## 🎯 系統特性

### 效能優化
- **雙緩衝**: 防止畫面撕裂
- **多線程**: 兩個螢幕獨立渲染
- **自適應品質**: 根據FPS自動調整解析度
- **硬體加速**: OpenCV CLAHE 對比度增強
- **零延遲模式**: 專為即時預覽設計

### 軟片模擬整合
支援 16 種 Fujifilm 軟片預設：
- **彩色**: PROVIA, VELVIA, ASTIA, CLASSIC_CHROME, REALA_ACE, PRO_NEG_HI, PRO_NEG_STD, CLASSIC_NEG
- **電影**: ETERNA, ETERNA_BLEACH_BYPASS
- **黑白**: MONOCHROME, ACROS
- **復古**: Nostalgic_Neg, Sepia
- **其他**: KODACHROME_64, REDSCALE

### AnalogGauge 支援
- **模式切換**: EV, ISO, 快門速度, 白平衡, 影像品質
- **編碼器控制**: 旋轉調整數值, 按壓重置
- **狀態同步**: 電池電量, 剩餘拍攝數
- **圓形顯示**: 完美適配 0.71吋 圓形螢幕

## 📊 效能指標

### 目標效能
- **主螢幕**: 30fps 穩定輸出
- **圓形螢幕**: 10fps 節能更新
- **延遲**: < 33ms (一幀時間)
- **CPU使用率**: < 50% (Raspberry Pi 4)

### 自適應品質等級
| 品質等級 | 解析度 | 適用場景 |
|---------|-------|----------|
| ULTRA_LOW | 80x60 | 極高FPS要求 |
| LOW | 160x120 | 一般預覽 |
| MEDIUM | 240x180 | 平衡品質/效能 |
| HIGH | 320x240 | 高品質預覽 |
| ULTRA_HIGH | 480x360 | 最佳品質 |

## 🔧 故障排除

### 常見問題

**1. 顯示器無法初始化**
```bash
# 檢查SPI是否啟用
sudo raspi-config
# Interface Options → SPI → Enable

# 檢查接線
# 主螢幕: SPI0.0, CS=GPIO8
# 圓形螢幕: SPI0.1, CS=GPIO7
```

**2. FPS過低**
```python
# 降低預覽品質
preview.set_quality(PreviewQuality.LOW)

# 啟用零延遲模式
preview.enable_zero_latency(True)

# 檢查系統負載
stats = camera_system.get_system_stats()
print(stats['renderer']['dropped_frames'])
```

**3. AnalogGauge 顯示異常**
```python
# 檢查模組載入
from analog_gauge_integration import ANALOG_GAUGE_AVAILABLE
print(f"AnalogGauge 可用: {ANALOG_GAUGE_AVAILABLE}")

# 重新初始化
gauge.stop()
gauge.start()
```

**4. 軟片模擬不可用**
```bash
# 檢查軟片模擬路徑
ls D:/Projects/python-project/mainCamera/filter/preset/systemPreset/

# 確認預設檔案存在
python -c "from preset_manager import FilmPresetManager; m=FilmPresetManager(); print(len(m.list_presets()))"
```

## 🎮 硬體整合

### GPIO 按鈕控制
```python
import RPi.GPIO as GPIO

# 設置按鈕
SHUTTER_BUTTON = 21
MODE_BUTTON = 20
ENCODER_A = 22
ENCODER_B = 23

def setup_buttons():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SHUTTER_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(MODE_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # 按鈕回調
    GPIO.add_event_detect(SHUTTER_BUTTON, GPIO.FALLING,
                         callback=lambda ch: camera_system.capture_photo(),
                         bouncetime=300)

    GPIO.add_event_detect(MODE_BUTTON, GPIO.FALLING,
                         callback=lambda ch: camera_system.cycle_camera_mode(),
                         bouncetime=300)

# 旋轉編碼器
def setup_encoder():
    GPIO.setup(ENCODER_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ENCODER_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def encoder_callback(channel):
        if GPIO.input(ENCODER_A) == GPIO.input(ENCODER_B):
            camera_system.adjust_ev_compensation(1)
        else:
            camera_system.adjust_ev_compensation(-1)

    GPIO.add_event_detect(ENCODER_A, GPIO.BOTH, callback=encoder_callback)
```

## 📈 系統監控

### 即時統計查看
```python
import time

def monitor_system(camera_system):
    while True:
        stats = camera_system.get_system_stats()

        print(f"\r主螢幕FPS: {stats['preview']['fps']:6.1f} | "
              f"丟幀: {stats['renderer']['dropped_frames']:4d} | "
              f"電池: {stats['camera_state']['battery_level']:3d}% | "
              f"軟片: {stats['camera_state']['film_simulation']:12s}",
              end="", flush=True)

        time.sleep(1)

# 在背景運行監控
import threading
monitor_thread = threading.Thread(target=monitor_system, args=(camera_system,), daemon=True)
monitor_thread.start()
```

## 🔗 相關連結

- [AnalogGauge 原始專案](D:/Projects/python-project/analogGauge/)
- [軟片模擬預設庫](D:/Projects/python-project/mainCamera/filter/preset/)
- [硬體驅動](D:/Projects/python-project/mainCamera/display/LcdIntegrate/)

---

## 🖥️ Windows 模擬器模式

如果你沒有實體螢幕，可以在 Windows 環境下使用模擬器：

### 快速啟動模擬器
```bash
cd D:\Projects\python-project\mainCamera\display\LcdIntegrate\mainCode
python start_simulator.py
```

### 選擇模式：
1. **完整系統 + 模擬器** - 完整的相機功能 + 視覺化窗口
2. **純模擬器演示** - 只顯示雙螢幕效果

### 模擬器特性：
- 🖼️ **主螢幕窗口**: 480x640 顯示相機預覽 (模擬 2.4吋螢幕)
- 🎛️ **圓形螢幕窗口**: 320x320 顯示 AnalogGauge (模擬 0.71吋圓形螢幕)
- 📊 **即時統計**: 顯示 FPS、幀數等效能指標
- 🎮 **完整控制**: 支援所有相機功能 (拍照、軟片切換、曝光調整等)

### 模擬器控制：
- 在命令行使用標準控制 (f, m, +, -, s, q)
- 在任一模擬器窗口按 `q` 也可退出
- 窗口可拖動和調整位置

---

💡 **提示**:
- 實體硬體: `python rd1_camera_system.py`
- Windows 模擬器: `python start_simulator.py`