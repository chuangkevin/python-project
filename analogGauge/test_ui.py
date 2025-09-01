"""
Epson RD-1 指針錶盤測試UI
提供滑桿和按鈕來手動調整指針數值，即時預覽效果
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import time
from rd1_gauge import RD1Gauge

class RD1GaugeTestUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Epson RD-1 指針錶盤測試工具")
        self.root.geometry("1000x700")
        
        # 初始化指針模組
        self.gauge = RD1Gauge(width=200, height=200)
        
        # 當前選擇的指針類型
        self.current_gauge_type = tk.StringVar(value="SHOTS")
        
        # 自動更新標志
        self.auto_update = True
        self.update_thread = None
        
        # 顯示模式
        self.display_mode = tk.StringVar(value="integrated")  # integrated, 2x2, single
        
        self.setup_ui()
        self.start_update_thread()
        
    def setup_ui(self):
        """設置用戶界面"""
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 左側控制面板
        control_frame = ttk.LabelFrame(main_frame, text="指針控制", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # 顯示模式選擇
        ttk.Label(control_frame, text="顯示模式:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        display_modes = ["integrated", "2x2", "single"]
        self.display_combo = ttk.Combobox(control_frame, textvariable=self.display_mode, 
                                         values=display_modes, state="readonly", width=15)
        self.display_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        self.display_combo.bind("<<ComboboxSelected>>", self.on_display_mode_changed)
        
        # 指針類型選擇
        ttk.Label(control_frame, text="選擇指針類型:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        gauge_types = ["SHOTS", "WB", "BATTERY", "QUALITY"]
        self.gauge_combo = ttk.Combobox(control_frame, textvariable=self.current_gauge_type, 
                                       values=gauge_types, state="readonly", width=20)
        self.gauge_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        self.gauge_combo.bind("<<ComboboxSelected>>", self.on_gauge_type_changed)
        
        # 數值控制區域
        self.setup_value_controls(control_frame)
        
        # 所有指針狀態顯示
        self.setup_status_display(control_frame)
        
        # 批量控制按鈕
        self.setup_batch_controls(control_frame)
        
        # 右側預覽面板
        preview_frame = ttk.LabelFrame(main_frame, text="即時預覽", padding="10")
        preview_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 動態預覽標題
        self.preview_title_label = ttk.Label(preview_frame, text="RD-1 整合錶盤:")
        self.preview_title_label.grid(row=0, column=0, pady=5)
        
        # 主預覽
        self.main_preview_label = ttk.Label(preview_frame)
        self.main_preview_label.grid(row=1, column=0, pady=10)
        
        # 單個指針預覽 (僅在single模式顯示)
        self.single_preview_label = ttk.Label(preview_frame)
        self.single_preview_label.grid(row=2, column=0, pady=10)
        
        # 配置網格權重
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        control_frame.columnconfigure(1, weight=1)
        
    def setup_value_controls(self, parent):
        """設置數值控制元件"""
        
        # 數值控制框架
        value_frame = ttk.LabelFrame(parent, text="數值調整", padding="10")
        value_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # 滑桿控制
        ttk.Label(value_frame, text="數值索引:").grid(row=0, column=0, sticky=tk.W)
        self.value_var = tk.IntVar(value=0)
        self.value_scale = ttk.Scale(value_frame, from_=0, to=5, orient=tk.HORIZONTAL, 
                                   variable=self.value_var, command=self.on_value_changed)
        self.value_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10)
        
        self.value_label = ttk.Label(value_frame, text="E")
        self.value_label.grid(row=0, column=2, padx=5)
        
        # 按鈕控制
        button_frame = ttk.Frame(value_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="◀ 上一個", command=self.prev_value).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="下一個 ▶", command=self.next_value).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="重置", command=self.reset_current).pack(side=tk.LEFT, padx=5)
        
        # 具體數值選擇
        ttk.Label(value_frame, text="直接選擇:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        self.direct_value_var = tk.StringVar()
        self.direct_value_combo = ttk.Combobox(value_frame, textvariable=self.direct_value_var,
                                              state="readonly", width=15)
        self.direct_value_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=10, pady=(10, 0))
        self.direct_value_combo.bind("<<ComboboxSelected>>", self.on_direct_value_changed)
        
        value_frame.columnconfigure(1, weight=1)
        
    def setup_status_display(self, parent):
        """設置狀態顯示區域"""
        
        status_frame = ttk.LabelFrame(parent, text="所有指針狀態", padding="10")
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.status_text = tk.Text(status_frame, height=8, width=40, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
    def setup_batch_controls(self, parent):
        """設置批量控制按鈕"""
        
        batch_frame = ttk.LabelFrame(parent, text="批量操作", padding="10")
        batch_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(batch_frame, text="全部重置", command=self.reset_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(batch_frame, text="隨機設置", command=self.randomize_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(batch_frame, text="演示動畫", command=self.demo_animation).pack(side=tk.LEFT, padx=5)
        
        # 保存/載入按鈕
        ttk.Button(batch_frame, text="保存圖像", command=self.save_images).pack(side=tk.RIGHT, padx=5)
        
    def on_gauge_type_changed(self, event=None):
        """指針類型改變時的處理"""
        gauge_type = self.current_gauge_type.get()
        config = self.gauge.GAUGE_CONFIGS[gauge_type]
        
        # 更新滑桿範圍
        max_value = len(config["values"]) - 1
        self.value_scale.configure(to=max_value)
        
        # 更新當前數值
        current_index = self.gauge.current_values[gauge_type]
        self.value_var.set(current_index)
        
        # 更新直接選擇下拉框
        self.direct_value_combo['values'] = config["values"]
        self.direct_value_var.set(config["values"][current_index])
        
        # 更新標籤
        self.update_value_label()
        
    def on_value_changed(self, value):
        """滑桿數值改變時的處理"""
        gauge_type = self.current_gauge_type.get()
        index = int(float(value))
        
        self.gauge.set_value(gauge_type, index)
        self.update_value_label()
        
        # 同步更新直接選擇
        config = self.gauge.GAUGE_CONFIGS[gauge_type]
        self.direct_value_var.set(config["values"][index])
        
    def on_direct_value_changed(self, event=None):
        """直接選擇數值改變時的處理"""
        gauge_type = self.current_gauge_type.get()
        value_str = self.direct_value_var.get()
        
        config = self.gauge.GAUGE_CONFIGS[gauge_type]
        try:
            index = config["values"].index(value_str)
            self.gauge.set_value(gauge_type, index)
            self.value_var.set(index)
            self.update_value_label()
        except ValueError:
            pass
            
    def update_value_label(self):
        """更新數值標籤"""
        gauge_type = self.current_gauge_type.get()
        current_value = self.gauge.get_value(gauge_type)
        current_index = self.gauge.current_values[gauge_type]
        self.value_label.config(text=f"{current_value} ({current_index})")
        
    def prev_value(self):
        """上一個數值"""
        current_index = self.value_var.get()
        if current_index > 0:
            self.value_var.set(current_index - 1)
            self.on_value_changed(current_index - 1)
            
    def next_value(self):
        """下一個數值"""
        gauge_type = self.current_gauge_type.get()
        config = self.gauge.GAUGE_CONFIGS[gauge_type]
        current_index = self.value_var.get()
        max_index = len(config["values"]) - 1
        
        if current_index < max_index:
            self.value_var.set(current_index + 1)
            self.on_value_changed(current_index + 1)
            
    def reset_current(self):
        """重置當前指針"""
        self.value_var.set(0)
        self.on_value_changed(0)
        
    def reset_all(self):
        """重置所有指針"""
        for gauge_type in self.gauge.GAUGE_CONFIGS:
            self.gauge.set_value(gauge_type, 0)
        
        # 如果當前選擇的指針被重置，更新UI
        self.on_gauge_type_changed()
        
    def randomize_all(self):
        """隨機設置所有指針"""
        import random
        
        for gauge_type in self.gauge.GAUGE_CONFIGS:
            config = self.gauge.GAUGE_CONFIGS[gauge_type]
            max_index = len(config["values"]) - 1
            random_index = random.randint(0, max_index)
            self.gauge.set_value(gauge_type, random_index)
            
        # 更新當前UI
        self.on_gauge_type_changed()
        
    def on_display_mode_changed(self, event=None):
        """顯示模式改變時的處理"""
        mode = self.display_mode.get()
        
        # 更新預覽標題
        titles = {
            "integrated": "RD-1 整合錶盤:",
            "2x2": "所有指針 (2x2 布局):",
            "single": "當前選擇指針:"
        }
        self.preview_title_label.config(text=titles.get(mode, "預覽:"))
        
        # 根據模式顯示/隱藏單個指針預覽
        if mode == "single":
            self.single_preview_label.grid(row=2, column=0, pady=10)
        else:
            self.single_preview_label.grid_remove()
        
    def demo_animation(self):
        """演示動畫 - 所有四個指針一起動"""
        def animate():
            # 所有指針的最大索引
            gauge_configs = {
                "SHOTS": len(self.gauge.GAUGE_CONFIGS["SHOTS"]["values"]) - 1,
                "WB": len(self.gauge.GAUGE_CONFIGS["WB"]["values"]) - 1,
                "BATTERY": len(self.gauge.GAUGE_CONFIGS["BATTERY"]["values"]) - 1,
                "QUALITY": len(self.gauge.GAUGE_CONFIGS["QUALITY"]["values"]) - 1
            }
            
            max_steps = max(gauge_configs.values()) + 1
            
            # 正向動畫 - 所有指針一起移動
            for step in range(max_steps):
                if not self.auto_update:
                    break
                    
                for gauge_type, max_idx in gauge_configs.items():
                    # 按比例計算每個指針的位置
                    target_idx = min(step, max_idx)
                    self.gauge.set_value(gauge_type, target_idx)
                
                # 更新當前選中指針的UI
                current_gauge = self.current_gauge_type.get()
                current_max = gauge_configs[current_gauge]
                current_idx = min(step, current_max)
                self.root.after(0, lambda idx=current_idx: self.value_var.set(idx))
                self.root.after(0, self.update_value_label)
                
                time.sleep(0.8)
                
            # 反向動畫 - 所有指針一起移動
            for step in range(max_steps - 1, -1, -1):
                if not self.auto_update:
                    break
                    
                for gauge_type, max_idx in gauge_configs.items():
                    target_idx = min(step, max_idx)
                    self.gauge.set_value(gauge_type, target_idx)
                
                # 更新當前選中指針的UI
                current_gauge = self.current_gauge_type.get()
                current_max = gauge_configs[current_gauge]
                current_idx = min(step, current_max)
                self.root.after(0, lambda idx=current_idx: self.value_var.set(idx))
                self.root.after(0, self.update_value_label)
                
                time.sleep(0.8)
                
        # 在新線程中執行動畫
        threading.Thread(target=animate, daemon=True).start()
        
    def save_images(self):
        """保存當前圖像"""
        try:
            mode = self.display_mode.get()
            saved_files = []
            
            if mode == "integrated":
                # 保存整合錶盤
                integrated_img = self.gauge.draw_all_gauges("integrated")
                integrated_img.save("rd1_integrated_display.png")
                saved_files.append("rd1_integrated_display.png")
                
            elif mode == "single":
                # 保存單個指針
                gauge_type = self.current_gauge_type.get()
                single_img = self.gauge.draw_gauge(gauge_type)
                filename = f"gauge_{gauge_type.lower()}.png"
                single_img.save(filename)
                saved_files.append(filename)
                
            else:  # 2x2
                # 保存所有指針
                all_img = self.gauge.draw_all_gauges("2x2")
                all_img.save("all_gauges_2x2.png")
                saved_files.append("all_gauges_2x2.png")
            
            # 同時保存當前所有模式
            integrated_img = self.gauge.draw_all_gauges("integrated")
            integrated_img.save("rd1_integrated_display.png")
            if "rd1_integrated_display.png" not in saved_files:
                saved_files.append("rd1_integrated_display.png")
            
            file_list = "\n- ".join(saved_files)
            messagebox.showinfo("保存成功", f"圖像已保存:\n- {file_list}")
        except Exception as e:
            messagebox.showerror("保存失敗", f"保存圖像時發生錯誤:\n{str(e)}")
            
    def update_previews(self):
        """更新預覽圖像"""
        try:
            # 更新動畫狀態
            self.gauge.update_animation()
            
            mode = self.display_mode.get()
            
            # 更新主預覽
            if mode == "integrated":
                main_img = self.gauge.draw_all_gauges("integrated")
                # 整合錶盤已經是450x450，適當縮放
                main_img = main_img.resize((400, 400), Image.Resampling.LANCZOS)
            elif mode == "2x2":
                main_img = self.gauge.draw_all_gauges("2x2")
                main_img = main_img.resize((400, 400), Image.Resampling.LANCZOS)
            else:  # single
                gauge_type = self.current_gauge_type.get()
                main_img = self.gauge.draw_gauge(gauge_type)
                main_img = main_img.resize((300, 300), Image.Resampling.LANCZOS)
            
            main_photo = ImageTk.PhotoImage(main_img)
            self.main_preview_label.configure(image=main_photo)
            self.main_preview_label.image = main_photo  # 保持引用
            
            # 更新單個指針預覽 (僅在single模式)
            if mode == "single":
                gauge_type = self.current_gauge_type.get()
                single_img = self.gauge.draw_gauge(gauge_type)
                single_img = single_img.resize((200, 200), Image.Resampling.LANCZOS)
                single_photo = ImageTk.PhotoImage(single_img)
                self.single_preview_label.configure(image=single_photo)
                self.single_preview_label.image = single_photo  # 保持引用
            
        except Exception as e:
            print(f"更新預覽時發生錯誤: {e}")
            
    def update_status(self):
        """更新狀態顯示"""
        try:
            info = self.gauge.get_gauge_info()
            
            self.status_text.config(state=tk.NORMAL)
            self.status_text.delete(1.0, tk.END)
            
            for gauge_type, data in info.items():
                line = f"{data['name']}: {data['current_value']} ({data['current_index']}/{data['total_values']-1})\n"
                self.status_text.insert(tk.END, line)
                
            self.status_text.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"更新狀態時發生錯誤: {e}")
            
    def start_update_thread(self):
        """開始更新線程"""
        def update_loop():
            while self.auto_update:
                try:
                    self.root.after(0, self.update_previews)
                    self.root.after(0, self.update_status)
                    time.sleep(0.1)  # 100ms 更新間隔
                except:
                    break
                    
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()
        
        # 初始化UI
        self.on_gauge_type_changed()
        self.on_display_mode_changed()
        
    def on_closing(self):
        """關閉應用時的清理"""
        self.auto_update = False
        if self.update_thread:
            self.update_thread.join(timeout=1)
        self.root.destroy()

def main():
    """主函數"""
    root = tk.Tk()
    app = RD1GaugeTestUI(root)
    
    # 設置關閉事件
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    print("Epson RD-1 指針錶盤測試工具已啟動")
    print("功能說明:")
    print("- 選擇指針類型來測試不同的指針")
    print("- 使用滑桿或直接選擇來調整數值")
    print("- 即時預覽指針變化")
    print("- 批量操作和演示動畫")
    print("- 保存圖像功能")
    
    root.mainloop()

if __name__ == "__main__":
    main()