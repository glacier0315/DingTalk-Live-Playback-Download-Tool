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
from unittest.mock import Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from dingtalk_downloader.core.m3u8_parser import M3u8Parser
from dingtalk_downloader.config.constants import BROWSER_TYPE_EDGE


@pytest.fixture
def mock_browser():
    """创建模拟的浏览器"""
    browser = Mock()
    browser.get_log.return_value = [
        {'message': '{"url":"https://test.com/live_hp/123/test.m3u8?uuid=abc"}'}
    ]
    browser.driver.execute_script.return_value = '#EXTM3U\n'
    return browser


def test_m3u8_parser_fetch_m3u8_links(mock_browser):
    """测试提取 m3u8 链接"""
    parser = M3u8Parser(mock_browser, BROWSER_TYPE_EDGE)
    links = parser.fetch_m3u8_links('https://n.dingtalk.com/test?liveUuid=abc')

    assert len(links) == 1
    assert 'https://test.com/live_hp/123/test.m3u8?uuid=abc' in links


def test_m3u8_parser_extract_prefix():
    """测试提取基础 URL"""
    parser = M3u8Parser(Mock(), BROWSER_TYPE_EDGE)
    url = 'https://test.com/live_hp/123/test.m3u8?uuid=abc'
    prefix = parser.extract_prefix(url)

    assert prefix == 'https://test.com/live_hp/123'


def test_m3u8_parser_download_m3u8_file(mock_browser, tmp_path):
    """测试下载 m3u8 文件"""
    import tempfile
    parser = M3u8Parser(mock_browser, BROWSER_TYPE_EDGE)

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        temp_file = f.name

    result = parser.download_m3u8_file('https://test.com/test.m3u8', temp_file, {})

    assert result == temp_file
    mock_browser.driver.execute_script.assert_called_once()
