"""
SystemControl - 系統控制與設定模組
統一管理相機系統的各項設定，包括雙轉盤配置
"""

__version__ = "1.0.0"
__author__ = "Camera Project Team"

from .core.system_manager import SystemManager

__all__ = ['SystemManager']