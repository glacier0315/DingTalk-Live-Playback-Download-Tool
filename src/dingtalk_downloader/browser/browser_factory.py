"""
钉钉直播回放下载工具 - 浏览器工厂模块

本模块提供浏览器工厂类，统一浏览器创建逻辑。

作者：项目团队
依赖：selenium
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2025-01-15: 添加日志记录
"""

import logging
from typing import Union
from .edge_driver import EdgeDriver
from .chrome_driver import ChromeDriver
from .firefox_driver import FirefoxDriver
from ..config.constants import BROWSER_TYPE_EDGE, BROWSER_TYPE_CHROME, BROWSER_TYPE_FIREFOX

logger = logging.getLogger(__name__)


class BrowserFactory:
    """
    浏览器工厂类，负责创建不同类型的浏览器实例。

    该类封装了 Edge、Chrome、Firefox 三种浏览器的创建逻辑，
    提供统一的接口供上层模块使用。
    """

    @staticmethod
    def create_browser(browser_type: str) -> Union[EdgeDriver, ChromeDriver, FirefoxDriver]:
        """
        创建浏览器实例。

        根据浏览器类型创建对应的浏览器实例。

        Args:
            browser_type: 浏览器类型（edge/chrome/firefox）

        Returns:
            浏览器实例

        Raises:
            ValueError: 浏览器类型不支持时
        """
        logger.debug(f"创建浏览器实例 - 浏览器类型: {browser_type}")

        if browser_type == BROWSER_TYPE_EDGE:
            logger.debug("创建 Edge 浏览器实例")
            return EdgeDriver()
        elif browser_type == BROWSER_TYPE_CHROME:
            logger.debug("创建 Chrome 浏览器实例")
            return ChromeDriver()
        elif browser_type == BROWSER_TYPE_FIREFOX:
            logger.debug("创建 Firefox 浏览器实例")
            return FirefoxDriver()
        else:
            logger.error(f"不支持的浏览器类型: {browser_type}")
            raise ValueError(f"不支持的浏览器类型: {browser_type}")
