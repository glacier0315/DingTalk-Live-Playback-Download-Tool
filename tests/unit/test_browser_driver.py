"""
钉钉直播回放下载工具 - browser_driver 单元测试

本模块测试浏览器驱动抽象基类模块。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2026-01-21
修改历史：
    - 2026-01-21: 初始版本
"""

import sys
import os
import pytest
from abc import ABC

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.browser.browser_driver import BrowserDriver


def test_browser_driver_is_abstract():
    """测试BrowserDriver是抽象基类"""
    assert issubclass(BrowserDriver, ABC)


def test_browser_driver_has_abstract_methods():
    """测试BrowserDriver有所有必需的抽象方法"""
    abstract_methods = [
        "create_driver",
        "get_log",
        "get_element_by_xpath",
        "get_element_by_class_name",
        "get_cookies",
        "navigate",
        "wait_for_video",
        "close",
    ]

    for method_name in abstract_methods:
        assert hasattr(BrowserDriver, method_name)
        method = getattr(BrowserDriver, method_name)
        assert callable(method)


def test_browser_driver_cannot_be_instantiated():
    """测试BrowserDriver不能直接实例化"""
    with pytest.raises(TypeError):
        BrowserDriver()


class ConcreteBrowserDriver(BrowserDriver):
    """具体的浏览器驱动实现,用于测试"""

    def create_driver(self):
        return None

    def get_log(self, log_type):
        return []

    def get_element_by_xpath(self, xpath):
        return None

    def get_element_by_class_name(self, class_name):
        return None

    def get_cookies(self):
        return []

    def navigate(self, url):
        pass

    def wait_for_video(self, timeout=20):
        pass

    def close(self):
        pass


def test_concrete_browser_driver_can_be_instantiated():
    """测试具体的浏览器驱动可以实例化"""
    driver = ConcreteBrowserDriver()
    assert driver is not None
    assert isinstance(driver, BrowserDriver)


def test_concrete_browser_driver_implements_all_methods():
    """测试具体的浏览器驱动实现了所有方法"""
    driver = ConcreteBrowserDriver()

    assert callable(driver.create_driver)
    assert callable(driver.get_log)
    assert callable(driver.get_element_by_xpath)
    assert callable(driver.get_element_by_class_name)
    assert callable(driver.get_cookies)
    assert callable(driver.navigate)
    assert callable(driver.wait_for_video)
    assert callable(driver.close)


def test_concrete_browser_driver_create_driver():
    """测试create_driver方法"""
    driver = ConcreteBrowserDriver()
    result = driver.create_driver()
    assert result is None


def test_concrete_browser_driver_get_log():
    """测试get_log方法"""
    driver = ConcreteBrowserDriver()
    result = driver.get_log("performance")
    assert result == []


def test_concrete_browser_driver_get_element_by_xpath():
    """测试get_element_by_xpath方法"""
    driver = ConcreteBrowserDriver()
    result = driver.get_element_by_xpath("//div[@class='test']")
    assert result is None


def test_concrete_browser_driver_get_element_by_class_name():
    """测试get_element_by_class_name方法"""
    driver = ConcreteBrowserDriver()
    result = driver.get_element_by_class_name("test-class")
    assert result is None


def test_concrete_browser_driver_get_cookies():
    """测试get_cookies方法"""
    driver = ConcreteBrowserDriver()
    result = driver.get_cookies()
    assert result == []


def test_concrete_browser_driver_navigate():
    """测试navigate方法"""
    driver = ConcreteBrowserDriver()
    driver.navigate("https://test.com")


def test_concrete_browser_driver_wait_for_video():
    """测试wait_for_video方法"""
    driver = ConcreteBrowserDriver()
    driver.wait_for_video(timeout=10)


def test_concrete_browser_driver_wait_for_video_default_timeout():
    """测试wait_for_video方法使用默认超时"""
    driver = ConcreteBrowserDriver()
    driver.wait_for_video()


def test_concrete_browser_driver_close():
    """测试close方法"""
    driver = ConcreteBrowserDriver()
    driver.close()
