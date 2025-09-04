#!/usr/bin/env python3
"""
ModeDial UI 模擬器
提供視覺化的雙轉盤控制介面來測試狀態機
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import time
import os
import sys

# 添加 src 目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from state_machine import ModeDial


class ModeDialSimulator:
    """雙轉盤模擬器主視窗"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("ModeDial Simulator - 雙轉盤相機控制模擬器")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2b2b2b')
        
        # 初始化狀態機
        self.mode_dial = ModeDial()
        self.mode_dial.set_callbacks(
            on_mode_changed=self.on_mode_changed,
            on_value_changed=self.on_value_changed,
            on_binding_triggered=self.on_binding_triggered
        )
        
        # 建立 UI
        self.setup_ui()
        self.update_display()
        
        # 紀錄日誌
        self.log_messages = []
    
    def setup_ui(self):
        """建立使用者介面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # 標題
        title_label = ttk.Label(main_frame, text="ModeDial Simulator", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 頂部控制區域
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill="x", pady=(0, 10))
        
        # 左側：轉盤視覺化
        left_frame = ttk.LabelFrame(top_frame, text="雙轉盤控制", padding=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.setup_dial_controls(left_frame)
        
        # 右側：狀態顯示
        right_frame = ttk.LabelFrame(top_frame, text="當前狀態", padding=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        self.setup_status_display(right_frame)
        
        # 底部：詳細資訊和控制
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        # 詳細狀態
        detail_frame = ttk.LabelFrame(bottom_frame, text="詳細資訊", padding=10)
        detail_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.setup_detail_display(detail_frame)
        
        # 控制面板
        control_frame = ttk.LabelFrame(bottom_frame, text="控制面板", padding=10)
        control_frame.pack(side="right", fill="y", padx=(5, 0))
        
        self.setup_control_panel(control_frame)
    
    def setup_dial_controls(self, parent):
        """建立轉盤控制區域"""
        # 左轉盤控制
        left_dial_frame = ttk.Frame(parent)
        left_dial_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        ttk.Label(left_dial_frame, text="左轉盤 (模式選擇)", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # 左轉盤按鈕
        dial_btn_frame = ttk.Frame(left_dial_frame)
        dial_btn_frame.pack(pady=5)
        
        ttk.Button(dial_btn_frame, text="◀", width=3,
                  command=lambda: self.rotate_left_dial(-1)).pack(side="left", padx=2)
        ttk.Button(dial_btn_frame, text="▶", width=3,
                  command=lambda: self.rotate_left_dial(1)).pack(side="left", padx=2)
        
        # 右轉盤控制
        right_dial_frame = ttk.Frame(parent)
        right_dial_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        ttk.Label(right_dial_frame, text="右轉盤 (數值調整)", 
                 font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # 右轉盤按鈕
        right_btn_frame = ttk.Frame(right_dial_frame)
        right_btn_frame.pack(pady=5)
        
        ttk.Button(right_btn_frame, text="◀", width=3,
                  command=lambda: self.rotate_right_dial(-1)).pack(side="left", padx=2)
        ttk.Button(right_btn_frame, text="▶", width=3,
                  command=lambda: self.rotate_right_dial(1)).pack(side="left", padx=2)
        
        # 右轉盤按壓按鈕
        press_frame = ttk.Frame(right_dial_frame)
        press_frame.pack(pady=10)
        
        ttk.Button(press_frame, text="按壓", width=8,
                  command=lambda: self.press_right_dial("press")).pack(side="left", padx=2)
        ttk.Button(press_frame, text="長按", width=8,
                  command=lambda: self.press_right_dial("longPress")).pack(side="left", padx=2)
    
    def setup_status_display(self, parent):
        """建立狀態顯示區域"""
        # 當前模式
        mode_frame = ttk.Frame(parent)
        mode_frame.pack(fill="x", pady=5)
        
        ttk.Label(mode_frame, text="當前模式:", font=("Arial", 10, "bold")).pack(side="left")
        self.mode_label = ttk.Label(mode_frame, text="--", 
                                   font=("Arial", 10), foreground="blue")
        self.mode_label.pack(side="right")
        
        # 當前值
        value_frame = ttk.Frame(parent)
        value_frame.pack(fill="x", pady=5)
        
        ttk.Label(value_frame, text="當前值:", font=("Arial", 10, "bold")).pack(side="left")
        self.value_label = ttk.Label(value_frame, text="--", 
                                    font=("Arial", 10), foreground="green")
        self.value_label.pack(side="right")
        
        # 模式索引
        index_frame = ttk.Frame(parent)
        index_frame.pack(fill="x", pady=5)
        
        ttk.Label(index_frame, text="模式索引:", font=("Arial", 10, "bold")).pack(side="left")
        self.index_label = ttk.Label(index_frame, text="--", 
                                    font=("Arial", 10))
        self.index_label.pack(side="right")
        
        # 提示資訊
        ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=10)
        
        ttk.Label(parent, text="提示:", font=("Arial", 10, "bold")).pack(anchor="w")
        self.hint_text = tk.Text(parent, height=4, width=30, 
                                font=("Arial", 9), state="disabled")
        self.hint_text.pack(fill="both", expand=True, pady=(5, 0))
    
    def setup_detail_display(self, parent):
        """建立詳細資訊顯示"""
        # 建立 Treeview
        self.detail_tree = ttk.Treeview(parent, show="tree headings", height=12)
        self.detail_tree["columns"] = ("value",)
        self.detail_tree.heading("#0", text="項目")
        self.detail_tree.heading("value", text="值")
        self.detail_tree.column("#0", width=200)
        self.detail_tree.column("value", width=200)
        
        # 滾動條
        scrollbar = ttk.Scrollbar(parent, orient="vertical", 
                                 command=self.detail_tree.yview)
        self.detail_tree.configure(yscrollcommand=scrollbar.set)
        
        self.detail_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_control_panel(self, parent):
        """建立控制面板"""
        # 重置按鈕
        ttk.Button(parent, text="重置", width=12,
                  command=self.reset_state).pack(pady=5)
        
        # 匯出狀態
        ttk.Button(parent, text="匯出狀態", width=12,
                  command=self.export_state).pack(pady=5)
        
        # 快捷鍵說明
        ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=10)
        
        shortcuts_text = """快捷鍵:
