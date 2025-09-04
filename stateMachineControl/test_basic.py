#!/usr/bin/env python3
"""
基本功能測試腳本
測試狀態機的核心功能
"""

import os
import sys

# 添加 src 目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from state_machine import ModeDial


def test_basic_functionality():
    """測試基本功能"""
    print("=== 基本功能測試 ===")
    
    # 建立狀態機
    dial = ModeDial()
    
    print(f"初始狀態: {dial.get_current_mode_id()}")
    print(f"可用模式: {dial.dial_order}")
    
    # 測試左轉盤
    print("\n--- 測試左轉盤 ---")
    for i in range(3):
        dial.rotate_left_dial(1)
        current_mode = dial.get_current_mode()
        print(f"模式 {i+1}: {current_mode.get('id')} - {current_mode.get('label')}")
    
    # 測試右轉盤
    print("\n--- 測試右轉盤 ---")
    for i in range(3):
        old_state = dial.get_current_state()
        dial.rotate_right_dial(1)
        new_state = dial.get_current_state()
        
        print(f"調整 {i+1}: {old_state.get('current_display_value')} → {new_state.get('current_display_value')}")
    
    # 測試按壓
    print("\n--- 測試按壓 ---")
    dial.press_right_dial("press")
    print("執行按壓動作")
    
    # 顯示最終狀態
    final_state = dial.get_current_state()
    print(f"\n最終狀態:")
    print(f"  當前模式: {final_state.get('current_mode', {}).get('label')}")
    print(f"  當前值: {final_state.get('current_display_value')}")
    print(f"  模式索引: {final_state.get('current_mode_index')}")


def test_all_modes():
    """測試所有模式"""
    print("\n=== 所有模式測試 ===")
    
    dial = ModeDial()
    
    for i, mode_id in enumerate(dial.dial_order):
        # 切換到該模式
        dial.current_mode_index = i
        current_mode = dial.get_current_mode()
        
        print(f"\n模式 {i}: {mode_id}")
        print(f"  標籤: {current_mode.get('label')}")
        print(f"  類型: {current_mode.get('type')}")
        print(f"  提示: {current_mode.get('hint', '無')}")
        
        # 測試該模式的操作
        if current_mode.get('type') in ['enum', 'range']:
            # 測試右轉盤調整
            old_value = dial.current_values.get(mode_id, "無")
            dial.rotate_right_dial(1)
            new_value = dial.current_values.get(mode_id, "無")
            print(f"  值調整: {old_value} → {new_value}")


def interactive_test():
    """互動測試"""
    print("\n=== 互動測試 ===")
    print("指令: l=左轉盤+, L=左轉盤-, r=右轉盤+, R=右轉盤-, p=按壓, s=狀態, q=退出")
    
    dial = ModeDial()
    
    # 設定回調函數
    def on_mode_changed(index, mode):
        print(f"[事件] 模式變更: {mode.get('label') if mode else '無'}")
    
    def on_value_changed(mode_id, old_value, new_value):
        print(f"[事件] 值變更 [{mode_id}]: {old_value} → {new_value}")
    
    def on_binding_triggered(mode_id, bindings, value):
        print(f"[事件] 綁定觸發 [{mode_id}]: {bindings}")
    
    dial.set_callbacks(on_mode_changed, on_value_changed, on_binding_triggered)
    
    while True:
        state = dial.get_current_state()
        current_mode = state.get('current_mode', {})
        
        print(f"\n當前: {current_mode.get('label', '無')} = {state.get('current_display_value', '無')}")
        
        try:
            cmd = input("指令: ").strip().lower()
            
            if cmd == 'q':
                break
            elif cmd == 'l':
                dial.rotate_left_dial(1)
            elif cmd == 'L':
                dial.rotate_left_dial(-1)
            elif cmd == 'r':
                dial.rotate_right_dial(1)
            elif cmd == 'R':
                dial.rotate_right_dial(-1)
            elif cmd == 'p':
                dial.press_right_dial("press")
            elif cmd == 's':
                state = dial.get_current_state()
                print("完整狀態:")
                for key, value in state.items():
                    if key not in ['current_values']:  # 簡化顯示
                        print(f"  {key}: {value}")
            else:
                print("未知指令")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"錯誤: {e}")
    
    print("互動測試結束")


def main():
    """主函數"""
    print("ModeDial 基本測試")
    print("==================")
    
    try:
        # 執行測試
        test_basic_functionality()
        test_all_modes()
        
        # 詢問是否進行互動測試
        if input("\n是否進行互動測試? (y/N): ").lower() == 'y':
            interactive_test()
        
        print("\n測試完成!")
        
    except Exception as e:
        print(f"測試錯誤: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())