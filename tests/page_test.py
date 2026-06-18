"""
页面操作测试脚本
用于测试 Page 类的操作方法
"""
import argparse
from loguru import logger

from core.driver import Driver
from pages.game_page import GamePage
from pages.farm_page import FarmPage
from pages.friend_page import FriendPage
from config.locators import Locators


def test_game_page(port: int = 7555):
    """测试游戏页面操作"""
    logger.info("=" * 50)
    logger.info("测试 GamePage 页面操作")
    logger.info("=" * 50)
    
    driver = Driver()
    driver.connect(port)
    
    game_page = GamePage(driver)
    
    # 测试进入农场
    logger.info("\n--- 测试 enter_farm ---")
    result = game_page.enter_farm()
    logger.info(f"进入农场结果: {result}")
    
    # 测试退出农场
    logger.info("\n--- 测试 exit_farm ---")
    result = game_page.exit_farm()
    logger.info(f"退出农场结果: {result}")
    
    driver.disconnect()
    logger.info("GamePage 测试完成")


def test_farm_page(port: int = 7555):
    """测试农场页面操作"""
    logger.info("=" * 50)
    logger.info("测试 FarmPage 页面操作")
    logger.info("=" * 50)
    
    driver = Driver()
    driver.connect(port)
    
    farm_page = FarmPage(driver)
    
    # 先进入农场
    game_page = GamePage(driver)
    game_page.enter_farm()
    
    # 测试收菜
    logger.info("\n--- 测试 harvest_all ---")
    count = farm_page.harvest_all()
    logger.info(f"收获数量: {count}")
    
    # 测试种菜
    logger.info("\n--- 测试 plant ---")
    result = farm_page.plant(crop="wheat")
    logger.info(f"种植结果: {result}")
    
    # 测试检查状态
    logger.info("\n--- 测试 check_empty_plots ---")
    empty_count = farm_page.check_empty_plots()
    logger.info(f"空地数量: {empty_count}")
    
    # 退出农场
    game_page.exit_farm()
    
    driver.disconnect()
    logger.info("FarmPage 测试完成")


def test_friend_page(port: int = 7555):
    """测试好友页面操作"""
    logger.info("=" * 50)
    logger.info("测试 FriendPage 页面操作")
    logger.info("=" * 50)
    
    driver = Driver()
    driver.connect(port)
    
    friend_page = FriendPage(driver)
    
    # 先进入农场
    game_page = GamePage(driver)
    game_page.enter_farm()
    
    # 测试打开好友列表
    logger.info("\n--- 测试 open_friend_list ---")
    result = friend_page.open_friend_list()
    logger.info(f"打开好友列表结果: {result}")
    
    # 测试偷菜
    logger.info("\n--- 测试 steal_from_friends ---")
    count = friend_page.steal_from_friends(max_count=5)
    logger.info(f"偷菜数量: {count}")
    
    # 测试祝福
    logger.info("\n--- 测试 bless_friends ---")
    count = friend_page.bless_friends(max_count=5)
    logger.info(f"祝福数量: {count}")
    
    # 关闭好友列表
    friend_page.close_friend_list()
    
    # 退出农场
    game_page.exit_farm()
    
    driver.disconnect()
    logger.info("FriendPage 测试完成")


def test_all_pages(port: int = 7555):
    """测试所有页面"""
    test_game_page(port)
    test_farm_page(port)
    test_friend_page(port)


def list_locators():
    """列出所有定位器"""
    logger.info("=" * 50)
    logger.info("所有元素定位器配置")
    logger.info("=" * 50)
    
    for name, config in Locators.ALL.items():
        logger.info(f"\n定位器: {name}")
        logger.info(f"  模板文件: {config.get('template', 'N/A')}")
        logger.info(f"  描述: {config.get('description', 'N/A')}")
        logger.info(f"  阈值: {config.get('threshold', 0.8)}")
        logger.info(f"  区域: {config.get('region', '全屏')}")


def main():
    parser = argparse.ArgumentParser(description="页面操作测试脚本")
    parser.add_argument("--port", type=int, default=7555, help="ADB端口")
    parser.add_argument("--test", choices=["game", "farm", "friend", "all", "locators"],
                        default="all", help="测试类型")
    
    args = parser.parse_args()
    
    if args.test == "game":
        test_game_page(args.port)
    elif args.test == "farm":
        test_farm_page(args.port)
    elif args.test == "friend":
        test_friend_page(args.port)
    elif args.test == "all":
        test_all_pages(args.port)
    elif args.test == "locators":
        list_locators()


if __name__ == "__main__":
    main()