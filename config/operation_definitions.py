"""
操作流程定义
定义每个操作的具体步骤
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class OperationStep:
    """操作步骤"""
    name: str                          # 步骤名称
    action: str                        # 动作类型
    target: str                        # 目标
    timeout: float = 10.0              # 超时时间
    delay: float = 0.5                 # 延迟时间
    optional: bool = False             # 是否可选（失败是否继续）
    description: str = ""              # 描述说明


class OperationDefinitions:
    """操作流程定义"""
    
    # ========== 进入游戏 ==========
    ENTER_GAME: List[OperationStep] = [
        OperationStep(
            name="点击启动游戏",
            action="click_template",
            target="game_start_btn",
            timeout=10.0,
            description="点击游戏启动按钮"
        ),
        OperationStep(
            name="等待游戏加载",
            action="wait",
            target="5.0",
            description="等待游戏加载完成"
        ),
    ]
    
    # ========== 进入农场 ==========
    ENTER_FARM: List[OperationStep] = [
        OperationStep(
            name="点击农场图标",
            action="click_template",
            target="farm_icon",
            timeout=10.0,
            description="点击农场入口"
        ),
        OperationStep(
            name="等待进入农场",
            action="wait",
            target="2.0",
        ),
    ]
    
    # ========== 收菜 ==========
    HARVEST: List[OperationStep] = [
        OperationStep(
            name="扫描成熟作物",
            action="find_all",
            target="harvest_btn",
            timeout=5.0,
        ),
        OperationStep(
            name="依次点击收获",
            action="click_found",
            target="harvest_btn",
        ),
    ]
    
    # ========== 种菜 ==========
    PLANT: List[OperationStep] = [
        OperationStep(
            name="查找空地块",
            action="find_all",
            target="empty_plot",
            timeout=5.0,
        ),
        OperationStep(
            name="点击空地块",
            action="click_found",
            target="empty_plot",
        ),
        OperationStep(
            name="点击种植按钮",
            action="click_template",
            target="plant_btn",
            optional=True,
        ),
    ]
    
    # ========== 好友偷菜 ==========
    STEAL: List[OperationStep] = [
        OperationStep(
            name="打开好友列表",
            action="click_template",
            target="friend_list_btn",
        ),
        OperationStep(
            name="等待好友列表",
            action="wait",
            target="1.0",
        ),
        OperationStep(
            name="查找可偷菜好友",
            action="find_all",
            target="steal_btn",
        ),
        OperationStep(
            name="点击偷菜",
            action="click_found",
            target="steal_btn",
        ),
        OperationStep(
            name="关闭好友列表",
            action="back",
            target="",
        ),
    ]
    
    # ========== 祝福好友 ==========
    BLESS: List[OperationStep] = [
        OperationStep(
            name="打开好友列表",
            action="click_template",
            target="friend_list_btn",
        ),
        OperationStep(
            name="等待好友列表",
            action="wait",
            target="1.0",
        ),
        OperationStep(
            name="查找祝福按钮",
            action="find_all",
            target="bless_btn",
        ),
        OperationStep(
            name="点击祝福",
            action="click_found",
            target="bless_btn",
        ),
        OperationStep(
            name="关闭好友列表",
            action="back",
            target="",
        ),
    ]
    
    # ========== 退出农场 ==========
    EXIT_FARM: List[OperationStep] = [
        OperationStep(
            name="返回",
            action="back",
            target="",
        ),
        OperationStep(
            name="等待退出",
            action="wait",
            target="1.0",
        ),
    ]
    
    # ========== 操作映射 ==========
    @classmethod
    def get_operation(cls, name: str) -> Optional[List[OperationStep]]:
        """获取操作流程
        
        Args:
            name: 操作名称
        
        Returns:
            操作步骤列表
        """
        operations = {
            "enter_game": cls.ENTER_GAME,
            "enter_farm": cls.ENTER_FARM,
            "harvest": cls.HARVEST,
            "plant": cls.PLANT,
            "steal": cls.STEAL,
            "bless": cls.BLESS,
            "exit_farm": cls.EXIT_FARM,
        }
        return operations.get(name)
    
    @classmethod
    def add_operation(cls, name: str, steps: List[OperationStep]):
        """添加新操作"""
        setattr(cls, name.upper(), steps)
    
    @classmethod
    def list_operations(cls) -> List[str]:
        """列出所有操作"""
        return [
            "enter_game",
            "enter_farm",
            "harvest",
            "plant",
            "steal",
            "bless",
            "exit_farm",
        ]


# 支持的动作类型说明
ACTION_TYPES = {
    "click_template": "点击模板图片",
    "click_position": "点击坐标 (格式: x,y 或 0.5,0.5)",
    "click_region": "点击区域中心",
    "long_press": "长按 (格式: x,y,duration 或 模板名)",
    "swipe": "滑动 (方向: up/down/left/right 或坐标)",
    "wait": "等待 (秒数)",
    "back": "返回键",
    "home": "Home键",
    "find_all": "查找所有匹配",
    "click_found": "点击找到的",
    "exists": "判断是否存在",
    "wait_for": "等待出现",
}