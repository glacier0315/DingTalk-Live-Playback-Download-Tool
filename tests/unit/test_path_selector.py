"""
钉钉直播回放下载工具 - path_selector 单元测试

本模块测试路径选择器类。

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

from dingtalk_downloader.utils.path_selector import PathSelector
from dingtalk_downloader.config.constants import SAVE_MODE_DEFAULT, SAVE_MODE_MANUAL


@pytest.fixture
def mock_yaml_config():
    """创建模拟的YamlConfig"""
    config = Mock()
    config.get_str.return_value = "downloads"
    return config


def test_path_selector_init_default_mode():
    """测试初始化（默认模式）"""
    selector = PathSelector(SAVE_MODE_DEFAULT)
    assert selector.save_mode == SAVE_MODE_DEFAULT
    assert selector.saved_path is None


def test_path_selector_init_manual_mode():
    """测试初始化（手动模式）"""
    selector = PathSelector(SAVE_MODE_MANUAL)
    assert selector.save_mode == SAVE_MODE_MANUAL
    assert selector.saved_path is None


def test_path_selector_get_save_dir_default_mode(mock_yaml_config):
    """测试获取保存目录（默认模式）"""
    with patch("dingtalk_downloader.utils.path_selector.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        
        selector = PathSelector(SAVE_MODE_DEFAULT)
        save_dir = selector.get_save_dir()
        
        assert save_dir is not None
        assert "downloads" in save_dir.lower()


def test_path_selector_get_save_dir_manual_mode(mock_yaml_config):
    """测试获取保存目录（手动模式）"""
    with patch("dingtalk_downloader.utils.path_selector.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        
        with patch("dingtalk_downloader.utils.path_selector.filedialog.askdirectory") as mock_askdir:
            mock_askdir.return_value = "/custom/path"
            
            selector = PathSelector(SAVE_MODE_MANUAL)
            save_dir = selector.get_save_dir()
            
            assert save_dir == "/custom/path"


def test_path_selector_get_save_dir_manual_mode_cancel(mock_yaml_config):
    """测试获取保存目录（手动模式-用户取消）"""
    with patch("dingtalk_downloader.utils.path_selector.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        
        with patch("dingtalk_downloader.utils.path_selector.filedialog.askdirectory") as mock_askdir:
            mock_askdir.return_value = None
            
            selector = PathSelector(SAVE_MODE_MANUAL)
            save_dir = selector.get_save_dir()
            
            assert save_dir is None


def test_path_selector_get_save_dir_invalid_mode(mock_yaml_config):
    """测试获取保存目录（无效模式）"""
    with patch("dingtalk_downloader.utils.path_selector.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        
        selector = PathSelector("3")
        save_dir = selector.get_save_dir()
        
        assert save_dir is None


def test_path_selector_get_saved_path(mock_yaml_config):
    """测试获取已保存的路径"""
    with patch("dingtalk_downloader.utils.path_selector.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        
        with patch("dingtalk_downloader.utils.path_selector.filedialog.askdirectory") as mock_askdir:
            mock_askdir.return_value = "/custom/path"
            
            selector = PathSelector(SAVE_MODE_MANUAL)
            selector.get_save_dir()
            saved_path = selector.get_saved_path()
            
            assert saved_path == "/custom/path"


def test_path_selector_get_saved_path_none():
    """测试获取已保存的路径（未保存）"""
    selector = PathSelector(SAVE_MODE_DEFAULT)
    saved_path = selector.get_saved_path()
    
    assert saved_path is None


def test_path_selector_get_default_download_dir_absolute(mock_yaml_config):
    """测试获取默认下载目录（绝对路径）"""
    with patch("dingtalk_downloader.utils.path_selector.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        mock_yaml_config.get_str.return_value = "/absolute/downloads"
        
        selector = PathSelector(SAVE_MODE_DEFAULT)
        save_dir = selector._get_default_download_dir()
        
        assert save_dir == "/absolute/downloads"


def test_path_selector_get_default_download_dir_relative(mock_yaml_config):
    """测试获取默认下载目录（相对路径）"""
    with patch("dingtalk_downloader.utils.path_selector.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        mock_yaml_config.get_str.return_value = "downloads"
        
        selector = PathSelector(SAVE_MODE_DEFAULT)
        save_dir = selector._get_default_download_dir()
        
        assert "downloads" in save_dir.lower()


def test_path_selector_get_default_download_dir_error(mock_yaml_config):
    """测试获取默认下载目录（异常处理）"""
    with patch("dingtalk_downloader.utils.path_selector.YamlConfig") as mock_yaml_config_class:
        mock_yaml_config_class.get_instance.return_value = mock_yaml_config
        mock_yaml_config.get_str.side_effect = Exception("Config error")
        
        selector = PathSelector(SAVE_MODE_DEFAULT)
        save_dir = selector._get_default_download_dir()
        
        assert save_dir is not None
        assert "downloads" in save_dir.lower()
