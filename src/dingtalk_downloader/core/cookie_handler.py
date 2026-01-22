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
from typing import Dict, Tuple, Any
from ..browser.browser_factory import BrowserFactory
from ..config.constants import LIVE_NAME_SELECTORS
from ..config.header_manager import HeaderManager

logger = logging.getLogger(__name__)


class CookieError(Exception):
    """Cookie处理异常"""

    pass


class CookieHandler:
    """
    Cookie 处理类，负责获取和管理 Cookie。

    该类封装了 Cookie 获取、请求头获取、直播名称获取的逻辑。

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

    def _build_headers(self, user_agent: str, referer: str) -> Dict[str, str]:
        """
        构建请求头。

        Args:
            user_agent: User-Agent字符串
            referer: Referer字符串

        Returns:
            请求头字典
        """
        headers = self.header_manager.get_headers()
        
        # 使用浏览器提供的User-Agent和Referer覆盖配置中的值
        headers["User-Agent"] = user_agent
        headers["Referer"] = referer
        
        return headers

    def _collect_browser_data(self) -> Tuple[Dict[str, str], Dict[str, str], str]:
        """
        从浏览器收集数据（请求头、Cookie、直播名称）。

        该方法提取了重复的数据收集逻辑，包括：
        - 获取User-Agent和Referer
        - 构建请求头
        - 获取直播名称
        - 获取Cookie字典

        Returns:
            tuple: 包含三个元素的元组
                - cookie_dict: Cookie字典，格式为{cookie_name: cookie_value}
                - headers: 请求头字典，包含User-Agent、Referer等
                - live_name: 直播视频名称
        """
        user_agent = self.browser.get_user_agent()
        referer = self.browser.get_referer()
        logger.debug(f"User-Agent: {user_agent}")
        logger.debug(f"Referer: {referer}")

        headers = self._build_headers(user_agent, referer)
        logger.info("请求头构建完成")

        live_name = self._get_live_name()
        logger.info(f"直播名称: {live_name}")

        cookies = self.browser.get_cookies()
        cookie_dict = {cookie["name"]: cookie["value"] for cookie in cookies}
        logger.info(f"获取到 {len(cookie_dict)} 个 Cookie")

        return cookie_dict, headers, live_name

    def get_cookie(self, url: str) -> Tuple[Any, Dict[str, str], Dict[str, str], str]:
        """
        获取 Cookie 和请求头信息。

        通过 Selenium 自动化浏览器访问指定 URL，获取登录后的 Cookie 和请求头信息。

        Args:
            url: 钉钉直播回放分享链接

        Returns:
            tuple: 包含四个元素的元组
                - browser: 浏览器实例
                - cookie_dict: Cookie 字典，格式为 {cookie_name: cookie_value}
                - headers: 请求头字典，包含 User-Agent、Referer 等
                - live_name: 直播视频名称

        Raises:
            CookieError: 获取失败时
        """
        logger.info(f"开始获取 Cookie - URL: {url}")

        try:
            self.browser = BrowserFactory.create_browser(self.browser_type)
            logger.info("浏览器实例创建成功")

            self.browser.create_driver()
            logger.info("浏览器驱动创建成功")

            self.browser.navigate(url)
            logger.info("导航到指定 URL")

            input("请在浏览器中登录钉钉账户后，按Enter键继续...")

            cookie_dict, headers, live_name = self._collect_browser_data()

            return self.browser, cookie_dict, headers, live_name

        except Exception as e:
            logger.error(f"获取Cookie时发生错误: {e}", exc_info=True)
            if self.browser:
                self.browser.close()
            raise CookieError(f"获取Cookie失败: {e}") from e

    def repeat_get_cookie(self, url: str) -> Tuple[Dict[str, str], Dict[str, str], str]:
        """
        重复获取 Cookie 和请求头信息。

        使用已有的浏览器实例重复获取 Cookie 和请求头信息。

        Args:
            url: 钉钉直播回放分享链接

        Returns:
            tuple: 包含三个元素的元组
                - cookie_dict: Cookie 字典，格式为 {cookie_name: cookie_value}
                - headers: 请求头字典，包含 User-Agent、Referer 等
                - live_name: 直播视频名称

        Raises:
            CookieError: 获取失败时
        """
        logger.info("重复获取 Cookie")

        try:
            if self.browser is None:
                logger.warning("浏览器实例不存在，调用 get_cookie")
                browser, cookie_dict, headers, live_name = self.get_cookie(url)
                return cookie_dict, headers, live_name

            self.browser.navigate(url)
            logger.info("导航到指定 URL")

            try:
                self.browser.wait_for_video(20)
                logger.info("视频加载完成")
            except Exception as e:
                logger.warning(f"等待视频加载时发生错误: {e}")
                input("未能确定页面是否成功加载。请在页面加载后，按Enter键继续...")

            cookie_dict, headers, live_name = self._collect_browser_data()

            return cookie_dict, headers, live_name

        except Exception as e:
            logger.error(f"重复获取Cookie时发生错误: {e}", exc_info=True)
            if self.browser:
                self.browser.close()
            raise CookieError(f"重复获取Cookie失败: {e}") from e

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
        logger.info("开始释放 Cookie 处理器资源")
        if self.browser:
            self.browser.close()
            self.browser = None
        logger.info("Cookie 处理器资源释放完成")
