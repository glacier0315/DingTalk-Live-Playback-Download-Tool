"""
钉钉直播回放下载工具 - m3u8_download_service 单元测试

本模块测试m3u8下载服务类。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2026-01-27
修改历史：
    - 2026-01-27: 初始版本
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.core.m3u8_download_service import M3u8DownloadService
from dingtalk_downloader.utils.models import M3u8Link


def test_m3u8_download_service_init():
    """测试初始化"""
    mock_m3u8_parser = Mock()
    mock_m3u8_file_manager = Mock()

    with patch(
        "dingtalk_downloader.core.m3u8_download_service.M3u8FileManager"
    ) as mock_m3u8_file_manager_class:
        mock_m3u8_file_manager_class.return_value = mock_m3u8_file_manager

        service = M3u8DownloadService(mock_m3u8_parser)

        assert service.m3u8_parser == mock_m3u8_parser
        assert service.m3u8_file_manager == mock_m3u8_file_manager
        mock_m3u8_file_manager_class.assert_called_once()


@patch("os.path.exists")
@patch("os.path.getsize")
def test_fetch_and_download_m3u8_success(mock_getsize, mock_exists):
    """测试成功获取并下载m3u8文件"""
    mock_m3u8_parser = Mock()
    mock_m3u8_parser.fetch_m3u8_link.return_value = "https://test.com/video.m3u8"
    mock_m3u8_parser.download_m3u8_file.return_value = "/path/to/video.m3u8"
    mock_m3u8_parser.extract_prefix.return_value = "https://test.com/"
    mock_m3u8_file_manager = Mock()
    mock_m3u8_file_manager.get_temp_file_path.return_value = "/path/to/video.m3u8"

    mock_exists.return_value = True
    mock_getsize.return_value = 1024

    with patch(
        "dingtalk_downloader.core.m3u8_download_service.M3u8FileManager"
    ) as mock_m3u8_file_manager_class:
        mock_m3u8_file_manager_class.return_value = mock_m3u8_file_manager
        service = M3u8DownloadService(mock_m3u8_parser)

        m3u8_link = service.fetch_and_download_m3u8(
            "https://n.dingtalk.com/test"
        )

        assert m3u8_link.url == "https://test.com/video.m3u8"
        assert m3u8_link.prefix == "https://test.com/"
        assert m3u8_link.local_file_path == "/path/to/video.m3u8"
        mock_m3u8_parser.fetch_m3u8_link.assert_called_once_with("https://n.dingtalk.com/test")
        mock_m3u8_file_manager.get_temp_file_path.assert_called_once()
        mock_m3u8_parser.download_m3u8_file.assert_called_once()
        mock_m3u8_parser.extract_prefix.assert_called_once_with("https://test.com/video.m3u8")


def test_fetch_and_download_m3u8_fetch_error():
    """测试获取m3u8链接错误"""
    mock_m3u8_parser = Mock()
    mock_m3u8_parser.fetch_m3u8_link.side_effect = Exception("获取m3u8链接失败")

    mock_m3u8_file_manager = Mock()
    mock_m3u8_file_manager.get_temp_file_path.return_value = "/path/to/video.m3u8"

    with patch(
        "dingtalk_downloader.core.m3u8_download_service.M3u8FileManager"
    ) as mock_m3u8_file_manager_class:
        mock_m3u8_file_manager_class.return_value = mock_m3u8_file_manager

        service = M3u8DownloadService(mock_m3u8_parser)

        with pytest.raises(Exception, match="获取m3u8链接失败"):
            service.fetch_and_download_m3u8(
                "https://n.dingtalk.com/test"
            )

        mock_m3u8_parser.fetch_m3u8_link.assert_called_once_with("https://n.dingtalk.com/test")


def test_fetch_and_download_m3u8_download_error():
    """测试下载m3u8文件错误"""
    from dingtalk_downloader.core.exceptions import DownloadError

    mock_m3u8_parser = Mock()
    mock_m3u8_parser.fetch_m3u8_link.return_value = "https://test.com/video.m3u8"
    mock_m3u8_parser.download_m3u8_file.side_effect = Exception("下载m3u8文件失败")

    mock_m3u8_file_manager = Mock()
    mock_m3u8_file_manager.get_temp_file_path.return_value = "/path/to/video.m3u8"

    with patch(
        "dingtalk_downloader.core.m3u8_download_service.M3u8FileManager"
    ) as mock_m3u8_file_manager_class:
        mock_m3u8_file_manager_class.return_value = mock_m3u8_file_manager

        service = M3u8DownloadService(mock_m3u8_parser)

        with pytest.raises(DownloadError, match="下载 m3u8 文件失败"):
            service.fetch_and_download_m3u8(
                "https://n.dingtalk.com/test"
            )

        mock_m3u8_parser.fetch_m3u8_link.assert_called_once_with("https://n.dingtalk.com/test")
        mock_m3u8_file_manager.get_temp_file_path.assert_called_once()
        mock_m3u8_parser.download_m3u8_file.assert_called_once()


def test_fetch_and_download_m3u8_file_not_exist():
    """测试m3u8文件不存在"""
    from dingtalk_downloader.core.exceptions import DownloadError

    mock_m3u8_parser = Mock()
    mock_m3u8_parser.fetch_m3u8_link.return_value = "https://test.com/video.m3u8"
    mock_m3u8_parser.download_m3u8_file.return_value = None

    mock_m3u8_file_manager = Mock()
    mock_m3u8_file_manager.get_temp_file_path.return_value = "/path/to/video.m3u8"

    with patch(
        "dingtalk_downloader.core.m3u8_download_service.M3u8FileManager"
    ) as mock_m3u8_file_manager_class:
        mock_m3u8_file_manager_class.return_value = mock_m3u8_file_manager

        service = M3u8DownloadService(mock_m3u8_parser)

        with pytest.raises(DownloadError, match="m3u8 文件下载失败或文件不存在"):
            service.fetch_and_download_m3u8(
                "https://n.dingtalk.com/test"
            )

    mock_m3u8_parser.fetch_m3u8_link.assert_called_once_with("https://n.dingtalk.com/test")
    mock_m3u8_file_manager.get_temp_file_path.assert_called_once()
    mock_m3u8_parser.download_m3u8_file.assert_called_once()
