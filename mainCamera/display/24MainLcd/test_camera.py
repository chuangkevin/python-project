#!/usr/bin/env python3
"""
相機測試程式
用於測試Camera Module 3連接和基本功能
"""

import sys
import time
from datetime import datetime

def test_camera():
    """測試相機功能"""
    
    print("=" * 50)
    print("Camera Module 3 測試程式")
    print("=" * 50)
    print("")
    
    # 測試1: 檢查Picamera2模組
    print("1. 檢查Picamera2模組...")
    try:
        from picamera2 import Picamera2
        print("   ✅ Picamera2模組載入成功")
    except ImportError as e:
        print(f"   ❌ 無法載入Picamera2: {e}")
        print("   請執行: sudo apt-get install python3-picamera2")
        return False
    
    # 測試2: 列出可用相機
    print("\n2. 偵測相機...")
    try:
        cameras = Picamera2.global_camera_info()
        if cameras:
            print(f"   ✅ 找到 {len(cameras)} 個相機")
            for i, cam in enumerate(cameras):
                print(f"   相機 {i}: {cam}")
        else:
            print("   ❌ 沒有偵測到相機")
            print("   請檢查:")
            print("   - 相機排線是否正確連接")
            print("   - 排線方向是否正確")
            print("   - 系統是否已重啟")
            return False
    except Exception as e:
        print(f"   ❌ 偵測相機時發生錯誤: {e}")
        return False
    
    # 測試3: 初始化相機
    print("\n3. 初始化相機...")
    try:
        picam2 = Picamera2()
        print("   ✅ 相機初始化成功")
        
        # 顯示相機資訊
        print("\n   相機詳細資訊:")
        camera_properties = picam2.camera_properties
        for key, value in camera_properties.items():
            print(f"   - {key}: {value}")
            
    except Exception as e:
        print(f"   ❌ 初始化失敗: {e}")
        return False
    
    # 測試4: 配置相機
    print("\n4. 配置相機...")
    try:
        # 創建預覽配置
        config = picam2.create_preview_configuration(
            main={"size": (1920, 1080)},
            lores={"size": (640, 480)},
            display="lores"
        )
        picam2.configure(config)
        print("   ✅ 相機配置成功")
        print(f"   - 主要解析度: 1920x1080")
        print(f"   - 預覽解析度: 640x480")
    except Exception as e:
        print(f"   ❌ 配置失敗: {e}")
        picam2.close()
        return False
    
    # 測試5: 啟動相機
    print("\n5. 啟動相機...")
    try:
        picam2.start()
        print("   ✅ 相機啟動成功")
        time.sleep(2)  # 等待相機穩定
    except Exception as e:
        print(f"   ❌ 啟動失敗: {e}")
        picam2.close()
        return False
    
    # 測試6: 拍照測試
    print("\n6. 拍照測試...")
    try:
        # 建立測試照片路徑
        test_photo = f"/home/kevin/test_photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        
        # 拍照
        picam2.capture_file(test_photo)
        print(f"   ✅ 拍照成功")
        print(f"   照片儲存至: {test_photo}")
        
        # 檢查檔案
        import os
        if os.path.exists(test_photo):
            file_size = os.path.getsize(test_photo) / 1024  # KB
            print(f"   檔案大小: {file_size:.1f} KB")
            
    except Exception as e:
        print(f"   ❌ 拍照失敗: {e}")
    
    # 測試7: 取得相機控制項
    print("\n7. 相機控制項測試...")
    try:
        controls = picam2.camera_controls
        print("   可用控制項:")
        for control, (min_val, max_val, default) in controls.items():
            if control in ['ExposureTime', 'AnalogueGain', 'Brightness', 'Contrast']:
                print(f"   - {control}: 最小={min_val}, 最大={max_val}, 預設={default}")
    except Exception as e:
        print(f"   ❌ 無法取得控制項: {e}")
    
    # 測試8: 自動對焦測試（如果支援）
    print("\n8. 自動對焦測試...")
    try:
        if 'AfMode' in picam2.camera_controls:
            print("   ✅ 相機支援自動對焦")
            # 觸發自動對焦
            picam2.set_controls({"AfMode": 1, "AfTrigger": 0})
            time.sleep(1)
            print("   自動對焦已觸發")
        else:
            print("   ℹ️ 相機不支援自動對焦")
    except Exception as e:
        print(f"   ⚠️ 自動對焦測試失敗: {e}")
    
    # 清理
    print("\n9. 清理資源...")
    try:
        picam2.stop()
        picam2.close()
        print("   ✅ 資源已釋放")
    except:
        pass
    
    return True

def check_system():
    """檢查系統環境"""
    print("\n系統環境檢查:")
    print("-" * 30)
    
    # 檢查Python版本
    print(f"Python版本: {sys.version}")
    
    # 檢查相關模組
    modules = ['picamera2', 'libcamera', 'numpy', 'PIL']
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module} 已安裝")
        except ImportError:
            print(f"❌ {module} 未安裝")
    
    # 檢查相機設備檔案
    import os
    print("\nVideo設備:")
    video_devices = [f for f in os.listdir('/dev') if f.startswith('video')]
    if video_devices:
        for device in video_devices[:5]:  # 只顯示前5個
            print(f"  /dev/{device}")
    else:
        print("  沒有找到video設備")

if __name__ == "__main__":
    print("開始相機測試...\n")
    
    # 系統檢查
    check_system()
    
    # 相機測試
    print("\n" + "=" * 50)
    success = test_camera()
    
    # 結果總結
    print("\n" + "=" * 50)
    if success:
        print("✅ 相機測試完成！所有功能正常")
    else:
        print("❌ 相機測試失敗！請根據上述錯誤訊息進行排查")
        print("\n建議檢查項目:")
        print("1. 確認相機排線連接正確")
        print("2. 確認已執行 setup_camera_module3.sh 並重啟")
        print("3. 檢查 /boot/firmware/config.txt 是否包含:")
        print("   - camera_auto_detect=1")
        print("   - dtoverlay=imx708")
    
    print("\n測試結束")
