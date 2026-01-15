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
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.core.downloader import Downloader
from dingtalk_downloader.config.constants import BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, SAVE_MODE_MANUAL


@patch("dingtalk_downloader.core.downloader.CookieHandler")
@patch("dingtalk_downloader.core.downloader.M3u8Parser")
@patch("dingtalk_downloader.core.downloader.NM3u8DLRE")
def test_downloader_init(mock_n_m3u8dl_re, mock_m3u8_parser, mock_cookie_handler):
    """测试初始化下载器"""
    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)

    assert downloader.browser_type == BROWSER_TYPE_EDGE
    assert downloader.save_mode == SAVE_MODE_DEFAULT
    assert downloader.cookie_handler is not None
    assert downloader.n_m3u8dl_re is not None


@patch("dingtalk_downloader.core.downloader.CookieHandler")
@patch("dingtalk_downloader.core.downloader.M3u8Parser")
@patch("dingtalk_downloader.core.downloader.NM3u8DLRE")
def test_downloader_close(mock_n_m3u8dl_re, mock_m3u8_parser, mock_cookie_handler):
    """测试关闭下载器"""
    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)
    downloader.close()

    mock_cookie_handler.return_value.close.assert_called_once()


@patch("dingtalk_downloader.core.downloader.CookieHandler")
@patch("dingtalk_downloader.core.downloader.M3u8Parser")
@patch("dingtalk_downloader.core.downloader.NM3u8DLRE")
def test_downloader_get_default_download_dir(mock_n_m3u8dl_re, mock_m3u8_parser, mock_cookie_handler):
    """测试获取默认下载目录"""
    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)
    save_dir = downloader._get_default_download_dir()

    assert "Downloads" in save_dir
    assert os.path.isabs(save_dir)


@patch("dingtalk_downloader.core.downloader.CookieHandler")
@patch("dingtalk_downloader.core.downloader.M3u8Parser")
@patch("dingtalk_downloader.core.downloader.NM3u8DLRE")
def test_downloader_get_manual_download_dir(mock_n_m3u8dl_re, mock_m3u8_parser, mock_cookie_handler):
    """测试获取手动选择的下载目录"""
    with patch("dingtalk_downloader.core.downloader.tk.Tk") as mock_tk, \
         patch("dingtalk_downloader.core.downloader.filedialog.askdirectory") as mock_askdirectory:
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_askdirectory.return_value = "/custom/path"
        
        downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_MANUAL)
        save_dir = downloader._get_manual_download_dir()

        assert save_dir == "/custom/path"
        mock_root.withdraw.assert_called_once()
        mock_root.destroy.assert_called_once()
        mock_askdirectory.assert_called_once_with(title="选择保存视频的目录")


@patch("dingtalk_downloader.core.downloader.CookieHandler")
@patch("dingtalk_downloader.core.downloader.M3u8Parser")
@patch("dingtalk_downloader.core.downloader.NM3u8DLRE")
def test_downloader_get_manual_download_dir_cancelled(mock_n_m3u8dl_re, mock_m3u8_parser, mock_cookie_handler):
    """测试用户取消选择下载目录"""
    with patch("dingtalk_downloader.core.downloader.tk.Tk") as mock_tk, \
         patch("dingtalk_downloader.core.downloader.filedialog.askdirectory") as mock_askdirectory:
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_askdirectory.return_value = ""
        
        downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_MANUAL)
        save_dir = downloader._get_manual_download_dir()

        assert save_dir == ""
        mock_root.withdraw.assert_called_once()
        mock_root.destroy.assert_called_once()
        mock_askdirectory.assert_called_once_with(title="选择保存视频的目录")


