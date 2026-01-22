"""
钉钉直播回放下载工具 - chrome_driver 单元测试

本模块测试Chrome浏览器驱动模块。

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

from dingtalk_downloader.browser.chrome_driver import ChromeDriver


def test_chrome_driver_init():
    """测试ChromeDriver初始化"""
    driver = ChromeDriver()

    assert driver.driver is None


def test_create_driver():
    """测试创建Chrome浏览器实例"""
    with patch("dingtalk_downloader.browser.chrome_driver.webdriver.Chrome") as mock_chrome:
        mock_driver_instance = Mock()
        mock_chrome.return_value = mock_driver_instance

        chrome_driver = ChromeDriver()
        result = chrome_driver.create_driver()

        assert result == mock_driver_instance
        assert chrome_driver.driver == mock_driver_instance
        mock_chrome.assert_called_once()

        call_args = mock_chrome.call_args
        assert "options" in call_args.kwargs


def test_get_log_with_driver():
    """测试获取浏览器日志 - 有驱动实例"""
    chrome_driver = ChromeDriver()
    chrome_driver.driver = Mock()

    mock_logs = [{"level": "INFO", "message": "test"}]
    chrome_driver.driver.get_log.return_value = mock_logs

    result = chrome_driver.get_log("performance")

    assert result == mock_logs
    chrome_driver.driver.get_log.assert_called_once_with("performance")


def test_get_log_without_driver():
    """测试获取浏览器日志 - 无驱动实例"""
    chrome_driver = ChromeDriver()

    result = chrome_driver.get_log("performance")

    assert result == []


def test_get_element_by_xpath_with_driver():
    """测试通过XPath获取元素 - 有驱动实例"""
    chrome_driver = ChromeDriver()
    chrome_driver.driver = Mock()

    mock_element = Mock()
    chrome_driver.driver.find_element.return_value = mock_element

    result = chrome_driver.get_element_by_xpath("//div[@class='test']")

    assert result == mock_element
    chrome_driver.driver.find_element.assert_called_once()


def test_get_element_by_xpath_without_driver():
    """测试通过XPath获取元素 - 无驱动实例"""
    chrome_driver = ChromeDriver()

    result = chrome_driver.get_element_by_xpath("//div[@class='test']")

    assert result is None


def test_get_element_by_class_name_with_driver():
    """测试通过类名获取元素 - 有驱动实例"""
    chrome_driver = ChromeDriver()
    chrome_driver.driver = Mock()

    mock_element = Mock()
    chrome_driver.driver.find_element.return_value = mock_element

    result = chrome_driver.get_element_by_class_name("test-class")

    assert result == mock_element
    chrome_driver.driver.find_element.assert_called_once()


def test_get_element_by_class_name_without_driver():
    """测试通过类名获取元素 - 无驱动实例"""
    chrome_driver = ChromeDriver()

    result = chrome_driver.get_element_by_class_name("test-class")

    assert result is None


def test_get_user_agent_with_driver():
    """测试获取User-Agent - 有驱动实例"""
    chrome_driver = ChromeDriver()
    chrome_driver.driver = Mock()

    mock_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    chrome_driver.driver.execute_script.return_value = mock_user_agent

    result = chrome_driver.get_user_agent()

    assert result == mock_user_agent
    chrome_driver.driver.execute_script.assert_called_once_with("return navigator.userAgent")


def test_get_user_agent_without_driver():
    """测试获取User-Agent - 无驱动实例"""
    chrome_driver = ChromeDriver()

    result = chrome_driver.get_user_agent()

    assert result == ""


def test_get_referer_with_driver():
    """测试获取Referer - 有驱动实例"""
    chrome_driver = ChromeDriver()
    chrome_driver.driver = Mock()

    mock_referer = "https://n.dingtalk.com/live/123"
    chrome_driver.driver.execute_script.return_value = mock_referer

    result = chrome_driver.get_referer()

    assert result == mock_referer
    chrome_driver.driver.execute_script.assert_called_once_with("return document.referrer")


def test_get_referer_with_driver_empty():
    """测试获取Referer - 有驱动实例但返回空"""
    chrome_driver = ChromeDriver()
    chrome_driver.driver = Mock()

    chrome_driver.driver.execute_script.return_value = None

    result = chrome_driver.get_referer()

    assert result == "https://n.dingtalk.com/"
    chrome_driver.driver.execute_script.assert_called_once_with("return document.referrer")


def test_get_referer_without_driver():
    """测试获取Referer - 无驱动实例"""
    chrome_driver = ChromeDriver()

    result = chrome_driver.get_referer()

    assert result == "https://n.dingtalk.com/"


def test_get_cookies_with_driver():
    """测试获取Cookie - 有驱动实例"""
    chrome_driver = ChromeDriver()
    chrome_driver.driver = Mock()

    mock_cookies = [{"name": "cookie1", "value": "value1"}, {"name": "cookie2", "value": "value2"}]
    chrome_driver.driver.get_cookies.return_value = mock_cookies

    result = chrome_driver.get_cookies()

    assert result == mock_cookies
    chrome_driver.driver.get_cookies.assert_called_once()


def test_get_cookies_without_driver():
    """测试获取Cookie - 无驱动实例"""
    chrome_driver = ChromeDriver()

    result = chrome_driver.get_cookies()

    assert result == []


def test_navigate_with_driver():
    """测试导航到URL - 有驱动实例"""
    chrome_driver = ChromeDriver()
    chrome_driver.driver = Mock()

    url = "https://n.dingtalk.com/live/123"
    chrome_driver.navigate(url)

    chrome_driver.driver.get.assert_called_once_with(url)


def test_navigate_without_driver():
    """测试导航到URL - 无驱动实例"""
    chrome_driver = ChromeDriver()

    url = "https://n.dingtalk.com/live/123"
    chrome_driver.navigate(url)

    assert chrome_driver.driver is None


def test_wait_for_video_with_driver():
    """测试等待视频加载 - 有驱动实例"""
    chrome_driver = ChromeDriver()
    chrome_driver.driver = Mock()

    with patch("dingtalk_downloader.browser.chrome_driver.WebDriverWait") as mock_wait:
        chrome_driver.wait_for_video(timeout=10)

        mock_wait.assert_called_once_with(chrome_driver.driver, 10)
        mock_wait.return_value.until.assert_called_once()


def test_wait_for_video_without_driver():
    """测试等待视频加载 - 无驱动实例"""
    chrome_driver = ChromeDriver()

    chrome_driver.wait_for_video(timeout=10)

    assert chrome_driver.driver is None


def test_close_with_driver():
    """测试关闭浏览器 - 有驱动实例"""
    chrome_driver = ChromeDriver()
    chrome_driver.driver = Mock()

    chrome_driver.close()

    assert chrome_driver.driver is None


def test_close_without_driver():
    """测试关闭浏览器 - 无驱动实例"""
    chrome_driver = ChromeDriver()

    chrome_driver.close()

    assert chrome_driver.driver is None


def test_full_workflow():
    """测试完整工作流程"""
    with patch("dingtalk_downloader.browser.chrome_driver.webdriver.Chrome") as mock_chrome:
        mock_driver_instance = Mock()
        mock_driver_instance.get_cookies.return_value = []
        mock_driver_instance.execute_script.return_value = "Mozilla/5.0"
        mock_chrome.return_value = mock_driver_instance

        chrome_driver = ChromeDriver()

        driver = chrome_driver.create_driver()
        assert driver is not None

        chrome_driver.navigate("https://n.dingtalk.com/test")
        mock_driver_instance.get.assert_called_once()

        cookies = chrome_driver.get_cookies()
        assert isinstance(cookies, list)

        user_agent = chrome_driver.get_user_agent()
        assert isinstance(user_agent, str)

        referer = chrome_driver.get_referer()
        assert isinstance(referer, str)

        chrome_driver.close()
        assert chrome_driver.driver is None
