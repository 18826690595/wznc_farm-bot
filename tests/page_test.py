"""
页面操作测试脚本

用于测试各页面的操作功能，验证页面流程是否正确

使用方式：
# 测试进入游戏
python tests/page_test.py --port 7555 --test enter_game

# 测试进入农场
python tests/page_test.py --port 7555 --test enter_farm

# 测试收菜
python tests/page_test.py --port 7555 --test harvest

# 测试完整流程
python tests/page_test.py --port 7555 --test full_cycle

# 测试所有页面操作
python tests/page_test.py --port 7555 --test all
"""

import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from core.driver import Driver
from pages.game_page import GamePage
from pages.farm_page import FarmPage
from pages.friend_page import FriendPage


class PageTester:
    """页面操作测试器"""
    
    def __init__(self, port: int = 7555):
        self.driver = Driver()
        self.driver.connect(port)
        
        self.game_page = GamePage(self.driver)
        self.farm_page = FarmPage(self.driver)
        self.friend_page = FriendPage(self.driver)
        
        logger.info("页面测试器已初始化")
    
    def test_enter_game(self) -> bool:
        """测试进入游戏"""
        logger.info("=" * 50)
        logger.info("测试: 进入游戏")
        logger.info("=" * 50)
        
        result = self.game_page.enter_game()
        logger.info(f"结果: {'成功' if result else '失败'}")
        return result
    
    def test_exit_game(self) -> bool:
        """测试退出游戏"""
        logger.info("=" * 50)
        logger.info("测试: 退出游戏")
        logger.info("=" * 50)
        
        result = self.game_page.exit_game()
        logger.info(f"结果: {'成功' if result else '失败'}")
        return result
    
    def test_enter_farm(self) -> bool:
        """测试进入农场"""
        logger.info("=" * 50)
        logger.info("测试: 进入农场")
        logger.info("=" * 50)
        
        result = self.game_page.enter_farm()
        logger.info(f"结果: {'成功' if result else '失败'}")
        return result
    
    def test_exit_farm(self) -> bool:
        """测试退出农场"""
        logger.info("=" * 50)
        logger.info("测试: 退出农场")
        logger.info("=" * 50)
        
        result = self.farm_page.exit_farm()
        logger.info(f"结果: {'成功' if result else '失败'}")
        return result
    
    def test_harvest(self) -> int:
        """测试收菜"""
        logger.info("=" * 50)
        logger.info("测试: 收菜")
        logger.info("=" * 50)
        
        count = self.farm_page.harvest_all()
        logger.info(f"结果: 收获 {count} 个作物")
        return count
    
    def test_plant(self, crop: str = "default") -> int:
        """测试种菜"""
        logger.info("=" * 50)
        logger.info(f"测试: 种菜 (作物: {crop})")
        logger.info("=" * 50)
        
        count = self.farm_page.plant_all_empty(crop)
        logger.info(f"结果: 种植 {count} 个作物")
        return count
    
    def test_steal(self, max_count: int = 10) -> int:
        """测试偷菜"""
        logger.info("=" * 50)
        logger.info(f"测试: 偷菜 (最多: {max_count})")
        logger.info("=" * 50)
        
        count = self.farm_page.steal_from_friends(max_count)
        logger.info(f"结果: 偷取 {count} 个作物")
        return count
    
    def test_bless(self, max_count: int = 10) -> int:
        """测试祝福"""
        logger.info("=" * 50)
        logger.info(f"测试: 祝福 (最多: {max_count})")
        logger.info("=" * 50)
        
        count = self.friend_page.bless_all(max_count)
        logger.info(f"结果: 祝福 {count} 个好友")
        return count
    
    def test_full_cycle(self) -> dict:
        """测试完整流程"""
        logger.info("=" * 50)
        logger.info("测试: 完整流程")
        logger.info("=" * 50)
        
        results = {
            "enter_game": False,
            "enter_farm": False,
            "harvest": 0,
            "plant": 0,
            "steal": 0,
            "exit_farm": False,
        }
        
        # 1. 进入游戏
        results["enter_game"] = self.game_page.enter_game()
        if not results["enter_game"]:
            logger.error("进入游戏失败，流程终止")
            return results
        
        # 2. 进入农场
        results["enter_farm"] = self.game_page.enter_farm()
        if not results["enter_farm"]:
            logger.error("进入农场失败，流程终止")
            return results
        
        # 3. 收菜
        results["harvest"] = self.farm_page.harvest_all()
        
        # 4. 种菜
        results["plant"] = self.farm_page.plant_all_empty()
        
        # 5. 偷菜
        results["steal"] = self.farm_page.steal_from_friends(10)
        
        # 6. 退出农场
        results["exit_farm"] = self.farm_page.exit_farm()
        
        logger.info(f"完整流程结果: {results}")
        return results
    
    def test_all(self):
        """运行所有测试"""
        logger.info("=" * 50)
        logger.info("运行所有页面测试")
        logger.info("=" * 50)
        
        tests = [
            ("进入游戏", self.test_enter_game),
            ("进入农场", self.test_enter_farm),
            ("收菜", self.test_harvest),
            ("种菜", lambda: self.test_plant()),
            ("偷菜", lambda: self.test_steal()),
            ("退出农场", self.test_exit_farm),
        ]
        
        results = []
        for name, test_func in tests:
            try:
                result = test_func()
                results.append((name, "成功", result))
            except Exception as e:
                results.append((name, "失败", str(e)))
            
            # 每个测试间隔2秒
            import time
            time.sleep(2)
        
        # 打印汇总
        logger.info("=" * 50)
        logger.info("测试汇总:")
        for name, status, result in results:
            logger.info(f"  {name}: {status} - {result}")
        logger.info("=" * 50)
        
        return results
    
    def close(self):
        """关闭连接"""
        self.driver.disconnect()
        logger.info("测试器已关闭")


def main():
    parser = argparse.ArgumentParser(description="页面操作测试脚本")
    parser.add_argument("--port", type=int, default=7555, help="ADB端口")
    parser.add_argument("--test", type=str, default="all", 
                       choices=["enter_game", "exit_game", "enter_farm", "exit_farm", 
                               "harvest", "plant", "steal", "bless", "full_cycle", "all"],
                       help="测试类型")
    parser.add_argument("--crop", type=str, default="default", help="种植作物类型")
    parser.add_argument("--max-steal", type=int, default=10, help="最大偷菜数量")
    parser.add_argument("--max-bless", type=int, default=10, help="最大祝福数量")
    
    args = parser.parse_args()
    
    # 初始化测试器
    tester = PageTester(args.port)
    
    try:
        # 运行测试
        if args.test == "all":
            tester.test_all()
        elif args.test == "enter_game":
            tester.test_enter_game()
        elif args.test == "exit_game":
            tester.test_exit_game()
        elif args.test == "enter_farm":
            tester.test_enter_farm()
        elif args.test == "exit_farm":
            tester.test_exit_farm()
        elif args.test == "harvest":
            tester.test_harvest()
        elif args.test == "plant":
            tester.test_plant(args.crop)
        elif args.test == "steal":
            tester.test_steal(args.max_steal)
        elif args.test == "bless":
            tester.test_bless(args.max_bless)
        elif args.test == "full_cycle":
            tester.test_full_cycle()
        
    finally:
        tester.close()


if __name__ == "__main__":
    main()