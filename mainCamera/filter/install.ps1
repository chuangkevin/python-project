# Fujifilm 軟片模擬系統安裝指令 (PowerShell)

Write-Host "🎬 安裝 Fujifilm 軟片模擬系統..." -ForegroundColor Green

# 檢查 Python 是否已安裝
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python 已安裝: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python 未安裝，請先安裝 Python 3.7 或更新版本" -ForegroundColor Red
    exit 1
}

# 安裝相依套件
Write-Host "📦 安裝相依套件..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    Write-Host "✓ 相依套件安裝完成" -ForegroundColor Green
} catch {
    Write-Host "⚠ 部分套件安裝可能失敗，請手動檢查" -ForegroundColor Yellow
}

# 執行測試
Write-Host "🧪 執行整合測試..." -ForegroundColor Yellow
try {
    python rd1_integration.py
    Write-Host "✓ 整合測試完成" -ForegroundColor Green
} catch {
    Write-Host "⚠ 測試執行有問題，請檢查相依套件" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 安裝完成！" -ForegroundColor Green
Write-Host "📝 使用說明請參考 README.md" -ForegroundColor Cyan
Write-Host "🚀 開始使用: python film_simulation_demo.py" -ForegroundColor Cyan
