"""
钉钉直播回放下载工具 - video_download_manager 单元测试

本模块测试视频下载管理器类。

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

from dingtalk_downloader.core.video_download_manager import VideoDownloadManager
from dingtalk_downloader.config.constants import (
    BROWSER_TYPE_EDGE,
    BROWSER_TYPE_CHROME,
    BROWSER_TYPE_FIREFOX,
    SAVE_MODE_DEFAULT,
    SAVE_MODE_MANUAL,
)
from dingtalk_downloader.utils.models import CookieData, HeadersData, VideoDownloadContext


@patch("dingtalk_downloader.core.video_download_manager.CookieHandler")
@patch("dingtalk_downloader.core.video_download_manager.PathSelector")
@patch("dingtalk_downloader.core.video_download_manager.NM3u8DLRE")
def test_video_download_manager_init_edge_default(
    mock_n_m3u8dl_re_class, mock_path_selector_class, mock_cookie_handler_class
):
    """测试Edge浏览器默认模式初始化"""
    mock_cookie_handler = Mock()
    mock_cookie_handler_class.return_value = mock_cookie_handler

    mock_path_selector = Mock()
    mock_path_selector.save_mode = SAVE_MODE_DEFAULT
    mock_path_selector_class.return_value = mock_path_selector

    mock_n_m3u8dl_re = Mock()
    mock_n_m3u8dl_re_class.return_value = mock_n_m3u8dl_re

    manager = VideoDownloadManager(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)

    assert manager.browser_type == BROWSER_TYPE_EDGE
    assert manager.cookie_handler == mock_cookie_handler
    assert manager.path_selector == mock_path_selector
    assert manager.n_m3u8dl_re == mock_n_m3u8dl_re
    mock_cookie_handler_class.assert_called_once_with(BROWSER_TYPE_EDGE)
    mock_path_selector_class.assert_called_once_with(SAVE_MODE_DEFAULT)
    mock_n_m3u8dl_re_class.assert_called_once()


@patch("dingtalk_downloader.core.video_download_manager.CookieHandler")
@patch("dingtalk_downloader.core.video_download_manager.PathSelector")
@patch("dingtalk_downloader.core.video_download_manager.NM3u8DLRE")
def test_video_download_manager_init_chrome_manual(
    mock_n_m3u8dl_re_class, mock_path_selector_class, mock_cookie_handler_class
):
    """测试Chrome浏览器手动模式初始化"""
    mock_cookie_handler = Mock()
    mock_cookie_handler_class.return_value = mock_cookie_handler

    mock_path_selector = Mock()
    mock_path_selector.save_mode = SAVE_MODE_MANUAL
    mock_path_selector_class.return_value = mock_path_selector

    mock_n_m3u8dl_re = Mock()
    mock_n_m3u8dl_re_class.return_value = mock_n_m3u8dl_re

    manager = VideoDownloadManager(BROWSER_TYPE_CHROME, SAVE_MODE_MANUAL)

    assert manager.browser_type == BROWSER_TYPE_CHROME
    assert manager.cookie_handler == mock_cookie_handler
    assert manager.path_selector == mock_path_selector
    assert manager.n_m3u8dl_re == mock_n_m3u8dl_re
    mock_cookie_handler_class.assert_called_once_with(BROWSER_TYPE_CHROME)
    mock_path_selector_class.assert_called_once_with(SAVE_MODE_MANUAL)
    mock_n_m3u8dl_re_class.assert_called_once()


@patch("dingtalk_downloader.core.video_download_manager.CookieHandler")
@patch("dingtalk_downloader.core.video_download_manager.PathSelector")
@patch("dingtalk_downloader.core.video_download_manager.NM3u8DLRE")
def test_video_download_manager_init_firefox_manual(
    mock_n_m3u8dl_re_class, mock_path_selector_class, mock_cookie_handler_class
):
    """测试Firefox浏览器手动模式初始化"""
    mock_cookie_handler = Mock()
    mock_cookie_handler_class.return_value = mock_cookie_handler

    mock_path_selector = Mock()
    mock_path_selector.save_mode = SAVE_MODE_MANUAL
    mock_path_selector_class.return_value = mock_path_selector

    mock_n_m3u8dl_re = Mock()
    mock_n_m3u8dl_re_class.return_value = mock_n_m3u8dl_re

    manager = VideoDownloadManager(BROWSER_TYPE_FIREFOX, SAVE_MODE_MANUAL)

    assert manager.browser_type == BROWSER_TYPE_FIREFOX
    assert manager.cookie_handler == mock_cookie_handler
    assert manager.path_selector == mock_path_selector
    assert manager.n_m3u8dl_re == mock_n_m3u8dl_re
    mock_cookie_handler_class.assert_called_once_with(BROWSER_TYPE_FIREFOX)
    mock_path_selector_class.assert_called_once_with(SAVE_MODE_MANUAL)
    mock_n_m3u8dl_re_class.assert_called_once()


@patch("dingtalk_downloader.core.video_download_manager.CookieHandler")
@patch("dingtalk_downloader.core.video_download_manager.PathSelector")
@patch("dingtalk_downloader.core.video_download_manager.NM3u8DLRE")
def test_initialize_download_success(
    mock_n_m3u8dl_re_class, mock_path_selector_class, mock_cookie_handler_class
):
    """测试初始化下载成功"""
    mock_cookie_handler = Mock()
    mock_cookie_handler_class.return_value = mock_cookie_handler

    mock_path_selector = Mock()
    mock_path_selector.save_mode = SAVE_MODE_DEFAULT
    mock_path_selector_class.return_value = mock_path_selector

    mock_n_m3u8dl_re = Mock()
    mock_n_m3u8dl_re_class.return_value = mock_n_m3u8dl_re

    mock_browser = Mock()
    mock_cookie_data = CookieData({"session": "test"})
    mock_headers_data = HeadersData({"User-Agent": "Mozilla/5.0"})

    mock_cookie_handler.get_cookie.return_value = (
        mock_browser,
        mock_cookie_data,
        mock_headers_data,
        "测试直播",
    )

    manager = VideoDownloadManager(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)
    context = manager.initialize_download("https://n.dingtalk.com/test")

    assert context.url == "https://n.dingtalk.com/test"
    assert context.cookie_data == mock_cookie_data
    assert context.headers_data == mock_headers_data
    assert context.live_name == "测试直播"
    assert context.save_mode == SAVE_MODE_DEFAULT
    assert manager.m3u8_parser is not None
    assert manager.m3u8_download_service is not None
    mock_cookie_handler.get_cookie.assert_called_once_with("https://n.dingtalk.com/test")


@patch("dingtalk_downloader.core.video_download_manager.CookieHandler")
@patch("dingtalk_downloader.core.video_download_manager.PathSelector")
@patch("dingtalk_downloader.core.video_download_manager.NM3u8DLRE")
def test_initialize_download_cookie_error(
    mock_n_m3u8dl_re_class, mock_path_selector_class, mock_cookie_handler_class
):
    """测试初始化下载Cookie错误"""
    from dingtalk_downloader.core.exceptions import CookieError

    mock_cookie_handler = Mock()
    mock_cookie_handler_class.return_value = mock_cookie_handler

    mock_path_selector = Mock()
    mock_path_selector.save_mode = SAVE_MODE_DEFAULT
    mock_path_selector_class.return_value = mock_path_selector

    mock_n_m3u8dl_re = Mock()
    mock_n_m3u8dl_re_class.return_value = mock_n_m3u8dl_re

    mock_cookie_handler.get_cookie.side_effect = CookieError("获取Cookie失败")

    manager = VideoDownloadManager(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)

    with pytest.raises(CookieError):
        manager.initialize_download("https://n.dingtalk.com/test")

    mock_cookie_handler.get_cookie.assert_called_once_with("https://n.dingtalk.com/test")


@patch("dingtalk_downloader.core.video_download_manager.CookieHandler")
@patch("dingtalk_downloader.core.video_download_manager.PathSelector")
@patch("dingtalk_downloader.core.video_download_manager.NM3u8DLRE")
def test_repeat_get_context_success(
    mock_n_m3u8dl_re_class, mock_path_selector_class, mock_cookie_handler_class
):
    """测试重复获取上下文成功"""
    mock_cookie_handler = Mock()
    mock_cookie_handler_class.return_value = mock_cookie_handler

    mock_path_selector = Mock()
    mock_path_selector.save_mode = SAVE_MODE_DEFAULT
    mock_path_selector_class.return_value = mock_path_selector

    mock_n_m3u8dl_re = Mock()
    mock_n_m3u8dl_re_class.return_value = mock_n_m3u8dl_re

    mock_cookie_data = CookieData({"session": "test"})
    mock_headers_data = HeadersData({"User-Agent": "Mozilla/5.0"})

    mock_cookie_handler.repeat_get_cookie.return_value = (
        mock_cookie_data,
        mock_headers_data,
        "测试直播",
    )

    manager = VideoDownloadManager(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)
    context = manager.repeat_get_context("https://n.dingtalk.com/test")

    assert context.url == "https://n.dingtalk.com/test"
    assert context.cookie_data == mock_cookie_data
    assert context.headers_data == mock_headers_data
    assert context.live_name == "测试直播"
    assert context.save_mode == SAVE_MODE_DEFAULT
    mock_cookie_handler.repeat_get_cookie.assert_called_once_with("https://n.dingtalk.com/test")


@patch("dingtalk_downloader.core.video_download_manager.CookieHandler")
@patch("dingtalk_downloader.core.video_download_manager.PathSelector")
@patch("dingtalk_downloader.core.video_download_manager.NM3u8DLRE")
def test_repeat_get_context_first_call(
    mock_n_m3u8dl_re_class, mock_path_selector_class, mock_cookie_handler_class
):
    """测试重复获取上下文首次调用"""
    mock_cookie_handler = Mock()
    mock_cookie_handler_class.return_value = mock_cookie_handler

    mock_path_selector = Mock()
    mock_path_selector.save_mode = SAVE_MODE_DEFAULT
    mock_path_selector_class.return_value = mock_path_selector

    mock_n_m3u8dl_re = Mock()
    mock_n_m3u8dl_re_class.return_value = mock_n_m3u8dl_re

    mock_cookie_data = CookieData({"session": "test"})
    mock_headers_data = HeadersData({"User-Agent": "Mozilla/5.0"})

    mock_cookie_handler.repeat_get_cookie.return_value = (
        mock_cookie_data,
        mock_headers_data,
        "测试直播",
    )

    manager = VideoDownloadManager(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)
    context = manager.repeat_get_context("https://n.dingtalk.com/test")

    assert context.url == "https://n.dingtalk.com/test"
    assert context.cookie_data == mock_cookie_data
    assert context.headers_data == mock_headers_data
    assert context.live_name == "测试直播"
    assert context.save_mode == SAVE_MODE_DEFAULT
    mock_cookie_handler.repeat_get_cookie.assert_called_once_with("https://n.dingtalk.com/test")


@patch("dingtalk_downloader.core.video_download_manager.CookieHandler")
@patch("dingtalk_downloader.core.video_download_manager.PathSelector")
@patch("dingtalk_downloader.core.video_download_manager.NM3u8DLRE")
@patch("os.path.exists")
def test_process_video_success(
    mock_exists, mock_n_m3u8dl_re_class, mock_path_selector_class, mock_cookie_handler_class
):
    """测试处理视频成功"""
    mock_exists.return_value = True

    mock_cookie_handler = Mock()
    mock_cookie_handler_class.return_value = mock_cookie_handler

    mock_path_selector = Mock()
    mock_path_selector.save_mode = SAVE_MODE_DEFAULT
    mock_path_selector_class.return_value = mock_path_selector

    mock_n_m3u8dl_re = Mock()
    mock_n_m3u8dl_re_class.return_value = mock_n_m3u8dl_re

    mock_browser = Mock()
    mock_cookie_data = CookieData({"session": "test"})
    mock_headers_data = HeadersData({"User-Agent": "Mozilla/5.0"})

    mock_cookie_handler.get_cookie.return_value = (
        mock_browser,
        mock_cookie_data,
        mock_headers_data,
        "测试直播",
    )

    mock_m3u8_link = Mock()
    mock_m3u8_link.url = "https://test.com/video.m3u8"
    mock_m3u8_link.prefix = "https://test.com/"
    mock_m3u8_link.local_file_path = "/path/to/video.m3u8"

    mock_m3u8_download_service = Mock()
    mock_m3u8_download_service.fetch_and_download_m3u8.return_value = mock_m3u8_link

    mock_path_selector.get_save_dir.return_value = "/downloads"

    mock_n_m3u8dl_re.download.return_value = True

    manager = VideoDownloadManager(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)
    context = manager.initialize_download("https://n.dingtalk.com/test")
    manager.m3u8_download_service = mock_m3u8_download_service

    result = manager.process_video(context)

    assert result is True
    mock_m3u8_download_service.fetch_and_download_m3u8.assert_called_once()
    mock_path_selector.get_save_dir.assert_called_once()
    mock_n_m3u8dl_re.download.assert_called_once()


@patch("dingtalk_downloader.core.video_download_manager.CookieHandler")
@patch("dingtalk_downloader.core.video_download_manager.PathSelector")
@patch("dingtalk_downloader.core.video_download_manager.NM3u8DLRE")
@patch("os.path.exists")
def test_process_video_failure(
    mock_exists, mock_n_m3u8dl_re_class, mock_path_selector_class, mock_cookie_handler_class
):
    """测试处理视频失败"""
    mock_exists.return_value = True

    mock_cookie_handler = Mock()
    mock_cookie_handler_class.return_value = mock_cookie_handler

    mock_path_selector = Mock()
    mock_path_selector.save_mode = SAVE_MODE_DEFAULT
    mock_path_selector_class.return_value = mock_path_selector

    mock_n_m3u8dl_re = Mock()
    mock_n_m3u8dl_re_class.return_value = mock_n_m3u8dl_re

    mock_browser = Mock()
    mock_cookie_data = CookieData({"session": "test"})
    mock_headers_data = HeadersData({"User-Agent": "Mozilla/5.0"})

    mock_cookie_handler.get_cookie.return_value = (
        mock_browser,
        mock_cookie_data,
        mock_headers_data,
        "测试直播",
    )

    mock_m3u8_link = Mock()
    mock_m3u8_link.url = "https://test.com/video.m3u8"
    mock_m3u8_link.prefix = "https://test.com/"
    mock_m3u8_link.local_file_path = "/path/to/video.m3u8"

    mock_m3u8_download_service = Mock()
    mock_m3u8_download_service.fetch_and_download_m3u8.return_value = mock_m3u8_link

    mock_path_selector.get_save_dir.return_value = "/downloads"

    mock_n_m3u8dl_re.download.return_value = False

    manager = VideoDownloadManager(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)
    context = manager.initialize_download("https://n.dingtalk.com/test")
    manager.m3u8_download_service = mock_m3u8_download_service

    result = manager.process_video(context)

    assert result is False
    mock_m3u8_download_service.fetch_and_download_m3u8.assert_called_once()
    mock_path_selector.get_save_dir.assert_called_once()
    mock_n_m3u8dl_re.download.assert_called_once()


@patch("dingtalk_downloader.core.video_download_manager.CookieHandler")
@patch("dingtalk_downloader.core.video_download_manager.PathSelector")
@patch("dingtalk_downloader.core.video_download_manager.NM3u8DLRE")
def test_process_video_m3u8_download_error(
    mock_n_m3u8dl_re_class, mock_path_selector_class, mock_cookie_handler_class
):
    """测试处理视频m3u8下载错误"""
    from dingtalk_downloader.core.exceptions import DownloadError

    mock_cookie_handler = Mock()
    mock_cookie_handler_class.return_value = mock_cookie_handler

    mock_path_selector = Mock()
    mock_path_selector.save_mode = SAVE_MODE_DEFAULT
    mock_path_selector_class.return_value = mock_path_selector

    mock_n_m3u8dl_re = Mock()
    mock_n_m3u8dl_re_class.return_value = mock_n_m3u8dl_re

    mock_browser = Mock()
    mock_cookie_data = CookieData({"session": "test"})
    mock_headers_data = HeadersData({"User-Agent": "Mozilla/5.0"})

    mock_cookie_handler.get_cookie.return_value = (
        mock_browser,
        mock_cookie_data,
        mock_headers_data,
        "测试直播",
    )

    mock_m3u8_download_service = Mock()
    mock_m3u8_download_service.fetch_and_download_m3u8.side_effect = DownloadError("m3u8下载失败")

    manager = VideoDownloadManager(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)
    context = manager.initialize_download("https://n.dingtalk.com/test")
    manager.m3u8_download_service = mock_m3u8_download_service

    with pytest.raises(DownloadError):
        manager.process_video(context)

    mock_m3u8_download_service.fetch_and_download_m3u8.assert_called_once()


@patch("dingtalk_downloader.core.video_download_manager.CookieHandler")
@patch("dingtalk_downloader.core.video_download_manager.PathSelector")
@patch("dingtalk_downloader.core.video_download_manager.NM3u8DLRE")
def test_close(mock_n_m3u8dl_re_class, mock_path_selector_class, mock_cookie_handler_class):
    """测试关闭管理器"""
    mock_cookie_handler = Mock()
    mock_cookie_handler_class.return_value = mock_cookie_handler

    mock_path_selector = Mock()
    mock_path_selector.save_mode = SAVE_MODE_DEFAULT
    mock_path_selector_class.return_value = mock_path_selector

    mock_n_m3u8dl_re = Mock()
    mock_n_m3u8dl_re_class.return_value = mock_n_m3u8dl_re

    manager = VideoDownloadManager(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)

    manager.close()

    mock_cookie_handler.close.assert_called_once()
