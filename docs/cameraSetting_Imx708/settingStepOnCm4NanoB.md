# CM4-NANO-B IMX708 相機設定完整指南

## 硬體資訊
- **主板**: Waveshare CM4-NANO-B
- **相機**: Raspberry Pi Camera Module 3 (IMX708, 12MP)
- **連線資訊**: IP 192.168.18.121, 用戶 kevin, 密碼 pi
- **參考文件**: [CM4-NANO-B Wiki](https://www.waveshare.net/wiki/CM4-NANO-B)

## 1. 硬體連接
確保 IMX708 相機模組正確連接到 CM4-NANO-B 的 CSI 介面。

## 2. 系統配置

### 2.1 修改 config.txt
```bash
sudo nano /boot/firmware/config.txt
```

關鍵設定：
```ini
# 停用自動檢測
camera_auto_detect=0

# 手動啟用 IMX708 相機（重要：指定 cam0）
dtoverlay=imx708,cam0

# GPU 記憶體設定
gpu_mem=128
```

**重要注意事項**: 必須使用 `dtoverlay=imx708,cam0` 而不是 `dtoverlay=imx708`，否則會出現 I2C 通訊錯誤 -5。

### 2.2 重新啟動系統
```bash
sudo reboot
```

## 3. 相機檢測驗證

### 3.1 檢查相機是否被偵測到
```bash
libcamera-hello --list-cameras
```

**期望輸出**:
```
Available cameras
-----------------
0 : imx708 [4608x2592 10-bit RGGB] (/base/soc/i2c0mux/i2c@0/imx708@1a)
    Modes: 'SRGGB10_CSI2P' : 1536x864 [120.13 fps - (768, 432)/3072x1728 crop]
                              2304x1296 [56.03 fps - (0, 0)/4608x2592 crop]
                              4608x2592 [14.35 fps - (0, 0)/4608x2592 crop]
```

### 3.2 基本拍照測試
```bash
libcamera-still -o test.jpg --width 1536 --height 864
```

### 3.3 Python picamera2 測試
```python
from picamera2 import Picamera2
import time

# 初始化相機
picam2 = Picamera2()
print("Camera info:", picam2.camera_info)

# 配置並拍照
config = picam2.create_still_configuration(main={"size": (1536, 864)})
picam2.configure(config)
picam2.start()
time.sleep(2)
picam2.capture_file("test_imx708.jpg")
picam2.stop()
print("Photo captured successfully!")
```

## 4. IMX708 專用相機應用程式

### 4.1 程式特色
- **專為 IMX708 優化**的解析度和幀率
- **11 種濾鏡**：10 種 Fujifilm 風格 + 1 種 IMX708 Natural
- **三種解析度模式**：
  - 高幀率模式：1536×864 @ 120fps
  - 平衡模式：2304×1296 @ 56fps  
  - 高解析度模式：4608×2592 @ 14fps
- **即時預覽**和 **FPS 顯示**
- **曝光調整**（-100 到 +100）
- **多種長寬比**（4:3、16:9、1:1）

### 4.2 執行方式
```bash
# 設定顯示環境
export DISPLAY=:0

# 執行專用程式
python3 camera_pro_imx708.py
```

### 4.3 程式運行確認
```bash
# 檢查程式是否運行
ps aux | grep camera_pro_imx708

# 期望看到類似輸出：
# kevin  2028  170 20.3 2236008 374820 ?  SLl  01:35  4:53 python3 camera_pro_imx708.py
```

## 5. 技術規格

### 5.1 IMX708 相機規格
- **感測器**: Sony IMX708 12MP CMOS
- **原生解析度**: 4608 × 2592
- **視野角**: 75° 對角線
- **對焦**: 自動對焦
- **介面**: 15-pin MIPI CSI-2

### 5.2 支援的解析度和幀率
| 解析度 | 幀率 | 用途 |
|--------|------|------|
| 1536×864 | 120fps | 高速攝影 |
| 2304×1296 | 56fps | 平衡模式 |
| 4608×2592 | 14fps | 高畫質靜態攝影 |

### 5.3 libcamera 調校檔案
使用官方調校檔案：`/usr/share/libcamera/ipa/rpi/vc4/imx708.json`

## 6. 故障排除

### 6.1 常見問題

**問題**: I2C 通訊錯誤 -5
```
failed to read chip id 708, with error -5
```
**解決方案**: 確保在 config.txt 中使用 `dtoverlay=imx708,cam0` 而不是 `dtoverlay=imx708`

**問題**: PyQt5 無法顯示
```
qt.qpa.xcb: could not connect to display
```
**解決方案**: 設定顯示環境 `export DISPLAY=:0`

**問題**: 相機無法啟動
**檢查步驟**:
1. 確認相機連接正確
2. 檢查 config.txt 設定
3. 重新啟動系統
4. 驗證 GPU 記憶體設定

### 6.2 除錯指令
```bash
# 檢查 dmesg 日誌
dmesg | grep -i imx708

# 檢查 I2C 設備
i2cdetect -y 0

# 檢查視頻設備
ls -l /dev/video*

# 檢查相機程序日誌
tail -f camera_app.log
```

## 7. 效能優化建議

### 7.1 系統設定
- GPU 記憶體設定為 128MB 或更高
- 確保足夠的 SD 卡空間用於照片儲存
- 使用高速 SD 卡（Class 10 或 U3）

### 7.2 應用程式優化
- 根據需求選擇適當的解析度
- 高幀率模式適用於運動攝影
- 高解析度模式適用於靜態攝影

## 8. 成功驗證指標

✅ **相機檢測成功**
- `libcamera-hello --list-cameras` 顯示 IMX708
- 相機路徑：`/base/soc/i2c0mux/i2c@0/imx708@1a`

✅ **基本功能正常**
- 可以拍攝測試照片
- picamera2 初始化成功

✅ **GUI 應用程式運行**
- camera_pro_imx708.py 正常執行
- CPU 使用率約 170%（即時預覽正常負載）
- 記憶體使用約 374MB

✅ **專用功能可用**
- 三種解析度模式切換
- 11 種濾鏡效果
- 即時預覽和 FPS 顯示

---

**設定完成日期**: 2025年9月17日  
**測試狀態**: ✅ 所有功能正常運行  
**建議**: 定期備份相機設定檔案以防配置丟失