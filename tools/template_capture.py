"""
模板截图工具
用于截图保存页面模板和按钮模板
"""
import os
import time
from pathlib import Path
from typing import Optional, Tuple, Union
from datetime import datetime

from loguru import logger

from core.device import device_manager
from core.vision import vision_engine


class TemplateCapture:
    """模板截图工具"""
    
    # 模板目录
    PAGES_DIR = Path("config/templates/pages")
    BUTTONS_DIR = Path("config/templates/buttons")
    
    def __init__(self):
        # 确保目录存在
        self.PAGES_DIR.mkdir(parents=True, exist_ok=True)
        self.BUTTONS_DIR.mkdir(parents=True, exist_ok=True)
        
        # 记录上一次匹配的模板名
        self._last_matched_template: Optional[str] = None
    
    def capture(
        self,
        name: str,
        template_type: str = "button",
        region: Optional[Union[Tuple[int, int, int, int], str]] = None,
        verify_match: bool = False,
        overwrite: bool = False,
        threshold: float = 0.8
    ) -> Tuple[bool, str]:
        """
        截图保存为模板
        
        Args:
            name: 模板名称（不含扩展名）
            template_type: 模板类型，"page" 或 "button"
            region: 截图区域，可选
                    - None: 全屏截图
                    - Tuple[int, int, int, int]: 像素区域 (x1, y1, x2, y2)
                    - str: 比例/百分比区域 "10%,20%,50%,80%"
            verify_match: 是否验证匹配（截图后验证当前页面能否匹配到此模板）
            overwrite: 是否覆盖已存在的模板（默认 False）
            threshold: 验证匹配时的阈值
        
        Returns:
            Tuple[bool, str]: (是否成功, 消息或路径)
        
        Examples:
            # 实例1：截图保存当前页面图片至页面模板目录
            capture("main_page", template_type="page")
            
            # 实例2：截图保存按钮图片至按钮模板目录（指定区域）
            capture("harvest_btn", template_type="button", region=(100, 200, 300, 400))
            
            # 实例3：截图保存并验证匹配
            capture("login_btn", verify_match=True)
            
            # 实例4：强制覆盖已存在的模板
            capture("harvest_btn", overwrite=True)
        """
        # 1. 确定保存目录
        if template_type == "page":
            save_dir = self.PAGES_DIR
        elif template_type == "button":
            save_dir = self.BUTTONS_DIR
        else:
            return False, f"未知的模板类型: {template_type}，请使用 'page' 或 'button'"
        
        # 2. 构建文件路径
        filename = f"{name}.png"
        filepath = save_dir / filename
        
        # 3. 检查是否已存在
        if filepath.exists() and not overwrite:
            return False, f"模板图片已存在: {filepath}\n如需覆盖，请设置 overwrite=True"
        
        # 4. 截图
        try:
            screenshot = device_manager.screenshot()
            if screenshot is None:
                return False, "截图失败：无法获取屏幕图像"
        except Exception as e:
            return False, f"截图失败: {e}"
        
        # 5. 裁剪区域（如果指定）
        if region is not None:
            region_tuple = self._parse_region(region)
            if region_tuple is None:
                return False, f"无效的区域参数: {region}"
            
            x1, y1, x2, y2 = region_tuple
            # 验证区域有效性
            h, w = screenshot.shape[:2]
            if x1 < 0 or y1 < 0 or x2 > w or y2 > h or x1 >= x2 or y1 >= y2:
                return False, f"区域超出屏幕范围: {region_tuple}, 屏幕: {w}x{h}"
            
            #裁剪
            cropped = screenshot[y1:y2, x1:x2]
            logger.info(f"裁剪区域: ({x1},{y1}) -> ({x2},{y2}), 尺寸: {cropped.shape[1]}x{cropped.shape[0]}")
        else:
            cropped = screenshot
            logger.info(f"全屏截图: {cropped.shape[1]}x{cropped.shape[0]}")
        
        # 6. 保存图片
        try:
            import cv2
            cv2.imwrite(str(filepath), cropped)
            logger.success(f"模板已保存: {filepath}")
        except Exception as e:
            return False, f"保存失败: {e}"
        
        # 7. 验证匹配（可选）
        if verify_match:
            verify_success = self._verify_template_match(filepath, threshold)
            if not verify_success:
                # 删除刚保存的图片（验证失败）
                filepath.unlink()
                return False, f"模板验证失败：无法在当前页面匹配到此模板"
            logger.success(f"模板验证成功: {name}")
        
        return True, str(filepath)
    
    def capture_page(
        self,
        name: str,
        verify_match: bool = False,
        overwrite: bool = False
    ) -> Tuple[bool, str]:
        """
        快捷方法：截图保存页面模板（全屏）
        
        Args:
            name: 模板名称
            verify_match: 是否验证匹配
            overwrite: 是否覆盖
        
        Returns:
            Tuple[bool, str]: (是否成功, 消息或路径)
        """
        return self.capture(
            name=name,
            template_type="page",
            region=None,  # 全屏
            verify_match=verify_match,
            overwrite=overwrite
        )
    
    def capture_button(
        self,
        name: str,
        region: Optional[Union[Tuple[int, int, int, int], str]] = None,
        verify_match: bool = False,
        overwrite: bool = False
    ) -> Tuple[bool, str]:
        """
        快捷方法：截图保存按钮模板
        
        Args:
            name: 模板名称
            region: 截图区域（按钮位置）
            verify_match: 是否验证匹配
            overwrite: 是否覆盖
        
        Returns:
            Tuple[bool, str]: (是否成功, 消息或路径)
        """
        return self.capture(
            name=name,
            template_type="button",
            region=region,
            verify_match=verify_match,
            overwrite=overwrite
        )
    
    def capture_region_interactive(
        self,
        name: str,
        template_type: str = "button",
        show_coords: bool = True
    ) -> Tuple[bool, str]:
        """
        交互式截图：先显示当前屏幕，用户手动选择区域
        
        Args:
            name: 模板名称
            template_type: 模板类型
            show_coords: 是否显示坐标信息
        
        Returns:
            Tuple[bool, str]: (是否成功, 消息或路径)
        
        Note:
            此方法需要在有图形界面的环境中运行
        """
        try:
            screenshot = device_manager.screenshot()
            import cv2
            
            # 显示截图
            window_name = "选择截图区域（按S保存，按Q退出）"
            cv2.imshow(window_name, screenshot)
            
            # 记录鼠标选择的区域
            selected_region = None
            
            def mouse_callback(event, x, y, flags, param):
                nonlocal selected_region
                if event == cv2.EVENT_LBUTTONDOWN:
                    selected_region = [(x, y)]
                elif event == cv2.EVENT_LBUTTONUP:
                    selected_region.append((x, y))
            
            cv2.setMouseCallback(window_name, mouse_callback)
            
            while True:
                key = cv2.waitKey(1) & 0xFF
                if key == ord('s') and selected_region and len(selected_region) == 2:
                    # 保存选中的区域
                    x1, y1 = selected_region[0]
                    x2, y2 = selected_region[1]
                    region = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
                    cv2.destroyAllWindows()
                    return self.capture(name, template_type, region)
                elif key == ord('q'):
                    cv2.destroyAllWindows()
                    return False, "用户取消截图"
            
        except Exception as e:
            return False, f"交互式截图失败: {e}"
    
    def list_templates(self, template_type: Optional[str] = None) -> dict:
        """
        列出所有模板
        
        Args:
            template_type: 模板类型，None 表示列出所有
        
        Returns:
            dict: {"pages": [...], "buttons": [...]}
        """
        result = {"pages": [], "buttons": []}
        
        if template_type is None or template_type == "page":
            for f in self.PAGES_DIR.glob("*.png"):
                result["pages"].append(f.stem)
        
        if template_type is None or template_type == "button":
            for f in self.BUTTONS_DIR.glob("*.png"):
                result["buttons"].append(f.stem)
        
        return result
    
    def delete_template(self, name: str, template_type: str = "button") -> Tuple[bool, str]:
        """
        删除模板
        
        Args:
            name: 模板名称
            template_type: 模板类型
        
        Returns:
            Tuple[bool, str]: (是否成功, 消息)
        """
        if template_type == "page":
            filepath = self.PAGES_DIR / f"{name}.png"
        else:
            filepath = self.BUTTONS_DIR / f"{name}.png"
        
        if not filepath.exists():
            return False, f"模板不存在: {filepath}"
        
        filepath.unlink()
        return True, f"模板已删除: {filepath}"
    
    def _parse_region(
        self,
        region: Union[Tuple[int, int, int, int], str]
    ) -> Optional[Tuple[int, int, int, int]]:
        """
        解析区域参数
        
        支持格式:
        - Tuple[int, int, int, int]: 像素坐标 (x1, y1, x2, y2)
        - str: "x1,y1,x2,y2" 或 "x1%,y1%,x2%,y2%"
        """
        if isinstance(region, tuple):
            return region
        
        if isinstance(region, str):
            try:
                parts = region.split(",")
                if len(parts) != 4:
                    return None
                
                # 获取屏幕尺寸
                screen_w, screen_h = device_manager.screen_size
                
                coords = []
                for i, part in enumerate(parts):
                    part = part.strip()
                    if "%" in part:
                        # 百分比
                        percent = float(part.replace("%", "")) / 100
                        if i % 2 == 0:  # x坐标
                            coords.append(int(percent * screen_w))
                        else:  # y坐标
                            coords.append(int(percent * screen_h))
                    else:
                        # 像素
                        coords.append(int(part))
                
                return tuple(coords)
            except Exception:
                return None
        
        return None
    
    def _verify_template_match(self, filepath: Path, threshold: float) -> bool:
        """
        验证模板能否匹配
        
        Args:
            filepath: 模板文件路径
            threshold: 匹配阈值
        
        Returns:
            bool: 是否能匹配
        """
        try:
            # 加载刚保存的模板
            import cv2
            template = cv2.imread(str(filepath))
            if template is None:
                return False
            
            # 再次截图
            screenshot = device_manager.screenshot()
            
            # 尝试匹配
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                self._last_matched_template = filepath.stem
                logger.debug(f"验证匹配成功: max_val={max_val:.3f}, position={max_loc}")
                return True
            else:
                logger.warning(f"验证匹配失败: max_val={max_val:.3f} < {threshold}")
                return False
                
        except Exception as e:
            logger.error(f"验证匹配异常: {e}")
            return False


# 全局实例
template_capture = TemplateCapture()