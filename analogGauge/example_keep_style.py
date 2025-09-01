"""
示例：使用動態配置保持原有的美麗 RD-1 風格
展示如何配置錶盤並設置數值，同時保持您的精美視覺設計
"""

from rd1_gauge import RD1Gauge

def main():
    # 創建錶盤實例
    gauge = RD1Gauge()
    
    # 配置白平衡錶盤 (保持原有視覺風格)
    gauge.configure_gauge_dynamic(
        gauge_type="WB",
        gauge_purpose="白平衡",
        values=["A(自動)", "晴天", "多雲", "陰天", "白熾燈", "螢光燈"],
        color=(150, 100, 50)  # 棕色指針
    )
    
    # 配置剩餘拍攝數錶盤
    gauge.configure_gauge_dynamic(
        gauge_type="SHOTS",
        gauge_purpose="剩餘拍攝數",
        values=["E", "10", "20", "50", "100", "500"],
        color=(220, 50, 50)  # 紅色指針
    )
    
    # 配置電池錶盤
    gauge.configure_gauge_dynamic(
        gauge_type="BATTERY",
        gauge_purpose="電池電量",
        values=["E", "1/4", "1/2", "3/4", "F"],
        color=(50, 200, 50)  # 綠色指針
    )
    
    # 配置品質錶盤
    gauge.configure_gauge_dynamic(
        gauge_type="QUALITY",
        gauge_purpose="影像品質",
        values=["R", "H", "N"],
        color=(120, 50, 50)  # 深紅指針
    )
    
    # 設置數值
    gauge.set_value("WB", "晴天")        # 白平衡設為晴天
    gauge.set_value("SHOTS", 2)          # 剩餘拍攝數設為 20
    gauge.set_value("BATTERY", "3/4")    # 電池設為 3/4
    gauge.set_value("QUALITY", "H")      # 品質設為高品質
    
    # 更新動畫
    for _ in range(100):
        gauge.update_animation()
    
    # 生成並顯示您美麗的整合錶盤圖像
    img = gauge.draw_integrated_rd1_display()
    img.show()
    
    print("顯示您精美的 RD-1 風格整合錶盤！")

if __name__ == "__main__":
    main()
