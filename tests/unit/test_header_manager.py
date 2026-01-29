"""
钉钉直播回放下载工具 - header_manager 单元测试

本模块测试请求头管理类。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2026-01-29
修改历史：
    - 2026-01-29: 初始版本
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.config.header_manager import HeaderManager


@pytest.fixture
def mock_yaml_config():
    """创建模拟的YamlConfig"""
    config = Mock()
    config.get.return_value = {
        "user_agent": "Mozilla/5.0",
        "referer": "https://n.dingtalk.com/",
        "accept": "application/vnd.apple.mpegurl, text/plain, */*",
        "accept_language": "zh-CN,zh;q=0.9,en;q=0.8",
        "accept_encoding": "gzip, deflate, br",
        "connection": "keep-alive",
        "sec_fetch_dest": "document",
        "sec_fetch_mode": "navigate",
        "sec_fetch_site": "none",
        "sec_fetch_user": "?1",
        "upgrade_insecure_requests": "1",
    }
    return config


def test_header_manager_init(mock_yaml_config):
    """测试初始化"""
    with patch("dingtalk_downloader.config.header_manager.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        
        manager = HeaderManager()
        
        assert manager.config == mock_yaml_config
        assert len(manager._headers_cache) > 0
        assert "User-Agent" in manager._headers_cache


def test_header_manager_load_headers(mock_yaml_config):
    """测试加载请求头"""
    with patch("dingtalk_downloader.config.header_manager.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        
        manager = HeaderManager()
        
        assert "User-Agent" in manager._headers_cache
        assert "Referer" in manager._headers_cache
        assert "Accept" in manager._headers_cache


def test_header_manager_get_headers(mock_yaml_config):
    """测试获取请求头字典"""
    with patch("dingtalk_downloader.config.header_manager.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        
        manager = HeaderManager()
        headers = manager.get_headers()
        
        assert isinstance(headers, dict)
        assert "User-Agent" in headers
        assert "Referer" in headers


def test_header_manager_get_headers_with_overrides(mock_yaml_config):
    """测试获取请求头字典（包含覆盖）"""
    with patch("dingtalk_downloader.config.header_manager.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        
        manager = HeaderManager()
        manager._override_headers["User-Agent"] = "Custom Agent"
        
        headers = manager.get_headers(include_overrides=True)
        
        assert headers["User-Agent"] == "Custom Agent"


def test_header_manager_get_headers_without_overrides(mock_yaml_config):
    """测试获取请求头字典（不包含覆盖）"""
    with patch("dingtalk_downloader.config.header_manager.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        
        manager = HeaderManager()
        manager._override_headers["User-Agent"] = "Custom Agent"
        
        headers = manager.get_headers(include_overrides=False)
        
        assert headers["User-Agent"] != "Custom Agent"


def test_header_manager_get_header(mock_yaml_config):
    """测试获取单个请求头"""
    with patch("dingtalk_downloader.config.header_manager.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        
        manager = HeaderManager()
        user_agent = manager.get_header("User-Agent")
        
        assert user_agent == "Mozilla/5.0"


def test_header_manager_get_header_with_default(mock_yaml_config):
    """测试获取单个请求头（带默认值）"""
    with patch("dingtalk_downloader.config.header_manager.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        
        manager = HeaderManager()
        value = manager.get_header("Non-Existent", "default")
        
        assert value == "default"


def test_header_manager_get_header_with_override(mock_yaml_config):
    """测试获取单个请求头（包含覆盖）"""
    with patch("dingtalk_downloader.config.header_manager.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        
        manager = HeaderManager()
        manager._override_headers["User-Agent"] = "Custom Agent"
        
        user_agent = manager.get_header("User-Agent", include_overrides=True)
        
        assert user_agent == "Custom Agent"


def test_header_manager_get_header_without_override(mock_yaml_config):
    """测试获取单个请求头（不包含覆盖）"""
    with patch("dingtalk_downloader.config.header_manager.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        
        manager = HeaderManager()
        manager._override_headers["User-Agent"] = "Custom Agent"
        
        user_agent = manager.get_header("User-Agent", include_overrides=False)
        
        assert user_agent != "Custom Agent"


def test_header_manager_reload_config(mock_yaml_config):
    """测试重新加载配置"""
    with patch("dingtalk_downloader.config.header_manager.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        
        manager = HeaderManager()
        manager._override_headers["Custom-Header"] = "Custom Value"
        
        manager.reload_config()
        
        assert mock_yaml_config.reload.called
        assert "Custom-Header" in manager._override_headers
