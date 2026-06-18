"""
ADB点击测试脚本

用于测试点击坐标位置是否正确，验证点击效果

使用方式：
# 点击指定坐标
python tests/adbtap_test.py --port 7555 --x 500 --y 300

# 点击比例坐标
python tests/adbtap_test.py --port 7555 --ratio 0.5,0.5

# 点击多个坐标（批量测试）
python tests/adbtap_test.py --port 7555 --coords "100,200;300,400;500,600"

# 点击后截图验证
python tests/adbtap_test.py --port 7555 --x 500 --y 300 --screenshot

# 长按测试
python tests/adbtap_test.py --port 7555 --x 500 --y 300 --duration 2

# 滑动测试
python tests/adbtap_test.py --port 7555 --swipe "100,200,500,600"
"""

import argparse
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from core.driver import Driver


class AdbTapTester:
    """ADB点击测试器"""
    
    def __init__(self, port: int = 7555):
        self.driver = Driver()
        self.driver.connect(port)
        logger.info(f"ADB点击测试器已初始化，端口: {port}")
        logger.info(f"屏幕尺寸: {self.driver.screen_width}x{self.driver.screen_height}")
    
    def tap(self, x: int, y: int, screenshot: bool = False):
        """点击指定坐标"""
        logger.info("=" * 50)
        logger.info(f"测试点击: ({x}, {y})")
        logger.info("=" * 50)
        
        # 截图前
        if screenshot:
            before_img = self.driver.screenshot()
            logger.info("已截取点击前图片")
        
        # 执行点击
        self.driver.tap(x, y)
        logger.info(f"已点击坐标: ({x}, {y})")
        
        # 等待响应
        time.sleep(0.5)
        
        # 截图后
        if screenshot:
            after_img = self.driver.screenshot()
            logger.info("已截取点击后图片")
            # 保存对比图
            self._save_comparison(before_img, after_img, x, y)
        
        logger.info("点击测试完成")
    
    def tap_ratio(self, ratio_x: float, ratio_y: float, screenshot: bool = False):
        """点击比例坐标"""
        x = int(self.driver.screen_width * ratio_x)
        y = int(self.driver.screen_height * ratio_y)
        logger.info(f"比例坐标 ({ratio_x}, {ratio_y}) -> 像素坐标 ({x}, {y})")
        self.tap(x, y, screenshot)
    
    def long_press(self, x: int, y: int, duration: float = 2.0):
        """长按测试"""
        logger.info("=" * 50)
        logger.info(f"测试长按: ({x}, {y}), 持续 {duration} 秒")
        logger.info("=" * 50)
        
        self.driver.long_press(x, y, duration)
        logger.info(f"已长按坐标: ({x}, {y}), 持续 {duration} 秒")
        logger.info("长按测试完成")
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 0.5):
        """滑动测试"""
        logger.info("=" * 50)
        logger.info(f"测试滑动: ({start_x}, {start_y}) -> ({end_x}, {end_y})")
        logger.info("=" * 50)
        
        self.driver.swipe(start_x, start_y, end_x, end_y, duration)
        logger.info(f"已滑动: ({start_x}, {start_y}) -> ({end_x}, {end_y})")
        logger.info("滑动测试完成")
    
    def batch_tap(self, coords: list, interval: float = 1.0):
        """批量点击测试"""
        logger.info("=" * 50)
        logger.info(f"批量点击测试: {len(coords)} 个坐标")
        logger.info("=" * 50)
        
        for i, (x, y) in enumerate(coords):
            logger.info(f"点击 {i+1}/{len(coords)}: ({x}, {y})")
            self.driver.tap(x, y)
            time.sleep(interval)
        
        logger.info("批量点击测试完成")
    
    def verify_tap(self, x: int, y: int, expected_template: str = None):
        """验证点击效果"""
        logger.info("=" * 50)
        logger.info(f"验证点击: ({x}, {y})")
        logger.info("=" * 50)
        
        # 点击
        self.driver.tap(x, y)
        time.sleep(1)
        
        # 截图验证
        screenshot = self.driver.screenshot()
        
        if expected_template:
            from core.vision import Vision
            vision = Vision()
            found = vision.find_template(screenshot, expected_template)
            if found:
                logger.info(f"验证成功: 找到预期模板 {expected_template}")
            else:
                logger.warning(f"验证失败: 未找到预期模板 {expected_template}")
        else:
            logger.info("点击完成，无模板验证")
        
        logger.info("验证测试完成")
    
    def interactive_mode(self):
        """交互模式"""
        logger.info("=" * 50)
        logger.info("进入交互模式")
        logger.info("输入坐标格式: x,y (如 500,300)")
        logger.info("输入 'q' 退出")
        logger.info("=" * 50)
        
        while True:
            try:
                input_str = input("请输入坐标: ").strip()
                if input_str.lower() == 'q':
                    break
                
                if ',' in input_str:
                    x, y = map(int, input_str.split(','))
                    self.tap(x, y, screenshot=True)
                else:
                    logger.warning("格式错误，请输入 x,y 格式")
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"错误: {e}")
        
        logger.info("交互模式结束")
    
    def _save_comparison(self, before_img, after_img, x: int, y: int):
        """保存对比图"""
        import cv2
        import datetime
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 在图片上标记点击位置
        cv2.circle(before_img, (x, y), 10, (0, 255, 0), 2)
        cv2.circle(after_img, (x, y), 10, (0, 0, 255), 2)
        
        # 保存
        before_path = f"logs/tap_before_{timestamp}.png"
        after_path = f"logs/tap_after_{timestamp}.png"
        
        cv2.imwrite(before_path, before_img)
        cv2.imwrite(after_path, after_img)
        
        logger.info(f"对比图已保存: {before_path}, {after_path}")
    
    def close(self):
        """关闭连接"""
        self.driver.disconnect()
        logger.info("测试器已关闭")


