#!/usr/bin/env python3
"""
SystemControl 模組展示腳本
展示系統控制模組的基本功能
"""

import sys
import os

# 添加當前目錄到路徑
sys.path.insert(0, os.path.dirname(__file__))

from core.system_manager import SystemManager

def demo_system_control():
    """展示系統控制功能"""
    print("=== SystemControl 模組展示 ===\n")
    
    # 初始化系統管理器
    print("🔧 初始化系統管理器...")
    system_manager = SystemManager()
    
    if system_manager.initialize_system():
        print("✅ 系統初始化成功\n")
    else:
        print("❌ 系統初始化失敗\n")
        return
    
    # 顯示系統狀態
    print("📊 系統狀態:")
    status = system_manager.get_system_status()
    for key, value in status.items():
        print(f"   {key}: {value}")
    print()
    
    # 展示模式切換
    print("🔄 模式切換測試:")
    modes = ["photo", "video", "manual"]
    for mode in modes:
        success = system_manager.switch_mode(mode)
        print(f"   切換至 {mode} 模式: {'✅' if success else '❌'}")
    print()
    
    # 展示設定模組
    print("⚙️ 設定模組展示:")
    print(f"   相機設定 - 影像品質: {system_manager.camera_settings.image_quality}")
    print(f"   顯示設定 - 主螢幕亮度: {system_manager.display_settings.main_brightness}")
    print(f"   轉盤設定 - 當前配置: {system_manager.dial_settings.current_profile}")
    print(f"   電源設定 - 低電量警告: {system_manager.power_settings.low_battery_warning}%")
    print(f"   儲存設定 - 當前路徑: {system_manager.storage_settings.current_storage_path}")
    print()
    
    # 展示轉盤整合 (如果可用)
    if system_manager.mode_dial:
        print("🎛️ 雙轉盤整合:")
        print("   ✅ stateMachineControl 整合成功")
        
        # 取得當前狀態
        state = system_manager.mode_dial.get_current_state()
        print(f"   當前模式: {state.get('current_mode', {}).get('label', 'N/A')}")
        print(f"   當前值: {state.get('current_display_value', 'N/A')}")
    else:
        print("🎛️ 雙轉盤整合:")
        print("   ⚠️ stateMachineControl 模組未找到")
    print()
    
    # 模擬系統關機
    print("🔌 模擬系統關機...")
    system_manager.shutdown_system()
    print("✅ 系統已安全關機")
    
    print("\n=== 展示完成 ===")
    print("📁 SystemControl 模組已建立完整架構")
    print("🔧 各設定模組已準備就緒，待後續實作")
    print("🎛️ 與 stateMachineControl 整合完成")

def show_module_structure():
    """顯示模組結構"""
    print("\n=== SystemControl 模組結構 ===")
    print("systemControl/")
    print("├── settings/              # 設定核心")
    print("│   ├── camera_settings.py      # 相機參數")
    print("│   ├── display_settings.py     # 螢幕設定")
    print("│   ├── dial_settings.py        # 轉盤設定")
    print("│   ├── power_settings.py       # 電源管理")
    print("│   └── storage_settings.py     # 儲存管理")
    print("├── ui/                    # 設定界面")
    print("│   ├── settings_menu.py        # 主設定選單")
    print("│   └── dial_config_ui.py       # 轉盤配置界面")
    print("├── config/                # 配置檔案")
    print("│   ├── system.json             # 系統配置")
    print("│   └── dial_profiles/          # 轉盤配置檔案")
    print("│       ├── default.json        # 預設模式")
    print("│       ├── video.json          # 錄影模式")
    print("│       └── manual.json         # 手動模式")
    print("├── core/                  # 核心管理")
    print("│   └── system_manager.py       # 系統管理器")
    print("└── demo.py                # 展示腳本")

if __name__ == "__main__":
    try:
        demo_system_control()
        show_module_structure()
    except KeyboardInterrupt:
        print("\n程序被用戶中斷")
    except Exception as e:
        print(f"\n展示過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()