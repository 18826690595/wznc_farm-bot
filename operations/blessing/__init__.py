"""
祝福操作 - 为好友祝福
"""
from loguru import logger
from core.action_base import ActionBase


class BlessingOperations:
    """祝福相关操作"""
    
    def __init__(self, action: ActionBase):
        self.action = action
    
    def bless(self, max_count: int = 20) -> int:
        """祝福"""
        logger.info("开始祝福...")
        count = 0
        
        # 打开好友列表
        if not self.action.click_template("friend_list_btn"):
            return 0
        
        self.action.wait(1.0)
        
        for _ in range(max_count):
            if self.action.click_template("bless_btn"):
                count += 1
                self.action.wait(0.5)
            else:
                self.action.swipe("down")
        
        self.action.back()
        logger.success(f"祝福完成: {count}")
        return count
