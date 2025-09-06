"""
模式轉盤邏輯
提供簡化的模式轉盤介面，封裝 ModeDial 類別的核心功能
"""

try:
    from .state_machine import ModeDial as _ModeDial
except ImportError:
    from state_machine import ModeDial as _ModeDial

# 重新匯出主要類別
ModeDial = _ModeDial

# 便利函數
def create_mode_dial(config_path=None):
    """
    建立模式轉盤實例
    
    Args:
        config_path: 配置檔案路徑，None 則使用預設配置
        
    Returns:
        ModeDial: 模式轉盤實例
    """
    return ModeDial(config_path)

def load_default_dial():
    """
    載入使用預設配置的模式轉盤
    
    Returns:
        ModeDial: 使用預設配置的模式轉盤實例
    """
    return ModeDial()

__all__ = ['ModeDial', 'create_mode_dial', 'load_default_dial']