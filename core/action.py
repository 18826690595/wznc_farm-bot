"""
操作执行器 - 封装所有农场操作动作
"""
import time
import random
from loguru import logger
from typing import Optional, Tuple
from .device import device_manager
from .vision import VisionEngine


class ActionExecutor:
    """
    操作执行器
    封装所有农场相关的高级操作
    """
    
    def __init__(self, vision: VisionEngine, random_delay: bool = True):
        """
        初始化执行器
        
        Args:
            vision: 视觉引擎
            random_delay: 是否启用随机延迟（防检测）
        """
        self.vision = vision
        self.random_delay = random_delay
        self.device = device_manager
    
    def _delay(self, base: float = 0.5, variance: float = 0.3):
        """
        执行延迟
        
        Args:
            base: 基础延迟时间
            variance: 随机变化范围
        """
        if self.random_delay:
            delay = base + random.uniform(-variance, variance)
            delay = max(0.1, delay)  # 最小0.1秒
        else:
            delay = base
        
        time.sleep(delay)
    
    def click_template(self, template_name: str, threshold: float = 0.8) -> bool:
        """
        点击模板图片
        
        Args:
            template_name: 模板名称
            threshold: 匹配阈值
            
        Returns:
            是否点击成功
        """
        screenshot = self.device.screenshot()
        rect = self.vision.find_template(screenshot, template_name, threshold)
        
        if rect:
            center = self.vision.get_center(rect)
            self.device.tap(*center)
            self._delay(0.5)
            return True
        
        return False
    
    def wait_and_click(
        self, 
        template_name: str, 
        timeout: float = 10.0,
        threshold: float = 0.8
    ) -> bool:
        """
        等待模板出现并点击
        
        Args:
            template_name: 模板名称
            timeout: 超时时间
            threshold: 匹配阈值
            
        Returns:
            是否点击成功
        """
        rect = self.vision.wait_for_template(
            self.device.screenshot,
            template_name,
            timeout,
            threshold=threshold
        )
        
        if rect:
            center = self.vision.get_center(rect)
            self.device.tap(*center)
            self._delay(0.5)
            return True
        
        return False
    
    def enter_farm(self) -> bool:
        """
        进入农场
        
        Returns:
            是否进入成功
        """
        logger.info("尝试进入农场...")
        
        # 查找农场图标
        if self.click_template("farm_icon"):
            logger.success("已进入农场")
            self._delay(1.0)  # 等待加载
            return True
        
        logger.warning("未找到农场入口")
        return False
    
    def exit_farm(self) -> bool:
        """
        退出农场
        
        Returns:
            是否退出成功
        """
        logger.info("退出农场...")
        self.device.back()
        self._delay(0.5)
        return True
    
    def harvest(self) -> int:
        """
        收获成熟作物
        
        Returns:
            收获数量
        """
        logger.info("开始收菜...")
        harvested = 0
        
        # 循环查找并点击收获按钮
        for _ in range(20):  # 最多20次
            screenshot = self.device.screenshot()
            
            # 查找收获按钮
            rects = self.vision.find_all_templates(screenshot, "harvest_btn")
            
            if not rects:
                break
            
            # 点击第一个收获按钮
            center = self.vision.get_center(rects[0])
            self.device.tap(*center)
            harvested += 1
            self._delay(0.8)
        
        logger.success(f"收菜完成，共收获 {harvested} 次")
        return harvested
    
    def plant(self, crop_name: Optional[str] = None) -> int:
        """
        种植作物
        
        Args:
            crop_name: 作物名称（可选）
            
        Returns:
            种植数量
        """
        logger.info(f"开始种菜: {crop_name or '默认作物'}...")
        planted = 0
        
        # 查找空地并种植
        for _ in range(20):
            screenshot = self.device.screenshot()
            
            # 查找种植按钮
            rect = self.vision.find_template(screenshot, "plant_btn")
            
            if not rect:
                break
            
            # 点击种植
            center = self.vision.get_center(rect)
            self.device.tap(*center)
            self._delay(0.5)
            
            # 如果指定了作物名，选择作物
            if crop_name:
                # 使用OCR查找作物名
                screenshot = self.device.screenshot()
                pos = self.vision.find_text(screenshot, crop_name)
                if pos:
                    self.device.tap(*pos)
                    self._delay(0.3)
            
            # 确认种植
            if self.click_template("confirm_btn"):
                planted += 1
                self._delay(0.8)
        
        logger.success(f"种菜完成，共种植 {planted} 次")
        return planted
    
    def steal_from_friends(self, max_count: int = 10) -> int:
        """
        偷好友的菜
        
        Args:
            max_count: 最大偷菜次数
            
        Returns:
            偷菜数量
        """
        logger.info("开始偷菜...")
        stolen = 0
        
        # 进入好友列表
        if not self.click_template("friend_list_btn"):
            logger.warning("无法打开好友列表")
            return 0
        
        self._delay(1.0)
        
        # 遍历好友
        for i in range(max_count):
            screenshot = self.device.screenshot()
            
            # 查找偷菜按钮
            rect = self.vision.find_template(screenshot, "steal_btn")
            
            if rect:
                center = self.vision.get_center(rect)
                self.device.tap(*center)
                stolen += 1
                self._delay(1.0)
                
                # 返回好友列表
                self.device.back()
                self._delay(0.5)
            else:
                # 向下滑动查找更多好友
                self.device.swipe_down(300)
                self._delay(0.3)
        
        # 返回农场
        self.device.back()
        self._delay(0.5)
        
        logger.success(f"偷菜完成，共偷了 {stolen} 次")
        return stolen
    
    def bless_friends(self, max_count: int = 10) -> int:
        """
        为好友祝福
        
        Args:
            max_count: 最大祝福次数
            
        Returns:
            祝福数量
        """
        logger.info("开始祝福...")
        blessed = 0
        
        # 进入好友列表
        if not self.click_template("friend_list_btn"):
            logger.warning("无法打开好友列表")
            return 0
        
        self._delay(1.0)
        
        for i in range(max_count):
            screenshot = self.device.screenshot()
            
            # 查找祝福按钮
            rect = self.vision.find_template(screenshot, "bless_btn")
            
            if rect:
                center = self.vision.get_center(rect)
                self.device.tap(*center)
                blessed += 1
                self._delay(0.8)
            else:
                # 向下滑动
                self.device.swipe_down(300)
                self._delay(0.3)
        
        # 返回
        self.device.back()
        self._delay(0.5)
        
        logger.success(f"祝福完成，共祝福 {blessed} 次")
        return blessed
    
    def scroll_to_top(self):
        """滚动到顶部"""
        for _ in range(3):
            self.device.swipe_up(500)
            self._delay(0.3)
    
    def scroll_to_bottom(self):
        """滚动到底部"""
        for _ in range(3):
            self.device.swipe_down(500)
            self._delay(0.3)
