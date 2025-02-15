"""日志管理模块"""
import os
import logging
from pathlib import Path
from rich.logging import RichHandler

def setup_logging(app_name: str):
    """设置日志系统"""
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 基本配置
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            RichHandler(show_time=False),
            logging.FileHandler(
                log_dir / f"{app_name}_install.log",
                encoding='utf-8'
            )
        ]
    )
    
    # 命令执行日志
    cmd_logger = logging.getLogger("command")
    cmd_logger.addHandler(
        logging.FileHandler(
            log_dir / f"{app_name}_commands.log",
            encoding='utf-8'
        )
    )
    
    # 安装器日志
    installer_logger = logging.getLogger("installer")
    installer_logger.addHandler(
        logging.FileHandler(
            log_dir / f"{app_name}_installer.log",
            encoding='utf-8'
        )
    ) 