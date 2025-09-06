# 📷 Raspberry Pi Dual Display Camera (RD-1 Style)

本專案將 Raspberry Pi CM4 打造成一台「復古雙螢幕相機」，靈感來自 **Epson RD-1**。  
特色是 **主螢幕 Live-View** + **副螢幕指針錶盤**，並結合雙轉盤、五向搖桿與兩段快門，提供接近傳統相機的操作體驗。

---

## ✨ 功能特色
- **主螢幕 (2.4" ILI9341 SPI LCD)**  
  - 即時 Live-View  
  - 顯示拍攝參數（快門 / ISO / EV / 白平衡 / 軟片模擬 / 電量 / 閃光燈控制）  

- **副螢幕 (0.71" GC9D01 圓形 LCD)**  
  - 類比錶盤風格（電量 / 白平衡 / 曝光補償 / 照片品質）  
  - 可切換不同指針 UI 模式  

- **雙轉盤設計**  
  - 左轉盤：決定右轉盤控制項（快門、ISO、EV、WB、軟片模擬等）  
  - 右轉盤：依當前模式調整數值，按壓作為確認/切換  

- **白平衡自訂**  
  - 預設場景（Auto/Daylight/Cloudy/Incandescent/Fluorescent/Shade）  
  - 每個場景可微調（A-B 軸 / G-M 軸）  
  - 白卡測光模式：拍攝白/灰卡，計算增益套用  

- **快門鍵**  
  - 兩段式：半按觸發自動對焦，全按拍照  
  - 支援 RAW (DNG) + JPEG  

- **復古手感設計**  
  - 五向搖桿：選單操作  
  - 過片桿：模擬拉片手感，可觸發「下一張」  
  - 機頂電源鍵：短按待機、長按安全關機  

- **硬體整合**  
  - **Camera Module 3 (IMX708, AF)** → 12MP、PDAF、RAW  
  - **MAX17043** → 電量監測  
  - **DS3231 RTC** → 離線時間維持  
  - **氙氣閃光模組** → 高功率觸發式閃光  
  - **補光 LED** → PWM 控制亮度  

---

## 📁 專案架構
```
python-project/
├── analogGauge/          # RD-1 風格指針錶盤模組
├── mainCamera/           # 主相機系統
│   ├── filter/           # 軟片模擬濾鏡 (Classic Chrome, Kodak, Fuji…)
│   ├── colorCorrection/  # Pi Camera 色彩校正與 Profile
│   ├── ui/              # 主界面與 Live-View
│   └── core/            # 核心相機功能
├── stateMachineControl/  # 雙轉盤控制邏輯 ✅
│   ├── src/             # 狀態機核心實作
│   ├── configs/         # 轉盤配置檔案 (JSON)
│   ├── schema/          # 配置驗證 Schema
│   └── simulator.py     # 雙轉盤模擬器 (開發工具)
├── systemControl/        # 系統控制與設定模組 🆕
│   ├── settings/        # 系統設定核心
│   │   ├── camera_settings.py    # 相機參數設定
│   │   ├── display_settings.py   # 螢幕亮度/對比設定
│   │   ├── dial_settings.py      # 雙轉盤行為設定
│   │   ├── power_settings.py     # 電源管理設定
│   │   └── storage_settings.py   # 儲存裝置設定
│   ├── ui/              # 設定界面
│   │   ├── settings_menu.py      # 主設定選單
│   │   └── dial_config_ui.py     # 轉盤配置界面
│   ├── config/          # 系統配置檔案
│   │   ├── system.json           # 系統全域配置
│   │   └── dial_profiles/        # 轉盤設定檔案夾
│   │       ├── default.json      # 預設轉盤配置
│   │       ├── video.json        # 錄影模式配置
│   │       └── manual.json       # 手動模式配置
│   └── core/            # 系統控制核心
│       └── system_manager.py     # 系統管理器
└── systemMonitor/        # 使用 analogGauge 製作的 Windows 系統儀表
```

### 實際檔案（目前進度）：
- ✅ `stateMachineControl/` → 雙轉盤邏輯完成，白平衡問題已修正
- ✅ `filter/` → 軟片模擬、網頁測試介面  
- ✅ `colorCorrection/` → 色彩校正與 profile 儲存  
- ✅ `uploads/`、`outputs/` → 測試影像資料夾
- 🆕 `systemControl/` → 系統控制模組 (準備建立)  

---

## ⚡ 硬體配置

### 螢幕
- **主螢幕**：2.4" ILI9341 TFT LCD (SPI, 240×320)  
- **副螢幕**：0.71" GC9D01 / GC9A01 圓形 LCD (SPI, 160×160 / 240×240)  

### 控制元件
- **五向搖桿**：導航選單  
- **兩段式快門**：半按 AF，全按拍照  
- **雙轉盤**：左＝模式選擇，右＝數值調整  
- **過片桿**：模擬復古相機操作  
- **電源鍵**：短按待機、長按安全關機  

### 感測與電源
- **Camera Module 3 (IMX708)**：支援 PDAF / RAW / HDR  
- **MAX17043 Fuel Gauge**：電池電壓 + 電量百分比  
- **DS3231 RTC**：準確時間戳  
- **鋰電池 (6000 mAh)**：行動電源模組 Type-C 供電  

### 閃光燈
- **氙氣閃光模組 (10 W·s)**：GPIO → 光耦觸發  
- **補光 LED (1W/3W)**：PWM 恆流控制  

### 儲存裝置
- 做一個底片造型的讀卡機，type-c
- rpi從usb拉一個tpye-c母座
- 如果有插額外的儲存裝置，使用額外的儲存裝置，否則用內建的儲存裝置
---

## 📝 開發說明

### 模組設計理念
- **模組化架構**：相機、濾鏡、色彩校正、指針 UI、系統控制皆獨立
- **分離關注點**：狀態機邏輯、系統設定、UI 界面各司其職
- **可配置性**：支援多種轉盤配置檔案，適應不同拍攝場景

### 核心功能模組
- **stateMachineControl**：純粹的雙轉盤邏輯，無 UI 依賴
- **systemControl**：統一管理系統設定，包括轉盤行為配置
- **白平衡系統**：支援場景切換、A-B/G-M 微調、自定義白卡測光
- **電源管理**：待機/關機模式已規劃（需搭配 UPS 模組）

### 雙轉盤控制邏輯
- **左轉盤**：模式選擇（快門、ISO、EV、白平衡、軟片模擬等）
- **右轉盤**：當前模式數值調整，支援按壓確認/切換
- **群組模式**：白平衡等複雜設定支援子選單導航
- **配置切換**：可在拍照/錄影/手動模式間切換不同轉盤行為

### 擴展性設計
- **轉盤設定檔**：JSON 格式，支援匯入/匯出/分享
- **濾鏡系統**：可持續加入新的軟片模擬效果
- **指針樣式**：analogGauge 支援多種復古錶盤設計

### TODO : 
因應閃燈閃爍時機未知，所以可否使用錄影(多frame)方法，用AI挑出最合適的照片
