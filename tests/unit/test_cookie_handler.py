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
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.core.cookie_handler import CookieHandler
from dingtalk_downloader.config.constants import BROWSER_TYPE_EDGE


@pytest.fixture
def mock_browser():
    """创建模拟的浏览器"""
    browser = Mock()
    browser.get_cookies.return_value = [{"name": "test", "value": "value"}]
    browser.get_user_agent.return_value = "Mozilla/5.0"
    browser.get_referer.return_value = "https://n.dingtalk.com/"
    browser.get_element_by_xpath.return_value.text = "测试直播"
    return browser


@patch("dingtalk_downloader.core.cookie_handler.BrowserFactory")
def test_cookie_handler_get_cookie(mock_browser_factory, mock_browser):
    """测试获取 Cookie"""
    mock_browser_factory.create_browser.return_value = mock_browser
    handler = CookieHandler(BROWSER_TYPE_EDGE)

    with patch("builtins.input", return_value=""):
        browser, cookies, headers, live_name = handler.get_cookie("https://n.dingtalk.com/test")

    assert len(cookies) == 1
    assert cookies["test"] == "value"
    assert "User-Agent" in headers
    assert "Referer" in headers
    assert live_name == "测试直播"


@patch("dingtalk_downloader.core.cookie_handler.BrowserFactory")
def test_cookie_handler_get_cookie_with_multiple_cookies(mock_browser_factory):
    """测试获取多个 Cookie"""
    mock_browser = Mock()
    mock_browser.get_cookies.return_value = [
        {"name": "cookie1", "value": "value1"},
        {"name": "cookie2", "value": "value2"}
    ]
    mock_browser.get_user_agent.return_value = "Mozilla/5.0"
    mock_browser.get_referer.return_value = "https://n.dingtalk.com/"
    mock_browser.get_element_by_xpath.return_value.text = "测试直播"
    
    mock_browser_factory.create_browser.return_value = mock_browser
    handler = CookieHandler(BROWSER_TYPE_EDGE)

    with patch("builtins.input", return_value=""):
        browser, cookies, headers, live_name = handler.get_cookie("https://n.dingtalk.com/test")

    assert len(cookies) == 2
    assert cookies["cookie1"] == "value1"
    assert cookies["cookie2"] == "value2"
    assert "User-Agent" in headers
    assert "Referer" in headers


@patch("dingtalk_downloader.core.cookie_handler.BrowserFactory")
def test_cookie_handler_close(mock_browser_factory, mock_browser):
    """测试关闭浏览器"""
    mock_browser_factory.create_browser.return_value = mock_browser
    handler = CookieHandler(BROWSER_TYPE_EDGE)
    
    with patch("builtins.input", return_value=""):
        handler.get_cookie("https://n.dingtalk.com/test")

    handler.close()
    mock_browser.close.assert_called_once()


@patch("dingtalk_downloader.core.cookie_handler.BrowserFactory")
def test_cookie_handler_repeat_get_cookie(mock_browser_factory, mock_browser):
    """测试重复获取 Cookie"""
    mock_browser_factory.create_browser.return_value = mock_browser
    handler = CookieHandler(BROWSER_TYPE_EDGE)
    
    with patch("builtins.input", return_value=""):
        handler.get_cookie("https://n.dingtalk.com/test")

    with patch("builtins.input", return_value=""):
        cookies, headers, live_name = handler.repeat_get_cookie("https://n.dingtalk.com/test2")

    assert len(cookies) == 1
    assert cookies["test"] == "value"
    assert "User-Agent" in headers
    assert "Referer" in headers


@patch("dingtalk_downloader.core.cookie_handler.BrowserFactory")
def test_cookie_handler_get_live_name_xpath(mock_browser_factory, mock_browser):
    """测试通过 XPath 获取直播名称"""
    mock_browser.get_cookies.return_value = [{"name": "test", "value": "value"}]
    mock_browser.get_user_agent.return_value = "Mozilla/5.0"
    mock_browser.get_referer.return_value = "https://n.dingtalk.com/"
    mock_browser.get_element_by_xpath.return_value.text = "XPath直播名称"
    
    mock_browser_factory.create_browser.return_value = mock_browser
    handler = CookieHandler(BROWSER_TYPE_EDGE)

    with patch("builtins.input", return_value=""):
        browser, cookies, headers, live_name = handler.get_cookie("https://n.dingtalk.com/test")

    assert live_name == "XPath直播名称"


@patch("dingtalk_downloader.core.cookie_handler.BrowserFactory")
def test_cookie_handler_get_live_name_css(mock_browser_factory, mock_browser):
    """测试通过 CSS 选择器获取直播名称"""
    mock_browser.get_cookies.return_value = [{"name": "test", "value": "value"}]
    mock_browser.get_user_agent.return_value = "Mozilla/5.0"
    mock_browser.get_referer.return_value = "https://n.dingtalk.com/"
    
    def get_element_by_xpath_side_effect(xpath):
        raise Exception("XPath failed")
    
    def get_element_by_class_name_side_effect(class_name):
        mock_element = Mock()
        mock_element.text = "CSS直播名称"
        return mock_element
    
    mock_browser.get_element_by_xpath.side_effect = get_element_by_xpath_side_effect
    mock_browser.get_element_by_class_name.side_effect = get_element_by_class_name_side_effect
    
    mock_browser_factory.create_browser.return_value = mock_browser
    handler = CookieHandler(BROWSER_TYPE_EDGE)

    with patch("builtins.input", return_value=""):
        browser, cookies, headers, live_name = handler.get_cookie("https://n.dingtalk.com/test")

    assert live_name == "CSS直播名称"


@patch("dingtalk_downloader.core.cookie_handler.BrowserFactory")
def test_cookie_handler_get_live_name_fallback(mock_browser_factory, mock_browser):
    """测试直播名称获取失败时的回退"""
    mock_browser.get_cookies.return_value = [{"name": "test", "value": "value"}]
    mock_browser.get_user_agent.return_value = "Mozilla/5.0"
    mock_browser.get_referer.return_value = "https://n.dingtalk.com/"
    
    def get_element_by_xpath_side_effect(xpath):
        raise Exception("XPath failed")
    
    def get_element_by_class_name_side_effect(class_name):
        raise Exception("CSS failed")
    
    mock_browser.get_element_by_xpath.side_effect = get_element_by_xpath_side_effect
    mock_browser.get_element_by_class_name.side_effect = get_element_by_class_name_side_effect
    
    mock_browser_factory.create_browser.return_value = mock_browser
    handler = CookieHandler(BROWSER_TYPE_EDGE)

    with patch("builtins.input", return_value=""):
        browser, cookies, headers, live_name = handler.get_cookie("https://n.dingtalk.com/test")

    assert live_name == "直播视频名称不可获取"
