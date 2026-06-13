"""
模板配置 - 在这里定义所有按钮/图标的模板图片

使用步骤：
1. 截取游戏截图（建议使用 MuMu 模拟器截图功能）
2. 用图片编辑工具裁剪出按钮/图标
3. 保存为 PNG 格式到 config/images/ 目录
4. 在下方 TemplateConfig 中配置
"""

from dataclasses import dataclass
from typing import Dict, Optional
import cv2
import numpy as np
from pathlib import Path
from loguru import logger


@dataclass
class TemplateInfo:
    """模板信息"""
    filename: str           # 图片文件名
    description: str        # 描述
    threshold: float = 0.8  # 匹配阈值 (0-1)
    multi_match: bool = False  # 是否多点匹配


class TemplateConfig:
    """
    模板配置类 - 管理所有按钮/图标模板
    
    TODO: 根据你的游戏截图，补充以下模板
    """
    
    # ========== 模板定义（需要你填充图片）==========
    TEMPLATES: Dict[str, TemplateInfo] = {
        # ----- 游戏启动 -----（新增）
        "game_start_btn": TemplateInfo(
            filename="game_start_btn.png",
            description="游戏启动按钮",
            threshold=0.8
        ),
        "game_loading": TemplateInfo(
            filename="game_loading.png",
            description="游戏加载完成标志",
            threshold=0.8
        ),
        
        # ----- 农场入口 -----
        "farm_icon": TemplateInfo(
            filename="farm_icon.png",
            description="农场入口图标（主界面）",
            threshold=0.8
        ),
        
        # ----- 收菜相关 -----
        "harvest_btn": TemplateInfo(
            filename="harvest_btn.png",
            description="收获按钮（成熟作物上）",
            threshold=0.75,
            multi_match=True  # 可能有多个成熟作物
        ),
        "harvest_confirm": TemplateInfo(
            filename="harvest_confirm.png",
            description="收获确认按钮",
            threshold=0.8
        ),
        
        # ----- 种菜相关 -----
        "plant_btn": TemplateInfo(
            filename="plant_btn.png",
            description="种植按钮（空地上）",
            threshold=0.75,
            multi_match=True
        ),
        "plant_confirm": TemplateInfo(
            filename="plant_confirm.png",
            description="种植确认按钮",
            threshold=0.8
        ),
        # TODO: 添加具体作物的选择按钮，如：
        # "crop_wheat": TemplateInfo("crop_wheat.png", "小麦"),
        # "crop_corn": TemplateInfo("crop_corn.png", "玉米"),
        
        # ----- 好友相关 -----
        "friend_list_btn": TemplateInfo(
            filename="friend_list_btn.png",
            description="好友列表入口",
            threshold=0.8
        ),
        "friend_farm_btn": TemplateInfo(
            filename="friend_farm_btn.png",
            description="进入好友农场",
            threshold=0.8
        ),
        
        # ----- 偷菜相关 -----
        "steal_btn": TemplateInfo(
            filename="steal_btn.png",
            description="偷菜按钮",
            threshold=0.75,
            multi_match=True
        ),
        "steal_confirm": TemplateInfo(
            filename="steal_confirm.png",
            description="偷菜确认按钮",
            threshold=0.8
        ),
        
        # ----- 祝福相关 -----
        "bless_btn": TemplateInfo(
            filename="bless_btn.png",
            description="祝福按钮",
            threshold=0.8,
            multi_match=True
        ),
        "bless_confirm": TemplateInfo(
            filename="bless_confirm.png",
            description="祝福确认按钮",
            threshold=0.8
        ),
        
        # ----- 通用按钮 -----
        "confirm_btn": TemplateInfo(
            filename="confirm_btn.png",
            description="通用确认按钮",
            threshold=0.8
        ),
        "cancel_btn": TemplateInfo(
            filename="cancel_btn.png",
            description="通用取消按钮",
            threshold=0.8
        ),
        "close_btn": TemplateInfo(
            filename="close_btn.png",
            description="关闭按钮",
            threshold=0.8
        ),
        
        # TODO: 在这里添加更多模板...
    }
    
    def __init__(self, template_dir: str = "config/images"):
        self.template_dir = Path(template_dir)
        self.images: Dict[str, np.ndarray] = {}
        self._load_all()
    
    def _load_all(self):
        """加载所有模板图片"""
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        loaded = 0
        missing = []
        
        for name, info in self.TEMPLATES.items():
            img_path = self.template_dir / info.filename
            
            if img_path.exists():
                img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
                if img is not None:
                    self.images[name] = img
                    loaded += 1
                    logger.debug(f"加载模板: {name} ({img.shape})")
                else:
                    missing.append(name)
            else:
                missing.append(name)
        
        logger.info(f"模板加载完成: {loaded} 个成功, {len(missing)} 个待添加")
        
        if missing:
            logger.warning(f"缺少模板图片: {missing}")
            logger.warning("请将对应图片放入 config/images/ 目录")
    
    def get(self, name: str) -> Optional[np.ndarray]:
        """获取模板图片"""
        return self.images.get(name)
    
    def get_info(self, name: str) -> Optional[TemplateInfo]:
        """获取模板配置信息"""
        return self.TEMPLATES.get(name)
    
    def exists(self, name: str) -> bool:
        """模板是否存在"""
        return name in self.images
    
    def list_missing(self) -> list:
        """列出缺失的模板"""
        return [name for name in self.TEMPLATES if name not in self.images]
    
    def print_status(self):
        """打印模板状态"""
        print("\n" + "=" * 60)
        print("模板图片状态")
        print("=" * 60)
        
        for name, info in self.TEMPLATES.items():
            status = "✓ 已加载" if name in self.images else "✗ 待添加"
            print(f"{name:20s} | {status:10s} | {info.description}")
        
        print("=" * 60)


# 全局实例
template_config = TemplateConfig()


if __name__ == "__main__":
    # 打印模板状态
    template_config.print_status()
