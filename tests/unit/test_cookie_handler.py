"""
钉钉直播回放下载工具 - cookie_handler 单元测试

本模块测试 Cookie 处理类。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from dingtalk_downloader.core.cookie_handler import CookieHandler
from dingtalk_downloader.config.constants import BROWSER_TYPE_EDGE


@pytest.fixture
def mock_browser():
    """创建模拟的浏览器"""
    browser = Mock()
    browser.get_cookies.return_value = [{'name': 'test', 'value': 'value'}]
    browser.get_user_agent.return_value = 'Mozilla/5.0'
    browser.get_referer.return_value = 'https://n.dingtalk.com/'
    browser.get_element_by_xpath.return_value.text = '测试直播'
    return browser


@patch('src.dingtalk_downloader.core.cookie_handler.BrowserFactory')
def test_cookie_handler_get_cookie(mock_browser_factory, mock_browser):
    """测试获取 Cookie"""
    mock_browser_factory.create_browser.return_value = mock_browser
    handler = CookieHandler(BROWSER_TYPE_EDGE)

    with patch('builtins.input', return_value=''):
        browser, cookies, headers, live_name = handler.get_cookie('https://n.dingtalk.com/test')

    assert len(cookies) == 1
    assert cookies['test'] == 'value'
    assert 'User-Agent' in headers
    assert 'Referer' in headers
    assert live_name == '测试直播'


@patch('src.dingtalk_downloader.core.cookie_handler.BrowserFactory')
def test_cookie_handler_close(mock_browser_factory, mock_browser):
    """测试关闭浏览器"""
    mock_browser_factory.create_browser.return_value = mock_browser
    handler = CookieHandler(BROWSER_TYPE_EDGE)
    handler.get_cookie('https://n.dingtalk.com/test')

    handler.close()
    mock_browser.close.assert_called_once()
