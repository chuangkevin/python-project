#!/usr/bin/env python3
"""
RD-1 Style Camera Control System - 輕量化單體應用
Raspberry Pi 專用相機控制軟體

架構設計：
- 單一 Python 應用程式
- tkinter GUI 界面
- 硬體直接控制 (GPIO/I2C/SPI)
- 整合 stateMachineControl 模組
"""

import sys
import os
import logging
from pathlib import Path

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    logger.error("tkinter 未安裝，請執行: sudo apt-get install python3-tk")
    sys.exit(1)

# 導入模組
from core.application import CameraApplication
from hardware.hardware_manager import HardwareManager
from settings.settings_manager import SettingsManager

def check_platform():
    """檢查執行平台並設定對應模式"""
    import platform
    
    is_pi = platform.machine().startswith('arm') or platform.machine().startswith('aarch64')
    is_dev = not is_pi
    
    logger.info(f"Platform: {platform.machine()}")
    logger.info(f"Running on Pi: {is_pi}, Development mode: {is_dev}")
    
    return is_pi, is_dev

def main():
    """主程式入口點"""
    logger.info("🚀 啟動 RD-1 Camera Control System")
    
    # 檢查平台
    is_pi, is_dev = check_platform()
    
    try:
        # 創建主應用程式
        app = CameraApplication(
            development_mode=is_dev,
            raspberry_pi=is_pi
        )
        
        # 初始化並啟動
        app.initialize()
        app.run()
        
    except KeyboardInterrupt:
        logger.info("收到中斷信號，正在關閉...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"應用程式錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()