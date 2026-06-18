"""
图像识别测试脚本

用于测试图像识别效果，验证模板匹配是否正确

使用方式：
# 测试识别指定模板
python tests/vision_test.py --port 7555 --template farm_icon

# 测试识别多个模板
python tests/vision_test.py --port 7555 --templates "farm_icon,harvest_btn,plant_btn"

# 测试识别并显示结果
python tests/vision_test.py --port 7555 --template farm_icon --show

# 测试识别指定区域
python tests/vision_test.py --port 7555 --template harvest_btn --region "100,200,300,400"

# 测试所有已定义的模板
python tests/vision_test.py --port 7555 --all

# 截图保存并标注识别结果
python tests/vision_test.py --port 7555 --template farm_icon --save

# 调整匹配阈值测试
python tests/vision_test.py --port 7555 --template farm_icon --threshold 0.7
"""

import argparse
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from core.driver import Driver
from core.vision import Vision
from config.locators import Locators


class VisionTester:
    """图像识别测试器"""
    
    def __init__(self, port: int = 7555):
        self.driver = Driver()
        self.driver.connect(port)
        self.vision = Vision()
        logger.info(f"图像识别测试器已初始化，端口: {port}")
        logger.info(f"屏幕尺寸: {self.driver.screen_width}x{self.driver.screen_height}")
    
    def test_template(self, template_name: str, threshold: float = None, 
                      region: tuple = None, show: bool = False, save: bool = False):
        """测试单个模板识别"""
        logger.info("=" * 50)
        logger.info(f"测试模板识别: {template_name}")
        logger.info("=" * 50)
        
        # 获取模板配置
        locator = Locators.get(template_name)
        if not locator:
            logger.error(f"模板未定义: {template_name}")
            return None
        
        logger.info(f"模板信息: {locator}")
        
        # 使用自定义阈值或默认阈值
        if threshold is None:
            threshold = locator.get("threshold", 0.8)
        
        logger.info(f"匹配阈值: {threshold}")
        
        # 截图
        screenshot = self.driver.screenshot()
        logger.info("已截取当前屏幕")
        
        # 识别
        result = self.vision.find_template(
            screenshot, 
            template_name,
            threshold=threshold,
            region=region
        )
        
        if result:
            x, y = result
            logger.info(f"识别成功! 位置: ({x}, {y})")
            
            # 显示或保存结果
            if show or save:
                self._mark_result(screenshot, x, y, template_name, save)
            
            return (x, y)
        else:
            logger.warning(f"识别失败: 未找到模板 {template_name}")
            
            if save:
                self._save_failed(screenshot, template_name)
            
            return None
    
    def test_templates(self, templates: list, threshold: float = None, save: bool = False):
        """测试多个模板识别"""
        logger.info("=" * 50)
        logger.info(f"测试多个模板: {len(templates)} 个")
        logger.info("=" * 50)
        
        results = {}
        screenshot = self.driver.screenshot()
        
        for template_name in templates:
            locator = Locators.get(template_name)
            if not locator:
                logger.warning(f"模板未定义: {template_name}")
                results[template_name] = {"found": False, "reason": "未定义"}
                continue
            
            actual_threshold = threshold or locator.get("threshold", 0.8)
            
            result = self.vision.find_template(screenshot, template_name, threshold=actual_threshold)
            
            if result:
                x, y = result
                logger.info(f"  {template_name}: 找到 @ ({x}, {y})")
                results[template_name] = {"found": True, "position": (x, y)}
            else:
                logger.warning(f"  {template_name}: 未找到")
                results[template_name] = {"found": False, "reason": "未匹配"}
        
        # 汇总
        logger.info("=" * 50)
        logger.info("识别汇总:")
        found_count = sum(1 for r in results.values() if r["found"])
        logger.info(f"  找到: {found_count}/{len(templates)}")
        for name, result in results.items():
            status = "✓" if result["found"] else "✗"
            logger.info(f"  {status} {name}: {result}")
        logger.info("=" * 50)
        
        # 保存标注图
        if save:
            self._save_multi_results(screenshot, results)
        
        return results
    
    def test_all_locators(self, save: bool = False):
        """测试所有已定义的定位器"""
        logger.info("=" * 50)
        logger.info("测试所有定位器")
        logger.info("=" * 50)
        
        all_locators = Locators.get_all()
        logger.info(f"已定义定位器数量: {len(all_locators)}")
        
        templates = list(all_locators.keys())
        return self.test_templates(templates, save=save)
    
    def test_region(self, template_name: str, region: tuple, save: bool = False):
        """测试区域识别"""
        logger.info("=" * 50)
        logger.info(f"测试区域识别: {template_name}")
        logger.info(f"区域: {region}")
        logger.info("=" * 50)
        
        return self.test_template(template_name, region=region, save=save)
    
    def compare_thresholds(self, template_name: str):
        """比较不同阈值的识别效果"""
        logger.info("=" * 50)
        logger.info(f"阈值比较测试: {template_name}")
        logger.info("=" * 50)
        
        thresholds = [0.6, 0.7, 0.8, 0.9]
        screenshot = self.driver.screenshot()
        
        results = {}
        for threshold in thresholds:
            result = self.vision.find_template(screenshot, template_name, threshold=threshold)
            results[threshold] = result
            
            if result:
                logger.info(f"  阈值 {threshold}: 找到 @ ({result[0]}, {result[1]})")
            else:
                logger.warning(f"  阈值 {threshold}: 未找到")
        
        # 推荐
        found_thresholds = [t for t, r in results.items() if r]
        if found_thresholds:
            recommended = max(found_thresholds)
            logger.info(f"推荐阈值: {recommended}")
        else:
            logger.warning("所有阈值都无法识别，建议检查模板图片")
        
        return results
    
    def interactive_mode(self):
        """交互模式"""
        logger.info("=" * 50)
        logger.info("进入交互模式")
        logger.info("输入模板名称进行测试")
        logger.info("输入 'all' 测试所有模板")
        logger.info("输入 'list' 列出所有模板")
        logger.info("输入 'q' 退出")
        logger.info("=" * 50)
        
        while True:
            try:
                input_str = input("请输入模板名称: ").strip()
                
                if input_str.lower() == 'q':
                    break
                elif input_str.lower() == 'all':
                    self.test_all_locators(save=True)
                elif input_str.lower() == 'list':
                    all_locators = Locators.get_all()
                    logger.info("已定义模板:")
                    for name, info in all_locators.items():
                        logger.info(f"  {name}: {info.get('description', '')}")
                else:
                    self.test_template(input_str, save=True)
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"错误: {e}")
        
        logger.info("交互模式结束")
    
    def _mark_result(self, screenshot, x: int, y: int, template_name: str, save: bool):
        """标注识别结果"""
        import cv2
        import datetime
        
        # 标记识别位置
        cv2.circle(screenshot, (x, y), 20, (0, 255, 0), 3)
        cv2.putText(screenshot, template_name, (x - 50, y - 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        if save:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"logs/vision_{template_name}_{timestamp}.png"
            cv2.imwrite(path, screenshot)
            logger.info(f"结果图已保存: {path}")
    
    def _save_failed(self, screenshot, template_name: str):
        """保存识别失败的截图"""
        import cv2
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"logs/vision_failed_{template_name}_{timestamp}.png"
        cv2.imwrite(path, screenshot)
        logger.info(f"失败截图已保存: {path}")
    
    def _save_multi_results(self, screenshot, results: dict):
        """保存多个结果的标注图"""
        import cv2
        import datetime
        
        for name, result in results.items():
            if result["found"]:
                x, y = result["position"]
                cv2.circle(screenshot, (x, y), 15, (0, 255, 0), 2)
                cv2.putText(screenshot, name, (x - 30, y - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"logs/vision_all_{timestamp}.png"
        cv2.imwrite(path, screenshot)
        logger.info(f"汇总结果图已保存: {path}")
    
    def close(self):
        """关闭连接"""
        self.driver.disconnect()
        logger.info("测试器已关闭")


def parse_region(region_str: str) -> tuple:
    """解析区域字符串"""
    coords = list(map(int, region_str.split(',')))
    return tuple(coords)


def main():
    parser = argparse.ArgumentParser(description="图像识别测试脚本")
    parser.add_argument("--port", type=int, default=7555, help="ADB端口")
    parser.add_argument("--template", type=str, help="模板名称")
    parser.add_argument("--templates", type=str, help="多个模板名称 (逗号分隔)")
    parser.add_argument("--all", action="store_true", help="测试所有模板")
    parser.add_argument("--threshold", type=float, help="匹配阈值")
    parser.add_argument("--region", type=str, help="识别区域 (如 100,200,300,400)")
    parser.add_argument("--show", action="store_true", help="显示结果")
    parser.add_argument("--save", action="store_true", help="保存结果图")
    parser.add_argument("--compare", action="store_true", help="比较不同阈值")
    parser.add_argument("--interactive", action="store_true", help="交互模式")
    
    args = parser.parse_args()
    
    # 初始化测试器
    tester = VisionTester(args.port)
    
    try:
        region = parse_region(args.region) if args.region else None
        
        if args.interactive:
            tester.interactive_mode()
        elif args.all:
            tester.test_all_locators(save=args.save)
        elif args.templates:
            templates = args.templates.split(',')
            tester.test_templates(templates, args.threshold, args.save)
        elif args.template:
            if args.compare:
                tester.compare_thresholds(args.template)
            else:
                tester.test_template(args.template, args.threshold, region, args.show, args.save)
        else:
            # 默认交互模式
            tester.interactive_mode()
    
    finally:
        tester.close()


if __name__ == "__main__":
    main()