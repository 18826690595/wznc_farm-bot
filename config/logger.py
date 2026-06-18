"""
日志配置模块
"""
import os
from loguru import logger
from datetime import datetime


def setup_logger(log_dir: str = None, account: str = None):
    """
    配置日志
    
    Args:
        log_dir: 日志目录，默认为 logs/
        account: 当前账号名，用于区分日志文件
    """
    if log_dir is None:
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "logs"
        )
    
    # 确保日志目录存在
    os.makedirs(log_dir, exist_ok=True)
    
    # 移除默认处理器
    logger.remove()
    
    # 控制台输出
    logger.add(
        sys.stderr,
        level="INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
    )
    
    # 日志文件名
    date_str = datetime.now().strftime("%Y-%m-%d")
    if account:
        log_file = os.path.join(log_dir, f"{date_str}_{account}.log")
    else:
        log_file = os.path.join(log_dir, f"{date_str}.log")
    
    # 文件输出
    logger.add(
        log_file,
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        rotation="00:00",  # 每天0点轮转
        retention="7 days",  # 保留7天
        encoding="utf-8"
    )
    
    # 错误日志单独文件
    error_log = os.path.join(log_dir, f"{date_str}_error.log")
    logger.add(
        error_log,
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
        rotation="00:00",
        retention="30 days",
        encoding="utf-8"
    )
    
    return logger


# 导入 sys 用于 stderr
import sys

# 默认初始化
setup_logger()