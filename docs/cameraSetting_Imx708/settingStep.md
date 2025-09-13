# Raspberry Pi 相機設定完整指南

## 目錄
1. [硬體需求](#硬體需求)
2. [問題診斷流程](#問題診斷流程)
3. [設定步驟](#設定步驟)
4. [相機測試方法](#相機測試方法)
5. [常見問題排除](#常見問題排除)
6. [測試結果記錄](#測試結果記錄)

---

## 硬體需求

### 支援的硬體組合
- ✅ **Raspberry Pi 4 + IMX708** - 4608x2592, 14fps
- ✅ **Raspberry Pi 4 + OV5647** - 2592x1944, 15fps  
- ❌ **Compute Module 4 載板** - CSI接口可能有問題

### 相機排線連接
```
正確連接方式：
- 金屬接點面朝下
- 藍色標籤面朝向USB接口方向
- 確保排線完全插入CSI接口
- 塑膠卡扣必須完全鎖緊
```

---

## 問題診斷流程

### 第一步：檢查硬體偵測
```bash
# 檢查相機是否被偵測
rpicam-hello --list-cameras

# 檢查GPU相機支援
vcgencmd get_camera

# 檢查I2C設備 (應該在0x1a或0x36看到相機)
sudo i2cdetect -y 10
```

### 第二步：檢查系統日志
```bash
# 查看相機初始化錯誤
sudo dmesg | grep -i -E 'imx708|ov5647|camera|probe'

# 常見錯誤碼含義:
# error -5: I2C通訊失敗 (硬體連接問題)
# error -110: 超時錯誤
# "No cameras available": 驅動或配置問題
```

### 第三步：檢查配置文件
```bash
# 檢查當前配置
cat /boot/firmware/config.txt | grep -E 'camera|dtoverlay'

# 檢查是否正確設定
grep "camera_auto_detect=0" /boot/firmware/config.txt
grep "dtoverlay=imx708" /boot/firmware/config.txt
```

---

## 設定步驟

### 步驟1：備份配置文件
```bash
sudo cp /boot/firmware/config.txt /boot/firmware/config.txt.backup
```

### 步驟2：關閉自動偵測
```bash
sudo sed -i 's/camera_auto_detect=1/camera_auto_detect=0/' /boot/firmware/config.txt
```

### 步驟3：添加手動相機配置
```bash
sudo tee -a /boot/firmware/config.txt << 'EOF'

# Manual camera configuration
#dtoverlay=ov5647
#dtoverlay=imx219
#dtoverlay=imx219,cam0
#dtoverlay=imx477
#dtoverlay=imx290,clock-frequency=37125000
#dtoverlay=imx378
#dtoverlay=ov9281
#dtoverlay=imx296
#dtoverlay=imx519
dtoverlay=imx708
#dtoverlay=imx708,vcm=0
EOF
```

### 步驟4：選擇正確的相機驅動
```bash
# 為IMX708相機 (取消註解)
sudo sed -i 's/#dtoverlay=imx708$/dtoverlay=imx708/' /boot/firmware/config.txt

# 為OV5647相機 (取消註解) 
sudo sed -i 's/#dtoverlay=ov5647/dtoverlay=ov5647/' /boot/firmware/config.txt

# 註解掉其他不需要的相機
sudo sed -i 's/dtoverlay=imx708/#dtoverlay=imx708/' /boot/firmware/config.txt
```

### 步驟5：重新啟動並測試
```bash
sudo reboot
```

---

## 相機測試方法

### 基本偵測測試
```bash
# 1. 檢查相機列表
rpicam-hello --list-cameras

# 預期輸出 (IMX708):
# 0 : imx708 [4608x2592 10-bit RGGB] (/base/soc/i2c0mux/i2c@1/imx708@1a)

# 預期輸出 (OV5647):
# 0 : ov5647 [2592x1944 10-bit GBRG] (/base/soc/i2c0mux/i2c@1/ov5647@36)
```

### 快速拍照測試
```bash
# 2. 拍攝測試照片
rpicam-still --output test.jpg --timeout 1000

# 成功標誌：
# - 命令執行無錯誤
# - 生成test.jpg文件
# - 檔案大小 > 0
```

### Python Picamera2測試
```python
# 3. Python相機測試
python3 -c "
from picamera2 import Picamera2
print('Camera info:', Picamera2.global_camera_info())
picam2 = Picamera2()
print('Camera initialized successfully')
picam2.close()
"

# 成功標誌：
# - Camera info: [{'Num': 0, 'Model': 'imx708', ...}]
# - Camera initialized successfully
```

---

## 常見問題排除

### 問題1：No cameras available
**原因分析:**
- 硬體連接問題 (90%)
- 驅動配置錯誤 (10%)

**解決步驟:**
1. 重新插拔相機排線
2. 檢查排線方向和鎖緊
3. 嘗試不同的相機驅動配置
4. 重新啟動系統

### 問題2：failed to read chip id, with error -5
**原因分析:**
- I2C通訊失敗 (硬體問題)
- 排線接觸不良
- 相機模組故障

**解決步驟:**
1. 檢查排線金屬接點是否乾淨
2. 確認排線完全插入
3. 嘗試更換排線
4. 檢查相機模組是否損壞

### 問題3：Connection timeout (SSH)
**原因分析:**
- IP地址改變
- 網路連接問題
- RPI未完全啟動

**解決步驟:**
1. 檢查路由器DHCP分配的IP
2. 等待RPI完全啟動 (約2分鐘)
3. 重新掃描網路尋找RPI

### 問題4：Host key verification failed
**解決方法:**
```bash
ssh-keygen -R [IP地址]
ssh -o StrictHostKeyChecking=no kevin@[IP地址]
```

---

## 判讀標準

### 成功偵測的標誌
✅ **rpicam-hello --list-cameras** 顯示相機資訊  
✅ **vcgencmd get_camera** 顯示 supported=1 detected=1  
✅ **i2cdetect** 在相應地址顯示設備  
✅ **dmesg** 無 probe failed 錯誤  
✅ **Picamera2.global_camera_info()** 返回非空列表  

### 失敗的標誌
❌ **"No cameras available"**  
❌ **"supported=0 detected=0"**  
❌ **I2C地址空白**  
❌ **"failed to read chip id" 錯誤**  
❌ **"IndexError: list index out of range"**  

---

## 測試結果記錄

### 硬體組合測試結果

| 硬體組合 | 相機型號 | 狀態 | 最大解析度 | 最大幀率 | 備註 |
|---------|---------|------|------------|----------|------|
| RPI4 | IMX708 | ✅ 成功 | 4608x2592 | 14fps | 支援120fps低解析度模式 |
| RPI4 | OV5647 | ✅ 成功 | 2592x1944 | 15fps | 經典相機模組 |
| CM4載板 | IMX708 | ❌ 失敗 | - | - | I2C通訊錯誤(-5) |
| CM4載板 | OV5647 | ❌ 失敗 | - | - | 硬體接口問題 |

### 相機規格對比

#### IMX708 (12MP)
```
解析度模式:
- 1536x864 @ 120fps (高幀率)
- 2304x1296 @ 56fps (中等)  
- 4608x2592 @ 14fps (最高)

色彩格式: 10-bit RGGB
I2C地址: 0x1a
```

#### OV5647 (5MP)
```
解析度模式:
- 640x480 @ 58fps
- 1296x972 @ 46fps
- 1920x1080 @ 32fps
- 2592x1944 @ 15fps

色彩格式: 10-bit GBRG  
I2C地址: 0x36
```

---

## 相機應用程式

### camera_pro.py 需求
- **Python函式庫**: picamera2, PyQt5, opencv-python, numpy
- **系統需求**: X11顯示 (GUI應用程式)
- **硬體需求**: 成功偵測的相機模組

### 執行指令
```bash
# 安裝依賴
sudo apt update
sudo apt install python3-picamera2 python3-pyqt5 python3-opencv python3-numpy

# 執行專業相機應用程式
python3 camera_pro.py
```

---

## 備註

- **CM4問題**: Compute Module 4的CSI接口實現可能與標準RPI4不同，導致某些載板無法正常工作
- **電源考量**: 確保相機模組有足夠的電源供應，特別是高解析度模式
- **排線品質**: 使用高品質的相機排線，避免接觸不良
- **環境因素**: 避免靜電和潮濕環境影響電子元件

---

*最後更新: 2025-09-13*  
*測試環境: Raspberry Pi OS (64-bit), Kernel 6.12.25+rpt-rpi-v8*

------
原始設定文章

https://www.openaicam.com/thread-5-1-1.html

树莓派镜像在Bullseye版本之后，底层的树莓派驱动由Raspicam切换成libcamera。libcamera是一个开源的软件栈（后面会称呼为驱动，方便理解），方便于第三方移植和开发自己的摄像头驱动。截止到20231211，官方已经针对libcamera提供了pycamera2库，方便用户使用Python程序调用
https://www.raspberrypi.com 树莓派官方libcamera程序使用详细说明

树莓派buster系统版本（也就是老版本）使用Raspicam摄像头库，目前只支持三个型号的摄像头，OV5647，IMX219（带加密芯片），IMX477（带加密芯片） 市场上不带加密芯片的IMX219和IMX477摄像头不支持
可以先更新一下系统：sudo apt update && sudo apt full-upgrade -y   
树莓派bookworm系统版本（新版系统）使用libcamera摄像头库，可以扩展各种型号的摄像头，目前支持的型号如下：
sudo  nano /boot/config.txt 或者 sudo  nano /boot/firmware/config.txt  打开后，找到   camera_auto_detect=1   这条，把后面的数字1改为0  ，    camera_auto_detect=0
在最后面添加下面内容
#dtoverlay=ov5647
#dtoverlay=imx219
#dtoverlay=imx219,cam0
#dtoverlay=imx477
#dtoverlay=imx290,clock-frequency=37125000
#dtoverlay=imx378
#dtoverlay=ov9281
#dtoverlay=imx296
#dtoverlay=imx519
#dtoverlay=imx708
#dtoverlay=imx708,vcm=0    这里是设置关闭自动对焦功能
使用哪个型号的摄像头，就去掉前面的#号，保存，重启
针对树莓派5，或者树莓派CM3和CM4,这些型号,都支持2个摄像头,设置方式如下:
sudo  nano /boot/config.txt  或者 sudo  nano /boot/firmware/config.txt ，在最后面添加下面内容
dtoverlay=imx219         
dtoverlay=imx219,cam0
以上dtoverlay=imx219     这条默认对应的接口是CSI/DSI1
dtoverlay=imx219,cam0   这条设置对应的接口是CSI/DSI0

树莓派5上使用IMX290，还需要添加json文件到指令目录才能使用。操作如下：
sudo wget https://www.waveshare.net/w/upload/7/7a/Imx290.zip
sudo unzip Imx290.zip
sudo cp imx290.json /usr/share/libcamera/ipa/rpi/pisp
sudo  nano /boot/firmware/config.txt
dtoverlay=imx290,clock-frequency=37125000,cam0


保存重启后可以通过    rpicam-hello --list-cameras     这个命令查看是否识别到对应的摄像头
以下是操作摄像头的一下指令：
rpicam-hello -h   #可以查看详细用法

sudo rpicam-hello -t 0 --camera 0
sudo rpicam-hello -t 0 --camera 1
rpicam-jpeg --camera 1 -t 2000 -o test.jpg
rpicam-jpeg --camera 0 -t 2000 -o test.jpg
rpicam-hello
rpicam-hello -t 0
rpicam-jpeg -o test.jpg
rpicam-jpeg -o test.jpg -t 2000 --width 640 --height 480
rpicam-still --output test.jpg
rpicam-vid -t 10s -o test.h264
通过SSH操作上面的命令，可能无法查看摄像头的实时图像，最好是在树莓派上接显示器和鼠标键盘，再使用上面的指令，就可以看到实时图像
可以通过libcamera -h  查看libcamera的详细介绍
在测试IMX296全彩摄像头如果出现颜色不能正常显示，可以尝试使用 sudo apt-get full-upgrade  更新系统，重启后再测试，一般都能解决问题。

树莓派buster系统版本的摄像头拍照指令：
可以参考：树莓派摄像头模块应用程序文档翻译
raspistill -o 1.jpg -t 2000
raspistill -cs 0 -o 1.jpg -t 2000
raspistill -cs 1 -o 2.jpg -t 2000
sudo raspivid -t 0 -cs 0
sudo raspivid -t 0 -cs 1
raspistill -3d sbs -w 1280 -h 480 -o 1.jpg

raspivid -t 0 -f -w 640 -h 480    强制全屏显示
raspivid -t 0 -w 1920 -h 1080 -fps 30 -sa 100

raspivid -o 1.h264    默认5秒

raspivid -o 1.h264 -t 10000     时间单位毫秒

raspivid -o 1.h264 -t 10000 -w 1280 -h 720  分辨率设置

raspivid -o 1.h264 -t 10000 -w 1280 -h 720  -fps 24   视频帧率设置

# 两秒钟（时间单位为毫秒）延迟后拍摄一张照片，并保存为 image.jpg
raspistill -t 2000 -o image.jpg

# 拍摄一张自定义大小的照片。
raspistill -t 2000 -o image.jpg -w 640 -h 480

# 降低图像质量，减小文件尺寸
raspistill -t 2000 -o image.jpg -q 5

# 强制使预览窗口出现在坐标为 100,100 的位置，并且尺寸为宽 300 和高 200 像素。
raspistill -t 2000 -o image.jpg -p 100,100,300,200

# 禁用预览窗口
raspistill -t 2000 -o image.jpg -n

# 将图像保存为 PNG 文件（无损压缩格式，但是要比 JPEG 速度慢）。注意，当选择图像编码时，文件扩展名将被忽略。
raspistill -t 2000 -o image.png –e png

# 向 JPEG 文件中添加一些 EXIF 信息。该命令将会把作者名称标签设置为 Dreamcolor，GPS 海拔高度为 123.5米。
raspistill -t 2000 -o image.jpg -x IFD0.Artist=Dreamcolor -x GPS.GPSAltitude=1235/10

# 设置浮雕风格图像特效
raspistill -t 2000 -o image.jpg -ifx emboss

# 设置 YUV 图像的 U 和 V 通道为指定的值（128:128 为黑白图像）
raspistill -t 2000 -o image.jpg -cfx 128:128

# 仅显示两秒钟预览图像，而不对图像进行保存。
raspistill -t 2000

# 间隔获取图片，在 10 分钟（10 分钟 = 600000 毫秒）的时间里，每 10 秒获取一张，并且命名为 image_number_001_today.jpg，image_number_002_today.jpg... 的形式，并且最后一张照片将命名为 latest.jpg。
raspistill -t 600000 -tl 10000 -o image_num_%03d_today.jpg -l latest.jpg

# 获取一张照片并发送至标准输出设备
raspistill -t 2000 -o -

# 获取一张照片并保存为一个文件
raspistill -t 2000 -o - > my_file.jpg

#摄像头一直工作，当按下回车键时获取一张照片。
raspistill -t 0 -k -o my_pics%02d.jpg

视频捕捉
图像尺寸和预览设置与图像捕捉相同。录制的视频默认尺寸为 1080p（1920×1080）

# 使用默认设置录制一段 5 秒钟的视频片段（1080p30）
raspivid -t 5000 -o video.h264

# 使用指定码率（3.5Mbits/s）录制一段 5 秒钟的视频片段
raspivid -t 5000 -o video.h264 -b 3500000

# 使用指定帧率（5fps）录制一段 5 秒钟的视频片段
raspivid -t 5000 -o video.h264 -f 5

# 发送到标准输出设备一段 5 秒钟经过编码的摄像头流图像
raspivid -t 5000 -o -

# 保存到文件一段 5 秒钟经过编码的摄像头流图像
raspivid -t 5000 -o - > my_file.h264

