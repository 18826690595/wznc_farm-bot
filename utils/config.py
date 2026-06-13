"""
配置管理模块
"""
import yaml
from pathlib import Path
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from loguru import logger


class DeviceConfig(BaseModel):
    """设备配置"""
    adb_port: int = Field(default=7555, description="MuMu模拟器ADB端口")
    screenshot_delay: float = Field(default=0.5, description="截图延迟")
    connect_timeout: int = Field(default=30, description="连接超时")


class FarmConfig(BaseModel):
    """农场配置"""
    harvest_interval: int = Field(default=300, description="收菜检查间隔(秒)")
    steal_interval: int = Field(default=600, description="偷菜检查间隔(秒)")
    bless_interval: int = Field(default=1800, description="祝福检查间隔(秒)")
    default_crop: str = Field(default="小麦", description="默认种植作物")


class SafetyConfig(BaseModel):
    """安全配置"""
    random_delay: bool = Field(default=True, description="随机延迟(防检测)")
    max_steal_per_run: int = Field(default=10, description="单次最大偷菜次数")
    max_bless_per_run: int = Field(default=20, description="单次最大祝福次数")
    operation_interval: float = Field(default=0.5, description="操作间隔")


class ScheduleConfig(BaseModel):
    """调度配置"""
    enable_harvest: bool = Field(default=True, description="启用收菜")
    enable_plant: bool = Field(default=True, description="启用种菜")
    enable_steal: bool = Field(default=True, description="启用偷菜")
    enable_bless: bool = Field(default=True, description="启用祝福")
    plant_cron: Optional[Dict[str, int]] = Field(
        default=None, 
        description="定时种菜 {'hour': 8, 'minute': 0}"
    )


class Settings(BaseModel):
    """总配置"""
    device: DeviceConfig = Field(default_factory=DeviceConfig)
    farm: FarmConfig = Field(default_factory=FarmConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    schedule: ScheduleConfig = Field(default_factory=ScheduleConfig)
    
    class Config:
        extra = "allow"


def load_config(config_path: str = "config/settings.yaml") -> Settings:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        Settings对象
    """
    path = Path(config_path)
    
    if not path.exists():
        logger.warning(f"配置文件不存在: {config_path}，使用默认配置")
        return Settings()
    
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        
        settings = Settings(**data)
        logger.success(f"配置加载成功: {config_path}")
        return settings
        
    except Exception as e:
        logger.error(f"配置加载失败: {e}，使用默认配置")
        return Settings()


def save_config(settings: Settings, config_path: str = "config/settings.yaml"):
    """
    保存配置文件
    
    Args:
        settings: Settings对象
        config_path: 配置文件路径
    """
    path = Path(config_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        data = settings.model_dump()
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        
        logger.success(f"配置保存成功: {config_path}")
        
    except Exception as e:
        logger.error(f"配置保存失败: {e}")


def get_default_config() -> Dict[str, Any]:
    """
    获取默认配置字典
    
    Returns:
        默认配置
    """
    return {
        'device': {
            'adb_port': 7555,
            'screenshot_delay': 0.5,
            'connect_timeout': 30
        },
        'farm': {
            'harvest_interval': 300,
            'steal_interval': 600,
            'bless_interval': 1800,
            'default_crop': '小麦'
        },
        'safety': {
            'random_delay': True,
            'max_steal_per_run': 10,
            'max_bless_per_run': 20,
            'operation_interval': 0.5
        },
        'schedule': {
            'enable_harvest': True,
            'enable_plant': True,
            'enable_steal': True,
            'enable_bless': True,
            'plant_cron': None
        }
    }
