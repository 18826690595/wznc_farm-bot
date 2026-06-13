"""
日志配置模块
"""
from loguru import logger
from pathlib import Path
import sys


def setup_logger(
    log_dir: str = "logs",
    log_level: str = "INFO",
    rotation: str = "10 MB",
    retention: str = "7 days"
):
    """
    配置日志系统
    
    Args:
        log_dir: 日志目录
        log_level: 日志级别
        rotation: 日志轮转大小
        retention: 日志保留时间
    """
    # 创建日志目录
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # 移除默认处理器
    logger.remove()
    
    # 控制台输出（彩色）
    logger.add(
        sys.stdout,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        colorize=True
    )
    
    # 文件输出（所有日志）
    logger.add(
        f"{log_dir}/wzry_farm_{log_level.lower()}.log",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation=rotation,
        retention=retention,
        encoding="utf-8"
    )
    
    # 错误日志单独记录
    logger.add(
        f"{log_dir}/wzry_farm_error.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
        rotation=rotation,
        retention=retention,
        encoding="utf-8"
    )
    
    logger.success("日志系统初始化完成")
    return logger