def parse_coords(coords_str: str) -> list:
    """解析坐标字符串"""
    coords = []
    for coord in coords_str.split(';'):
        x, y = map(int, coord.split(','))
        coords.append((x, y))
    return coords


def main():
    parser = argparse.ArgumentParser(description="ADB点击测试脚本")
    parser.add_argument("--port", type=int, default=7555, help="ADB端口")
    parser.add_argument("--x", type=int, help="X坐标")
    parser.add_argument("--y", type=int, help="Y坐标")
    parser.add_argument("--ratio", type=str, help="比例坐标 (如 0.5,0.5)")
    parser.add_argument("--coords", type=str, help="批量坐标 (如 100,200;300,400)")
    parser.add_argument("--screenshot", action="store_true", help="点击后截图")
    parser.add_argument("--duration", type=float, default=2.0, help="长按持续时间")
    parser.add_argument("--swipe", type=str, help="滑动坐标 (如 100,200,500,600)")
    parser.add_argument("--interactive", action="store_true", help="交互模式")
    parser.add_argument("--verify", type=str, help="验证模板名称")
    
    args = parser.parse_args()
    
    # 初始化测试器
    tester = AdbTapTester(args.port)
    
    try:
        if args.interactive:
            tester.interactive_mode()
        elif args.ratio:
            ratio_x, ratio_y = map(float, args.ratio.split(','))
            tester.tap_ratio(ratio_x, ratio_y, args.screenshot)
        elif args.x and args.y:
            if args.verify:
                tester.verify_tap(args.x, args.y, args.verify)
            else:
                tester.tap(args.x, args.y, args.screenshot)
        elif args.coords:
            coords = parse_coords(args.coords)
            tester.batch_tap(coords)
        elif args.swipe:
            coords = list(map(int, args.swipe.split(',')))
            tester.swipe(coords[0], coords[1], coords[2], coords[3])
        else:
            # 默认交互模式
            tester.interactive_mode()
    
    finally:
        tester.close()


if __name__ == "__main__":
    main()