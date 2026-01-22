"""
钉钉直播回放下载工具 - main 单元测试

本模块测试主程序入口。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.main import main, single_mode, batch_mode
from dingtalk_downloader.config.constants import (
    BROWSER_TYPE_EDGE,
    BROWSER_TYPE_CHROME,
    BROWSER_TYPE_FIREFOX,
    DOWNLOAD_MODE_SINGLE,
    DOWNLOAD_MODE_BATCH,
    SAVE_MODE_DEFAULT,
    SAVE_MODE_MANUAL,
)


def test_single_mode_with_default_options():
    """测试单个视频下载模式 - 使用默认选项"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.Downloader"
    ) as mock_downloader_class:

        mock_input.side_effect = [
            "https://n.dingtalk.com/test",  # 钉钉链接
            "",  # 保存模式（默认1）
            "",  # 浏览器类型（默认1）
        ]

        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        single_mode()

        mock_downloader.download_single_video.assert_called_once_with("https://n.dingtalk.com/test")
        assert mock_downloader_class.call_count == 1


def test_single_mode_with_manual_options():
    """测试单个视频下载模式 - 手动选择选项"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.Downloader"
    ) as mock_downloader_class:

        mock_input.side_effect = [
            "https://n.dingtalk.com/test",  # 钉钉链接
            "2",  # 保存模式（手动选择）
            "3",  # 浏览器类型（Firefox）
        ]

        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        single_mode()

        mock_downloader.download_single_video.assert_called_once_with("https://n.dingtalk.com/test")
        assert mock_downloader_class.call_count == 1


def test_single_mode_keyboard_interrupt():
    """测试单个视频下载模式 - 用户中断"""
    with patch("builtins.input") as mock_input:
        mock_input.side_effect = KeyboardInterrupt()

        with pytest.raises(SystemExit) as exc_info:
            single_mode()

        assert exc_info.value.code == 0


def test_single_mode_exception():
    """测试单个视频下载模式 - 异常处理"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.Downloader"
    ) as mock_downloader_class:

        mock_input.side_effect = ["https://n.dingtalk.com/test", "", ""]
        mock_downloader_class.side_effect = Exception("下载失败")

        with pytest.raises(SystemExit) as exc_info:
            single_mode()

        assert exc_info.value.code == 1


def test_batch_mode_with_default_options():
    """测试批量下载模式 - 使用默认选项"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.FileReader"
    ) as mock_file_reader_class, patch(
        "dingtalk_downloader.main.Downloader"
    ) as mock_downloader_class:

        mock_input.side_effect = [
            "test.csv",  # 文件路径
            "",  # 保存模式（默认1）
            "",  # 浏览器类型（默认1）
        ]

        mock_file_reader = Mock()
        mock_file_reader.read_links.return_value = {
            "Sheet1": ["https://n.dingtalk.com/test1", "https://n.dingtalk.com/test2"]
        }
        mock_file_reader_class.return_value = mock_file_reader

        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        batch_mode()

        mock_downloader.download_batch_videos.assert_called_once()
        assert mock_downloader_class.call_count == 1


def test_batch_mode_with_manual_options():
    """测试批量下载模式 - 手动选择选项"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.FileReader"
    ) as mock_file_reader_class, patch(
        "dingtalk_downloader.main.Downloader"
    ) as mock_downloader_class:

        mock_input.side_effect = [
            "test.xlsx",  # 文件路径
            "2",  # 保存模式（手动选择）
            "2",  # 浏览器类型（Chrome）
        ]

        mock_file_reader = Mock()
        mock_file_reader.read_links.return_value = {"Sheet1": ["https://n.dingtalk.com/test1"]}
        mock_file_reader_class.return_value = mock_file_reader

        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        batch_mode()

        mock_downloader.download_batch_videos.assert_called_once()
        assert mock_downloader_class.call_count == 1


def test_batch_mode_keyboard_interrupt():
    """测试批量下载模式 - 用户中断"""
    with patch("builtins.input") as mock_input:
        mock_input.side_effect = KeyboardInterrupt()

        with pytest.raises(SystemExit) as exc_info:
            batch_mode()

        assert exc_info.value.code == 0


def test_batch_mode_exception():
    """测试批量下载模式 - 异常处理"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.FileReader"
    ) as mock_file_reader_class:

        mock_input.side_effect = ["test.csv", "", ""]
        mock_file_reader_class.side_effect = Exception("文件读取失败")

        with pytest.raises(SystemExit) as exc_info:
            batch_mode()

        assert exc_info.value.code == 1


def test_main_single_mode():
    """测试主程序入口 - 单个视频下载模式"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.single_mode"
    ) as mock_single_mode:

        mock_input.side_effect = ["1"]  # 选择单个视频下载模式

        main()

        mock_single_mode.assert_called_once()


def test_main_batch_mode():
    """测试主程序入口 - 批量下载模式"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.batch_mode"
    ) as mock_batch_mode:

        mock_input.side_effect = ["2"]  # 选择批量下载模式

        main()

        mock_batch_mode.assert_called_once()


def test_main_keyboard_interrupt():
    """测试主程序入口 - 用户中断"""
    with patch("builtins.input") as mock_input:
        mock_input.side_effect = KeyboardInterrupt()

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0


def test_main_exception():
    """测试主程序入口 - 异常处理"""
    with patch("builtins.input") as mock_input:
        mock_input.side_effect = Exception("输入错误")

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1


def test_main_default_mode():
    """测试主程序入口 - 默认模式"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.single_mode"
    ) as mock_single_mode:

        mock_input.side_effect = [""]  # 直接回车，默认选择单个视频下载模式

        main()

        mock_single_mode.assert_called_once()


def test_single_mode_edge_browser():
    """测试单个视频下载模式 - Edge浏览器"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.Downloader"
    ) as mock_downloader_class:

        mock_input.side_effect = ["https://n.dingtalk.com/test", "", "1"]  # Edge

        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        single_mode()

        call_args = mock_downloader_class.call_args
        assert call_args[0][0] == BROWSER_TYPE_EDGE


def test_single_mode_chrome_browser():
    """测试单个视频下载模式 - Chrome浏览器"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.Downloader"
    ) as mock_downloader_class:

        mock_input.side_effect = ["https://n.dingtalk.com/test", "", "2"]  # Chrome

        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        single_mode()

        call_args = mock_downloader_class.call_args
        assert call_args[0][0] == BROWSER_TYPE_CHROME


def test_single_mode_firefox_browser():
    """测试单个视频下载模式 - Firefox浏览器"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.Downloader"
    ) as mock_downloader_class:

        mock_input.side_effect = ["https://n.dingtalk.com/test", "", "3"]  # Firefox

        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        single_mode()

        call_args = mock_downloader_class.call_args
        assert call_args[0][0] == BROWSER_TYPE_FIREFOX


def test_single_mode_default_save_mode():
    """测试单个视频下载模式 - 默认保存模式"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.Downloader"
    ) as mock_downloader_class:

        mock_input.side_effect = ["https://n.dingtalk.com/test", "", ""]  # 默认保存模式

        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        single_mode()

        call_args = mock_downloader_class.call_args
        assert call_args[0][1] == SAVE_MODE_DEFAULT


def test_single_mode_manual_save_mode():
    """测试单个视频下载模式 - 手动保存模式"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.Downloader"
    ) as mock_downloader_class:

        mock_input.side_effect = ["https://n.dingtalk.com/test", "2", ""]  # 手动保存模式

        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        single_mode()

        call_args = mock_downloader_class.call_args
        assert call_args[0][1] == SAVE_MODE_MANUAL
