"""
操作执行器 V2 - 基于操作定义执行流程

TODO: 填充具体的操作逻辑
"""
import time
import random
from loguru import logger
from typing import Optional, List, Tuple
from core.device import device_manager
from core.vision import VisionEngine
from config.template_config import template_config, TemplateInfo
from config.operation_definitions import OperationDefinitions, OperationStep


class ActionExecutorV2:
    """
    操作执行器 V2
    
    基于操作定义执行流程，支持：
    - 模板点击
    - 坐标点击
    - 滑动操作
    - 等待
    - 条件检查
    """
    
    def __init__(self, vision: VisionEngine, random_delay: bool = True):
        self.vision = vision
        self.random_delay = random_delay
        self.device = device_manager
        
        # 执行结果缓存
        self._found_positions: List[Tuple[int, int]] = []
        
        logger.info("操作执行器 V2 已初始化")
    
    def _delay(self, base: float = 0.5, variance: float = 0.3):
        """随机延迟"""
        if self.random_delay:
            delay = base + random.uniform(-variance, variance)
            delay = max(0.1, delay)
        else:
            delay = base
        time.sleep(delay)
    
    # ========== 基础操作 ==========
    
    def click_template(self, template_name: str, threshold: Optional[float] = None) -> bool:
        """
        点击模板
        
        Args:
            template_name: 模板名称
            threshold: 匹配阈值
            
        Returns:
            是否成功
        """
        # 获取模板配置
        info = template_config.get_info(template_name)
        img = template_config.get(template_name)
        
        if img is None:
            logger.warning(f"模板不存在: {template_name}")
            return False
        
        threshold = threshold or (info.threshold if info else 0.8)
        
        # 截图并匹配
        screenshot = self.device.screenshot()
        rect = self.vision.find_template(screenshot, template_name, threshold)
        
        if rect:
            center = self.vision.get_center(rect)
            self.device.tap(*center)
            self._delay(0.5)
            return True
        
        return False
    
    def click_position(self, x: int, y: int):
        """点击坐标"""
        self.device.tap(x, y)
        self._delay(0.3)
    
    def click_ratio(self, ratio_x: float, ratio_y: float):
        """
        按比例点击（适配不同分辨率）
        
        Args:
            ratio_x: X 比例 (0.0~1.0)，0.5 = 屏幕水平中间
            ratio_y: Y 比例 (0.0~1.0)，0.5 = 屏幕垂直中间
        """
        self.device.tap_ratio(ratio_x, ratio_y)
        self._delay(0.3)
    
    def long_press(self, x: int, y: int, duration: float = 1.0):
        """
        长按坐标
        
        Args:
            x: X坐标
            y: Y坐标
            duration: 长按时长
        """
        self.device.long_press(x, y, duration)
        self._delay(0.3)
    
    def swipe(self, direction: str, distance: int = 300):
        """
        滑动
        
        Args:
            direction: 方向 up/down/left/right
            distance: 距离
        """
        width, height = self.device.screen_size
        center_x = width // 2
        center_y = height // 2
        
        if direction == "up":
            self.device.swipe((center_x, center_y), (center_x, center_y - distance))
        elif direction == "down":
            self.device.swipe((center_x, center_y), (center_x, center_y + distance))
        elif direction == "left":
            self.device.swipe((center_x, center_y), (center_x - distance, center_y))
        elif direction == "right":
            self.device.swipe((center_x, center_y), (center_x + distance, center_y))
        
        self._delay(0.3)
    
    def wait(self, seconds: float):
        """等待"""
        time.sleep(seconds)
    
    def back(self):
        """返回键"""
        self.device.back()
        self._delay(0.3)
    
    # ========== 查找操作 ==========
    
    def find_all(self, template_name: str) -> List[Tuple[int, int]]:
        """
        查找所有匹配位置
        
        Returns:
            中心点坐标列表
        """
        info = template_config.get_info(template_name)
        img = template_config.get(template_name)
        
        if img is None:
            return []
        
        screenshot = self.device.screenshot()
        threshold = info.threshold if info else 0.8
        
        rects = self.vision.find_all_templates(screenshot, template_name, threshold)
        positions = [self.vision.get_center(r) for r in rects]
        
        # 缓存结果
        self._found_positions = positions
        
        logger.debug(f"找到 {len(positions)} 个 '{template_name}'")
        return positions
    
    def click_found(self, index: int = 0) -> bool:
        """
        点击已找到的位置
        
        Args:
            index: 索引（0=第一个）
            
        Returns:
            是否成功
        """
        if index >= len(self._found_positions):
            return False
        
        x, y = self._found_positions[index]
        self.device.tap(x, y)
        self._delay(0.5)
        return True
    
    # ========== 流程执行 ==========
    
    def execute_steps(self, steps: List[OperationStep]) -> Tuple[bool, str]:
        """
        执行操作流程
        
        Args:
            steps: 操作步骤列表
            
        Returns:
            (是否成功, 错误信息)
        """
        for i, step in enumerate(steps):
            logger.info(f"执行步骤 {i+1}/{len(steps)}: {step.name}")
            
            try:
                success = self._execute_step(step)
                
                if not success and not step.optional:
                    return False, f"步骤 '{step.name}' 失败"
                
                # 步骤后延迟
                if step.delay > 0:
                    self._delay(step.delay)
                    
            except Exception as e:
                if not step.optional:
                    return False, f"步骤 '{step.name}' 异常: {e}"
                logger.warning(f"可选步骤 '{step.name}' 失败: {e}")
        
        return True, ""
    
    def _execute_step(self, step: OperationStep) -> bool:
        """执行单个步骤"""
        action = step.action
        target = step.target

        # 解析扩展参数
        params = self._parse_step_params(step)

        if action == "click_template":
            # 支持区域限定
            region = self.action_base.parse_region(params.get("region", ""))
            return self.click_template(
                target,
                region=region,
                threshold=params.get("threshold")
            )

        elif action == "click_position":
            # 支持比例和百分比
            self.click_position(coord=target)
            return True

        elif action == "click_ratio":
            # 比例点击：target="0.5,0.5" 表示屏幕中央
            coords = self.action_base.parse_coords(target)
            if coords and len(coords) == 2:
                self.click_ratio(ratio_x=coords[0], ratio_y=coords[1])
            return True

        elif action == "click_region":
            # 点击区域中心
            region = self.action_base.parse_region(target)
            if region:
                self.action_base.click_region(region)
            return True

        elif action == "long_press":
            # 格式: "x,y,duration" 或 比例格式
            self.long_press(coord=target)
            return True

        elif action == "swipe":
            self.swipe(target)
            return True

        elif action == "wait":
            self.wait(float(target))
            return True

        elif action == "back":
            self.back()
            return True

        elif action == "find_all":
            region = self.action_base.parse_region(params.get("region", ""))
            positions = self.find_all(target, region=region)
            return len(positions) > 0

        elif action == "click_found":
            return self.click_found()

        elif action == "exists":
            # 判断元素是否存在（不点击）
            region = self.action_base.parse_region(params.get("region", ""))
            return self.action_base.exists(target, region=region)

        elif action == "wait_for":
            # 等待元素出现
            region = self.action_base.parse_region(params.get("region", ""))
            timeout = float(params.get("timeout", "10"))
            return self.action_base.wait_for(target, timeout=timeout, region=region)

        else:
            logger.warning(f"未知动作: {action}")
            return False

    def _parse_step_params(self, step: OperationStep) -> dict:
        """解析步骤的扩展参数"""
        params = {}
        if step.description and "|" in step.description:
            # 支持在description中写参数: "点击按钮|region:100,200,500,800"
            for part in step.description.split("|"):
                if ":" in part:
                    k, v = part.split(":", 1)
                    params[k.strip()] = v.strip()
        return params
    
    # ========== 高级操作（封装常用流程）==========
    
    def enter_game(self) -> bool:
        """进入游戏"""
        logger.info("进入游戏...")
        steps = OperationDefinitions.get_operation("enter_game")
        if steps:
            success, msg = self.execute_steps(steps)
            if success:
                logger.success("已进入游戏")
            else:
                logger.error(f"进入游戏失败: {msg}")
            return success
        return False
    
    def enter_farm(self) -> bool:
        """进入农场"""
        logger.info("进入农场...")
        steps = OperationDefinitions.get_operation("enter_farm")
        if steps:
            success, msg = self.execute_steps(steps)
            if success:
                logger.success("已进入农场")
            return success
        return False
    
    def exit_farm(self) -> bool:
        """退出农场"""
        logger.info("退出农场...")
        steps = OperationDefinitions.get_operation("exit_farm")
        if steps:
            success, _ = self.execute_steps(steps)
            return success
        return False
    
    def harvest(self) -> int:
        """
        收菜
        
        Returns:
            收获数量
        """
        logger.info("开始收菜...")
        harvested = 0
        
        steps = OperationDefinitions.get_operation("harvest")
        if not steps:
            return 0
        
        # 循环收菜（最多20次）
        for _ in range(20):
            success, _ = self.execute_steps(steps)
            if success:
                harvested += 1
            else:
                break
        
        logger.success(f"收菜完成: {harvested} 次")
        return harvested
    
    def plant(self, crop_name: Optional[str] = None) -> int:
        """
        种菜
        
        Args:
            crop_name: 作物名称（可选）
            
        Returns:
            种植数量
        """
        logger.info(f"开始种菜: {crop_name or '默认'}...")
        planted = 0
        
        steps = OperationDefinitions.get_operation("plant")
        if not steps:
            return 0
        
        # 循环种植（最多20次）
        for _ in range(20):
            # TODO: 如果需要选择作物，在这里添加逻辑
            success, _ = self.execute_steps(steps)
            if success:
                planted += 1
            else:
                break
        
        logger.success(f"种菜完成: {planted} 次")
        return planted
    
    def steal(self, max_count: int = 10) -> int:
        """
        偷菜
        
        Returns:
            偷菜数量
        """
        logger.info("开始偷菜...")
        stolen = 0
        
        steps = OperationDefinitions.get_operation("steal")
        if not steps:
            return 0
        
        for _ in range(max_count):
            success, _ = self.execute_steps(steps)
            if success:
                stolen += 1
            else:
                # 尝试滑动查找更多
                scroll_steps = OperationDefinitions.get_operation("scroll_down")
                if scroll_steps:
                    self.execute_steps(scroll_steps)
                else:
                    break
        
        logger.success(f"偷菜完成: {stolen} 次")
        return stolen
    
    def bless(self, max_count: int = 20) -> int:
        """
        祝福
        
        Returns:
            祝福数量
        """
        logger.info("开始祝福...")
        blessed = 0
        
        steps = OperationDefinitions.get_operation("bless")
        if not steps:
            return 0
        
        for _ in range(max_count):
            success, _ = self.execute_steps(steps)
            if success:
                blessed += 1
            else:
                break
        
        logger.success(f"祝福完成: {blessed} 次")
        return blessed
