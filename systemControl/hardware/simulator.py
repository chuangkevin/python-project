#!/usr/bin/env python3
"""
RD-1 Camera Control - 硬體模擬器
開發模式下模擬硬體事件，方便測試和開發
"""

import logging
import threading
import time
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Dict, Any

logger = logging.getLogger(__name__)

class HardwareSimulator:
    """硬體事件模擬器"""
    
    def __init__(self):
        self.event_callback = None
        self.simulation_window = None
        self._running = False
        
        logger.info("硬體模擬器初始化")
    
    def set_event_callback(self, callback: Callable):
        """設定事件回調函數"""
        self.event_callback = callback
        logger.info("設定硬體事件回調函數")
    
    def show_simulator_window(self):
        """顯示硬體模擬器視窗"""
        if self.simulation_window is None:
            self._create_simulator_window()
    
    def _create_simulator_window(self):
        """創建模擬器視窗"""
        self.simulation_window = tk.Toplevel()
        self.simulation_window.title("RD-1 硬體模擬器")
        self.simulation_window.geometry("400x600")
        self.simulation_window.resizable(False, False)
        
        # 設定關閉事件
        self.simulation_window.protocol("WM_DELETE_WINDOW", self._on_simulator_close)
        
        # 創建UI元件
        self._create_simulator_ui()
        
        logger.info("硬體模擬器視窗已創建")
    
    def _create_simulator_ui(self):
        """創建模擬器UI"""
        # 標題
        title_frame = ttk.Frame(self.simulation_window)
        title_frame.pack(pady=10, padx=10, fill='x')
        
        ttk.Label(title_frame, text="RD-1 硬體模擬器", 
                 font=('Arial', 14, 'bold')).pack()
        ttk.Label(title_frame, text="模擬相機硬體控制", 
                 font=('Arial', 10)).pack()
        
        # 分隔線
        ttk.Separator(self.simulation_window, orient='horizontal').pack(fill='x', pady=5)
        
        # 雙轉盤控制
        self._create_dial_controls()
        
        # 按鈕控制
        self._create_button_controls()
        
        # 狀態顯示
        self._create_status_display()
    
    def _create_dial_controls(self):
        """創建雙轉盤控制"""
        dial_frame = ttk.LabelFrame(self.simulation_window, text="雙轉盤控制")
        dial_frame.pack(pady=10, padx=10, fill='x')
        
        # 左轉盤 (模式選擇)
        left_dial_frame = ttk.Frame(dial_frame)
        left_dial_frame.pack(side='left', padx=20, pady=10)
        
        ttk.Label(left_dial_frame, text="左轉盤 (模式)", 
                 font=('Arial', 10, 'bold')).pack()
        
        left_buttons = ttk.Frame(left_dial_frame)
        left_buttons.pack(pady=5)
        
        ttk.Button(left_buttons, text="◀", width=3,
                  command=lambda: self._send_dial_event('left', 'ccw')).pack(side='left')
        ttk.Button(left_buttons, text="▶", width=3,
                  command=lambda: self._send_dial_event('left', 'cw')).pack(side='left')
        
        # 右轉盤 (數值調整)
        right_dial_frame = ttk.Frame(dial_frame)
        right_dial_frame.pack(side='right', padx=20, pady=10)
        
        ttk.Label(right_dial_frame, text="右轉盤 (數值)", 
                 font=('Arial', 10, 'bold')).pack()
        
        right_buttons = ttk.Frame(right_dial_frame)
        right_buttons.pack(pady=5)
        
        ttk.Button(right_buttons, text="◀", width=3,
                  command=lambda: self._send_dial_event('right', 'ccw')).pack(side='left')
        ttk.Button(right_buttons, text="▶", width=3,
                  command=lambda: self._send_dial_event('right', 'cw')).pack(side='left')
        
        # 右轉盤按壓
        ttk.Button(right_dial_frame, text="按壓", width=8,
                  command=lambda: self._send_button_event('right_dial', 'press')).pack(pady=5)
    
    def _create_button_controls(self):
        """創建按鈕控制"""
        button_frame = ttk.LabelFrame(self.simulation_window, text="按鈕控制")
        button_frame.pack(pady=10, padx=10, fill='x')
        
        # 快門鍵
        shutter_frame = ttk.Frame(button_frame)
        shutter_frame.pack(pady=10)
        
        ttk.Label(shutter_frame, text="快門控制", 
                 font=('Arial', 10, 'bold')).pack()
        
        shutter_buttons = ttk.Frame(shutter_frame)
        shutter_buttons.pack(pady=5)
        
        ttk.Button(shutter_buttons, text="半按", width=8,
                  command=lambda: self._send_button_event('shutter', 'half_press')).pack(side='left', padx=2)
        ttk.Button(shutter_buttons, text="全按", width=8,
                  command=lambda: self._send_button_event('shutter', 'full_press')).pack(side='left', padx=2)
        
        # 五向搖桿
        joystick_frame = ttk.Frame(button_frame)
        joystick_frame.pack(pady=10)
        
        ttk.Label(joystick_frame, text="五向搖桿", 
                 font=('Arial', 10, 'bold')).pack()
        
        # 搖桿按鈕佈局
        joystick_grid = ttk.Frame(joystick_frame)
        joystick_grid.pack(pady=5)
        
        ttk.Button(joystick_grid, text="↑", width=3,
                  command=lambda: self._send_button_event('joystick_up', 'press')).grid(row=0, column=1)
        ttk.Button(joystick_grid, text="←", width=3,
                  command=lambda: self._send_button_event('joystick_left', 'press')).grid(row=1, column=0)
        ttk.Button(joystick_grid, text="OK", width=3,
                  command=lambda: self._send_button_event('joystick_center', 'press')).grid(row=1, column=1)
        ttk.Button(joystick_grid, text="→", width=3,
                  command=lambda: self._send_button_event('joystick_right', 'press')).grid(row=1, column=2)
        ttk.Button(joystick_grid, text="↓", width=3,
                  command=lambda: self._send_button_event('joystick_down', 'press')).grid(row=2, column=1)
        
        # 其他按鈕
        other_buttons = ttk.Frame(button_frame)
        other_buttons.pack(pady=10)
        
        ttk.Button(other_buttons, text="電源鍵", width=10,
                  command=lambda: self._send_button_event('power', 'press')).pack(side='left', padx=5)
        ttk.Button(other_buttons, text="過片桿", width=10,
                  command=lambda: self._send_button_event('film_advance', 'press')).pack(side='left', padx=5)
    
    def _create_status_display(self):
        """創建狀態顯示"""
        status_frame = ttk.LabelFrame(self.simulation_window, text="模擬器狀態")
        status_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        # 事件日誌
        self.event_log = tk.Text(status_frame, height=8, width=45, 
                                font=('Courier', 9))
        self.event_log.pack(pady=5, padx=5, fill='both', expand=True)
        
        # 滾動條
        scrollbar = ttk.Scrollbar(status_frame, orient='vertical', 
                                 command=self.event_log.yview)
        scrollbar.pack(side='right', fill='y')
        self.event_log.config(yscrollcommand=scrollbar.set)
        
        # 控制按鈕
        control_frame = ttk.Frame(status_frame)
        control_frame.pack(pady=5)
        
        ttk.Button(control_frame, text="清除日誌", width=10,
                  command=self._clear_log).pack(side='left', padx=5)
        ttk.Button(control_frame, text="自動測試", width=10,
                  command=self._start_auto_test).pack(side='left', padx=5)
    
    def _send_dial_event(self, dial: str, direction: str):
        """發送轉盤事件"""
        event = {
            'type': 'dial_rotation',
            'dial': dial,
            'direction': direction,
            'timestamp': time.time()
        }
        
        self._send_event(event)
        self._log_event(f"轉盤事件: {dial} {direction}")
    
    def _send_button_event(self, button: str, action: str):
        """發送按鈕事件"""
        event = {
            'type': 'button_press',
            'button': button,
            'action': action,
            'timestamp': time.time()
        }
        
        self._send_event(event)
        self._log_event(f"按鈕事件: {button} {action}")
    
    def _send_event(self, event: Dict[str, Any]):
        """發送事件到主應用程式"""
        if self.event_callback:
            try:
                self.event_callback(event)
                logger.debug(f"發送硬體事件: {event}")
            except Exception as e:
                logger.error(f"事件回調失敗: {e}")
                self._log_event(f"錯誤: 事件回調失敗 - {e}")
    
    def _log_event(self, message: str):
        """記錄事件到日誌"""
        if hasattr(self, 'event_log'):
            timestamp = time.strftime("%H:%M:%S")
            log_message = f"[{timestamp}] {message}\n"
            
            self.event_log.insert(tk.END, log_message)
            self.event_log.see(tk.END)
            
            # 限制日誌長度
            if self.event_log.index(tk.END).split('.')[0] != '1':
                line_count = int(self.event_log.index(tk.END).split('.')[0]) - 1
                if line_count > 100:
                    self.event_log.delete('1.0', '2.0')
    
    def _clear_log(self):
        """清除事件日誌"""
        if hasattr(self, 'event_log'):
            self.event_log.delete('1.0', tk.END)
            self._log_event("日誌已清除")
    
    def _start_auto_test(self):
        """開始自動測試序列"""
        def auto_test_sequence():
            test_events = [
                ('left', 'cw'),
                ('right', 'cw'),
                ('right', 'ccw'),
                ('left', 'ccw'),
            ]
            
            for dial, direction in test_events:
                self._send_dial_event(dial, direction)
                time.sleep(0.5)
            
            # 模擬按鈕測試
            self._send_button_event('shutter', 'half_press')
            time.sleep(0.2)
            self._send_button_event('shutter', 'full_press')
            
            self._log_event("自動測試序列完成")
        
        # 在背景執行測試
        threading.Thread(target=auto_test_sequence, daemon=True).start()
        self._log_event("開始自動測試序列...")
    
    def _on_simulator_close(self):
        """模擬器視窗關閉事件"""
        self.simulation_window.destroy()
        self.simulation_window = None
        logger.info("硬體模擬器視窗已關閉")
    
    def cleanup(self):
        """清理模擬器資源"""
        self._running = False
        
        if self.simulation_window:
            try:
                self.simulation_window.destroy()
            except:
                pass
            self.simulation_window = None
        
        logger.info("硬體模擬器已清理")