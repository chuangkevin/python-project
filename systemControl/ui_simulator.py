#!/usr/bin/env python3
"""
SystemControl UI 模擬器
提供視覺化的系統設定管理介面來測試 SystemControl
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import time
import os
import sys

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(__file__))

from core.system_manager import SystemManager

class SystemControlSimulator:
    """SystemControl 模擬器主視窗"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SystemControl Simulator - 系統控制模擬器")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # 初始化系統管理器
        self.system_manager = SystemManager()
        if not self.system_manager.initialize_system():
            messagebox.showerror("錯誤", "系統初始化失敗")
            return
        
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
        title_label = ttk.Label(main_frame, text="SystemControl Simulator", 
                               font=("Arial", 18, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 頂部控制區域
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill="x", pady=(0, 10))
        
        # 左側：系統狀態
        left_frame = ttk.LabelFrame(top_frame, text="系統狀態", padding=10)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.setup_system_status(left_frame)
        
        # 右側：模式控制
        right_frame = ttk.LabelFrame(top_frame, text="模式控制", padding=10)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        self.setup_mode_controls(right_frame)
        
        # 中部：設定控制
        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        # 相機設定
        camera_frame = ttk.LabelFrame(middle_frame, text="相機設定", padding=10)
        camera_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.setup_camera_controls(camera_frame)
        
        # 轉盤設定
        dial_frame = ttk.LabelFrame(middle_frame, text="轉盤設定", padding=10)
        dial_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        self.setup_dial_controls(dial_frame)
        
        # 底部：詳細資訊和日誌
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        # 詳細資訊
        detail_frame = ttk.LabelFrame(bottom_frame, text="詳細資訊", padding=10)
        detail_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        self.setup_detail_display(detail_frame)
        
        # 控制面板和日誌
        control_frame = ttk.LabelFrame(bottom_frame, text="控制面板", padding=10)
        control_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        self.setup_control_panel(control_frame)
    
    def setup_system_status(self, parent):
        """建立系統狀態顯示"""
        # 系統初始化狀態
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill="x", pady=5)
        
        ttk.Label(status_frame, text="初始化狀態:", font=("Arial", 10, "bold")).pack(side="left")
        self.init_status_label = ttk.Label(status_frame, text="--", 
                                          font=("Arial", 10), foreground="green")
        self.init_status_label.pack(side="right")
        
        # 當前模式
        mode_frame = ttk.Frame(parent)
        mode_frame.pack(fill="x", pady=5)
        
        ttk.Label(mode_frame, text="當前模式:", font=("Arial", 10, "bold")).pack(side="left")
        self.current_mode_label = ttk.Label(mode_frame, text="--", 
                                           font=("Arial", 10), foreground="blue")
        self.current_mode_label.pack(side="right")
        
        # 轉盤配置
        profile_frame = ttk.Frame(parent)
        profile_frame.pack(fill="x", pady=5)
        
        ttk.Label(profile_frame, text="轉盤配置:", font=("Arial", 10, "bold")).pack(side="left")
        self.profile_label = ttk.Label(profile_frame, text="--", 
                                      font=("Arial", 10))
        self.profile_label.pack(side="right")
        
        # 如果有 ModeDial，顯示轉盤狀態
        if self.system_manager.mode_dial:
            ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=10)
            ttk.Label(parent, text="轉盤狀態:", font=("Arial", 10, "bold")).pack(anchor="w")
            
            dial_info_frame = ttk.Frame(parent)
            dial_info_frame.pack(fill="x", pady=5)
            
            ttk.Label(dial_info_frame, text="轉盤模式:", font=("Arial", 9)).pack(side="left")
            self.dial_mode_label = ttk.Label(dial_info_frame, text="--", 
                                            font=("Arial", 9), foreground="purple")
            self.dial_mode_label.pack(side="right")
            
            dial_value_frame = ttk.Frame(parent)
            dial_value_frame.pack(fill="x", pady=5)
            
            ttk.Label(dial_value_frame, text="當前值:", font=("Arial", 9)).pack(side="left")
            self.dial_value_label = ttk.Label(dial_value_frame, text="--", 
                                             font=("Arial", 9), foreground="purple")
            self.dial_value_label.pack(side="right")
    
    def setup_mode_controls(self, parent):
        """建立模式控制"""
        ttk.Label(parent, text="系統模式切換", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # 模式按鈕
        modes = [("拍照模式", "photo"), ("錄影模式", "video"), ("手動模式", "manual")]
        
        for mode_name, mode_id in modes:
            btn = ttk.Button(parent, text=mode_name, width=15,
                           command=lambda m=mode_id: self.switch_mode(m))
            btn.pack(pady=2, fill="x")
        
        ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=10)
        
        # 系統控制
        ttk.Button(parent, text="重新初始化", width=15,
                  command=self.reinitialize_system).pack(pady=2, fill="x")
        
        ttk.Button(parent, text="保存所有設定", width=15,
                  command=self.save_all_settings).pack(pady=2, fill="x")
    
    def setup_camera_controls(self, parent):
        """建立相機設定控制"""
        ttk.Label(parent, text="相機參數調整", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # 影像品質
        quality_frame = ttk.Frame(parent)
        quality_frame.pack(fill="x", pady=5)
        
        ttk.Label(quality_frame, text="影像品質:").pack(side="left")
        self.quality_var = tk.StringVar(value=self.system_manager.camera_settings.image_quality)
        quality_combo = ttk.Combobox(quality_frame, textvariable=self.quality_var,
                                    values=["high", "medium", "low"], state="readonly", width=15)
        quality_combo.pack(side="right")
        quality_combo.bind("<<ComboboxSelected>>", self.on_quality_changed)
        
        # 拍攝格式
        format_frame = ttk.Frame(parent)
        format_frame.pack(fill="x", pady=5)
        
        ttk.Label(format_frame, text="拍攝格式:").pack(side="left")
        self.format_var = tk.StringVar(value=self.system_manager.camera_settings.capture_format)
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var,
                                   values=["jpeg", "raw", "both"], state="readonly", width=15)
        format_combo.pack(side="right")
        format_combo.bind("<<ComboboxSelected>>", self.on_format_changed)
        
        # 錄影解析度
        video_frame = ttk.Frame(parent)
        video_frame.pack(fill="x", pady=5)
        
        ttk.Label(video_frame, text="錄影解析度:").pack(side="left")
        self.video_var = tk.StringVar(value=self.system_manager.camera_settings.video_resolution)
        video_combo = ttk.Combobox(video_frame, textvariable=self.video_var,
                                  values=["4k", "1080p", "720p", "480p"], state="readonly", width=15)
        video_combo.pack(side="right")
        video_combo.bind("<<ComboboxSelected>>", self.on_video_changed)
        
        # 對焦模式
        af_frame = ttk.Frame(parent)
        af_frame.pack(fill="x", pady=5)
        
        ttk.Label(af_frame, text="對焦模式:").pack(side="left")
        self.af_var = tk.StringVar(value=self.system_manager.camera_settings.autofocus_mode)
        af_combo = ttk.Combobox(af_frame, textvariable=self.af_var,
                               values=["single", "continuous", "manual"], state="readonly", width=15)
        af_combo.pack(side="right")
        af_combo.bind("<<ComboboxSelected>>", self.on_af_changed)
        
        # HDR 開關
        hdr_frame = ttk.Frame(parent)
        hdr_frame.pack(fill="x", pady=5)
        
        ttk.Label(hdr_frame, text="HDR:").pack(side="left")
        self.hdr_var = tk.BooleanVar(value=self.system_manager.camera_settings.hdr_enabled)
        hdr_check = ttk.Checkbutton(hdr_frame, variable=self.hdr_var,
                                   command=self.on_hdr_changed)
        hdr_check.pack(side="right")
    
    def setup_dial_controls(self, parent):
        """建立轉盤設定控制"""
        ttk.Label(parent, text="轉盤配置管理", font=("Arial", 12, "bold")).pack(pady=(0, 10))
        
        # 當前配置選擇
        profile_frame = ttk.Frame(parent)
        profile_frame.pack(fill="x", pady=5)
        
        ttk.Label(profile_frame, text="當前配置:").pack(side="left")
        self.current_profile_var = tk.StringVar(value=self.system_manager.dial_settings.current_profile)
        profiles = self.system_manager.dial_settings.get_available_profiles()
        profile_combo = ttk.Combobox(profile_frame, textvariable=self.current_profile_var,
                                    values=profiles, state="readonly", width=15)
        profile_combo.pack(side="right")
        profile_combo.bind("<<ComboboxSelected>>", self.on_profile_changed)
        
        # 左轉盤靈敏度
        left_sens_frame = ttk.Frame(parent)
        left_sens_frame.pack(fill="x", pady=5)
        
        ttk.Label(left_sens_frame, text="左轉盤靈敏度:").pack(side="left")
        self.left_sens_var = tk.DoubleVar(value=self.system_manager.dial_settings.left_dial_sensitivity)
        left_sens_scale = ttk.Scale(left_sens_frame, from_=0.1, to=2.0, orient="horizontal",
                                   variable=self.left_sens_var, command=self.on_sensitivity_changed)
        left_sens_scale.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # 右轉盤靈敏度
        right_sens_frame = ttk.Frame(parent)
        right_sens_frame.pack(fill="x", pady=5)
        
        ttk.Label(right_sens_frame, text="右轉盤靈敏度:").pack(side="left")
        self.right_sens_var = tk.DoubleVar(value=self.system_manager.dial_settings.right_dial_sensitivity)
        right_sens_scale = ttk.Scale(right_sens_frame, from_=0.1, to=2.0, orient="horizontal",
                                    variable=self.right_sens_var, command=self.on_sensitivity_changed)
        right_sens_scale.pack(side="right", fill="x", expand=True, padx=(5, 0))
        
        # 配置管理按鈕
        ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=10)
        
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill="x")
        
        ttk.Button(btn_frame, text="保存配置", width=12,
                  command=self.save_current_profile).pack(side="left", padx=2)
        
        ttk.Button(btn_frame, text="重載配置", width=12,
                  command=self.reload_current_profile).pack(side="right", padx=2)
        
        # 如果有 ModeDial，添加轉盤模擬控制
        if self.system_manager.mode_dial:
            ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=10)
            
            ttk.Label(parent, text="轉盤模擬", font=("Arial", 10, "bold")).pack()
            
            dial_sim_frame = ttk.Frame(parent)
            dial_sim_frame.pack(fill="x", pady=5)
            
            ttk.Button(dial_sim_frame, text="左轉盤 ◀", width=8,
                      command=lambda: self.simulate_dial("left", -1)).pack(side="left", padx=1)
            ttk.Button(dial_sim_frame, text="左轉盤 ▶", width=8,
                      command=lambda: self.simulate_dial("left", 1)).pack(side="left", padx=1)
            
            ttk.Button(dial_sim_frame, text="右轉盤 ◀", width=8,
                      command=lambda: self.simulate_dial("right", -1)).pack(side="right", padx=1)
            ttk.Button(dial_sim_frame, text="右轉盤 ▶", width=8,
                      command=lambda: self.simulate_dial("right", 1)).pack(side="right", padx=1)
    
    def setup_detail_display(self, parent):
        """建立詳細資訊顯示"""
        # 建立 Treeview
        self.detail_tree = ttk.Treeview(parent, show="tree headings", height=15)
        self.detail_tree["columns"] = ("value",)
        self.detail_tree.heading("#0", text="設定項目")
        self.detail_tree.heading("value", text="值")
        self.detail_tree.column("#0", width=200)
        self.detail_tree.column("value", width=300)
        
        # 滾動條
        scrollbar = ttk.Scrollbar(parent, orient="vertical", 
                                 command=self.detail_tree.yview)
        self.detail_tree.configure(yscrollcommand=scrollbar.set)
        
        self.detail_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def setup_control_panel(self, parent):
        """建立控制面板"""
        # 系統控制按鈕
        ttk.Button(parent, text="匯出系統狀態", width=15,
                  command=self.export_system_state).pack(pady=5)
        
        ttk.Button(parent, text="重置為預設", width=15,
                  command=self.reset_to_defaults).pack(pady=5)
        
        # 日誌顯示
        ttk.Separator(parent, orient="horizontal").pack(fill="x", pady=10)
        
        ttk.Label(parent, text="操作日誌:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        # 日誌文本框
        log_frame = ttk.Frame(parent)
        log_frame.pack(fill="both", expand=True, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, width=40, 
                               font=("Arial", 9), state="disabled")
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical",
                                     command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side="left", fill="both", expand=True)
        log_scrollbar.pack(side="right", fill="y")
    
    # 事件處理方法
    def switch_mode(self, mode):
        """切換系統模式"""
        success = self.system_manager.switch_mode(mode)
        self.add_log(f"切換至 {mode} 模式: {'成功' if success else '失敗'}")
        self.update_display()
    
    def on_quality_changed(self, event):
        """影像品質變更"""
        quality = self.quality_var.get()
        success = self.system_manager.camera_settings.set_image_quality(quality)
        self.add_log(f"影像品質設定為 {quality}: {'成功' if success else '失敗'}")
        self.update_display()
    
    def on_format_changed(self, event):
        """拍攝格式變更"""
        format_type = self.format_var.get()
        success = self.system_manager.camera_settings.set_capture_format(format_type)
        self.add_log(f"拍攝格式設定為 {format_type}: {'成功' if success else '失敗'}")
    
    def on_video_changed(self, event):
        """錄影解析度變更"""
        resolution = self.video_var.get()
        success = self.system_manager.camera_settings.set_video_resolution(resolution)
        self.add_log(f"錄影解析度設定為 {resolution}: {'成功' if success else '失敗'}")
    
    def on_af_changed(self, event):
        """對焦模式變更"""
        af_mode = self.af_var.get()
        success = self.system_manager.camera_settings.set_autofocus_mode(af_mode)
        self.add_log(f"對焦模式設定為 {af_mode}: {'成功' if success else '失敗'}")
    
    def on_hdr_changed(self):
        """HDR 設定變更"""
        hdr_enabled = self.hdr_var.get()
        self.system_manager.camera_settings.enable_hdr(hdr_enabled)
        self.add_log(f"HDR {'啟用' if hdr_enabled else '關閉'}")
    
    def on_profile_changed(self, event):
        """轉盤配置變更"""
        profile_name = self.current_profile_var.get()
        success = self.system_manager.dial_settings.load_profile(profile_name)
        self.add_log(f"載入轉盤配置 {profile_name}: {'成功' if success else '失敗'}")
        self.update_display()
    
    def on_sensitivity_changed(self, value):
        """轉盤靈敏度變更"""
        left_sens = self.left_sens_var.get()
        right_sens = self.right_sens_var.get()
        self.system_manager.dial_settings.set_dial_sensitivity(left_sens, right_sens)
        self.add_log(f"轉盤靈敏度: 左={left_sens:.1f}, 右={right_sens:.1f}")
    
    def simulate_dial(self, dial, direction):
        """模擬轉盤操作"""
        if not self.system_manager.mode_dial:
            return
        
        old_state = self.system_manager.mode_dial.get_current_state()
        old_value = old_state.get('current_display_value', '')
        
        if dial == "left":
            self.system_manager.mode_dial.rotate_left_dial(direction)
        else:
            self.system_manager.mode_dial.rotate_right_dial(direction)
        
        new_state = self.system_manager.mode_dial.get_current_state()
        new_value = new_state.get('current_display_value', '')
        
        self.add_log(f"{dial}轉盤旋轉: {old_value} → {new_value}")
        self.update_display()
    
    def save_current_profile(self):
        """保存當前轉盤配置"""
        profile_name = self.system_manager.dial_settings.current_profile
        success = self.system_manager.dial_settings.save_profile(profile_name)
        self.add_log(f"保存轉盤配置 {profile_name}: {'成功' if success else '失敗'}")
    
    def reload_current_profile(self):
        """重新載入當前配置"""
        profile_name = self.system_manager.dial_settings.current_profile
        success = self.system_manager.dial_settings.load_profile(profile_name)
        self.add_log(f"重載轉盤配置 {profile_name}: {'成功' if success else '失敗'}")
        self.update_display()
    
    def reinitialize_system(self):
        """重新初始化系統"""
        success = self.system_manager.initialize_system()
        self.add_log(f"系統重新初始化: {'成功' if success else '失敗'}")
        self.update_display()
    
    def save_all_settings(self):
        """保存所有設定"""
        self.system_manager._save_all_settings()
        self.add_log("所有設定已保存")
    
    def export_system_state(self):
        """匯出系統狀態"""
        try:
            timestamp = int(time.time())
            filename = f"system_state_{timestamp}.json"
            
            # 收集所有狀態
            state = {
                "timestamp": timestamp,
                "system_status": self.system_manager.get_system_status(),
                "camera_settings": self.system_manager.camera_settings.get_all_settings(),
                "dial_settings": self.system_manager.dial_settings.get_current_profile_info()
            }
            
            # 如果有轉盤狀態，也加入
            if self.system_manager.mode_dial:
                state["dial_state"] = self.system_manager.mode_dial.get_current_state()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2, default=str)
            
            messagebox.showinfo("匯出成功", f"系統狀態已匯出至 {filename}")
            self.add_log(f"系統狀態匯出至 {filename}")
            
        except Exception as e:
            messagebox.showerror("匯出失敗", f"匯出失敗: {str(e)}")
            self.add_log(f"匯出失敗: {e}")
    
    def reset_to_defaults(self):
        """重置為預設設定"""
        result = messagebox.askyesno("確認重置", "確定要重置所有設定為預設值嗎？")
        if result:
            self.system_manager.camera_settings.reset_to_defaults()
            # 重新載入預設轉盤配置
            self.system_manager.dial_settings.load_profile("default")
            self.add_log("所有設定已重置為預設值")
            self.update_display()
    
    def add_log(self, message):
        """添加日誌"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_messages.append(log_entry)
        
        # 保持最多 100 條日誌
        if len(self.log_messages) > 100:
            self.log_messages.pop(0)
        
        # 更新日誌顯示
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(1.0, "\n".join(self.log_messages))
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        
        print(log_entry)  # 也輸出到控制台
    
    def update_display(self):
        """更新顯示"""
        try:
            # 更新系統狀態
            status = self.system_manager.get_system_status()
            self.init_status_label.config(text="已初始化" if status["initialized"] else "未初始化")
            self.current_mode_label.config(text=status["current_mode"])
            self.profile_label.config(text=self.system_manager.dial_settings.current_profile)
            
            # 更新轉盤狀態 (如果可用)
            if self.system_manager.mode_dial:
                dial_state = self.system_manager.mode_dial.get_current_state()
                current_mode = dial_state.get('current_mode', {})
                self.dial_mode_label.config(text=current_mode.get('label', 'N/A'))
                self.dial_value_label.config(text=dial_state.get('current_display_value', 'N/A'))
            
            # 更新相機設定控件
            self.quality_var.set(self.system_manager.camera_settings.image_quality)
            self.format_var.set(self.system_manager.camera_settings.capture_format)
            self.video_var.set(self.system_manager.camera_settings.video_resolution)
            self.af_var.set(self.system_manager.camera_settings.autofocus_mode)
            self.hdr_var.set(self.system_manager.camera_settings.hdr_enabled)
            
            # 更新轉盤設定控件
            profile_info = self.system_manager.dial_settings.get_current_profile_info()
            self.current_profile_var.set(profile_info['name'])
            self.left_sens_var.set(profile_info['left_sensitivity'])
            self.right_sens_var.set(profile_info['right_sensitivity'])
            
            # 更新詳細資訊樹
            self.update_detail_tree()
            
        except Exception as e:
            self.add_log(f"更新顯示失敗: {e}")
    
    def update_detail_tree(self):
        """更新詳細資訊樹"""
        # 清空現有項目
        for item in self.detail_tree.get_children():
            self.detail_tree.delete(item)
        
        try:
            # 系統狀態
            system_info = self.detail_tree.insert("", "end", text="系統狀態")
            status = self.system_manager.get_system_status()
            for key, value in status.items():
                self.detail_tree.insert(system_info, "end", text=key, values=(str(value),))
            
            # 相機設定
            camera_info = self.detail_tree.insert("", "end", text="相機設定")
            camera_settings = self.system_manager.camera_settings.get_all_settings()
            for category, settings in camera_settings.items():
                category_node = self.detail_tree.insert(camera_info, "end", text=category)
                if isinstance(settings, dict):
                    for key, value in settings.items():
                        self.detail_tree.insert(category_node, "end", text=key, values=(str(value),))
                else:
                    self.detail_tree.insert(category_node, "end", text="value", values=(str(settings),))
            
            # 轉盤設定
            dial_info = self.detail_tree.insert("", "end", text="轉盤設定")
            dial_settings = self.system_manager.dial_settings.get_current_profile_info()
            for key, value in dial_settings.items():
                if key != "profile_data":  # 跳過複雜的配置資料
                    self.detail_tree.insert(dial_info, "end", text=key, values=(str(value),))
            
            # 如果有轉盤狀態，也加入
            if self.system_manager.mode_dial:
                dial_state_info = self.detail_tree.insert("", "end", text="轉盤狀態")
                dial_state = self.system_manager.mode_dial.get_current_state()
                for key, value in dial_state.items():
                    if key not in ["current_values", "sub_mode_stack", "dial_order"]:  # 跳過複雜資料
                        self.detail_tree.insert(dial_state_info, "end", text=key, values=(str(value),))
            
        except Exception as e:
            self.add_log(f"更新詳細資訊失敗: {e}")
    
    def run(self):
        """運行模擬器"""
        self.root.mainloop()

def main():
    """主函數"""
    print("啟動 SystemControl UI 模擬器...")
    
    try:
        simulator = SystemControlSimulator()
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