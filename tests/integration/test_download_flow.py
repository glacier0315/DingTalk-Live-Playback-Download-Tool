"""
钉钉直播回放下载工具 - 集成测试

本模块测试完整下载流程。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2026-01-27: 重写-适配新的架构
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.core.downloader import Downloader
from dingtalk_downloader.config.constants import BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT
from dingtalk_downloader.utils.models import VideoDownloadContext


@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_single_download_flow_success(mock_video_manager_class):
    """测试单个视频下载流程成功"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_context = Mock(spec=VideoDownloadContext)
    mock_context.live_name = "测试直播"
    mock_video_manager.initialize_download.return_value = mock_context
    mock_video_manager.process_video.return_value = True

    mock_user_controller = Mock()
    mock_user_controller.get_user_input.return_value = "q"

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)

    downloader.download_single_video("https://n.dingtalk.com/test?liveUuid=abc")

    mock_video_manager.initialize_download.assert_called_once()
    mock_video_manager.process_video.assert_called_once()


@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_single_download_flow_failure(mock_video_manager_class):
    """测试单个视频下载流程失败"""
    from dingtalk_downloader.core.exceptions import DownloadError

    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_context = Mock(spec=VideoDownloadContext)
    mock_context.live_name = "测试直播"
    mock_video_manager.initialize_download.return_value = mock_context
    mock_video_manager.process_video.side_effect = DownloadError("下载失败")

    mock_user_controller = Mock()
    mock_user_controller.get_user_input.return_value = "q"

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)

    downloader.download_single_video("https://n.dingtalk.com/test?liveUuid=abc")

    mock_video_manager.initialize_download.assert_called_once()
    mock_video_manager.process_video.assert_called_once()


@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
@patch("dingtalk_downloader.core.downloader.validate_dingtalk_url")
def test_single_download_flow_continue(mock_validate_url, mock_video_manager_class):
    """测试单个视频下载流程继续"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_context1 = Mock(spec=VideoDownloadContext)
    mock_context1.live_name = "测试直播1"
    mock_context2 = Mock(spec=VideoDownloadContext)
    mock_context2.live_name = "测试直播2"
    mock_video_manager.initialize_download.side_effect = [mock_context1, mock_context2]
    mock_video_manager.process_video.return_value = True
    mock_validate_url.return_value = "https://n.dingtalk.com/test2?liveUuid=abc"
    mock_user_controller = Mock()
    mock_user_controller.get_user_input.side_effect = [
        "https://n.dingtalk.com/test2?liveUuid=abc",
        "q"
    ]

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)
    downloader.download_single_video("https://n.dingtalk.com/test1?liveUuid=abc")

    assert mock_video_manager.initialize_download.call_count == 2
    assert mock_video_manager.process_video.call_count == 2


@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_batch_download_flow_success(mock_video_manager_class):
    """测试批量下载流程成功"""
    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_context1 = Mock(spec=VideoDownloadContext)
    mock_context1.live_name = "测试直播1"
    mock_context2 = Mock(spec=VideoDownloadContext)
    mock_context2.live_name = "测试直播2"
    mock_video_manager.initialize_download.side_effect = [mock_context1, mock_context2]
    mock_video_manager.process_video.return_value = True

    mock_user_controller = Mock()
    mock_user_controller.ask_continue_download.return_value = False

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)

    urls = {
        0: "https://n.dingtalk.com/test1?liveUuid=abc",
        1: "https://n.dingtalk.com/test2?liveUuid=abc",
    }

    downloader.download_batch_videos(urls)

    assert mock_video_manager.initialize_download.call_count == 2
    assert mock_video_manager.process_video.call_count == 2


@patch("dingtalk_downloader.core.downloader.VideoDownloadManager")
def test_batch_download_flow_failure(mock_video_manager_class):
    """测试批量下载流程失败"""
    from dingtalk_downloader.core.exceptions import DownloadError

    mock_video_manager = Mock()
    mock_video_manager_class.return_value = mock_video_manager

    mock_context = Mock(spec=VideoDownloadContext)
    mock_context.live_name = "测试直播"
    mock_video_manager.initialize_download.side_effect = [mock_context, mock_context]
    mock_video_manager.process_video.side_effect = DownloadError("下载失败")

    mock_user_controller = Mock()
    mock_user_controller.ask_continue_download.return_value = False

    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, mock_user_controller)

    urls = {
        0: "https://n.dingtalk.com/test1?liveUuid=abc",
        1: "https://n.dingtalk.com/test2?liveUuid=abc",
    }

    downloader.download_batch_videos(urls)

    assert mock_video_manager.initialize_download.call_count == 2
    assert mock_video_manager.process_video.call_count == 2
