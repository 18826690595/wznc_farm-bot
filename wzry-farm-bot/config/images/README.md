"""
模板图片说明

请在当前目录放置以下PNG格式的模板图片：
图片尺寸建议：根据实际游戏截图裁剪

必需模板：
"""

# 模板图片列表
TEMPLATES = {
    "farm_icon.png": "农场入口图标（在主界面查找农场入口）",
    "harvest_btn.png": "收获按钮（成熟的作物上显示）",
    "plant_btn.png": "种植按钮（空地上显示）",
    "steal_btn.png": "偷菜按钮（好友农场可偷取的作物上）",
    "bless_btn.png": "祝福按钮（好友列表或农场界面）",
    "friend_list_btn.png": "好友列表入口按钮",
    "confirm_btn.png": "确认按钮（种植确认等）"
}

if __name__ == "__main__":
    print("需要的模板图片：")
    print("-" * 60)
    for name, desc in TEMPLATES.items():
        print(f"{name:25s} - {desc}")
    print("-" * 60)
    print("\n制作方法：")
    print("1. 使用MuMu模拟器截图功能截取游戏画面")
    print("2. 使用图片编辑工具裁剪出对应按钮/图标")
    print("3. 保存为PNG格式，放入此目录")
    print("4. 建议尺寸：保留一定边缘，不要裁剪太紧")
