"""
钉钉直播回放下载工具 - cookie_handler 单元测试

本模块测试 Cookie 处理类。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2026-01-27: 更新-适配新的架构，使用HeaderManager
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.core.cookie_handler import CookieHandler
from dingtalk_downloader.config.constants import BROWSER_TYPE_EDGE
from dingtalk_downloader.utils.models import CookieData, HeadersData


@pytest.fixture
def mock_browser():
    """创建模拟的浏览器"""
    browser = Mock()
    browser.get_cookies.return_value = [{"name": "test", "value": "value"}]
    return browser


@pytest.fixture
def mock_header_manager():
    """创建模拟的请求头管理器"""
    header_manager = Mock()
    header_manager.get_headers.return_value = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://n.dingtalk.com/",
    }
    return header_manager


@patch("dingtalk_downloader.core.cookie_handler.BrowserFactory")
@patch("dingtalk_downloader.core.cookie_handler.HeaderManager")
def test_cookie_handler_init(mock_header_manager_class, mock_browser_factory):
    """测试初始化"""
    mock_header_manager = Mock()
    mock_header_manager_class.return_value = mock_header_manager

    handler = CookieHandler(BROWSER_TYPE_EDGE)

    assert handler.browser_type == BROWSER_TYPE_EDGE
    assert handler.browser is None
    assert handler.header_manager == mock_header_manager
    mock_header_manager_class.assert_called_once()


@patch("dingtalk_downloader.core.cookie_handler.BrowserFactory")
@patch("dingtalk_downloader.core.cookie_handler.HeaderManager")
def test_cookie_handler_get_cookie_success(
    mock_header_manager_class, mock_browser_factory, mock_browser, mock_header_manager
):
    """测试获取Cookie成功"""
    mock_header_manager_class.return_value = mock_header_manager
    mock_browser_factory.create_browser.return_value = mock_browser

    mock_browser.get_cookies.return_value = [{"name": "test", "value": "value"}]

    def get_element_by_xpath_side_effect(xpath):
        mock_element = Mock()
        mock_element.text = "测试直播"
        return mock_element

    mock_browser.get_element_by_xpath.side_effect = get_element_by_xpath_side_effect

    handler = CookieHandler(BROWSER_TYPE_EDGE)

    with patch("builtins.input", return_value=""):
        browser, cookie_data, headers_data, live_name = handler.get_cookie(
            "https://n.dingtalk.com/test"
        )

    assert len(cookie_data) == 1
    assert cookie_data.get("test") == "value"
    assert "User-Agent" in headers_data
    assert "Referer" in headers_data
    assert live_name == "测试直播"
    mock_header_manager.get_headers.assert_called_once()


@patch("dingtalk_downloader.core.cookie_handler.BrowserFactory")
@patch("dingtalk_downloader.core.cookie_handler.HeaderManager")
def test_cookie_handler_get_cookie_browser_error(mock_header_manager_class, mock_browser_factory):
    """测试获取Cookie浏览器错误"""
    from dingtalk_downloader.core.exceptions import CookieError

    mock_header_manager = Mock()
    mock_header_manager_class.return_value = mock_header_manager

    mock_browser_factory.create_browser.side_effect = Exception("浏览器启动失败")

    handler = CookieHandler(BROWSER_TYPE_EDGE)

    with pytest.raises(CookieError):
        handler.get_cookie("https://n.dingtalk.com/test")


@patch("dingtalk_downloader.core.cookie_handler.BrowserFactory")
@patch("dingtalk_downloader.core.cookie_handler.HeaderManager")
def test_cookie_handler_repeat_get_cookie_success(
    mock_header_manager_class, mock_browser_factory, mock_browser, mock_header_manager
):
    """测试重复获取Cookie成功"""
    mock_header_manager_class.return_value = mock_header_manager
    mock_browser_factory.create_browser.return_value = mock_browser

    mock_browser.get_cookies.return_value = [{"name": "test", "value": "value"}]

    def get_element_by_xpath_side_effect(xpath):
        mock_element = Mock()
        mock_element.text = "测试直播"
        return mock_element

    mock_browser.get_element_by_xpath.side_effect = get_element_by_xpath_side_effect

    handler = CookieHandler(BROWSER_TYPE_EDGE)

    with patch("builtins.input", return_value=""):
        handler.get_cookie("https://n.dingtalk.com/test")

    with patch("builtins.input", return_value=""):
        cookie_data, headers_data, live_name = handler.repeat_get_cookie(
            "https://n.dingtalk.com/test2"
        )

    assert len(cookie_data) == 1
    assert cookie_data.get("test") == "value"
    assert "User-Agent" in headers_data
    assert "Referer" in headers_data
    assert live_name == "测试直播"
    mock_header_manager.get_headers.assert_called()


@patch("dingtalk_downloader.core.cookie_handler.BrowserFactory")
@patch("dingtalk_downloader.core.cookie_handler.HeaderManager")
def test_cookie_handler_repeat_get_cookie_first_call(
    mock_header_manager_class, mock_browser_factory, mock_browser, mock_header_manager
):
    """测试重复获取Cookie首次调用"""
    mock_header_manager_class.return_value = mock_header_manager
    mock_browser_factory.create_browser.return_value = mock_browser

    mock_browser.get_cookies.return_value = [{"name": "test", "value": "value"}]

    def get_element_by_xpath_side_effect(xpath):
        mock_element = Mock()
        mock_element.text = "测试直播"
        return mock_element

    mock_browser.get_element_by_xpath.side_effect = get_element_by_xpath_side_effect

    handler = CookieHandler(BROWSER_TYPE_EDGE)

    with patch("builtins.input", return_value=""):
        cookie_data, headers_data, live_name = handler.repeat_get_cookie(
            "https://n.dingtalk.com/test"
        )

    assert len(cookie_data) == 1
    assert cookie_data.get("test") == "value"
    assert "User-Agent" in headers_data
    assert "Referer" in headers_data
    assert live_name == "测试直播"
    mock_header_manager.get_headers.assert_called_once()


@patch("dingtalk_downloader.core.cookie_handler.BrowserFactory")
@patch("dingtalk_downloader.core.cookie_handler.HeaderManager")
def test_cookie_handler_collect_browser_data_success(
    mock_header_manager_class, mock_browser_factory, mock_browser, mock_header_manager
):
    """测试收集浏览器数据成功"""
    mock_header_manager_class.return_value = mock_header_manager
    mock_browser_factory.create_browser.return_value = mock_browser

    mock_browser.get_cookies.return_value = [{"name": "test", "value": "value"}]

    def get_element_by_xpath_side_effect(xpath):
        mock_element = Mock()
        mock_element.text = "测试直播"
        return mock_element

    mock_browser.get_element_by_xpath.side_effect = get_element_by_xpath_side_effect

    handler = CookieHandler(BROWSER_TYPE_EDGE)
    handler.browser = mock_browser

    cookie_data, headers_data, live_name = handler._collect_browser_data()

    assert len(cookie_data) == 1
    assert cookie_data.get("test") == "value"
    assert "User-Agent" in headers_data
    assert "Referer" in headers_data
    assert live_name == "测试直播"
    mock_header_manager.get_headers.assert_called_once()


@patch("dingtalk_downloader.core.cookie_handler.BrowserFactory")
@patch("dingtalk_downloader.core.cookie_handler.HeaderManager")
def test_cookie_handler_get_live_name_xpath_success(
    mock_header_manager_class, mock_browser_factory, mock_browser, mock_header_manager
):
    """测试通过XPath获取直播名称成功"""
    mock_header_manager_class.return_value = mock_header_manager
    mock_browser_factory.create_browser.return_value = mock_browser

    mock_browser.get_cookies.return_value = [{"name": "test", "value": "value"}]

    def get_element_by_xpath_side_effect(xpath):
        mock_element = Mock()
        mock_element.text = "XPath直播名称"
        return mock_element

    mock_browser.get_element_by_xpath.side_effect = get_element_by_xpath_side_effect

    handler = CookieHandler(BROWSER_TYPE_EDGE)
    handler.browser = mock_browser

    live_name = handler._get_live_name()

    assert live_name == "XPath直播名称"


@patch("dingtalk_downloader.core.cookie_handler.BrowserFactory")
@patch("dingtalk_downloader.core.cookie_handler.HeaderManager")
def test_cookie_handler_get_live_name_css_success(
    mock_header_manager_class, mock_browser_factory, mock_browser, mock_header_manager
):
    """测试通过CSS选择器获取直播名称成功"""
    mock_header_manager_class.return_value = mock_header_manager
    mock_browser_factory.create_browser.return_value = mock_browser

    mock_browser.get_cookies.return_value = [{"name": "test", "value": "value"}]

    def get_element_by_xpath_side_effect(xpath):
        raise Exception("XPath failed")

    def get_element_by_class_name_side_effect(class_name):
        mock_element = Mock()
        mock_element.text = "CSS直播名称"
        return mock_element

    mock_browser.get_element_by_xpath.side_effect = get_element_by_xpath_side_effect
    mock_browser.get_element_by_class_name.side_effect = get_element_by_class_name_side_effect

    handler = CookieHandler(BROWSER_TYPE_EDGE)
    handler.browser = mock_browser

    live_name = handler._get_live_name()

    assert live_name == "CSS直播名称"


@patch("dingtalk_downloader.core.cookie_handler.BrowserFactory")
@patch("dingtalk_downloader.core.cookie_handler.HeaderManager")
def test_cookie_handler_get_live_name_fallback(
    mock_header_manager_class, mock_browser_factory, mock_browser, mock_header_manager
):
    """测试直播名称获取失败回退"""
    mock_header_manager_class.return_value = mock_header_manager
    mock_browser_factory.create_browser.return_value = mock_browser

    mock_browser.get_cookies.return_value = [{"name": "test", "value": "value"}]

    def get_element_by_xpath_side_effect(xpath):
        raise Exception("XPath failed")

    def get_element_by_class_name_side_effect(class_name):
        raise Exception("CSS failed")

    mock_browser.get_element_by_xpath.side_effect = get_element_by_xpath_side_effect
    mock_browser.get_element_by_class_name.side_effect = get_element_by_class_name_side_effect

    handler = CookieHandler(BROWSER_TYPE_EDGE)
    handler.browser = mock_browser

    live_name = handler._get_live_name()

    assert live_name == "直播视频名称不可获取"


@patch("dingtalk_downloader.core.cookie_handler.BrowserFactory")
@patch("dingtalk_downloader.core.cookie_handler.HeaderManager")
def test_cookie_handler_close(
    mock_header_manager_class, mock_browser_factory, mock_browser, mock_header_manager
):
    """测试关闭浏览器"""
    mock_header_manager_class.return_value = mock_header_manager
    mock_browser_factory.create_browser.return_value = mock_browser

    handler = CookieHandler(BROWSER_TYPE_EDGE)

    with patch("builtins.input", return_value=""):
        handler.get_cookie("https://n.dingtalk.com/test")

    handler.close()

    mock_browser.close.assert_called_once()
    assert handler.browser is None
