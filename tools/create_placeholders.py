"""
示例模板图片生成脚本

这个脚本会生成示例占位图，帮助你了解模板尺寸
实际使用时请用真实游戏截图替换
"""

import cv2
import numpy as np
from pathlib import Path


def create_placeholder(filename: str, width: int, height: int, text: str):
    """创建占位图"""
    # 创建彩色图片
    img = np.ones((height, width, 3), dtype=np.uint8) * 240  # 灰色背景
    
    # 添加文字
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, 0.5, 1)[0]
    text_x = (width - text_size[0]) // 2
    text_y = (height + text_size[1]) // 2
    cv2.putText(img, text, (text_x, text_y), font, 0.5, (100, 100, 100), 1)
    
    # 添加边框
    cv2.rectangle(img, (0, 0), (width-1, height-1), (200, 200, 200), 1)
    
    return img


def main():
    output_dir = Path("config/images")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("生成示例占位图...")
    print("=" * 50)
    print("注意：这些是占位图，请用真实截图替换！")
    print("=" * 50)
    
    templates = [
        ("farm_icon.png", 60, 60, "Farm"),
        ("harvest_btn.png", 40, 40, "Harvest"),
        ("plant_btn.png", 40, 40, "Plant"),
        ("friend_list_btn.png", 50, 50, "Friend"),
        ("steal_btn.png", 40, 40, "Steal"),
        ("bless_btn.png", 40, 40, "Bless"),
        ("confirm_btn.png", 80, 40, "Confirm"),
        ("plant_confirm.png", 80, 40, "OK"),
        ("harvest_confirm.png", 80, 40, "OK"),
        ("close_btn.png", 30, 30, "X"),
    ]
    
    for filename, w, h, text in templates:
        img = create_placeholder(filename, w, h, text)
        path = output_dir / filename
        cv2.imwrite(str(path), img)
        print(f"  ✓ {filename} ({w}x{h})")
    
    print("\n" + "=" * 50)
    print("占位图已生成到 config/images/")
    print("请用真实游戏截图替换这些占位图！")
    print("=" * 50)


if __name__ == "__main__":
    main()
