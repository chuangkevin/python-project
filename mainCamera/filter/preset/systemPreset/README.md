# 軟片模擬預設系統

## 📁 目錄結構

```
systemPreset/
├── _template.json          # 預設模板格式
├── fujifilm/              # Fujifilm 軟片預設
│   ├── PROVIA.json
│   ├── VELVIA.json
│   ├── CLASSIC_CHROME.json
│   └── ETERNA.json
├── kodak/                 # Kodak 軟片預設
│   └── KODACHROME_64.json
├── cinema/               # 電影膠片預設
├── vintage/              # 復古風格預設
└── special/              # 特殊效果預設
    └── REDSCALE.json
```

## 🚀 使用方法

### 基本使用

```python
from preset_manager import FilmPresetManager

# 創建預設管理器
manager = FilmPresetManager()

# 列出所有預設
presets = manager.list_presets()
print(f"找到 {len(presets)} 個預設")

# 使用特定預設處理圖像
processor = manager.create_processor('PROVIA')
result = processor.process_image('input.jpg')
```

### 分類篩選

```python
# 只顯示彩色軟片
color_presets = manager.list_presets(category='color')

# 只顯示Fujifilm軟片
fuji_presets = manager.list_presets(manufacturer='Fujifilm')

# 組合篩選
fuji_color = manager.list_presets(category='color', manufacturer='Fujifilm')
```

### 獲取預設詳情

```python
# 獲取預設完整資料
preset_data = manager.get_preset('VELVIA')
print(preset_data['metadata']['description'])
print(preset_data['processing']['saturation']['global'])
```

## 📝 JSON 預設格式

### 基本結構

```json
{
  "metadata": {
    "name": "軟片名稱",
    "description": "軟片描述",
    "manufacturer": "廠商名稱",
    "category": "color|bw|cinema|vintage|special",
    "icon": "圖標檔案名.jpg",
    "tags": ["標籤1", "標籤2"]
  },
  "processing": {
    "tone_curve": {
      "enabled": true,
      "type": "film|vintage|high_contrast",
      "gamma": 0.9
    },
    "saturation": {
      "enabled": true,
      "global": 1.2,
      "skin_protection": true
    },
    "contrast": {
      "enabled": true,
      "global": 1.1
    }
  }
}
```

### 支援的處理參數

- **tone_curve**: 色調曲線調整
- **color_temperature**: 色溫調整
- **saturation**: 飽和度調整
- **contrast**: 對比度調整
- **brightness**: 亮度調整
- **split_toning**: 分離調色
- **vintage_fade**: 復古褪色
- **film_grain**: 膠片顆粒
- **vignette**: 暗角效果

## 🎨 現有預設

### Fujifilm 系列
- **PROVIA**: 標準專業反轉片，平衡自然色彩
- **VELVIA**: 高飽和度風景片，鮮豔銳利色彩
- **CLASSIC CHROME**: 低飽和度硬調，復古雜誌風格
- **ETERNA**: 電影膠片風格，抑制飽和度

### Kodak 系列
- **KODACHROME 64**: 經典Kodak色彩科學，高飽和度

### 特殊效果
- **REDSCALE**: 紅調特殊效果，實驗性藝術風格

## 🔧 新增自訂預設

### 1. 複製模板
```bash
cp _template.json fujifilm/MY_PRESET.json
```

### 2. 編輯預設參數
根據需要調整 `metadata` 和 `processing` 參數

### 3. 重新載入預設
```python
manager.reload_presets()
```

## 📊 預設驗證

系統會自動驗證預設檔案格式：

- 必要的 metadata 欄位
- 必要的 processing 欄位
- 參數值的合理範圍

## 🔗 與現有系統整合

### 與 analogGauge 整合

```python
from preset_manager import FilmPresetManager
from analogGauge.circular_screen import CircularScreenAPI

# 創建軟片選擇列表
manager = FilmPresetManager()
presets = manager.list_presets()

# 生成錶盤值列表
gauge_values = [preset['name'][:3] for preset in presets]

# 加入到 RD1Gauge 配置
film_gauge_config = {
    "name": "FILM",
    "label": "軟片模擬",
    "values": gauge_values
}
```

### 與網頁 demo 整合

```python
from flask import Flask
from preset_manager import FilmPresetManager

app = Flask(__name__)
manager = FilmPresetManager()

@app.route('/api/presets')
def get_presets():
    return {"presets": manager.list_presets()}

@app.route('/api/process/<preset_id>')
def process_image(preset_id):
    processor = manager.create_processor(preset_id)
    # 處理上傳的圖像...
```

## 🎯 效能考量

- **快取**: 預設載入後會快取在記憶體中
- **批次處理**: 支援批次處理多張圖像
- **即時預覽**: 可搭配低解析度圖像做即時預覽

## 📈 擴展建議

1. **新增更多軟片**: Ilford、Agfa 等品牌
2. **進階參數**: 色相範圍調整、遮罩功能
3. **使用者預設**: 支援使用者自訂預設匯入/匯出
4. **預設組合**: 支援多個預設的混合效果

## 🔍 疑難排解

### 預設載入失敗
- 檢查 JSON 格式是否正確
- 確認必要欄位是否存在
- 查看控制台錯誤訊息

### 圖像處理錯誤
- 確認輸入圖像格式支援
- 檢查參數數值範圍
- 驗證圖像尺寸限制