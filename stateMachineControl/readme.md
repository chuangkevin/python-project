m# 📖 ModeDial（模式轉盤）模組 README

> 目標：用一個 **JSON 設定檔**定義「左轉盤控制 / 右轉盤行為 / UI 顯示」與「狀態機邏輯」，讓你的相機專案（CM4 + Camera Module 3）能像傳統相機一樣用**雙轉盤**流暢操作。

---

## 🧱 模組定位
- **左轉盤**：選擇「控制類別」（例：快門、ISO、EV、WB、軟片模擬、閃燈、測光、自拍、對焦模式…）
- **右轉盤**：依左轉盤當前類別，調整對應數值（或選項）；按壓＝確認/次要功能
- **狀態機**：以 JSON 描述「模式 → 子狀態（選項/範圍）→ 轉場規則（旋轉/按壓/長按）」

---

## 📁 建議專案結構
# 📖 ModeDial（模式轉盤）模組 README

> 目標：用一個 **JSON 設定檔**定義「左轉盤控制 / 右轉盤行為 / UI 顯示」與「狀態機邏輯」，讓你的相機專案（CM4 + Camera Module 3）能像傳統相機一樣用**雙轉盤**流暢操作。

---

## 🧱 模組定位
- **左轉盤**：選擇「控制類別」（例：快門、ISO、EV、WB、軟片模擬、閃燈、測光、自拍、對焦模式…）
- **右轉盤**：依左轉盤當前類別，調整對應數值（或選項）；按壓＝確認/次要功能
- **狀態機**：以 JSON 描述「模式 → 子狀態（選項/範圍）→ 轉場規則（旋轉/按壓/長按）」

---

## 📁 建議專案結構
modeDial/
├─ README.md # 本文件
├─ schema/
│ └─ mode_dial.schema.json # JSON Schema（用於驗證配置檔）
├─ configs/
│ ├─ mode_dial.default.json # 預設模式轉盤設定
│ └─ profiles/
│ └─ film_sims.json # 軟片模擬選單（共用）
└─ src/
├─ loader.py # 載入/驗證 JSON、提供查詢 API
├─ state_machine.py # 狀態機核心（事件/轉場）
└─ bindings.md # 與硬體/相機控制層的綁定說明


> 你可以先只建立 `configs/mode_dial.default.json` 與 `schema/mode_dial.schema.json`，其餘檔案視開發進度補上。

---

## 🧩 JSON 設定檔設計理念
- **宣告式**：把「有哪些模式、每個模式有哪些選項或數值範圍、旋轉與按壓的行為、顯示文字/圖示」都寫在 JSON
- **可擴充**：未來要新增模式（例如：畫質、驅動模式、顯示資訊切換）只改 JSON，不改程式
- **可在地化**：同一個 `id` 可對應多語系 `label`（本案先以繁中為主）

---

