"""
日志配置模块
配置原生 logging，记录业务与登录日志
"""

import logging
import sys


def setup_logging() -> None:
    """初始化全局日志格式与级别"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
