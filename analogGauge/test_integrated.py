"""
測試整合 RD-1 錶盤功能
"""

from rd1_gauge import RD1Gauge

def test_integrated_display():
    """測試整合錶盤顯示"""
    print("測試 RD-1 整合錶盤...")
    
    # 創建指針實例
    gauge = RD1Gauge()
    
    # 設置一些測試值
    print("設置測試數值...")
    gauge.set_value("SHOTS", 2)    # "20"
    gauge.set_value("WB", 1)       # "☀"
    gauge.set_value("BATTERY", 3)  # "3/4"
    gauge.set_value("QUALITY", 1)  # "H"
    
    print("生成整合錶盤圖像...")
    
    # 測試動畫更新
    for i in range(10):
        gauge.update_animation()  # 讓動畫收斂到目標值
    
    # 生成整合錶盤
    integrated_img = gauge.draw_integrated_rd1_display()
    integrated_img.save("test_rd1_integrated.png")
    print("✓ 整合錶盤已保存為 test_rd1_integrated.png")
    
    # 測試不同的數值
    print("\n測試動畫過渡...")
    gauge.set_value("SHOTS", 5)    # "500"
    gauge.set_value("WB", 4)       # "💡" 
    gauge.set_value("BATTERY", 0)  # "E"
    gauge.set_value("QUALITY", 2)  # "N"
    
    # 動畫更新
    for i in range(20):
        gauge.update_animation()
    
    # 生成第二個測試圖像
    integrated_img2 = gauge.draw_integrated_rd1_display()
    integrated_img2.save("test_rd1_integrated_2.png")
    print("✓ 第二個測試錶盤已保存為 test_rd1_integrated_2.png")
    
    # 顯示當前狀態
    print("\n當前指針狀態:")
    info = gauge.get_gauge_info()
    for gauge_type, data in info.items():
        print(f"  {data['name']}: {data['current_value']} (索引: {data['current_index']})")
    
    print("\n測試完成！請檢查生成的圖像文件。")

if __name__ == "__main__":
    test_integrated_display()