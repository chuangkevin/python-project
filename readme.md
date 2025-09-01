# Raspberry Pi Dual Display Camera (RD-1 Style)

本專案讓 Raspberry Pi 變成一台雙螢幕「復古指針相機」：
- **主螢幕 (2.4" LCD / HDMI)**：顯示 Live-View 與相機參數
- **副螢幕 (圓形 LCD)**：模擬 Epson RD-1 四個指針錶盤 (剩餘拍攝數 / 白平衡 / 電池電量 / 影像品質)
- **旋轉編碼器**：模擬相機轉盤
- **五向按鈕**：模擬方向鍵與功能鍵

---

## 🛠 安裝步驟

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-picamera2 python3-opencv python3-pip \
                    python3-pil python3-numpy python3-spidev git
pip install gc9a01 st7789

# 啟用 Camera 與 SPI
sudo raspi-config nonint do_camera 0
sudo raspi-config nonint do_spi 0
sudo reboot

---
▶️ 執行程式

將以下程式存成 dual_display_cam.py：

```

import time, math, threading
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from picamera2 import Picamera2, Preview

# 如果你用 GC9A01 圓螢幕
from gc9a01 import GC9A01 as RoundLCD

# 圓螢幕設定
SPI_PORT = 0
SPI_CS   = 0
PIN_DC   = 25
PIN_RST  = 24
WIDTH = HEIGHT = 240

# Epson RD-1 四個指針模式
gauges = [
    {"name": "SHOTS", "label": "剩餘拍攝數", "values": ["E", "10", "20", "50", "100", "500"]},
    {"name": "WB", "label": "白平衡", "values": ["A", "☀", "⛅", "☁", "💡", "💡"]},
    {"name": "BATTERY", "label": "電池電量", "values": ["E", "1/4", "1/2", "3/4", "F"]},
    {"name": "QUALITY", "label": "影像品質", "values": ["R", "H", "N"]}
]
current_gauge = 0

def draw_rd1_gauge(gauge_info, value_index):
    img = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    cx = cy = WIDTH // 2
    r_outer = 110
    
    # 錶盤外圈
    draw.ellipse((cx-r_outer, cy-r_outer, cx+r_outer, cy+r_outer), outline=(200,200,200), width=2)
    
    # 繪製刻度標籤
    values = gauge_info["values"]
    num_values = len(values)
    for i, val in enumerate(values):
        angle = math.radians(-120 + (240 * i / (num_values - 1)))
        label_x = cx + int(95 * math.cos(angle))
        label_y = cy + int(95 * math.sin(angle))
        draw.text((label_x-10, label_y-10), str(val), fill=(150,150,150))
    
    # 指針
    if value_index < num_values:
        angle = math.radians(-120 + (240 * value_index / (num_values - 1)))
        xh = cx + int(80 * math.cos(angle))
        yh = cy + int(80 * math.sin(angle))
        draw.line((cx, cy, xh, yh), fill=(255,255,255), width=4)
    
    # 中心標籤
    draw.text((cx-30, cy+50), gauge_info["label"], fill=(255,255,255))
    return img

def gauge_worker(disp):
    value_index = 0
    while True:
        gauge_info = gauges[current_gauge]
        frame = draw_rd1_gauge(gauge_info, value_index)
        disp.display(frame)
        value_index = (value_index + 1) % len(gauge_info["values"])
        time.sleep(1.5)  # 較慢的切換速度，模擬真實指針移動

def main():
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size":(640,480)})
    picam2.configure(config)
    picam2.start_preview(Preview.QTGL)  # 主螢幕 LiveView
    picam2.start()

    disp = RoundLCD(port=SPI_PORT, cs=SPI_CS, dc=PIN_DC, rst=PIN_RST, rotation=0)
    threading.Thread(target=gauge_worker, args=(disp,), daemon=True).start()

    print("Running dual display cam. Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        picam2.stop()
        disp.cleanup()

if __name__ == "__main__":
    main()
```



執行：

```

python3 dual_display_cam.py

```


🚀 開機自動啟動

一鍵建立 systemd service：

```
sudo tee /etc/systemd/system/rpi-dualcam.service > /dev/null <<'EOF'
[Unit]
Description=Raspberry Pi Dual Display Camera
After=local-fs.target
Before=basic.target

[Service]
Type=simple
Environment=LIBCAMERA_LOG_LEVELS=*:0
ExecStart=/usr/bin/python3 /home/pi/dual_display_cam.py
WorkingDirectory=/home/pi
StandardOutput=journal
StandardError=journal
Restart=on-failure
User=pi

[Install]
WantedBy=basic.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable rpi-dualcam
sudo systemctl start rpi-dualcam

```

⚡ 備註

這是最小範例：主螢幕跑 LiveView、圓螢幕模擬 Epson RD-1 四個指針錶盤。

四個指針功能：
- **剩餘拍攝數**：E → 10 → 20 → 50 → 100 → 500
- **白平衡**：A(自動) → 晴天 → 多雲 → 陰天 → 白熾燈 → 螢光燈
- **電池電量**：E(空) → 1/4 → 1/2 → 3/4 → F(滿)
- **影像品質**：R(RAW) → H(高品質JPEG) → N(一般JPEG)

你可以改 draw_rd1_gauge() 接收真實相機數據，或透過按鈕切換不同指針模式。

旋轉編碼器 / 五向鍵 可以透過 GPIO 事件擴充到 UI。

若要開機秒啟動，建議用 Raspberry Pi OS Lite 並關閉用不到的服務。

```
