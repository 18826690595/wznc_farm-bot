"""
农场管理器 - 整合收菜、种菜、偷菜功能
"""
from loguru import logger
from typing import Optional
from core.device import device_manager
from core.vision import VisionEngine
from core.action import ActionExecutor
from core.state_machine import StateMachine, FarmState


class FarmManager:
    """
    农场管理器
    整合所有农场操作，提供统一的操作接口
    """
    
    def __init__(
        self, 
        vision: VisionEngine,
        action: ActionExecutor,
        state_machine: StateMachine
    ):
        """
        初始化农场管理器
        
        Args:
            vision: 视觉引擎
            action: 操作执行器
            state_machine: 状态机
        """
        self.vision = vision
        self.action = action
        self.state_machine = state_machine
        self.device = device_manager
        
        # 统计数据
        self.stats = {
            'total_harvested': 0,
            'total_planted': 0,
            'total_stolen': 0,
            'last_harvest_time': None,
            'last_plant_time': None,
            'last_steal_time': None,
        }
        
        logger.info("农场管理器已初始化")
    
    def run_full_cycle(
        self, 
        crop_name: Optional[str] = None,
        do_steal: bool = True,
        max_steal: int = 10
    ) -> dict:
        """
        执行完整农场循环：收菜 -> 种菜 -> 偷菜
        
        Args:
            crop_name: 要种植的作物
            do_steal: 是否偷菜
            max_steal: 最大偷菜次数
            
        Returns:
            操作结果统计
        """
        logger.info("开始执行农场完整循环...")
        
        results = {
            'harvested': 0,
            'planted': 0,
            'stolen': 0,
            'success': False
        }
        
        try:
            # 1. 收菜
            if self.state_machine.transition_to(FarmState.HARVESTING):
                results['harvested'] = self.action.harvest()
                self.stats['total_harvested'] += results['harvested']
                self.state_machine.transition_to(FarmState.IDLE)
            
            # 2. 种菜
            if self.state_machine.transition_to(FarmState.PLANTING):
                results['planted'] = self.action.plant(crop_name)
                self.stats['total_planted'] += results['planted']
                self.state_machine.transition_to(FarmState.IDLE)
            
            # 3. 偷菜
            if do_steal and self.state_machine.transition_to(FarmState.STEALING):
                results['stolen'] = self.action.steal_from_friends(max_steal)
                self.stats['total_stolen'] += results['stolen']
                self.state_machine.transition_to(FarmState.IDLE)
            
            results['success'] = True
            logger.success("农场循环完成")
            
        except Exception as e:
            logger.error(f"农场循环失败: {e}")
            self.state_machine.transition_to(FarmState.ERROR, str(e))
            results['success'] = False
        
        return results
    
    def harvest_only(self) -> int:
        """
        仅执行收菜
        
        Returns:
            收获数量
        """
        logger.info("执行单独收菜...")
        
        if not self.state_machine.transition_to(FarmState.HARVESTING):
            return 0
        
        try:
            count = self.action.harvest()
            self.stats['total_harvested'] += count
            self.state_machine.transition_to(FarmState.IDLE)
            return count
        except Exception as e:
            logger.error(f"收菜失败: {e}")
            self.state_machine.transition_to(FarmState.ERROR, str(e))
            return 0
    
    def plant_only(self, crop_name: Optional[str] = None) -> int:
        """
        仅执行种菜
        
        Args:
            crop_name: 作物名称
            
        Returns:
            种植数量
        """
        logger.info("执行单独种菜...")
        
        if not self.state_machine.transition_to(FarmState.PLANTING):
            return 0
        
        try:
            count = self.action.plant(crop_name)
            self.stats['total_planted'] += count
            self.state_machine.transition_to(FarmState.IDLE)
            return count
        except Exception as e:
            logger.error(f"种菜失败: {e}")
            self.state_machine.transition_to(FarmState.ERROR, str(e))
            return 0
    
    def steal_only(self, max_count: int = 10) -> int:
        """
        仅执行偷菜
        
        Args:
            max_count: 最大次数
            
        Returns:
            偷菜数量
        """
        logger.info("执行单独偷菜...")
        
        if not self.state_machine.transition_to(FarmState.STEALING):
            return 0
        
        try:
            count = self.action.steal_from_friends(max_count)
            self.stats['total_stolen'] += count
            self.state_machine.transition_to(FarmState.IDLE)
            return count
        except Exception as e:
            logger.error(f"偷菜失败: {e}")
            self.state_machine.transition_to(FarmState.ERROR, str(e))
            return 0
    
    def get_stats(self) -> dict:
        """
        获取统计数据
        
        Returns:
            统计信息字典
        """
        return self.stats.copy()
    
    def reset_stats(self):
        """重置统计数据"""
        self.stats = {
            'total_harvested': 0,
            'total_planted': 0,
            'total_stolen': 0,
            'last_harvest_time': None,
            'last_plant_time': None,
            'last_steal_time': None,
        }
        logger.info("统计数据已重置")
    
    def check_crop_status(self) -> dict:
        """
        检查作物状态
        
        Returns:
            状态信息
        """
        logger.info("检查作物状态...")
        
        screenshot = self.device.screenshot()
        
        # 统计成熟和未成熟的作物
        mature_count = len(
            self.vision.find_all_templates(screenshot, "harvest_btn")
        )
        empty_count = len(
            self.vision.find_all_templates(screenshot, "plant_btn")
        )
        
        status = {
            'mature_crops': mature_count,
            'empty_slots': empty_count,
            'total_slots': mature_count + empty_count
        }
        
        logger.info(f"作物状态: 成熟{mature_count}, 空地{empty_count}")
        return status
