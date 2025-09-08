"""
修正的雙螢幕相機控制系統
修正：
1. 主螢幕：圓形輪盤導航選單 (基於 stateInMainScreenWhenStateChange.jpg)
2. 左編碼器：左右旋轉功能，模擬真實編碼器
"""

import tkinter as tk
from tkinter import ttk
import math
from typing import Dict, Any, Optional, Callable
from datetime import datetime


class CircularWheelMenu:
    """圓形輪盤選單 - 基於 stateInMainScreenWhenStateChange.jpg 設計"""
    
    def __init__(self, parent_canvas, callback: Callable):
        self.canvas = parent_canvas
        self.callback = callback
        
        # 輪盤配置
        self.center_x = 400
        self.center_y = 300
        self.outer_radius = 150
        self.inner_radius = 60
        self.current_selection = 0  # 當前選中的選項索引
        
        # 選項配置 (順時針排列)
        self.options = [
            {"name": "預設", "state": "default", "icon": "○", "angle": 0},
            {"name": "軟片", "state": "film", "icon": "🎞️", "angle": 45},
            {"name": "畫質", "state": "quality", "icon": "⚡", "angle": 90},
            {"name": "白平衡", "state": "wb", "icon": "☀️", "angle": 135},
            {"name": "比例", "state": "ratio", "icon": "📐", "angle": 180},
            {"name": "ISO", "state": "iso", "icon": "📊", "angle": 225},
            {"name": "對焦", "state": "focus", "icon": "●", "angle": 270},
            {"name": "設定", "state": "settings", "icon": "⚙️", "angle": 315}
        ]
    
    def draw_wheel(self):
        """繪製圓形輪盤選單"""
        # 清除之前的繪製
        self.canvas.delete("wheel")
        
        # 繪製外圓
        self.canvas.create_oval(
            self.center_x - self.outer_radius, self.center_y - self.outer_radius,
            self.center_x + self.outer_radius, self.center_y + self.outer_radius,
            fill="#f0f0f0", outline="#cccccc", width=2, tags="wheel"
        )
        
        # 繪製中心圓
        self.canvas.create_oval(
            self.center_x - self.inner_radius, self.center_y - self.inner_radius,
            self.center_x + self.inner_radius, self.center_y + self.inner_radius,
            fill="#000000", outline="#666666", width=2, tags="wheel"
        )
        
        # 繪製分割線和高亮背景
        for i, option in enumerate(self.options):
            angle_rad = math.radians(option["angle"])
            
            # 分割線
            inner_x = self.center_x + self.inner_radius * math.cos(angle_rad)
            inner_y = self.center_y + self.inner_radius * math.sin(angle_rad)
            outer_x = self.center_x + self.outer_radius * math.cos(angle_rad)
            outer_y = self.center_y + self.outer_radius * math.sin(angle_rad)
            
            self.canvas.create_line(
                inner_x, inner_y, outer_x, outer_y,
                fill="#cccccc", width=1, tags="wheel"
            )
            
            # 選項背景 (如果是選中項則高亮)
            if i == self.current_selection:
                # 計算扇形的角度範圍 (45度扇形)
                start_angle = option["angle"] - 22.5
                end_angle = option["angle"] + 22.5
                
                # 繪製高亮扇形 (正確的多邊形)
                points = []
                
                # 內圓弧點
                for angle in range(int(start_angle), int(end_angle) + 1, 3):
                    angle_rad = math.radians(angle)
                    x = self.center_x + self.inner_radius * math.cos(angle_rad)
                    y = self.center_y + self.inner_radius * math.sin(angle_rad)
                    points.extend([x, y])
                
                # 外圓弧點 (逆序)
                for angle in range(int(end_angle), int(start_angle) - 1, -3):
                    angle_rad = math.radians(angle)
                    x = self.center_x + self.outer_radius * math.cos(angle_rad)
                    y = self.center_y + self.outer_radius * math.sin(angle_rad)
                    points.extend([x, y])
                
                if len(points) >= 6:  # 至少3個點
                    self.canvas.create_polygon(
                        points, fill="#4a90e2", outline="", tags="wheel"
                    )
        
        # 重繪中心圓 (確保在高亮扇形上方)
        self.canvas.create_oval(
            self.center_x - self.inner_radius, self.center_y - self.inner_radius,
            self.center_x + self.inner_radius, self.center_y + self.inner_radius,
            fill="#000000", outline="#666666", width=2, tags="wheel"
        )
        
        # 重繪所有選項圖標和文字 (確保在扇形上方)
        for i, option in enumerate(self.options):
            angle_rad = math.radians(option["angle"])
            
            # 選項圖標和文字
            icon_radius = (self.outer_radius + self.inner_radius) / 2
            icon_x = self.center_x + icon_radius * math.cos(angle_rad)
            icon_y = self.center_y + icon_radius * math.sin(angle_rad)
            
            # 圖標
            self.canvas.create_text(
                icon_x, icon_y - 10, text=option["icon"],
                font=("Arial", 16), fill="#333333" if i != self.current_selection else "#ffffff",
                tags="wheel"
            )
            
            # 文字
            self.canvas.create_text(
                icon_x, icon_y + 10, text=option["name"],
                font=("Arial", 10), fill="#333333" if i != self.current_selection else "#ffffff",
                tags="wheel"
            )
        
        # 中心指示器
        self.canvas.create_text(
            self.center_x, self.center_y, text="○",
            font=("Arial", 20), fill="#ffffff", tags="wheel"
        )
    
    def rotate_selection(self, direction: int):
        """旋轉選擇 (direction: 1=順時針, -1=逆時針)"""
        self.current_selection = (self.current_selection + direction) % len(self.options)
        self.draw_wheel()
        
        # 提供聲音反饋
        print(f"輪盤旋轉: {self.options[self.current_selection]['name']}")
        
        # 使用預覽回調，不隱藏選單
        current_option = self.options[self.current_selection]
        if hasattr(self, 'preview_callback') and self.preview_callback:
            self.preview_callback(current_option['state'])
    
    def select_current(self):
        """選擇當前項目"""
        current_option = self.options[self.current_selection]
        print(f"選擇: {current_option['name']}")
        
        if self.callback:
            self.callback(current_option['state'])


