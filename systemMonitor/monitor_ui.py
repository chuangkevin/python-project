"""
系統監控即時 UI 界面
顯示 RD-1 風格的系統資源監控錶盤
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import time
from system_gauge import SystemMonitorGauge

class SystemMonitorUI:
    """系統監控 UI 類別"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Usage Monitor")
        # 調整視窗大小適應錶盤顯示 (預設為收合狀態)
        self.root.geometry("520x520")
        self.root.configure(bg='#f0f0f0')
        self.root.resizable(True, True)  # 允許調整大小
        
        # 系統監控實例
        self.monitor = SystemMonitorGauge()
        
        # UI 控制變數
        self.is_running = False
        self.update_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """設置 UI 界面"""
        # 主標題
        title_label = tk.Label(
            self.root, 
            text="🖥️ Usage Monitor", 
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        )
        title_label.pack(pady=10)
        
        # 錶盤顯示區域
        self.gauge_frame = tk.Frame(self.root, bg='white', relief='sunken', bd=2)
        self.gauge_frame.pack(pady=10, padx=20, fill='x')
        
        # 錶盤圖像標籤
        self.gauge_label = tk.Label(self.gauge_frame, bg='white')
        self.gauge_label.pack(expand=True)
        
        # 控制按鈕區域
        control_frame = tk.Frame(self.root, bg='#f0f0f0')
        control_frame.pack(pady=10)
        
        # 開始/停止按鈕
        self.start_button = tk.Button(
            control_frame,
            text="▶️ 開始監控",
            command=self.start_monitoring,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=12
        )
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = tk.Button(
            control_frame,
            text="⏸️ 停止監控", 
            command=self.stop_monitoring,
            bg='#f44336',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=12,
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=5)
        
        # 重新整理按鈕
        refresh_button = tk.Button(
            control_frame,
            text="🔄 手動更新",
            command=self.manual_refresh,
            bg='#2196F3',
            fg='white', 
            font=('Arial', 12, 'bold'),
            width=12
        )
        refresh_button.pack(side='left', padx=5)
        
        # 標籤顯示控制按鈕
        self.label_button = tk.Button(
            control_frame,
            text="🏷️ 隱藏標籤",
            command=self.toggle_labels,
            bg='#FF9800',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=12
        )
        self.label_button.pack(side='left', padx=5)
        
        # 玻璃效果控制按鈕
        self.glass_button = tk.Button(
            control_frame,
            text="✨ 關閉玻璃",
            command=self.toggle_glass_effect,
            bg='#2196F3',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=12
        )
        self.glass_button.pack(side='left', padx=5)
        
        # 折疊控制按鈕區域
        collapse_control_frame = tk.Frame(self.root, bg='#f0f0f0')
        collapse_control_frame.pack(pady=5)
        
        self.collapse_button = tk.Button(
            collapse_control_frame,
            text="� 顯示詳細資訊",  # 預設為隱藏狀態的按鈕文字
            command=self.toggle_details,
            bg='#9E9E9E',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=15
        )
        self.collapse_button.pack()
        
        # 可收合的詳細資訊容器 (預設隱藏)
        self.details_container = tk.Frame(self.root, bg='#f0f0f0')
        # 不使用 pack()，讓它一開始就隱藏
        
        # 詳細資訊區域 (移到容器內)
        info_frame = tk.LabelFrame(
            self.details_container, 
            text="詳細系統資訊",
            bg='#f0f0f0',
            font=('Arial', 11, 'bold')
        )
        info_frame.pack(pady=10, padx=20, fill='x')
        
        # 控制收合狀態 (預設為隱藏)
        self.details_visible = False
        
        # 系統資訊標籤
        self.info_labels = {}
        info_grid = tk.Frame(info_frame, bg='#f0f0f0')
        info_grid.pack(pady=10, padx=10, fill='x')
        
        # 建立資訊標籤
        info_items = [
            ("cpu", "🖥️ CPU:"),
            ("memory", "🧠 記憶體:"),
            ("disk", "💾 硬碟:"),
            ("network", "🌐 網路:")
        ]
        
        for i, (key, label) in enumerate(info_items):
            row = i // 2
            col = (i % 2) * 2
            
            tk.Label(
                info_grid, 
                text=label, 
                font=('Arial', 10, 'bold'),
                bg='#f0f0f0'
            ).grid(row=row, column=col, sticky='w', padx=5, pady=2)
            
            self.info_labels[key] = tk.Label(
                info_grid,
                text="載入中...",
                font=('Arial', 10),
                bg='#f0f0f0',
                width=20
            )
            self.info_labels[key].grid(row=row, column=col+1, sticky='w', padx=5, pady=2)
        
        # 狀態列 (移到容器內)
        self.status_label = tk.Label(
            self.details_container,
            text="💡 點擊「開始監控」開始即時系統監控",
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='#666'
        )
        self.status_label.pack(pady=5)
        
        # 初始顯示
        self.manual_refresh()
        
        # 啟動時自動開始監控
        self.start_monitoring()
        
    def start_monitoring(self):
        """開始即時監控"""
        if not self.is_running:
            self.is_running = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.status_label.config(text="🟢 即時監控中...")
            
            # 啟動監控執行緒
            self.update_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            self.update_thread.start()
    
    def stop_monitoring(self):
        """停止即時監控"""
        self.is_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled') 
        self.status_label.config(text="⏸️ 監控已停止")
        
    def toggle_labels(self):
        """切換標籤顯示狀態"""
        current_state = self.monitor.get_label_visibility()
        new_state = not current_state
        self.monitor.set_label_visibility(new_state)
        
        # 更新按鈕文字
        if new_state:
            self.label_button.config(text="🏷️ 隱藏標籤")
        else:
            self.label_button.config(text="🏷️ 顯示標籤")
    
    def toggle_glass_effect(self):
        """切換玻璃反光效果狀態"""
        current_state = self.monitor.get_glass_effect()
        new_state = not current_state
        self.monitor.set_glass_effect(new_state)
        
        # 更新按鈕文字
        if new_state:
            self.glass_button.config(text="✨ 關閉玻璃")
        else:
            self.glass_button.config(text="✨ 開啟玻璃")
    
    def toggle_details(self):
        """切換詳細資訊顯示狀態"""
        if self.details_visible:
            # 隱藏詳細資訊
            self.details_container.pack_forget()
            self.collapse_button.config(text="🔼 顯示詳細資訊")
            self.details_visible = False
            # 調整視窗大小以適應收合狀態
            self.root.geometry("520x520")
        else:
            # 顯示詳細資訊
            self.details_container.pack(fill='both', expand=True)
            self.collapse_button.config(text="🔽 隱藏詳細資訊")
            self.details_visible = True
            # 恢復原始視窗大小
            self.root.geometry("520x720")
        
    def manual_refresh(self):
        """手動重新整理"""
        try:
            # 更新系統指標
            levels = self.monitor.update_system_metrics()
            
            # 更新錶盤圖像
            self.update_gauge_display()
            
            # 更新詳細資訊
            self.update_detailed_info()
            
            if not self.is_running:
                self.status_label.config(text="✅ 手動更新完成")
                
        except Exception as e:
            self.status_label.config(text=f"❌ 更新失敗: {str(e)}")
    
    def monitoring_loop(self):
        """監控執行緒主迴圈 - 使用與 test_ui.py 相同的 120fps 超完美動畫"""
        while self.is_running:
            try:
                # 每次循環都更新動畫狀態 (與 test_ui.py 相同)
                self.monitor.gauge.update_animation()
                
                # 計數器
                if hasattr(self, 'loop_counter'):
                    self.loop_counter += 1
                else:
                    self.loop_counter = 0
                
                # 每 15 次循環更新一次系統數據 (約每 0.125 秒)
                if self.loop_counter % 15 == 0:
                    self.monitor.update_system_metrics()
                
                # 每 5 次循環更新一次錶盤顯示 (約每 0.04 秒)
                if self.loop_counter % 5 == 0:
                    self.root.after(0, self.update_gauge_display)
                    
                # 每 60 次循環更新一次詳細資訊 (約每 0.5 秒)
                if self.loop_counter % 60 == 0:
                    self.root.after(0, self.update_detailed_info)
                
                # 使用與 test_ui.py 完全相同的更新間隔
                time.sleep(0.008)  # 8.3ms 更新間隔 = 120fps 超完美動畫
                
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(text=f"❌ 監控錯誤: {str(e)}"))
                break
    
    def update_gauge_display(self):
        """更新錶盤顯示"""
        try:
            # 生成錶盤圖像
            gauge_image = self.monitor.draw_system_monitor_display()
            
            # 調整圖像大小適應顯示區域
            display_size = (450, 450)  # 適應 400x400 畫布的顯示
            gauge_image = gauge_image.resize(display_size, Image.Resampling.LANCZOS)
            
            # 轉換為 Tkinter 格式
            photo = ImageTk.PhotoImage(gauge_image)
            self.gauge_label.configure(image=photo)
            self.gauge_label.image = photo  # 保持引用
            
        except Exception as e:
            print(f"錶盤顯示更新失敗: {e}")
            import traceback
            traceback.print_exc()
    
    def update_detailed_info(self):
        """更新詳細資訊顯示"""
        try:
            info = self.monitor.get_detailed_info()
            
            self.info_labels["cpu"].config(text=f"{info['cpu_percent']}")
            self.info_labels["memory"].config(
                text=f"{info['memory_percent']} ({info['memory_used']}/{info['memory_total']})"
            )
            self.info_labels["disk"].config(
                text=f"{info['disk_percent']} ({info['disk_used']}/{info['disk_total']})"
            )
            self.info_labels["network"].config(text=f"{info['net_speed']}")
            
        except Exception as e:
            print(f"詳細資訊更新失敗: {e}")
    
    def run(self):
        """啟動 UI"""
        self.root.mainloop()

def main():
    """主程式進入點"""
    print("啟動系統監控 RD-1 風格錶盤...")
    app = SystemMonitorUI()
    app.run()

if __name__ == "__main__":
    main()