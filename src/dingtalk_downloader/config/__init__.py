"""
钉钉直播回放下载工具 - 配置模块

本模块包含配置项定义和常量定义。

作者：项目团队
依赖：无
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2025-01-15: 添加日志配置模块导出
    - 2026-01-21: 添加CONFIG_FILE_PATH常量导出
    - 2026-01-25: 添加配置异常类导出
"""

from .logger_config import LoggerConfig
from .yaml_config import (
    YamlConfig,
    ConfigError,
    ConfigLoadError,
    ConfigValueError,
    ConfigValidationError,
)
from .header_manager import HeaderManager

__all__ = [
    "LoggerConfig",
    "YamlConfig",
    "HeaderManager",
    "ConfigError",
    "ConfigLoadError",
    "ConfigValueError",
    "ConfigValidationError",
]
