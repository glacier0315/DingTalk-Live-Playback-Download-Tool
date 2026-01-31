"""
钉钉直播回放下载工具 - m3u8_parser 单元测试

本模块测试 m3u8 解析类。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2026-01-27: 更新-适配新的API，fetch_m3u8_link返回单个字符串
"""

import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.core.m3u8_parser import M3u8Parser
from dingtalk_downloader.core.exceptions import M3u8ParseError


@pytest.fixture
def mock_browser():
    """创建模拟的浏览器"""
    browser = Mock()
    browser.driver = Mock()
    browser.driver.execute_script.return_value = "#EXTM3U\n"
    return browser


@pytest.fixture
def mock_browser_with_logs():
    """创建带有日志的模拟浏览器"""
    browser = Mock()
    browser.driver = Mock()
    browser.driver.execute_script.return_value = "#EXTM3U\n"
    browser.get_log.return_value = [
        {"message": '{"url":"https://test.com/live_hp/123/test.m3u8?liveUuid=abc"}'}
    ]
    return browser


def test_m3u8_parser_init(mock_browser):
    """测试初始化"""
    parser = M3u8Parser(mock_browser)

    assert parser.browser == mock_browser
    assert parser.max_retries == 5


def test_m3u8_parser_init_custom_max_retries(mock_browser):
    """测试自定义最大重试次数"""
    parser = M3u8Parser(mock_browser, max_retries=10)

    assert parser.browser == mock_browser
    assert parser.max_retries == 10


def test_m3u8_parser_fetch_m3u8_link_success(mock_browser_with_logs):
    """测试成功获取m3u8链接"""
    mock_browser_with_logs.get_log.return_value = [
        {"message": '{"url":"https://test.com/live_hp/123/test.m3u8?liveUuid=abc"}'}
    ]
    mock_browser_with_logs.extract_m3u8_links_from_logs.return_value = [
        "https://test.com/live_hp/123/test.m3u8?liveUuid=abc"
    ]

    parser = M3u8Parser(mock_browser_with_logs)
    link = parser.fetch_m3u8_link("https://n.dingtalk.com/test?liveUuid=abc")

    assert link == "https://test.com/live_hp/123/test.m3u8?liveUuid=abc"


def test_m3u8_parser_fetch_m3u8_link_no_live_uuid(mock_browser):
    """测试没有liveUuid的情况"""
    from dingtalk_downloader.core.exceptions import M3u8ParseError

    parser = M3u8Parser(mock_browser)

    with pytest.raises(M3u8ParseError) as exc_info:
        parser.fetch_m3u8_link("https://n.dingtalk.com/test")

    assert "未能从 URL 提取 liveUuid 参数" in str(exc_info.value)


def test_m3u8_parser_fetch_m3u8_link_retry_success(mock_browser):
    """测试重试机制成功"""
    mock_browser.get_log.side_effect = [
        [{"message": '{"url":"https://test.com/other/file.txt"}'}],
        [{"message": '{"url":"https://test.com/other/file.txt"}'}],
        [{"message": '{"url":"https://test.com/live_hp/123/test.m3u8?liveUuid=abc"}'}],
    ]
    mock_browser.extract_m3u8_links_from_logs.side_effect = [
        [],
        [],
        ["https://test.com/live_hp/123/test.m3u8?liveUuid=abc"],
    ]

    parser = M3u8Parser(mock_browser, max_retries=3)
    link = parser.fetch_m3u8_link("https://n.dingtalk.com/test?liveUuid=abc")

    assert link == "https://test.com/live_hp/123/test.m3u8?liveUuid=abc"
    assert mock_browser.get_log.call_count == 3


def test_m3u8_parser_fetch_m3u8_link_retry_failure(mock_browser):
    """测试重试机制失败"""
    mock_browser.get_log.return_value = [{"message": '{"url":"https://test.com/other/file.txt"}'}]
    mock_browser.extract_m3u8_links_from_logs.return_value = []

    parser = M3u8Parser(mock_browser, max_retries=2)

    with pytest.raises(M3u8ParseError):
        parser.fetch_m3u8_link("https://n.dingtalk.com/test?liveUuid=abc")

    assert mock_browser.get_log.call_count == 2


def test_m3u8_parser_download_m3u8_file_success(mock_browser, tmp_path):
    """测试成功下载m3u8文件"""
    parser = M3u8Parser(mock_browser)

    temp_file = tmp_path / "test.m3u8"
    mock_browser.driver.execute_script.return_value = "#EXTM3U\n#EXT-X-VERSION:3\n"
    result = parser.download_m3u8_file("https://test.com/test.m3u8", str(temp_file))
    assert result == str(temp_file)
    assert temp_file.exists()
    mock_browser.driver.execute_script.assert_called_once()

def test_m3u8_parser_download_m3u8_file_failure(mock_browser, tmp_path):
    """测试下载m3u8文件失败"""
    parser = M3u8Parser(mock_browser)

    temp_file = tmp_path / "test.m3u8"
    mock_browser.driver.execute_script.side_effect = Exception("下载失败")

    with pytest.raises(M3u8ParseError):
        parser.download_m3u8_file("https://test.com/test.m3u8", str(temp_file))


def test_m3u8_parser_extract_prefix_success():
    """测试成功提取基础URL"""
    parser = M3u8Parser(Mock())
    url = "https://test.com/live_hp/123/test.m3u8?uuid=abc"
    prefix = parser.extract_prefix(url)

    assert prefix == "https://test.com/live_hp/123"


def test_m3u8_parser_extract_prefix_no_match():
    """测试提取基础URL无匹配"""
    parser = M3u8Parser(Mock())
    url = "https://test.com/other/path/test.m3u8"
    prefix = parser.extract_prefix(url)

    assert prefix == url


def test_m3u8_parser_refresh_page(mock_browser):
    """测试刷新页面"""
    parser = M3u8Parser(mock_browser)

    parser._refresh_page()

    mock_browser.driver.execute_script.assert_called_once_with("location.reload();")
