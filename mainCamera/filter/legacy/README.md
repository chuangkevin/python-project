# Legacy 代碼歸檔

這個目錄包含了軟片模擬系統的舊版本代碼，已被新的模組化預設管理系統取代。

## 📁 目錄結構

### `v1_monolithic/`
- **enhanced_film_simulation.py** (46KB) - 舊版單體式軟片模擬引擎
  - 包含 40+ 種軟片效果的硬編碼實現
  - 直接集成色彩校正系統
  - 已被 `preset_manager.py` + JSON 預設系統取代

### `web_demo/`
- **enhanced_web_app.py** - Flask 網頁演示應用
- **templates/** - HTML 模板
- **uploads/** - 上傳文件目錄
- **tools/** - 網頁工具
- **install.ps1** - PowerShell 安裝腳本
- **requirements.txt** - 舊版依賴清單

### `tests/`
- **simple_test.py** - 簡單功能測試
- **test_preset_manager.py** - 預設管理器測試

### `assets/`
- **filmIcons/** - 軟片圖標資源
- **samplePicture/** - 測試圖片
- **results/** - 處理結果

## 🚀 新系統

現在使用的新系統：

### 核心文件
- `preset_manager.py` - 模組化預設管理器
- `preset_ui.py` - PyQt5 圖形界面
- `preset/systemPreset/` - JSON 預設檔案庫

### 優勢
- **模組化**: JSON 預設可獨立管理
- **可擴展**: 輕鬆添加新軟片類型
- **標準化**: 統一的預設格式
- **高效**: 按需載入預設
- **可視化**: 圖形界面操作

## 📚 歷史

- **2025-09-19**: 創建 enhanced_film_simulation.py (單體式)
- **2025-09-22**: 重構為模組化預設系統
- **2025-09-22**: 舊代碼歸檔到 legacy/