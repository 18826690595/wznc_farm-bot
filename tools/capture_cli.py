"""
模板截图 CLI 工具

使用方法:
    python tools/capture_cli.py page <名称> [--verify] [--overwrite]
    python tools/capture_cli.py button <名称> [--region "x1,y1,x2,y2"] [--verify] [--overwrite]
    python tools/capture_cli.py list
    python tools/capture_cli.py delete <类型> <名称>
"""
import argparse
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.template_capture import template_capture
from core.device import device_manager
from loguru import logger


def main():
    parser = argparse.ArgumentParser(
        description="模板截图工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 实例1：截图保存当前页面图片至页面模板目录
    python tools/capture_cli.py page main_page
    
    # 实例2：截图保存按钮图片至按钮模板目录（指定区域）
    python tools/capture_cli.py button harvest_btn --region "100,200,300,400"
    
    # 实例3：截图保存并验证匹配
    python tools/capture_cli.py button login_btn --verify
    
    # 实例4：强制覆盖已存在的模板
    python tools/capture_cli.py page main_page --overwrite
    
    # 列出所有模板
    python tools/capture_cli.py list
    
    # 删除模板
    python tools/capture_cli.py delete button harvest_btn
        """
    )
    
    parser.add_argument(
        "action",
        choices=["page", "button", "list", "delete"],
        help="操作类型: page(页面模板), button(按钮模板), list(列出), delete(删除)"
    )
    
    parser.add_argument(
        "name",
        nargs="?",
        help="模板名称"
    )
    
    parser.add_argument(
        "--region",
        type=str,
        default=None,
        help="截图区域: 'x1,y1,x2,y2' 或 '10%,20%,50%,80%'"
    )
    
    parser.add_argument(
        "--verify",
        action="store_true",
        help="是否验证匹配（截图后验证能否匹配到）"
    )
    
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="是否覆盖已存在的模板"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=7555,
        help="ADB端口（默认7555）"
    )
    
    args = parser.parse_args()
    
    # 连接设备
    if args.action in ["page", "button"]:
        logger.info(f"连接设备: 127.0.0.1:{args.port}")
        if not device_manager.connect(args.port):
            logger.error("设备连接失败")
            sys.exit(1)
        logger.success("设备连接成功")
    
    # 执行操作
    if args.action == "page":
        # 截图保存页面模板
        if not args.name:
            logger.error("请指定模板名称")
            sys.exit(1)
        
        success, msg = template_capture.capture_page(
            name=args.name,
            verify_match=args.verify,
            overwrite=args.overwrite
        )
        
        if success:
            logger.success(f"页面模板保存成功: {msg}")
        else:
            logger.error(msg)
            sys.exit(1)
    
    elif args.action == "button":
        # 截图保存按钮模板
        if not args.name:
            logger.error("请指定模板名称")
            sys.exit(1)
        
        success, msg = template_capture.capture_button(
            name=args.name,
            region=args.region,
            verify_match=args.verify,
            overwrite=args.overwrite
        )
        
        if success:
            logger.success(f"按钮模板保存成功: {msg}")
        else:
            logger.error(msg)
            sys.exit(1)
    
    elif args.action == "list":
        # 列出所有模板
        templates = template_capture.list_templates()
        
        print("\n模板列表:")
        print("=" * 40)
        
        if templates["pages"]:
            print(f"\n页面模板 ({len(templates['pages'])} 个):")
            for name in templates["pages"]:
                print(f"  - {name}")
        else:
            print("\n页面模板: 无")
        
        if templates["buttons"]:
            print(f"\n按钮模板 ({len(templates['buttons'])} 个):")
            for name in templates["buttons"]:
                print(f"  - {name}")
        else:
            print("\n按钮模板: 无")
        
        print("=" * 40)
    
    elif args.action == "delete":
        # 删除模板
        if not args.name:
            logger.error("请指定模板名称")
            sys.exit(1)
        
        template_type = args.name  # 第二个参数是类型
        if args.action == "delete" and len(sys.argv) < 4:
            logger.error("用法: capture_cli.py delete <类型> <名称>")
            sys.exit(1)
        
        template_name = sys.argv[3]  # 第三个参数是名称
        
        success, msg = template_capture.delete_template(template_name, template_type)
        
        if success:
            logger.success(msg)
        else:
            logger.error(msg)
            sys.exit(1)


if __name__ == "__main__":
    main()