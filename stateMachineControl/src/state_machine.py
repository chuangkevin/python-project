"""
雙轉盤狀態機核心
管理左轉盤模式選擇和右轉盤數值調整
"""

from typing import Dict, Any, Optional, List, Callable
try:
    from .loader import ConfigLoader
except ImportError:
    from loader import ConfigLoader


class ModeDial:
    """
    雙轉盤相機控制狀態機
    
    左轉盤：模式選擇
    右轉盤：數值調整
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化模式轉盤
        
        Args:
            config_path: 配置檔案路徑，None 則使用預設配置
        """
        # 載入配置
        if config_path:
            self.config_loader = ConfigLoader()
            self.config_loader.load_config(config_path)
        else:
            self.config_loader = ConfigLoader.load_default_config()
        
        # 驗證配置
        try:
            self.config_loader.validate_config()
        except Exception as e:
            print(f"配置驗證警告: {e}")
        
        # 初始化狀態
        self.dial_order = self.config_loader.get_dial_order()
        self.modes = self.config_loader.get_modes()
        self.current_mode_index = 0
        self.current_values = {}  # 儲存每個模式的當前值
        self.sub_mode_stack = []  # 子模式堆疊（用於 group 類型）
        
        # 回調函數
        self.on_value_changed = None  # 值變更回調
        self.on_mode_changed = None   # 模式變更回調
        self.on_binding_triggered = None  # 綁定觸發回調
        
        # 初始化所有模式的預設值
        self._init_default_values()
    
    def _init_default_values(self):
        """初始化所有模式的預設值"""
        for mode in self.modes:
            mode_id = mode.get("id")
            mode_type = mode.get("type")
            
            if mode_type == "enum":
                # enum 類型：預設第一個選項
                enum_options = mode.get("enum", [])
                if enum_options:
                    self.current_values[mode_id] = 0  # 索引
            
            elif mode_type == "range":
                # range 類型：預設中間值
                range_config = mode.get("range", {})
                min_val = range_config.get("min", 0)
                max_val = range_config.get("max", 100)
                self.current_values[mode_id] = (min_val + max_val) / 2
            
            elif mode_type == "toggle":
                # toggle 類型：預設 False
                self.current_values[mode_id] = False
            
            elif mode_type == "group":
                # group 類型：預設第一個子模式
                group_modes = mode.get("group", [])
                if group_modes:
                    self.current_values[mode_id] = 0  # 子模式索引
                    # 遞歸初始化子模式
                    for i, sub_mode in enumerate(group_modes):
                        sub_mode_id = sub_mode.get("id")
                        if sub_mode_id:
                            self._init_mode_value(sub_mode)
    
    def _init_mode_value(self, mode: Dict[str, Any]):
        """初始化單個模式的預設值"""
        mode_id = mode.get("id")
        mode_type = mode.get("type")
        
        if mode_type == "enum":
            self.current_values[mode_id] = 0
        elif mode_type == "range":
            range_config = mode.get("range", {})
            min_val = range_config.get("min", 0)
            max_val = range_config.get("max", 100)
            self.current_values[mode_id] = (min_val + max_val) / 2
        elif mode_type == "toggle":
            self.current_values[mode_id] = False
    
    def get_current_mode(self) -> Optional[Dict[str, Any]]:
        """取得當前模式（如果是群組模式，返回當前活躍的子模式）"""
        if not self.dial_order or self.current_mode_index >= len(self.dial_order):
            return None
        
        mode_id = self.dial_order[self.current_mode_index]
        mode = self.config_loader.get_mode_by_id(mode_id)
        
        # 如果是群組模式，返回當前活躍的子模式
        if mode and mode.get("type") == "group":
            group_modes = mode.get("group", [])
            current_sub_index = self.current_values.get(mode_id, 0)
            if 0 <= current_sub_index < len(group_modes):
                return group_modes[current_sub_index]
        
        return mode
    
    def get_current_mode_id(self) -> str:
        """取得當前模式 ID（主模式的ID，不是子模式）"""
        if not self.dial_order or self.current_mode_index >= len(self.dial_order):
            return ""
        return self.dial_order[self.current_mode_index]
    
    def get_current_active_mode_id(self) -> str:
        """取得當前活躍模式的ID（如果是群組模式，返回子模式ID）"""
        current_mode = self.get_current_mode()
        if current_mode:
            return current_mode.get("id", "")
        return ""
    
    def rotate_left_dial(self, direction: int):
        """
        旋轉左轉盤（模式選擇）
        
        Args:
            direction: 1 為順時針，-1 為逆時針
        """
        if not self.dial_order:
            return
        
        old_index = self.current_mode_index
        self.current_mode_index = (self.current_mode_index + direction) % len(self.dial_order)
        
        if old_index != self.current_mode_index:
            self._trigger_mode_changed()
    
    def rotate_right_dial(self, direction: int):
        """
        旋轉右轉盤（數值調整）
        
        Args:
            direction: 1 為順時針，-1 為逆時針
        """
        # 獲取主模式ID用於群組索引
        main_mode_id = self.get_current_mode_id()
        if not main_mode_id:
            return
            
        # 獲取當前活躍的模式（可能是子模式）
        current_mode = self.get_current_mode()
        if not current_mode:
            return
        
        mode_id = current_mode.get("id")
        events = current_mode.get("events", {})
        rotate_action = events.get("rotate", "noop")
        
        if rotate_action == "noop":
            return
        
        # 檢查主模式是否為群組
        main_mode = self.config_loader.get_mode_by_id(main_mode_id)
        is_group_mode = main_mode and main_mode.get("type") == "group"
        
        if is_group_mode:
            # 群組模式：調整當前子模式的值，但群組索引儲存在主模式ID下
            old_value = self.current_values.get(mode_id)
            new_value = self._calculate_new_value(current_mode, direction, rotate_action)
            
            if new_value != old_value:
                self.current_values[mode_id] = new_value
                self._trigger_value_changed(mode_id, old_value, new_value)
                self._trigger_bindings(current_mode)
        else:
            # 一般模式：調整主模式的值
            old_value = self.current_values.get(mode_id)
            new_value = self._calculate_new_value(current_mode, direction, rotate_action)
            
            if new_value != old_value:
                self.current_values[mode_id] = new_value
                self._trigger_value_changed(mode_id, old_value, new_value)
                self._trigger_bindings(current_mode)
    
    def _calculate_new_value(self, mode: Dict[str, Any], direction: int, action: str) -> Any:
        """計算新值"""
        mode_id = mode.get("id")
        mode_type = mode.get("type")
        current_value = self.current_values.get(mode_id, 0)
        
        if mode_type == "enum":
            enum_options = mode.get("enum", [])
            if not enum_options:
                return current_value
            
            if action in ["next", "prev"]:
                delta = 1 if action == "next" else -1
                if direction < 0:  # 逆時針則反向
                    delta = -delta
                new_index = (current_value + delta) % len(enum_options)
                return new_index
        
        elif mode_type == "range":
            range_config = mode.get("range", {})
            min_val = range_config.get("min", 0)
            max_val = range_config.get("max", 100)
            step = range_config.get("step", 1)
            
            if action in ["inc", "dec"]:
                delta = step if action == "inc" else -step
                if direction < 0:  # 逆時針則反向
                    delta = -delta
                new_value = current_value + delta
                return max(min_val, min(max_val, new_value))
        
        elif mode_type == "group":
            # group 類型調整子模式索引
            group_modes = mode.get("group", [])
            if group_modes:
                delta = 1 if direction > 0 else -1
                new_index = (current_value + delta) % len(group_modes)
                return new_index
        
        elif mode_type == "toggle":
            # toggle 類型在旋轉時切換狀態
            if action in ["next", "prev", "toggle"]:
                return not current_value
        
        elif mode_type == "action":
            # action 類型旋轉時不改變值
            return current_value
        
        return current_value
    
    def press_right_dial(self, press_type: str = "press"):
        """
        按壓右轉盤
        
        Args:
            press_type: "press" 或 "longPress"
        """
        current_mode = self.get_current_mode()
        if not current_mode:
            return
        
        events = current_mode.get("events", {})
        action = events.get(press_type, "noop")
        
        if action == "noop":
            return
        
        self._handle_press_action(current_mode, action)
    
    def _handle_press_action(self, mode: Dict[str, Any], action: str):
        """處理按壓動作"""
        mode_id = mode.get("id")
        mode_type = mode.get("type")
        
        if action == "confirm":
            # 確認當前值，觸發綁定
            self._trigger_bindings(mode)
        
        elif action == "toggle" and mode_type == "toggle":
            # 切換開關
            current_value = self.current_values.get(mode_id, False)
            new_value = not current_value
            self.current_values[mode_id] = new_value
            self._trigger_value_changed(mode_id, current_value, new_value)
            self._trigger_bindings(mode)
        
        elif action == "enterSub" and mode_type == "group":
            # 進入子模式
            group_modes = mode.get("group", [])
            current_sub_index = self.current_values.get(mode_id, 0)
            if current_sub_index < len(group_modes):
                self.sub_mode_stack.append((mode_id, current_sub_index))
        
        elif action == "back":
            # 返回上級模式
            if self.sub_mode_stack:
                self.sub_mode_stack.pop()
        
        elif action == "enter":
            # 進入功能（如設定選單）
            self._trigger_bindings(mode)
    
    def _trigger_bindings(self, mode: Dict[str, Any]):
        """觸發綁定"""
        mode_id = mode.get("id")
        mode_type = mode.get("type")
        current_value = self.current_values.get(mode_id)
        
        bindings = None
        
        if mode_type == "enum":
            enum_options = mode.get("enum", [])
            if current_value < len(enum_options):
                bindings = enum_options[current_value].get("bindings", {})
        
        elif mode_type == "range":
            range_config = mode.get("range", {})
            bindings = range_config.get("bindings", {})
        
        elif mode_type == "toggle":
            toggle_config = mode.get("toggle", {})
            state_key = "on" if current_value else "off"
            state_config = toggle_config.get(state_key, {})
            bindings = state_config.get("bindings", {})
        
        if bindings and self.on_binding_triggered:
            self.on_binding_triggered(mode_id, bindings, current_value)
    
    def _trigger_mode_changed(self):
        """觸發模式變更事件"""
        if self.on_mode_changed:
            current_mode = self.get_current_mode()
            self.on_mode_changed(self.current_mode_index, current_mode)
    
    def _trigger_value_changed(self, mode_id: str, old_value: Any, new_value: Any):
        """觸發值變更事件"""
        if self.on_value_changed:
            self.on_value_changed(mode_id, old_value, new_value)
    
    def get_current_state(self) -> Dict[str, Any]:
        """取得完整的當前狀態"""
        current_mode = self.get_current_mode()
        current_mode_id = self.get_current_mode_id()
        
        state = {
            "version": "1.0.0",
            "current_mode_index": self.current_mode_index,
            "current_mode": current_mode,
            "current_mode_id": current_mode_id,
            "current_values": self.current_values.copy(),
            "sub_mode_stack": self.sub_mode_stack.copy(),
            "dial_order": self.dial_order.copy(),
            "total_modes": len(self.dial_order)
        }
        
        # 添加當前模式的詳細資訊
        if current_mode:
            current_value = self.current_values.get(current_mode_id)
            state["current_display_value"] = self._get_display_value(current_mode, current_value)
        
        return state
    
    def _get_display_value(self, mode: Dict[str, Any], value: Any) -> str:
        """取得顯示用的值"""
        mode_type = mode.get("type")
        
        if mode_type == "enum":
            enum_options = mode.get("enum", [])
            if isinstance(value, int) and 0 <= value < len(enum_options):
                return enum_options[value].get("label", str(value))
        
        elif mode_type == "range":
            range_config = mode.get("range", {})
            display_format = range_config.get("display", "{value}")
            unit = range_config.get("unit", "")
            try:
                if "{value" in display_format:
                    return display_format.format(value=value)
                else:
                    return f"{value}{unit}"
            except:
                return str(value)
        
        elif mode_type == "toggle":
            return "開" if value else "關"
        
        elif mode_type == "group":
            group_modes = mode.get("group", [])
            if isinstance(value, int) and 0 <= value < len(group_modes):
                return group_modes[value].get("label", str(value))
        
        elif mode_type == "action":
            return mode.get("label", "動作")
        
        return str(value)
    
    def reset_to_defaults(self):
        """重置所有值到預設"""
        self.current_mode_index = 0
        self.current_values.clear()
        self.sub_mode_stack.clear()
        self._init_default_values()
        self._trigger_mode_changed()
    
    def set_callbacks(self, on_mode_changed: Callable = None, 
                     on_value_changed: Callable = None,
                     on_binding_triggered: Callable = None):
        """設定回調函數"""
        if on_mode_changed:
            self.on_mode_changed = on_mode_changed
        if on_value_changed:
            self.on_value_changed = on_value_changed
        if on_binding_triggered:
            self.on_binding_triggered = on_binding_triggered