"""
钉钉直播回放下载工具 - Cookie 处理模块

本模块负责获取和管理 Cookie。

作者：项目团队
依赖：selenium
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
"""

import sys
from typing import Dict, Tuple, Union
from ..browser.browser_factory import BrowserFactory
from ..browser.edge_driver import EdgeDriver
from ..browser.chrome_driver import ChromeDriver
from ..browser.firefox_driver import FirefoxDriver
from ..config.constants import BROWSER_TYPE_EDGE, BROWSER_TYPE_CHROME, BROWSER_TYPE_FIREFOX, DEFAULT_HEADERS


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

    def get_cookie(self, url: str) -> Tuple[Union[EdgeDriver, ChromeDriver, FirefoxDriver], Dict[str, str], Dict[str, str], str]:
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
            Exception: 获取失败时
        """
        try:
            self.browser = BrowserFactory.create_browser(self.browser_type)
            self.browser.create_driver()
            self.browser.navigate(url)
            input("请在浏览器中登录钉钉账户后，按Enter键继续...")

            user_agent = self.browser.get_user_agent()
            referer = self.browser.get_referer()

            headers = {
                'User-Agent': user_agent,
                'Referer': referer,
                'Accept': 'application/vnd.apple.mpegurl, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }

            live_name = self._get_live_name()
            print(f"直播名称: {live_name}")

            cookies = self.browser.get_cookies()
            cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}

            return self.browser, cookie_dict, headers, live_name

        except Exception as e:
            print(f"获取Cookie时发生错误: {e}")
            if self.browser:
                self.browser.close()
            sys.exit(1)

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
            Exception: 获取失败时
        """
        try:
            if self.browser is None:
                return self.get_cookie(url)

            self.browser.navigate(url)
            try:
                self.browser.wait_for_video(20)
            except Exception as e:
                input("未能确定页面是否成功加载。请在页面加载后，按Enter键继续...")

            user_agent = self.browser.get_user_agent()
            referer = self.browser.get_referer()

            headers = {
                'User-Agent': user_agent,
                'Referer': referer,
                'Accept': 'application/vnd.apple.mpegurl, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }

            live_name = self._get_live_name()
            print(f"直播名称: {live_name}")

            cookies = self.browser.get_cookies()
            cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}

            return cookie_dict, headers, live_name

        except Exception as e:
            print(f"重复获取Cookie时发生错误: {e}")
            if self.browser:
                self.browser.close()
            sys.exit(1)

    def _get_live_name(self) -> str:
        """
        获取直播视频名称。

        尝试通过 XPath 和 CSS 选择器获取直播视频名称。

        Returns:
            直播视频名称
        """
        try:
            live_name = self.browser.get_element_by_xpath('//*[@id="live-room"]/div[1]/div[1]/h3').text
            return live_name
        except Exception as e:
            print(f"XPath 获取失败: {e}")
            try:
                live_name = self.browser.get_element_by_class_name("vwi5-oG8").text
                return live_name
            except Exception as e:
                print(f"CSS Selector 获取失败: {e}")
                return "直播视频名称不可获取"

    def close(self) -> None:
        """
        关闭浏览器，释放资源。
        """
        if self.browser:
            self.browser.close()
            self.browser = None
