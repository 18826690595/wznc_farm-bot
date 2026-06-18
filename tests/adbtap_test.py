"""
ADB 点击测试脚本
用于测试点击坐标位置是否正确
"""
import argparse
import time
from loguru import logger

from core.driver import Driver


def test_single_tap(port: int, x: int, y: int, delay: float = 1.0):
    """
    测试单次点击
    
    Args:
        port: ADB端口
        x: 点击X坐标
        y: 点击Y坐标
        delay: 点击后等待时间
    """
    logger.info("=" * 50)
    logger.info(f"测试点击坐标: ({x}, {y})")
    logger.info("=" * 50)
    
    driver = Driver()
    driver.connect(port)
    
    # 获取屏幕尺寸
    screen_width, screen_height = driver.get_screen_size()
    logger.info(f"屏幕尺寸: {screen_width} x {screen_height}")
    
    # 点击前截图
    logger.info("点击前截图...")
    screenshot_before = driver.screenshot()
    logger.info(f"截图尺寸: {screenshot_before.shape}")
    
    # 执行点击
    logger.info(f"点击坐标: ({x}, {y})")
    driver.tap(x, y)
    
    # 等待
    time.sleep(delay)
    
    # 点击后截图
    logger.info("点击后截图...")
    screenshot_after = driver.screenshot()
    
    # 保存截图对比
    import cv2
    import os
    save_dir = os.path.join(os.path.dirname(__file__), "test_results")
    os.makedirs(save_dir, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    cv2.imwrite(os.path.join(save_dir, f"{timestamp}_before.png"), screenshot_before)
    cv2.imwrite(os.path.join(save_dir, f"{timestamp}_after.png"), screenshot_after)
    
    logger.info(f"截图已保存到: {save_dir}")
    
    driver.disconnect()
    logger.info("点击测试完成")


def test_tap_sequence(port: int, coords: list, delay: float = 1.0):
    """
    测试连续点击多个坐标
    
    Args:
        port: ADB端口
        coords: 坐标列表 [(x1, y1), (x2, y2), ...]
        delay: 每次点击后等待时间
    """
    logger.info("=" * 50)
    logger.info(f"测试连续点击 {len(coords)} 个坐标")
    logger.info("=" * 50)
    
    driver = Driver()
    driver.connect(port)
    
    screen_width, screen_height = driver.get_screen_size()
    logger.info(f"屏幕尺寸: {screen_width} x {screen_height}")
    
    for i, (x, y) in enumerate(coords):
        logger.info(f"\n第 {i+1} 次点击: ({x}, {y})")
        driver.tap(x, y)
        time.sleep(delay)
    
    driver.disconnect()
    logger.info("连续点击测试完成")


def test_proportion_tap(port: int, proportion_x: float, proportion_y: float, delay: float = 1.0):
    """
    测试比例坐标点击
    
    Args:
        port: ADB端口
        proportion_x: X比例 (0.0 ~ 1.0)
        proportion_y: Y比例 (0.0 ~ 1.0)
        delay: 点击后等待时间
    """
    logger.info("=" * 50)
    logger.info(f"测试比例点击: ({proportion_x}, {proportion_y})")
    logger.info("=" * 50)
    
    driver = Driver()
    driver.connect(port)
    
    screen_width, screen_height = driver.get_screen_size()
    logger.info(f"屏幕尺寸: {screen_width} x {screen_height}")
    
    # 计算实际坐标
    x = int(screen_width * proportion_x)
    y = int(screen_height * proportion_y)
    logger.info(f"实际坐标: ({x}, {y})")
    
    driver.tap(x, y)
    time.sleep(delay)
    
    driver.disconnect()
    logger.info("比例点击测试完成")


def test_region_tap(port: int, region: tuple, delay: float = 1.0):
    """
    测试区域中心点击
    
    Args:
        port: ADB端口
        region: 区域 (x1, y1, x2, y2)
        delay: 点击后等待时间
    """
    logger.info("=" * 50)
    logger.info(f"测试区域点击: {region}")
    logger.info("=" * 50)
    
    driver = Driver()
    driver.connect(port)
    
    x1, y1, x2, y2 = region
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    logger.info(f"区域中心坐标: ({center_x}, {center_y})")
    
    driver.tap(center_x, center_y)
    time.sleep(delay)
    
    driver.disconnect()
    logger.info("区域点击测试完成")


def interactive_test(port: int):
    """交互式点击测试"""
    logger.info("=" * 50)
    logger.info("交互式点击测试")
    logger.info("=" * 50)
    
    driver = Driver()
    driver.connect(port)
    
    screen_width, screen_height = driver.get_screen_size()
    logger.info(f"屏幕尺寸: {screen_width} x {screen_height}")
    logger.info("输入坐标进行测试，输入 'q' 退出")
    
    while True:
        try:
            input_str = input("\n输入坐标 (x,y) 或比例 (0.5,0.5): ")
            if input_str.lower() == 'q':
                break
            
            parts = input_str.split(',')
            x_str, y_str = parts[0].strip(), parts[1].strip()
            
            # 判断是比例还是像素
            if '.' in x_str or '.' in y_str:
                x = int(screen_width * float(x_str))
                y = int(screen_height * float(y_str))
                logger.info(f"比例转换: ({float(x_str)}, {float(y_str)}) -> ({x}, {y})")
            else:
                x = int(x_str)
                y = int(y_str)
            
            logger.info(f"点击: ({x}, {y})")
            driver.tap(x, y)
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"输入错误: {e}")
    
    driver.disconnect()
    logger.info("交互测试结束")


def main():
    parser = argparse.ArgumentParser(description="ADB点击测试脚本")
    parser.add_argument("--port", type=int, default=7555, help="ADB端口")
    parser.add_argument("--x", type=int, help="点击X坐标")
    parser.add_argument("--y", type=int, help="点击Y坐标")
    parser.add_argument("--px", type=float, help="点击X比例 (0.0~1.0)")
    parser.add_argument("--py", type=float, help="点击Y比例 (0.0~1.0)")
    parser.add_argument("--region", type=str, help="点击区域 (x1,y1,x2,y2)")
    parser.add_argument("--coords", type=str, help="连续点击坐标 (x1,y1;x2,y2;x3,y3)")
    parser.add_argument("--delay", type=float, default=1.0, help="点击后等待时间")
    parser.add_argument("--interactive", action="store_true", help="交互式测试")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_test(args.port)
    elif args.x and args.y:
        test_single_tap(args.port, args.x, args.y, args.delay)
    elif args.px and args.py:
        test_proportion_tap(args.port, args.px, args.py, args.delay)
    elif args.region:
        region = tuple(map(int, args.region.split(',')))
        test_region_tap(args.port, region, args.delay)
    elif args.coords:
        coords = [tuple(map(int, c.split(','))) for c in args.coords.split(';')]
        test_tap_sequence(args.port, coords, args.delay)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()