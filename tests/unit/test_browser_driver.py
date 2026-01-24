"""
钉钉直播回放下载工具 - browser_driver 单元测试

本模块测试浏览器驱动抽象基类模块。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2026-01-21
修改历史：
    - 2026-01-21: 初始版本
    - 2026-01-24: 添加继承测试和新增方法测试
"""

import sys
import os
import pytest
from abc import ABC
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.browser.browser_driver import BrowserDriver


class TestBrowserDriverAbstract:
    """测试 BrowserDriver 抽象基类特性"""

    def test_browser_driver_is_abstract(self):
        """测试 BrowserDriver 是抽象基类"""
        assert issubclass(BrowserDriver, ABC)

    def test_browser_driver_has_abstract_methods(self):
        """测试 BrowserDriver 有所有必需的抽象方法"""
        abstract_methods = ["create_driver", "get_log"]

        for method_name in abstract_methods:
            assert hasattr(BrowserDriver, method_name)
            method = getattr(BrowserDriver, method_name)
            assert getattr(method, "__isabstractmethod__", False)

    def test_browser_driver_has_concrete_methods(self):
        """测试 BrowserDriver 有所有通用的非抽象方法"""
        concrete_methods = [
            "get_element_by_xpath",
            "get_element_by_class_name",
            "get_cookies",
            "navigate",
            "wait_for_video",
            "close",
            "is_driver_initialized",
            "get_driver",
        ]

        for method_name in concrete_methods:
            assert hasattr(BrowserDriver, method_name)
            method = getattr(BrowserDriver, method_name)
            assert callable(method)
            is_abstract = getattr(method, "__isabstractmethod__", False)
            assert not is_abstract, f"{method_name} 不应该是抽象方法"

    def test_browser_driver_cannot_be_instantiated(self):
        """测试 BrowserDriver 不能直接实例化"""
        with pytest.raises(TypeError):
            BrowserDriver()


class ConcreteBrowserDriver(BrowserDriver):
    """具体的浏览器驱动实现，用于测试"""

    def __init__(self):
        super().__init__()
        self.call_log = []

    def create_driver(self):
        self.call_log.append("create_driver")
        return None

    def get_log(self, log_type):
        self.call_log.append(f"get_log:{log_type}")
        return []


class TestBrowserDriverInheritance:
    """测试 BrowserDriver 继承功能"""

    def test_concrete_browser_driver_can_be_instantiated(self):
        """测试具体的浏览器驱动可以实例化"""
        driver = ConcreteBrowserDriver()
        assert driver is not None
        assert isinstance(driver, BrowserDriver)

    def test_concrete_browser_driver_has_driver_attribute(self):
        """测试具体的浏览器驱动有 driver 属性"""
        driver = ConcreteBrowserDriver()
        assert hasattr(driver, "driver")
        assert driver.driver is None

    def test_concrete_browser_driver_implements_all_methods(self):
        """测试具体的浏览器驱动实现了所有必需方法"""
        driver = ConcreteBrowserDriver()

        assert callable(driver.create_driver)
        assert callable(driver.get_log)
        assert callable(driver.get_element_by_xpath)
        assert callable(driver.get_element_by_class_name)
        assert callable(driver.get_cookies)
        assert callable(driver.navigate)
        assert callable(driver.wait_for_video)
        assert callable(driver.close)

    def test_init_calls_parent_init(self):
        """测试 __init__ 调用父类初始化"""
        driver = ConcreteBrowserDriver()
        assert driver.driver is None


class TestBrowserDriverConcreteMethods:
    """测试 BrowserDriver 具体方法实现"""

    def test_create_driver(self):
        """测试 create_driver 方法"""
        driver = ConcreteBrowserDriver()
        result = driver.create_driver()
        assert result is None

    def test_get_log(self):
        """测试 get_log 方法"""
        driver = ConcreteBrowserDriver()
        result = driver.get_log("performance")
        assert result == []

    def test_get_element_by_xpath_without_driver(self):
        """测试 get_element_by_xpath - 无驱动实例"""
        driver = ConcreteBrowserDriver()
        result = driver.get_element_by_xpath("//div[@class='test']")
        assert result is None

    def test_get_element_by_class_name_without_driver(self):
        """测试 get_element_by_class_name - 无驱动实例"""
        driver = ConcreteBrowserDriver()
        result = driver.get_element_by_class_name("test-class")
        assert result is None

    def test_get_cookies_without_driver(self):
        """测试 get_cookies - 无驱动实例"""
        driver = ConcreteBrowserDriver()
        result = driver.get_cookies()
        assert result == []

    def test_navigate_without_driver(self):
        """测试 navigate - 无驱动实例"""
        driver = ConcreteBrowserDriver()
        driver.navigate("https://test.com")

    def test_wait_for_video_without_driver(self):
        """测试 wait_for_video - 无驱动实例"""
        driver = ConcreteBrowserDriver()
        driver.wait_for_video(timeout=10)

    def test_wait_for_video_default_timeout(self):
        """测试 wait_for_video 使用默认超时"""
        driver = ConcreteBrowserDriver()
        driver.wait_for_video()

    def test_close_without_driver(self):
        """测试 close - 无驱动实例"""
        driver = ConcreteBrowserDriver()
        driver.close()

    def test_is_driver_initialized_without_driver(self):
        """测试 is_driver_initialized - 无驱动实例"""
        driver = ConcreteBrowserDriver()
        assert driver.is_driver_initialized() is False

    def test_get_driver_without_driver(self):
        """测试 get_driver - 无驱动实例"""
        driver = ConcreteBrowserDriver()
        assert driver.get_driver() is None


