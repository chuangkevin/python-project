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

## 📁 專案架構 (重構版本)

### 🎯 架構重構進度追蹤
- [ ] **階段1**: 配置檔案統一化 (configs → profiles) - 待開始
- [ ] **階段2**: 硬體抽象層建立 - 待開始  
- [x] **階段0.5**: 基礎模組完善 - ✅ **已完成**
  - ✅ stateMachineControl 狀態機邏輯完成
  - ✅ systemControl/settings 設定系統完成
- [ ] **階段3**: 軟片模擬系統整合 - 待開始
- [ ] **階段4**: 模組整合層建立 - 待開始
- [ ] **階段5**: 完整系統測試 - 待開始

```
python-project/
├── analogGauge/          # RD-1 風格指針錶盤模組 ✅
├── mainCamera/           # 主相機系統 ✅
│   ├── filter/           # 軟片模擬濾鏡 (11種Fujifilm效果) ✅
│   ├── colorCorrection/  # Pi Camera 色彩校正與 Profile ✅
│   ├── ui/              # 主界面與 Live-View
│   ├── core/            # 核心相機功能
│   └── integration/      # 🔄 與systemControl整合層 (階段4)
├── stateMachineControl/  # 純狀態機邏輯 ✅ (完成)
│   ├── src/             # 狀態轉換核心邏輯
│   │   ├── state_machine.py     # 狀態機實作 ✅
│   │   ├── mode_dial.py         # 模式轉盤邏輯 ✅
│   │   └── loader.py            # 配置載入器 ✅
│   ├── configs/         # 配置檔案
│   │   └── mode_dial.default.json  # 預設轉盤配置
│   ├── schema/          # JSON Schema 驗證
│   │   └── mode_dial.schema.json   # 配置檔案結構定義
│   ├── simulator.py     # 雙轉盤UI模擬器 ✅
│   └── validate_config.py  # 配置驗證工具 ✅
├── systemControl/        # 🎯 系統控制中樞 (重構中)
│   ├── hardware/        # 🔄 硬體抽象層 (階段2)
│   │   ├── gpio_controller.py   # GPIO統一管理
│   │   ├── button_handler.py    # 按鈕事件處理
│   │   ├── encoder_handler.py   # 轉盤編碼器處理
│   │   ├── display_controller.py# 雙螢幕控制
│   │   └── camera_interface.py  # 相機硬體介面
│   ├── settings/        # 系統設定核心 ✅
│   │   ├── camera_settings.py   # 相機參數設定 ✅
│   │   ├── display_settings.py  # 螢幕亮度設定 ✅
│   │   ├── dial_settings.py     # 轉盤行為設定 ✅
│   │   ├── film_settings.py     # 軟片模擬設定 ✅
│   │   ├── power_settings.py    # 電源管理設定 ✅
│   │   └── storage_settings.py  # 儲存裝置設定 ✅
│   ├── configs/         # 設定檔案
│   │   └── camera_settings.json  # 相機預設設定
│   ├── profiles/        # 🔄 統一配置管理 (階段1)
│   │   ├── dial_configs/        # 從stateMachineControl遷移
│   │   ├── camera_profiles/     # 相機設定檔案
│   │   └── film_profiles/       # 軟片模擬預設
│   ├── integration/     # 🔄 模組整合層 (階段4)
│   │   ├── state_machine_bridge.py  # 與stateMachineControl溝通
│   │   └── camera_bridge.py         # 與mainCamera溝通
│   ├── ui/              # 設定界面 ✅
│   │   ├── settings_menu.py     # 主設定選單
│   │   └── dial_config_ui.py    # 轉盤配置界面
│   ├── core/            # 系統管理器 ✅
│   │   └── system_manager.py    # 中央系統管理
│   └── ui_simulator.py  # 系統測試界面 ✅
└── systemMonitor/        # Windows 系統儀表 ✅
```

