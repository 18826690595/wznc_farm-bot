"""
项目结构验证脚本（无需安装依赖）
"""
from pathlib import Path
import sys

def check_structure():
    """检查项目结构"""
    print("\n" + "=" * 60)
    print("项目结构验证")
    print("=" * 60)
    
    required_files = {
        '核心文件': [
            'main.py',
            'main_v2.py',
            'requirements.txt',
            '.coze',
            'README.md',
            'AGENTS.md',
            'FILLING_GUIDE.md',
        ],
        '核心模块 (core/)': [
            'core/__init__.py',
            'core/device.py',
            'core/vision.py',
            'core/action.py',
            'core/action_v2.py',
            'core/state_machine.py',
        ],
        '功能模块 (modules/)': [
            'modules/__init__.py',
            'modules/farm.py',
            'modules/blessing.py',
            'modules/scheduler.py',
        ],
        '工具模块 (utils/)': [
            'utils/__init__.py',
            'utils/config.py',
            'utils/logger.py',
        ],
        '配置文件 (config/)': [
            'config/settings.yaml',
            'config/template_config.py',
            'config/operation_definitions.py',
        ],
    }
    
    all_ok = True
    
    for category, files in required_files.items():
        print(f"\n{category}:")
        for f in files:
            path = Path(f)
            if path.exists():
                print(f"  ✓ {f}")
            else:
                print(f"  ✗ {f} (缺失)")
                all_ok = False
    
    # 检查模板图片目录
    print(f"\n模板图片目录 (config/images/):")
    images_dir = Path("config/images")
    if images_dir.exists():
        images = list(images_dir.glob("*.png"))
        if images:
            for img in images:
                print(f"  ✓ {img.name}")
        else:
            print("  ⚠ 暂无模板图片（需要你添加）")
    else:
        print("  ✗ 目录不存在")
    
    # 检查日志目录
    print(f"\n日志目录 (logs/):")
    logs_dir = Path("logs")
    if logs_dir.exists():
        print("  ✓ logs/")
    else:
        print("  ⚠ logs/ 不存在（运行时自动创建）")
    
    print("\n" + "=" * 60)
    
    if all_ok:
        print("✓ 项目结构完整！")
        print("\n下一步：")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 添加模板图片到 config/images/")
        print("3. 根据需要修改 config/operation_definitions.py")
        print("4. 运行: python main_v2.py --once")
        return 0
    else:
        print("✗ 部分文件缺失，请检查！")
        return 1


def print_quick_start():
    """打印快速开始指南"""
    print("\n" + "=" * 60)
    print("快速开始指南")
    print("=" * 60)
    
    print("""
步骤 1: 安装依赖
-------------------
pip install -r requirements.txt


步骤 2: 准备模板图片
-------------------
1) 启动 MuMu 模拟器
2) 进入王者荣耀农场
3) 截取以下按钮图片：
   - farm_icon.png      : 农场入口图标
   - harvest_btn.png    : 收获按钮
   - plant_btn.png      : 种植按钮
   - friend_list_btn.png: 好友列表
   - steal_btn.png      : 偷菜按钮
   - bless_btn.png      : 祝福按钮
4) 保存到 config/images/ 目录


步骤 3: 配置操作步骤（可选）
-------------------
如果默认流程不符合你的游戏界面，
修改 config/operation_definitions.py


步骤 4: 运行测试
-------------------
# 检查状态
python main_v2.py --check

# 执行一次
python main_v2.py --once

# 守护进程
python main_v2.py --daemon 300


配置文件: config/settings.yaml
填充指南: FILLING_GUIDE.md
    """)


def main():
    root = Path(__file__).parent
    if str(root) != str(Path.cwd()):
        print(f"切换到项目目录: {root}")
        import os
        os.chdir(root)
    
    result = check_structure()
    
    if result == 0:
        print_quick_start()
    
    return result


if __name__ == "__main__":
    sys.exit(main())
