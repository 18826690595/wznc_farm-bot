"""
图像识别引擎 - 基于OpenCV实现模板匹配
"""
import cv2
import numpy as np
from pathlib import Path
from loguru import logger
from typing import List, Optional, Tuple


class VisionEngine:
    """
    图像识别引擎
    提供模板匹配、文字识别等视觉能力
    """
    
    def __init__(self, template_dir: str = "config/images"):
        """
        初始化视觉引擎
        
        Args:
            template_dir: 模板图片目录
        """
        self.template_dir = Path(template_dir)
        self.templates = {}
        self._load_templates()
        
        # OCR引擎（延迟加载）
        self._ocr_reader = None
    
    def _load_templates(self):
        """加载所有模板图片"""
        if not self.template_dir.exists():
            logger.warning(f"模板目录不存在: {self.template_dir}")
            return
        
        for img_path in self.template_dir.glob("*.png"):
            template = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
            if template is not None:
                name = img_path.stem
                self.templates[name] = template
                logger.debug(f"加载模板: {name}")
        
        logger.info(f"已加载 {len(self.templates)} 个模板")
    
    def find_template(
        self,
        screenshot: np.ndarray,
        template_name: str,
        threshold: float = 0.8,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        在截图中查找模板

        Args:
            screenshot: 截图（numpy数组）
            template_name: 模板名称
            threshold: 匹配阈值（0-1）
            region: 限定识别区域 (x1,y1,x2,y2)，None为全屏

        Returns:
            匹配区域 (x, y, width, height) 或 None
        """
        if template_name not in self.templates:
            logger.warning(f"模板不存在: {template_name}")
            return None

        template = self.templates[template_name]
        h, w = template.shape[:2]

        # 裁剪区域
        search_img = screenshot
        offset_x, offset_y = 0, 0

        if region:
            x1, y1, x2, y2 = region
            # 边界检查
            h_img, w_img = screenshot.shape[:2]
            x1 = max(0, min(x1, w_img))
            y1 = max(0, min(y1, h_img))
            x2 = max(x1, min(x2, w_img))
            y2 = max(y1, min(y2, h_img))
            search_img = screenshot[y1:y2, x1:x2]
            offset_x, offset_y = x1, y1
            logger.debug(f"限定区域: ({x1},{y1})-({x2},{y2})")

        # 模板匹配
        result = cv2.matchTemplate(search_img, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            x, y = max_loc
            # 还原到全图坐标
            return (offset_x + x, offset_y + y, w, h)

        return None
    
    def find_all_templates(
        self,
        screenshot: np.ndarray,
        template_name: str,
        threshold: float = 0.8,
        min_distance: int = 50,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> List[Tuple[int, int, int, int]]:
        """
        查找所有匹配的模板（多个结果）

        Args:
            screenshot: 截图
            template_name: 模板名称
            threshold: 匹配阈值
            min_distance: 最小距离（去重）
            region: 限定识别区域 (x1,y1,x2,y2)

        Returns:
            匹配区域列表
        """
        if template_name not in self.templates:
            return []

        template = self.templates[template_name]
        h, w = template.shape[:2]

        # 裁剪区域
        search_img = screenshot
        offset_x, offset_y = 0, 0

        if region:
            x1, y1, x2, y2 = region
            h_img, w_img = screenshot.shape[:2]
            x1 = max(0, min(x1, w_img))
            y1 = max(0, min(y1, h_img))
            x2 = max(x1, min(x2, w_img))
            y2 = max(y1, min(y2, h_img))
            search_img = screenshot[y1:y2, x1:x2]
            offset_x, offset_y = x1, y1

        # 模板匹配
        result = cv2.matchTemplate(search_img, template, cv2.TM_CCOEFF_NORMED)

        # 查找所有峰值
        locations = np.where(result >= threshold)
        matches = []

        for pt in zip(*locations[::-1]):
            # 检查与已有匹配的距离
            is_duplicate = False
            for existing in matches:
                dist = np.sqrt((pt[0] - (existing[0] - offset_x))**2 +
                             (pt[1] - (existing[1] - offset_y))**2)
                if dist < min_distance:
                    is_duplicate = True
                    break

            if not is_duplicate:
                # 还原到全图坐标
                matches.append((offset_x + pt[0], offset_y + pt[1], w, h))

        return matches
    
    def get_center(self, rect: Tuple[int, int, int, int]) -> Tuple[int, int]:
        """
        获取矩形中心点
        
        Args:
            rect: (x, y, width, height)
            
        Returns:
            中心点坐标 (x, y)
        """
        x, y, w, h = rect
        return (x + w // 2, y + h // 2)
    
    def wait_for_template(
        self,
        screenshot_func,
        template_name: str,
        timeout: float = 10.0,
        interval: float = 0.5,
        threshold: float = 0.8
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        等待模板出现
        
        Args:
            screenshot_func: 截图函数
            template_name: 模板名称
            timeout: 超时时间
            interval: 检查间隔
            threshold: 匹配阈值
            
        Returns:
            匹配区域或None
        """
        start_time = cv2.getTickCount() / cv2.getTickFrequency()
        
        while True:
            # 检查超时
            current_time = cv2.getTickCount() / cv2.getTickFrequency()
            if current_time - start_time > timeout:
                logger.warning(f"等待模板超时: {template_name}")
                return None
            
            # 截图并查找
            screenshot = screenshot_func()
            result = self.find_template(screenshot, template_name, threshold)
            
            if result:
                return result
            
            # 等待
            import time
            time.sleep(interval)
    
    @property
    def ocr_reader(self):
        """获取OCR阅读器（延迟加载）"""
        if self._ocr_reader is None:
            import easyocr
            self._ocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=False)
            logger.info("OCR引擎已初始化")
        return self._ocr_reader
    
    def recognize_text(
        self, 
        image: np.ndarray,
        region: Optional[Tuple[int, int, int, int]] = None
    ) -> List[Tuple[str, float]]:
        """
        OCR文字识别
        
        Args:
            image: 图片
            region: 识别区域 (x, y, w, h)
            
        Returns:
            识别结果列表 [(文字, 置信度), ...]
        """
        # 裁剪区域
        if region:
            x, y, w, h = region
            image = image[y:y+h, x:x+w]
        
        # OCR识别
        results = self.ocr_reader.readtext(image)
        
        # 格式化输出
        texts = []
        for detection in results:
            text = detection[1]
            confidence = detection[2]
            texts.append((text, confidence))
        
        return texts
    
    def find_text(
        self,
        image: np.ndarray,
        target_text: str
    ) -> Optional[Tuple[int, int]]:
        """
        查找指定文字的位置
        
        Args:
            image: 图片
            target_text: 目标文字
            
        Returns:
            文字中心坐标或None
        """
        results = self.ocr_reader.readtext(image)
        
        for detection in results:
            bbox = detection[0]  # 边界框
            text = detection[1]
            
            if target_text in text:
                # 计算中心点
                x = int((bbox[0][0] + bbox[2][0]) / 2)
                y = int((bbox[0][1] + bbox[2][1]) / 2)
                logger.debug(f"找到文字 '{target_text}': 位置({x}, {y})")
                return (x, y)
        
        return None
