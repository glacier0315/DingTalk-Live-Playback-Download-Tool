"""
钉钉直播回放下载工具 - m3u8_parser 单元测试

本模块测试 m3u8 解析类。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
"""

import sys
import os
import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.core.m3u8_parser import M3u8Parser
from dingtalk_downloader.config.constants import BROWSER_TYPE_EDGE, BROWSER_TYPE_CHROME, BROWSER_TYPE_FIREFOX


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
        {"message": '{"url":"https://test.com/live_hp/123/test.m3u8?uuid=abc"}'}
    ]
    return browser


def test_m3u8_parser_fetch_m3u8_links_edge(mock_browser_with_logs):
    """测试提取 m3u8 链接 (Edge浏览器)"""
    mock_browser_with_logs.get_log.return_value = [
        {"message": '{"url":"https://test.com/live_hp/123/test.m3u8?liveUuid=abc"}'}
    ]
    
    parser = M3u8Parser(mock_browser_with_logs, BROWSER_TYPE_EDGE)
    links = parser.fetch_m3u8_links("https://n.dingtalk.com/test?liveUuid=abc")

    assert len(links) == 1
    assert "https://test.com/live_hp/123/test.m3u8?liveUuid=abc" in links


def test_m3u8_parser_fetch_m3u8_links_chrome(mock_browser_with_logs):
    """测试提取 m3u8 链接 (Chrome浏览器)"""
    mock_browser_with_logs.get_log.return_value = [
        {"message": '{"url":"https://test.com/live_hp/456/test.m3u8?liveUuid=def"}'}
    ]
    
    parser = M3u8Parser(mock_browser_with_logs, BROWSER_TYPE_CHROME)
    links = parser.fetch_m3u8_links("https://n.dingtalk.com/test?liveUuid=def")

    assert len(links) == 1
    assert "https://test.com/live_hp/456/test.m3u8?liveUuid=def" in links


def test_m3u8_parser_fetch_m3u8_links_firefox(mock_browser_with_logs):
    """测试提取 m3u8 链接 (Firefox浏览器)"""
    mock_browser_with_logs.get_log.return_value = [
        "https://test.com/live_hp/789/test.m3u8?liveUuid=ghi"
    ]
    
    parser = M3u8Parser(mock_browser_with_logs, BROWSER_TYPE_FIREFOX)
    links = parser.fetch_m3u8_links("https://n.dingtalk.com/test?liveUuid=ghi")

    assert len(links) == 1
    assert "https://test.com/live_hp/789/test.m3u8?liveUuid=ghi" in links


def test_m3u8_parser_fetch_m3u8_links_no_live_uuid(mock_browser):
    """测试没有 liveUuid 的情况"""
    parser = M3u8Parser(mock_browser, BROWSER_TYPE_EDGE)
    links = parser.fetch_m3u8_links("https://n.dingtalk.com/test")

    assert links is None


def test_m3u8_parser_fetch_m3u8_links_not_found(mock_browser):
    """测试未找到 m3u8 链接的情况"""
    mock_browser.get_log.return_value = [
        {"message": '{"url":"https://test.com/other/file.txt"}'}
    ]
    
    parser = M3u8Parser(mock_browser, BROWSER_TYPE_EDGE)
    links = parser.fetch_m3u8_links("https://n.dingtalk.com/test?liveUuid=abc")

    assert links is None


def test_m3u8_parser_fetch_m3u8_links_retry(mock_browser):
    """测试重试机制"""
    mock_browser.get_log.side_effect = [
        [{"message": '{"url":"https://test.com/other/file.txt"}'}],
        [{"message": '{"url":"https://test.com/other/file.txt"}'}],
        [{"message": '{"url":"https://test.com/live_hp/123/test.m3u8?liveUuid=abc"}'}]
    ]
    
    parser = M3u8Parser(mock_browser, BROWSER_TYPE_EDGE, max_retries=3)
    links = parser.fetch_m3u8_links("https://n.dingtalk.com/test?liveUuid=abc")

    assert len(links) == 1
    assert "https://test.com/live_hp/123/test.m3u8?liveUuid=abc" in links
    assert mock_browser.get_log.call_count == 3


