#!/usr/bin/env python3
"""
測試 RAW 格式拍攝腳本
"""

import sys
import os
sys.path.append('/home/kevin')

from ultra_camera_app import UltraCameraApp
import time

def main():
    print("🧪 RAW 拍攝測試")
    print("=" * 40)
    
    # 建立 sample 目錄
    sample_dir = "/tmp/camera_samples"
    os.makedirs(sample_dir, exist_ok=True)
    print(f"📁 樣本目錄: {sample_dir}")
    
    # 初始化相機應用
    app = UltraCameraApp()
    
    try:
        # 初始化相機
        if not app.setup_camera():
            print("❌ 相機初始化失敗")
            return False
        
        print("✅ 相機初始化完成")
        print("📸 準備拍攝最大解析度 RAW 格式...")
        
        # 等待3秒讓相機穩定
        for i in range(3, 0, -1):
            print(f"⏰ {i}...")
            time.sleep(1)
        
        # 拍攝 RAW 格式
        raw_path, jpg_path = app.take_raw_photo(sample_dir)
        
        if raw_path and jpg_path:
            print("✅ 拍攝成功！")
            print(f"RAW 檔案: {raw_path}")
            print(f"JPG 檔案: {jpg_path}")
            
            # 顯示檔案資訊
            if os.path.exists(raw_path):
                raw_size = os.path.getsize(raw_path) / 1024 / 1024
                print(f"RAW 大小: {raw_size:.2f} MB")
            
            if os.path.exists(jpg_path):
                jpg_size = os.path.getsize(jpg_path) / 1024 / 1024
                print(f"JPG 大小: {jpg_size:.2f} MB")
                
            return True
        else:
            print("❌ 拍攝失敗")
            return False
            
    except Exception as e:
        print(f"❌ 測試出現錯誤: {e}")
        return False
        
    finally:
        app.cleanup()

if __name__ == "__main__":
    main()