### 📊 模組狀態與進度
| 模組 | 狀態 | 功能完成度 | 備註 |
|------|------|------------|------|
| `analogGauge/` | ✅ 完成 | 100% | RD-1風格錶盤 |
| `mainCamera/filter/` | ✅ 完成 | 100% | 11種Fujifilm軟片效果 |
| `mainCamera/colorCorrection/` | ✅ 完成 | 100% | 色彩校正系統 |
| `stateMachineControl/` | ✅ 完成 | 100% | 純狀態機邏輯，含UI模擬器 |
| `systemControl/settings/` | ✅ 完成 | 100% | 基礎設定系統，含軟片模擬 |
| `systemControl/hardware/` | 🔄 開發中 | 0% | 硬體抽象層 |
| `systemControl/profiles/` | 🔄 開發中 | 0% | 統一配置管理 |
| `systemControl/integration/` | 🔄 開發中 | 0% | 模組整合層 |  

---

## ⚡ 硬體配置

### 螢幕
- **主螢幕**：2.4" ILI9341 TFT LCD (SPI, 240×320)  
- **副螢幕**：0.71" GC9D01 / GC9A01 圓形 LCD (SPI, 160×160 / 240×240)  

### 控制元件
- **五向搖桿**：導航選單 (含2個擴展鍵)
- **兩段式快門**：半按 AF，全按拍照 (可自訂功能，如白卡測光)
- **三轉盤設計**：
  - 左轉盤：模式選擇
  - 右轉盤：數值調整
  - 對焦轉盤：手動對焦(MF)模式下控制對焦環
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

### 🔧 重構設計理念
- **責任分離**：狀態機邏輯 vs 系統控制 vs 硬體抽象
- **統一配置**：所有配置檔案統一在systemControl/profiles/
- **硬體抽象**：GPIO/I2C/SPI統一管理，支援硬體切換
- **事件驅動**：硬體事件→軟體事件，模組間低耦合通信

### 📦 核心模組職責
#### `stateMachineControl/` - 狀態機邏輯
- ✅ **純邏輯處理**：狀態轉換、模式切換
- ✅ **無硬體依賴**：僅處理抽象狀態
- ✅ **測試友好**：simulator.py獨立測試

#### `systemControl/` - 系統控制中樞
- 🔄 **硬體管理**：GPIO、編碼器、按鈕統一控制
- 🔄 **配置管理**：統一的設定檔案和配置切換
- ✅ **系統設定**：相機、顯示、電源、儲存設定
- 🔄 **模組整合**：其他模組的協調和通信

#### `mainCamera/` - 相機功能
- ✅ **影像處理**：拍攝、RAW處理、軟片模擬
- ✅ **色彩校正**：IMX708專用色彩配置
- 🔄 **系統整合**：與systemControl協同工作

### 🎛️ 控制系統架構
- **雙轉盤**：左=模式選擇，右=數值調整
- **五向搖桿**：選單導航和快速設定
- **兩段快門**：半按對焦，全按拍攝
- **硬體事件總線**：統一事件處理和分發

### 🔄 配置管理系統
- **統一配置**：profiles/目錄統一管理所有設定
- **版本控制**：配置檔案版本化和遷移
- **動態切換**：運行時配置熱切換
- **分享機制**：配置檔案匯入/匯出

### 🧪 開發與測試工具

#### stateMachineControl/simulator.py - 雙轉盤UI模擬器
- **功能**：視覺化測試狀態機邏輯，無需硬體即可驗證轉盤操作
- **控制**：
  - 左轉盤：模式選擇（◀▶ 或 A/D 鍵）
  - 右轉盤：數值調整（◀▶ 或 ←/→ 鍵）+ 按壓/長按（Space/L 鍵）
- **顯示**：即時狀態、詳細資訊樹、操作日誌、配置匯出
- **使用方式**：
  ```bash
  cd stateMachineControl
  python simulator.py
  ```

**注意**：此模擬器專注於狀態機邏輯測試，僅包含雙轉盤操作。其他硬體控制（五向搖桿、快門鍵等）將在 systemControl 的硬體抽象層中實現。

---

### TODO : 
因應閃燈閃爍時機未知，所以可否使用錄影(多frame)方法，用AI挑出最合適的照片
