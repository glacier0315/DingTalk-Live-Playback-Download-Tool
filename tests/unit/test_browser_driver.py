"""
钉钉直播回放下载工具 - browser_driver 单元测试

本模块测试浏览器驱动抽象基类。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2026-01-29
修改历史：
    - 2026-01-29: 初始版本
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from abc import ABC

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.browser.browser_driver import BrowserDriver, COMMON_BROWSER_ARGS


class ConcreteBrowserDriver(BrowserDriver):
    """具体的浏览器驱动实现，用于测试抽象基类"""
    
    def create_driver(self):
        """创建浏览器实例"""
        mock_driver = MagicMock()
        mock_driver.find_element.return_value.text = "Test Element"
        return mock_driver
    
    def get_log(self, log_type: str):
        """获取浏览器日志"""
        return [{"message": "test log message"}]


def test_browser_driver_init():
    """测试浏览器驱动初始化"""
    driver = ConcreteBrowserDriver()
    assert driver.driver is None


def test_browser_driver_create_driver():
    """测试创建浏览器实例"""
    driver = ConcreteBrowserDriver()
    web_driver = driver.create_driver()
    
    assert web_driver is not None


def test_browser_driver_get_element_by_xpath():
    """测试通过XPath获取元素"""
    driver = ConcreteBrowserDriver()
    web_driver = driver.create_driver()
    
    element = driver.get_element_by_xpath("//div[@class='test']")
    
    assert element is not None
    assert element.text == "Test Element"
    web_driver.find_element.assert_called_once()


def test_browser_driver_get_element_by_xpath_no_driver():
    """测试通过XPath获取元素（无driver）"""
    driver = ConcreteBrowserDriver()
    
    element = driver.get_element_by_xpath("//div[@class='test']")
    
    assert element is None


def test_browser_driver_get_element_by_class_name():
    """测试通过类名获取元素"""
    driver = ConcreteBrowserDriver()
    web_driver = driver.create_driver()
    
    element = driver.get_element_by_class_name("test-class")
    
    assert element is not None
    assert element.text == "Test Element"
    web_driver.find_element.assert_called_once()


def test_browser_driver_get_element_by_class_name_no_driver():
    """测试通过类名获取元素（无driver）"""
    driver = ConcreteBrowserDriver()
    
    element = driver.get_element_by_class_name("test-class")
    
    assert element is None


def test_browser_driver_get_cookies():
    """测试获取Cookie"""
    driver = ConcreteBrowserDriver()
    web_driver = driver.create_driver()
    web_driver.get_cookies.return_value = [{"name": "test", "value": "value"}]
    
    cookies = driver.get_cookies()
    
    assert len(cookies) == 1
    assert cookies[0]["name"] == "test"
    web_driver.get_cookies.assert_called_once()


def test_browser_driver_get_cookies_no_driver():
    """测试获取Cookie（无driver）"""
    driver = ConcreteBrowserDriver()
    
    cookies = driver.get_cookies()
    
    assert cookies == []


def test_browser_driver_navigate():
    """测试导航到URL"""
    driver = ConcreteBrowserDriver()
    web_driver = driver.create_driver()
    
    driver.navigate("https://example.com")
    
    web_driver.get.assert_called_once_with("https://example.com")


def test_browser_driver_navigate_no_driver():
    """测试导航到URL（无driver）"""
    driver = ConcreteBrowserDriver()
    
    driver.navigate("https://example.com")
    
    assert driver.driver is None


def test_browser_driver_wait_for_video():
    """测试等待视频加载"""
    driver = ConcreteBrowserDriver()
    web_driver = driver.create_driver()
    web_driver.execute_script.return_value = False
    
    driver.wait_for_video(timeout=10)
    
    web_driver.execute_script.assert_called_once()


def test_browser_driver_wait_for_video_no_driver():
    """测试等待视频加载（无driver）"""
    driver = ConcreteBrowserDriver()
    
    driver.wait_for_video(timeout=10)
    
    assert driver.driver is None


def test_browser_driver_close():
    """测试关闭浏览器"""
    driver = ConcreteBrowserDriver()
    web_driver = driver.create_driver()
    
    driver.close()
    
    assert driver.driver is None
    web_driver.quit.assert_called_once()


def test_browser_driver_close_no_driver():
    """测试关闭浏览器（无driver）"""
    driver = ConcreteBrowserDriver()
    
    driver.close()
    
    assert driver.driver is None


def test_browser_driver_is_driver_initialized():
    """测试检查浏览器驱动是否已初始化"""
    driver = ConcreteBrowserDriver()
    
    assert driver.is_driver_initialized() is False
    
    driver.create_driver()
    
    assert driver.is_driver_initialized() is True


def test_browser_driver_get_driver():
    """测试获取浏览器驱动实例"""
    driver = ConcreteBrowserDriver()
    
    assert driver.get_driver() is None
    
    web_driver = driver.create_driver()
    
    assert driver.get_driver() == web_driver


def test_browser_driver_extract_m3u8_links_from_logs():
    """测试从浏览器日志中提取m3u8链接"""
    driver = ConcreteBrowserDriver()
    
    logs = [
        {"message": '{"url":"https://test.com/video1.m3u8?liveUuid=abc"}'},
        {"message": '{"url":"https://test.com/video2.m3u8?liveUuid=abc"}'},
        {"message": "other message"},
        {"message": '{"url":"https://test.com/video1.m3u8?liveUuid=def"}'},
    ]
    
    links = driver.extract_m3u8_links_from_logs(logs, "abc")
    
    assert len(links) == 2
    assert "video1.m3u8" in links[0]
    assert "video2.m3u8" in links[1]


def test_browser_driver_extract_m3u8_links_from_logs_filter_duplicates():
    """测试从浏览器日志中提取m3u8链接（过滤重复）"""
    driver = ConcreteBrowserDriver()
    
    logs = [
        {"message": '{"url":"https://test.com/video1.m3u8?liveUuid=abc"}'},
        {"message": '{"url":"https://test.com/video1.m3u8?liveUuid=abc"}'},
    ]
    
    links = driver.extract_m3u8_links_from_logs(logs, "abc")
    
    assert len(links) == 1
    assert "video1.m3u8" in links[0]


def test_browser_driver_extract_m3u8_links_from_logs_filter_different_uuid():
    """测试从浏览器日志中提取m3u8链接（过滤不同UUID）"""
    driver = ConcreteBrowserDriver()
    
    logs = [
        {"message": '{"url":"https://test.com/video1.m3u8?liveUuid=abc"}'},
        {"message": '{"url":"https://test.com/video2.m3u8?liveUuid=def"}'},
    ]
    
    links = driver.extract_m3u8_links_from_logs(logs, "abc")
    
    assert len(links) == 1
    assert "video1.m3u8" in links[0]


def test_browser_driver_extract_m3u8_links_from_logs_no_valid_links():
    """测试从浏览器日志中提取m3u8链接（无有效链接）"""
    driver = ConcreteBrowserDriver()
    
    logs = [
        {"message": "other message"},
        {"message": "another message"},
    ]
    
    links = driver.extract_m3u8_links_from_logs(logs, "abc")
    
    assert len(links) == 0


def test_common_browser_args():
    """测试通用浏览器参数"""
    assert isinstance(COMMON_BROWSER_ARGS, list)
    assert len(COMMON_BROWSER_ARGS) > 0
    assert "--disable-usb-device-event-log" in COMMON_BROWSER_ARGS
