#!/usr/bin/env python3
"""
Ultra Camera App - 專為 RPI HDMI 全螢幕設計
特點：
- 全螢幕 HDMI 輸出
- 無需桌面環境
- 穩定長時間運行
- 基本拍照功能
- 按鍵控制
"""

import cv2
import numpy as np
import os
import time
from datetime import datetime
from picamera2 import Picamera2, Preview
import threading
import signal
import sys

class UltraCameraApp:
    def __init__(self):
        self.picam2 = None
        self.running = True
        self.photo_count = 0
        self.photos_dir = "/home/kevin/Pictures"
        
        # 確保照片目錄存在
        os.makedirs(self.photos_dir, exist_ok=True)
        
        # 設置信號處理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, sig, frame):
        """優雅地處理退出信號"""
        print(f"\n🛑 收到退出信號 ({sig})，正在關閉相機...")
        self.running = False
        
    def setup_camera(self):
        """初始化相機設定"""
        print("📷 初始化相機...")
        
        try:
            self.picam2 = Picamera2()
            
            # 全螢幕配置 - 針對 HDMI 優化
            camera_config = self.picam2.create_preview_configuration(
                main={
                    "size": (1920, 1080),  # Full HD
                    "format": "RGB888"
                },
                display="main"
            )
            
            self.picam2.configure(camera_config)
            
            # 啟動全螢幕預覽到 HDMI
            self.picam2.start_preview(Preview.DRM, 
                                    x=0, y=0, 
                                    width=1920, height=1080)
            
            self.picam2.start()
            
            print("✅ 相機初始化完成 - 全螢幕 HDMI 輸出")
            return True
            
        except Exception as e:
            print(f"❌ 相機初始化失敗: {e}")
            return False
    
    def take_photo(self):
        """拍照功能"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"photo_{timestamp}_{self.photo_count:04d}.jpg"
            filepath = os.path.join(self.photos_dir, filename)
            
            # 拍照
            self.picam2.capture_file(filepath)
            
            self.photo_count += 1
            print(f"📸 照片已儲存: {filename}")
            
            return filepath
            
        except Exception as e:
            print(f"❌ 拍照失敗: {e}")
            return None
    
    def take_raw_photo(self, output_dir="/tmp"):
        """拍攝最大解析度 RAW 格式照片"""
        try:
            # 暫停當前預覽
            self.picam2.stop()
            
            # 設定最大解析度 RAW 格式配置
            raw_config = self.picam2.create_still_configuration(
                main={"size": (2592, 1944)},  # OV5647 最大解析度
                raw={"size": (2592, 1944), "format": "SGBRG10"}  # RAW 格式
            )
            
            self.picam2.configure(raw_config)
            self.picam2.start()
            
            # 等待相機穩定
            time.sleep(2)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            raw_filename = f"raw_5mp_{timestamp}.dng"
            jpg_filename = f"raw_5mp_{timestamp}.jpg"
            
            raw_filepath = os.path.join(output_dir, raw_filename)
            jpg_filepath = os.path.join(output_dir, jpg_filename)
            
            # 拍攝 RAW 和 JPG
            request = self.picam2.capture_request()
            
            # 儲存 RAW 格式 (.dng)
            with open(raw_filepath, "wb") as f:
                f.write(request.make_buffer("raw"))
            
            # 儲存 JPG 格式
            request.save("main", jpg_filepath)
            request.release()
            
            print(f"📸 RAW 照片已儲存:")
            print(f"   RAW: {raw_filename} ({os.path.getsize(raw_filepath) / 1024 / 1024:.1f} MB)")
            print(f"   JPG: {jpg_filename} ({os.path.getsize(jpg_filepath) / 1024 / 1024:.1f} MB)")
            
            # 恢復原預覽配置
            self.setup_camera()
            
            return raw_filepath, jpg_filepath
            
        except Exception as e:
            print(f"❌ RAW 拍攝失敗: {e}")
            # 嘗試恢復原配置
            self.setup_camera()
            return None, None
    
    def display_info_overlay(self):
        """顯示基本資訊"""
        info_lines = [
            "🎬 Ultra Camera App",
            f"📸 已拍攝: {self.photo_count} 張",
            "⌨️  控制: 空白鍵拍照, ESC退出",
            f"📁 儲存至: {self.photos_dir}",
            f"🕒 {datetime.now().strftime('%H:%M:%S')}"
        ]
        
        # 這裡可以加入 overlay 顯示邏輯
        # 目前先在 console 輸出
        return info_lines
    
    def handle_keyboard_input(self):
        """處理鍵盤輸入（在獨立執行緒中）"""
        print("⌨️  鍵盤控制已啟用:")
        print("   空白鍵 - 拍照")
        print("   ESC/Ctrl+C - 退出")
        print("   R - 重新啟動相機")
        
        while self.running:
            try:
                # 這裡可以加入更sophisticated的鍵盤處理
                # 目前使用簡單的時間間隔
                time.sleep(1)
                
            except KeyboardInterrupt:
                self.running = False
                break
    
    def health_check(self):
        """健康檢查"""
        try:
            # 檢查相機是否還在運行
            if self.picam2 is None:
                return False
                
            # 可以加入更多健康檢查
            return True
            
        except:
            return False
    
    def run(self):
        """主程序執行"""
        print("🚀 Ultra Camera App 啟動中...")
        
        # 初始化相機
        if not self.setup_camera():
            print("❌ 相機初始化失敗，程序退出")
            return False
        
        # 啟動鍵盤處理執行緒
        keyboard_thread = threading.Thread(target=self.handle_keyboard_input)
        keyboard_thread.daemon = True
        keyboard_thread.start()
        
        print("✅ Ultra Camera App 已啟動！")
        print("📺 HDMI 全螢幕預覽中...")
        
        # 主循環
        frame_count = 0
        last_info_time = time.time()
        
        try:
            while self.running:
                # 每5秒輸出狀態資訊
                if time.time() - last_info_time > 5:
                    frame_count += 1
                    print(f"🔄 運行狀態: 正常 (循環 {frame_count})")
                    
                    # 健康檢查
                    if not self.health_check():
                        print("⚠️  健康檢查失敗，準備重啟...")
                        break
                        
                    last_info_time = time.time()
                
                # 主循環延遲
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n🛑 收到鍵盤中斷")
        except Exception as e:
            print(f"❌ 運行時錯誤: {e}")
        
        finally:
            self.cleanup()
        
        return True
    
    def cleanup(self):
        """清理資源"""
        print("🧹 正在清理資源...")
        
        self.running = False
        
        if self.picam2:
            try:
                self.picam2.stop_preview()
                self.picam2.stop()
                self.picam2.close()
                print("✅ 相機資源已清理")
            except Exception as e:
                print(f"⚠️  相機清理警告: {e}")
        
        print("✅ Ultra Camera App 已安全關閉")

def main():
    """主函數"""
    print("=" * 50)
    print("🎬 Ultra Camera App for Raspberry Pi")
    print("📺 HDMI 全螢幕相機應用程式")
    print("=" * 50)
    
    app = UltraCameraApp()
    
    try:
        success = app.run()
        exit_code = 0 if success else 1
        
    except Exception as e:
        print(f"❌ 程序異常: {e}")
        exit_code = 1
    
    finally:
        print(f"👋 程序退出 (代碼: {exit_code})")
        sys.exit(exit_code)

if __name__ == "__main__":
    main()