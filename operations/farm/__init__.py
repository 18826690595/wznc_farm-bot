"""
农场操作 - 收菜/种菜/偷菜
"""
from loguru import logger
from core.action_base import ActionBase
from config.operation_definitions import OperationDefinitions


class FarmOperations:
    """农场相关操作"""
    
    def __init__(self, action: ActionBase):
        self.action = action
    
    def enter(self) -> bool:
        """进入农场"""
        logger.info("进入农场...")
        steps = OperationDefinitions.get_operation("enter_farm")
        if steps:
            success = self._execute_steps(steps)
            if success:
                logger.success("已进入农场")
            return success
        return False
    
    def exit(self) -> bool:
        """退出农场"""
        logger.info("退出农场...")
        self.action.back()
        return True
    
    def harvest(self) -> int:
        """收菜"""
        logger.info("开始收菜...")
        count = 0
        
        for _ in range(20):  # 最多20次
            positions = self.action.find_all("harvest_btn")
            if not positions:
                break
            
            self.action.click_found()
            count += 1
        
        logger.success(f"收菜完成: {count}")
        return count
    
    def plant(self, crop_name: str = None) -> int:
        """种菜"""
        logger.info(f"开始种菜: {crop_name or '默认'}...")
        count = 0
        
        for _ in range(20):
            positions = self.action.find_all("plant_btn")
            if not positions:
                break
            
            self.action.click_found()
            count += 1
        
        logger.success(f"种菜完成: {count}")
        return count
    
    def steal(self, max_count: int = 10) -> int:
        """偷菜"""
        logger.info("开始偷菜...")
        count = 0
        
        # 打开好友列表
        if not self.action.click_template("friend_list_btn"):
            return 0
        
        self.action.wait(1.0)
        
        for _ in range(max_count):
            if self.action.click_template("steal_btn"):
                count += 1
                self.action.back()
                self.action.wait(0.5)
            else:
                self.action.swipe("down")
        
        self.action.back()
        logger.success(f"偷菜完成: {count}")
        return count
    
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
            else:
                success = False
            
            if not success and not step.optional:
                return False
            
            if step.delay > 0:
                self.action._delay(step.delay)
        
        return True
