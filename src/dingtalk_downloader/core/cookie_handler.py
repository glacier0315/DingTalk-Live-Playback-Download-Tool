"""
钉钉直播回放下载工具 - Cookie 处理模块

本模块负责获取和管理 Cookie。

作者：项目团队
依赖：selenium
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2025-01-15: 添加日志记录
    - 2026-01-21: 重构-提取请求头构建逻辑,移除sys.exit调用
    - 2026-01-22: 重构-使用配置中的直播名称选择器
"""

import logging
from typing import Tuple
from ..browser.browser_factory import BrowserFactory
from ..config.constants import LIVE_NAME_SELECTORS, BROWSER_WAIT_TIMEOUT
from ..config.header_manager import HeaderManager
from ..utils.models import CookieData, HeadersData
from .exceptions import CookieError

logger = logging.getLogger(__name__)


class CookieHandler:
    """
    Cookie 处理类，负责获取和管理 Cookie。
    该类封装了 Cookie 获取、请求头获取、直播名称获取的逻辑。
    支持上下文管理器，确保资源正确释放。

    Attributes:
        browser: 浏览器实例
        browser_type: 浏览器类型
    """

    def __init__(self, browser_type: str):
        """
        初始化 Cookie 处理器。

        Args:
            browser_type: 浏览器类型（edge/chrome/firefox）
        """
        self.browser_type = browser_type
        self.browser = None
        self.header_manager = HeaderManager()
        logger.debug(f"Cookie 处理器初始化 - 浏览器类型: {browser_type}")

    def __enter__(self):
        """
        上下文管理器入口。

        Returns:
            self: CookieHandler实例
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器出口，确保资源正确释放。

        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常追踪
        """
        self.close()
        return False


    def initialize_browser(self) -> bool:
        """
        初始化浏览器实例。

        Returns:
            bool: 是否为新实例
        """
        is_new = False
        if self.browser is None:
            self.browser = BrowserFactory.create_browser(self.browser_type)
            logger.debug("浏览器实例创建成功")

            self.browser.create_driver()
            logger.debug("浏览器驱动创建成功")
            is_new = True
        return is_new

    def _collect_browser_data(
        self,
    ) -> Tuple[CookieData, HeadersData, str]:
        """
        从浏览器收集数据（请求头、Cookie、直播名称）。
        该方法提取了重复的数据收集逻辑，包括：
        - 获取直播名称
        - 获取Cookie字典

        Returns:
            tuple: 包含三个元素的元组
                - cookie_data: Cookie数据值对象
                - headers_data: 请求头数据值对象
                - live_name: 直播视频名称
        """
        headers_dict = self.header_manager.get_headers()
        headers_data = HeadersData(headers=headers_dict)
        logger.debug(f"获取到 {len(headers_data)} 个 headers")

        live_name = self._get_live_name()
        logger.debug(f"直播名称: {live_name}")

        cookies = self.browser.get_cookies()
        cookie_dict = {cookie["name"]: cookie["value"] for cookie in cookies}
        cookie_data = CookieData(cookies=cookie_dict)
        logger.debug(f"获取到 {len(cookie_data)} 个 Cookie")

        return cookie_data, headers_data, live_name

    def get_cookie(self, url: str) -> Tuple[CookieData, HeadersData, str]:
        """
        获取 Cookie 和请求头信息。

        通过 Selenium 自动化浏览器访问指定 URL，获取登录后的 Cookie 和请求头信息。

        Args:
            url: 钉钉直播回放分享链接

        Returns:
            tuple: 包含四个元素的元组
                - cookie_data: Cookie 数据值对象
                - headers_data: 请求头数据值对象
                - live_name: 直播视频名称

        Raises:
            CookieError: 获取失败时
        """
        logger.info(f"开始获取 Cookie, headers, live_name")

        try:
            is_new = self.initialize_browser()

            self.browser.navigate(url)
            logger.debug(f"导航到指定 URL: {url}")

            if is_new:
                input("请在浏览器中登录钉钉账户后，按Enter键继续...")
            else:
                try:
                    self.browser.wait_for_video(BROWSER_WAIT_TIMEOUT)
                    logger.debug("视频加载完成")
                except Exception as e:
                    logger.warning(f"等待视频加载时发生错误: {e}")
                    input("未能确定页面是否成功加载。请在页面加载后，按Enter键继续...")

            return self._collect_browser_data()
        except Exception as e:
            self.close()
            logger.error(f"获取Cookie时发生错误: {e}", exc_info=True)
            raise CookieError(f"获取Cookie失败: {e}") from e

    def _get_live_name(self) -> str:
        """
        获取直播视频名称。

        尝试通过配置中的多个选择器获取直播视频名称。

        Returns:
            直播视频名称
        """
        for selector_type, selector_value in LIVE_NAME_SELECTORS:
            try:
                if selector_type == "xpath":
                    live_name = self.browser.get_element_by_xpath(selector_value).text
                elif selector_type == "css":
                    live_name = self.browser.get_element_by_class_name(selector_value).text
                else:
                    continue

                logger.debug(f"通过 {selector_type} 获取直播名称: {live_name}")
                return live_name
            except Exception as e:
                logger.debug(f"{selector_type} 获取失败: {e}")
                continue

        logger.warning("所有选择器均获取失败")
        return "直播视频名称不可获取"

    def close(self) -> None:
        """
        关闭浏览器，释放资源。
        """
        logger.debug("开始释放 Cookie 处理器资源")
        if self.browser:
            self.browser.close()
            self.browser = None
        logger.debug("Cookie 处理器资源释放完成")
