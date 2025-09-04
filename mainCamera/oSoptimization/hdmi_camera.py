#!/usr/bin/env python3
"""
HDMI 相機程序 - 針對 HDMI 輸出優化
3 秒快速開機相機應用
"""

import cv2
import numpy as np
from picamera2 import Picamera2, Preview
import time
import os

def main():
    print("🚀 啟動 HDMI 相機程序...")
    
    try:
        # 初始化相機
        picam2 = Picamera2()
        
        # 配置相機 - HDMI 全解析度
        camera_config = picam2.create_preview_configuration(
            main={"size": (1920, 1080)},  # HDMI 1080p
            display="main"
        )
        picam2.configure(camera_config)
        
        # 啟動預覽到 HDMI
        picam2.start_preview(Preview.DRM)
        picam2.start()
        
        print("✅ 相機已啟動！HDMI 應該顯示預覽畫面")
        print("按 Ctrl+C 停止程序")
        
        # 主循環
        frame_count = 0
        start_time = time.time()
        
        while True:
            # 簡單的 FPS 計算
            frame_count += 1
            if frame_count % 30 == 0:
                elapsed = time.time() - start_time
                fps = frame_count / elapsed
                print(f"FPS: {fps:.1f}")
            
            time.sleep(0.03)  # ~30 FPS
            
    except KeyboardInterrupt:
        print("\n🛑 程序停止")
    except Exception as e:
        print(f"❌ 錯誤: {e}")
    finally:
        try:
            picam2.stop()
            picam2.close()
        except:
            pass
        print("✅ 相機已關閉")

if __name__ == "__main__":
    main()