"""
祝福管理器 - 为好友送上祝福
"""
from loguru import logger
from typing import List, Dict
from core.device import device_manager
from core.vision import VisionEngine
from core.action import ActionExecutor
from core.state_machine import StateMachine, FarmState


class BlessingManager:
    """
    祝福管理器
    管理好友祝福功能
    """
    
    def __init__(
        self,
        vision: VisionEngine,
        action: ActionExecutor,
        state_machine: StateMachine
    ):
        """
        初始化祝福管理器
        
        Args:
            vision: 视觉引擎
            action: 操作执行器
            state_machine: 状态机
        """
        self.vision = vision
        self.action = action
        self.state_machine = state_machine
        self.device = device_manager
        
        # 统计
        self.stats = {
            'total_blessed': 0,
            'blessed_friends': []
        }
        
        logger.info("祝福管理器已初始化")
    
    def bless_all_friends(self, max_count: int = 20) -> int:
        """
        为所有好友祝福
        
        Args:
            max_count: 最大祝福次数
            
        Returns:
            祝福数量
        """
        logger.info("开始为好友祝福...")
        
        if not self.state_machine.transition_to(FarmState.BLESSING):
            logger.warning("无法进入祝福状态")
            return 0
        
        try:
            count = self.action.bless_friends(max_count)
            self.stats['total_blessed'] += count
            self.state_machine.transition_to(FarmState.IDLE)
            logger.success(f"祝福完成，共 {count} 次")
            return count
            
        except Exception as e:
            logger.error(f"祝福失败: {e}")
            self.state_machine.transition_to(FarmState.ERROR, str(e))
            return 0
    
    def bless_specific_friends(self, friend_names: List[str]) -> Dict[str, bool]:
        """
        为指定好友祝福
        
        Args:
            friend_names: 好友名称列表
            
        Returns:
            祝福结果 {好友名: 是否成功}
        """
        logger.info(f"为指定好友祝福: {friend_names}")
        
        results = {}
        
        # 进入好友列表
        if not self.action.click_template("friend_list_btn"):
            logger.warning("无法打开好友列表")
            return {name: False for name in friend_names}
        
        for friend_name in friend_names:
            try:
                # 使用OCR查找好友
                screenshot = self.device.screenshot()
                pos = self.vision.find_text(screenshot, friend_name)
                
                if pos:
                    # 点击好友
                    self.device.tap(*pos)
                    
                    # 点击祝福按钮
                    import time
                    time.sleep(0.5)
                    success = self.action.click_template("bless_btn")
                    
                    results[friend_name] = success
                    
                    if success:
                        self.stats['total_blessed'] += 1
                        self.stats['blessed_friends'].append(friend_name)
                    
                    # 返回好友列表
                    self.device.back()
                    time.sleep(0.3)
                else:
                    results[friend_name] = False
                    logger.warning(f"未找到好友: {friend_name}")
                    
            except Exception as e:
                logger.error(f"祝福 {friend_name} 失败: {e}")
                results[friend_name] = False
        
        # 返回农场
        self.device.back()
        
        return results
    
    def get_bless_status(self) -> dict:
        """
        获取祝福状态
        
        Returns:
            状态信息
        """
        return {
            'total_blessed': self.stats['total_blessed'],
            'recent_friends': self.stats['blessed_friends'][-10:]  # 最近10个
        }
    
    def reset_stats(self):
        """重置统计"""
        self.stats = {
            'total_blessed': 0,
            'blessed_friends': []
        }
        logger.info("祝福统计已重置")
