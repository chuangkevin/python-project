#!/usr/bin/env python3
"""
RD-1 Camera Control - 硬體管理器
統一管理所有硬體元件：GPIO、I2C、SPI、編碼器、按鈕、螢幕等
"""

import logging
import threading
import time
from collections import deque
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class HardwareManager:
    """硬體管理器 - 統一管理所有硬體元件"""
    
    def __init__(self, development_mode=False, raspberry_pi=False):
        self.development_mode = development_mode
        self.raspberry_pi = raspberry_pi
        self.initialized = False
        self.event_queue = deque()
        self._event_lock = threading.Lock()
        
        # 硬體元件
        self.gpio_controller = None
        self.button_handler = None
        self.encoder_handler = None
        self.display_controller = None
        
        logger.info(f"硬體管理器初始化 - 開發模式: {development_mode}, Pi模式: {raspberry_pi}")
    
    def initialize(self):
        """初始化所有硬體元件"""
        logger.info("正在初始化硬體元件...")
        
        try:
            if self.raspberry_pi:
                self._init_raspberry_pi_hardware()
            else:
                self._init_development_hardware()
            
            self.initialized = True
            logger.info("✅ 硬體管理器初始化完成")
            
        except Exception as e:
            logger.error(f"硬體初始化失敗: {e}")
            # 回退到開發模式
            self.development_mode = True
            self._init_development_hardware()
    
    def _init_raspberry_pi_hardware(self):
        """初始化 Raspberry Pi 硬體"""
        logger.info("正在初始化 Raspberry Pi 硬體...")
        
        try:
            # GPIO 控制器
            from systemControl.hardware.gpio_controller import GPIOController
            self.gpio_controller = GPIOController()
            self.gpio_controller.initialize()
            
            # 按鈕處理器
            from systemControl.hardware.button_handler import ButtonHandler
            self.button_handler = ButtonHandler(self.gpio_controller)
            self.button_handler.set_event_callback(self._on_hardware_event)
            
            # 編碼器處理器 (雙轉盤)
            from systemControl.hardware.encoder_handler import EncoderHandler
            self.encoder_handler = EncoderHandler(self.gpio_controller)
            self.encoder_handler.set_event_callback(self._on_hardware_event)
            
            # 顯示控制器 (雙螢幕)
            from systemControl.hardware.display_controller import DisplayController
            self.display_controller = DisplayController()
            self.display_controller.initialize()
            
            logger.info("✅ Raspberry Pi 硬體初始化完成")
            
        except ImportError as e:
            logger.error(f"硬體模組導入失敗: {e}")
            raise
        except Exception as e:
            logger.error(f"Pi 硬體初始化失敗: {e}")
            raise
    
    def _init_development_hardware(self):
        """初始化開發模式硬體 (模擬)"""
        logger.info("正在初始化開發模式硬體模擬器...")
        
        try:
            # 使用模擬器
            from systemControl.hardware.simulator import HardwareSimulator
            self.simulator = HardwareSimulator()
            self.simulator.set_event_callback(self._on_hardware_event)
            
            logger.info("✅ 開發模式硬體模擬器初始化完成")
            
        except Exception as e:
            logger.warning(f"開發模式硬體初始化失敗: {e}")
            # 繼續執行，只是沒有硬體事件
    
    def _on_hardware_event(self, event):
        """硬體事件回調函數"""
        with self._event_lock:
            self.event_queue.append(event)
            logger.debug(f"硬體事件: {event}")
    
    def poll_events(self) -> List[Dict[str, Any]]:
        """輪詢硬體事件"""
        events = []
        
        with self._event_lock:
            while self.event_queue:
                events.append(self.event_queue.popleft())
        
        return events
    
    def update_setting(self, category: str, key: str, value: Any):
        """更新硬體設定"""
        try:
            if category == 'display':
                if self.display_controller:
                    self.display_controller.update_setting(key, value)
            elif category == 'camera':
                # 相機設定會在相機界面處理
                pass
            elif category == 'hardware':
                # 硬體特定設定
                if key == 'encoder_sensitivity':
                    if self.encoder_handler:
                        self.encoder_handler.set_sensitivity(value)
                elif key == 'button_debounce':
                    if self.button_handler:
                        self.button_handler.set_debounce_time(value)
                        
            logger.info(f"硬體設定更新: {category}.{key} = {value}")
            
        except Exception as e:
            logger.error(f"硬體設定更新失敗: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """取得硬體狀態"""
        status = {
            'initialized': self.initialized,
            'development_mode': self.development_mode,
            'raspberry_pi': self.raspberry_pi
        }
        
        if self.raspberry_pi:
            if self.gpio_controller:
                status['gpio'] = self.gpio_controller.get_status()
            if self.display_controller:
                status['display'] = self.display_controller.get_status()
        
        return status
    
    def trigger_haptic_feedback(self, intensity: float = 1.0):
        """觸發觸覺回饋"""
        try:
            if self.development_mode:
                logger.info(f"模擬觸覺回饋: {intensity}")
            elif self.gpio_controller:
                # 實際的觸覺回饋實作
                self.gpio_controller.trigger_haptic(intensity)
        except Exception as e:
            logger.error(f"觸覺回饋失敗: {e}")
    
    def update_display(self, display_id: str, content: Dict[str, Any]):
        """更新顯示內容"""
        try:
            if self.display_controller:
                self.display_controller.update_display(display_id, content)
            elif self.development_mode:
                logger.info(f"模擬顯示更新 [{display_id}]: {content}")
        except Exception as e:
            logger.error(f"顯示更新失敗: {e}")
    
    def set_led_state(self, led_id: str, state: bool):
        """設定 LED 狀態"""
        try:
            if self.gpio_controller:
                self.gpio_controller.set_led_state(led_id, state)
            elif self.development_mode:
                logger.info(f"模擬 LED 狀態 [{led_id}]: {state}")
        except Exception as e:
            logger.error(f"LED 狀態設定失敗: {e}")
    
    def simulate_button_press(self, button_id: str, action: str = 'press'):
        """模擬按鈕按壓 (開發模式用)"""
        if self.development_mode:
            event = {
                'type': 'button_press',
                'button': button_id,
                'action': action,
                'timestamp': time.time()
            }
            self._on_hardware_event(event)
    
    def simulate_dial_rotation(self, dial: str, direction: str):
        """模擬轉盤旋轉 (開發模式用)"""
        if self.development_mode:
            event = {
                'type': 'dial_rotation',
                'dial': dial,  # 'left' or 'right'
                'direction': direction,  # 'cw' or 'ccw'
                'timestamp': time.time()
            }
            self._on_hardware_event(event)
    
    def cleanup(self):
        """清理硬體資源"""
        logger.info("正在清理硬體資源...")
        
        try:
            if self.gpio_controller:
                self.gpio_controller.cleanup()
            
            if self.display_controller:
                self.display_controller.cleanup()
                
            if hasattr(self, 'simulator'):
                self.simulator.cleanup()
            
            self.initialized = False
            logger.info("✅ 硬體資源清理完成")
            
        except Exception as e:
            logger.error(f"硬體清理失敗: {e}")


class MockHardware:
    """硬體模擬器 - 用於開發和測試"""
    
    def __init__(self):
        self.event_callback = None
        self._running = False
        self._thread = None
    
    def set_event_callback(self, callback):
        """設定事件回調函數"""
        self.event_callback = callback
    
    def start_simulation(self):
        """開始模擬硬體事件"""
        self._running = True
        self._thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self._thread.start()
    
    def _simulation_loop(self):
        """模擬迴圈 - 產生測試事件"""
        while self._running:
            # 定期產生測試事件
            time.sleep(5)
            
            if self.event_callback:
                # 模擬轉盤旋轉
                self.event_callback({
                    'type': 'dial_rotation',
                    'dial': 'left',
                    'direction': 'cw',
                    'timestamp': time.time()
                })
    
    def cleanup(self):
        """清理模擬器"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)