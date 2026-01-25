"""
钉钉直播回放下载工具 - 日志配置模块

本模块负责配置和管理日志系统。
使用YamlConfig单例模式确保配置只加载一次。

作者：项目团队
依赖：logging, logging.handlers, os, datetime
创建日期：2025-01-15
修改历史：
    - 2025-01-15: 初始版本
    - 2026-01-21: 改造为从YAML读取配置
    - 2026-01-25: 使用YamlConfig单例模式
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Optional


class CustomFormatter(logging.Formatter):
    """自定义日志格式化器"""

    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录

        Args:
            record: 日志记录

        Returns:
            格式化后的日志字符串
        """
        if hasattr(record, "module_name"):
            record.module_name = record.module_name
        else:
            record.module_name = record.name.split(".")[-1]

        return super().format(record)


class RotatingFileHandlerWithCleanup(logging.handlers.RotatingFileHandler):
    """带清理功能的文件处理器"""

    def __init__(self, filename: str, max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5):
        """
        初始化文件处理器

        Args:
            filename: 日志文件名
            max_bytes: 单个文件最大字节数，默认 10MB
            backup_count: 备份文件数量，默认 5
        """
        super().__init__(filename, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")


class LoggerConfig:
    """日志配置类"""

    _initialized = False
    _log_dir = None

    @staticmethod
    def setup_logging(log_level: Optional[str] = None) -> None:
        """
        初始化日志系统

        Args:
            log_level: 日志级别，默认从YAML配置文件读取
        """
        if LoggerConfig._initialized:
            return

        try:
            from .yaml_config import YamlConfig

            yaml_config = YamlConfig.get_instance()

            LoggerConfig._log_dir = yaml_config.get_str("logging.dir", "logs")
            os.makedirs(LoggerConfig._log_dir, exist_ok=True)

            log_level_str = log_level or yaml_config.get_str("logging.level", "INFO")
            numeric_level = getattr(logging, log_level_str.upper(), logging.INFO)

            max_bytes = yaml_config.get_int("logging.max_bytes", 10 * 1024 * 1024)
            backup_count = yaml_config.get_int("logging.backup_count", 5)

            root_logger = logging.getLogger()
            root_logger.setLevel(numeric_level)

            if root_logger.handlers:
                root_logger.handlers.clear()

            formatter = CustomFormatter(
                fmt="[%(asctime)s.%(msecs)03d] [%(levelname)-8s] [%(module_name)-20s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            console_handler = logging.StreamHandler()
            console_handler.setLevel(numeric_level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

            log_filename = os.path.join(
                LoggerConfig._log_dir,
                f"dingtalk_downloader_{datetime.now().strftime('%Y-%m-%d')}.log",
            )
            file_handler = RotatingFileHandlerWithCleanup(
                log_filename, max_bytes=max_bytes, backup_count=backup_count
            )
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

            LoggerConfig._initialized = True

            logging.info("日志系统初始化成功")
            logging.info(f"日志级别: {log_level_str}")
            logging.info(f"日志目录: {LoggerConfig._log_dir}")
            logging.info(f"日志文件: {log_filename}")

        except Exception as e:
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.INFO)
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(
                logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s")
            )
            root_logger.addHandler(console_handler)
            root_logger.error(f"日志系统初始化失败: {e}", exc_info=True)
            LoggerConfig._initialized = True

    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        """
        获取 logger 实例

        Args:
            name: logger 名称，通常使用 __name__

        Returns:
            logger 实例
        """
        if not LoggerConfig._initialized:
            LoggerConfig.setup_logging()

        logger = logging.getLogger(name)
        return logger

    @staticmethod
    def clean_old_logs(days: int = None) -> None:
        """
        清理过期日志文件

        Args:
            days: 保留天数，默认从YAML配置文件读取
        """
        if LoggerConfig._log_dir is None:
            LoggerConfig._log_dir = os.path.join(os.getcwd(), "logs")

        if not os.path.exists(LoggerConfig._log_dir):
            return

        try:
            from .yaml_config import YamlConfig

            yaml_config = YamlConfig.get_instance()
            retention_days = days or yaml_config.get_int("logging.retention_days", 30)

            now = datetime.now()
            logger = LoggerConfig.get_logger(__name__)

            for filename in os.listdir(LoggerConfig._log_dir):
                if not filename.startswith("dingtalk_downloader_") or not filename.endswith(".log"):
                    continue

                filepath = os.path.join(LoggerConfig._log_dir, filename)
                file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                file_age = (now - file_mtime).days

                if file_age > retention_days:
                    os.remove(filepath)
                    logger.info(f"已删除过期日志文件: {filename}")

        except Exception as e:
            logger = LoggerConfig.get_logger(__name__)
            logger.warning(f"清理过期日志文件时发生错误: {e}")
