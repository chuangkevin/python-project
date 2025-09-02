# 🎬 Fujifilm 軟片模擬系統

## 專案概述

這個軟片模擬系統為您的 Raspberry Pi 雙螢幕相機專案 (RD-1 Style) 提供了完整的 Fujifilm 軟片模擬功能。基於 Reddit 社群分享的 Fujifilm 官方資料，實現了 11 種經典軟片效果。

## 🎯 支援的軟片模擬

### 彩色軟片
1. **PROVIA** (STD) - 標準專業反轉片，平衡自然色彩
2. **Velvia** (VIV) - 高飽和度風景片，鮮豔銳利色彩
3. **ASTIA** (AST) - 人像柔和片，優秀膚色表現
4. **Classic Chrome** (CHR) - 20世紀雜誌風格，低飽和度硬調
5. **Classic Negative** (NEG) - SUPERIA底片風格，立體感強
6. **ETERNA** (ETN) - 電影膠片風格，抑制飽和度
7. **Nostalgic Negative** - 復古相冊風格，琥珀色高光
8. **REALA ACE** - 中性色彩高對比，適合所有主題

### 黑白軟片
9. **ACROS** (ACR) - 細緻黑白片，豐富陰影細節
10. **Monochrome** (B&W) - 標準黑白轉換
11. **Sepia** (SEP) - 復古棕褐色，懷舊氛圍

## 📁 檔案結構

```
mainCamera/filter/
├── film_simulation.py      # 核心軟片模擬引擎
├── film_simulation_demo.py # 測試與示範程式
├── rd1_integration.py      # RD-1 系統整合模組
├── requirements.txt        # 相依套件清單
└── README.md              # 說明文件 (本檔案)
```

## 🚀 快速開始

### 1. 安裝相依套件

```bash
cd mainCamera/filter
pip install -r requirements.txt
```

### 2. 基本使用

```python
from rd1_integration import RD1CameraIntegration

# 建立相機整合系統
camera = RD1CameraIntegration()

# 切換軟片模擬
current_sim = camera.cycle_film_simulation("next")
print(f"當前軟片: {current_sim['name']}")

# 取得錶盤顯示值
gauge_value = camera.get_rd1_gauge_value()
print(f"錶盤顯示: {gauge_value}")

# 拍照並套用軟片模擬
# output_path = camera.take_photo_with_simulation(image_data)
```

### 3. 與 RD-1 錶盤系統整合

在您的 `rd1_gauge.py` 中加入軟片模擬錶盤：

```python
from mainCamera.filter.rd1_integration import RD1CameraIntegration

# 建立軟片模擬系統
camera_system = RD1CameraIntegration()

# 加入軟片錶盤到現有的 gauges 列表
film_gauge = {
    "name": "FILM",
    "label": "軟片模擬",
    "values": camera_system.update_rd1_gauge_values()
}

# 將 film_gauge 加入到您的 gauges 列表中
gauges.append(film_gauge)
```

## 🧪 測試與示範

### 1. 互動式測試

```bash
python film_simulation_demo.py
```

### 2. 命令列模式

```bash
# 列出所有軟片模擬
python film_simulation_demo.py list

# 處理單張圖像
python film_simulation_demo.py single -i input.jpg -o output_dir

# 建立比較圖
python film_simulation_demo.py comparison -i input.jpg -o comparison.jpg

# 即時預覽
python film_simulation_demo.py preview

# 批次處理
python film_simulation_demo.py batch -i input_dir -o output_dir
```

### 3. 整合示範

```bash
python rd1_integration.py
```

## 🔧 系統整合

### 與相機主程式整合

1. **引入模組**
```python
from mainCamera.filter.rd1_integration import RD1CameraIntegration
```

2. **初始化系統**
```python
camera_with_film = RD1CameraIntegration()
```

3. **按鈕控制軟片切換**
```python
# 在旋轉編碼器或按鈕事件中
def on_film_button_press():
    current_sim = camera_with_film.cycle_film_simulation("next")
    update_film_gauge_display(current_sim['icon'])
```

