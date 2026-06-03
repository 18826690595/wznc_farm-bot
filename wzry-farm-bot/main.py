"""
王者荣耀农场自动化脚本 - 主入口
支持MuMu模拟器，实现自动收菜、种菜、偷菜、祝福
"""
import sys
import signal
import time
from pathlib import Path
from typing import Optional

from loguru import logger

# 添加项目根目录到路径
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from utils.config import load_config, Settings
from utils.logger import setup_logger
from core.device import device_manager
from core.vision import VisionEngine
from core.action import ActionExecutor
from core.state_machine import StateMachine, FarmState
from modules.farm import FarmManager
from modules.blessing import BlessingManager
from modules.scheduler import TaskScheduler


class WZRYFarmBot:
    """
    王者荣耀农场自动化机器人
    整合所有模块，提供统一入口
    """
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        """
        初始化机器人
        
        Args:
            config_path: 配置文件路径
        """
        # 1. 加载配置
        self.config = load_config(config_path)
        
        # 2. 初始化日志
        setup_logger(
            log_dir="logs",
            log_level="INFO"
        )
        
        logger.info("=" * 50)
        logger.info("王者荣耀农场自动化脚本启动")
        logger.info("=" * 50)
        
        # 3. 初始化核心组件
        self.vision = VisionEngine()
        self.state_machine = StateMachine()
        self.action = ActionExecutor(
            vision=self.vision,
            random_delay=self.config.safety.random_delay
        )
        
        # 4. 初始化功能模块
        self.farm = FarmManager(
            vision=self.vision,
            action=self.action,
            state_machine=self.state_machine
        )
        
        self.blessing = BlessingManager(
            vision=self.vision,
            action=self.action,
            state_machine=self.state_machine
        )
        
        self.scheduler = TaskScheduler()
        
        # 5. 状态
        self._running = False
        
        # 6. 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器（优雅退出）"""
        logger.info(f"收到信号 {signum}，正在停止...")
        self.stop()
        sys.exit(0)
    
    def connect(self) -> bool:
        """
        连接MuMu模拟器
        
        Returns:
            是否连接成功
        """
        logger.info("正在连接MuMu模拟器...")
        
        if not device_manager.connect(self.config.device.adb_port):
            logger.error("连接失败！请检查：")
            logger.error("1. MuMu模拟器是否已启动")
            logger.error("2. ADB调试是否已开启")
            logger.error("3. 端口配置是否正确（默认7555）")
            return False
        
        return True
    
    def run_once(self):
        """
        执行一次完整循环
        """
        logger.info("执行单次农场循环...")
        
        # 进入农场
        if not self.action.enter_farm():
            logger.error("无法进入农场")
            return
        
        try:
            # 执行完整循环
            results = self.farm.run_full_cycle(
                crop_name=self.config.farm.default_crop,
                do_steal=self.config.schedule.enable_steal,
                max_steal=self.config.safety.max_steal_per_run
            )
            
            # 祝福
            if self.config.schedule.enable_bless:
                self.blessing.bless_all_friends(
                    self.config.safety.max_bless_per_run
                )
            
            # 输出统计
            logger.info(f"本次执行结果: {results}")
            logger.info(f"总统计: {self.farm.get_stats()}")
            
        finally:
            # 退出农场
            self.action.exit_farm()
    
    def run_scheduled(self):
        """
        运行定时任务模式
        """
        logger.info("启动定时任务模式...")
        
        # 设置任务
        self.scheduler.setup_default_tasks(
            harvest_func=self.farm.harvest_only,
            plant_func=lambda: self.farm.plant_only(self.config.farm.default_crop),
            steal_func=lambda: self.farm.steal_only(self.config.safety.max_steal_per_run),
            bless_func=lambda: self.blessing.bless_all_friends(self.config.safety.max_bless_per_run),
            config={
                'harvest_interval': self.config.farm.harvest_interval if self.config.schedule.enable_harvest else None,
                'steal_interval': self.config.farm.steal_interval if self.config.schedule.enable_steal else None,
                'bless_interval': self.config.farm.bless_interval if self.config.schedule.enable_bless else None,
                'plant_cron': self.config.schedule.plant_cron
            }
        )
        
        # 打印任务
        self.scheduler.print_jobs()
        
        # 启动调度器
        self.scheduler.start()
        self._running = True
        
        logger.success("定时任务已启动，按Ctrl+C停止")
        
        # 主循环
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("用户中断")
        finally:
            self.stop()
    
    def run_daemon(self, interval: int = 300):
        """
        运行守护进程模式（循环执行）
        
        Args:
            interval: 执行间隔（秒）
        """
        logger.info(f"启动守护进程模式，间隔 {interval} 秒...")
        
        self._running = True
        
        try:
            while self._running:
                try:
                    self.run_once()
                except Exception as e:
                    logger.error(f"执行出错: {e}")
                
                logger.info(f"等待 {interval} 秒后继续...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("用户中断")
        finally:
            self.stop()
    
    def stop(self):
        """停止机器人"""
        logger.info("正在停止...")
        
        self._running = False
        
        # 停止调度器
        if self.scheduler.is_running:
            self.scheduler.stop()
        
        # 断开设备
        device_manager.disconnect()
        
        # 停止状态机
        self.state_machine.stop()
        
        logger.success("已停止")
    
    def interactive(self):
        """交互模式"""
        print("\n" + "=" * 50)
        print("王者荣耀农场自动化 - 交互模式")
        print("=" * 50)
        print("\n命令列表:")
        print("  1 - 执行一次完整循环")
        print("  2 - 仅收菜")
        print("  3 - 仅种菜")
        print("  4 - 仅偷菜")
        print("  5 - 仅祝福")
        print("  6 - 查看统计")
        print("  7 - 查看状态")
        print("  0 - 退出")
        print()
        
        while True:
            try:
                cmd = input("请输入命令: ").strip()
                
                if cmd == "1":
                    self.run_once()
                elif cmd == "2":
                    self.farm.harvest_only()
                elif cmd == "3":
                    self.farm.plant_only(self.config.farm.default_crop)
                elif cmd == "4":
                    self.farm.steal_only(self.config.safety.max_steal_per_run)
                elif cmd == "5":
                    self.blessing.bless_all_friends(self.config.safety.max_bless_per_run)
                elif cmd == "6":
                    print(f"\n农场统计: {self.farm.get_stats()}")
                    print(f"祝福统计: {self.blessing.get_bless_status()}\n")
                elif cmd == "7":
                    print(f"\n状态机: {self.state_machine.state.name}")
                    print(f"设备: {'已连接' if device_manager.is_connected else '未连接'}\n")
                elif cmd == "0":
                    print("再见！")
                    break
                else:
                    print("未知命令")
                    
            except KeyboardInterrupt:
                print("\n退出交互模式")
                break
            except Exception as e:
                logger.error(f"命令执行失败: {e}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="王者荣耀农场自动化脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py --once                  # 执行一次
  python main.py --schedule              # 定时任务模式
  python main.py --daemon 300            # 守护进程模式，间隔300秒
  python main.py --interactive           # 交互模式
        """
    )
    
    parser.add_argument('--once', action='store_true', help='执行一次完整循环')
    parser.add_argument('--schedule', action='store_true', help='定时任务模式')
    parser.add_argument('--daemon', type=int, metavar='INTERVAL', help='守护进程模式')
    parser.add_argument('--interactive', action='store_true', help='交互模式')
    parser.add_argument('--config', type=str, default='config/settings.yaml', help='配置文件路径')
    
    args = parser.parse_args()
    
    # 创建机器人
    bot = WZRYFarmBot(config_path=args.config)
    
    # 连接设备
    if not bot.connect():
        sys.exit(1)
    
    # 选择模式
    if args.once:
        bot.run_once()
    elif args.schedule:
        bot.run_scheduled()
    elif args.daemon:
        bot.run_daemon(args.daemon)
    elif args.interactive:
        bot.interactive()
    else:
        # 默认：执行一次
        bot.run_once()
    
    # 清理
    bot.stop()


if __name__ == "__main__":
    main()
