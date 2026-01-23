"""
钉钉直播回放下载工具 - firefox_driver 单元测试

本模块测试Firefox浏览器驱动模块。

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

from dingtalk_downloader.browser.firefox_driver import FirefoxDriver


def test_firefox_driver_init():
    """测试FirefoxDriver初始化"""
    driver = FirefoxDriver()

    assert driver.driver is None


def test_create_driver():
    """测试创建Firefox浏览器实例"""
    with patch("dingtalk_downloader.browser.firefox_driver.webdriver.Firefox") as mock_firefox:
        mock_driver_instance = Mock()
        mock_firefox.return_value = mock_driver_instance

        firefox_driver = FirefoxDriver()
        result = firefox_driver.create_driver()

        assert result == mock_driver_instance
        assert firefox_driver.driver == mock_driver_instance
        mock_firefox.assert_called_once()

        call_args = mock_firefox.call_args
        assert "options" in call_args.kwargs


def test_get_log_with_driver():
    """测试获取浏览器日志 - 有驱动实例"""
    firefox_driver = FirefoxDriver()
    firefox_driver.driver = Mock()

    mock_logs = [{"name": "test", "duration": 100}]
    firefox_driver.driver.execute_script.return_value = mock_logs

    result = firefox_driver.get_log("performance")

    assert result == mock_logs
    firefox_driver.driver.execute_script.assert_called_once()


def test_get_log_without_driver():
    """测试获取浏览器日志 - 无驱动实例"""
    firefox_driver = FirefoxDriver()

    result = firefox_driver.get_log("performance")

    assert result == []


def test_get_element_by_xpath_with_driver():
    """测试通过XPath获取元素 - 有驱动实例"""
    firefox_driver = FirefoxDriver()
    firefox_driver.driver = Mock()

    mock_element = Mock()
    firefox_driver.driver.find_element.return_value = mock_element

    result = firefox_driver.get_element_by_xpath("//div[@class='test']")

    assert result == mock_element
    firefox_driver.driver.find_element.assert_called_once()


def test_get_element_by_xpath_without_driver():
    """测试通过XPath获取元素 - 无驱动实例"""
    firefox_driver = FirefoxDriver()

    result = firefox_driver.get_element_by_xpath("//div[@class='test']")

    assert result is None


def test_get_element_by_class_name_with_driver():
    """测试通过类名获取元素 - 有驱动实例"""
    firefox_driver = FirefoxDriver()
    firefox_driver.driver = Mock()

    mock_element = Mock()
    firefox_driver.driver.find_element.return_value = mock_element

    result = firefox_driver.get_element_by_class_name("test-class")

    assert result == mock_element
    firefox_driver.driver.find_element.assert_called_once()


def test_get_element_by_class_name_without_driver():
    """测试通过类名获取元素 - 无驱动实例"""
    firefox_driver = FirefoxDriver()

    result = firefox_driver.get_element_by_class_name("test-class")

    assert result is None


def test_get_cookies_with_driver():
    """测试获取Cookie - 有驱动实例"""
    firefox_driver = FirefoxDriver()
    firefox_driver.driver = Mock()

    mock_cookies = [{"name": "cookie1", "value": "value1"}, {"name": "cookie2", "value": "value2"}]
    firefox_driver.driver.get_cookies.return_value = mock_cookies

    result = firefox_driver.get_cookies()

    assert result == mock_cookies
    firefox_driver.driver.get_cookies.assert_called_once()


def test_get_cookies_without_driver():
    """测试获取Cookie - 无驱动实例"""
    firefox_driver = FirefoxDriver()

    result = firefox_driver.get_cookies()

    assert result == []


def test_navigate_with_driver():
    """测试导航到URL - 有驱动实例"""
    firefox_driver = FirefoxDriver()
    firefox_driver.driver = Mock()

    url = "https://n.dingtalk.com/live/123"
    firefox_driver.navigate(url)

    firefox_driver.driver.get.assert_called_once_with(url)


def test_navigate_without_driver():
    """测试导航到URL - 无驱动实例"""
    firefox_driver = FirefoxDriver()

    url = "https://n.dingtalk.com/live/123"
    firefox_driver.navigate(url)

    assert firefox_driver.driver is None


def test_wait_for_video_with_driver():
    """测试等待视频加载 - 有驱动实例"""
    firefox_driver = FirefoxDriver()
    firefox_driver.driver = Mock()

    with patch("dingtalk_downloader.browser.firefox_driver.WebDriverWait") as mock_wait:
        firefox_driver.wait_for_video(timeout=10)

        mock_wait.assert_called_once_with(firefox_driver.driver, 10)
        mock_wait.return_value.until.assert_called_once()


def test_wait_for_video_without_driver():
    """测试等待视频加载 - 无驱动实例"""
    firefox_driver = FirefoxDriver()

    firefox_driver.wait_for_video(timeout=10)

    assert firefox_driver.driver is None


def test_close_with_driver():
    """测试关闭浏览器 - 有驱动实例"""
    firefox_driver = FirefoxDriver()
    firefox_driver.driver = Mock()

    firefox_driver.close()

    assert firefox_driver.driver is None


def test_close_without_driver():
    """测试关闭浏览器 - 无驱动实例"""
    firefox_driver = FirefoxDriver()

    firefox_driver.close()

    assert firefox_driver.driver is None


def test_full_workflow():
    """测试完整工作流程"""
    with patch("dingtalk_downloader.browser.firefox_driver.webdriver.Firefox") as mock_firefox:
        mock_driver_instance = Mock()
        mock_driver_instance.get_cookies.return_value = []
        mock_driver_instance.execute_script.return_value = "Mozilla/5.0"
        mock_firefox.return_value = mock_driver_instance

        firefox_driver = FirefoxDriver()

        driver = firefox_driver.create_driver()
        assert driver is not None
        firefox_driver.navigate("https://n.dingtalk.com/test")
        mock_driver_instance.get.assert_called_once()
        cookies = firefox_driver.get_cookies()
        assert isinstance(cookies, list)
        firefox_driver.close()
        assert firefox_driver.driver is None
