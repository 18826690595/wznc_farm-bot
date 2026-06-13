"""
主入口 V3 - 模块化版本

结构更清晰：
- core/action_base.py      基础操作
- operations/game/         游戏操作
- operations/farm/         农场操作
- operations/blessing/     祝福操作
"""

import sys
import signal
from pathlib import Path

from loguru import logger

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from utils.config import load_config
from utils.logger import setup_logger
from core.device import device_manager
from core.vision import VisionEngine
from core.action_base import ActionBase

# 导入各模块操作
from operations.game import GameOperations
from operations.farm import FarmOperations
from operations.blessing import BlessingOperations


class WZRYFarmBotV3:
    """
    王者荣耀农场自动化 V3
    
    模块化设计，每个功能独立维护
    """
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        # 加载配置
        self.config = load_config(config_path)
        
        # 初始化日志
        setup_logger(log_dir="logs", log_level="INFO")
        
        # 初始化核心组件
        self.vision = VisionEngine()
        self.action = ActionBase(vision=self.vision)
        
        # 初始化各模块操作 ← 按模块拆分
        self.game = GameOperations(self.action)      # 游戏操作
        self.farm = FarmOperations(self.action)      # 农场操作
        self.blessing = BlessingOperations(self.action)  # 祝福操作
        
        # 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        
        self._running = False
        logger.info("机器人初始化完成 (V3 模块化版)")
    
    def _signal_handler(self, signum, frame):
        logger.info("正在停止...")
        self.stop()
        sys.exit(0)
    
    def connect(self) -> bool:
        """连接 MuMu 模拟器"""
        logger.info("连接 MuMu 模拟器...")
        
        if not device_manager.connect(self.config.device.adb_port):
            logger.error("连接失败！")
            return False
        
        logger.success(f"连接成功！")
        return True
    
    def run_once(self):
        """执行一次完整循环"""
        logger.info("=" * 40)
        logger.info("执行单次循环")
        logger.info("=" * 40)
        
        stats = {'harvested': 0, 'planted': 0, 'stolen': 0, 'blessed': 0}
        
        try:
            # 1. 进入游戏
            if not self.game.enter():
                logger.error("无法进入游戏")
                return stats
            
            # 2. 进入农场
            if not self.farm.enter():
                logger.error("无法进入农场")
                return stats
            
            # 3. 收菜
            stats['harvested'] = self.farm.harvest()
            
            # 4. 种菜
            stats['planted'] = self.farm.plant()
            
            # 5. 偷菜
            stats['stolen'] = self.farm.steal(10)
            
            # 6. 祝福
            stats['blessed'] = self.blessing.bless(20)
            
            # 7. 退出
            self.farm.exit()
            
        except Exception as e:
            logger.error(f"执行出错: {e}")
        
        logger.info(f"结果: {stats}")
        return stats
    
    def stop(self):
        """停止"""
        self._running = False
        device_manager.disconnect()
        logger.success("已停止")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="王者荣耀农场自动化 V3")
    parser.add_argument('--once', action='store_true', help='执行一次')
    parser.add_argument('--daemon', type=int, help='守护进程模式')
    
    args = parser.parse_args()
    
    bot = WZRYFarmBotV3()
    
    if not bot.connect():
        return
    
    if args.daemon:
        import time
        bot._running = True
        while bot._running:
            bot.run_once()
            time.sleep(args.daemon)
    else:
        bot.run_once()
    
    bot.stop()


if __name__ == "__main__":
    main()
