"""
钉钉直播回放下载工具 - Edge 浏览器驱动模块

本模块提供 Edge 浏览器驱动类。

作者：项目团队
依赖：selenium
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
"""

from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List, Optional


class EdgeDriver:
    """
    Edge 浏览器驱动类。

    该类封装了 Edge 浏览器的创建、配置和操作逻辑。

    Attributes:
        driver: Edge 浏览器实例
    """

    def __init__(self):
        """
        初始化 Edge 浏览器驱动。
        """
        self.driver: Optional[webdriver.Edge] = None

    def create_driver(self) -> webdriver.Edge:
        """
        创建 Edge 浏览器实例。

        配置 Edge 浏览器选项，包括禁用 USB 设备事件日志、忽略证书错误、禁用日志等。

        Returns:
            Edge 浏览器实例
        """
        edge_options = EdgeOptions()
        edge_options.add_argument('--disable-usb-device-event-log')
        edge_options.add_argument('--ignore-certificate-errors')
        edge_options.add_argument('--disable-logging')
        edge_options.add_argument('--disable_ssl_verification')
        edge_options.add_argument('--log-level=3')
        edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        edge_options.set_capability("ms:loggingPrefs", {"performance": "ALL"})

        self.driver = webdriver.Edge(options=edge_options)
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

    def get_user_agent(self) -> str:
        """
        获取 User-Agent。

        通过 JavaScript 获取 User-Agent。

        Returns:
            User-Agent 字符串
        """
        if self.driver:
            return self.driver.execute_script("return navigator.userAgent")
        return ""

    def get_referer(self) -> str:
        """
        获取 Referer。

        通过 JavaScript 获取 Referer。

        Returns:
            Referer 字符串
        """
        if self.driver:
            referer = self.driver.execute_script("return document.referrer")
            return referer if referer else 'https://n.dingtalk.com/'
        return 'https://n.dingtalk.com/'

    def get_cookies(self) -> List[dict]:
        """
        获取 Cookie。

        获取浏览器的所有 Cookie。

        Returns:
            Cookie 列表
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
                lambda driver: driver.execute_script("return isNaN(document.querySelector('video')?.duration)") == False
            )

    def close(self) -> None:
        """
        关闭浏览器，释放资源。
        """
        if self.driver:
            self.driver.quit()
            self.driver = None
