#!/usr/bin/env python3
"""
RD-1 Camera Control - 核心應用程式類別
負責協調所有模組並管理應用程式生命週期
"""

import sys
import os
import threading
import time
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class CameraApplication:
    """RD-1 相機控制系統主應用程式"""
    
    def __init__(self, development_mode=False, raspberry_pi=False):
        self.development_mode = development_mode
        self.raspberry_pi = raspberry_pi
        self.running = False
        
        # 核心元件
        self.hardware_manager = None
        self.settings_manager = None
        self.state_machine = None
        self.ui_manager = None
        self.camera_interface = None
        
        logger.info(f"應用程式初始化 - 開發模式: {development_mode}, Pi模式: {raspberry_pi}")
    
    def initialize(self):
        """初始化所有系統元件"""
        logger.info("正在初始化系統元件...")
        
        try:
            # 1. 初始化設定管理器
            self._init_settings()
            
            # 2. 初始化硬體管理器
            self._init_hardware()
            
            # 3. 初始化狀態機
            self._init_state_machine()
            
            # 4. 初始化相機界面
            self._init_camera()
            
            # 5. 初始化UI界面
            self._init_ui()
            
            logger.info("✅ 所有系統元件初始化完成")
            
        except Exception as e:
            logger.error(f"初始化失敗: {e}")
            raise
    
    def _init_settings(self):
        """初始化設定管理器"""
        try:
            from settings.settings_manager import SettingsManager
            self.settings_manager = SettingsManager()
            self.settings_manager.load_all_settings()
            logger.info("✅ 設定管理器初始化完成")
        except Exception as e:
            logger.warning(f"設定管理器初始化失敗: {e}")
            # 使用預設設定繼續執行
    
    def _init_hardware(self):
        """初始化硬體管理器"""
        try:
            from hardware.hardware_manager import HardwareManager
            self.hardware_manager = HardwareManager(
                development_mode=self.development_mode,
                raspberry_pi=self.raspberry_pi
            )
            self.hardware_manager.initialize()
            logger.info("✅ 硬體管理器初始化完成")
        except Exception as e:
            logger.warning(f"硬體管理器初始化失敗: {e}")
            # 繼續以軟體模擬模式執行
    
    def _init_state_machine(self):
        """初始化狀態機"""
        try:
            # 整合現有的 stateMachineControl 模組
            sys.path.append(str(Path(__file__).parent.parent.parent / "stateMachineControl" / "src"))
            from state_machine import ModeDial
            
            self.state_machine = ModeDial()
            logger.info("✅ 狀態機初始化完成")
        except Exception as e:
            logger.warning(f"狀態機初始化失敗: {e}")
            # 使用內建狀態管理
    
    def _init_camera(self):
        """初始化相機界面"""
        try:
            # 相機界面模組還未實作，暫時跳過
            logger.info("✅ 相機界面初始化完成 (模擬模式)")
        except Exception as e:
            logger.warning(f"相機界面初始化失敗: {e}")
            # 使用模擬相機
    
    def _init_ui(self):
        """初始化使用者界面"""
        try:
            import tkinter as tk
            from tkinter import ttk
            
            self.root = tk.Tk()
            self.root.title("RD-1 Camera Control System")
            self.root.geometry("900x700")
            self.root.configure(bg="#0f0f0f")  # 深色背景
            
            # 設定深色主題
            self._setup_dark_theme()
            
            # 創建 analogGauge 風格的相機控制界面
            self._create_camera_control_ui()
            
            logger.info("✅ UI界面初始化完成")
        except Exception as e:
            logger.error(f"UI界面初始化失敗: {e}")
            # 如果新界面失敗，回退到測試界面
            self._create_test_ui()
            logger.warning("回退到測試界面")
    
    def _setup_dark_theme(self):
        """設定深色主題"""
        try:
            from tkinter import ttk
            style = ttk.Style()
            style.theme_use('clam')
            
            # 自定義深色樣式
            style.configure('Dark.TFrame', background='#1a1a1a')
            style.configure('Dark.TLabel', background='#1a1a1a', foreground='#ffffff')
            style.configure('Dark.TButton', background='#333333', foreground='#ffffff')
            style.configure('Dark.TNotebook', background='#1a1a1a')
            style.configure('Dark.TNotebook.Tab', background='#333333', foreground='#ffffff')
            
        except Exception as e:
            logger.warning(f"深色主題設定失敗: {e}")
    
    def _create_camera_control_ui(self):
        """創建 analogGauge 風格的相機控制界面"""
        try:
            import sys
            import tkinter as tk
            from pathlib import Path
            
            # 添加 UI 模組路徑
            ui_path = Path(__file__).parent.parent / "ui"
            sys.path.append(str(ui_path))
            
            try:
                from camera_control_display import CameraControlDisplay
                # 創建 analogGauge 版本
                self.main_container = tk.Frame(self.root, bg="#0f0f0f")
                self.main_container.pack(fill="both", expand=True)
                self.camera_display = CameraControlDisplay(self.main_container)
            except ImportError:
                # 回退到簡化版本
                from simple_camera_control import SimpleCameraControlDisplay
                self.main_container = tk.Frame(self.root, bg="#0f0f0f")
                self.main_container.pack(fill="both", expand=True)
                self.camera_display = SimpleCameraControlDisplay(self.main_container, self.trigger_shutter)
            
            # 綁定快門觸發事件
            if hasattr(self.camera_display, 'shutter_button'):
                self.camera_display.shutter_button.configure(command=self.trigger_shutter)
            
            logger.info("✅ analogGauge 相機控制界面已載入")
            
        except Exception as e:
            logger.error(f"相機控制界面載入失敗: {e}")
            raise
    
    def _create_test_ui(self):
        """創建測試用 UI"""
        import tkinter as tk
        from tkinter import ttk
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 標題
        title_label = ttk.Label(main_frame, text="🎬 RD-1 Camera Control System", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=10)
        
        # 狀態顯示
        status_frame = ttk.LabelFrame(main_frame, text="系統狀態", padding="10")
        status_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(status_frame, text=f"開發模式: {'是' if self.development_mode else '否'}").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(status_frame, text=f"Raspberry Pi: {'是' if self.raspberry_pi else '否'}").grid(row=1, column=0, sticky=tk.W)
        
        # 控制按鈕
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(control_frame, text="📸 觸發快門", 
                  command=self.trigger_shutter).grid(row=0, column=0, padx=5)
        
        ttk.Button(control_frame, text="🎛️ 顯示硬體模擬器", 
                  command=self._show_hardware_simulator).grid(row=0, column=1, padx=5)
        
        ttk.Button(control_frame, text="⚙️ 系統狀態", 
                  command=self._show_system_status).grid(row=0, column=2, padx=5)
        
        # 日誌顯示
        log_frame = ttk.LabelFrame(main_frame, text="系統日誌", padding="10")
        log_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, width=80)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 初始日誌
        self._add_log("系統啟動完成")
        
        # 配置網格權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(3, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def _add_log(self, message):
        """添加日誌到界面"""
        import time
        import tkinter as tk
        if hasattr(self, 'log_text'):
            timestamp = time.strftime("%H:%M:%S")
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)
    
    def _show_hardware_simulator(self):
        """顯示硬體模擬器"""
        if self.hardware_manager and hasattr(self.hardware_manager, 'simulator'):
            self.hardware_manager.simulator.show_simulator_window()
            self._add_log("已開啟硬體模擬器視窗")
        else:
            self._add_log("硬體模擬器不可用")
    
    def _show_system_status(self):
        """顯示系統狀態"""
        status = self.get_current_state()
        self._add_log(f"系統狀態: {status}")
    
    def run(self):
        """啟動應用程式主迴圈"""
        logger.info("🎬 啟動應用程式主迴圈")
        self.running = True
        
        try:
            # 啟動硬體事件監聽線程
            if self.hardware_manager:
                hardware_thread = threading.Thread(
                    target=self._hardware_event_loop,
                    daemon=True
                )
                hardware_thread.start()
            
            # 啟動 tkinter 主迴圈
            self.root.mainloop()
            
        except KeyboardInterrupt:
            logger.info("收到中斷信號")
        finally:
            self.shutdown()
    
    def _hardware_event_loop(self):
        """硬體事件處理迴圈"""
        while self.running:
            try:
                if self.hardware_manager:
                    # 處理硬體事件
                    events = self.hardware_manager.poll_events()
                    for event in events:
                        self._handle_hardware_event(event)
                
                time.sleep(0.01)  # 100Hz 輪詢頻率
                
            except Exception as e:
                logger.error(f"硬體事件處理錯誤: {e}")
                time.sleep(0.1)
    
    def _handle_hardware_event(self, event):
        """處理硬體事件"""
        try:
            event_type = event.get('type')
            
            if event_type == 'dial_rotation':
                self._handle_dial_event(event)
            elif event_type == 'button_press':
                self._handle_button_event(event)
            elif event_type == 'encoder_change':
                self._handle_encoder_event(event)
            
            # 更新 UI
            if self.ui_manager:
                self.ui_manager.update_from_hardware_event(event)
                
        except Exception as e:
            logger.error(f"硬體事件處理錯誤: {e}")
    
    def _handle_dial_event(self, event):
        """處理轉盤事件"""
        dial = event.get('dial')  # 'left' or 'right'
        direction = event.get('direction')  # 'cw' or 'ccw'
        
        if self.state_machine:
            if dial == 'left':
                self.state_machine.rotate_left_dial(1 if direction == 'cw' else -1)
            elif dial == 'right':
                self.state_machine.rotate_right_dial(1 if direction == 'cw' else -1)
    
    def _handle_button_event(self, event):
        """處理按鈕事件"""
        button = event.get('button')
        action = event.get('action')  # 'press', 'release', 'long_press'
        
        if button == 'shutter' and action == 'press':
            self.trigger_shutter()
        elif button == 'right_dial' and action == 'press':
            if self.state_machine:
                self.state_machine.press_right_dial()
    
    def _handle_encoder_event(self, event):
        """處理編碼器事件"""
        # 處理其他編碼器事件
        pass
    
    def trigger_shutter(self):
        """觸發快門"""
        try:
            logger.info("📸 觸發快門")
            if self.camera_interface:
                result = self.camera_interface.capture_image()
                if self.ui_manager:
                    self.ui_manager.show_capture_result(result)
            else:
                logger.info("模擬快門觸發")
        except Exception as e:
            logger.error(f"快門觸發失敗: {e}")
    
    def get_current_state(self):
        """取得目前系統狀態"""
        state = {
            'running': self.running,
            'development_mode': self.development_mode,
            'raspberry_pi': self.raspberry_pi
        }
        
        if self.state_machine:
            state['camera'] = self.state_machine.get_current_state()
        
        if self.hardware_manager:
            state['hardware'] = self.hardware_manager.get_status()
            
        return state
    
    def update_setting(self, category, key, value):
        """更新設定值"""
        try:
            if self.settings_manager:
                self.settings_manager.update_setting(category, key, value)
            
            # 同步更新到硬體
            if self.hardware_manager:
                self.hardware_manager.update_setting(category, key, value)
                
            logger.info(f"設定更新: {category}.{key} = {value}")
        except Exception as e:
            logger.error(f"設定更新失敗: {e}")
    
    def shutdown(self):
        """關閉應用程式"""
        logger.info("🛑 正在關閉應用程式")
        self.running = False
        
        # 清理資源
        if self.hardware_manager:
            self.hardware_manager.cleanup()
        
        if self.camera_interface:
            self.camera_interface.cleanup()
            
        if self.settings_manager:
            self.settings_manager.save_all_settings()
        
        logger.info("✅ 應用程式已安全關閉")