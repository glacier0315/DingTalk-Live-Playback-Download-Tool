"""
钉钉直播回放下载工具 - edge_driver 单元测试

本模块测试 Edge 浏览器驱动模块。

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

from dingtalk_downloader.browser.edge_driver import EdgeDriver
from dingtalk_downloader.browser.browser_driver import BrowserDriver


class TestEdgeDriverInheritance:
    """测试 EdgeDriver 继承关系"""

    def test_edge_driver_is_subclass_of_browser_driver(self):
        """测试 EdgeDriver 是 BrowserDriver 的子类"""
        assert issubclass(EdgeDriver, BrowserDriver)

    def test_edge_driver_instance_is_browser_driver(self):
        """测试 EdgeDriver 实例是 BrowserDriver 类型"""
        driver = EdgeDriver()
        assert isinstance(driver, BrowserDriver)

    def test_edge_driver_init_calls_parent_init(self):
        """测试 EdgeDriver.__init__ 调用父类初始化"""
        driver = EdgeDriver()
        assert driver.driver is None


class TestEdgeDriverInit:
    """测试 EdgeDriver 初始化"""

    def test_edge_driver_init(self):
        """测试 EdgeDriver 初始化"""
        driver = EdgeDriver()
        assert driver.driver is None


class TestEdgeDriverCreateDriver:
    """测试 create_driver 方法（Edge 特定实现）"""

    def test_create_driver_returns_edge_instance(self):
        """测试创建 Edge 浏览器实例"""
        with patch("dingtalk_downloader.browser.edge_driver.webdriver.Edge") as mock_edge:
            mock_driver_instance = Mock()
            mock_edge.return_value = mock_driver_instance

            edge_driver = EdgeDriver()
            result = edge_driver.create_driver()

            assert result == mock_driver_instance
            assert edge_driver.driver == mock_driver_instance
            mock_edge.assert_called_once()

    def test_create_driver_configures_edge_options(self):
        """测试创建驱动时配置 Edge 选项"""
        with patch("dingtalk_downloader.browser.edge_driver.webdriver.Edge") as mock_edge:
            mock_driver_instance = Mock()
            mock_edge.return_value = mock_driver_instance

            edge_driver = EdgeDriver()
            edge_driver.create_driver()

            call_args = mock_edge.call_args
            assert "options" in call_args.kwargs

    def test_create_driver_sets_driver_attribute(self):
        """测试创建驱动时设置 driver 属性"""
        with patch("dingtalk_downloader.browser.edge_driver.webdriver.Edge") as mock_edge:
            mock_driver_instance = Mock()
            mock_edge.return_value = mock_driver_instance

            edge_driver = EdgeDriver()
            edge_driver.create_driver()

            assert edge_driver.driver == mock_driver_instance


class TestEdgeDriverGetLog:
    """测试 get_log 方法（Edge 特定实现）"""

    def test_get_log_with_driver(self):
        """测试获取浏览器日志 - 有驱动实例"""
        edge_driver = EdgeDriver()
        edge_driver.driver = Mock()

        mock_logs = [{"level": "INFO", "message": "test"}]
        edge_driver.driver.get_log.return_value = mock_logs

        result = edge_driver.get_log("performance")

        assert result == mock_logs
        edge_driver.driver.get_log.assert_called_once_with("performance")

    def test_get_log_without_driver(self):
        """测试获取浏览器日志 - 无驱动实例"""
        edge_driver = EdgeDriver()

        result = edge_driver.get_log("performance")

        assert result == []

    def test_get_log_different_log_types(self):
        """测试获取不同类型的日志"""
        edge_driver = EdgeDriver()
        edge_driver.driver = Mock()

        mock_logs = [{"level": "INFO", "message": "test"}]
        edge_driver.driver.get_log.return_value = mock_logs

        for log_type in ["performance", "browser", "driver"]:
            result = edge_driver.get_log(log_type)
            assert result == mock_logs


class TestEdgeDriverInheritedMethods:
    """测试继承自父类的方法"""

    def test_get_element_by_xpath_uses_parent_implementation(self):
        """测试 get_element_by_xpath 使用父类实现"""
        edge_driver = EdgeDriver()
        edge_driver.driver = Mock()

        mock_element = Mock()
        edge_driver.driver.find_element.return_value = mock_element

        result = edge_driver.get_element_by_xpath("//div[@class='test']")

        assert result == mock_element

    def test_get_element_by_class_name_uses_parent_implementation(self):
        """测试 get_element_by_class_name 使用父类实现"""
        edge_driver = EdgeDriver()
        edge_driver.driver = Mock()

        mock_element = Mock()
        edge_driver.driver.find_element.return_value = mock_element

        result = edge_driver.get_element_by_class_name("test-class")

        assert result == mock_element

    def test_get_cookies_uses_parent_implementation(self):
        """测试 get_cookies 使用父类实现"""
        edge_driver = EdgeDriver()
        edge_driver.driver = Mock()

        mock_cookies = [{"name": "cookie1", "value": "value1"}]
        edge_driver.driver.get_cookies.return_value = mock_cookies

        result = edge_driver.get_cookies()

        assert result == mock_cookies

    def test_navigate_uses_parent_implementation(self):
        """测试 navigate 使用父类实现"""
        edge_driver = EdgeDriver()
        edge_driver.driver = Mock()

        url = "https://n.dingtalk.com/live/123"
        edge_driver.navigate(url)

        edge_driver.driver.get.assert_called_once_with(url)

    def test_wait_for_video_uses_parent_implementation(self):
        """测试 wait_for_video 使用父类实现"""
        edge_driver = EdgeDriver()
        edge_driver.driver = Mock()

        with patch("dingtalk_downloader.browser.browser_driver.WebDriverWait") as mock_wait:
            edge_driver.wait_for_video(timeout=10)

            mock_wait.assert_called_once_with(edge_driver.driver, 10)

    def test_close_uses_parent_implementation(self):
        """测试 close 使用父类实现"""
        edge_driver = EdgeDriver()
        edge_driver.driver = Mock()

        edge_driver.close()

        assert edge_driver.driver is None

    def test_is_driver_initialized_uses_parent_implementation(self):
        """测试 is_driver_initialized 使用父类实现"""
        edge_driver = EdgeDriver()
        assert edge_driver.is_driver_initialized() is False

        edge_driver.driver = Mock()
        assert edge_driver.is_driver_initialized() is True

    def test_get_driver_uses_parent_implementation(self):
        """测试 get_driver 使用父类实现"""
        edge_driver = EdgeDriver()
        assert edge_driver.get_driver() is None

        mock_driver = Mock()
        edge_driver.driver = mock_driver
        assert edge_driver.get_driver() == mock_driver


class TestEdgeDriverFullWorkflow:
    """测试完整工作流程"""

    def test_full_workflow(self):
        """测试完整工作流程"""
        with patch("dingtalk_downloader.browser.edge_driver.webdriver.Edge") as mock_edge:
            mock_driver_instance = Mock()
            mock_driver_instance.get_cookies.return_value = []
            mock_driver_instance.execute_script.return_value = "Mozilla/5.0"
            mock_edge.return_value = mock_driver_instance

            edge_driver = EdgeDriver()

            driver = edge_driver.create_driver()
            assert driver is not None

            edge_driver.navigate("https://n.dingtalk.com/test")
            mock_driver_instance.get.assert_called_once()

            cookies = edge_driver.get_cookies()
            assert isinstance(cookies, list)

            edge_driver.close()
            assert edge_driver.driver is None

    def test_multiple_create_and_close_cycles(self):
        """测试多次创建和关闭浏览器"""
        with patch("dingtalk_downloader.browser.edge_driver.webdriver.Edge") as mock_edge:
            mock_driver_instance = Mock()
            mock_edge.return_value = mock_driver_instance

            edge_driver = EdgeDriver()

            for i in range(3):
                driver = edge_driver.create_driver()
                assert driver is not None
                edge_driver.close()
                assert edge_driver.driver is None
