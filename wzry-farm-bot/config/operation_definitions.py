"""
操作定义 - 在这里定义所有农场操作的详细步骤

TODO: 根据实际游戏界面，填充每个操作的具体步骤
"""

from loguru import logger
from typing import List, Tuple, Optional, Callable
from dataclasses import dataclass
import time
import random


@dataclass
class OperationStep:
    """操作步骤"""
    name: str                    # 步骤名称
    action: str                  # 动作类型: click/swipe/wait/check
    target: str                  # 目标（模板名或坐标）
    timeout: float = 10.0        # 超时时间
    delay: float = 0.5           # 执行后延迟
    optional: bool = False       # 是否可选（失败不中断）
    description: str = ""        # 描述


class OperationDefinitions:
    """
    操作定义类 - 定义所有农场操作的步骤流程
    
    TODO: 根据你的游戏界面，修改以下操作步骤
    """
    
    # ========== 操作流程定义 ==========
    
    # ----- 进入游戏 -----（新增）
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
            description="等待游戏加载"
        ),
        # TODO: 如果需要等待特定界面出现，可以添加：
        # OperationStep(
        #     name="等待主界面",
        #     action="click_template",
        #     target="game_loading",
        #     timeout=30.0,
        #     description="等待游戏加载完成"
        # ),
    ]
    
    # ----- 进入农场 -----
    ENTER_FARM: List[OperationStep] = [
        # TODO: 根据你的游戏界面修改
        OperationStep(
            name="查找农场入口",
            action="click_template",
            target="farm_icon",
            timeout=5.0,
            description="在主界面点击农场图标"
        ),
        OperationStep(
            name="等待农场加载",
            action="wait",
            target="1.0",  # 等待秒数
            description="等待农场界面加载"
        ),
        # TODO: 如果有其他步骤，在这里添加...
    ]
    
    # ----- 收菜流程 -----
    HARVEST: List[OperationStep] = [
        # TODO: 根据你的游戏界面修改
        OperationStep(
            name="查找成熟作物",
            action="find_all",
            target="harvest_btn",
            description="查找所有成熟作物"
        ),
        OperationStep(
            name="点击收获",
            action="click_found",
            target="harvest_btn",
            delay=0.8,
            description="点击收获按钮"
        ),
        # TODO: 如果需要确认，添加：
        # OperationStep(
        #     name="确认收获",
        #     action="click_template",
        #     target="harvest_confirm",
        #     optional=True,  # 可选，没有确认按钮也能继续
        # ),
    ]
    
    # ----- 种菜流程 -----
    PLANT: List[OperationStep] = [
        # TODO: 根据你的游戏界面修改
        OperationStep(
            name="查找空地",
            action="find_all",
            target="plant_btn",
            description="查找所有空地"
        ),
        OperationStep(
            name="点击种植",
            action="click_found",
            target="plant_btn",
            delay=0.5,
            description="点击种植按钮"
        ),
        # TODO: 添加作物选择步骤
        # OperationStep(
        #     name="选择作物",
        #     action="click_template",
        #     target="crop_wheat",  # 或其他作物
        #     description="选择要种植的作物"
        # ),
        OperationStep(
            name="确认种植",
            action="click_template",
            target="plant_confirm",
            optional=True,
            description="确认种植"
        ),
    ]
    
    # ----- 偷菜流程 -----
    STEAL: List[OperationStep] = [
        # TODO: 根据你的游戏界面修改
        OperationStep(
            name="打开好友列表",
            action="click_template",
            target="friend_list_btn",
            description="打开好友列表"
        ),
        OperationStep(
            name="等待列表加载",
            action="wait",
            target="1.0",
            description="等待好友列表加载"
        ),
        OperationStep(
            name="查找可偷作物",
            action="find_all",
            target="steal_btn",
            description="查找可偷取的作物"
        ),
        OperationStep(
            name="点击偷菜",
            action="click_found",
            target="steal_btn",
            delay=1.0,
            description="点击偷菜按钮"
        ),
        # TODO: 添加确认步骤...
    ]
    
    # ----- 祝福流程 -----
    BLESS: List[OperationStep] = [
        # TODO: 根据你的游戏界面修改
        OperationStep(
            name="打开好友列表",
            action="click_template",
            target="friend_list_btn",
            description="打开好友列表"
        ),
        OperationStep(
            name="等待列表加载",
            action="wait",
            target="1.0",
            description="等待好友列表加载"
        ),
        OperationStep(
            name="查找祝福按钮",
            action="find_all",
            target="bless_btn",
            description="查找可祝福的好友"
        ),
        OperationStep(
            name="点击祝福",
            action="click_found",
            target="bless_btn",
            delay=0.8,
            description="点击祝福按钮"
        ),
    ]
    
    # ----- 退出农场 -----
    EXIT_FARM: List[OperationStep] = [
        OperationStep(
            name="返回",
            action="back",
            target="",
            description="按返回键退出农场"
        ),
    ]
    
    # ----- 滚动查找更多 -----
    SCROLL_DOWN: List[OperationStep] = [
        OperationStep(
            name="向下滑动",
            action="swipe",
            target="down",  # down/up/left/right
            description="向下滑动查找更多"
        ),
    ]
    
    # TODO: 添加更多操作流程...
    # 例如：浇水、除草、施肥等
    
    @classmethod
    def get_operation(cls, name: str) -> Optional[List[OperationStep]]:
        """获取操作流程"""
        operations = {
            "enter_game": cls.ENTER_GAME,    # 新增
            "enter_farm": cls.ENTER_FARM,
            "harvest": cls.HARVEST,
            "plant": cls.PLANT,
            "steal": cls.STEAL,
            "bless": cls.BLESS,
            "exit_farm": cls.EXIT_FARM,
            "scroll_down": cls.SCROLL_DOWN,
        }
        return operations.get(name)
    
    @classmethod
    def print_operations(cls):
        """打印所有操作定义"""
        print("\n" + "=" * 60)
        print("操作流程定义")
        print("=" * 60)
        
        operations = [
            ("ENTER_GAME", cls.ENTER_GAME),  # 新增
            ("ENTER_FARM", cls.ENTER_FARM),
            ("HARVEST", cls.HARVEST),
            ("PLANT", cls.PLANT),
            ("STEAL", cls.STEAL),
            ("BLESS", cls.BLESS),
            ("EXIT_FARM", cls.EXIT_FARM),
        ]
        
        for name, steps in operations:
            print(f"\n{name}:")
            for i, step in enumerate(steps, 1):
                print(f"  {i}. {step.name}: {step.action} -> {step.target}")
                if step.description:
                    print(f"     ({step.description})")
        
        print("\n" + "=" * 60)


if __name__ == "__main__":
    OperationDefinitions.print_operations()
