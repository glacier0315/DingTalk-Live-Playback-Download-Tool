"""
钉钉直播回放下载工具 - chrome_driver 单元测试

本模块测试 Chrome 浏览器驱动模块。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2026-01-24: 优化测试，删除重复测试，添加继承测试
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.browser.chrome_driver import ChromeDriver
from dingtalk_downloader.browser.browser_driver import BrowserDriver


class TestChromeDriverInheritance:
    """测试 ChromeDriver 继承关系"""

    def test_chrome_driver_is_subclass_of_browser_driver(self):
        """测试 ChromeDriver 是 BrowserDriver 的子类"""
        assert issubclass(ChromeDriver, BrowserDriver)

    def test_chrome_driver_instance_is_browser_driver(self):
        """测试 ChromeDriver 实例是 BrowserDriver 类型"""
        driver = ChromeDriver()
        assert isinstance(driver, BrowserDriver)

    def test_chrome_driver_init_calls_parent_init(self):
        """测试 ChromeDriver.__init__ 调用父类初始化"""
        driver = ChromeDriver()
        assert driver.driver is None


class TestChromeDriverInit:
    """测试 ChromeDriver 初始化"""

    def test_chrome_driver_init(self):
        """测试 ChromeDriver 初始化"""
        driver = ChromeDriver()
        assert driver.driver is None


class TestChromeDriverCreateDriver:
    """测试 create_driver 方法（Chrome 特定实现）"""

    def test_create_driver_returns_chrome_instance(self):
        """测试创建 Chrome 浏览器实例"""
        with patch("dingtalk_downloader.browser.chrome_driver.webdriver.Chrome") as mock_chrome:
            mock_driver_instance = Mock()
            mock_chrome.return_value = mock_driver_instance

            chrome_driver = ChromeDriver()
            result = chrome_driver.create_driver()

            assert result == mock_driver_instance
            assert chrome_driver.driver == mock_driver_instance
            mock_chrome.assert_called_once()

    def test_create_driver_configures_chrome_options(self):
        """测试创建驱动时配置 Chrome 选项"""
        with patch("dingtalk_downloader.browser.chrome_driver.webdriver.Chrome") as mock_chrome:
            mock_driver_instance = Mock()
            mock_chrome.return_value = mock_driver_instance

            chrome_driver = ChromeDriver()
            chrome_driver.create_driver()

            call_args = mock_chrome.call_args
            assert "options" in call_args.kwargs

    def test_create_driver_sets_driver_attribute(self):
        """测试创建驱动时设置 driver 属性"""
        with patch("dingtalk_downloader.browser.chrome_driver.webdriver.Chrome") as mock_chrome:
            mock_driver_instance = Mock()
            mock_chrome.return_value = mock_driver_instance

            chrome_driver = ChromeDriver()
            chrome_driver.create_driver()

            assert chrome_driver.driver == mock_driver_instance


class TestChromeDriverGetLog:
    """测试 get_log 方法（Chrome 特定实现）"""

    def test_get_log_with_driver(self):
        """测试获取浏览器日志 - 有驱动实例"""
        chrome_driver = ChromeDriver()
        chrome_driver.driver = Mock()

        mock_logs = [{"level": "INFO", "message": "test"}]
        chrome_driver.driver.get_log.return_value = mock_logs

        result = chrome_driver.get_log("performance")

        assert result == mock_logs
        chrome_driver.driver.get_log.assert_called_once_with("performance")

    def test_get_log_without_driver(self):
        """测试获取浏览器日志 - 无驱动实例"""
        chrome_driver = ChromeDriver()

        result = chrome_driver.get_log("performance")

        assert result == []

    def test_get_log_different_log_types(self):
        """测试获取不同类型的日志"""
        chrome_driver = ChromeDriver()
        chrome_driver.driver = Mock()

        mock_logs = [{"level": "INFO", "message": "test"}]
        chrome_driver.driver.get_log.return_value = mock_logs

        for log_type in ["performance", "browser", "driver"]:
            result = chrome_driver.get_log(log_type)
            assert result == mock_logs


class TestChromeDriverInheritedMethods:
    """测试继承自父类的方法"""

    def test_get_element_by_xpath_uses_parent_implementation(self):
        """测试 get_element_by_xpath 使用父类实现"""
        chrome_driver = ChromeDriver()
        chrome_driver.driver = Mock()

        mock_element = Mock()
        chrome_driver.driver.find_element.return_value = mock_element

        result = chrome_driver.get_element_by_xpath("//div[@class='test']")

        assert result == mock_element

    def test_get_element_by_class_name_uses_parent_implementation(self):
        """测试 get_element_by_class_name 使用父类实现"""
        chrome_driver = ChromeDriver()
        chrome_driver.driver = Mock()

        mock_element = Mock()
        chrome_driver.driver.find_element.return_value = mock_element

        result = chrome_driver.get_element_by_class_name("test-class")

        assert result == mock_element

    def test_get_cookies_uses_parent_implementation(self):
        """测试 get_cookies 使用父类实现"""
        chrome_driver = ChromeDriver()
        chrome_driver.driver = Mock()

        mock_cookies = [{"name": "cookie1", "value": "value1"}]
        chrome_driver.driver.get_cookies.return_value = mock_cookies

        result = chrome_driver.get_cookies()

        assert result == mock_cookies

    def test_navigate_uses_parent_implementation(self):
        """测试 navigate 使用父类实现"""
        chrome_driver = ChromeDriver()
        chrome_driver.driver = Mock()

        url = "https://n.dingtalk.com/live/123"
        chrome_driver.navigate(url)

        chrome_driver.driver.get.assert_called_once_with(url)

    def test_wait_for_video_uses_parent_implementation(self):
        """测试 wait_for_video 使用父类实现"""
        chrome_driver = ChromeDriver()
        chrome_driver.driver = Mock()

        with patch("dingtalk_downloader.browser.browser_driver.WebDriverWait") as mock_wait:
            chrome_driver.wait_for_video(timeout=10)

            mock_wait.assert_called_once_with(chrome_driver.driver, 10)

    def test_close_uses_parent_implementation(self):
        """测试 close 使用父类实现"""
        chrome_driver = ChromeDriver()
        chrome_driver.driver = Mock()

        chrome_driver.close()

        assert chrome_driver.driver is None

    def test_is_driver_initialized_uses_parent_implementation(self):
        """测试 is_driver_initialized 使用父类实现"""
        chrome_driver = ChromeDriver()
        assert chrome_driver.is_driver_initialized() is False

        chrome_driver.driver = Mock()
        assert chrome_driver.is_driver_initialized() is True

    def test_get_driver_uses_parent_implementation(self):
        """测试 get_driver 使用父类实现"""
        chrome_driver = ChromeDriver()
        assert chrome_driver.get_driver() is None

        mock_driver = Mock()
        chrome_driver.driver = mock_driver
        assert chrome_driver.get_driver() == mock_driver


class TestChromeDriverFullWorkflow:
    """测试完整工作流程"""

    def test_full_workflow(self):
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

            chrome_driver.close()
            assert chrome_driver.driver is None

    def test_multiple_create_and_close_cycles(self):
        """测试多次创建和关闭浏览器"""
        with patch("dingtalk_downloader.browser.chrome_driver.webdriver.Chrome") as mock_chrome:
            mock_driver_instance = Mock()
            mock_chrome.return_value = mock_driver_instance

            chrome_driver = ChromeDriver()

            for i in range(3):
                driver = chrome_driver.create_driver()
                assert driver is not None
                chrome_driver.close()
                assert chrome_driver.driver is None
