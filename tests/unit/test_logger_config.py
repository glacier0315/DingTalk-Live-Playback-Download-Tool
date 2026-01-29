"""
钉钉直播回放下载工具 - logger_config 单元测试

本模块测试日志配置类。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2026-01-29
修改历史：
    - 2026-01-29: 初始版本
"""

import sys
import os
import pytest
import logging
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.config.logger_config import (
    LoggerConfig,
    CustomFormatter,
    RotatingFileHandlerWithCleanup,
)


@pytest.fixture(autouse=True)
def reset_logger_config():
    """重置LoggerConfig状态"""
    LoggerConfig._initialized = False
    LoggerConfig._log_dir = None
    yield
    LoggerConfig._initialized = False
    LoggerConfig._log_dir = None


def test_custom_formatter_format():
    """测试自定义格式化器"""
    formatter = CustomFormatter(
        fmt="[%(asctime)s.%(msecs)03d] [%(levelname)-8s] [%(module_name)-20s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    record = logging.LogRecord(
        name="test.module",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    
    formatted = formatter.format(record)
    assert "Test message" in formatted
    assert "INFO" in formatted
    assert "module" in formatted


def test_custom_formatter_with_module_name():
    """测试自定义格式化器（带module_name属性）"""
    formatter = CustomFormatter(
        fmt="[%(module_name)-20s] %(message)s",
    )
    
    record = logging.LogRecord(
        name="test.module",
        level=logging.INFO,
        pathname="test.py",
        lineno=1,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    record.module_name = "custom_module"
    
    formatted = formatter.format(record)
    assert "custom_module" in formatted


def test_rotating_file_handler_with_cleanup_init(tmp_path):
    """测试带清理功能的文件处理器初始化"""
    log_file = tmp_path / "test.log"
    
    handler = RotatingFileHandlerWithCleanup(
        str(log_file), max_bytes=1024, backup_count=3
    )
    
    assert handler.maxBytes == 1024
    assert handler.backupCount == 3


def test_logger_config_setup_logging_default(tmp_path):
    """测试日志系统初始化（默认配置）"""
    with patch("dingtalk_downloader.config.logger_config.YamlConfig") as mock_yaml_config:
        mock_config = Mock()
        mock_config.get_str.side_effect = lambda key, default=None: {
            "logging.dir": str(tmp_path / "logs"),
            "logging.level": "INFO",
            "logging.max_bytes": 10485760,
            "logging.backup_count": 5,
        }.get(key, default)
        mock_yaml_config.get_instance.return_value = mock_config
        
        LoggerConfig.setup_logging()
        
        assert LoggerConfig._initialized is True
        assert LoggerConfig._log_dir == str(tmp_path / "logs")


def test_logger_config_setup_logging_custom_level(tmp_path):
    """测试日志系统初始化（自定义级别）"""
    with patch("dingtalk_downloader.config.logger_config.YamlConfig") as mock_yaml_config:
        mock_config = Mock()
        mock_config.get_str.side_effect = lambda key, default=None: {
            "logging.dir": str(tmp_path / "logs"),
            "logging.level": "DEBUG",
            "logging.max_bytes": 10485760,
            "logging.backup_count": 5,
        }.get(key, default)
        mock_yaml_config.get_instance.return_value = mock_config
        
        LoggerConfig.setup_logging("DEBUG")
        
        assert LoggerConfig._initialized is True


def test_logger_config_setup_logging_once(tmp_path):
    """测试日志系统初始化（只初始化一次）"""
    with patch("dingtalk_downloader.config.logger_config.YamlConfig") as mock_yaml_config:
        mock_config = Mock()
        mock_config.get_str.side_effect = lambda key, default=None: {
            "logging.dir": str(tmp_path / "logs"),
            "logging.level": "INFO",
            "logging.max_bytes": 10485760,
            "logging.backup_count": 5,
        }.get(key, default)
        mock_yaml_config.get_instance.return_value = mock_config
        
        LoggerConfig.setup_logging()
        initial_count = mock_config.get_str.call_count
        
        LoggerConfig.setup_logging()
        
        assert mock_config.get_str.call_count == initial_count


def test_logger_config_setup_logging_error(tmp_path):
    """测试日志系统初始化（异常处理）"""
    with patch("dingtalk_downloader.config.logger_config.YamlConfig") as mock_yaml_config:
        mock_yaml_config.get_instance.side_effect = Exception("Config error")
        
        LoggerConfig.setup_logging()
        
        assert LoggerConfig._initialized is True


def test_logger_config_get_logger(tmp_path):
    """测试获取logger实例"""
    with patch("dingtalk_downloader.config.logger_config.YamlConfig") as mock_yaml_config:
        mock_config = Mock()
        mock_config.get_str.side_effect = lambda key, default=None: {
            "logging.dir": str(tmp_path / "logs"),
            "logging.level": "INFO",
            "logging.max_bytes": 10485760,
            "logging.backup_count": 5,
        }.get(key, default)
        mock_yaml_config.get_instance.return_value = mock_config
        
        logger = LoggerConfig.get_logger("test.module")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test.module"


def test_logger_config_get_logger_auto_setup(tmp_path):
    """测试获取logger实例（自动初始化）"""
    with patch("dingtalk_downloader.config.logger_config.YamlConfig") as mock_yaml_config:
        mock_config = Mock()
        mock_config.get_str.side_effect = lambda key, default=None: {
            "logging.dir": str(tmp_path / "logs"),
            "logging.level": "INFO",
            "logging.max_bytes": 10485760,
            "logging.backup_count": 5,
        }.get(key, default)
        mock_yaml_config.get_instance.return_value = mock_config
        
        assert LoggerConfig._initialized is False
        
        logger = LoggerConfig.get_logger("test.module")
        
        assert LoggerConfig._initialized is True


def test_logger_config_clean_old_logs(tmp_path):
    """测试清理过期日志文件"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    
    current_date = datetime.now()
    
    old_log_1 = log_dir / "dingtalk_downloader_2026-01-01.log"
    old_log_2 = log_dir / "dingtalk_downloader_2026-01-15.log"
    new_log = log_dir / "dingtalk_downloader_2026-01-29.log"
    other_file = log_dir / "other.txt"
    
    old_log_1.write_text("old log 1")
    old_log_2.write_text("old log 2")
    new_log.write_text("new log")
    other_file.write_text("other")
    
    with patch("dingtalk_downloader.config.logger_config.YamlConfig") as mock_yaml_config:
        mock_config = Mock()
        mock_config.get_int.return_value = 30
        mock_yaml_config.get_instance.return_value = mock_config
        
        LoggerConfig._log_dir = str(log_dir)
        LoggerConfig.clean_old_logs()
        
        assert not old_log_1.exists()
        assert not old_log_2.exists()
        assert new_log.exists()
        assert other_file.exists()


def test_logger_config_clean_old_logs_no_dir():
    """测试清理过期日志文件（目录不存在）"""
    LoggerConfig._log_dir = None
    
    LoggerConfig.clean_old_logs()
    
    assert LoggerConfig._log_dir is not None


def test_logger_config_clean_old_logs_error(tmp_path):
    """测试清理过期日志文件（异常处理）"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    
    log_file = log_dir / "dingtalk_downloader_2026-01-01.log"
    log_file.write_text("old log")
    
    with patch("dingtalk_downloader.config.logger_config.YamlConfig") as mock_yaml_config:
        mock_config = Mock()
        mock_config.get_int.return_value = 30
        mock_yaml_config.get_instance.return_value = mock_config
        
        LoggerConfig._log_dir = str(log_dir)
        
        with patch("os.listdir", side_effect=PermissionError("Access denied")):
            LoggerConfig.clean_old_logs()
        
        assert log_file.exists()


def test_logger_config_clean_old_logs_custom_days(tmp_path):
    """测试清理过期日志文件（自定义天数）"""
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    
    current_date = datetime.now()
    
    old_log = log_dir / "dingtalk_downloader_2026-01-01.log"
    new_log = log_dir / "dingtalk_downloader_2026-01-29.log"
    
    old_log.write_text("old log")
    new_log.write_text("new log")
    
    with patch("dingtalk_downloader.config.logger_config.YamlConfig") as mock_yaml_config:
        mock_config = Mock()
        mock_config.get_int.return_value = 30
        mock_yaml_config.get_instance.return_value = mock_config
        
        LoggerConfig._log_dir = str(log_dir)
        LoggerConfig.clean_old_logs(days=10)
        
        assert not old_log.exists()
        assert new_log.exists()
