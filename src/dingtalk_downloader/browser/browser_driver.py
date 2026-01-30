"""
钉钉直播回放下载工具 - 浏览器驱动抽象基类

本模块定义浏览器驱动的抽象接口和通用实现。

作者：项目团队
依赖：selenium, abc
创建日期：2026-01-21
修改历史：
    - 2026-01-21: 初始版本
    - 2026-01-24: 重构实现通用方法，消除子类代码冗余
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Union
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import logging
from ..config.constants import BROWSER_WAIT_TIMEOUT

logger = logging.getLogger(__name__)

COMMON_BROWSER_ARGS = [
    "--disable-usb-device-event-log",
    "--ignore-certificate-errors",
    "--disable-logging",
    "--log-level=3",
]


class BrowserDriver(ABC):
    """
    浏览器驱动抽象基类。

    该类定义了所有浏览器驱动必须实现的接口，并提供通用方法的默认实现。
    子类只需实现浏览器特定的方法（create_driver、get_log），
    其他通用方法通过父类统一实现，消除代码冗余。

    Attributes:
        driver: 浏览器驱动实例，初始化为None

    Example:
        class ChromeDriver(BrowserDriver):
            def create_driver(self) -> WebDriver:
                # 浏览器特定实现
                pass

            def get_log(self, log_type: str) -> List[dict]:
                # 浏览器特定实现
                pass
    """

    def __init__(self):
        """
        初始化浏览器驱动。

        子类通过super().__init__()调用父类初始化方法。
        """
        self.driver: Optional[WebDriver] = None
        logger.debug("浏览器驱动基类初始化")

    @abstractmethod
    def create_driver(self) -> WebDriver:
        """
        创建浏览器实例。

        子类必须实现此方法以提供浏览器特定的创建逻辑。

        Returns:
            WebDriver: 浏览器实例

        Raises:
            Exception: 创建失败时
        """
        pass

    @staticmethod
    def apply_common_options(options) -> None:
        """
        应用通用浏览器配置选项。

        Args:
            options: 浏览器选项对象
        """
        for arg in COMMON_BROWSER_ARGS:
            options.add_argument(arg)

    @abstractmethod
    def get_log(self, log_type: str) -> List[dict]:
        """
        获取浏览器日志。

        子类必须实现此方法，因为不同浏览器的日志获取方式可能不同。

        Args:
            log_type: 日志类型(如"performance")

        Returns:
            List[dict]: 日志列表

        Raises:
            Exception: 获取失败时
        """
        pass

    def get_element_by_xpath(self, xpath: str) -> Optional[WebDriver]:
        """
        通过XPath获取元素。

        通用方法实现，子类可通过super()调用后扩展。

        Args:
            xpath: XPath表达式

        Returns:
            WebDriver: 元素对象，如果driver未初始化则返回None
        """
        if self.driver:
            return self.driver.find_element(By.XPATH, xpath)
        return None

    def get_element_by_class_name(self, class_name: str) -> Optional[WebDriver]:
        """
        通过类名获取元素。

        通用方法实现，子类可通过super()调用后扩展。

        Args:
            class_name: 类名

        Returns:
            WebDriver: 元素对象，如果driver未初始化则返回None
        """
        if self.driver:
            return self.driver.find_element(By.CLASS_NAME, class_name)
        return None

    def get_cookies(self) -> List[dict]:
        """
        获取Cookie。

        通用方法实现，子类可通过super()调用后扩展。

        Returns:
            List[dict]: Cookie列表，如果driver未初始化则返回空列表
        """
        if self.driver:
            return self.driver.get_cookies()
        return []

    def navigate(self, url: str) -> None:
        """
        导航到指定URL。

        通用方法实现，子类可通过super()调用后扩展。

        Args:
            url: 目标URL
        """
        if self.driver:
            self.driver.get(url)

    def wait_for_video(self, timeout: int = BROWSER_WAIT_TIMEOUT) -> None:
        """
        等待视频加载。

        通用方法实现，子类可通过super()调用后扩展。
        等待视频元素的duration属性变为有效值。

        Args:
            timeout: 超时时间(秒),默认为20

        Raises:
            TimeoutException: 等待超时时
        """
        if self.driver:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: not driver.execute_script(
                    "return isNaN(document.querySelector('video')?.duration)"
                )
            )

    def close(self) -> None:
        """
        关闭浏览器,释放资源。

        通用方法实现，子类可通过super()调用后扩展。
        先调用父类逻辑关闭driver，再执行子类特定的清理逻辑。

        Example:
            def close(self) -> None:
                super().close()
                # 子类特定清理逻辑
                self.driver_service = None
        """
        logger.debug("开始关闭浏览器")
        if self.driver:
            self.driver.quit()
            self.driver = None
        logger.debug("浏览器关闭完成")

    def is_driver_initialized(self) -> bool:
        """
        检查浏览器驱动是否已初始化。

        Returns:
            bool: 如果driver已初始化且不为None则返回True
        """
        return self.driver is not None

    def get_driver(self) -> Optional[WebDriver]:
        """
        获取浏览器驱动实例。

        Returns:
            WebDriver: 浏览器驱动实例，如果未初始化则返回None
        """
        return self.driver

    def extract_m3u8_links_from_logs(self, logs: List[dict], live_uuid: str) -> List[str]:
        """
        从浏览器日志中提取m3u8链接。

        提供默认实现，处理Edge和Chrome的日志格式。
        子类可以重写此方法以处理特定浏览器的日志格式。

        Args:
            logs: 浏览器日志列表

        Returns:
            List[str]: m3u8链接列表
        """
        m3u8_links = []
        for log in logs:
            try:
                if "message" in log:
                    log_message = log["message"]
                else:
                    log_message = str(log)

                if ".m3u8" in log_message:
                    start_idx = log_message.find('url":"') + len('url":"')
                    end_idx = log_message.find('"', start_idx)
                    m3u8_url = log_message[start_idx:end_idx]
                    # 过滤掉非当前直播的m3u8链接
                    if live_uuid not in m3u8_url:
                        continue

                    # 过滤掉重复的m3u8链接
                    if m3u8_url in m3u8_links:
                        continue

                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"从日志中提取到消息: {log_message}")
                        logger.debug(f"从日志中提取到 m3u8 链接: {m3u8_url}")
                    m3u8_links.append(m3u8_url)
            except Exception as e:
                logger.error(f"提取m3u8链接时发生错误: {e}", exc_info=True)
        return m3u8_links