## ✅ JSON Schema（簡化版）
> 存檔於 `schema/mode_dial.schema.json`。用 `jsonschema` 套件即可驗證。

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ModeDialConfig",
  "type": "object",
  "required": ["version", "dialOrder", "modes"],
  "properties": {
    "version": { "type": "string" },
    "dialOrder": {
      "description": "左轉盤的模式順序（轉一格換到下一個）",
      "type": "array",
      "items": { "type": "string" },
      "minItems": 1
    },
    "ui": {
      "description": "全域 UI 設定（可選）",
      "type": "object",
      "properties": {
        "icons": { "type": "object", "additionalProperties": { "type": "string" } }
      },
      "additionalProperties": false
    },
    "modes": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "label", "type"],
        "properties": {
          "id": { "type": "string" },
          "label": { "type": "string" },
          "type": {
            "type": "string",
            "enum": ["enum", "range", "toggle", "action", "group"]
          },
          "hint": { "type": "string" },

          "enum": {
            "description": "type=enum 時的選項",
            "type": "array",
            "items": {
              "type": "object",
              "required": ["id", "label"],
              "properties": {
                "id": { "type": "string" },
                "label": { "type": "string" },
                "value": {},
                "icon": { "type": "string" },
                "bindings": { "type": "object" }
              },
              "additionalProperties": false
            }
          },

          "range": {
            "description": "type=range 時的數值設定",
            "type": "object",
            "required": ["min", "max", "step"],
            "properties": {
              "min": { "type": "number" },
              "max": { "type": "number" },
              "step": { "type": "number" },
              "unit": { "type": "string" },
              "display": { "type": "string" },
              "bindings": { "type": "object" }
            },
            "additionalProperties": false
          },

          "toggle": {
            "description": "type=toggle 的 on/off 行為",
            "type": "object",
            "properties": {
              "on": { "type": "object", "properties": { "label": { "type": "string" }, "bindings": { "type": "object" } }, "additionalProperties": false },
              "off": { "type": "object", "properties": { "label": { "type": "string" }, "bindings": { "type": "object" } }, "additionalProperties": false }
            },
            "additionalProperties": false
          },

          "group": {
            "description": "把多個子模式包成一組（例如 WB：預設/微調/白卡）",
            "type": "array",
            "items": { "$ref": "#/properties/modes/items" }
          },

          "events": {
            "description": "右轉盤/按壓/長按 的事件對應",
            "type": "object",
            "properties": {
              "rotate": { "type": "string", "enum": ["next", "prev", "inc", "dec"] },
              "press": { "type": "string", "enum": ["confirm", "toggle", "enter", "noop"] },
              "longPress": { "type": "string", "enum": ["enterSub", "back", "custom", "noop"] }
            },
            "additionalProperties": false
          }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}

🧪 設定檔範例（可直接用）

