"""
钉钉直播回放下载工具 - 集成测试

本模块测试完整下载流程。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.core.downloader import Downloader
from dingtalk_downloader.config.constants import BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT


@patch("dingtalk_downloader.core.downloader.CookieHandler")
@patch("dingtalk_downloader.core.downloader.M3u8Parser")
@patch("dingtalk_downloader.core.downloader.NM3u8DLRE")
def test_single_download_flow(mock_n_m3u8dl_re, mock_m3u8_parser, mock_cookie_handler):
    """测试单个视频下载流程"""
    mock_cookie_handler.return_value.get_cookie.return_value = (
        Mock(),
        {"test": "value"},
        {"User-Agent": "Mozilla/5.0"},
        "测试直播",
    )
    mock_m3u8_parser.return_value.fetch_m3u8_links.return_value = ["https://test.com/test.m3u8"]
    mock_m3u8_parser.return_value.download_m3u8_file.return_value = "output.m3u8"
    mock_m3u8_parser.return_value.extract_prefix.return_value = "https://test.com/live_hp/123"
    mock_n_m3u8dl_re.return_value.download.return_value = True

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)

    with patch("builtins.input", side_effect=["q"]):
        downloader.download_single_video("https://n.dingtalk.com/test")

    mock_cookie_handler.return_value.get_cookie.assert_called_once()
    mock_m3u8_parser.return_value.fetch_m3u8_links.assert_called()
    mock_n_m3u8dl_re.return_value.download.assert_called_once()


@patch("dingtalk_downloader.core.downloader.CookieHandler")
@patch("dingtalk_downloader.core.downloader.M3u8Parser")
@patch("dingtalk_downloader.core.downloader.NM3u8DLRE")
def test_batch_download_flow(mock_n_m3u8dl_re, mock_m3u8_parser, mock_cookie_handler):
    """测试批量下载流程"""
    mock_cookie_handler.return_value.get_cookie.return_value = (
        Mock(),
        {"test": "value"},
        {"User-Agent": "Mozilla/5.0"},
        "测试直播",
    )
    mock_cookie_handler.return_value.repeat_get_cookie.return_value = (
        {"test": "value"},
        {"User-Agent": "Mozilla/5.0"},
        "测试直播",
    )
    mock_m3u8_parser.return_value.fetch_m3u8_links.return_value = ["https://test.com/test.m3u8"]
    mock_m3u8_parser.return_value.download_m3u8_file.return_value = "output.m3u8"
    mock_m3u8_parser.return_value.extract_prefix.return_value = "https://test.com/live_hp/123"
    mock_n_m3u8dl_re.return_value.download.return_value = True

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)

    with patch("builtins.input", side_effect=["q"]):
        downloader.download_batch_videos(
            {0: "https://n.dingtalk.com/test1", 1: "https://n.dingtalk.com/test2"}
        )

    mock_cookie_handler.return_value.get_cookie.assert_called_once()
    mock_cookie_handler.return_value.repeat_get_cookie.assert_called_once()
    mock_n_m3u8dl_re.return_value.download.assert_called()
