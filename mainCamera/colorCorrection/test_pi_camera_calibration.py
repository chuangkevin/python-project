#!/usr/bin/env python3
"""
Pi Camera V5647 色彩校正 + 軟片模擬整合測試
"""

import cv2
import numpy as np
import os
from enhanced_film_simulation import EnhancedFilmSimulation

def create_test_image() -> np.ndarray:
    """創建戶外場景測試圖像"""
    # 創建一個模擬戶外場景的測試圖像
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    
    # 天空區域（上半部）- 藍色
    img[0:150, :] = [200, 130, 50]  # BGR: 藍天
    
    # 植被區域（中部）- 綠色
    img[150:250, :] = [50, 150, 30]  # BGR: 草地/樹木
    
    # 建築物區域（下部）- 灰色/棕色
    img[250:400, 0:200] = [120, 140, 160]  # 建築物
    img[250:400, 200:400] = [80, 100, 140]   # 陰影區域
    img[250:400, 400:600] = [140, 160, 180]  # 明亮區域
    
    # 添加一些膚色區域（模擬人物）
    img[280:320, 220:260] = [140, 170, 200]  # 膚色
    
    # 添加一些噪音，模擬 Pi Camera 特性
    noise = np.random.normal(0, 5, img.shape).astype(np.int16)
    img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    return img

def test_color_calibration():
    """測試色彩校正系統"""
    print("🧪 Pi Camera V5647 色彩校正系統測試")
    print("=" * 50)
    
    # 建立增強軟片模擬系統（啟用色彩校正）
    film_sim = EnhancedFilmSimulation(enable_calibration=True)
    
    # 建立測試圖像
    test_img = create_test_image()
    print("✅ 已創建戶外場景測試圖像")
    
    # 顯示相機資訊
    camera_info = film_sim.get_camera_info()
    print(f"📷 相機配置: {camera_info.get('name', 'Unknown')}")
    
    # 分析圖像特徵
    analysis = film_sim.analyze_image_for_rd1(test_img)
    print(f"\n📊 圖像分析結果:")
    print(f"   場景類型: {analysis.get('scene_type', 'unknown')}")
    print(f"   亮度等級: {analysis.get('brightness_level', 'unknown')}")
    print(f"   建議白平衡: {analysis.get('wb_suggestion', 'A')}")
    print(f"   建議品質: {analysis.get('quality_suggestion', 'N')}")
    print(f"   建議拍攝數: {analysis.get('shots_estimation', '50')}")
    
    # 測試不同的處理模式
    print(f"\n🎞️ 軟片模擬測試:")
    
    # 1. 僅色彩校正
    corrected_only, rd1_analysis = film_sim.process_for_rd1_display(test_img, enable_color_correction=True)
    print("   ✅ Pi Camera V5647 色彩校正完成")
    
    # 2. 色彩校正 + Classic Chrome
    classic_chrome_result = film_sim.apply_simulation(test_img, 'CLASSIC_CHROME', apply_color_correction=True)
    print("   ✅ Classic Chrome (含色彩校正) 完成")
    
    # 3. 色彩校正 + Kodak Portra 400
    portra_result = film_sim.apply_simulation(test_img, 'KODAK_PORTRA_400', apply_color_correction=True)
    print("   ✅ Kodak Portra 400 (含色彩校正) 完成")
    
    # 4. 比較無色彩校正的結果
    classic_chrome_no_correction = film_sim.apply_simulation(test_img, 'CLASSIC_CHROME', apply_color_correction=False)
    print("   ✅ Classic Chrome (無色彩校正) 完成")
    
    # 儲存測試結果
    outputs_dir = "calibration_test_outputs"
    if not os.path.exists(outputs_dir):
        os.makedirs(outputs_dir)
    
    cv2.imwrite(f"{outputs_dir}/01_original.jpg", test_img)
    cv2.imwrite(f"{outputs_dir}/02_color_corrected.jpg", corrected_only)
    cv2.imwrite(f"{outputs_dir}/03_classic_chrome_with_correction.jpg", classic_chrome_result)
    cv2.imwrite(f"{outputs_dir}/04_portra_400_with_correction.jpg", portra_result)
    cv2.imwrite(f"{outputs_dir}/05_classic_chrome_no_correction.jpg", classic_chrome_no_correction)
    
    print(f"\n💾 測試結果已儲存到: {outputs_dir}/")
    
    # 計算處理效果差異
    def calculate_difference(img1, img2):
        diff = np.abs(img1.astype(float) - img2.astype(float)).mean()
        return diff
    
    print(f"\n📈 處理效果分析:")
    print(f"   原圖 vs 色彩校正: {calculate_difference(test_img, corrected_only):.2f}")
    print(f"   有校正 vs 無校正 Classic Chrome: {calculate_difference(classic_chrome_result, classic_chrome_no_correction):.2f}")
    
    # RD-1 錶盤設定建議
    print(f"\n🎛️ RD-1 錶盤建議設定:")
    wb_values = ["A", "☀", "⛅", "☁", "💡", "💡"]
    quality_values = ["R", "H", "N"]
    shots_values = ["E", "10", "20", "50", "100", "500"]
    
    wb_index = wb_values.index(analysis.get('wb_suggestion', 'A')) if analysis.get('wb_suggestion', 'A') in wb_values else 0
    quality_index = quality_values.index(analysis.get('quality_suggestion', 'N')) if analysis.get('quality_suggestion', 'N') in quality_values else 2
    shots_index = shots_values.index(analysis.get('shots_estimation', '50')) if analysis.get('shots_estimation', '50') in shots_values else 3
    
    print(f"   白平衡錶盤: {wb_index} ({analysis.get('wb_suggestion', 'A')})")
    print(f"   品質錶盤: {quality_index} ({analysis.get('quality_suggestion', 'N')})")
    print(f"   拍攝數錶盤: {shots_index} ({analysis.get('shots_estimation', '50')})")
    
    return True

def test_batch_processing():
    """測試批次處理功能"""
    print("\n🔄 批次處理測試")
    print("-" * 30)
    
    film_sim = EnhancedFilmSimulation(enable_calibration=True)
    test_img = create_test_image()
    
    # 測試多種軟片模擬
    simulations_to_test = [
        'CLASSIC_CHROME',
        'KODAK_PORTRA_400',
        'VELVIA',
        'PROVIA'
    ]
    
    for sim in simulations_to_test:
        try:
            result = film_sim.apply_simulation(test_img, sim, apply_color_correction=True)
            print(f"   ✅ {sim} 處理成功")
        except Exception as e:
            print(f"   ❌ {sim} 處理失敗: {e}")
    
    print("🎉 批次處理測試完成")

if __name__ == "__main__":
    try:
        # 主要測試
        test_color_calibration()
        
        # 批次處理測試
        test_batch_processing()
        
        print("\n🎉 所有測試完成！")
        print("\n💡 使用建議:")
        print("   1. 將此系統整合到 RD-1 相機主程式")
        print("   2. 根據錶盤分析結果自動調整錶盤顯示")
        print("   3. 在 Live-View 中啟用即時色彩校正")
        print("   4. 儲存照片時套用軟片模擬效果")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
