"""
图像识别测试脚本
用于测试模板匹配效果
"""
import argparse
import os
import time
import cv2
from loguru import logger

from core.driver import Driver
from core.vision import VisionEngine
from config.locators import Locators


def test_template_match(port: int, locator_name: str, threshold: float = None, region: tuple = None):
    """
    测试单个模板匹配
    
    Args:
        port: ADB端口
        locator_name: 定位器名称
        threshold: 匹配阈值（可选，覆盖默认值）
        region: 匹配区域（可选）
    """
    logger.info("=" * 50)
    logger.info(f"测试模板匹配: {locator_name}")
    logger.info("=" * 50)
    
    # 获取定位器配置
    locator_config = Locators.ALL.get(locator_name)
    if not locator_config:
        logger.error(f"定位器不存在: {locator_name}")
        return False
    
    logger.info(f"定位器配置:")
    logger.info(f"  模板文件: {locator_config.get('template', 'N/A')}")
    logger.info(f"  描述: {locator_config.get('description', 'N/A')}")
    
    # 使用传入阈值或默认阈值
    actual_threshold = threshold or locator_config.get('threshold', 0.8)
    logger.info(f"  阈值: {actual_threshold}")
    
    # 使用传入区域或默认区域
    actual_region = region or locator_config.get('region')
    if actual_region:
        logger.info(f"  区域: {actual_region}")
    else:
        logger.info(f"  区域: 全屏")
    
    # 连接设备并截图
    driver = Driver()
    driver.connect(port)
    
    screenshot = driver.screenshot()
    logger.info(f"截图尺寸: {screenshot.shape}")
    
    # 初始化视觉引擎
    vision = VisionEngine()
    
    # 加载模板
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "config", "templates", locator_config.get('template', '')
    )
    
    if not os.path.exists(template_path):
        logger.error(f"模板文件不存在: {template_path}")
        driver.disconnect()
        return False
    
    template = cv2.imread(template_path)
    logger.info(f"模板尺寸: {template.shape}")
    
    # 执行匹配
    result = vision.find_template(
        screenshot,
        locator_name,
        threshold=actual_threshold,
        region=actual_region
    )
    
    if result:
        x, y = result
        logger.info(f"✓ 匹配成功! 位置: ({x}, {y})")
        
        # 在截图上标记匹配位置
        marked_screenshot = screenshot.copy()
        cv2.circle(marked_screenshot, (x, y), 20, (0, 255, 0), 3)
        cv2.putText(marked_screenshot, locator_name, (x + 25, y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        # 保存标记后的截图
        save_dir = os.path.join(os.path.dirname(__file__), "test_results")
        os.makedirs(save_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(save_dir, f"{timestamp}_{locator_name}_matched.png")
        cv2.imwrite(save_path, marked_screenshot)
        logger.info(f"标记截图已保存: {save_path}")
        
        # 点击测试
        logger.info(f"点击位置: ({x}, {y})")
        driver.tap(x, y)
        time.sleep(1)
        
        success = True
    else:
        logger.warning(f"✗ 匹配失败，未找到模板")
        
        # 保存截图用于调试
        save_dir = os.path.join(os.path.dirname(__file__), "test_results")
        os.makedirs(save_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(save_dir, f"{timestamp}_{locator_name}_failed.png")
        cv2.imwrite(save_path, screenshot)
        logger.info(f"截图已保存用于调试: {save_path}")
        
        success = False
    
    driver.disconnect()
    return success


def test_all_templates(port: int):
    """测试所有模板匹配"""
    logger.info("=" * 50)
    logger.info("测试所有模板匹配")
    logger.info("=" * 50)
    
    results = {}
    
    for locator_name in Locators.ALL.keys():
        logger.info(f"\n测试: {locator_name}")
        success = test_template_match(port, locator_name)
        results[locator_name] = success
        time.sleep(0.5)
    
    # 输出统计
    logger.info("\n" + "=" * 50)
    logger.info("测试结果统计")
    logger.info("=" * 50)
    
    success_count = sum(1 for v in results.values() if v)
    fail_count = len(results) - success_count
    
    for name, success in results.items():
        status = "✓" if success else "✗"
        logger.info(f"{status} {name}")
    
    logger.info(f"\n成功: {success_count}, 失败: {fail_count}")
    
    return results


def test_region_matching(port: int, locator_name: str, regions: list):
    """
    测试不同区域匹配效果
    
    Args:
        port: ADB端口
        locator_name: 定位器名称
        regions: 区域列表 [(x1,y1,x2,y2), ...]
    """
    logger.info("=" * 50)
    logger.info(f"测试区域匹配: {locator_name}")
    logger.info("=" * 50)
    
    driver = Driver()
    driver.connect(port)
    
    screenshot = driver.screenshot()
    vision = VisionEngine()
    
    for region in regions:
        logger.info(f"\n测试区域: {region}")
        result = vision.find_template(screenshot, locator_name, region=region)
        
        if result:
            logger.info(f"✓ 区域内匹配成功: {result}")
        else:
            logger.info(f"✗ 区域内未匹配")
    
    driver.disconnect()


def interactive_match_test(port: int):
    """交互式匹配测试"""
    logger.info("=" * 50)
    logger.info("交互式匹配测试")
    logger.info("=" * 50)
    
    driver = Driver()
    driver.connect(port)
    
    screen_width, screen_height = driver.get_screen_size()
    logger.info(f"屏幕尺寸: {screen_width} x {screen_height}")
    
    logger.info("可用定位器:")
    for name in Locators.ALL.keys():
        logger.info(f"  - {name}")
    
    logger.info("\n输入定位器名称进行测试，输入 'q' 退出")
    
    while True:
        input_str = input("\n定位器名称: ").strip()
        if input_str.lower() == 'q':
            break
        
        if input_str not in Locators.ALL:
            logger.warning(f"定位器不存在: {input_str}")
            continue
        
        # 截图并匹配
        screenshot = driver.screenshot()
        vision = VisionEngine()
        result = vision.find_template(screenshot, input_str)
        
        if result:
            logger.info(f"✓ 匹配成功: {result}")
            logger.info("是否点击? (y/n)")
            if input().lower() == 'y':
                driver.tap(result[0], result[1])
                time.sleep(1)
        else:
            logger.info(f"✗ 未匹配")
    
    driver.disconnect()
    logger.info("交互测试结束")


def save_current_screenshot(port: int, name: str = "current"):
    """保存当前截图"""
    logger.info("=" * 50)
    logger.info("保存当前截图")
    logger.info("=" * 50)
    
    driver = Driver()
    driver.connect(port)
    
    screenshot = driver.screenshot()
    
    save_dir = os.path.join(os.path.dirname(__file__), "test_results")
    os.makedirs(save_dir, exist_ok=True)
    
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    save_path = os.path.join(save_dir, f"{timestamp}_{name}.png")
    cv2.imwrite(save_path, screenshot)
    
    logger.info(f"截图已保存: {save_path}")
    
    driver.disconnect()


def main():
    parser = argparse.ArgumentParser(description="图像识别测试脚本")
    parser.add_argument("--port", type=int, default=7555, help="ADB端口")
    parser.add_argument("--locator", type=str, help="定位器名称")
    parser.add_argument("--threshold", type=float, help="匹配阈值")
    parser.add_argument("--region", type=str, help="匹配区域 (x1,y1,x2,y2)")
    parser.add_argument("--all", action="store_true", help="测试所有模板")
    parser.add_argument("--interactive", action="store_true", help="交互式测试")
    parser.add_argument("--save", action="store_true", help="保存当前截图")
    parser.add_argument("--name", type=str, default="current", help="截图名称")
    
    args = parser.parse_args()
    
    region = None
    if args.region:
        region = tuple(map(int, args.region.split(',')))
    
    if args.interactive:
        interactive_match_test(args.port)
    elif args.all:
        test_all_templates(args.port)
    elif args.save:
        save_current_screenshot(args.port, args.name)
    elif args.locator:
        test_template_match(args.port, args.locator, args.threshold, region)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()