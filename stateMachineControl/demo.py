#!/usr/bin/env python3
"""
ModeDial 功能展示
"""

import os
import sys
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from state_machine import ModeDial


def print_current_state(dial, title=""):
    """顯示當前狀態"""
    if title:
        print(f"\n=== {title} ===")
    
    state = dial.get_current_state()
    current_mode = state.get('current_mode', {})
    
    print(f"模式: {current_mode.get('label', 'N/A')}")
    print(f"值:   {state.get('current_display_value', 'N/A')}")
    print(f"索引: {state.get('current_mode_index')}/{state.get('total_modes', 0)-1}")


def demo_enum_mode(dial):
    """展示 enum 類型模式（快門速度）"""
    print_current_state(dial, "Enum 模式展示 - 快門速度")
    
    # 確保在快門模式
    while dial.get_current_mode_id() != "shutter":
        dial.rotate_left_dial(1)
    
    print("調整快門速度:")
    for i in range(5):
        dial.rotate_right_dial(1)
        state = dial.get_current_state()
        print(f"  步驟 {i+1}: {state.get('current_display_value')}")
        time.sleep(0.2)


def demo_range_mode(dial):
    """展示 range 類型模式（EV 補償）"""
    print_current_state(dial, "Range 模式展示 - EV 補償")
    
    # 切換到 EV 模式
    while dial.get_current_mode_id() != "ev":
        dial.rotate_left_dial(1)
    
    print("調整 EV 補償:")
    # 先調整到負值
    for i in range(3):
        dial.rotate_right_dial(-1)
    
    for i in range(7):
        dial.rotate_right_dial(1)
        state = dial.get_current_state()
        print(f"  步驟 {i+1}: {state.get('current_display_value')}")
        time.sleep(0.2)


def demo_toggle_mode(dial):
    """展示 toggle 類型模式（閃燈）"""
    print_current_state(dial, "Toggle 模式展示 - 閃燈")
    
    # 切換到閃燈模式
    while dial.get_current_mode_id() != "flash":
        dial.rotate_left_dial(1)
    
    print("切換閃燈開關:")
    for i in range(4):
        dial.press_right_dial("press")  # toggle 用按壓切換
        state = dial.get_current_state()
        print(f"  步驟 {i+1}: {state.get('current_display_value')}")
        time.sleep(0.3)


def demo_all_modes(dial):
    """展示所有模式"""
    print_current_state(dial, "所有模式巡覽")
    
    for i in range(len(dial.dial_order)):
        dial.current_mode_index = i
        state = dial.get_current_state()
        current_mode = state.get('current_mode', {})
        
        mode_info = f"{i+1:2d}. {current_mode.get('id', 'N/A'):12s}"
        mode_info += f" - {current_mode.get('label', 'N/A'):15s}"
        mode_info += f" ({current_mode.get('type', 'N/A'):6s})"
        mode_info += f" = {state.get('current_display_value', 'N/A')}"
        
        print(mode_info)
        time.sleep(0.1)


def demo_callbacks(dial):
    """展示回調函數"""
    print_current_state(dial, "回調函數展示")
    
    # 設定回調函數
    def on_mode_changed(index, mode):
        mode_label = mode.get('label', 'N/A') if mode else 'None'
        print(f"  [回調] 模式變更: {mode_label}")
    
    def on_value_changed(mode_id, old_value, new_value):
        print(f"  [回調] 值變更 [{mode_id}]: {old_value} -> {new_value}")
    
    def on_binding_triggered(mode_id, bindings, value):
        print(f"  [回調] 綁定觸發 [{mode_id}]: {bindings}")
    
    dial.set_callbacks(on_mode_changed, on_value_changed, on_binding_triggered)
    
    print("執行操作並觀察回調:")
    print("1. 切換模式")
    dial.rotate_left_dial(1)
    
    print("2. 調整數值")
    dial.rotate_right_dial(1)
    
    print("3. 按壓確認")
    dial.press_right_dial("press")


def main():
    print("=== ModeDial 功能展示 ===")
    
    try:
        # 建立狀態機
        dial = ModeDial()
        print("[OK] 狀態機初始化完成")
        
        # 各種展示
        demo_all_modes(dial)
        time.sleep(1)
        
        demo_enum_mode(dial)
        time.sleep(1)
        
        demo_range_mode(dial)
        time.sleep(1)
        
        demo_toggle_mode(dial)
        time.sleep(1)
        
        demo_callbacks(dial)
        
        print(f"\n=== 展示完成 ===")
        print("系統功能:")
        print("- JSON 驅動的配置系統")
        print("- 11 種預定義模式")
        print("- 4 種模式類型: enum, range, toggle, action")
        print("- 完整的回調事件系統")
        print("- 硬體綁定抽象層")
        
        print(f"\n[SUCCESS] 所有功能展示完成！")
        
    except Exception as e:
        print(f"[ERROR] 展示失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())