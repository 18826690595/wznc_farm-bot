"""
基礎操作 - 只封装底层操作，不含业务逻辑
"""
import re
import time
import random
from loguru import logger
from typing import Optional, List, Tuple, Union
from core.device import device_manager
from core.vision import VisionEngine
from config.template_config import template_config


# ========== 类型定义 ==========
# 坐标支持多种格式:
# - 像素: "500,300"
# - 比例: "0.5,0.5" (屏幕中央)
# - 比例: "50%,50%" (屏幕中央)
# - 区域中心: (x1, y1, x2, y2)
Coordinate = Union[str, Tuple[int, int]]
Region = Tuple[int, int, int, int]  # (x1, y1, x2, y2)


class ActionBase:
    """
    基础操作类 - 只做底层封装
    
    不包含具体业务逻辑，只提供：
    - 点击模板
    - 点击坐标
    - 滑动
    - 等待
    等
    """
    
    def __init__(self, vision: VisionEngine, random_delay: bool = True):
        self.vision = vision
        self.random_delay = random_delay
        self.device = device_manager
        self._found_positions: List[Tuple[int, int]] = []
    
    def _delay(self, base: float = 0.5, variance: float = 0.3):
        """随机延迟"""
        if self.random_delay:
            delay = base + random.uniform(-variance, variance)
            delay = max(0.1, delay)
        else:
            delay = base
        time.sleep(delay)

    # ========== 坐标解析 ==========

    def parse_coordinate(self, coord) -> Tuple[int, int]:
        """
        解析坐标（支持像素和比例两种格式）

        支持的格式:
            "500,300"           -> 像素坐标
            "0.5,0.5"           -> 比例坐标（屏幕中央）
            "50%,50%"           -> 百分比坐标（屏幕中央）
            (500, 300)          -> 元组格式
        """
        if isinstance(coord, (tuple, list)):
            return int(coord[0]), int(coord[1])

        coord_str = str(coord).strip()

        # 解析百分比格式 "50%,50%"
        if '%' in coord_str:
            parts = coord_str.replace('%', '').split(',')
            width, height = self.device.screen_size
            x = int(float(parts[0].strip()) / 100 * width)
            y = int(float(parts[1].strip()) / 100 * height)
            return x, y

        # 解析比例格式 "0.5,0.5"
        if re.match(r'^[\d.]+,[\d.]+$', coord_str):
            parts = coord_str.split(',')
            if float(parts[0]) <= 1.0 and float(parts[1]) <= 1.0:
                width, height = self.device.screen_size
                x = int(float(parts[0]) * width)
                y = int(float(parts[1]) * height)
                return x, y

        # 像素格式 "500,300"
        parts = coord_str.split(',')
        return int(parts[0].strip()), int(parts[1].strip())

    def parse_region(self, region_str: str) -> Optional[Region]:
        """
        解析区域字符串

        格式: "x1,y1,x2,y2" 或 "x1%,y1%,x2%,y2%"

        示例:
            "100,200,500,800"     -> 像素区域
            "10%,20%,50%,80%"     -> 比例区域
        """
        if not region_str:
            return None

        region_str = region_str.strip()
        width, height = self.device.screen_size

        if '%' in region_str:
            parts = region_str.replace('%', '').split(',')
            x1 = int(float(parts[0]) / 100 * width)
            y1 = int(float(parts[1]) / 100 * height)
            x2 = int(float(parts[2]) / 100 * width)
            y2 = int(float(parts[3]) / 100 * height)
        else:
            parts = region_str.split(',')
            x1, y1, x2, y2 = [int(p.strip()) for p in parts[:4]]

        return (x1, y1, x2, y2)
    
    # ========== 点击操作 ==========

    def click_template(self, template_name: str, threshold: Optional[float] = None,
                       region: Optional[Region] = None) -> bool:
        """
        点击模板图片

        Args:
            template_name: 模板名称
            threshold: 匹配阈值（None则用配置）
            region: 限定识别区域 (x1,y1,x2,y2)，None为全屏
        """
        info = template_config.get_info(template_name)
        img = template_config.get(template_name)

        if img is None:
            logger.warning(f"模板不存在: {template_name}")
            return False

        threshold = threshold or (info.threshold if info else 0.8)
        screenshot = self.device.screenshot()
        rect = self.vision.find_template(screenshot, template_name, threshold, region=region)

        if rect:
            center = self.vision.get_center(rect)
            self.device.tap(*center)
            self._delay(0.5)
            logger.debug(f"点击模板 {template_name} 成功: {center}")
            return True

        logger.debug(f"未找到模板: {template_name}")
        return False

    def click_position(self, x=None, y=None, coord: Optional[Coordinate] = None):
        """
        点击坐标（支持像素和比例）

        支持多种调用方式:
            click_position(500, 300)         # 像素
            click_position(coord="0.5,0.5")  # 比例
            click_position(coord="50%,50%")  # 百分比
            click_position(coord="500,300")  # 像素字符串
        """
        if coord is not None:
            x, y = self.parse_coordinate(coord)
        elif x is None or y is None:
            raise ValueError("必须提供坐标: x,y 或 coord")

        self.device.tap(int(x), int(y))
        self._delay(0.3)
        logger.debug(f"点击坐标: ({x}, {y})")

    def click_region(self, region: Region):
        """
        点击区域中心

        示例:
            click_region((100, 200, 500, 800))  # 点击区域中心
        """
        x1, y1, x2, y2 = region
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        self.device.tap(center_x, center_y)
        self._delay(0.3)
        logger.debug(f"点击区域中心: ({center_x}, {center_y})")

    def long_press(self, x=None, y=None, duration: float = 1.0,
                   coord: Optional[Coordinate] = None):
        """
        长按（支持比例）

        示例:
            long_press(500, 300, 2.0)
            long_press(coord="0.5,0.5", duration=2.0)
        """
        if coord is not None:
            x, y = self.parse_coordinate(coord)
        self.device.long_press(int(x), int(y), duration)
        self._delay(0.3)
    
    # ========== 滑动操作 ==========
    
    def swipe(self, direction: str, distance: int = 300):
        """滑动"""
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
    
    # ========== 查找操作 ==========

    def find_all(self, template_name: str,
                 region: Optional[Region] = None) -> List[Tuple[int, int]]:
        """
        查找所有匹配位置

        Args:
            template_name: 模板名称
            region: 限定识别区域 (x1,y1,x2,y2)

        返回: 中心点坐标列表
        """
        info = template_config.get_info(template_name)
        img = template_config.get(template_name)

        if img is None:
            return []

        screenshot = self.device.screenshot()
        threshold = info.threshold if info else 0.8
        rects = self.vision.find_all_templates(screenshot, template_name, threshold, region=region)
        positions = [self.vision.get_center(r) for r in rects]
        self._found_positions = positions

        if region:
            logger.debug(f"在区域 {region} 找到 {len(positions)} 个 '{template_name}'")
        else:
            logger.debug(f"全屏找到 {len(positions)} 个 '{template_name}'")
        return positions

    def exists(self, template_name: str,
               region: Optional[Region] = None,
               threshold: Optional[float] = None) -> bool:
        """
        判断按钮是否存在（不点击）

        Args:
            template_name: 模板名称
            region: 限定识别区域
            threshold: 匹配阈值
        """
        positions = self.find_all(template_name, region=region)
        return len(positions) > 0

    def wait_for(self, template_name: str,
                 timeout: float = 10.0,
                 region: Optional[Region] = None) -> bool:
        """
        等待按钮出现

        Args:
            template_name: 模板名称
            timeout: 超时时间（秒）
            region: 限定识别区域

        Returns:
            True: 按钮出现
            False: 超时未出现
        """
        start = time.time()
        while time.time() - start < timeout:
            if self.exists(template_name, region=region):
                return True
            time.sleep(0.5)
        return False

    def click_found(self, index: int = 0) -> bool:
        """点击已找到的位置"""
        if index >= len(self._found_positions):
            return False
        x, y = self._found_positions[index]
        self.device.tap(x, y)
        self._delay(0.5)
        return True
    
    # ========== 其他操作 ==========
    
    def wait(self, seconds: float):
        """等待"""
        time.sleep(seconds)
    
    def back(self):
        """返回键"""
        self.device.back()
        self._delay(0.3)
    
    def screenshot(self):
        """截图"""
        return self.device.screenshot()