@patch("dingtalk_downloader.core.downloader.CookieHandler")
@patch("dingtalk_downloader.core.downloader.M3u8Parser")
@patch("dingtalk_downloader.core.downloader.NM3u8DLRE")
def test_downloader_download_video_default_mode(mock_n_m3u8dl_re, mock_m3u8_parser, mock_cookie_handler):
    """测试默认模式下载视频"""
    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)
    
    mock_cookies = {"session": "test"}
    mock_headers = {"User-Agent": "test"}
    mock_n_m3u8dl_re.return_value.download.return_value = True
    
    result = downloader._download_video("test.m3u8", "test_video", "https://test.com", mock_cookies, mock_headers)

    mock_n_m3u8dl_re.return_value.download.assert_called_once()
    assert result is True


@patch("dingtalk_downloader.core.downloader.CookieHandler")
@patch("dingtalk_downloader.core.downloader.M3u8Parser")
@patch("dingtalk_downloader.core.downloader.NM3u8DLRE")
def test_downloader_download_video_invalid_mode(mock_n_m3u8dl_re, mock_m3u8_parser, mock_cookie_handler):
    """测试无效的保存模式"""
    downloader = Downloader(BROWSER_TYPE_EDGE, "invalid_mode")
    
    mock_cookies = {"session": "test"}
    mock_headers = {"User-Agent": "test"}
    
    result = downloader._download_video("test.m3u8", "test_video", "https://test.com", mock_cookies, mock_headers)

    mock_n_m3u8dl_re.return_value.download.assert_not_called()
    assert result is False


@patch("dingtalk_downloader.core.downloader.CookieHandler")
@patch("dingtalk_downloader.core.downloader.M3u8Parser")
@patch("dingtalk_downloader.core.downloader.NM3u8DLRE")
def test_downloader_download_video_success(mock_n_m3u8dl_re, mock_m3u8_parser, mock_cookie_handler):
    """测试下载成功"""
    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)
    
    mock_cookies = {"session": "test"}
    mock_headers = {"User-Agent": "test"}
    mock_n_m3u8dl_re.return_value.download.return_value = True
    
    result = downloader._download_video("test.m3u8", "test_video", "https://test.com", mock_cookies, mock_headers)

    assert result is True
    assert downloader.saved_path is not None
    assert "Downloads" in downloader.saved_path


@patch("dingtalk_downloader.core.downloader.CookieHandler")
@patch("dingtalk_downloader.core.downloader.M3u8Parser")
@patch("dingtalk_downloader.core.downloader.NM3u8DLRE")
def test_downloader_download_video_failure(mock_n_m3u8dl_re, mock_m3u8_parser, mock_cookie_handler):
    """测试下载失败"""
    downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)
    
    mock_cookies = {"session": "test"}
    mock_headers = {"User-Agent": "test"}
    mock_n_m3u8dl_re.return_value.download.return_value = False
    
    result = downloader._download_video("test.m3u8", "test_video", "https://test.com", mock_cookies, mock_headers)

    assert result is False
    assert downloader.saved_path is None


@patch("dingtalk_downloader.core.downloader.CookieHandler")
@patch("dingtalk_downloader.core.downloader.M3u8Parser")
@patch("dingtalk_downloader.core.downloader.NM3u8DLRE")
def test_downloader_download_video_cancelled(mock_n_m3u8dl_re, mock_m3u8_parser, mock_cookie_handler):
    """测试用户取消目录选择"""
    with patch("dingtalk_downloader.core.downloader.tk.Tk") as mock_tk, \
         patch("dingtalk_downloader.core.downloader.filedialog.askdirectory") as mock_askdirectory:
        mock_root = MagicMock()
        mock_tk.return_value = mock_root
        mock_askdirectory.return_value = ""
        
        downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_MANUAL)
        
        mock_cookies = {"session": "test"}
        mock_headers = {"User-Agent": "test"}
        
        result = downloader._download_video("test.m3u8", "test_video", "https://test.com", mock_cookies, mock_headers)

        assert result is False
        assert downloader.saved_path is None
        mock_n_m3u8dl_re.return_value.download.assert_not_called()