def test_m3u8_parser_extract_prefix():
    """测试提取基础 URL"""
    parser = M3u8Parser(Mock(), BROWSER_TYPE_EDGE)
    url = "https://test.com/live_hp/123/test.m3u8?uuid=abc"
    prefix = parser.extract_prefix(url)

    assert prefix == "https://test.com/live_hp/123"


def test_m3u8_parser_extract_prefix_no_match():
    """测试提取基础 URL - 无匹配"""
    parser = M3u8Parser(Mock(), BROWSER_TYPE_EDGE)
    url = "https://test.com/other/path/test.m3u8"
    prefix = parser.extract_prefix(url)

    assert prefix == url


def test_m3u8_parser_download_m3u8_file(mock_browser, tmp_path):
    """测试下载 m3u8 文件"""
    parser = M3u8Parser(mock_browser, BROWSER_TYPE_EDGE)
    
    temp_file = tmp_path / "test.m3u8"
    mock_browser.driver.execute_script.return_value = "#EXTM3U\n#EXT-X-VERSION:3\n"

    result = parser.download_m3u8_file("https://test.com/test.m3u8", str(temp_file), {})

    assert result == str(temp_file)
    assert temp_file.exists()
    mock_browser.driver.execute_script.assert_called_once()


def test_m3u8_parser_download_m3u8_file_with_headers(mock_browser, tmp_path):
    """测试下载 m3u8 文件 - 带请求头"""
    parser = M3u8Parser(mock_browser, BROWSER_TYPE_EDGE)
    
    temp_file = tmp_path / "test.m3u8"
    mock_browser.driver.execute_script.return_value = "#EXTM3U\n"
    headers = {"User-Agent": "test", "Referer": "https://test.com"}

    result = parser.download_m3u8_file("https://test.com/test.m3u8", str(temp_file), headers)

    assert result == str(temp_file)
    assert temp_file.exists()
    mock_browser.driver.execute_script.assert_called_once()


def test_m3u8_parser_refresh_page(mock_browser):
    """测试刷新页面"""
    parser = M3u8Parser(mock_browser, BROWSER_TYPE_EDGE)
    
    parser._refresh_page()

    mock_browser.driver.execute_script.assert_called_once_with("location.reload();")


def test_m3u8_parser_fetch_m3u8_links_exception_handling(mock_browser):
    """测试异常处理"""
    mock_browser.get_log.side_effect = Exception("Network error")
    
    parser = M3u8Parser(mock_browser, BROWSER_TYPE_EDGE)
    links = parser.fetch_m3u8_links("https://n.dingtalk.com/test?liveUuid=abc")

    assert links is None


def test_m3u8_parser_fetch_m3u8_links_log_exception_handling(mock_browser):
    """测试日志处理异常处理"""
    mock_browser.get_log.return_value = [
        {"message": "invalid json"}
    ]
    
    parser = M3u8Parser(mock_browser, BROWSER_TYPE_EDGE)
    links = parser.fetch_m3u8_links("https://n.dingtalk.com/test?liveUuid=abc")

    assert links is None


def test_m3u8_parser_download_m3u8_file_exception_handling(mock_browser, tmp_path):
    """测试下载 m3u8 文件异常处理"""
    parser = M3u8Parser(mock_browser, BROWSER_TYPE_EDGE)
    
    temp_file = tmp_path / "test.m3u8"
    mock_browser.driver.execute_script.side_effect = Exception("Download error")

    with patch('sys.exit') as mock_exit:
        parser.download_m3u8_file("https://test.com/test.m3u8", str(temp_file), {})
        mock_exit.assert_called_once_with(1)
