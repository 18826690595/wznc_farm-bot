"""
模板截图工具 - 全自动版本
所有参数通过调用时传入，不需要手动输入
"""

import argparse
import sys
from typing import Optional, Tuple

from tools.template_capture import template_capture
from core.device import device_manager


def connect_device(port: int = 7555) -> bool:
    """连接设备"""
    print(f"=== 连接设备 ===")
    print(f"ADB端口: {port}")
    success = device_manager.connect(port)
    if success:
        print(f"✓ 已连接设备: 127.0.0.1:{port}")
    else:
        print(f"✗ 连接失败")
    return success


def capture_page(
    name: str,
    port: int = 7555,
    verify_match: bool = False,
    overwrite: bool = False,
) -> Tuple[bool, str]:
    """
    截图保存页面模板（全屏）
    
    参数:
        name: 模板名称
        port: ADB端口，默认7555
        verify_match: 是否验证匹配
        overwrite: 是否覆盖已存在的模板
    """
    if not connect_device(port):
        return False, "设备连接失败"
    
    print(f"\n=== 截图保存页面模板 ===")
    print(f"模板名称: {name}")
    print(f"验证匹配: {verify_match}")
    print(f"覆盖已存在: {overwrite}")
    
    success, msg = template_capture.capture_page(
        name=name,
        verify_match=verify_match,
        overwrite=overwrite,
    )
    print(f"结果: {msg}")
    return success, msg


def capture_button(
    name: str,
    region: Optional[Tuple[int, int, int, int]] = None,
    port: int = 7555,
    verify_match: bool = False,
    overwrite: bool = False,
    threshold: float = 0.8,
) -> Tuple[bool, str]:
    """
    截图保存按钮模板（指定区域）
    
    参数:
        name: 模板名称
        region: 截图区域 (x1,y1,x2,y2)，None表示全屏
        port: ADB端口，默认7555
        verify_match: 是否验证匹配
        overwrite: 是否覆盖已存在的模板
        threshold: 匹配阈值
    """
    if not connect_device(port):
        return False, "设备连接失败"
    
    print(f"\n=== 截图保存按钮模板 ===")
    print(f"模板名称: {name}")
    print(f"截图区域: {region if region else '全屏'}")
    print(f"验证匹配: {verify_match}")
    print(f"覆盖已存在: {overwrite}")
    
    success, msg = template_capture.capture_button(
        name=name,
        region=region,
        verify_match=verify_match,
        overwrite=overwrite,
        threshold=threshold,
    )
    print(f"结果: {msg}")
    return success, msg


def list_templates() -> None:
    """列出所有模板"""
    template_capture.list_templates()


def delete_template(template_type: str, name: str) -> Tuple[bool, str]:
    """
    删除模板
    
    参数:
        template_type: 模板类型 (page/button)
        name: 模板名称
    """
    success, msg = template_capture.delete_template(template_type, name)
    print(f"结果: {msg}")
    return success, msg


def batch_capture(
    templates: list,
    port: int = 7555,
) -> None:
    """
    批量截图
    
    参数:
        templates: 模板列表，每个元素是字典
            [{"type": "page", "name": "xxx", "region": (x1,y1,x2,y2), "verify": True}, ...]
        port: ADB端口
    """
    if not connect_device(port):
        print("设备连接失败，批量截图终止")
        return
    
    print(f"\n=== 批量截图 ({len(templates)}个模板) ===")
    
    for i, item in enumerate(templates, 1):
        print(f"\n[{i}/{len(templates)}]")
        
        template_type = item.get("type", "button")
        name = item.get("name")
        region = item.get("region")
        verify = item.get("verify", False)
        overwrite = item.get("overwrite", False)
        
        if not name:
            print("✗ 缺少模板名称，跳过")
            continue
        
        if template_type == "page":
            capture_page(name, port, verify, overwrite)
        else:
            capture_button(name, region, port, verify, overwrite)


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="模板截图工具 - 全自动版本")
    
    # 基础参数
    parser.add_argument("--port", type=int, default=7555, help="ADB端口，默认7555")
    
    # 操作类型
    subparsers = parser.add_subparsers(dest="action", help="操作类型")
    
    # 截图页面模板
    page_parser = subparsers.add_parser("page", help="截图页面模板")
    page_parser.add_argument("name", help="模板名称")
    page_parser.add_argument("--verify", action="store_true", help="验证匹配")
    page_parser.add_argument("--overwrite", action="store_true", help="覆盖已存在")
    
    # 截图按钮模板
    button_parser = subparsers.add_parser("button", help="截图按钮模板")
    button_parser.add_argument("name", help="模板名称")
    button_parser.add_argument("--region", type=str, help="截图区域 x1,y1,x2,y2")
    button_parser.add_argument("--verify", action="store_true", help="验证匹配")
    button_parser.add_argument("--overwrite", action="store_true", help="覆盖已存在")
    
    # 列出模板
    subparsers.add_parser("list", help="列出所有模板")
    
    # 删除模板
    delete_parser = subparsers.add_parser("delete", help="删除模板")
    delete_parser.add_argument("type", choices=["page", "button"], help="模板类型")
    delete_parser.add_argument("name", help="模板名称")
    
    args = parser.parse_args()
    
    if args.action == "page":
        capture_page(args.name, args.port, args.verify, args.overwrite)
    
    elif args.action == "button":
        region = None
        if args.region:
            region = tuple(map(int, args.region.split(",")))
        capture_button(args.name, region, args.port, args.verify, args.overwrite)
    
    elif args.action == "list":
        list_templates()
    
    elif args.action == "delete":
        delete_template(args.type, args.name)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()