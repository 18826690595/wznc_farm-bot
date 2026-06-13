"""
游戏操作 - 进入/退出游戏
"""
from loguru import logger
from core.action_base import ActionBase
from config.operation_definitions import OperationDefinitions


class GameOperations:
    """游戏相关操作"""
    
    def __init__(self, action: ActionBase):
        self.action = action
    
    def enter(self) -> bool:
        """进入游戏"""
        logger.info("进入游戏...")
        steps = OperationDefinitions.get_operation("enter_game")
        if steps:
            success = self._execute_steps(steps)
            if success:
                logger.success("已进入游戏")
            return success
        return False
    
    def exit(self) -> bool:
        """退出游戏"""
        logger.info("退出游戏...")
        self.action.back()
        return True
    
    def _execute_steps(self, steps) -> bool:
        """执行步骤"""
        for i, step in enumerate(steps):
            logger.info(f"步骤 {i+1}/{len(steps)}: {step.name}")
            
            action = step.action
            target = step.target
            
            if action == "click_template":
                success = self.action.click_template(target)
            elif action == "click_position":
                x, y = map(int, target.split(","))
                self.action.click_position(x, y)
                success = True
            elif action == "wait":
                self.action.wait(float(target))
                success = True
            elif action == "back":
                self.action.back()
                success = True
            else:
                success = False
            
            if not success and not step.optional:
                return False
            
            if step.delay > 0:
                self.action._delay(step.delay)
        
        return True
