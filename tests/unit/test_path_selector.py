"""
钉钉直播回放下载工具 - path_selector 单元测试

本模块测试路径选择器类。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2026-01-27
修改历史：
    - 2026-01-27: 初始版本
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.utils.path_selector import PathSelector
from dingtalk_downloader.config.constants import SAVE_MODE_DEFAULT, SAVE_MODE_MANUAL


def test_path_selector_init_default():
    """测试默认模式初始化"""
    selector = PathSelector(SAVE_MODE_DEFAULT)

    assert selector.save_mode == SAVE_MODE_DEFAULT
    assert selector.saved_path is None


def test_path_selector_init_manual():
    """测试手动模式初始化"""
    selector = PathSelector(SAVE_MODE_MANUAL)

    assert selector.save_mode == SAVE_MODE_MANUAL
    assert selector.saved_path is None


@patch("dingtalk_downloader.utils.path_selector.YamlConfig")
def test_get_save_dir_default(mock_yaml_config_class):
    """测试获取默认保存目录"""
    mock_config = Mock()
    mock_config.get_str.return_value = "Downloads"
    mock_yaml_config_class.get_instance.return_value = mock_config

    selector = PathSelector(SAVE_MODE_DEFAULT)
    save_dir = selector.get_save_dir()

    assert save_dir is not None
    assert "Downloads" in save_dir
    assert selector.saved_path == save_dir
    mock_yaml_config_class.get_instance.assert_called_once()
    mock_config.get_str.assert_called_once_with("download.default_dir", "Downloads")


@patch("dingtalk_downloader.utils.path_selector.tk.Tk")
@patch("dingtalk_downloader.utils.path_selector.filedialog.askdirectory")
def test_get_save_dir_manual_success(mock_askdirectory, mock_tk):
    """测试获取手动选择的保存目录成功"""
    mock_root = Mock()
    mock_tk.return_value = mock_root
    mock_askdirectory.return_value = "/custom/path"

    selector = PathSelector(SAVE_MODE_MANUAL)
    save_dir = selector.get_save_dir()

    assert save_dir == "/custom/path"
    assert selector.saved_path == "/custom/path"
    mock_root.withdraw.assert_called_once()
    mock_root.destroy.assert_called_once()
    mock_askdirectory.assert_called_once_with(title="选择保存视频的目录")


@patch("dingtalk_downloader.utils.path_selector.tk.Tk")
@patch("dingtalk_downloader.utils.path_selector.filedialog.askdirectory")
def test_get_save_dir_manual_cancelled(mock_askdirectory, mock_tk):
    """测试获取手动选择的保存目录取消"""
    mock_root = Mock()
    mock_tk.return_value = mock_root
    mock_askdirectory.return_value = ""

    selector = PathSelector(SAVE_MODE_MANUAL)
    save_dir = selector.get_save_dir()

    assert save_dir is None
    assert selector.saved_path is None
    mock_root.withdraw.assert_called_once()
    mock_root.destroy.assert_called_once()
    mock_askdirectory.assert_called_once_with(title="选择保存视频的目录")


def test_get_saved_path():
    """测试获取已保存的路径"""
    selector = PathSelector(SAVE_MODE_DEFAULT)
    selector.saved_path = "/path/to/downloads"

    saved_path = selector.get_saved_path()

    assert saved_path == "/path/to/downloads"


def test_get_saved_path_none():
    """测试获取已保存的路径为None"""
    selector = PathSelector(SAVE_MODE_DEFAULT)

    saved_path = selector.get_saved_path()

    assert saved_path is None