存檔於 configs/mode_dial.default.json。
你可以先只保留自己要的模式；日後新增就擴充 JSON。
{
  "version": "1.0.0",
  "dialOrder": [
    "shutter", "iso", "ev", "wb", "film", "flash", "metering", "self_timer", "af_mode", "display", "menu"
  ],
  "ui": {
    "icons": {
      "shutter": "icon_shutter",
      "iso": "icon_iso",
      "ev": "icon_ev",
      "wb": "icon_wb",
      "film": "icon_film",
      "flash": "icon_flash",
      "metering": "icon_metering",
      "self_timer": "icon_timer",
      "af_mode": "icon_af",
      "display": "icon_display",
      "menu": "icon_menu"
    }
  },
  "modes": [
    {
      "id": "shutter",
      "label": "快門速度",
      "type": "enum",
      "hint": "右轉盤切換快門檔位，按壓切 M/AE",
      "enum": [
        { "id": "1/1000", "label": "1/1000", "value": 0.001, "bindings": { "control": "ExposureTime" } },
        { "id": "1/500",  "label": "1/500",  "value": 0.002, "bindings": { "control": "ExposureTime" } },
        { "id": "1/250",  "label": "1/250",  "value": 0.004, "bindings": { "control": "ExposureTime" } },
        { "id": "1/125",  "label": "1/125",  "value": 0.008, "bindings": { "control": "ExposureTime" } },
        { "id": "1/60",   "label": "1/60",   "value": 0.0167,"bindings": { "control": "ExposureTime" } },
        { "id": "1/30",   "label": "1/30",   "value": 0.0333,"bindings": { "control": "ExposureTime" } },
        { "id": "1/15",   "label": "1/15",   "value": 0.0667,"bindings": { "control": "ExposureTime" } },
        { "id": "1/8",    "label": "1/8",    "value": 0.125, "bindings": { "control": "ExposureTime" } },
        { "id": "1/4",    "label": "1/4",    "value": 0.25,  "bindings": { "control": "ExposureTime" } },
        { "id": "1/2",    "label": "1/2",    "value": 0.5,   "bindings": { "control": "ExposureTime" } },
        { "id": "1",      "label": "1s",     "value": 1.0,   "bindings": { "control": "ExposureTime" } }
      ],
      "events": { "rotate": "next", "press": "toggle", "longPress": "noop" }
    },

    {
      "id": "iso",
      "label": "ISO",
      "type": "enum",
      "enum": [
        { "id": "iso_100",  "label": "100",  "value": 100,  "bindings": { "control": "ISO" } },
        { "id": "iso_200",  "label": "200",  "value": 200,  "bindings": { "control": "ISO" } },
        { "id": "iso_400",  "label": "400",  "value": 400,  "bindings": { "control": "ISO" } },
        { "id": "iso_800",  "label": "800",  "value": 800,  "bindings": { "control": "ISO" } },
        { "id": "iso_1600", "label": "1600", "value": 1600, "bindings": { "control": "ISO" } }
      ],
      "events": { "rotate": "next", "press": "confirm", "longPress": "noop" }
    },

    {
      "id": "ev",
      "label": "曝光補償",
      "type": "range",
      "range": { "min": -3.0, "max": 3.0, "step": 0.33, "unit": "EV", "display": "{value:+.2f}EV", "bindings": { "control": "ExposureValue" } },
      "events": { "rotate": "inc", "press": "confirm", "longPress": "noop" }
    },

    {
      "id": "wb",
      "label": "白平衡",
      "type": "group",
      "group": [
        {
          "id": "wb_preset",
          "label": "WB：預設",
          "type": "enum",
          "enum": [
            { "id": "auto",        "label": "自動",   "bindings": { "control": "AwbMode", "value": "auto" } },
            { "id": "daylight",    "label": "日光",   "bindings": { "control": "AwbMode", "value": "daylight" } },
            { "id": "cloudy",      "label": "陰天",   "bindings": { "control": "AwbMode", "value": "cloudy" } },
            { "id": "incandescent","label": "鎢絲燈", "bindings": { "control": "AwbMode", "value": "incandescent" } },
            { "id": "fluorescent", "label": "螢光燈", "bindings": { "control": "AwbMode", "value": "fluorescent" } },
            { "id": "shade",       "label": "陰影",   "bindings": { "control": "AwbMode", "value": "shade" } },
            { "id": "custom",      "label": "自定義", "bindings": { "control": "AwbEnable", "value": false } }
          ],
          "events": { "rotate": "next", "press": "confirm", "longPress": "enterSub" }
        },
        {
          "id": "wb_tweak",
          "label": "WB：微調",
          "type": "range",
          "range": { "min": -10, "max": 10, "step": 1, "unit": "step", "display": "A/B {value}", "bindings": { "control": "ColourGains_AB" } },
          "events": { "rotate": "inc", "press": "confirm", "longPress": "back" }
        },
        {
          "id": "wb_whitecard",
          "label": "WB：白卡測光",
          "type": "action",
          "hint": "長按右轉盤→擷取中心區塊計算增益",
          "events": { "rotate": "noop", "press": "confirm", "longPress": "custom" }
        }
      ]
    },

    {
      "id": "film",
      "label": "軟片模擬",
      "type": "enum",
      "enum": [
        { "id": "classic_chrome", "label": "Classic Chrome", "bindings": { "pipeline": "filmSim", "value": "classic_chrome" } },
        { "id": "kodak_400",      "label": "Kodak 400",      "bindings": { "pipeline": "filmSim", "value": "kodak_400" } },
        { "id": "acros",          "label": "ACROS",          "bindings": { "pipeline": "filmSim", "value": "acros" } }
      ],
      "events": { "rotate": "next", "press": "confirm", "longPress": "noop" }
    },

    {
      "id": "flash",
      "label": "閃燈",
      "type": "toggle",
      "toggle": {
        "on":  { "label": "開", "bindings": { "gpio": "FLASH_EN", "value": 1 } },
        "off": { "label": "關", "bindings": { "gpio": "FLASH_EN", "value": 0 } }
      },
      "events": { "rotate": "noop", "press": "toggle", "longPress": "noop" }
    },

    {
      "id": "metering",
      "label": "測光模式",
      "type": "enum",
      "enum": [
        { "id": "average", "label": "平均", "bindings": { "control": "Metering", "value": "average" } },
        { "id": "center",  "label": "中央重點", "bindings": { "control": "Metering", "value": "center" } },
        { "id": "spot",    "label": "點測", "bindings": { "control": "Metering", "value": "spot" } }
      ],
      "events": { "rotate": "next", "press": "confirm", "longPress": "noop" }
    },

    {
      "id": "self_timer",
      "label": "自拍時長",
      "type": "enum",
      "enum": [
        { "id": "off",  "label": "關",  "bindings": { "control": "SelfTimer", "value": 0 } },
        { "id": "2s",   "label": "2 秒","bindings": { "control": "SelfTimer", "value": 2 } },
        { "id": "10s",  "label": "10 秒","bindings": { "control": "SelfTimer", "value": 10 } }
      ],
      "events": { "rotate": "next", "press": "confirm", "longPress": "noop" }
    },

    {
      "id": "af_mode",
      "label": "對焦模式",
      "type": "enum",
      "enum": [
        { "id": "af_s", "label": "AF-S", "bindings": { "control": "AfMode", "value": "single" } },
        { "id": "af_c", "label": "AF-C", "bindings": { "control": "AfMode", "value": "continuous" } },
        { "id": "mf",   "label": "MF",   "bindings": { "control": "AfMode", "value": "manual" } }
      ],
      "events": { "rotate": "next", "press": "confirm", "longPress": "noop" }
    },

    {
      "id": "display",
      "label": "顯示資訊",
      "type": "enum",
      "enum": [
        { "id": "full",    "label": "完整資訊", "bindings": { "ui": "osd_level", "value": "full" } },
        { "id": "minimal", "label": "簡潔",     "bindings": { "ui": "osd_level", "value": "minimal" } },
        { "id": "off",     "label": "關閉",     "bindings": { "ui": "osd_level", "value": "off" } }
      ],
      "events": { "rotate": "next", "press": "confirm", "longPress": "noop" }
    },

    {
      "id": "menu",
      "label": "設定選單",
      "type": "action",
      "hint": "按壓進入系統設定",
      "events": { "rotate": "noop", "press": "enter", "longPress": "noop" }
    }
  ]
}

