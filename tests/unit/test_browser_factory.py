"""
钉钉直播回放下载工具 - browser_factory 单元测试

本模块测试浏览器工厂类。

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

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.browser.browser_factory import BrowserFactory
from dingtalk_downloader.config.constants import (
    BROWSER_TYPE_EDGE,
    BROWSER_TYPE_CHROME,
    BROWSER_TYPE_FIREFOX,
)
from dingtalk_downloader.browser.edge_driver import EdgeDriver
from dingtalk_downloader.browser.chrome_driver import ChromeDriver
from dingtalk_downloader.browser.firefox_driver import FirefoxDriver


def test_browser_factory_create_edge():
    """测试创建 Edge 浏览器"""
    with patch("dingtalk_downloader.browser.edge_driver.webdriver") as mock_webdriver:
        mock_driver = Mock()
        mock_webdriver.Edge.return_value = mock_driver

        browser = BrowserFactory.create_browser(BROWSER_TYPE_EDGE)

        assert isinstance(browser, EdgeDriver)
        assert browser.create_driver() == mock_driver


def test_browser_factory_create_chrome():
    """测试创建 Chrome 浏览器"""
    with patch("dingtalk_downloader.browser.chrome_driver.webdriver") as mock_webdriver:
        mock_driver = Mock()
        mock_webdriver.Chrome.return_value = mock_driver

        browser = BrowserFactory.create_browser(BROWSER_TYPE_CHROME)

        assert isinstance(browser, ChromeDriver)
        assert browser.create_driver() == mock_driver


def test_browser_factory_create_firefox():
    """测试创建 Firefox 浏览器"""
    with patch("dingtalk_downloader.browser.firefox_driver.webdriver") as mock_webdriver:
        mock_driver = Mock()
        mock_webdriver.Firefox.return_value = mock_driver

        browser = BrowserFactory.create_browser(BROWSER_TYPE_FIREFOX)

        assert isinstance(browser, FirefoxDriver)
        assert browser.create_driver() == mock_driver


def test_browser_factory_invalid_type():
    """测试创建不支持的浏览器类型"""
    with pytest.raises(ValueError) as exc_info:
        BrowserFactory.create_browser("safari")

    assert "不支持的浏览器类型: safari" in str(exc_info.value)


def test_browser_factory_case_sensitive():
    """测试浏览器类型大小写敏感"""
    with pytest.raises(ValueError) as exc_info:
        BrowserFactory.create_browser("EDGE")

    assert "不支持的浏览器类型: EDGE" in str(exc_info.value)


def test_browser_factory_empty_type():
    """测试空浏览器类型"""
    with pytest.raises(ValueError) as exc_info:
        BrowserFactory.create_browser("")

    assert "不支持的浏览器类型: " in str(exc_info.value)


def test_browser_factory_none_type():
    """测试 None 浏览器类型"""
    with pytest.raises(ValueError) as exc_info:
        BrowserFactory.create_browser(None)

    assert "不支持的浏览器类型: None" in str(exc_info.value)


def test_browser_factory_multiple_creations():
    """测试创建多个浏览器实例"""
    with patch("dingtalk_downloader.browser.edge_driver.webdriver") as mock_edge_webdriver, patch(
        "dingtalk_downloader.browser.chrome_driver.webdriver"
    ) as mock_chrome_webdriver, patch(
        "dingtalk_downloader.browser.firefox_driver.webdriver"
    ) as mock_firefox_webdriver:

        mock_edge_driver = Mock()
        mock_chrome_driver = Mock()
        mock_firefox_driver = Mock()

        mock_edge_webdriver.Edge.return_value = mock_edge_driver
        mock_chrome_webdriver.Chrome.return_value = mock_chrome_driver
        mock_firefox_webdriver.Firefox.return_value = mock_firefox_driver

        edge_browser = BrowserFactory.create_browser(BROWSER_TYPE_EDGE)
        chrome_browser = BrowserFactory.create_browser(BROWSER_TYPE_CHROME)
        firefox_browser = BrowserFactory.create_browser(BROWSER_TYPE_FIREFOX)

        assert isinstance(edge_browser, EdgeDriver)
        assert isinstance(chrome_browser, ChromeDriver)
        assert isinstance(firefox_browser, FirefoxDriver)
        assert edge_browser.create_driver() == mock_edge_driver
        assert chrome_browser.create_driver() == mock_chrome_driver
        assert firefox_browser.create_driver() == mock_firefox_driver


def test_browser_factory_create_edge_without_mock():
    """测试创建 Edge 浏览器（不使用 mock）"""
    with patch("dingtalk_downloader.browser.edge_driver.webdriver.Edge"):
        browser = BrowserFactory.create_browser(BROWSER_TYPE_EDGE)
        assert isinstance(browser, EdgeDriver)


def test_browser_factory_create_chrome_without_mock():
    """测试创建 Chrome 浏览器（不使用 mock）"""
    with patch("dingtalk_downloader.browser.chrome_driver.webdriver.Chrome"):
        browser = BrowserFactory.create_browser(BROWSER_TYPE_CHROME)
        assert isinstance(browser, ChromeDriver)


def test_browser_factory_create_firefox_without_mock():
    """测试创建 Firefox 浏览器（不使用 mock）"""
    with patch("dingtalk_downloader.browser.firefox_driver.webdriver.Firefox"):
        browser = BrowserFactory.create_browser(BROWSER_TYPE_FIREFOX)
        assert isinstance(browser, FirefoxDriver)
