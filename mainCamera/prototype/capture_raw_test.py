#!/usr/bin/env python3
"""
使用運行中的相機拍攝 RAW 測試
"""

import sys
import os
import time
from datetime import datetime
from picamera2 import Picamera2

def capture_raw_sample():
    """拍攝 RAW 格式樣本"""
    print("🧪 開始 RAW 拍攝測試")
    
    try:
        # 初始化相機
        picam2 = Picamera2()
        
        # 設定最大解析度 RAW 配置
        raw_config = picam2.create_still_configuration(
            main={"size": (2592, 1944)},  # 最大解析度
            raw={"size": (2592, 1944), "format": "SGBRG10"}  # RAW 格式
        )
        
        picam2.configure(raw_config)
        picam2.start()
        
        # 等待相機穩定
        print("⏰ 等待相機穩定...")
        time.sleep(3)
        
        # 產生檔案名稱
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sample_dir = "/tmp/camera_samples"
        os.makedirs(sample_dir, exist_ok=True)
        
        raw_filename = f"working_raw_{timestamp}.dng"
        jpg_filename = f"working_jpg_{timestamp}.jpg"
        
        raw_filepath = os.path.join(sample_dir, raw_filename)
        jpg_filepath = os.path.join(sample_dir, jpg_filename)
        
        print(f"📸 準備拍攝...")
        
        # 拍攝請求
        request = picam2.capture_request()
        
        # 儲存 RAW 格式
        with open(raw_filepath, "wb") as f:
            f.write(request.make_buffer("raw"))
        
        # 儲存 JPG 格式
        request.save("main", jpg_filepath)
        request.release()
        
        # 檢查檔案大小
        if os.path.exists(raw_filepath):
            raw_size = os.path.getsize(raw_filepath) / 1024 / 1024
            print(f"✅ RAW 儲存成功: {raw_filename} ({raw_size:.2f} MB)")
        
        if os.path.exists(jpg_filepath):
            jpg_size = os.path.getsize(jpg_filepath) / 1024 / 1024
            print(f"✅ JPG 儲存成功: {jpg_filename} ({jpg_size:.2f} MB)")
        
        picam2.stop()
        picam2.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 拍攝失敗: {e}")
        return False

if __name__ == "__main__":
    capture_raw_sample()