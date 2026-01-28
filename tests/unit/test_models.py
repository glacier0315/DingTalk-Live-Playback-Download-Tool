"""
钉钉直播回放下载工具 - models 单元测试

本模块测试数据模型类。

作者：项目团队
依赖：pytest
创建日期：2026-01-26
修改历史：
    - 2026-01-26: 初始版本
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.utils.models import CookieData, HeadersData, M3u8Link, VideoDownloadContext


def test_cookie_data_creation():
    """测试创建Cookie数据"""
    cookie_data = CookieData({"session": "abc123", "user": "test"})
    assert len(cookie_data) == 2
    assert cookie_data.get("session") == "abc123"
    assert cookie_data.get("user") == "test"


def test_cookie_data_to_dict():
    """测试Cookie数据转换为字典"""
    cookie_data = CookieData({"session": "abc123"})
    cookie_dict = cookie_data.to_dict()
    assert cookie_dict == {"session": "abc123"}
    assert cookie_dict is not cookie_data.cookies


def test_cookie_data_validation():
    """测试Cookie数据验证"""
    with pytest.raises(ValueError):
        CookieData("invalid")

    with pytest.raises(ValueError):
        CookieData({"key": 123})


def test_headers_data_creation():
    """测试创建请求头数据"""
    headers_data = HeadersData({"User-Agent": "Mozilla/5.0", "Referer": "https://example.com"})
    assert len(headers_data) == 2
    assert headers_data.get("User-Agent") == "Mozilla/5.0"
    assert headers_data.get("Referer") == "https://example.com"


def test_headers_data_to_dict():
    """测试请求头数据转换为字典"""
    headers_data = HeadersData({"User-Agent": "Mozilla/5.0"})
    headers_dict = headers_data.to_dict()
    assert headers_dict == {"User-Agent": "Mozilla/5.0"}
    assert headers_dict is not headers_data.headers


def test_m3u8_link_creation():
    """测试创建m3u8链接"""
    m3u8_link = M3u8Link("https://example.com/live/video.m3u8", "https://example.com/live/")
    assert m3u8_link.url == "https://example.com/live/video.m3u8"
    assert m3u8_link.prefix == "https://example.com/live/"
    assert m3u8_link.local_file_path is None


def test_m3u8_link_creation_with_local_path():
    """测试创建m3u8链接（包含本地路径）"""
    m3u8_link = M3u8Link(
        "https://example.com/live/video.m3u8",
        "https://example.com/live/",
        "/path/to/local/video.m3u8",
    )
    assert m3u8_link.url == "https://example.com/live/video.m3u8"
    assert m3u8_link.prefix == "https://example.com/live/"
    assert m3u8_link.local_file_path == "/path/to/local/video.m3u8"


def test_m3u8_link_validation():
    """测试m3u8链接验证"""
    with pytest.raises(ValueError):
        M3u8Link("", "https://example.com/live/")

    with pytest.raises(ValueError):
        M3u8Link("https://example.com/live/video.m3u8", "")

    with pytest.raises(ValueError):
        M3u8Link("invalid-url", "https://example.com/live/")


def test_m3u8_link_local_file_path_validation():
    """测试m3u8链接本地文件路径验证"""
    with pytest.raises(ValueError):
        M3u8Link("https://example.com/live/video.m3u8", "https://example.com/live/", 123)

    with pytest.raises(ValueError):
        M3u8Link("invalid-url", "https://example.com/live/")


def test_video_download_context_creation():
    """测试创建视频下载上下文"""
    cookie_data = CookieData({"session": "abc"})
    headers_data = HeadersData({"User-Agent": "Mozilla"})
    context = VideoDownloadContext(
        url="https://n.dingtalk.com/test",
        cookie_data=cookie_data,
        headers_data=headers_data,
        live_name="测试直播",
        save_dir="Downloads",
        save_mode="1",
    )
    assert context.url == "https://n.dingtalk.com/test"
    assert context.live_name == "测试直播"
    assert context.save_dir == "Downloads"
    assert context.save_mode == "1"


def test_video_download_context_get_cookies_dict():
    """测试获取Cookie字典"""
    cookie_data = CookieData({"session": "abc"})
    headers_data = HeadersData({"User-Agent": "Mozilla"})
    context = VideoDownloadContext(
        url="https://n.dingtalk.com/test",
        cookie_data=cookie_data,
        headers_data=headers_data,
        live_name="测试直播",
    )
    cookies_dict = context.get_cookies_dict()
    assert cookies_dict == {"session": "abc"}


def test_video_download_context_get_headers_dict():
    """测试获取请求头字典"""
    cookie_data = CookieData({"session": "abc"})
    headers_data = HeadersData({"User-Agent": "Mozilla"})
    context = VideoDownloadContext(
        url="https://n.dingtalk.com/test",
        cookie_data=cookie_data,
        headers_data=headers_data,
        live_name="测试直播",
    )
    headers_dict = context.get_headers_dict()
    assert headers_dict == {"User-Agent": "Mozilla"}


def test_video_download_context_is_save_dir_set():
    """测试检查保存目录是否已设置"""
    cookie_data = CookieData({"session": "abc"})
    headers_data = HeadersData({"User-Agent": "Mozilla"})
    context = VideoDownloadContext(
        url="https://n.dingtalk.com/test",
        cookie_data=cookie_data,
        headers_data=headers_data,
        live_name="测试直播",
        save_dir="Downloads",
    )
    assert context.is_save_dir_set() is True

    context_no_dir = VideoDownloadContext(
        url="https://n.dingtalk.com/test",
        cookie_data=cookie_data,
        headers_data=headers_data,
        live_name="测试直播",
    )
    assert context_no_dir.is_save_dir_set() is False
