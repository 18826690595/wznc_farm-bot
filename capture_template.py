#!/usr/bin/env python3
"""
模板截图脚本
用于截图保存模板图片到 config/templates/ 目录

使用方式：
    python capture_template.py

然后在交互界面输入参数即可
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.device import device_manager
from tools.template_capture import template_capture
from loguru import logger


def connect_device():
    """连接设备"""
    print("\n=== 连接设备 ===")
    port = input("ADB端口 (默认7555): ").strip() or "7555"
    
    try:
        device_manager.connect(int(port))
        print(f"✓ 已连接设备: 127.0.0.1:{port}")
        return True
    except Exception as e:
        print(f"✗ 连接失败: {e}")
        return False


def capture_page_template():
    """截图保存页面模板"""
    print("\n=== 截图保存页面模板 ===")
    
    name = input("模板名称 (如 main_page): ").strip()
    if not name:
        print("✗ 名称不能为空")
        return
    
    # 是否验证匹配
    verify = input("是否验证匹配? (y/n, 默认n): ").strip().lower() == 'y'
    
    # 是否覆盖
    overwrite = input("是否覆盖已存在的模板? (y/n, 默认n): ").strip().lower() == 'y'
    
    # 执行截图
    success, msg = template_capture.capture_page(
        name=name,
        verify_match=verify,
        overwrite=overwrite
    )
    
    if success:
        print(f"✓ {msg}")
    else:
        print(f"✗ {msg}")


def capture_button_template():
    """截图保存按钮模板"""
    print("\n=== 截图保存按钮模板 ===")
    
    name = input("模板名称 (如 harvest_btn): ").strip()
    if not name:
        print("✗ 名称不能为空")
        return
    
    # 截图区域
    region_str = input("截图区域 (x1,y1,x2,y2, 全屏直接回车): ").strip()
    region = None
    if region_str:
        try:
            region = tuple(map(int, region_str.split(",")))
        except:
            print("✗ 区域格式错误，应为: x1,y1,x2,y2")
            return
    
    # 是否验证匹配
    verify = input("是否验证匹配? (y/n, 默认n): ").strip().lower() == 'y'
    
    # 是否覆盖
    overwrite = input("是否覆盖已存在的模板? (y/n, 默认n): ").strip().lower() == 'y'
    
    # 执行截图
    success, msg = template_capture.capture_button(
        name=name,
        region=region,
        verify_match=verify,
        overwrite=overwrite
    )
    
    if success:
        print(f"✓ {msg}")
    else:
        print(f"✗ {msg}")


def list_templates():
    """列出所有模板"""
    print("\n=== 模板列表 ===")
    
    pages_dir = project_root / "config" / "templates" / "pages"
    buttons_dir = project_root / "config" / "templates" / "buttons"
    
    print("\n页面模板:")
    if pages_dir.exists():
        files = list(pages_dir.glob("*.png"))
        if files:
            for f in files:
                print(f"  - {f.name}")
        else:
            print("  (无)")
    else:
        print("  (目录不存在)")
    
    print("\n按钮模板:")
    if buttons_dir.exists():
        files = list(buttons_dir.glob("*.png"))
        if files:
            for f in files:
                print(f"  - {f.name}")
        else:
            print("  (无)")
    else:
        print("  (目录不存在)")


def delete_template():
    """删除模板"""
    print("\n=== 删除模板 ===")
    
    template_type = input("模板类型 (page/button): ").strip().lower()
    if template_type not in ['page', 'button']:
        print("✗ 类型只能是 page 或 button")
        return
    
    name = input("模板名称: ").strip()
    if not name:
        print("✗ 名称不能为空")
        return
    
    success, msg = template_capture.delete_template(name, template_type)
    
    if success:
        print(f"✓ {msg}")
    else:
        print(f"✗ {msg}")


def interactive_mode():
    """交互模式"""
    print("\n" + "=" * 50)
    print("   王者荣耀农场 - 模板截图工具")
    print("=" * 50)
    
    while True:
        print("\n请选择操作:")
        print("  1. 截图保存页面模板 (全屏)")
        print("  2. 截图保存按钮模板 (指定区域)")
        print("  3. 查看模板列表")
        print("  4. 删除模板")
        print("  5. 重新连接设备")
        print("  0. 退出")
        
        choice = input("\n请输入选项 (0-5): ").strip()
        
        if choice == '0':
            print("\n再见！")
            break
        elif choice == '1':
            capture_page_template()
        elif choice == '2':
            capture_button_template()
        elif choice == '3':
            list_templates()
        elif choice == '4':
            delete_template()
        elif choice == '5':
            connect_device()
        else:
            print("✗ 无效选项")


def main():
    """主入口"""
    # 先连接设备
    if not connect_device():
        print("\n无法连接设备，请检查:")
        print("  1. MuMu模拟器是否启动")
        print("  2. ADB调试是否开启")
        print("  3. ADB端口是否正确")
        return
    
    # 进入交互模式
    interactive_mode()


if __name__ == "__main__":
    main()