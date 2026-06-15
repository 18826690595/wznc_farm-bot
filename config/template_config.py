"""
模板配置文件
定义所有模板图片的路径和参数
"""

from dataclasses import dataclass
from typing import Dict
from pathlib import Path


@dataclass
class TemplateInfo:
    """模板信息"""
    filename: str                      # 文件名
    description: str = ""              # 描述
    threshold: float = 0.8             # 匹配阈值
    region: tuple = None               # 搜索区域限制 (x1,y1,x2,y2)


class TemplateConfig:
    """模板配置管理"""
    
    # 模板图片根目录
    TEMPLATE_DIR = Path(__file__).parent
    
    # 页面模板目录
    PAGES_DIR = TEMPLATE_DIR / "templates" / "pages"
    
    # 按钮模板目录
    BUTTONS_DIR = TEMPLATE_DIR / "templates" / "buttons"
    
    # 所有模板定义
    TEMPLATES: Dict[str, TemplateInfo] = {
        # ========== 游戏相关 ==========
        "game_start_btn": TemplateInfo(
            filename="game_start_btn.png",
            description="游戏启动按钮",
        ),
        "game_loading": TemplateInfo(
            filename="game_loading.png",
            description="游戏加载界面",
        ),
        
        # ========== 农场相关 ==========
        "farm_icon": TemplateInfo(
            filename="farm_icon.png",
            description="农场入口图标",
        ),
        "harvest_btn": TemplateInfo(
            filename="harvest_btn.png",
            description="收获按钮",
        ),
        "plant_btn": TemplateInfo(
            filename="plant_btn.png",
            description="种植按钮",
        ),
        "empty_plot": TemplateInfo(
            filename="empty_plot.png",
            description="空地块",
        ),
        
        # ========== 好友相关 ==========
        "friend_list_btn": TemplateInfo(
            filename="friend_list_btn.png",
            description="好友列表入口",
        ),
        "steal_btn": TemplateInfo(
            filename="steal_btn.png",
            description="偷菜按钮",
        ),
        "bless_btn": TemplateInfo(
            filename="bless_btn.png",
            description="祝福按钮",
        ),
        
        # ========== 确认弹窗 ==========
        "confirm_btn": TemplateInfo(
            filename="confirm_btn.png",
            description="确认按钮",
        ),
        "cancel_btn": TemplateInfo(
            filename="cancel_btn.png",
            description="取消按钮",
        ),
        "close_btn": TemplateInfo(
            filename="close_btn.png",
            description="关闭按钮",
        ),
    }
    
    @classmethod
    def get_template_path(cls, name: str, template_type: str = "button") -> Path:
        """获取模板图片路径
        
        Args:
            name: 模板名称
            template_type: 模板类型 ("page" 或 "button")
        
        Returns:
            模板图片完整路径
        """
        if template_type == "page":
            return cls.PAGES_DIR / f"{name}.png"
        else:
            return cls.BUTTONS_DIR / f"{name}.png"
    
    @classmethod
    def get_template_info(cls, name: str) -> TemplateInfo:
        """获取模板信息"""
        return cls.TEMPLATES.get(name)
    
    @classmethod
    def add_template(cls, name: str, info: TemplateInfo):
        """添加新模板"""
        cls.TEMPLATES[name] = info
    
    @classmethod
    def list_templates(cls) -> Dict[str, TemplateInfo]:
        """列出所有模板"""
        return cls.TEMPLATES.copy()