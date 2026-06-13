"""
单元测试 - 验证项目结构和导入
"""
import sys
from pathlib import Path

# 添加项目根目录
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


def test_imports():
    """测试所有模块导入"""
    print("测试模块导入...")
    
    try:
        # 核心模块
        from core.device import DeviceManager, device_manager
        from core.vision import VisionEngine
        from core.action import ActionExecutor
        from core.state_machine import StateMachine, FarmState
        print("✓ 核心模块导入成功")
    except ImportError as e:
        print(f"✗ 核心模块导入失败: {e}")
        return False
    
    try:
        # 功能模块
        from modules.farm import FarmManager
        from modules.blessing import BlessingManager
        from modules.scheduler import TaskScheduler
        print("✓ 功能模块导入成功")
    except ImportError as e:
        print(f"✗ 功能模块导入失败: {e}")
        return False
    
    try:
        # 工具模块
        from utils.config import load_config, Settings
        from utils.logger import setup_logger
        print("✓ 工具模块导入成功")
    except ImportError as e:
        print(f"✗ 工具模块导入失败: {e}")
        return False
    
    return True


def test_config():
    """测试配置加载"""
    print("\n测试配置加载...")
    
    from utils.config import load_config
    
    config = load_config("config/settings.yaml")
    
    print(f"✓ 配置加载成功")
    print(f"  - ADB端口: {config.device.adb_port}")
    print(f"  - 收菜间隔: {config.farm.harvest_interval}秒")
    print(f"  - 随机延迟: {config.safety.random_delay}")
    
    return True


def test_state_machine():
    """测试状态机"""
    print("\n测试状态机...")
    
    from core.state_machine import StateMachine, FarmState
    
    sm = StateMachine()
    
    print(f"✓ 初始状态: {sm.state.name}")
    
    # 测试状态转换
    if sm.can_transition_to(FarmState.HARVESTING):
        sm.transition_to(FarmState.HARVESTING)
        print(f"✓ 转换到: {sm.state.name}")
        
        sm.transition_to(FarmState.IDLE)
        print(f"✓ 返回到: {sm.state.name}")
    
    return True


def test_scheduler():
    """测试调度器"""
    print("\n测试调度器...")
    
    from modules.scheduler import TaskScheduler
    
    scheduler = TaskScheduler()
    
    # 添加测试任务
    def test_job():
        print("  [任务执行] 测试任务运行")
    
    scheduler.add_interval_job(
        job_id="test",
        func=test_job,
        interval=5,
        unit='seconds'
    )
    
    jobs = scheduler.get_jobs()
    print(f"✓ 添加任务成功: {list(jobs.keys())}")
    
    return True


def main():
    """运行所有测试"""
    print("=" * 60)
    print("王者荣耀农场自动化 - 项目测试")
    print("=" * 60)
    
    results = []
    
    # 执行测试
    results.append(("模块导入", test_imports()))
    results.append(("配置加载", test_config()))
    results.append(("状态机", test_state_machine()))
    results.append(("调度器", test_scheduler()))
    
    # 输出结果
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print("-" * 60)
    
    all_passed = True
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name:15s} {status}")
        if not result:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓ 所有测试通过！项目结构正确。")
        print("\n下一步：")
        print("1. 准备模板图片到 config/images/")
        print("2. 启动MuMu模拟器并开启ADB调试")
        print("3. 运行: python main.py --once")
    else:
        print("\n✗ 部分测试失败，请检查依赖安装。")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
