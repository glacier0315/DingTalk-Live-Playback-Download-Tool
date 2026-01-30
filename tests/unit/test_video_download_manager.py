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
import time
from unittest.mock import Mock, patch, call

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
    mock_path_selector.save_mode = str(SAVE_MODE_DEFAULT)
    mock_path_selector_class.return_value = mock_path_selector

    mock_n_m3u8dl_re = Mock()
    mock_n_m3u8dl_re_class.return_value = mock_n_m3u8dl_re

    manager = VideoDownloadManager(BROWSER_TYPE_EDGE, str(SAVE_MODE_DEFAULT))

    assert manager.browser_type == BROWSER_TYPE_EDGE
    assert manager.cookie_handler is None
    assert manager.path_selector is None
    assert manager.n_m3u8dl_re is None
    mock_cookie_handler_class.assert_not_called()
    mock_path_selector_class.assert_not_called()
    mock_n_m3u8dl_re_class.assert_not_called()


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
    mock_path_selector.save_mode = str(SAVE_MODE_MANUAL)
    mock_path_selector_class.return_value = mock_path_selector

    mock_n_m3u8dl_re = Mock()
    mock_n_m3u8dl_re_class.return_value = mock_n_m3u8dl_re

    manager = VideoDownloadManager(BROWSER_TYPE_CHROME, str(SAVE_MODE_MANUAL))

    assert manager.browser_type == BROWSER_TYPE_CHROME
    assert manager.cookie_handler is None
    assert manager.path_selector is None
    assert manager.n_m3u8dl_re is None
    mock_cookie_handler_class.assert_not_called()
    mock_path_selector_class.assert_not_called()
    mock_n_m3u8dl_re_class.assert_not_called()


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
    mock_path_selector.save_mode = str(SAVE_MODE_MANUAL)
    mock_path_selector_class.return_value = mock_path_selector

    mock_n_m3u8dl_re = Mock()
    mock_n_m3u8dl_re_class.return_value = mock_n_m3u8dl_re

    manager = VideoDownloadManager(BROWSER_TYPE_FIREFOX, str(SAVE_MODE_MANUAL))

    assert manager.browser_type == BROWSER_TYPE_FIREFOX
    assert manager.cookie_handler is None
    assert manager.path_selector is None
    assert manager.n_m3u8dl_re is None
    mock_cookie_handler_class.assert_not_called()
    mock_path_selector_class.assert_not_called()
    mock_n_m3u8dl_re_class.assert_not_called()


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


