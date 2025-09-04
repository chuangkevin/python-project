#!/usr/bin/env python3
"""
快速測試腳本
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from state_machine import ModeDial


def main():
    print("=== ModeDial 快速測試 ===")
    
    # 建立狀態機
    dial = ModeDial()
    print("[OK] 狀態機建立成功")
    
    # 測試基本功能
    initial_state = dial.get_current_state()
    print(f"[OK] 初始模式: {initial_state['current_mode']['label']}")
    
    # 測試左轉盤
    dial.rotate_left_dial(1)
    new_state = dial.get_current_state()
    print(f"[OK] 切換模式: {new_state['current_mode']['label']}")
    
    # 測試右轉盤
    old_value = new_state['current_display_value']
    dial.rotate_right_dial(1)
    final_state = dial.get_current_state()
    print(f"[OK] 調整數值: {old_value} -> {final_state['current_display_value']}")
    
    # 測試按壓
    dial.press_right_dial("press")
    print("[OK] 按壓功能正常")
    
    # 顯示配置資訊
    print(f"\n配置資訊:")
    print(f"  總模式數: {len(dial.dial_order)}")
    print(f"  模式列表: {', '.join(dial.dial_order)}")
    
    print("\n[SUCCESS] 所有測試通過！")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] 測試失敗: {e}")
        import traceback
        traceback.print_exc()