4. **拍照時套用軟片模擬**
```python
def capture_photo():
    # 取得相機圖像
    image = capture_from_camera()
    
    # 套用軟片模擬並儲存
    saved_path = camera_with_film.take_photo_with_simulation(
        image, 
        metadata={"iso": 400, "aperture": "f/2.8", "shutter": "1/60"}
    )
    
    return saved_path
```

### 錶盤顯示整合

將軟片模擬加入 RD-1 四個錶盤系統：

```python
# 在 rd1_gauge.py 中修改 gauges 列表
gauges = [
    {"name": "SHOTS", "label": "剩餘拍攝數", "values": ["E", "10", "20", "50", "100", "500"]},
    {"name": "WB", "label": "白平衡", "values": ["A", "☀", "⛅", "☁", "💡", "💡"]},
    {"name": "BATTERY", "label": "電池電量", "values": ["E", "1/4", "1/2", "3/4", "F"]},
    {"name": "FILM", "label": "軟片模擬", "values": ["STD", "VIV", "AST", "CHR", "NEG", "ETN", "ACR", "B&W", "SEP"]}
]
```

## 📊 軟片模擬效果說明

### 技術實現

每種軟片模擬都基於真實 Fujifilm 相機的特性實現：

- **色調曲線調整**: 模擬不同軟片的亮度響應
- **色彩分級**: 實現陰影/高光的色彩偏移
- **飽和度控制**: 精確控制色彩飽和度
- **對比度調整**: 模擬軟片的對比特性
- **Gamma校正**: 調整中間調表現

### 使用建議

| 軟片類型 | 適用場景 | 特色 |
|---------|---------|------|
| PROVIA | 日常拍攝、人像 | 自然平衡的色彩 |
| Velvia | 風景攝影 | 鮮豔的天空和綠色 |
| ASTIA | 人像攝影 | 優秀的膚色表現 |
| Classic Chrome | 街拍、紀實 | 低飽和度復古感 |
| ETERNA | 錄影、電影感 | 電影級色彩表現 |
| ACROS | 藝術創作 | 細緻的黑白表現 |

## 🛠 進階設定

### 自訂軟片模擬

您可以在 `film_simulation.py` 中新增自己的軟片模擬：

```python
def _custom_film(self, img: np.ndarray) -> np.ndarray:
    """自訂軟片模擬"""
    # 實現您的效果
    result = self._saturation_adjust(img, 1.2)
    result = self._contrast_adjust(result, 1.1)
    return result

# 註冊新軟片
self.simulations['Custom'] = self._custom_film
```

### 效能最佳化

對於 Raspberry Pi 的即時處理：

1. **降低解析度**: 預覽時使用較小尺寸
2. **快取結果**: 避免重複計算相同設定
3. **非同步處理**: 在背景執行軟片模擬

## 🔍 疑難排解

### 常見問題

1. **模組匯入錯誤**
   - 確認已安裝所有相依套件
   - 檢查 Python 路徑設定

2. **圖像處理緩慢**
   - 降低圖像解析度
   - 檢查 Raspberry Pi 效能設定

3. **記憶體不足**
   - 處理較小的圖像批次
   - 釋放不必要的圖像資料

### 除錯模式

```python
# 啟用詳細輸出
camera = RD1CameraIntegration()
camera.film_sim.debug = True
```

## 📈 未來擴展

### 計劃功能

1. **更多軟片模擬**: 加入 Kodak、Ilford 等品牌
2. **即時預覽**: 攝像頭即時軟片效果
3. **自動場景偵測**: 根據場景自動選擇適合軟片
4. **濾鏡疊加**: 模擬物理濾鏡效果

### 貢獻指南

歡迎提交新的軟片模擬或改進建議！

## 📄 授權

本專案基於 MIT 授權條款開源。

## 🙏 致謝

- Reddit r/fujifilm 社群提供的軟片模擬資料
- Fujifilm 官方技術文件
- OpenCV 和 PIL 開源專案
