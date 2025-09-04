#!/usr/bin/env python3
"""
驗證配置檔案
"""

import os
import sys
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from loader import ConfigLoader


def main():
    print("=== 配置檔案驗證 ===")
    
    try:
        # 載入配置
        config_path = "configs/mode_dial.default.json"
        schema_path = "schema/mode_dial.schema.json"
        
        print(f"載入配置: {config_path}")
        loader = ConfigLoader()
        loader.load_config(config_path)
        print("[OK] 配置檔案載入成功")
        
        print(f"載入 Schema: {schema_path}")
        loader.load_schema(schema_path)
        print("[OK] Schema 載入成功")
        
        # 驗證配置
        print("驗證配置...")
        loader.validate_config()
        print("[OK] 配置驗證通過")
        
        # 顯示配置資訊
        dial_order = loader.get_dial_order()
        modes = loader.get_modes()
        
        print(f"\n配置資訊:")
        print(f"  版本: {loader.config_data.get('version', 'N/A')}")
        print(f"  模式數量: {len(modes)}")
        print(f"  轉盤順序: {len(dial_order)} 個模式")
        
        print(f"\n模式列表:")
        for i, mode_id in enumerate(dial_order):
            mode = loader.get_mode_by_id(mode_id)
            if mode:
                print(f"  {i+1:2d}. {mode_id:12s} - {mode.get('label', 'N/A'):15s} ({mode.get('type', 'N/A')})")
        
        # 測試特定模式
        print(f"\n測試模式查詢:")
        test_modes = ['shutter', 'iso', 'ev']
        for mode_id in test_modes:
            mode = loader.get_mode_by_id(mode_id)
            if mode:
                print(f"  {mode_id}: {mode.get('label')} - {mode.get('type')}")
        
        print(f"\n[SUCCESS] 配置檔案驗證完成！")
        
    except Exception as e:
        print(f"[ERROR] 驗證失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())