"""
钉钉直播回放下载工具 - downloader 单元测试

本模块测试下载器类。

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

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from dingtalk_downloader.core.downloader import Downloader
from dingtalk_downloader.config.constants import BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT


@patch('src.dingtalk_downloader.core.downloader.CookieHandler')
@patch('src.dingtalk_downloader.core.downloader.M3u8Parser')
@patch('src.dingtalk_downloader.core.downloader.NM3u8DLRE')
def test_downloader_init(mock_n_m3u8dl_re, mock_m3u8_parser, mock_cookie_handler):
    """测试初始化下载器"""
    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)

    assert downloader.browser_type == BROWSER_TYPE_EDGE
    assert downloader.save_mode == SAVE_MODE_DEFAULT
    assert downloader.cookie_handler is not None


@patch('src.dingtalk_downloader.core.downloader.CookieHandler')
@patch('src.dingtalk_downloader.core.downloader.M3u8Parser')
@patch('src.dingtalk_downloader.core.downloader.NM3u8DLRE')
def test_downloader_close(mock_n_m3u8dl_re, mock_m3u8_parser, mock_cookie_handler):
    """测试关闭下载器"""
    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)
    downloader.close()

    mock_cookie_handler.return_value.close.assert_called_once()