class MainScreenWindow:
    """主螢幕窗口 - Live View + 圓形輪盤導航"""
    
    def __init__(self, state_callback: Optional[Callable] = None):
        self.state_callback = state_callback
        self.current_state = "default"
        self.overlay_visible = False
        
        # 創建主螢幕窗口
        self.root = tk.Toplevel()
        self.root.title("主螢幕 - Live View")
        self.root.geometry("800x600")
        self.root.configure(bg="#000000")
        
        self._create_interface()
        self._start_live_view_simulation()
    
    def _create_interface(self):
        """創建主螢幕界面"""
        # Live View 區域
        self.live_view_frame = tk.Frame(self.root, bg="#000000")
        self.live_view_frame.pack(fill="both", expand=True)
        
        # Live View 標籤
        self.live_view_label = tk.Label(
            self.live_view_frame,
            text="LIVE VIEW",
            font=("Arial", 24, "bold"),
            fg="#ffffff",
            bg="#000000"
        )
        self.live_view_label.pack(expand=True)
        
        # 導航覆蓋層 (初始隱藏)
        self.overlay_frame = tk.Frame(self.root, bg="#000000")
        
        # 創建圓形輪盤導航
        self.overlay_canvas = tk.Canvas(
            self.overlay_frame,
            width=800, height=600,
            bg="#000000",
            highlightthickness=0
        )
        self.overlay_canvas.pack(fill="both", expand=True)
        
        # 創建圓形輪盤選單
        self.wheel_menu = CircularWheelMenu(self.overlay_canvas, self._select_state)
        # 設定預覽回調 (僅用於圓形螢幕切換，不隱藏選單)
        self.wheel_menu.preview_callback = self._preview_state
    
    def _select_state(self, state: str):
        """選擇狀態"""
        self.current_state = state
        print(f"主螢幕: 選擇狀態 {state}")
        
        # 通知圓形螢幕
        if self.state_callback:
            print(f"主螢幕: 呼叫狀態回調 - {state}")
            self.state_callback(state)
        else:
            print("主螢幕: 警告 - 狀態回調為空!")
        
        # 隱藏覆蓋層
        self.hide_overlay()
    
    def _preview_state(self, state: str):
        """預覽狀態 (旋轉時觸發，不隱藏選單)"""
        print(f"主螢幕: 預覽狀態 {state}")
        
        # 只通知圓形螢幕切換，不隱藏選單
        if self.state_callback:
            print(f"主螢幕: 呼叫狀態預覽回調 - {state}")
            self.state_callback(state)
    
    def show_overlay(self):
        """顯示圓形輪盤導航覆蓋層"""
        if self.overlay_visible:
            return
            
        self.overlay_visible = True
        
        # 隱藏 Live View
        self.live_view_frame.pack_forget()
        
        # 顯示覆蓋層
        self.overlay_frame.pack(fill="both", expand=True)
        
        # 繪製輪盤
        self.wheel_menu.draw_wheel()
        
        print("主螢幕: 顯示圓形輪盤導航")
        
        # 3秒後自動隱藏
        if hasattr(self, '_hide_timer'):
            self.root.after_cancel(self._hide_timer)
        self._hide_timer = self.root.after(3000, self.hide_overlay)
    
    def hide_overlay(self):
        """隱藏圓形輪盤導航"""
        if not self.overlay_visible:
            return
            
        self.overlay_visible = False
        
        # 隱藏覆蓋層
        self.overlay_frame.pack_forget()
        
        # 恢復 Live View
        self.live_view_frame.pack(fill="both", expand=True)
        
        print("主螢幕: 隱藏圓形輪盤導航，返回 Live View")
    
    def rotate_wheel(self, direction: int):
        """旋轉輪盤 (由編碼器觸發)"""
        if self.overlay_visible:
            self.wheel_menu.rotate_selection(direction)
            
            # 重設自動隱藏計時器
            if hasattr(self, '_hide_timer'):
                self.root.after_cancel(self._hide_timer)
            self._hide_timer = self.root.after(3000, self.hide_overlay)
    
    def select_wheel_item(self):
        """選擇輪盤當前項目"""
        if self.overlay_visible:
            self.wheel_menu.select_current()
    
    def _start_live_view_simulation(self):
        """啟動 Live View 模擬"""
        self._update_live_view()
        self.root.after(1000, self._start_live_view_simulation)
    
    def _update_live_view(self):
        """更新 Live View 顯示"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.live_view_label.configure(
            text=f"📸 LIVE VIEW\n\n相機取景器模擬\n當前時間: {current_time}\n模式: {self.current_state}"
        )


class CircularScreenWindow:
    """圓形螢幕窗口 - RD-1 整合式錶盤"""
    
    def __init__(self):
        self.current_mode = "default"
        
        # 錶盤配置
        self.gauge_configs = {
            "SHOTS": {
                "values": ["1/1000", "1/500", "1/250", "1/125", "1/60", "1/30"],
                "color": (255, 255, 255),
                "current_index": 3
            },
            "WB": {
                "values": ["AUTO", "SUNNY", "CLOUD", "SHADE"],
                "color": (255, 100, 100),
                "current_index": 0
            },
            "QUALITY": {
                "values": ["BASIC", "FINE", "S.FINE"],
                "color": (100, 255, 100),
                "current_index": 1
            },
            "BATTERY": {
                "values": ["LOW", "MID", "FULL"],
                "color": (100, 100, 255),
                "current_index": 2
            }
        }
        
        # 錶盤尺寸
        self.canvas_size = 400
        self.cx = self.cy = self.canvas_size // 2
        self.main_radius = 140
        self.small_gauge_radius = 90
        
        # 創建圓形螢幕窗口
        self.root = tk.Toplevel()
        self.root.title("圓形螢幕 - RD-1 錶盤")
        self.root.geometry("450x500")
        self.root.configure(bg="#0f0f0f")
        
        self._create_interface()
        self._update_display()
    
    def _create_interface(self):
        """創建圓形螢幕界面"""
        # 標題
        title_label = tk.Label(
            self.root,
            text="RD-1 整合式錶盤",
            font=("Arial", 14, "bold"),
            fg="#ffffff",
            bg="#0f0f0f"
        )
        title_label.pack(pady=(10, 5))
        
        # 錶盤 Canvas
        self.canvas = tk.Canvas(
            self.root,
            width=self.canvas_size,
            height=self.canvas_size,
            bg="#0f0f0f",
            highlightthickness=0
        )
        self.canvas.pack(pady=10)
        
        # 模式顯示
        self.mode_label = tk.Label(
            self.root,
            text="模式: 預設 (整合式錶盤)",
            fg="#00ff00",
            bg="#0f0f0f",
            font=("Arial", 12)
        )
        self.mode_label.pack(pady=5)
    
    def _draw_integrated_rd1_display(self):
        """繪製 RD-1 整合式錶盤"""
        # 清除 Canvas
        self.canvas.delete("all")
        
        # 主錶盤背景
        self.canvas.create_oval(
            self.cx - self.main_radius, self.cy - self.main_radius,
            self.cx + self.main_radius, self.cy + self.main_radius,
            fill="#191919", outline="#b4b4b4", width=3
        )
        
        # 主錶盤刻度 (SHOTS)
        shots_config = self.gauge_configs["SHOTS"]
        shots_values = shots_config["values"]
        
        for i, value in enumerate(shots_values):
            angle_deg = -150 + (300 * i / (len(shots_values) - 1))
            angle = math.radians(angle_deg)
            
            # 刻度線
            tick_start_r = self.main_radius - 15
            tick_end_r = self.main_radius - 5
            tick_start_x = self.cx + int(tick_start_r * math.cos(angle))
            tick_start_y = self.cy + int(tick_start_r * math.sin(angle))
            tick_end_x = self.cx + int(tick_end_r * math.cos(angle))
            tick_end_y = self.cy + int(tick_end_r * math.sin(angle))
            
            self.canvas.create_line(
                tick_start_x, tick_start_y, tick_end_x, tick_end_y,
                fill="#c8c8c8", width=2
            )
            
            # 數值標籤
            label_r = self.main_radius + 15
            label_x = self.cx + int(label_r * math.cos(angle))
            label_y = self.cy + int(label_r * math.sin(angle))
            
            self.canvas.create_text(
                label_x, label_y, text=value, fill="#ffffff",
                font=("Arial", 10), anchor="center"
            )
        
        # 三個小錶盤
        small_gauges = {
            "WB": {
                "center": (self.cx - 110, self.cy - 50),
                "start_angle": -45,
                "arc_range": 90
            },
            "QUALITY": {
                "center": (self.cx + 110, self.cy - 50),
                "start_angle": 135,
                "arc_range": 90
            },
            "BATTERY": {
                "center": (self.cx, self.cy + 110),
                "start_angle": -135,
                "arc_range": 90
            }
        }
        
        # 繪製小錶盤
        for gauge_type, gauge_layout in small_gauges.items():
            gx, gy = gauge_layout["center"]
            start_angle = gauge_layout["start_angle"]
            arc_range = gauge_layout["arc_range"]
            
            gauge_config = self.gauge_configs[gauge_type]
            values = gauge_config["values"]
            current_index = gauge_config["current_index"]
            gauge_color = gauge_config["color"]
            num_values = len(values)
            
            # 扇形弧線
            for arc_angle in range(int(start_angle), int(start_angle + arc_range) + 1, 5):
                angle_rad = math.radians(arc_angle)
                arc_x = gx + int(self.small_gauge_radius * math.cos(angle_rad))
                arc_y = gy + int(self.small_gauge_radius * math.sin(angle_rad))
                
                self.canvas.create_oval(
                    arc_x - 1, arc_y - 1, arc_x + 1, arc_y + 1,
                    fill="#969696", outline=""
                )
            
            # 小錶盤刻度
            for i, val in enumerate(values):
                if num_values > 1:
                    angle = math.radians(start_angle + (arc_range * i / (num_values - 1)))
                else:
                    angle = math.radians(start_angle)
                
                # 刻度線
                tick_start_r = self.small_gauge_radius - 10
                tick_end_r = self.small_gauge_radius - 5
                tick_start_x = gx + int(tick_start_r * math.cos(angle))
                tick_start_y = gy + int(tick_start_r * math.sin(angle))
                tick_end_x = gx + int(tick_end_r * math.cos(angle))
                tick_end_y = gy + int(tick_end_r * math.sin(angle))
                
                self.canvas.create_line(
                    tick_start_x, tick_start_y, tick_end_x, tick_end_y,
                    fill="#b4b4b4", width=1
                )
                
                # 標籤
                if i == 0 or i == num_values - 1 or (num_values <= 3):
                    label_r = self.small_gauge_radius - 18
                    label_x = gx + int(label_r * math.cos(angle))
                    label_y = gy + int(label_r * math.sin(angle))
                    
                    self.canvas.create_text(
                        label_x, label_y, text=str(val), fill="#c8c8c8",
                        font=("Arial", 8), anchor="center"
                    )
            
            # 小錶盤指針
            if num_values > 1:
                needle_angle = math.radians(start_angle + (arc_range * current_index / (num_values - 1)))
            else:
                needle_angle = math.radians(start_angle)
            
            needle_length = self.small_gauge_radius - 15
            needle_x = gx + int(needle_length * math.cos(needle_angle))
            needle_y = gy + int(needle_length * math.sin(needle_angle))
            
            self._draw_sharp_needle(gx, gy, needle_x, needle_y, gauge_color, width=6)
            
            # 指針中心點
            center_r = 4
            color_hex = f"#{gauge_color[0]:02x}{gauge_color[1]:02x}{gauge_color[2]:02x}"
            self.canvas.create_oval(
                gx - center_r, gy - center_r, 
                gx + center_r, gy + center_r,
                fill=color_hex, outline=""
            )
            
            # 標籤
            self.canvas.create_text(
                gx, gy, text=gauge_type, fill="#ffffff",
                font=("Arial", 10, "bold"), anchor="center"
            )
        
        # 主指針 (SHOTS)
        shots_index = self.gauge_configs["SHOTS"]["current_index"]
        shots_num_values = len(self.gauge_configs["SHOTS"]["values"])
        
        if shots_num_values > 1:
            main_needle_angle = math.radians(-150 + (300 * shots_index / (shots_num_values - 1)))
        else:
            main_needle_angle = 0
        
        main_needle_length = self.main_radius - 50
        main_needle_x = self.cx + int(main_needle_length * math.cos(main_needle_angle))
        main_needle_y = self.cy + int(main_needle_length * math.sin(main_needle_angle))
        
        self._draw_sharp_needle(self.cx, self.cy, main_needle_x, main_needle_y, (255, 255, 255), width=10)
        
        # 主指針中心點
        center_r = 8
        self.canvas.create_oval(
            self.cx - center_r, self.cy - center_r, 
            self.cx + center_r, self.cy + center_r,
            fill="#ffffff", outline=""
        )
    
    def _draw_sharp_needle(self, cx, cy, nx, ny, color, width=8):
        """繪製尖銳指針"""
        color_hex = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
        
        dx = nx - cx
        dy = ny - cy
        length = math.sqrt(dx*dx + dy*dy)
        
        if length == 0:
            return
        
        ux = dx / length
        uy = dy / length
        vx = -uy
        vy = ux
        
        half_width = width // 2
        
        points = [
            cx + vx * half_width, cy + vy * half_width,
            cx - vx * half_width, cy - vy * half_width,
            nx, ny,
            cx + vx * half_width, cy + vy * half_width
        ]
        
        self.canvas.create_polygon(points, fill=color_hex, outline=color_hex)
    
    def _draw_single_mode_display(self):
        """繪製單一模式專用錶盤"""
        # 清除 Canvas
        self.canvas.delete("all")
        
        # 簡單單一錶盤
        self.canvas.create_oval(
            50, 50, 350, 350,
            fill="#191919", outline="#b4b4b4", width=2
        )
        
        mode_names = {
            "film": "軟片模擬",
            "quality": "相片畫質",
            "wb": "白平衡", 
            "ratio": "照片比例",
            "iso": "ISO",
            "focus": "對焦模式",
            "settings": "系統設定"
        }
        display_name = mode_names.get(self.current_mode, self.current_mode)
        
        self.canvas.create_text(
            200, 200, text=f"{display_name}\n專用錶盤",
            fill="#ffffff", font=("Arial", 16), anchor="center"
        )
    
    def switch_mode(self, mode: str):
        """切換顯示模式"""
        self.current_mode = mode
        
        if mode == "default":
            self.mode_label.configure(text="模式: 預設 (RD-1 整合式錶盤)")
        else:
            mode_names = {
                "film": "軟片模擬",
                "quality": "相片畫質",
                "wb": "白平衡",
                "ratio": "照片比例", 
                "iso": "ISO",
                "focus": "對焦模式",
                "settings": "系統設定"
            }
            display_name = mode_names.get(mode, mode)
            self.mode_label.configure(text=f"模式: {display_name} (專用錶盤)")
        
        self._update_display()
        print(f"圓形螢幕: 切換到 {mode} 模式")
    
    def _update_display(self):
        """更新錶盤顯示"""
        if self.current_mode == "default":
            self._draw_integrated_rd1_display()
        else:
            self._draw_single_mode_display()


class ControlPanelWindow:
    """控制面板 - 模擬編碼器控制 (含左右旋轉功能)"""
    
    def __init__(self, main_screen: MainScreenWindow, circular_screen: CircularScreenWindow):
        self.main_screen = main_screen
        self.circular_screen = circular_screen
        
        # 創建控制面板窗口
        self.root = tk.Toplevel()
        self.root.title("控制面板 - 編碼器模擬")
        self.root.geometry("350x500")
        self.root.configure(bg="#2d2d2d")
        
        self._create_interface()
    
    def _create_interface(self):
        """創建控制面板界面"""
        # 標題
        title_label = tk.Label(
            self.root,
            text="🎛️ 控制面板",
            font=("Arial", 16, "bold"),
            fg="#ffffff",
            bg="#2d2d2d"
        )
        title_label.pack(pady=(10, 20))
        
        # 左編碼器 (狀態切換)
        left_frame = tk.LabelFrame(
            self.root,
            text="左編碼器 - 狀態切換",
            fg="#ffffff",
            bg="#2d2d2d",
            font=("Arial", 12, "bold")
        )
        left_frame.pack(fill="x", padx=20, pady=10)
        
        # 編碼器旋轉控制
        rotate_frame = tk.Frame(left_frame, bg="#2d2d2d")
        rotate_frame.pack(pady=10)
        
        tk.Button(
            rotate_frame,
            text="◀ 逆時針",
            font=("Arial", 12),
            width=12,
            height=2,
            bg="#4a4a4a",
            fg="#ffffff",
            command=lambda: self._left_encoder_rotate(-1),
            relief="raised",
            bd=3
        ).pack(side="left", padx=5)
        
        tk.Button(
            rotate_frame,
            text="順時針 ▶",
            font=("Arial", 12),
            width=12,
            height=2,
            bg="#4a4a4a",
            fg="#ffffff",
            command=lambda: self._left_encoder_rotate(1),
            relief="raised",
            bd=3
        ).pack(side="right", padx=5)
        
        # 編碼器按下
        tk.Button(
            left_frame,
            text="按下編碼器 (顯示選單)",
            font=("Arial", 12),
            width=25,
            height=1,
            bg="#2d4a3e",
            fg="#ffffff",
            command=self._left_encoder_pressed,
            relief="raised",
            bd=3
        ).pack(pady=5)
        
        tk.Button(
            left_frame,
            text="✓ 選擇當前項目",
            font=("Arial", 12),
            width=25,
            height=1,
            bg="#3e2d4a",
            fg="#ffffff",
            command=self._select_current_item,
            relief="raised",
            bd=2
        ).pack(pady=5)
        
        tk.Button(
            left_frame,
            text="返回預設",
            font=("Arial", 12),
            width=25,
            height=1,
            bg="#2d4a3e",
            fg="#ffffff",
            command=self._return_to_default,
            relief="raised",
            bd=2
        ).pack(pady=5)
        
        # 右編碼器 (參數調整)  
        right_frame = tk.LabelFrame(
            self.root,
            text="右編碼器 - 參數調整",
            fg="#ffffff",
            bg="#2d2d2d",
            font=("Arial", 12, "bold")
        )
        right_frame.pack(fill="x", padx=20, pady=10)
        
        # 右編碼器旋轉控制
        right_rotate_frame = tk.Frame(right_frame, bg="#2d2d2d")
        right_rotate_frame.pack(pady=10)
        
        tk.Button(
            right_rotate_frame,
            text="◀ 參數 -",
            font=("Arial", 12),
            width=12,
            height=1,
            bg="#4a4a4a",
            fg="#ffffff",
            command=lambda: self._adjust_parameter(-1),
            relief="raised",
            bd=2
        ).pack(side="left", padx=5)
        
        tk.Button(
            right_rotate_frame,
            text="參數 + ▶",
            font=("Arial", 12),
            width=12,
            height=1,
            bg="#4a4a4a",
            fg="#ffffff",
            command=lambda: self._adjust_parameter(1),
            relief="raised",
            bd=2
        ).pack(side="right", padx=5)
        
        # 快門按鈕
        shutter_frame = tk.LabelFrame(
            self.root,
            text="快門",
            fg="#ffffff",
            bg="#2d2d2d",
            font=("Arial", 12, "bold")
        )
        shutter_frame.pack(fill="x", padx=20, pady=10)
        
        self.shutter_button = tk.Button(
            shutter_frame,
            text="📸 快門",
            font=("Arial", 16, "bold"),
            width=20,
            height=2,
            bg="#2d4a3e",
            fg="#ffffff",
            command=self._shutter_pressed,
            relief="raised",
            bd=3
        )
        self.shutter_button.pack(pady=10)
    
    def _left_encoder_rotate(self, direction: int):
        """左編碼器旋轉 - 在圓形輪盤選單中旋轉選擇"""
        print(f"左編碼器旋轉: {'順時針' if direction > 0 else '逆時針'}")
        
        # 如果導航選單沒有顯示，先顯示
        if not self.main_screen.overlay_visible:
            self.main_screen.show_overlay()
        
        # 旋轉輪盤選擇
        self.main_screen.rotate_wheel(direction)
    
    def _left_encoder_pressed(self):
        """左編碼器按下 - 顯示圓形輪盤選單"""
        print("左編碼器按下: 顯示圓形輪盤選單")
        self.main_screen.show_overlay()
    
    def _select_current_item(self):
        """選擇當前輪盤項目"""
        print("選擇當前輪盤項目")
        self.main_screen.select_wheel_item()
    
    def _return_to_default(self):
        """返回預設模式"""
        print("返回預設模式")
        self.main_screen.current_state = "default"
        self.circular_screen.switch_mode("default")
        self.main_screen.hide_overlay()
    
    def _adjust_parameter(self, direction: int):
        """右編碼器調整參數"""
        current_mode = self.circular_screen.current_mode
        
        if current_mode == "default":
            # 預設模式調整 SHOTS
            config = self.circular_screen.gauge_configs["SHOTS"]
            current_index = config["current_index"]
            max_index = len(config["values"]) - 1
            
            new_index = max(0, min(max_index, current_index + direction))
            config["current_index"] = new_index
            
            current_value = config["values"][new_index]
            print(f"參數調整: SHOTS = {current_value}")
        else:
            # 其他模式的專用參數調整
            print(f"參數調整: {current_mode} 模式參數 {'+' if direction > 0 else '-'}")
        
        # 更新圓形螢幕顯示
        self.circular_screen._update_display()
    
    def _shutter_pressed(self):
        """快門按下"""
        print("快門觸發!")
        
        # 按鈕動畫
        self.shutter_button.configure(state="disabled", bg="#666666")
        
        # 1秒後恢復
        self.root.after(1000, self._shot_complete)
    
    def _shot_complete(self):
        """拍攝完成"""
        self.shutter_button.configure(state="normal", bg="#2d4a3e")


class FixedDualScreenSystem:
    """修正的雙螢幕相機控制系統"""
    
    def __init__(self):
        # 創建主窗口
        self.root = tk.Tk()
        self.root.title("修正的雙螢幕相機控制系統")
        self.root.geometry("400x250")
        self.root.configure(bg="#0f0f0f")
        
        # 先創建各個窗口（沒有回調）
        self.main_screen = MainScreenWindow(None)  # 先不設定回調
        self.circular_screen = CircularScreenWindow()
        self.control_panel = ControlPanelWindow(self.main_screen, self.circular_screen)
        
        # 設定狀態回調（現在 circular_screen 已經存在）
        def on_state_changed(state):
            print(f"系統: 狀態變更回調 - {state}")
            self.circular_screen.switch_mode(state)
        
        # 將回調設定到主螢幕
        self.main_screen.state_callback = on_state_changed
        
        self._create_main_interface()
        
        print("修正的雙螢幕相機控制系統啟動")
        print("- 主螢幕: Live View + 圓形輪盤導航")
        print("- 圓形螢幕: RD-1 整合式錶盤")
        print("- 控制面板: 完整編碼器模擬 (含左右旋轉)")
    
    def _create_main_interface(self):
        """創建主界面"""
        # 標題
        title_label = tk.Label(
            self.root,
            text="修正的雙螢幕相機控制系統",
            font=("Arial", 16, "bold"),
            fg="#ffffff",
            bg="#0f0f0f"
        )
        title_label.pack(pady=20)
        
        # 修正說明
        info_label = tk.Label(
            self.root,
            text="圓形輪盤導航選單\n左編碼器左右旋轉功能\nRD-1 整合式錶盤\n\n使用說明:\n左編碼器 = 狀態選擇 (旋轉+按下)\n右編碼器 = 參數調整",
            font=("Arial", 11),
            fg="#cccccc",
            bg="#0f0f0f",
            justify="center"
        )
        info_label.pack(pady=10)
        
        # 退出按鈕
        tk.Button(
            self.root,
            text="退出系統",
            font=("Arial", 12),
            width=15,
            height=1,
            bg="#8b0000",
            fg="#ffffff",
            command=self.root.quit,
            relief="raised",
            bd=2
        ).pack(pady=20)
    
    def run(self):
        """啟動系統"""
        self.root.mainloop()


if __name__ == "__main__":
    # 啟動修正的雙螢幕系統
    system = FixedDualScreenSystem()
    system.run()