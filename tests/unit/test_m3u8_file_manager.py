"""
钉钉直播回放下载工具 - m3u8_file_manager 单元测试

本模块测试m3u8文件管理类。

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
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.utils.m3u8_file_manager import M3u8FileManager


@pytest.fixture
def mock_yaml_config():
    """创建模拟的YamlConfig"""
    config = Mock()
    config.get.return_value = "temp"
    return config


def test_m3u8_file_manager_init(mock_yaml_config):
    """测试初始化"""
    with patch("dingtalk_downloader.utils.m3u8_file_manager.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        with patch("dingtalk_downloader.utils.m3u8_file_manager.ensure_dir_exists") as mock_ensure_dir:
            manager = M3u8FileManager()
            
            assert manager.config is not None
            assert manager.temp_dir is not None
            mock_ensure_dir.assert_called_once()


def test_m3u8_file_manager_resolve_temp_dir_absolute(mock_yaml_config):
    """测试解析临时目录（绝对路径）"""
    with patch("dingtalk_downloader.utils.m3u8_file_manager.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        mock_yaml_config.get.return_value = "/absolute/temp"
        
        manager = M3u8FileManager()
        temp_dir = manager._resolve_temp_dir()
        
        assert temp_dir is not None


def test_m3u8_file_manager_resolve_temp_dir_relative(mock_yaml_config):
    """测试解析临时目录（相对路径）"""
    with patch("dingtalk_downloader.utils.m3u8_file_manager.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        mock_yaml_config.get.return_value = "temp"
        
        manager = M3u8FileManager()
        temp_dir = manager._resolve_temp_dir()
        
        assert temp_dir is not None


def test_m3u8_file_manager_ensure_temp_dir_exists(tmp_path):
    """测试确保临时目录存在"""
    with patch("dingtalk_downloader.utils.m3u8_file_manager.YamlConfig") as mock_yaml_config_class:
        mock_config = Mock()
        mock_config.get.return_value = str(tmp_path / "temp")
        mock_yaml_config_class.get_instance.return_value = mock_config
        
        manager = M3u8FileManager()
        
        assert manager.temp_dir is not None


def test_m3u8_file_manager_generate_filename_no_prefix():
    """测试生成文件名（无前缀）"""
    with patch("dingtalk_downloader.utils.m3u8_file_manager.YamlConfig") as mock_yaml_config_class:
        mock_config = Mock()
        mock_yaml_config_class.get_instance.return_value = mock_config
        
        manager = M3u8FileManager()
        filename = manager.generate_filename()
        
        assert filename.endswith(".m3u8")


def test_m3u8_file_manager_generate_filename_with_prefix():
    """测试生成文件名（带前缀）"""
    with patch("dingtalk_downloader.utils.m3u8_file_manager.YamlConfig") as mock_yaml_config_class:
        mock_config = Mock()
        mock_yaml_config_class.get_instance.return_value = mock_config
        
        manager = M3u8FileManager()
        filename = manager.generate_filename(prefix="test")
        
        assert filename.startswith("test_")
        assert filename.endswith(".m3u8")


def test_m3u8_file_manager_get_temp_file_path_no_filename():
    """测试获取临时文件路径（无文件名）"""
    with patch("dingtalk_downloader.utils.m3u8_file_manager.YamlConfig") as mock_yaml_config_class:
        mock_config = Mock()
        mock_config.get.return_value = "temp"
        mock_yaml_config_class.get_instance.return_value = mock_config
        
        manager = M3u8FileManager()
        file_path = manager.get_temp_file_path()
        
        assert file_path.endswith(".m3u8")


def test_m3u8_file_manager_get_temp_file_path_with_filename():
    """测试获取临时文件路径（带文件名）"""
    with patch("dingtalk_downloader.utils.m3u8_file_manager.YamlConfig") as mock_yaml_config_class:
        mock_config = Mock()
        mock_config.get.return_value = "temp"
        mock_yaml_config_class.get_instance.return_value = mock_config
        
        manager = M3u8FileManager()
        file_path = manager.get_temp_file_path(filename="custom.m3u8")
        
        assert file_path.endswith("custom.m3u8")


def test_m3u8_file_manager_get_temp_dir():
    """测试获取临时目录"""
    with patch("dingtalk_downloader.utils.m3u8_file_manager.YamlConfig") as mock_yaml_config_class:
        mock_config = Mock()
        mock_config.get.return_value = "temp"
        mock_yaml_config_class.get_instance.return_value = mock_config
        
        manager = M3u8FileManager()
        temp_dir = manager.get_temp_dir()
        
        assert temp_dir is not None