A/D - 左轉盤
←/→ - 右轉盤  
Space - 按壓
L - 長按
R - 重置"""
        
        ttk.Label(parent, text=shortcuts_text, font=("Arial", 9),
                 justify="left").pack(anchor="w")
        
        # 綁定快捷鍵
        self.root.bind("<Key>", self.on_keypress)
        self.root.focus_set()
    
    def on_keypress(self, event):
        """處理快捷鍵"""
        key = event.char.lower()
        
        if key == 'a':
            self.rotate_left_dial(-1)
        elif key == 'd':
            self.rotate_left_dial(1)
        elif event.keysym == 'Left':
            self.rotate_right_dial(-1)
        elif event.keysym == 'Right':
            self.rotate_right_dial(1)
        elif key == ' ':
            self.press_right_dial("press")
        elif key == 'l':
            self.press_right_dial("longPress")
        elif key == 'r':
            self.reset_state()
    
    def rotate_left_dial(self, direction):
        """旋轉左轉盤"""
        self.mode_dial.rotate_left_dial(direction)
        self.add_log(f"左轉盤旋轉 {'順時針' if direction > 0 else '逆時針'}")
    
    def rotate_right_dial(self, direction):
        """旋轉右轉盤"""
        self.mode_dial.rotate_right_dial(direction)
        self.add_log(f"右轉盤旋轉 {'順時針' if direction > 0 else '逆時針'}")
    
    def press_right_dial(self, press_type):
        """按壓右轉盤"""
        self.mode_dial.press_right_dial(press_type)
        self.add_log(f"右轉盤{'長按' if press_type == 'longPress' else '按壓'}")
    
    def reset_state(self):
        """重置狀態"""
        self.mode_dial.reset_to_defaults()
        self.add_log("系統重置")
    
    def export_state(self):
        """匯出當前狀態"""
        state = self.mode_dial.get_current_state()
        timestamp = int(time.time())
        filename = f"mode_dial_state_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2, default=str)
            messagebox.showinfo("匯出成功", f"狀態已匯出至 {filename}")
            self.add_log(f"狀態匯出至 {filename}")
        except Exception as e:
            messagebox.showerror("匯出失敗", f"匯出失敗: {str(e)}")
    
    def on_mode_changed(self, mode_index, mode):
        """模式變更回調"""
        self.update_display()
        mode_label = mode.get("label", "未知") if mode else "無"
        self.add_log(f"模式切換至: {mode_label}")
    
    def on_value_changed(self, mode_id, old_value, new_value):
        """值變更回調"""
        self.update_display()
        self.add_log(f"值變更 [{mode_id}]: {old_value} → {new_value}")
    
    def on_binding_triggered(self, mode_id, bindings, value):
        """綁定觸發回調"""
        self.add_log(f"觸發綁定 [{mode_id}]: {bindings}")
    
    def add_log(self, message):
        """添加日誌"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_messages.append(log_entry)
        
        # 保持最多 100 條日誌
        if len(self.log_messages) > 100:
            self.log_messages.pop(0)
        
        print(log_entry)  # 也輸出到控制台
    
    def update_display(self):
        """更新顯示"""
        state = self.mode_dial.get_current_state()
        current_mode = state.get("current_mode", {})
        
        # 更新狀態標籤
        self.mode_label.config(text=current_mode.get("label", "--"))
        self.value_label.config(text=state.get("current_display_value", "--"))
        self.index_label.config(text=f"{state.get('current_mode_index', 0)}/{state.get('total_modes', 0)-1}")
        
        # 更新提示
        hint = current_mode.get("hint", "")
        self.hint_text.config(state="normal")
        self.hint_text.delete(1.0, tk.END)
        self.hint_text.insert(1.0, hint)
        self.hint_text.config(state="disabled")
        
        # 更新詳細資訊樹
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)
        
        # 添加基本資訊
        basic_info = self.detail_tree.insert("", "end", text="基本資訊")
        self.detail_tree.insert(basic_info, "end", text="版本", values=(state.get("version", ""),))
        self.detail_tree.insert(basic_info, "end", text="當前模式ID", values=(state.get("current_mode_id", ""),))
        self.detail_tree.insert(basic_info, "end", text="模式索引", values=(f"{state.get('current_mode_index')}/{state.get('total_modes', 0)-1}",))
        
        # 添加當前值
        values_info = self.detail_tree.insert("", "end", text="所有模式當前值")
        current_values = state.get("current_values", {})
        for mode_id, value in current_values.items():
            self.detail_tree.insert(values_info, "end", text=mode_id, values=(str(value),))
        
        # 添加模式詳情
        if current_mode:
            mode_info = self.detail_tree.insert("", "end", text="當前模式詳情")
            self.detail_tree.insert(mode_info, "end", text="ID", values=(current_mode.get("id", ""),))
            self.detail_tree.insert(mode_info, "end", text="標籤", values=(current_mode.get("label", ""),))
            self.detail_tree.insert(mode_info, "end", text="類型", values=(current_mode.get("type", ""),))
            
            # 事件處理
            events = current_mode.get("events", {})
            if events:
                events_info = self.detail_tree.insert(mode_info, "end", text="事件")
                for event_type, action in events.items():
                    self.detail_tree.insert(events_info, "end", text=event_type, values=(action,))
    
    def run(self):
        """運行模擬器"""
        self.root.mainloop()


def main():
    """主函數"""
    print("啟動 ModeDial 模擬器...")
    print("快捷鍵: A/D=左轉盤, ←/→=右轉盤, Space=按壓, L=長按, R=重置")
    
    try:
        simulator = ModeDialSimulator()
        simulator.run()
    except KeyboardInterrupt:
        print("\n模擬器被用戶中斷")
    except Exception as e:
        print(f"模擬器錯誤: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())