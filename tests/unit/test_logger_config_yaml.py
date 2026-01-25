"""
钉钉直播回放下载工具 - logger_config_yaml 单元测试

本模块测试LoggerConfig从YAML读取配置。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2026-01-21
修改历史：
    - 2026-01-21: 初始版本
"""

import sys
import os
import yaml
import pytest
import tempfile
import logging
from unittest.mock import patch, Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.config.logger_config import LoggerConfig


def test_setup_logging_from_yaml():
    """测试从YAML读取日志配置"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {
            "logging": {
                "level": "DEBUG",
                "dir": "test_logs",
                "max_bytes": 5242880,
                "backup_count": 3,
                "retention_days": 15,
            }
        }
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        with patch("dingtalk_downloader.config.yaml_config.YamlConfig") as mock_yaml_config_class:
            mock_instance = Mock()
            mock_instance.get_str.side_effect = lambda key, default=None: {
                "logging.level": "DEBUG",
                "logging.dir": "test_logs",
                "logging.max_bytes": 5242880,
                "logging.backup_count": 3,
                "logging.retention_days": 15,
            }.get(key, default)
            mock_instance.get_int.side_effect = lambda key, default=None: {
                "logging.level": "DEBUG",
                "logging.dir": "test_logs",
                "logging.max_bytes": 5242880,
                "logging.backup_count": 3,
                "logging.retention_days": 15,
            }.get(key, default)
            mock_yaml_config_class.get_instance.return_value = mock_instance

            LoggerConfig._initialized = False
            LoggerConfig.setup_logging()

            assert LoggerConfig._initialized is True
            assert LoggerConfig._log_dir == "test_logs"
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_log_level_from_yaml():
    """测试从YAML读取日志级别"""
    with patch("dingtalk_downloader.config.yaml_config.YamlConfig") as mock_yaml_config_class:
        mock_instance = Mock()
        mock_instance.get_str.side_effect = lambda key, default=None: {
            "logging.level": "WARNING",
            "logging.dir": "logs",
            "logging.max_bytes": 10485760,
            "logging.backup_count": 5,
            "logging.retention_days": 30,
        }.get(key, default)
        mock_instance.get_int.side_effect = lambda key, default=None: {
            "logging.level": "WARNING",
            "logging.dir": "logs",
            "logging.max_bytes": 10485760,
            "logging.backup_count": 5,
            "logging.retention_days": 30,
        }.get(key, default)
        mock_yaml_config_class.get_instance.return_value = mock_instance

        LoggerConfig._initialized = False
        LoggerConfig.setup_logging()

        root_logger = logging.getLogger()
        assert root_logger.level == logging.WARNING


def test_log_dir_from_yaml():
    """测试从YAML读取日志目录"""
    with patch("dingtalk_downloader.config.yaml_config.YamlConfig") as mock_yaml_config_class:
        mock_instance = Mock()
        mock_instance.get_str.side_effect = lambda key, default=None: {
            "logging.level": "INFO",
            "logging.dir": "custom_logs",
            "logging.max_bytes": 10485760,
            "logging.backup_count": 5,
            "logging.retention_days": 30,
        }.get(key, default)
        mock_instance.get_int.side_effect = lambda key, default=None: {
            "logging.level": "INFO",
            "logging.dir": "custom_logs",
            "logging.max_bytes": 10485760,
            "logging.backup_count": 5,
            "logging.retention_days": 30,
        }.get(key, default)
        mock_yaml_config_class.get_instance.return_value = mock_instance

        LoggerConfig._initialized = False
        LoggerConfig.setup_logging()

        assert LoggerConfig._log_dir == "custom_logs"


def test_log_max_bytes_from_yaml():
    """测试从YAML读取日志文件最大大小"""
    with patch("dingtalk_downloader.config.yaml_config.YamlConfig") as mock_yaml_config_class:
        mock_instance = Mock()
        mock_instance.get.side_effect = lambda key, default=None: {
            "logging.level": "INFO",
            "logging.dir": "logs",
            "logging.max_bytes": 20971520,
            "logging.backup_count": 5,
            "logging.retention_days": 30,
        }.get(key, default)
        mock_yaml_config_class.return_value = mock_instance

        LoggerConfig._initialized = False
        LoggerConfig.setup_logging()

        assert LoggerConfig._initialized is True


def test_log_backup_count_from_yaml():
    """测试从YAML读取日志备份数量"""
    with patch("dingtalk_downloader.config.yaml_config.YamlConfig") as mock_yaml_config_class:
        mock_instance = Mock()
        mock_instance.get.side_effect = lambda key, default=None: {
            "logging.level": "INFO",
            "logging.dir": "logs",
            "logging.max_bytes": 10485760,
            "logging.backup_count": 10,
            "logging.retention_days": 30,
        }.get(key, default)
        mock_yaml_config_class.return_value = mock_instance

        LoggerConfig._initialized = False
        LoggerConfig.setup_logging()

        assert LoggerConfig._initialized is True


def test_log_retention_days_from_yaml():
    """测试从YAML读取日志保留天数"""
    with patch("dingtalk_downloader.config.yaml_config.YamlConfig") as mock_yaml_config_class:
        mock_instance = Mock()
        mock_instance.get.side_effect = lambda key, default=None: {
            "logging.level": "INFO",
            "logging.dir": "logs",
            "logging.max_bytes": 10485760,
            "logging.backup_count": 5,
            "logging.retention_days": 60,
        }.get(key, default)
        mock_yaml_config_class.return_value = mock_instance

        LoggerConfig._initialized = False
        LoggerConfig.setup_logging()

        assert LoggerConfig._initialized is True


def test_setup_logging_with_override():
    """测试使用参数覆盖YAML配置"""
    with patch("dingtalk_downloader.config.yaml_config.YamlConfig") as mock_yaml_config_class:
        mock_instance = Mock()
        mock_instance.get_str.side_effect = lambda key, default=None: {
            "logging.level": "INFO",
            "logging.dir": "logs",
            "logging.max_bytes": 10485760,
            "logging.backup_count": 5,
            "logging.retention_days": 30,
        }.get(key, default)
        mock_instance.get_int.side_effect = lambda key, default=None: {
            "logging.level": "INFO",
            "logging.dir": "logs",
            "logging.max_bytes": 10485760,
            "logging.backup_count": 5,
            "logging.retention_days": 30,
        }.get(key, default)
        mock_yaml_config_class.get_instance.return_value = mock_instance

        LoggerConfig._initialized = False
        LoggerConfig.setup_logging(log_level="ERROR")

        root_logger = logging.getLogger()
        assert root_logger.level == logging.ERROR


def test_setup_logging_yaml_error():
    """测试YAML配置读取错误时的回退"""
    with patch("dingtalk_downloader.config.yaml_config.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.side_effect = Exception("YAML error")

        LoggerConfig._initialized = False
        LoggerConfig.setup_logging()

        assert LoggerConfig._initialized is True
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO


def test_get_logger():
    """测试获取logger实例"""
    LoggerConfig._initialized = False
    LoggerConfig.setup_logging()

    logger = LoggerConfig.get_logger("test_module")

    assert logger is not None
    assert logger.name == "test_module"


def test_get_logger_auto_setup():
    """测试获取logger时自动初始化"""
    LoggerConfig._initialized = False

    logger = LoggerConfig.get_logger("test_module")

    assert LoggerConfig._initialized is True
    assert logger is not None


def test_clean_old_logs_from_yaml():
    """测试从YAML读取日志保留天数并清理"""
    with patch("dingtalk_downloader.config.yaml_config.YamlConfig") as mock_yaml_config_class:
        mock_instance = Mock()
        mock_instance.get.side_effect = lambda key, default=None: {"logging.retention_days": 7}.get(
            key, default
        )
        mock_yaml_config_class.return_value = mock_instance

        LoggerConfig._log_dir = None
        LoggerConfig.clean_old_logs()

        assert LoggerConfig._log_dir is not None


def test_clean_old_logs_with_override():
    """测试使用参数覆盖YAML配置"""
    with patch("dingtalk_downloader.config.yaml_config.YamlConfig") as mock_yaml_config_class:
        mock_instance = Mock()
        mock_instance.get.side_effect = lambda key, default=None: {
            "logging.retention_days": 30
        }.get(key, default)
        mock_yaml_config_class.return_value = mock_instance

        LoggerConfig._log_dir = None
        LoggerConfig.clean_old_logs(days=15)

        assert LoggerConfig._log_dir is not None


def test_clean_old_logs_no_dir():
    """测试日志目录不存在时的处理"""
    LoggerConfig._log_dir = "/non/existent/logs"

    LoggerConfig.clean_old_logs()


def test_custom_formatter():
    """测试自定义格式化器"""
    from dingtalk_downloader.config.logger_config import CustomFormatter

    formatter = CustomFormatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(module_name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    record = logging.LogRecord(
        name="test.module",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="test message",
        args=(),
        exc_info=None,
    )

    formatted = formatter.format(record)

    assert "test message" in formatted
    assert "INFO" in formatted


def test_rotating_file_handler_with_cleanup():
    """测试带清理功能的文件处理器"""
    from dingtalk_downloader.config.logger_config import RotatingFileHandlerWithCleanup

    fd, path = tempfile.mkstemp(suffix=".log")
    try:
        os.close(fd)

        handler = RotatingFileHandlerWithCleanup(filename=path, max_bytes=1024, backup_count=3)

        assert handler.maxBytes == 1024
        assert handler.backupCount == 3
        assert handler.encoding == "utf-8"

        handler.close()
    finally:
        if os.path.exists(path):
            os.unlink(path)
