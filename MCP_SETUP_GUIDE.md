# 🎨 UI 設計 MCP 服務器設置指南

本專案已成功整合兩個強大的 UI 設計 MCP 服務器，提供 AI 驅動的 UI 開發工具。

## 🔧 已配置的 MCP 服務器

### 1. **Figma MCP Server** 
- **功能**: 與 Figma 設計稿直接對話和協作
- **位置**: `D:\GitClone\cursor-talk-to-figma-mcp`
- **命令**: `bun D:\GitClone\cursor-talk-to-figma-mcp\dist\server.js`
- **狀態**: ✅ 已連接

### 2. **21st.dev Magic MCP Server**
- **功能**: AI 驅動的現代 UI 組件生成器
- **位置**: `D:\GitClone\magic-mcp` 
- **命令**: `node D:\GitClone\magic-mcp\dist\index.js`
- **狀態**: ✅ 已連接

## 📋 配置文件位置

### 全局配置
- `C:\Users\kevin\.claude\mcp.json` - 全局 MCP 服務器配置
- `C:\Users\kevin\.claude.json` - Claude Code 主配置文件

### 專案配置
- `.mcp.json` - 專案級 MCP 服務器配置
- `.vscode/settings.json` - VS Code 專案設定

## 🚀 使用方法

### Figma MCP Server 使用步驟

1. **啟動 WebSocket 服務器**:
   ```bash
   cd D:\GitClone\cursor-talk-to-figma-mcp
   bun run src/socket.ts
   ```

2. **安裝 Figma 插件**:
   - 打開 Figma Desktop App（必須使用桌面版）
   - 進入 Plugins > Development > Import plugin from manifest
   - 選擇 `cursor-talk-to-figma-mcp/src/cursor_mcp_plugin/manifest.json`

3. **保持插件窗口開啟**: 在 Figma 中保持插件窗口開啟以維持連接

### Magic MCP Server 使用方法

1. **在 Claude 對話中使用**:
   ```
   /ui create a modern navigation bar with responsive design
   /ui build a card component with hover animations
   /ui generate a dashboard layout with sidebar
   ```

2. **功能特色**:
   - 自然語言描述創建 UI 組件
   - TypeScript 支援
   - 即時預覽
   - SVGL 品牌資源整合

## 🛠️ 故障排除

### 檢查 MCP 服務器狀態
```bash
cd D:\GitClone\python-project
claude mcp list
```

### 重新啟動 MCP 服務器
```bash
# 重新啟動 Claude Code
claude config reload

# 或重新啟動 VS Code
```

### 常見問題

1. **Figma MCP 連接失敗**:
   - 確保使用 Figma Desktop App（非網頁版）
   - 檢查 WebSocket 服務器是否運行
   - 確保插件窗口保持開啟

2. **Magic MCP 無回應**:
   - 檢查 Node.js 是否正確安裝
   - 確認 `/ui` 命令格式正確
   - 檢查網路連接（需要存取 21st.dev API）

3. **路徑問題**:
   - 所有路徑均使用絕對路徑
   - Windows 路徑使用雙反斜線 `\\`

## 📊 驗證設定

運行以下命令檢查所有配置是否正確：

```bash
# 檢查 MCP 服務器連接狀態
claude mcp list

# 檢查 Claude Code 配置
claude config get

# 在 VS Code 中檢查狀態欄是否顯示 "UI Tools"
```

## 🎯 專案整合

這些 UI 設計工具特別適合您的 **Raspberry Pi 雙螢幕相機專案**:

- **使用 Figma MCP**: 設計和調整相機 UI 界面
- **使用 Magic MCP**: 快速生成相機控制組件
- **組合使用**: 從 Figma 獲取設計靈感，用 Magic 實現組件

## 🔄 更新說明

如需更新 MCP 服務器:

```bash
# 更新 Figma MCP
cd D:\GitClone\cursor-talk-to-figma-mcp
git pull
bun install
bun run build

# 更新 Magic MCP  
cd D:\GitClone\magic-mcp
git pull
npm install
npm run build
```

---

**設定完成時間**: 2025-09-07  
**配置版本**: v1.0  
**支援的 IDE**: VS Code (Claude Code Extension)