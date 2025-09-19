# Claude 開發記錄

## 2025-09-07 架構重構完成

### 重大變更
- ✅ **架構改變**: 從 React+FastAPI 雙端架構 → Python 單體應用
- ✅ **主程式**: `systemControl/main.py` - tkinter GUI 應用
- ✅ **核心控制器**: `systemControl/core/application.py` - 統一管理所有模組
- ✅ **硬體抽象**: `systemControl/hardware/` - 支援開發模式模擬器

### 當前狀況
- ✅ 可運行: `cd systemControl && python main.py`
- ✅ 功能: 基本 tkinter 測試界面 (快門按鈕、硬體模擬器、系統狀態)
- ⚠️ **UI 問題**: 目前界面很陽春，與之前用 MCP 工具設計的精美 React 組件差距很大

### 技術細節
- **平台偵測**: 自動判斷 Raspberry Pi vs 開發環境
- **模組整合**: 
  - `stateMachineControl/` - 狀態機邏輯 ✅
  - `systemControl/settings/` - 統一設定管理 ✅
  - `hardware/hardware_manager.py` - 硬體統一管理 ✅
- **錯誤修復**: 解決了 tkinter import 和相機界面 import 路徑問題

## 2025-09-19 UI框架升級完成

### 重大更新
- ✅ **UI框架**: 從 Tkinter → PyQt5 升級完成
- ✅ **圓形界面**: 完整保留所有功能並優化顯示效果
- ✅ **清理舊代碼**: 移除 tkinter 版本，統一使用 PyQt

### 新UI特性
- 🎨 **現代化界面**: PyQt5 提供更好的視覺效果
- 🔄 **完整功能**: 雙編碼器控制、動畫、風格切換
- ⚡ **穩定渲染**: 使用bytes buffer解決圖像轉換問題
- 🎛️ **4種風格**: rd1_classic, mpc15_style, specture_dark, specture_light

### 檔案變更
- `systemControl/ui/circular_screen.py` - 主UI實現 (PyQt版本)
- `systemControl/ui/tk_circular_screen.py` - 已刪除
- `run_circular_ui.py` - 新的統一啟動腳本
- `test_circular_ui.py` - 功能測試腳本

### 檔案狀態
- MCP 配置已移到全域 (`~/.mcp.json`)
- Git 狀態乾淨，所有 unstaged 檔案都是必要的新模組
- README.md 已更新反映 Python 單體架構

### 啟動指令

**主應用**:
```bash
cd D:\Projects\python-project\systemControl
python main.py
```

**圓形UI界面**:
```bash
cd D:\Projects\python-project
python -m systemControl.ui.circular_screen
# 或使用啟動腳本
python run_circular_ui.py
```