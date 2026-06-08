"""
王者荣耀农场自动化脚本 V2 - 更清晰的骨架结构
"""

import sys
import signal
from pathlib import Path
from typing import Optional

from loguru import logger

ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from utils.config import load_config
from utils.logger import setup_logger
from core.device import device_manager
from core.vision import VisionEngine
from core.action_v2 import ActionExecutorV2
from core.state_machine import StateMachine, FarmState
from config.template_config import template_config
from config.operation_definitions import OperationDefinitions


class WZRYFarmBotV2:
    """
    王者荣耀农场自动化机器人 V2
    
    骨架已搭建好，你需要填充：
    1. config/images/ 目录下的模板图片
    2. config/operation_definitions.py 中的操作步骤
    """
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """初始化"""
        # 1. 加载配置
        self.config = load_config(config_path)
        
        # 2. 初始化日志
        setup_logger(log_dir="logs", log_level="INFO")
        
        # 3. 打印骨架状态
        self._print_status()
        
        # 4. 初始化核心组件
        self.vision = VisionEngine()
        self.state_machine = StateMachine()
        self.action = ActionExecutorV2(
            vision=self.vision,
            random_delay=self.config.safety.random_delay
        )
        
        # 5. 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        self._running = False
        logger.info("机器人初始化完成")
    
    def _print_status(self):
        """打印骨架状态"""
        print("\n" + "=" * 60)
        print("王者荣耀农场自动化 - 骨架状态检查")
        print("=" * 60)
        
        # 模板状态
        template_config.print_status()
        
        # 操作定义
        print("\n操作流程定义:")
        OperationDefinitions.print_operations()
        
        print("\n下一步:")
        missing = template_config.list_missing()
        if missing:
            print("❌ 请先添加模板图片:")
            for name in missing:
                info = template_config.TEMPLATES.get(name)
                if info:
                    print(f"   - config/images/{info.filename} : {info.description}")
            print("\n   制作方法:")
            print("   1. 使用 MuMu 截图功能截取游戏画面")
            print("   2. 用图片工具裁剪出按钮/图标")
            print("   3. 保存为 PNG 格式")
        else:
            print("✅ 所有模板已就绪，可以开始运行！")
        
        print("=" * 60 + "\n")
    
    def _signal_handler(self, signum, frame):
        """信号处理"""
        logger.info(f"收到信号 {signum}，正在停止...")
        self.stop()
        sys.exit(0)
    
    def connect(self) -> bool:
        """连接 MuMu 模拟器"""
        logger.info("连接 MuMu 模拟器...")
        
        if not device_manager.connect(self.config.device.adb_port):
            logger.error("连接失败！请检查：")
            logger.error("  1. MuMu 模拟器是否启动")
            logger.error("  2. ADB 调试是否开启")
            logger.error("  3. 端口是否正确（默认 7555）")
            return False
        
        logger.success(f"连接成功！设备: {device_manager.screen_size}")
        return True
    
    def run_once(self):
        """执行一次完整循环"""
        logger.info("=" * 40)
        logger.info("执行单次农场循环")
        logger.info("=" * 40)
        
        stats = {
            'harvested': 0,
            'planted': 0,
            'stolen': 0,
            'blessed': 0
        }
        
        try:
            # 0. 进入游戏（新增）
            if not self.action.enter_game():
                logger.error("无法进入游戏")
                return stats
            
            # 1. 进入农场
            if not self.action.enter_farm():
                logger.error("无法进入农场")
                return stats
            
            # 2. 收菜
            if self.config.schedule.enable_harvest:
                stats['harvested'] = self.action.harvest()
            
            # 3. 种菜
            if self.config.schedule.enable_plant:
                stats['planted'] = self.action.plant(
                    self.config.farm.default_crop
                )
            
            # 4. 偷菜
            if self.config.schedule.enable_steal:
                stats['stolen'] = self.action.steal(
                    self.config.safety.max_steal_per_run
                )
            
            # 5. 祝福
            if self.config.schedule.enable_bless:
                stats['blessed'] = self.action.bless(
                    self.config.safety.max_bless_per_run
                )
            
            # 6. 退出农场
            self.action.exit_farm()
            
        except Exception as e:
            logger.error(f"执行出错: {e}")
            self.action.exit_farm()
        
        logger.info(f"执行结果: {stats}")
        return stats
    
    def run_daemon(self, interval: int = 300):
        """守护进程模式"""
        logger.info(f"启动守护进程，间隔 {interval} 秒...")
        
        self._running = True
        while self._running:
            try:
                self.run_once()
            except Exception as e:
                logger.error(f"执行出错: {e}")
            
            logger.info(f"等待 {interval} 秒...")
            import time
            time.sleep(interval)
    
    def stop(self):
        """停止"""
        self._running = False
        device_manager.disconnect()
        self.state_machine.stop()
        logger.success("已停止")


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="王者荣耀农场自动化 V2")
    parser.add_argument('--once', action='store_true', help='执行一次')
    parser.add_argument('--daemon', type=int, metavar='INTERVAL', help='守护进程模式')
    parser.add_argument('--check', action='store_true', help='仅检查骨架状态')
    parser.add_argument('--config', type=str, default='config/settings.yaml')
    
    args = parser.parse_args()
    
    # 仅检查
    if args.check:
        template_config.print_status()
        OperationDefinitions.print_operations()
        return
    
    # 创建机器人
    bot = WZRYFarmBotV2(config_path=args.config)
    
    # 检查模板
    if template_config.list_missing():
        print("\n❌ 缺少模板图片，请先添加！")
        print("   运行 python main_v2.py --check 查看详情")
        return
    
    # 连接
    if not bot.connect():
        return
    
    # 运行
    if args.daemon:
        bot.run_daemon(args.daemon)
    else:
        bot.run_once()
    
    bot.stop()


if __name__ == "__main__":
    main()
