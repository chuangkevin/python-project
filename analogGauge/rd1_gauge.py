"""
Epson RD-1 風格指針錶盤模組
獨立的指針邏輯，支援四種指針模式
"""

import math
import time
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, List, Union, Optional

class RD1Gauge:
    """Epson RD-1 風格的指針錶盤"""
    
    # 四個指針的配置 (白底配色)
    GAUGE_CONFIGS = {
        "SHOTS": {
            "name": "剩餘拍攝數",
            "values": ["E", "10", "20", "50", "100", "500"],
            "color": (50, 50, 50),     # 深灰指針
            "position": "top_left"
        },
        "WB": {
            "name": "白平衡", 
            "values": ["A", "☀", "⛅", "☁", "💡", "💡"],
            "color": (150, 100, 50),   # 棕色指針
            "position": "top_right"
        },
        "BATTERY": {
            "name": "電池電量",
            "values": ["E", "1/4", "1/2", "3/4", "F"],
            "color": (50, 120, 50),    # 深綠指針
            "position": "bottom_left"
        },
        "QUALITY": {
            "name": "影像品質",
            "values": ["R", "H", "N"],
            "color": (120, 50, 50),    # 深紅指針
            "position": "bottom_right"
        }
    }
    
    def __init__(self, width: int = 240, height: int = 240):
        """
        初始化指針錶盤
        
        Args:
            width: 錶盤寬度
            height: 錶盤高度
        """
        self.width = width
        self.height = height
        self.cx = width // 2
        self.cy = height // 2
        self.r_outer = min(width, height) // 2 - 20
        
        # 當前狀態
        self.current_values = {
            "SHOTS": 0,    # 指向 "E"
            "WB": 0,       # 指向 "A"
            "BATTERY": 4,  # 指向 "F"
            "QUALITY": 0   # 指向 "R"
        }
        
        # 動畫狀態 (用於平滑過渡)
        self.target_values = self.current_values.copy()
        self.animation_values = {k: float(v) for k, v in self.current_values.items()}
        self.animation_speed = 0.04  # 超慢動畫速度配合120fps
        
        # 超細緻化步進 - 每個整數值之間插入更多中間步驟
        self.interpolation_steps = 50  # 每個整數間隔分為50個子步驟
        
    def set_value(self, gauge_type: str, value: Union[int, str]) -> bool:
        """
        設置指針數值
        
        Args:
            gauge_type: 指針類型 ("SHOTS", "WB", "BATTERY", "QUALITY")
            value: 數值索引或具體值
            
        Returns:
            bool: 設置是否成功
        """
        if gauge_type not in self.GAUGE_CONFIGS:
            return False
            
        config = self.GAUGE_CONFIGS[gauge_type]
        
        # 如果是字符串，找到對應索引
        if isinstance(value, str):
            try:
                value = config["values"].index(value)
            except ValueError:
                return False
        
        # 檢查索引範圍
        if 0 <= value < len(config["values"]):
            self.target_values[gauge_type] = value
            return True
        return False
    
    def get_value(self, gauge_type: str) -> Optional[str]:
        """獲取當前指針數值"""
        if gauge_type not in self.GAUGE_CONFIGS:
            return None
        
        config = self.GAUGE_CONFIGS[gauge_type]
        index = int(self.animation_values[gauge_type])
        return config["values"][index]
    
    def update_animation(self):
        """更新動畫狀態 - 細緻化插值"""
        for gauge_type in self.GAUGE_CONFIGS:
            current = self.animation_values[gauge_type]
            target = float(self.target_values[gauge_type])
            
            # 計算更細緻的步進
            diff = target - current
            
            if abs(diff) > 0.001:  # 極小閾值確保超完美平滑
                # 使用極小步進配合120fps
                step_size = diff * self.animation_speed
                
                # 限制單次步進的最大值，配合120fps的極小移動
                max_step = 0.008  # 極小的單次最大移動距離
                if abs(step_size) > max_step:
                    step_size = max_step if step_size > 0 else -max_step
                
                self.animation_values[gauge_type] += step_size
            else:
                self.animation_values[gauge_type] = target
    
    def _calculate_needle_position(self, gauge_type: str) -> tuple:
        """計算指針位置 (支援動畫)"""
        config = self.GAUGE_CONFIGS[gauge_type]
        value_index = self.animation_values[gauge_type]  # 使用動畫值
        num_values = len(config["values"])
        
        # 計算角度 (-120° 到 +120°)
        if num_values > 1:
            angle = math.radians(-120 + (240 * value_index / (num_values - 1)))
        else:
            angle = 0
            
        # 計算指針端點
        needle_length = self.r_outer - 30
        x = self.cx + int(needle_length * math.cos(angle))
        y = self.cy + int(needle_length * math.sin(angle))
        
        return x, y, angle
    
    def draw_gauge(self, gauge_type: str, background_color: tuple = (255, 255, 255)) -> Image.Image:
        """
        繪製單個指針錶盤
        
        Args:
            gauge_type: 指針類型
            background_color: 背景顏色
            
        Returns:
            PIL.Image: 錶盤圖像
        """
        if gauge_type not in self.GAUGE_CONFIGS:
            raise ValueError(f"Invalid gauge type: {gauge_type}")
            
        config = self.GAUGE_CONFIGS[gauge_type]
        
        # 創建畫布
        img = Image.new("RGB", (self.width, self.height), background_color)
        draw = ImageDraw.Draw(img)
        
        # 繪製錶盤外框 (黑色邊框)
        draw.ellipse(
            (self.cx - self.r_outer, self.cy - self.r_outer, 
             self.cx + self.r_outer, self.cy + self.r_outer),
            outline=(50, 50, 50), width=2
        )
        
        # 繪製刻度和標籤
        values = config["values"]
        num_values = len(values)
        
        for i, val in enumerate(values):
            # 計算刻度位置
            angle = math.radians(-120 + (240 * i / (num_values - 1)) if num_values > 1 else 0)
            
            # 刻度線
            tick_start_r = self.r_outer - 15
            tick_end_r = self.r_outer - 5
            tick_start_x = self.cx + int(tick_start_r * math.cos(angle))
            tick_start_y = self.cy + int(tick_start_r * math.sin(angle))
            tick_end_x = self.cx + int(tick_end_r * math.cos(angle))
            tick_end_y = self.cy + int(tick_end_r * math.sin(angle))
            
            draw.line((tick_start_x, tick_start_y, tick_end_x, tick_end_y), 
                     fill=(80, 80, 80), width=2)
            
            # 標籤
            label_r = self.r_outer - 35
            label_x = self.cx + int(label_r * math.cos(angle))
            label_y = self.cy + int(label_r * math.sin(angle))
            
            # 繪製文字（簡單居中）
            text_width = len(str(val)) * 6
            draw.text((label_x - text_width//2, label_y - 8), str(val), 
                     fill=(60, 60, 60))
        
        # 繪製指針
        needle_x, needle_y, angle = self._calculate_needle_position(gauge_type)
        
        # 指針主體
        draw.line((self.cx, self.cy, needle_x, needle_y), 
                 fill=config["color"], width=4)
        
        # 指針中心圓點
        center_r = 8
        draw.ellipse((self.cx - center_r, self.cy - center_r, 
                     self.cx + center_r, self.cy + center_r),
                    fill=config["color"])
        
        # 錶盤名稱 (黑色文字)
        name_y = self.cy + self.r_outer - 60
        text_width = len(config["name"]) * 7
        draw.text((self.cx - text_width//2, name_y), config["name"], 
                 fill=(30, 30, 30))
        
        # 當前數值顯示
        current_val = self.get_value(gauge_type)
        val_y = self.cy + self.r_outer - 40
        val_width = len(str(current_val)) * 8
        draw.text((self.cx - val_width//2, val_y), str(current_val), 
                 fill=config["color"])
        
        return img
    
    def draw_integrated_rd1_display(self) -> Image.Image:
        """
        繪製真正的 RD-1 風格整合錶盤
        根據真實照片：一個大錶盤包含多個小錶盤，每個有自己的指針中心
        
        Returns:
            PIL.Image: RD-1 風格整合錶盤
        """
        # 黑色背景，模仿真實 RD-1 的黑色錶盤
        canvas_size = 400  # 回到合理尺寸
        img = Image.new("RGB", (canvas_size, canvas_size), (15, 15, 15))
        draw = ImageDraw.Draw(img)
        
        cx = cy = canvas_size // 2
        main_radius = 140  # 縮小主錶盤半徑讓整體更緊湊
        
        # 繪製主要錶盤外框 (黑色錶盤，類似照片)
        draw.ellipse((cx - main_radius, cy - main_radius, 
                     cx + main_radius, cy + main_radius),
                    fill=(25, 25, 25), outline=(180, 180, 180), width=3)
        
        # 繪製外圈刻度 (E, 5, 15, 20, 50, 100, 500)
        shots_values = ["E", "5", "15", "20", "50", "100", "500"]
        for i, value in enumerate(shots_values):
            angle_deg = -150 + (300 * i / (len(shots_values) - 1))  # 分佈在300度範圍
            angle = math.radians(angle_deg)
            
            # 刻度線
            tick_start_r = main_radius - 15
            tick_end_r = main_radius - 5
            tick_start_x = cx + int(tick_start_r * math.cos(angle))
            tick_start_y = cy + int(tick_start_r * math.sin(angle))
            tick_end_x = cx + int(tick_end_r * math.cos(angle))
            tick_end_y = cy + int(tick_end_r * math.sin(angle))
            
            draw.line((tick_start_x, tick_start_y, tick_end_x, tick_end_y), 
                     fill=(200, 200, 200), width=2)
            
            # 數值標籤移到錶盤外圍 (像照片一樣)
            label_r = main_radius + 15  # 移到外圍
            label_x = cx + int(label_r * math.cos(angle))
            label_y = cy + int(label_r * math.sin(angle))
            
            text_width = len(value) * 8
            draw.text((label_x - text_width//2, label_y - 8), value, 
                     fill=(255, 255, 255))
        
        # 移除底部 SHOTS 標籤 (不需要)
        
        # 三個小錶盤區域 (恢復之前的完美位置)
        small_gauge_radius = 90  # 恢復之前的大小
        small_gauges = {
            # 左上小錶盤 (WB 白平衡)
            "WB": {
                "center": (cx - 110, cy - 50),  # 恢復之前位置
                "values": ["A", "☀", "⛅", "☁", "💡"],
                "current_index": self.animation_values["WB"]
            },
            # 右上小錶盤 (Quality 品質)
            "QUALITY": {
                "center": (cx + 110, cy - 50),  # 恢復之前位置
                "values": ["R", "H", "N"],
                "current_index": self.animation_values["QUALITY"]
            },
            # 中下小錶盤 (Battery 電池)
            "BATTERY": {
                "center": (cx, cy + 110),  # 恢復之前位置
                "values": ["E", "1/4", "1/2", "3/4", "F"],
                "current_index": self.animation_values["BATTERY"]
            }
        }
        
        # 繪製小錶盤
        for gauge_type, gauge_data in small_gauges.items():
            gx, gy = gauge_data["center"]
            values = gauge_data["values"]
            current_index = gauge_data["current_index"]
            num_values = len(values)
            
            # 小錶盤使用90度扇形範圍，根據照片中實際指針指向方向
            if gauge_type == "WB":  # 左上錶盤，指針指向右下方向
                start_angle = -45   # 從右上開始
                arc_range = 90      # 到右下結束
            elif gauge_type == "QUALITY":  # 右上錶盤，指針指向左下方向  
                start_angle = 135   # 從左下開始
                arc_range = 90      # 到左上結束
            elif gauge_type == "BATTERY":  # 中下錶盤，指針指向上方向
                start_angle = -135  # 從左上開始
                arc_range = 90      # 到右上結束
            else:
                start_angle = -45
                arc_range = 90
            
            # 小錶盤扇形弧線 (不是完整圓圈)
            # 只繪製對應的扇形弧線
            arc_start = start_angle
            arc_end = start_angle + arc_range
            
            # 繪製扇形弧線
            for arc_angle in range(int(arc_start), int(arc_end) + 1, 5):
                angle_rad = math.radians(arc_angle)
                arc_x = gx + int(small_gauge_radius * math.cos(angle_rad))
                arc_y = gy + int(small_gauge_radius * math.sin(angle_rad))
                
                # 畫小點來形成弧線
                draw.ellipse((arc_x - 1, arc_y - 1, arc_x + 1, arc_y + 1),
                           fill=(150, 150, 150))
            
            # 繪製小錶盤刻度和標籤 (90度範圍)
            for i, val in enumerate(values):
                angle = math.radians(start_angle + (arc_range * i / (num_values - 1)) if num_values > 1 else start_angle)
                
                # 小刻度線
                tick_start_r = small_gauge_radius - 10
                tick_end_r = small_gauge_radius - 5
                tick_start_x = gx + int(tick_start_r * math.cos(angle))
                tick_start_y = gy + int(tick_start_r * math.sin(angle))
                tick_end_x = gx + int(tick_end_r * math.cos(angle))
                tick_end_y = gy + int(tick_end_r * math.sin(angle))
                
                draw.line((tick_start_x, tick_start_y, tick_end_x, tick_end_y), 
                         fill=(180, 180, 180), width=1)
                
                # 小標籤 (只顯示關鍵數值以避免擁擠)
                if i == 0 or i == num_values - 1 or (num_values <= 3):
                    label_r = small_gauge_radius - 18
                    label_x = gx + int(label_r * math.cos(angle))
                    label_y = gy + int(label_r * math.sin(angle))
                    
                    text_width = len(str(val)) * 6
                    draw.text((label_x - text_width//2, label_y - 6), str(val), 
                             fill=(200, 200, 200))
            
            # 繪製小錶盤指針 (90度範圍)
            if num_values > 1:
                needle_angle = math.radians(start_angle + (arc_range * current_index / (num_values - 1)))
            else:
                needle_angle = math.radians(start_angle)
                
            needle_length = small_gauge_radius - 15
            needle_x = gx + int(needle_length * math.cos(needle_angle))
            needle_y = gy + int(needle_length * math.sin(needle_angle))
            
            # 指針顏色
            needle_color = self.GAUGE_CONFIGS[gauge_type]["color"]
            
            # 繪製更平滑的指針 (使用多重線條模擬抗鋸齒)
            # 主指針線條
            draw.line((gx, gy, needle_x, needle_y), 
                     fill=needle_color, width=4)
            # 添加半透明邊緣減少鋸齒
            edge_color = tuple(min(255, c + 50) for c in needle_color)
            draw.line((gx, gy, needle_x, needle_y), 
                     fill=edge_color, width=2)
            
            # 指針中心點
            center_r = 4
            draw.ellipse((gx - center_r, gy - center_r, 
                         gx + center_r, gy + center_r),
                        fill=needle_color)
        
        # 中央主指針 (SHOTS - 拍攝數)
        shots_index = self.animation_values["SHOTS"]
        shots_config = self.GAUGE_CONFIGS["SHOTS"]
        shots_num_values = len(shots_config["values"])
        
        if shots_num_values > 1:
            main_needle_angle = math.radians(-150 + (300 * shots_index / (shots_num_values - 1)))
        else:
            main_needle_angle = 0
            
        main_needle_length = main_radius - 50  # 調整主指針長度
        main_needle_x = cx + int(main_needle_length * math.cos(main_needle_angle))
        main_needle_y = cy + int(main_needle_length * math.sin(main_needle_angle))
        
        # 繪製更平滑的主指針
        # 主指針線條 (加厚)
        draw.line((cx, cy, main_needle_x, main_needle_y), 
                 fill=(255, 255, 255), width=6)
        # 添加半透明邊緣減少鋸齒
        draw.line((cx, cy, main_needle_x, main_needle_y), 
                 fill=(220, 220, 220), width=4)
        
        # 主指針中心點
        main_center_r = 8
        draw.ellipse((cx - main_center_r, cy - main_center_r, 
                     cx + main_center_r, cy + main_center_r),
                    fill=(255, 255, 255), outline=(200, 200, 200), width=2)
        
        return img
    
    def draw_all_gauges(self, layout: str = "2x2") -> Image.Image:
        """
        繪製所有四個指針錶盤
        
        Args:
            layout: 布局方式 ("2x2", "1x4", "4x1", "integrated")
            
        Returns:
            PIL.Image: 組合圖像
        """
        if layout == "integrated":
            return self.draw_integrated_rd1_display()
            
        background_color = (255, 255, 255)  # 白底
        
        if layout == "2x2":
            # 2x2 網格布局
            combined_width = self.width * 2
            combined_height = self.height * 2
            combined_img = Image.new("RGB", (combined_width, combined_height), background_color)
            
            gauge_types = ["SHOTS", "WB", "BATTERY", "QUALITY"]
            positions = [(0, 0), (1, 0), (0, 1), (1, 1)]
            
            for gauge_type, (col, row) in zip(gauge_types, positions):
                gauge_img = self.draw_gauge(gauge_type)
                x = col * self.width
                y = row * self.height
                combined_img.paste(gauge_img, (x, y))
                
        elif layout == "1x4":
            # 橫向排列
            combined_width = self.width * 4
            combined_height = self.height
            combined_img = Image.new("RGB", (combined_width, combined_height), background_color)
            
            gauge_types = ["SHOTS", "WB", "BATTERY", "QUALITY"]
            for i, gauge_type in enumerate(gauge_types):
                gauge_img = self.draw_gauge(gauge_type)
                combined_img.paste(gauge_img, (i * self.width, 0))
                
        elif layout == "4x1":
            # 縱向排列
            combined_width = self.width
            combined_height = self.height * 4
            combined_img = Image.new("RGB", (combined_width, combined_height), background_color)
            
            gauge_types = ["SHOTS", "WB", "BATTERY", "QUALITY"]
            for i, gauge_type in enumerate(gauge_types):
                gauge_img = self.draw_gauge(gauge_type)
                combined_img.paste(gauge_img, (0, i * self.height))
        else:
            raise ValueError(f"Invalid layout: {layout}")
            
        return combined_img
    
    def get_gauge_info(self) -> Dict:
        """獲取所有指針的當前狀態信息"""
        info = {}
        for gauge_type in self.GAUGE_CONFIGS:
            config = self.GAUGE_CONFIGS[gauge_type]
            info[gauge_type] = {
                "name": config["name"],
                "current_index": int(self.animation_values[gauge_type]),
                "target_index": self.target_values[gauge_type],
                "current_value": self.get_value(gauge_type),
                "total_values": len(config["values"]),
                "all_values": config["values"]
            }
        return info

if __name__ == "__main__":
    # 簡單測試
    gauge = RD1Gauge()
    
    # 設置一些測試值
    gauge.set_value("SHOTS", 3)  # 指向 "50"
    gauge.set_value("WB", 1)     # 指向 "☀"
    gauge.set_value("BATTERY", 2) # 指向 "1/2"
    gauge.set_value("QUALITY", 1) # 指向 "H"
    
    # 繪製單個錶盤
    img = gauge.draw_gauge("SHOTS")
    img.save("test_single_gauge.png")
    print("測試圖像已保存為 test_single_gauge.png")
    
    # 繪製所有錶盤 (2x2布局)
    all_img = gauge.draw_all_gauges("2x2")
    all_img.save("test_all_gauges.png")
    print("組合圖像已保存為 test_all_gauges.png")
    
    # 繪製整合 RD-1 風格錶盤
    integrated_img = gauge.draw_all_gauges("integrated")
    integrated_img.save("test_integrated_rd1.png")
    print("RD-1整合錶盤已保存為 test_integrated_rd1.png")
    
    print("\n當前指針狀態:")
    for gauge_type, info in gauge.get_gauge_info().items():
        print(f"{info['name']}: {info['current_value']}")