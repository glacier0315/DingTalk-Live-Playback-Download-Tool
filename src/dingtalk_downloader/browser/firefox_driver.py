"""
钉钉直播回放下载工具 - Firefox 浏览器驱动模块

本模块提供 Firefox 浏览器驱动类。

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
import re
from typing import List
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from .browser_driver import BrowserDriver

logger = logging.getLogger(__name__)


class FirefoxDriver(BrowserDriver):
    """
    Firefox 浏览器驱动类。

    该类封装了 Firefox 浏览器的创建、配置和操作逻辑。
    继承 BrowserDriver 父类，复用通用方法实现，
    仅需实现浏览器特定的创建和日志获取逻辑。

    Attributes:
        driver: Firefox 浏览器实例
    """

    def __init__(self):
        """
        初始化 Firefox 浏览器驱动。

        通过 super().__init__() 调用父类初始化方法，
        继承 BrowserDriver 的通用属性和行为。
        """
        super().__init__()
        logger.debug("Firefox 浏览器驱动初始化")

    def create_driver(self) -> webdriver.Firefox:
        """
        创建 Firefox 浏览器实例。

        配置 Firefox 浏览器选项，包括禁用 USB 设备事件日志、忽略证书错误、禁用日志等。

        Returns:
            Firefox 浏览器实例
        """
        logger.info("开始创建 Firefox 浏览器驱动")

        firefox_options = FirefoxOptions()
        self.apply_common_options(firefox_options)
        firefox_options.set_capability(
            "moz:firefoxOptions",
            {
                "log": {
                    "level": "ALL",
                    "browser": "ALL",
                }
            },
        )

        self.driver = webdriver.Firefox(options=firefox_options)
        logger.info("Firefox 浏览器驱动创建成功")
        return self.driver

    def get_log(self, log_type: str) -> List[dict]:
        """
        获取浏览器日志。

        使用 JavaScript 获取 Firefox 性能日志。

        Args:
            log_type: 日志类型（如 "performance"）

        Returns:
            日志列表
        """
        if self.driver:
            logs = self.driver.execute_script(
                """
                var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {};
                var network = performance.getEntries() || {};
                return network;
            """
            )
            return logs
        return []

    def extract_m3u8_links_from_logs(self, logs: List[dict], live_uuid: str) -> List[str]:
        """
        从浏览器日志中提取m3u8链接。

        重写父类方法，处理Firefox特定的日志格式。

        Args:
            logs: 浏览器日志列表
            live_uuid: 直播UUID，用于过滤m3u8链接

        Returns:
            List[str]: m3u8链接列表
        """
        m3u8_links = []
        pattern = r'https://[^,\'"]+\.m3u8\?[^\'"]+'

        for log in logs:
            try:
                log_message = str(log)
                found_links = re.findall(pattern, log_message)

                if found_links:
                    cleaned_link = re.sub(r'[\]\s\\\'"]+$', "", found_links[0])
                    if live_uuid not in cleaned_link:
                        continue
                    if cleaned_link in m3u8_links:
                        continue
                    m3u8_links.append(cleaned_link)
            except Exception as e:
                logger.error(f"提取m3u8链接时发生错误: {e}", exc_info=True)

        return m3u8_links
