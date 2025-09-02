"""
快速測試改進後的軟片模擬效果
"""

import cv2
import numpy as np
import os
from film_simulation import FujifilmSimulation

def create_test_image():
    """創建一個測試圖像"""
    # 創建一個彩色測試圖像，包含不同亮度和色彩區域
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    
    # 漸層背景
    for i in range(400):
        for j in range(600):
            img[i, j] = [
                int(100 + 100 * (i / 400)),      # 藍色通道
                int(50 + 150 * (j / 600)),       # 綠色通道  
                int(150 + 80 * ((i + j) / 1000)) # 紅色通道
            ]
    
    # 添加一些幾何形狀作為測試元素
    cv2.rectangle(img, (50, 50), (150, 150), (255, 100, 100), -1)   # 紅色方形
    cv2.rectangle(img, (200, 50), (300, 150), (100, 255, 100), -1)  # 綠色方形
    cv2.rectangle(img, (350, 50), (450, 150), (100, 100, 255), -1)  # 藍色方形
    
    # 膚色測試區域
    cv2.rectangle(img, (50, 200), (150, 300), (180, 140, 120), -1)  # 模擬膚色
    
    # 中性灰階測試
    for i in range(5):
        gray_val = 50 + i * 40
        cv2.rectangle(img, (200 + i * 50, 200), (240 + i * 50, 300), 
                     (gray_val, gray_val, gray_val), -1)
    
    return img

def test_improved_simulations():
    """測試改進後的軟片模擬"""
    
    # 建立輸出資料夾
    os.makedirs('test_improved', exist_ok=True)
    
    # 初始化軟片模擬器
    sim = FujifilmSimulation()
    
    # 創建測試圖像
    test_img = create_test_image()
    cv2.imwrite('test_improved/original_test.jpg', test_img)
    
    print("🧪 測試改進後的軟片模擬效果...")
    
    # 重點測試改進的軟片模擬
    improved_sims = ['PROVIA', 'Velvia', 'REALA_ACE', 'Classic_Chrome']
    
    for sim_name in improved_sims:
        try:
            print(f"處理 {sim_name}...")
            result = sim.apply(test_img, sim_name)
            output_path = f'test_improved/{sim_name}_improved.jpg'
            cv2.imwrite(output_path, result)
            
            # 計算平均亮度
            gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
            avg_brightness = np.mean(gray)
            
            print(f"✓ {sim_name} 完成 - 平均亮度: {avg_brightness:.1f}")
            
        except Exception as e:
            print(f"✗ {sim_name} 失敗: {e}")
    
    print("🎉 測試完成！檢查 test_improved 資料夾中的結果")
    
    # 如果有參考圖像，也處理它
    reference_images = ['../../../analogGauge/rd-1_gauge.jpg']
    
    for ref_img_path in reference_images:
        if os.path.exists(ref_img_path):
            print(f"\n📸 處理參考圖像: {ref_img_path}")
            
            ref_img = cv2.imread(ref_img_path)
            if ref_img is not None:
                # 調整大小以加快處理
                height, width = ref_img.shape[:2]
                if width > 800:
                    new_width = 800
                    new_height = int(height * (new_width / width))
                    ref_img = cv2.resize(ref_img, (new_width, new_height))
                
                # 儲存原始圖像
                cv2.imwrite('test_improved/reference_original.jpg', ref_img)
                
                for sim_name in improved_sims:
                    try:
                        result = sim.apply(ref_img, sim_name)
                        output_path = f'test_improved/reference_{sim_name}.jpg'
                        cv2.imwrite(output_path, result)
                        print(f"✓ 參考圖像 {sim_name} 完成")
                    except Exception as e:
                        print(f"✗ 參考圖像 {sim_name} 失敗: {e}")

if __name__ == "__main__":
    test_improved_simulations()
