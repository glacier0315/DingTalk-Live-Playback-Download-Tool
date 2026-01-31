"""
钉钉直播回放下载工具 - firefox_driver 单元测试

本模块测试 Firefox 浏览器驱动模块。

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

from dingtalk_downloader.browser.firefox_driver import FirefoxDriver
from dingtalk_downloader.browser.browser_driver import BrowserDriver


class TestFirefoxDriverInheritance:
    """测试 FirefoxDriver 继承关系"""

    def test_firefox_driver_is_subclass_of_browser_driver(self):
        """测试 FirefoxDriver 是 BrowserDriver 的子类"""
        assert issubclass(FirefoxDriver, BrowserDriver)

    def test_firefox_driver_instance_is_browser_driver(self):
        """测试 FirefoxDriver 实例是 BrowserDriver 类型"""
        driver = FirefoxDriver()
        assert isinstance(driver, BrowserDriver)

    def test_firefox_driver_init_calls_parent_init(self):
        """测试 FirefoxDriver.__init__ 调用父类初始化"""
        driver = FirefoxDriver()
        assert driver.driver is None


class TestFirefoxDriverInit:
    """测试 FirefoxDriver 初始化"""

    def test_firefox_driver_init(self):
        """测试 FirefoxDriver 初始化"""
        driver = FirefoxDriver()
        assert driver.driver is None


class TestFirefoxDriverCreateDriver:
    """测试 create_driver 方法（Firefox 特定实现）"""

    def test_create_driver_returns_firefox_instance(self):
        """测试创建 Firefox 浏览器实例"""
        with patch("dingtalk_downloader.browser.firefox_driver.webdriver.Firefox") as mock_firefox:
            mock_driver_instance = Mock()
            mock_firefox.return_value = mock_driver_instance

            firefox_driver = FirefoxDriver()
            result = firefox_driver.create_driver()

            assert result == mock_driver_instance
            assert firefox_driver.driver == mock_driver_instance
            mock_firefox.assert_called_once()

    def test_create_driver_configures_firefox_options(self):
        """测试创建驱动时配置 Firefox 选项"""
        with patch("dingtalk_downloader.browser.firefox_driver.webdriver.Firefox") as mock_firefox:
            mock_driver_instance = Mock()
            mock_firefox.return_value = mock_driver_instance

            firefox_driver = FirefoxDriver()
            firefox_driver.create_driver()

            call_args = mock_firefox.call_args
            assert "options" in call_args.kwargs

    def test_create_driver_sets_driver_attribute(self):
        """测试创建驱动时设置 driver 属性"""
        with patch("dingtalk_downloader.browser.firefox_driver.webdriver.Firefox") as mock_firefox:
            mock_driver_instance = Mock()
            mock_firefox.return_value = mock_driver_instance

            firefox_driver = FirefoxDriver()
            firefox_driver.create_driver()

            assert firefox_driver.driver == mock_driver_instance


class TestFirefoxDriverGetLog:
    """测试 get_log 方法（Firefox 特定实现）"""

    def test_get_log_with_driver(self):
        """测试获取浏览器日志 - 有驱动实例"""
        firefox_driver = FirefoxDriver()
        firefox_driver.driver = Mock()

        mock_logs = [{"name": "test", "duration": 100}]
        firefox_driver.driver.execute_script.return_value = mock_logs

        result = firefox_driver.get_log("performance")

        assert result == mock_logs
        firefox_driver.driver.execute_script.assert_called_once()

    def test_get_log_without_driver(self):
        """测试获取浏览器日志 - 无驱动实例"""
        firefox_driver = FirefoxDriver()

        result = firefox_driver.get_log("performance")

        assert result == []

    def test_get_log_uses_javascript(self):
        """测试 get_log 使用 JavaScript 获取日志"""
        firefox_driver = FirefoxDriver()
        firefox_driver.driver = Mock()

        mock_logs = []
        firefox_driver.driver.execute_script.return_value = mock_logs

        result = firefox_driver.get_log("performance")

        assert result == mock_logs
        firefox_driver.driver.execute_script.assert_called_once()
        script_call = firefox_driver.driver.execute_script.call_args[0][0]
        assert "performance" in script_call or "window.performance" in script_call


class TestFirefoxDriverInheritedMethods:
    """测试继承自父类的方法"""

    def test_get_element_by_xpath_uses_parent_implementation(self):
        """测试 get_element_by_xpath 使用父类实现"""
        firefox_driver = FirefoxDriver()
        firefox_driver.driver = Mock()

        mock_element = Mock()
        firefox_driver.driver.find_element.return_value = mock_element

        result = firefox_driver.get_element_by_xpath("//div[@class='test']")

        assert result == mock_element

    def test_get_element_by_class_name_uses_parent_implementation(self):
        """测试 get_element_by_class_name 使用父类实现"""
        firefox_driver = FirefoxDriver()
        firefox_driver.driver = Mock()

        mock_element = Mock()
        firefox_driver.driver.find_element.return_value = mock_element

        result = firefox_driver.get_element_by_class_name("test-class")

        assert result == mock_element

    def test_get_cookies_uses_parent_implementation(self):
        """测试 get_cookies 使用父类实现"""
        firefox_driver = FirefoxDriver()
        firefox_driver.driver = Mock()

        mock_cookies = [{"name": "cookie1", "value": "value1"}]
        firefox_driver.driver.get_cookies.return_value = mock_cookies

        result = firefox_driver.get_cookies()

        assert result == mock_cookies

    def test_navigate_uses_parent_implementation(self):
        """测试 navigate 使用父类实现"""
        firefox_driver = FirefoxDriver()
        firefox_driver.driver = Mock()

        url = "https://n.dingtalk.com/live/123"
        firefox_driver.navigate(url)

        firefox_driver.driver.get.assert_called_once_with(url)

    def test_wait_for_video_uses_parent_implementation(self):
        """测试 wait_for_video 使用父类实现"""
        firefox_driver = FirefoxDriver()
        firefox_driver.driver = Mock()

        with patch("dingtalk_downloader.browser.browser_driver.WebDriverWait") as mock_wait:
            firefox_driver.wait_for_video(timeout=10)

            mock_wait.assert_called_once_with(firefox_driver.driver, 10)

    def test_close_uses_parent_implementation(self):
        """测试 close 使用父类实现"""
        firefox_driver = FirefoxDriver()
        firefox_driver.driver = Mock()

        firefox_driver.close()

        assert firefox_driver.driver is None

    def test_is_driver_initialized_uses_parent_implementation(self):
        """测试 is_driver_initialized 使用父类实现"""
        firefox_driver = FirefoxDriver()
        assert firefox_driver.is_driver_initialized() is False

        firefox_driver.driver = Mock()
        assert firefox_driver.is_driver_initialized() is True

    def test_get_driver_uses_parent_implementation(self):
        """测试 get_driver 使用父类实现"""
        firefox_driver = FirefoxDriver()
        assert firefox_driver.get_driver() is None

        mock_driver = Mock()
        firefox_driver.driver = mock_driver
        assert firefox_driver.get_driver() == mock_driver


class TestFirefoxDriverFullWorkflow:
    """测试完整工作流程"""

    def test_full_workflow(self):
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

    def test_multiple_create_and_close_cycles(self):
        """测试多次创建和关闭浏览器"""
        with patch("dingtalk_downloader.browser.firefox_driver.webdriver.Firefox") as mock_firefox:
            mock_driver_instance = Mock()
            mock_firefox.return_value = mock_driver_instance

            firefox_driver = FirefoxDriver()

            for i in range(3):
                driver = firefox_driver.create_driver()
                assert driver is not None
                firefox_driver.close()
                assert firefox_driver.driver is None


class TestFirefoxDriverExtractM3u8Links:
    """测试 extract_m3u8_links_from_logs 方法"""

    def test_extract_m3u8_links_from_logs_no_links(self):
        """测试提取m3u8链接（无链接）"""
        driver = FirefoxDriver()
        logs = []
        live_uuid = "test-uuid"
        result = driver.extract_m3u8_links_from_logs(logs, live_uuid)
        assert result == []

    def test_extract_m3u8_links_from_logs_multiple_links(self):
        """测试提取m3u8链接（多个链接）"""
        driver = FirefoxDriver()
        live_uuid = "test-uuid"
        logs = [
            "Network request: https://example.com/video1.m3u8?token=abc&uuid=test-uuid",
            "Network request: https://example.com/video2.m3u8?token=def&uuid=test-uuid"
        ]
        result = driver.extract_m3u8_links_from_logs(logs, live_uuid)
        assert len(result) == 2
        assert "https://example.com/video1.m3u8?token=abc&uuid=test-uuid" in result
        assert "https://example.com/video2.m3u8?token=def&uuid=test-uuid" in result

    def test_extract_m3u8_links_from_logs_exception(self):
        """测试提取m3u8链接（异常）"""
        driver = FirefoxDriver()
        logs = [{"name": "test"}]
        live_uuid = "test-uuid"
        result = driver.extract_m3u8_links_from_logs(logs, live_uuid)
        assert result == []

    def test_extract_m3u8_links_from_logs_invalid_object(self):
        """测试提取m3u8链接（无效对象）"""
        driver = FirefoxDriver()
        logs = [None, 123, True]
        live_uuid = "test-uuid"
        result = driver.extract_m3u8_links_from_logs(logs, live_uuid)
        assert result == []

    def test_extract_m3u8_links_from_logs_dingtalk_links(self):
        """测试提取钉钉m3u8链接"""
        driver = FirefoxDriver()
        logs = [
            "Network request: https://n.dingtalk.com/live/123.m3u8?auth=abc&uuid=test-uuid"
        ]
        live_uuid = "test-uuid"
        result = driver.extract_m3u8_links_from_logs(logs, live_uuid)
        assert len(result) == 1
        assert "https://n.dingtalk.com/live/123.m3u8?auth=abc&uuid=test-uuid" in result

    def test_extract_m3u8_links_from_logs_cleaned_links(self):
        """测试提取并清理m3u8链接"""
        driver = FirefoxDriver()
        logs = [
            "Network request: https://example.com/video.m3u8?token=abc&uuid=test-uuid\"]"
        ]
        live_uuid = "test-uuid"
        result = driver.extract_m3u8_links_from_logs(logs, live_uuid)
        assert len(result) == 1
        assert result[0] == "https://example.com/video.m3u8?token=abc&uuid=test-uuid"

    def test_extract_m3u8_links_from_logs_filter_by_live_uuid(self):
        """测试根据live_uuid过滤m3u8链接"""
        driver = FirefoxDriver()
        live_uuid = "test-uuid-123"
        logs = [
            "Network request: https://example.com/video1.m3u8?token=abc&uuid=other-uuid",
            "Network request: https://example.com/video2.m3u8?token=def&uuid=test-uuid-123",
            "Network request: https://example.com/video3.m3u8?token=ghi&uuid=another-uuid"
        ]
        result = driver.extract_m3u8_links_from_logs(logs, live_uuid)
        assert len(result) == 1
        assert "https://example.com/video2.m3u8?token=def&uuid=test-uuid-123" in result
