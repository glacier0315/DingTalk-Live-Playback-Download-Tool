"""
钉钉直播回放下载工具 - 浏览器驱动抽象基类

本模块定义浏览器驱动的抽象接口。

作者：项目团队
依赖：selenium, abc
创建日期：2026-01-21
修改历史：
    - 2026-01-21: 初始版本
"""

from abc import ABC, abstractmethod
from typing import List
from selenium.webdriver.remote.webdriver import WebDriver


class BrowserDriver(ABC):
    """
    浏览器驱动抽象基类。

    该类定义了所有浏览器驱动必须实现的接口。
    """

    @abstractmethod
    def create_driver(self) -> WebDriver:
        """
        创建浏览器实例。

        Returns:
            WebDriver: 浏览器实例

        Raises:
            Exception: 创建失败时
        """
        pass

    @abstractmethod
    def get_log(self, log_type: str) -> List[dict]:
        """
        获取浏览器日志。

        Args:
            log_type: 日志类型(如"performance")

        Returns:
            List[dict]: 日志列表

        Raises:
            Exception: 获取失败时
        """
        pass

    @abstractmethod
    def get_element_by_xpath(self, xpath: str):
        """
        通过XPath获取元素。

        Args:
            xpath: XPath表达式

        Returns:
            WebElement: 元素对象

        Raises:
            Exception: 获取失败时
        """
        pass

    @abstractmethod
    def get_element_by_class_name(self, class_name: str):
        """
        通过类名获取元素。

        Args:
            class_name: 类名

        Returns:
            WebElement: 元素对象

        Raises:
            Exception: 获取失败时
        """
        pass

    @abstractmethod
    def get_user_agent(self) -> str:
        """
        获取User-Agent。

        Returns:
            str: User-Agent字符串

        Raises:
            Exception: 获取失败时
        """
        pass

    @abstractmethod
    def get_referer(self) -> str:
        """
        获取Referer。

        Returns:
            str: Referer字符串

        Raises:
            Exception: 获取失败时
        """
        pass

    @abstractmethod
    def get_cookies(self) -> List[dict]:
        """
        获取Cookie。

        Returns:
            List[dict]: Cookie列表

        Raises:
            Exception: 获取失败时
        """
        pass

    @abstractmethod
    def navigate(self, url: str) -> None:
        """
        导航到指定URL。

        Args:
            url: 目标URL

        Raises:
            Exception: 导航失败时
        """
        pass

    @abstractmethod
    def wait_for_video(self, timeout: int = 20) -> None:
        """
        等待视频加载。

        Args:
            timeout: 超时时间(秒),默认为20

        Raises:
            Exception: 等待超时时
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """
        关闭浏览器,释放资源。

        Raises:
            Exception: 关闭失败时
        """
        pass