class TestBrowserDriverWithMockedDriver:
    """使用 Mock 驱动测试 BrowserDriver 方法"""

    def test_get_element_by_xpath_with_driver(self):
        """测试 get_element_by_xpath - 有驱动实例"""
        driver = ConcreteBrowserDriver()
        driver.driver = Mock()

        mock_element = Mock()
        driver.driver.find_element.return_value = mock_element

        result = driver.get_element_by_xpath("//div[@class='test']")

        assert result == mock_element
        driver.driver.find_element.assert_called_once()

    def test_get_element_by_class_name_with_driver(self):
        """测试 get_element_by_class_name - 有驱动实例"""
        driver = ConcreteBrowserDriver()
        driver.driver = Mock()

        mock_element = Mock()
        driver.driver.find_element.return_value = mock_element

        result = driver.get_element_by_class_name("test-class")

        assert result == mock_element
        driver.driver.find_element.assert_called_once()

    def test_get_cookies_with_driver(self):
        """测试 get_cookies - 有驱动实例"""
        driver = ConcreteBrowserDriver()
        driver.driver = Mock()

        mock_cookies = [{"name": "cookie1", "value": "value1"}]
        driver.driver.get_cookies.return_value = mock_cookies

        result = driver.get_cookies()

        assert result == mock_cookies
        driver.driver.get_cookies.assert_called_once()

    def test_navigate_with_driver(self):
        """测试 navigate - 有驱动实例"""
        driver = ConcreteBrowserDriver()
        driver.driver = Mock()

        url = "https://test.com"
        driver.navigate(url)

        driver.driver.get.assert_called_once_with(url)

    def test_close_with_driver(self):
        """测试 close - 有驱动实例"""
        driver = ConcreteBrowserDriver()
        driver.driver = Mock()

        driver.close()

        assert driver.driver is None


class TestBrowserDriverNewMethods:
    """测试 BrowserDriver 新增方法"""

    def test_is_driver_initialized_false(self):
        """测试 is_driver_initialized - 未初始化"""
        driver = ConcreteBrowserDriver()
        assert driver.is_driver_initialized() is False

    def test_is_driver_initialized_true(self):
        """测试 is_driver_initialized - 已初始化"""
        driver = ConcreteBrowserDriver()
        driver.driver = Mock()
        assert driver.is_driver_initialized() is True

    def test_get_driver_returns_none(self):
        """测试 get_driver - 未初始化"""
        driver = ConcreteBrowserDriver()
        assert driver.get_driver() is None

    def test_get_driver_returns_driver(self):
        """测试 get_driver - 已初始化"""
        driver = ConcreteBrowserDriver()
        mock_driver = Mock()
        driver.driver = mock_driver
        assert driver.get_driver() == mock_driver


class TestBrowserDriverWaitForVideo:
    """测试 wait_for_video 方法的详细行为"""

    def test_wait_for_video_calls_execute_script(self):
        """测试 wait_for_video 执行 JavaScript 检查"""
        driver = ConcreteBrowserDriver()
        driver.driver = Mock()

        with patch("dingtalk_downloader.browser.browser_driver.WebDriverWait") as mock_wait:
            driver.wait_for_video(timeout=10)

            mock_wait.assert_called_once_with(driver.driver, 10)

    def test_wait_for_video_uses_custom_timeout(self):
        """测试 wait_for_video 使用自定义超时"""
        driver = ConcreteBrowserDriver()
        driver.driver = Mock()

        with patch("dingtalk_downloader.browser.browser_driver.WebDriverWait") as mock_wait:
            custom_timeout = 30
            driver.wait_for_video(timeout=custom_timeout)

            mock_wait.assert_called_once_with(driver.driver, custom_timeout)

    def test_wait_for_video_with_zero_timeout(self):
        """测试 wait_for_video 使用零超时"""
        driver = ConcreteBrowserDriver()
        driver.driver = Mock()

        with patch("dingtalk_downloader.browser.browser_driver.WebDriverWait") as mock_wait:
            driver.wait_for_video(timeout=0)

            mock_wait.assert_called_once_with(driver.driver, 0)
