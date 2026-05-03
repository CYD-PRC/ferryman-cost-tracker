"""
Ferryman Cost Tracker
AI 权限控制的成本追踪中间层，PRE-GHR 框架的工程参考实现。
"""

from .tracker import FerrymanTracker
from .router import gear_aware_call, MODEL_REGISTRY

__version__ = "0.1.0"
__all__ = ["FerrymanTracker", "gear_aware_call", "MODEL_REGISTRY"]
