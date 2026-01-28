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
    - 2026-01-24: 重构使用super()调用父类，消除代码冗余
"""

import logging
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from .browser_driver import BrowserDriver

logger = logging.getLogger(__name__)


class ChromeDriver(BrowserDriver):
    """
    Chrome 浏览器驱动类。

    该类封装了 Chrome 浏览器的创建、配置和操作逻辑。
    继承 BrowserDriver 父类，复用通用方法实现，
    仅需实现浏览器特定的创建和日志获取逻辑。

    Attributes:
        driver: Chrome 浏览器实例
    """

    def __init__(self):
        """
        初始化 Chrome 浏览器驱动。

        通过 super().__init__() 调用父类初始化方法，
        继承 BrowserDriver 的通用属性和行为。
        """
        super().__init__()
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
        self.apply_common_options(chrome_options)
        chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

        self.driver = webdriver.Chrome(options=chrome_options)
        logger.info("Chrome 浏览器驱动创建成功")
        return self.driver

    def get_log(self, log_type: str) -> List[dict]:
        """
        获取浏览器日志。

        使用 Chrome 特定的日志获取方式。

        Args:
            log_type: 日志类型（如 "performance"）

        Returns:
            日志列表
        """
        if self.driver:
            return self.driver.get_log(log_type)
        return []
