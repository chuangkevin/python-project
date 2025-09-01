"""
創建一個高質量的玻璃覆蓋 PNG 檔案
Create a high-quality glass overlay PNG file for the RD-1 gauge
"""
from PIL import Image, ImageDraw
import math

def create_glass_overlay(size=400):
    """創建玻璃效果覆蓋層"""
    # 創建透明背景圖像
    overlay = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    center_x, center_y = size // 2, size // 2
    radius = size // 2 - 10
    
    # 1. 外圈高光 - 模擬玻璃邊緣反射
    for i in range(5):
        alpha = 40 - i * 8
        draw.ellipse([
            center_x - radius - i, center_y - radius - i,
            center_x + radius + i, center_y + radius + i
        ], outline=(255, 255, 255, alpha), width=2)
    
    # 2. 弧形高光 - 模擬光源反射
    highlight_radius = radius * 0.8
    for angle in range(30, 90, 2):  # 從左上到右上的弧
        x1 = center_x + highlight_radius * math.cos(math.radians(angle))
        y1 = center_y + highlight_radius * math.sin(math.radians(angle))
        x2 = center_x + (highlight_radius + 15) * math.cos(math.radians(angle))
        y2 = center_y + (highlight_radius + 15) * math.sin(math.radians(angle))
        
        alpha = int(60 * math.sin(math.radians(angle - 30)))
        draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, alpha), width=1)
    
    # 3. 中心高光點
    for i in range(3):
        alpha = 80 - i * 20
        draw.ellipse([
            center_x - 8 + i, center_y - 8 + i,
            center_x + 8 - i, center_y + 8 - i
        ], fill=(255, 255, 255, alpha))
    
    # 4. 徑向高光線 - 模擬放射狀反射
    for angle in range(0, 360, 30):
        x1 = center_x + radius * 0.3 * math.cos(math.radians(angle))
        y1 = center_y + radius * 0.3 * math.sin(math.radians(angle))
        x2 = center_x + radius * 0.6 * math.cos(math.radians(angle))
        y2 = center_y + radius * 0.6 * math.sin(math.radians(angle))
        
        alpha = 25
        draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, alpha), width=1)
    
    # 5. 漸變光暈 - 整體玻璃效果
    for r in range(0, radius, 5):
        alpha = int(15 * (1 - r / radius))
        draw.ellipse([
            center_x - r, center_y - r,
            center_x + r, center_y + r
        ], outline=(255, 255, 255, alpha), width=1)
    
    return overlay

if __name__ == "__main__":
    # 創建玻璃覆蓋層
    glass_overlay = create_glass_overlay(400)
    
    # 保存為 PNG
    glass_overlay.save("glass_overlay.png", "PNG")
    print("玻璃覆蓋層已保存為 glass_overlay.png")
    
    # 顯示效果預覽（可選）
    try:
        glass_overlay.show()
    except:
        print("無法顯示預覽，但檔案已成功創建")