🔌 綁定約定（bindings）說明

這些鍵只是「語意標籤」，真正如何呼叫相機/硬體 API 由你的控制層實作。

"control": "ExposureTime" → 對應 Picamera2 / libcamera 的曝光時間控制

"control": "ISO" → 轉換為 AnalogueGain / AeEnable 等

"control": "ExposureValue" → EV 補償

"control": "AwbMode" / "AwbEnable" / "ColourGains_*" → 白平衡控制

"pipeline": "filmSim" → 交給你的影像處理管線切換濾鏡

"gpio": "FLASH_EN" → 你的 GPIO 名稱表（在程式裡映射到 BCM 腳位）

"ui": "osd_level" → UI 顯示層的狀態切換

🧷 你原本的需求如何落在 JSON

軟片模擬：id="film" 的 enum 清單，你可以把 profiles/film_sims.json 引入，或直接嵌入

過片模式（驅動）：可新增 id="drive"，type=enum，值＝單張/連拍/包圍

測光/自拍/對焦模式：已內建在例子（metering、self_timer、af_mode）

顯示資訊：display 模式

白平衡：wb 以 group 表示（預設/微調/白卡）

你也可以用你原提出的簡短風格：
{"軟片模擬":["Classic Chrome","Kodak 400"]},{"過片模式":["單張","連拍"]}
但為了可落地執行與擴充，本 README 提供了帶語意的結構化版本。

🧪 驗證與載入（說明）

用 jsonschema 驗證 mode_dial.default.json 是否符合 mode_dial.schema.json

程式端只需：

解析 dialOrder 生成左轉盤序列

依當前 mode.id 與 type 解析右轉盤事件

把被選中的 bindings 發佈到你的控制層（相機/GPIO/UI）

📝 版本化建議

version 請用 major.minor.patch（例：1.0.0）

大改 schema 時升 major；新增模式/選項升 minor；修正文案升 patch

✅ 快速檢查清單

左轉盤順序是否符合你的實體刻度（或 UI 顯示）

每個模式是否有 events（旋轉/按壓/長按）

bindings 是否對應到你控制層的關鍵字（避免拼錯）

WB/Film/Flash 等「跨子系統」是否有一致的 id/label 命名規範