@patch("dingtalk_downloader.core.video_download_manager.time.sleep")
@patch("dingtalk_downloader.core.video_download_manager.random.uniform")
@patch("dingtalk_downloader.core.video_download_manager.CookieHandler")
@patch("dingtalk_downloader.core.video_download_manager.PathSelector")
@patch("dingtalk_downloader.core.video_download_manager.NM3u8DLRE")
@patch("os.path.exists")
def test_process_video_failure(
    mock_exists, mock_n_m3u8dl_re_class, mock_path_selector_class, 
    mock_cookie_handler_class, mock_random, mock_sleep
):
    """测试处理视频失败"""
    mock_exists.return_value = True

    mock_cookie_handler = Mock()
    mock_cookie_handler_class.return_value = mock_cookie_handler

    mock_path_selector = Mock()
    mock_path_selector.save_mode = str(SAVE_MODE_DEFAULT)
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

    mock_cookie_handler.repeat_get_cookie.return_value = (
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
    mock_random.return_value = 5.0

    manager = VideoDownloadManager(BROWSER_TYPE_EDGE, str(SAVE_MODE_DEFAULT))
    context = manager.initialize_download("https://n.dingtalk.com/test")
    manager.m3u8_download_service = mock_m3u8_download_service

    result = manager.process_video(context)

    assert result is False
    assert mock_n_m3u8dl_re.download.call_count == 20
    mock_sleep.assert_called()


@patch("dingtalk_downloader.core.video_download_manager.time.sleep")
@patch("dingtalk_downloader.core.video_download_manager.random.uniform")
@patch("dingtalk_downloader.core.video_download_manager.CookieHandler")
@patch("dingtalk_downloader.core.video_download_manager.PathSelector")
@patch("dingtalk_downloader.core.video_download_manager.NM3u8DLRE")
def test_process_video_m3u8_download_error(
    mock_n_m3u8dl_re_class, mock_path_selector_class, 
    mock_cookie_handler_class, mock_random, mock_sleep
):
    """测试处理视频m3u8下载错误"""
    from dingtalk_downloader.core.exceptions import DownloadError

    mock_cookie_handler = Mock()
    mock_cookie_handler_class.return_value = mock_cookie_handler

    mock_path_selector = Mock()
    mock_path_selector.save_mode = str(SAVE_MODE_DEFAULT)
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

    mock_cookie_handler.repeat_get_cookie.return_value = (
        mock_cookie_data,
        mock_headers_data,
        "测试直播",
    )

    mock_m3u8_download_service = Mock()
    mock_m3u8_download_service.fetch_and_download_m3u8.side_effect = Exception("m3u8下载失败")
    manager = VideoDownloadManager(BROWSER_TYPE_EDGE, str(SAVE_MODE_DEFAULT))
    context = manager.initialize_download("https://n.dingtalk.com/test")
    manager.m3u8_download_service = mock_m3u8_download_service
    
    mock_random.return_value = 5.0
    
    with pytest.raises(DownloadError):
        manager.process_video(context)
    
    assert mock_m3u8_download_service.fetch_and_download_m3u8.call_count == 20
    mock_sleep.assert_called()


@patch("dingtalk_downloader.core.video_download_manager.CookieHandler")
@patch("dingtalk_downloader.core.video_download_manager.PathSelector")
@patch("dingtalk_downloader.core.video_download_manager.NM3u8DLRE")
def test_close(mock_n_m3u8dl_re_class, mock_path_selector_class, mock_cookie_handler_class):
    """测试关闭管理器"""
    mock_cookie_handler = Mock()
    mock_cookie_handler_class.return_value = mock_cookie_handler

    mock_path_selector = Mock()
    mock_path_selector.save_mode = str(SAVE_MODE_DEFAULT)
    mock_path_selector_class.return_value = mock_path_selector

    mock_n_m3u8dl_re = Mock()
    mock_n_m3u8dl_re_class.return_value = mock_n_m3u8dl_re

    manager = VideoDownloadManager(BROWSER_TYPE_EDGE, str(SAVE_MODE_DEFAULT))
    
    # 初始化cookie_handler以确保close()能够调用它
    manager.cookie_handler = mock_cookie_handler

    manager.close()

    mock_cookie_handler.close.assert_called_once()


def test_video_download_manager_init_with_dependency_injection():
    """测试使用依赖注入初始化"""
    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()

    manager = VideoDownloadManager(
        BROWSER_TYPE_EDGE,
        SAVE_MODE_DEFAULT,
        cookie_handler=mock_cookie_handler,
        path_selector=mock_path_selector,
        n_m3u8dl_re=mock_n_m3u8dl_re,
    )

    assert manager.browser_type == BROWSER_TYPE_EDGE
    assert manager.cookie_handler == mock_cookie_handler
    assert manager.path_selector == mock_path_selector
    assert manager.n_m3u8dl_re == mock_n_m3u8dl_re


def test_initialize_download_with_injected_dependencies():
    """测试使用注入的依赖初始化下载"""
    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_path_selector.save_mode = str(SAVE_MODE_DEFAULT)
    mock_m3u8_parser = Mock()
    mock_m3u8_download_service = Mock()
    mock_n_m3u8dl_re = Mock()

    mock_browser = Mock()
    mock_cookie_data = CookieData({"session": "test"})
    mock_headers_data = HeadersData({"User-Agent": "Mozilla/5.0"})

    mock_cookie_handler.get_cookie.return_value = (
        mock_browser,
        mock_cookie_data,
        mock_headers_data,
        "测试直播",
    )

    manager = VideoDownloadManager(
        BROWSER_TYPE_EDGE,
        str(SAVE_MODE_DEFAULT),
        cookie_handler=mock_cookie_handler,
        m3u8_parser=mock_m3u8_parser,
        m3u8_download_service=mock_m3u8_download_service,
        path_selector=mock_path_selector,
        n_m3u8dl_re=mock_n_m3u8dl_re,
    )

    context = manager.initialize_download("https://n.dingtalk.com/test")

    assert context.url == "https://n.dingtalk.com/test"
    assert context.cookie_data == mock_cookie_data
    assert context.headers_data == mock_headers_data
    assert context.live_name == "测试直播"
    assert manager.m3u8_parser == mock_m3u8_parser
    assert manager.m3u8_download_service == mock_m3u8_download_service
    assert manager.n_m3u8dl_re == mock_n_m3u8dl_re
    mock_cookie_handler.get_cookie.assert_called_once_with("https://n.dingtalk.com/test")


def test_repeat_get_context_with_injected_dependencies():
    """测试使用注入的依赖重复获取上下文"""
    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_path_selector.save_mode = str(SAVE_MODE_DEFAULT)

    mock_cookie_data = CookieData({"session": "test"})
    mock_headers_data = HeadersData({"User-Agent": "Mozilla/5.0"})

    mock_cookie_handler.repeat_get_cookie.return_value = (
        mock_cookie_data,
        mock_headers_data,
        "测试直播",
    )

    manager = VideoDownloadManager(
        BROWSER_TYPE_EDGE,
        str(SAVE_MODE_DEFAULT),
        cookie_handler=mock_cookie_handler,
        path_selector=mock_path_selector,
    )

    context = manager.repeat_get_context("https://n.dingtalk.com/test")

    assert context.url == "https://n.dingtalk.com/test"
    assert context.cookie_data == mock_cookie_data
    assert context.headers_data == mock_headers_data
    assert context.live_name == "测试直播"
    mock_cookie_handler.repeat_get_cookie.assert_called_once_with("https://n.dingtalk.com/test")


@patch("os.path.exists")
def test_download_video_with_injected_dependencies(mock_exists):
    """测试使用注入的依赖下载视频"""
    mock_exists.return_value = True

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_m3u8_download_service = Mock()
    mock_n_m3u8dl_re = Mock()

    mock_m3u8_link = Mock()
    mock_m3u8_link.url = "https://test.com/video.m3u8"
    mock_m3u8_link.prefix = "https://test.com/"
    mock_m3u8_link.local_file_path = "/path/to/video.m3u8"

    mock_m3u8_download_service.fetch_and_download_m3u8.return_value = mock_m3u8_link
    mock_path_selector.get_save_dir.return_value = "/downloads"
    mock_n_m3u8dl_re.download.return_value = True

    manager = VideoDownloadManager(
        BROWSER_TYPE_EDGE,
        SAVE_MODE_DEFAULT,
        cookie_handler=mock_cookie_handler,
        m3u8_download_service=mock_m3u8_download_service,
        path_selector=mock_path_selector,
        n_m3u8dl_re=mock_n_m3u8dl_re,
    )

    context = VideoDownloadContext(
        url="https://n.dingtalk.com/test",
        cookie_data=CookieData({"session": "test"}),
        headers_data=HeadersData({"User-Agent": "Mozilla/5.0"}),
        live_name="测试直播",
        save_mode=SAVE_MODE_DEFAULT,
    )

    result = manager.process_video(context)

    assert result is True
    mock_m3u8_download_service.fetch_and_download_m3u8.assert_called_once()
    mock_path_selector.get_save_dir.assert_called_once()
    mock_n_m3u8dl_re.download.assert_called_once()


def test_cleanup_context_with_injected_dependencies():
    """测试使用注入的依赖清理上下文"""
    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_m3u8_parser = Mock()
    mock_m3u8_download_service = Mock()

    manager = VideoDownloadManager(
        BROWSER_TYPE_EDGE,
        SAVE_MODE_DEFAULT,
        cookie_handler=mock_cookie_handler,
        m3u8_parser=mock_m3u8_parser,
        m3u8_download_service=mock_m3u8_download_service,
        path_selector=mock_path_selector,
    )

    context = VideoDownloadContext(
        url="https://n.dingtalk.com/test",
        cookie_data=CookieData({"session": "test"}),
        headers_data=HeadersData({"User-Agent": "Mozilla/5.0"}),
        live_name="测试直播",
        save_mode=SAVE_MODE_DEFAULT,
    )

    manager.cleanup_context(context)

    assert manager.m3u8_parser is None
    assert manager.m3u8_download_service is None


@patch("dingtalk_downloader.core.video_download_manager.time.sleep")
@patch("dingtalk_downloader.core.video_download_manager.random.uniform")
@patch("os.path.exists")
def test_process_video_with_retry_success(mock_exists, mock_random, mock_sleep):
    """测试重试机制在失败后重试成功"""
    mock_exists.return_value = True

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_path_selector.save_mode = str(SAVE_MODE_DEFAULT)
    mock_m3u8_download_service = Mock()
    mock_n_m3u8dl_re = Mock()

    mock_m3u8_link = Mock()
    mock_m3u8_link.url = "https://test.com/video.m3u8"
    mock_m3u8_link.prefix = "https://test.com/"
    mock_m3u8_link.local_file_path = "/path/to/video.m3u8"

    mock_cookie_data = CookieData({"session": "test"})
    mock_headers_data = HeadersData({"User-Agent": "Mozilla/5.0"})

    mock_cookie_handler.repeat_get_cookie.return_value = (
        mock_cookie_data,
        mock_headers_data,
        "测试直播",
    )

    mock_m3u8_download_service.fetch_and_download_m3u8.return_value = mock_m3u8_link
    mock_path_selector.get_save_dir.return_value = "/downloads"

    mock_n_m3u8dl_re.download.side_effect = [False, True]
    mock_random.return_value = 5.0

    manager = VideoDownloadManager(
        BROWSER_TYPE_EDGE,
        str(SAVE_MODE_DEFAULT),
        cookie_handler=mock_cookie_handler,
        m3u8_download_service=mock_m3u8_download_service,
        path_selector=mock_path_selector,
        n_m3u8dl_re=mock_n_m3u8dl_re,
    )

    context = VideoDownloadContext(
        url="https://n.dingtalk.com/test",
        cookie_data=mock_cookie_data,
        headers_data=mock_headers_data,
        live_name="测试直播",
        save_mode=str(SAVE_MODE_DEFAULT),
    )

    result = manager.process_video(context)

    assert result is True
    assert mock_n_m3u8dl_re.download.call_count == 2
    mock_sleep.assert_called_once_with(5.0)
    mock_cookie_handler.repeat_get_cookie.assert_called_once_with("https://n.dingtalk.com/test")


@patch("dingtalk_downloader.core.video_download_manager.time.sleep")
@patch("dingtalk_downloader.core.video_download_manager.random.uniform")
@patch("os.path.exists")
def test_process_video_with_retry_max_attempts(mock_exists, mock_random, mock_sleep):
    """测试重试机制达到最大重试次数后停止"""
    mock_exists.return_value = True

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_path_selector.save_mode = str(SAVE_MODE_DEFAULT)
    mock_m3u8_download_service = Mock()
    mock_n_m3u8dl_re = Mock()

    mock_m3u8_link = Mock()
    mock_m3u8_link.url = "https://test.com/video.m3u8"
    mock_m3u8_link.prefix = "https://test.com/"
    mock_m3u8_link.local_file_path = "/path/to/video.m3u8"

    mock_cookie_data = CookieData({"session": "test"})
    mock_headers_data = HeadersData({"User-Agent": "Mozilla/5.0"})

    mock_cookie_handler.repeat_get_cookie.return_value = (
        mock_cookie_data,
        mock_headers_data,
        "测试直播",
    )

    mock_m3u8_download_service.fetch_and_download_m3u8.return_value = mock_m3u8_link
    mock_path_selector.get_save_dir.return_value = "/downloads"

    mock_n_m3u8dl_re.download.return_value = False
    mock_random.return_value = 5.0

    manager = VideoDownloadManager(
        BROWSER_TYPE_EDGE,
        str(SAVE_MODE_DEFAULT),
        cookie_handler=mock_cookie_handler,
        m3u8_download_service=mock_m3u8_download_service,
        path_selector=mock_path_selector,
        n_m3u8dl_re=mock_n_m3u8dl_re,
    )

    context = VideoDownloadContext(
        url="https://n.dingtalk.com/test",
        cookie_data=mock_cookie_data,
        headers_data=mock_headers_data,
        live_name="测试直播",
        save_mode=str(SAVE_MODE_DEFAULT),
    )

    result = manager.process_video(context)

    assert result is False
    assert mock_n_m3u8dl_re.download.call_count == 20
    assert mock_sleep.call_count == 19
    assert mock_cookie_handler.repeat_get_cookie.call_count == 19


@patch("dingtalk_downloader.core.video_download_manager.time.sleep")
@patch("dingtalk_downloader.core.video_download_manager.random.uniform")
@patch("os.path.exists")
def test_process_video_with_retry_random_wait(mock_exists, mock_random, mock_sleep):
    """测试重试机制在每次重试前等待3-10秒"""
    mock_exists.return_value = True

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_path_selector.save_mode = str(SAVE_MODE_DEFAULT)
    mock_m3u8_download_service = Mock()
    mock_n_m3u8dl_re = Mock()

    mock_m3u8_link = Mock()
    mock_m3u8_link.url = "https://test.com/video.m3u8"
    mock_m3u8_link.prefix = "https://test.com/"
    mock_m3u8_link.local_file_path = "/path/to/video.m3u8"

    mock_cookie_data = CookieData({"session": "test"})
    mock_headers_data = HeadersData({"User-Agent": "Mozilla/5.0"})

    mock_cookie_handler.repeat_get_cookie.return_value = (
        mock_cookie_data,
        mock_headers_data,
        "测试直播",
    )

    mock_m3u8_download_service.fetch_and_download_m3u8.return_value = mock_m3u8_link
    mock_path_selector.get_save_dir.return_value = "/downloads"

    mock_n_m3u8dl_re.download.side_effect = [False, False, True]
    mock_random.side_effect = [3.5, 7.2]

    manager = VideoDownloadManager(
        BROWSER_TYPE_EDGE,
        str(SAVE_MODE_DEFAULT),
        cookie_handler=mock_cookie_handler,
        m3u8_download_service=mock_m3u8_download_service,
        path_selector=mock_path_selector,
        n_m3u8dl_re=mock_n_m3u8dl_re,
    )

    context = VideoDownloadContext(
        url="https://n.dingtalk.com/test",
        cookie_data=mock_cookie_data,
        headers_data=mock_headers_data,
        live_name="测试直播",
        save_mode=str(SAVE_MODE_DEFAULT),
    )

    result = manager.process_video(context)

    assert result is True
    assert mock_n_m3u8dl_re.download.call_count == 3
    assert mock_random.call_count == 2
    mock_sleep.assert_has_calls([call(3.5), call(7.2)])


@patch("dingtalk_downloader.core.video_download_manager.time.sleep")
@patch("dingtalk_downloader.core.video_download_manager.random.uniform")
@patch("os.path.exists")
def test_process_video_with_retry_refresh_m3u8_link(mock_exists, mock_random, mock_sleep):
    """测试重试机制在每次重试前重新获取m3u8链接"""
    mock_exists.return_value = True

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_path_selector.save_mode = str(SAVE_MODE_DEFAULT)
    mock_m3u8_download_service = Mock()
    mock_n_m3u8dl_re = Mock()

    mock_m3u8_link1 = Mock()
    mock_m3u8_link1.url = "https://test.com/video1.m3u8"
    mock_m3u8_link1.prefix = "https://test.com/"
    mock_m3u8_link1.local_file_path = "/path/to/video1.m3u8"

    mock_m3u8_link2 = Mock()
    mock_m3u8_link2.url = "https://test.com/video2.m3u8"
    mock_m3u8_link2.prefix = "https://test.com/"
    mock_m3u8_link2.local_file_path = "/path/to/video2.m3u8"

    mock_cookie_data = CookieData({"session": "test"})
    mock_headers_data = HeadersData({"User-Agent": "Mozilla/5.0"})

    mock_cookie_handler.repeat_get_cookie.return_value = (
        mock_cookie_data,
        mock_headers_data,
        "测试直播",
    )

    mock_m3u8_download_service.fetch_and_download_m3u8.side_effect = [
        mock_m3u8_link1,
        mock_m3u8_link2,
    ]
    mock_path_selector.get_save_dir.return_value = "/downloads"

    mock_n_m3u8dl_re.download.side_effect = [False, True]
    mock_random.return_value = 5.0

    manager = VideoDownloadManager(
        BROWSER_TYPE_EDGE,
        str(SAVE_MODE_DEFAULT),
        cookie_handler=mock_cookie_handler,
        m3u8_download_service=mock_m3u8_download_service,
        path_selector=mock_path_selector,
        n_m3u8dl_re=mock_n_m3u8dl_re,
    )

    context = VideoDownloadContext(
        url="https://n.dingtalk.com/test",
        cookie_data=mock_cookie_data,
        headers_data=mock_headers_data,
        live_name="测试直播",
        save_mode=str(SAVE_MODE_DEFAULT),
    )

    result = manager.process_video(context)

    assert result is True
    assert mock_m3u8_download_service.fetch_and_download_m3u8.call_count == 2
    mock_cookie_handler.repeat_get_cookie.assert_called_once_with("https://n.dingtalk.com/test")


@patch("dingtalk_downloader.core.video_download_manager.time.sleep")
@patch("dingtalk_downloader.core.video_download_manager.random.uniform")
@patch("os.path.exists")
def test_process_video_no_retry_on_first_success(mock_exists, mock_random, mock_sleep):
    """测试首次下载成功时不进行重试"""
    mock_exists.return_value = True

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_path_selector.save_mode = str(SAVE_MODE_DEFAULT)
    mock_m3u8_download_service = Mock()
    mock_n_m3u8dl_re = Mock()

    mock_m3u8_link = Mock()
    mock_m3u8_link.url = "https://test.com/video.m3u8"
    mock_m3u8_link.prefix = "https://test.com/"
    mock_m3u8_link.local_file_path = "/path/to/video.m3u8"

    mock_cookie_data = CookieData({"session": "test"})
    mock_headers_data = HeadersData({"User-Agent": "Mozilla/5.0"})

    mock_m3u8_download_service.fetch_and_download_m3u8.return_value = mock_m3u8_link
    mock_path_selector.get_save_dir.return_value = "/downloads"

    mock_n_m3u8dl_re.download.return_value = True

    manager = VideoDownloadManager(
        BROWSER_TYPE_EDGE,
        str(SAVE_MODE_DEFAULT),
        cookie_handler=mock_cookie_handler,
        m3u8_download_service=mock_m3u8_download_service,
        path_selector=mock_path_selector,
        n_m3u8dl_re=mock_n_m3u8dl_re,
    )

    context = VideoDownloadContext(
        url="https://n.dingtalk.com/test",
        cookie_data=mock_cookie_data,
        headers_data=mock_headers_data,
        live_name="测试直播",
        save_mode=str(SAVE_MODE_DEFAULT),
    )

    result = manager.process_video(context)

    assert result is True
    assert mock_n_m3u8dl_re.download.call_count == 1
    mock_sleep.assert_not_called()
    mock_random.assert_not_called()
    mock_cookie_handler.repeat_get_cookie.assert_not_called()


@patch("dingtalk_downloader.core.video_download_manager.time.sleep")
@patch("dingtalk_downloader.core.video_download_manager.random.uniform")
@patch("os.path.exists")
def test_process_video_with_exception_retry(mock_exists, mock_random, mock_sleep):
    """测试重试机制在异常情况下也能正常工作"""
    mock_exists.return_value = True

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_path_selector.save_mode = str(SAVE_MODE_DEFAULT)
    mock_m3u8_download_service = Mock()
    mock_n_m3u8dl_re = Mock()

    mock_m3u8_link = Mock()
    mock_m3u8_link.url = "https://test.com/video.m3u8"
    mock_m3u8_link.prefix = "https://test.com/"
    mock_m3u8_link.local_file_path = "/path/to/video.m3u8"

    mock_cookie_data = CookieData({"session": "test"})
    mock_headers_data = HeadersData({"User-Agent": "Mozilla/5.0"})

    mock_cookie_handler.repeat_get_cookie.return_value = (
        mock_cookie_data,
        mock_headers_data,
        "测试直播",
    )

    mock_m3u8_download_service.fetch_and_download_m3u8.return_value = mock_m3u8_link
    mock_path_selector.get_save_dir.return_value = "/downloads"

    from dingtalk_downloader.core.exceptions import DownloadError

    mock_n_m3u8dl_re.download.side_effect = [DownloadError("下载失败"), True]
    mock_random.return_value = 5.0

    manager = VideoDownloadManager(
        BROWSER_TYPE_EDGE,
        str(SAVE_MODE_DEFAULT),
        cookie_handler=mock_cookie_handler,
        m3u8_download_service=mock_m3u8_download_service,
        path_selector=mock_path_selector,
        n_m3u8dl_re=mock_n_m3u8dl_re,
    )

    context = VideoDownloadContext(
        url="https://n.dingtalk.com/test",
        cookie_data=mock_cookie_data,
        headers_data=mock_headers_data,
        live_name="测试直播",
        save_mode=str(SAVE_MODE_DEFAULT),
    )

    result = manager.process_video(context)

    assert result is True
    assert mock_n_m3u8dl_re.download.call_count == 2
    mock_sleep.assert_called_once_with(5.0)
    mock_cookie_handler.repeat_get_cookie.assert_called_once_with("https://n.dingtalk.com/test")
