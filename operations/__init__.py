"""
操作模块

按功能拆分，方便维护：
- game/      游戏操作（进入游戏、退出游戏）
- farm/      农场操作（收菜、种菜、偷菜）
- blessing/  祝福操作
"""

from operations.game import GameOperations
from operations.farm import FarmOperations
from operations.blessing import BlessingOperations

__all__ = ['GameOperations', 'FarmOperations', 'BlessingOperations']
