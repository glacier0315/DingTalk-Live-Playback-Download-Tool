"""
钉钉直播回放下载工具 - Chrome 浏览器驱动模块

本模块提供 Chrome 浏览器驱动类。

作者：项目团队
依赖：selenium
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2025-01-15: 添加日志记录
    - 2026-01-21: 重构为继承BrowserDriver抽象基类
"""

import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from typing import List, Optional
from .browser_driver import BrowserDriver

logger = logging.getLogger(__name__)


class ChromeDriver(BrowserDriver):
    """
    Chrome 浏览器驱动类。

    该类封装了 Chrome 浏览器的创建、配置和操作逻辑。

    Attributes:
        driver: Chrome 浏览器实例
    """

    def __init__(self):
        """
        初始化 Chrome 浏览器驱动。
        """
        self.driver: Optional[webdriver.Chrome] = None
        logger.debug("Chrome 浏览器驱动初始化")

    def create_driver(self) -> webdriver.Chrome:
        """
        创建 Chrome 浏览器实例。

        配置 Chrome 浏览器选项，包括禁用 USB 设备事件日志、忽略证书错误、禁用日志等。

        Returns:
            Chrome 浏览器实例
        """
        logger.info("开始创建 Chrome 浏览器驱动")

        chrome_options = ChromeOptions()
        chrome_options.add_argument("--disable-usb-device-event-log")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-logging")
        chrome_options.add_argument("--log-level=3")
        chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        self.driver = webdriver.Chrome(options=chrome_options)
        logger.info("Chrome 浏览器驱动创建成功")
        return self.driver

    def get_log(self, log_type: str) -> List[dict]:
        """
        获取浏览器日志。

        获取指定类型的浏览器日志。

        Args:
            log_type: 日志类型（如 "performance"）

        Returns:
            日志列表
        """
        if self.driver:
            return self.driver.get_log(log_type)
        return []

    def get_element_by_xpath(self, xpath: str):
        """
        通过 XPath 获取元素。

        Args:
            xpath: XPath 表达式

        Returns:
            元素对象
        """
        if self.driver:
            return self.driver.find_element(By.XPATH, xpath)
        return None

    def get_element_by_class_name(self, class_name: str):
        """
        通过类名获取元素。

        Args:
            class_name: 类名

        Returns:
            元素对象
        """
        if self.driver:
            return self.driver.find_element(By.CLASS_NAME, class_name)
        return None

    def get_cookies(self) -> List[dict]:
        """
        获取Cookie。

        获取浏览器的所有Cookie。

        Returns:
            Cookie列表
        """
        if self.driver:
            return self.driver.get_cookies()
        return []

    def navigate(self, url: str) -> None:
        """
        导航到指定 URL。

        Args:
            url: 目标 URL
        """
        if self.driver:
            self.driver.get(url)

    def wait_for_video(self, timeout: int = 20) -> None:
        """
        等待视频加载。

        等待视频元素加载完成。

        Args:
            timeout: 超时时间（秒），默认为 20
        """
        if self.driver:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: not driver.execute_script(
                    "return isNaN(document.querySelector('video')?.duration)"
                )
            )

    def close(self) -> None:
        """
        关闭浏览器，释放资源。
        """
        logger.info("开始关闭 Chrome 浏览器")
        if self.driver:
            self.driver.quit()
            self.driver = None
        logger.info("Chrome 浏览器关闭完成")
