"""
A lightweight wrapper of the project's `systemMonitor/monitor_ui.py` to run the Windows toy example
from within the `analogGauge` package. This file is a near-copy of the original with imports
adjusted for package layout (relative import to `analogGauge.examples.windows_toy.system_gauge`)
so it works when executed as a module: `python -m analogGauge.examples.windows_toy.monitor_ui`.

This example is intended as a usage demonstration only. It expects `psutil` to be installed.
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import time
from .system_gauge import SystemMonitorGauge

class SystemMonitorUI:
    """System monitor UI (example wrapper)"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Usage Monitor (analogGauge example)")
        self.root.geometry("520x520")
        self.root.configure(bg='#f0f0f0')
        self.root.resizable(True, True)

        self.monitor = SystemMonitorGauge()

        self.is_running = False
        self.update_thread = None

        self.setup_ui()

    def setup_ui(self):
        title_label = tk.Label(
            self.root,
            text="🖥️ Usage Monitor (analogGauge example)",
            font=('Arial', 16, 'bold'),
            bg='#f0f0f0'
        )
        title_label.pack(pady=10)

        self.gauge_frame = tk.Frame(self.root, bg='white', relief='sunken', bd=2)
        self.gauge_frame.pack(pady=10, padx=20, fill='x')

        self.gauge_label = tk.Label(self.gauge_frame, bg='white')
        self.gauge_label.pack(expand=True)

        control_frame = tk.Frame(self.root, bg='#f0f0f0')
        control_frame.pack(pady=10)

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

        collapse_control_frame = tk.Frame(self.root, bg='#f0f0f0')
        collapse_control_frame.pack(pady=5)

        self.collapse_button = tk.Button(
            collapse_control_frame,
            text="� 顯示詳細資訊",
            command=self.toggle_details,
            bg='#9E9E9E',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=15
        )
        self.collapse_button.pack()

        self.details_container = tk.Frame(self.root, bg='#f0f0f0')
        self.details_visible = False

        info_frame = tk.LabelFrame(
            self.details_container,
            text="詳細系統資訊",
            bg='#f0f0f0',
            font=('Arial', 11, 'bold')
        )
        info_frame.pack(pady=10, padx=20, fill='x')

        self.info_labels = {}
        info_grid = tk.Frame(info_frame, bg='#f0f0f0')
        info_grid.pack(pady=10, padx=10, fill='x')

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

        self.status_label = tk.Label(
            self.details_container,
            text="💡 點擊「開始監控」開始即時系統監控",
            font=('Arial', 10),
            bg='#f0f0f0',
            fg='#666'
        )
        self.status_label.pack(pady=5)

        self.manual_refresh()
        self.start_monitoring()

    def start_monitoring(self):
        if not self.is_running:
            self.is_running = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.status_label.config(text="🟢 即時監控中...")
            self.update_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            self.update_thread.start()

    def stop_monitoring(self):
        self.is_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_label.config(text="⏸️ 監控已停止")

    def toggle_labels(self):
        current_state = self.monitor.get_label_visibility()
        new_state = not current_state
        self.monitor.set_label_visibility(new_state)
        if new_state:
            self.label_button.config(text="🏷️ 隱藏標籤")
        else:
            self.label_button.config(text="🏷️ 顯示標籤")

    def toggle_glass_effect(self):
        current_state = self.monitor.get_glass_effect()
        new_state = not current_state
        self.monitor.set_glass_effect(new_state)
        if new_state:
            self.glass_button.config(text="✨ 關閉玻璃")
        else:
            self.glass_button.config(text="✨ 開啟玻璃")

    def toggle_details(self):
        if self.details_visible:
            self.details_container.pack_forget()
            self.collapse_button.config(text="🔼 顯示詳細資訊")
            self.details_visible = False
            self.root.geometry("520x520")
        else:
            self.details_container.pack(fill='both', expand=True)
            self.collapse_button.config(text="🔽 隱藏詳細資訊")
            self.details_visible = True
            self.root.geometry("520x720")

    def manual_refresh(self):
        try:
            levels = self.monitor.update_system_metrics()
            self.update_gauge_display()
            self.update_detailed_info()
            if not self.is_running:
                self.status_label.config(text="✅ 手動更新完成")
        except Exception as e:
            self.status_label.config(text=f"❌ 更新失敗: {str(e)}")

    def monitoring_loop(self):
        while self.is_running:
            try:
                self.monitor.gauge.update_animation()
                if hasattr(self, 'loop_counter'):
                    self.loop_counter += 1
                else:
                    self.loop_counter = 0
                if self.loop_counter % 15 == 0:
                    self.monitor.update_system_metrics()
                if self.loop_counter % 5 == 0:
                    self.root.after(0, self.update_gauge_display)
                if self.loop_counter % 60 == 0:
                    self.root.after(0, self.update_detailed_info)
                time.sleep(0.008)
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(text=f"❌ 監控錯誤: {str(e)}"))
                break

    def update_gauge_display(self):
        try:
            gauge_image = self.monitor.draw_system_monitor_display()
            display_size = (450, 450)
            gauge_image = gauge_image.resize(display_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(gauge_image)
            self.gauge_label.configure(image=photo)
            self.gauge_label.image = photo
        except Exception as e:
            print(f"錶盤顯示更新失敗: {e}")
            import traceback
            traceback.print_exc()

    def update_detailed_info(self):
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
        self.root.mainloop()


def main():
    print("啟動系統監控 RD-1 風格錶盤 (analogGauge example)...")
    app = SystemMonitorUI()
    app.run()


if __name__ == "__main__":
    main()
