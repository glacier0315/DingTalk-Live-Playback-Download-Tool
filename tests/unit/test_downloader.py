"""
钉钉直播回放下载工具 - downloader 单元测试

本模块测试下载器类。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2026-01-27: 重写-适配新的架构，使用VideoDownloadManager
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.core.downloader import Downloader
from dingtalk_downloader.core.dependency_factory import DependencyFactory
from dingtalk_downloader.core.exceptions import (
    DownloadError,
    BrowserError,
    NetworkError,
    ValidationError,
)
from dingtalk_downloader.core.cookie_handler import CookieError
from dingtalk_downloader.core.m3u8_parser import M3u8ParseError
from dingtalk_downloader.config.constants import (
    BROWSER_TYPE_EDGE,
    BROWSER_TYPE_CHROME,
    BROWSER_TYPE_FIREFOX,
    SAVE_MODE_DEFAULT,
    SAVE_MODE_MANUAL,
)
from dingtalk_downloader.utils.models import VideoDownloadContext


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_downloader_init_edge_default(mock_video_manager_class, mock_dependency_factory_class):
    """测试Edge浏览器默认模式初始化"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)

    assert downloader.browser_type == BROWSER_TYPE_EDGE
    assert downloader.save_mode == SAVE_MODE_DEFAULT
    assert downloader.video_manager == mock_video_manager
    assert downloader.dependency_factory == mock_dependency_factory
    mock_dependency_factory_class.assert_called_once()
    mock_dependency_factory.get_cookie_handler.assert_called_once_with(BROWSER_TYPE_EDGE)
    mock_dependency_factory.get_path_selector.assert_called_once_with(SAVE_MODE_DEFAULT)
    mock_dependency_factory.get_n_m3u8dl_re.assert_called_once()
    mock_video_manager_class.assert_called_once()


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_downloader_init_chrome_manual(mock_video_manager_class, mock_dependency_factory_class):
    """测试Chrome浏览器手动模式初始化"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    downloader = Downloader(BROWSER_TYPE_CHROME, SAVE_MODE_MANUAL, mock_user_controller)

    assert downloader.browser_type == BROWSER_TYPE_CHROME
    assert downloader.save_mode == SAVE_MODE_MANUAL
    assert downloader.video_manager == mock_video_manager
    assert downloader.dependency_factory == mock_dependency_factory
    mock_dependency_factory_class.assert_called_once()
    mock_dependency_factory.get_cookie_handler.assert_called_once_with(BROWSER_TYPE_CHROME)
    mock_dependency_factory.get_path_selector.assert_called_once_with(SAVE_MODE_MANUAL)
    mock_dependency_factory.get_n_m3u8dl_re.assert_called_once()
    mock_video_manager_class.assert_called_once()


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_downloader_init_firefox_manual(mock_video_manager_class, mock_dependency_factory_class):
    """测试Firefox浏览器手动模式初始化"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    downloader = Downloader(BROWSER_TYPE_FIREFOX, SAVE_MODE_MANUAL, mock_user_controller)

    assert downloader.browser_type == BROWSER_TYPE_FIREFOX
    assert downloader.save_mode == SAVE_MODE_MANUAL
    assert downloader.video_manager == mock_video_manager
    assert downloader.dependency_factory == mock_dependency_factory
    mock_dependency_factory_class.assert_called_once()
    mock_dependency_factory.get_cookie_handler.assert_called_once_with(BROWSER_TYPE_FIREFOX)
    mock_dependency_factory.get_path_selector.assert_called_once_with(SAVE_MODE_MANUAL)
    mock_dependency_factory.get_n_m3u8dl_re.assert_called_once()
    mock_video_manager_class.assert_called_once()


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_downloader_close(mock_video_manager_class, mock_dependency_factory_class):
    """测试关闭下载器"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)
    downloader.close()

    mock_video_manager.close.assert_called_once()


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_download_single_video_success(mock_video_manager_class, mock_dependency_factory_class):
    """测试单个视频下载成功"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    mock_context = Mock(spec=VideoDownloadContext)
    mock_context.live_name = "测试直播"
    mock_video_manager.initialize_download.return_value = mock_context
    mock_video_manager.process_video.return_value = True

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)

    mock_user_controller.get_user_input.return_value = "q"

    downloader.download_single_video("https://n.dingtalk.com/test?liveUuid=abc")

    mock_video_manager.initialize_download.assert_called_once_with(
        "https://n.dingtalk.com/test?liveUuid=abc"
    )
    mock_video_manager.process_video.assert_called_once_with(mock_context)
    mock_user_controller.get_user_input.assert_called_once()


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_download_single_video_failure(mock_video_manager_class, mock_dependency_factory_class):
    """测试单个视频下载失败"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    mock_context = Mock(spec=VideoDownloadContext)
    mock_context.live_name = "测试直播"
    mock_video_manager.initialize_download.return_value = mock_context
    mock_video_manager.process_video.return_value = False

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)

    mock_user_controller.get_user_input.return_value = "q"

    downloader.download_single_video("https://n.dingtalk.com/test?liveUuid=abc")

    mock_video_manager.initialize_download.assert_called_once_with(
        "https://n.dingtalk.com/test?liveUuid=abc"
    )
    mock_video_manager.process_video.assert_called_once_with(mock_context)
    mock_user_controller.get_user_input.assert_called_once()

@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_download_single_video_exit(mock_video_manager_class, mock_dependency_factory_class):
    """测试退出"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    mock_context = Mock(spec=VideoDownloadContext)
    mock_context.live_name = "测试直播"
    mock_video_manager.initialize_download.return_value = mock_context
    mock_video_manager.process_video.return_value = True

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)

    mock_user_controller.get_user_input.return_value = "q"

    downloader.download_single_video("https://n.dingtalk.com/test?liveUuid=abc")

    mock_video_manager.initialize_download.assert_called_once_with(
        "https://n.dingtalk.com/test?liveUuid=abc"
    )
    mock_video_manager.process_video.assert_called_once_with(mock_context)
    mock_user_controller.get_user_input.assert_called_once()


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_download_batch_videos_success(mock_video_manager_class, mock_dependency_factory_class):
    """测试批量下载成功"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    mock_context1 = Mock(spec=VideoDownloadContext)
    mock_context1.live_name = "测试直播1"
    mock_context2 = Mock(spec=VideoDownloadContext)
    mock_context2.live_name = "测试直播2"

    mock_video_manager.initialize_download.side_effect = [mock_context1, mock_context2]
    mock_video_manager.process_video.return_value = True

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)

    urls = {
        0: "https://n.dingtalk.com/test1?liveUuid=abc",
        1: "https://n.dingtalk.com/test2?liveUuid=def",
    }

    mock_user_controller.ask_continue_download.return_value = False

    downloader.download_batch_videos(urls)

    assert mock_video_manager.initialize_download.call_count == 2
    assert mock_video_manager.process_video.call_count == 2
    mock_user_controller.ask_continue_download.assert_called_once()


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_download_batch_videos_failure(mock_video_manager_class, mock_dependency_factory_class):
    """测试批量下载失败"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    mock_context = Mock(spec=VideoDownloadContext)
    mock_context.live_name = "测试直播"
    mock_video_manager.initialize_download.side_effect = [mock_context, mock_context]
    mock_video_manager.process_video.return_value = False

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)

    urls = {
        0: "https://n.dingtalk.com/test1?liveUuid=abc",
        1: "https://n.dingtalk.com/test2?liveUuid=def",
    }

    mock_user_controller.ask_continue_download.return_value = False

    downloader.download_batch_videos(urls)

    assert mock_video_manager.initialize_download.call_count == 2
    assert mock_video_manager.process_video.call_count == 2
    mock_user_controller.ask_continue_download.assert_called_once()


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_download_batch_videos_continue(mock_video_manager_class, mock_dependency_factory_class):
    """测试批量下载继续"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    mock_context1 = Mock(spec=VideoDownloadContext)
    mock_context1.live_name = "测试直播1"
    mock_context2 = Mock(spec=VideoDownloadContext)
    mock_context2.live_name = "测试直播2"

    mock_video_manager.initialize_download.side_effect = [mock_context1, mock_context2]
    mock_video_manager.process_video.return_value = True

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)

    urls = {
        0: "https://n.dingtalk.com/test1?liveUuid=abc",
        1: "https://n.dingtalk.com/test2?liveUuid=def",
    }

    mock_user_controller.ask_continue_download.return_value = False

    downloader.download_batch_videos(urls)

    assert mock_video_manager.initialize_download.call_count == 2
    assert mock_video_manager.process_video.call_count == 2
    mock_user_controller.ask_continue_download.assert_called_once()


def test_downloader_init_with_injected_dependency_factory():
    """测试使用注入的DependencyFactory初始化"""
    mock_dependency_factory = Mock(spec=DependencyFactory)
    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_video_manager = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    with patch("dingtalk_downloader.core.downloader.VideoDownloadManager", return_value=mock_video_manager):
        downloader = Downloader(
            BROWSER_TYPE_EDGE,
            SAVE_MODE_DEFAULT,
            user_controller=Mock(),
            dependency_factory=mock_dependency_factory,
        )

        assert downloader.browser_type == BROWSER_TYPE_EDGE
        assert downloader.save_mode == SAVE_MODE_DEFAULT
        assert downloader.dependency_factory == mock_dependency_factory
        assert downloader.video_manager == mock_video_manager
        mock_dependency_factory.get_cookie_handler.assert_called_once_with(BROWSER_TYPE_EDGE)
        mock_dependency_factory.get_path_selector.assert_called_once_with(SAVE_MODE_DEFAULT)
        mock_dependency_factory.get_n_m3u8dl_re.assert_called_once()


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_download_single_video_download_error(mock_video_manager_class, mock_dependency_factory_class):
    """测试单个视频下载（下载错误）"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    mock_context = Mock(spec=VideoDownloadContext)
    mock_context.live_name = "测试直播"
    mock_video_manager.initialize_download.return_value = mock_context
    mock_video_manager.process_video.side_effect = DownloadError("下载失败")

    mock_user_controller.get_user_input.return_value = "q"

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)
    downloader.download_single_video("https://n.dingtalk.com/test?liveUuid=abc")


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_download_single_video_browser_error(mock_video_manager_class, mock_dependency_factory_class):
    """测试单个视频下载（浏览器错误）"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    mock_context = Mock(spec=VideoDownloadContext)
    mock_context.live_name = "测试直播"
    mock_video_manager.initialize_download.return_value = mock_context
    mock_video_manager.process_video.side_effect = BrowserError("浏览器错误")

    mock_user_controller.get_user_input.return_value = "q"

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)
    downloader.download_single_video("https://n.dingtalk.com/test?liveUuid=abc")


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_download_single_video_network_error(mock_video_manager_class, mock_dependency_factory_class):
    """测试单个视频下载（网络错误）"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    mock_context = Mock(spec=VideoDownloadContext)
    mock_context.live_name = "测试直播"
    mock_video_manager.initialize_download.return_value = mock_context
    mock_video_manager.process_video.side_effect = NetworkError("网络错误")

    mock_user_controller.get_user_input.return_value = "q"

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)
    downloader.download_single_video("https://n.dingtalk.com/test?liveUuid=abc")


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_download_single_video_validation_error(mock_video_manager_class, mock_dependency_factory_class):
    """测试单个视频下载（验证错误）"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    mock_context = Mock(spec=VideoDownloadContext)
    mock_context.live_name = "测试直播"
    mock_video_manager.initialize_download.return_value = mock_context
    mock_video_manager.process_video.side_effect = ValidationError("验证错误")

    mock_user_controller.get_user_input.return_value = "q"

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)
    downloader.download_single_video("https://n.dingtalk.com/test?liveUuid=abc")


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_download_single_video_keyboard_interrupt(mock_video_manager_class, mock_dependency_factory_class):
    """测试单个视频下载（键盘中断）"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    mock_context = Mock(spec=VideoDownloadContext)
    mock_context.live_name = "测试直播"
    mock_video_manager.initialize_download.return_value = mock_context
    mock_video_manager.process_video.side_effect = KeyboardInterrupt()

    mock_user_controller = Mock()

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)
    with pytest.raises(KeyboardInterrupt):
        downloader.download_single_video("https://n.dingtalk.com/test?liveUuid=abc")


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_download_single_video_cookie_error(mock_video_manager_class, mock_dependency_factory_class):
    """测试单个视频下载（Cookie错误）"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    mock_video_manager.initialize_download.side_effect = CookieError("Cookie错误")

    mock_user_controller = Mock()

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)
    with pytest.raises(DownloadError):
        downloader.download_single_video("https://n.dingtalk.com/test?liveUuid=abc")


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_download_single_video_m3u8_parse_error(mock_video_manager_class, mock_dependency_factory_class):
    """测试单个视频下载（M3U8解析错误）"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    mock_video_manager.initialize_download.side_effect = M3u8ParseError("M3U8解析错误")

    mock_user_controller = Mock()

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)
    with pytest.raises(DownloadError):
        downloader.download_single_video("https://n.dingtalk.com/test?liveUuid=abc")


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_download_single_video_unknown_error(mock_video_manager_class, mock_dependency_factory_class):
    """测试单个视频下载（未知错误）"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    mock_video_manager.initialize_download.side_effect = Exception("未知错误")

    mock_user_controller = Mock()

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)
    with pytest.raises(DownloadError):
        downloader.download_single_video("https://n.dingtalk.com/test?liveUuid=abc")


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_download_batch_videos_first_error(mock_video_manager_class, mock_dependency_factory_class):
    """测试批量下载（第一个视频错误）"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    mock_context = Mock(spec=VideoDownloadContext)
    mock_context.live_name = "测试直播"
    mock_video_manager.initialize_download.return_value = mock_context
    mock_video_manager.process_video.side_effect = DownloadError("下载失败")

    mock_user_controller.ask_continue_download.return_value = False

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)
    downloader.download_batch_videos({0: "https://n.dingtalk.com/test?liveUuid=abc"})


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_download_batch_videos_remaining_error(mock_video_manager_class, mock_dependency_factory_class):
    """测试批量下载（剩余视频错误）"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    mock_context1 = Mock(spec=VideoDownloadContext)
    mock_context1.live_name = "测试直播1"
    mock_context2 = Mock(spec=VideoDownloadContext)
    mock_context2.live_name = "测试直播2"

    mock_video_manager.initialize_download.side_effect = [mock_context1, mock_context2]
    mock_video_manager.process_video.side_effect = [None, DownloadError("下载失败")]

    mock_user_controller.ask_continue_download.return_value = False

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)
    downloader.download_batch_videos({
        0: "https://n.dingtalk.com/test1?liveUuid=abc",
        1: "https://n.dingtalk.com/test2?liveUuid=def"
    })


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_download_batch_videos_keyboard_interrupt(mock_video_manager_class, mock_dependency_factory_class):
    """测试批量下载（键盘中断）"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    mock_context = Mock(spec=VideoDownloadContext)
    mock_context.live_name = "测试直播"
    mock_video_manager.initialize_download.return_value = mock_context
    mock_video_manager.process_video.side_effect = KeyboardInterrupt()

    mock_user_controller = Mock()

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)
    with pytest.raises(KeyboardInterrupt):
        downloader.download_batch_videos({0: "https://n.dingtalk.com/test?liveUuid=abc"})


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_download_batch_videos_unknown_error(mock_video_manager_class, mock_dependency_factory_class):
    """测试批量下载（未知错误）"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    mock_context = Mock(spec=VideoDownloadContext)
    mock_context.live_name = "测试直播"
    mock_video_manager.initialize_download.return_value = mock_context
    mock_video_manager.process_video.side_effect = Exception("未知错误")

    mock_user_controller = Mock()

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)
    with pytest.raises(DownloadError):
        downloader.download_batch_videos({0: "https://n.dingtalk.com/test?liveUuid=abc"})


@patch("dingtalk_downloader.core.downloader.DependencyFactory")
@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_continue_download_exit(mock_video_manager_class, mock_dependency_factory_class):
    """测试继续下载（退出）"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_dependency_factory = Mock()
    mock_dependency_factory_class.return_value = mock_dependency_factory

    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()
    mock_user_controller = Mock()

    mock_dependency_factory.get_cookie_handler.return_value = mock_cookie_handler
    mock_dependency_factory.get_path_selector.return_value = mock_path_selector
    mock_dependency_factory.get_n_m3u8dl_re.return_value = mock_n_m3u8dl_re

    mock_context1 = Mock(spec=VideoDownloadContext)
    mock_context1.live_name = "测试直播1"
    mock_context2 = Mock(spec=VideoDownloadContext)
    mock_context2.live_name = "测试直播2"

    mock_video_manager.initialize_download.side_effect = [mock_context1, mock_context2]
    mock_video_manager.process_video.return_value = True

    mock_user_controller.ask_continue_download.return_value = False

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)
    downloader.download_batch_videos({
        0: "https://n.dingtalk.com/test1?liveUuid=abc",
        1: "https://n.dingtalk.com/test2?liveUuid=def"
    })

    mock_user_controller.ask_continue_download.assert_called_once()


def test_close_no_video_manager():
    """测试关闭（无视频管理器）"""
    mock_user_controller = Mock()
    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)
    downloader.video_manager = None
    downloader.close()
    assert downloader.video_manager is None
