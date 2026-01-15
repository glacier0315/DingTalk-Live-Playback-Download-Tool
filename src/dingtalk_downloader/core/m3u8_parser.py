"""
钉钉直播回放下载工具 - m3u8 解析模块

本模块负责从浏览器网络日志中提取 m3u8 链接和基础 URL。

作者：项目团队
依赖：selenium, re, urllib.parse
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2025-01-15: 添加日志记录
"""

import re
import sys
import logging
from urllib.parse import urlparse, parse_qs
from typing import List, Optional, Union
from ..browser.edge_driver import EdgeDriver
from ..browser.chrome_driver import ChromeDriver
from ..browser.firefox_driver import FirefoxDriver
from ..config.constants import (
    BROWSER_TYPE_EDGE,
    BROWSER_TYPE_CHROME,
    BROWSER_TYPE_FIREFOX,
    MAX_RETRY_COUNT,
)

logger = logging.getLogger(__name__)


class M3u8Parser:
    """
    m3u8 解析类，负责提取 m3u8 链接和基础 URL。

    该类封装了从浏览器网络日志中提取 m3u8 链接的逻辑，
    支持 Edge、Chrome、Firefox 三种浏览器。

    Attributes:
        browser: 浏览器实例
        browser_type: 浏览器类型
        max_retries: 最大重试次数
    """

    def __init__(
        self,
        browser: Union[EdgeDriver, ChromeDriver, FirefoxDriver],
        browser_type: str,
        max_retries: int = MAX_RETRY_COUNT,
    ):
        """
        初始化 m3u8 解析器。

        Args:
            browser: 浏览器实例
            browser_type: 浏览器类型（edge/chrome/firefox）
            max_retries: 最大重试次数，默认为 5
        """
        self.browser = browser
        self.browser_type = browser_type
        self.max_retries = max_retries

    def fetch_m3u8_links(self, url: str) -> Optional[List[str]]:
        """
        从浏览器网络日志中提取 m3u8 链接。

        从用户输入的 URL 中提取 liveUuid，然后从浏览器网络日志中提取包含 liveUuid 的 m3u8 链接。

        Args:
            url: 钉钉直播回放分享链接

        Returns:
            m3u8 链接列表，如果提取失败则返回 None

        Raises:
            Exception: 提取失败时
        """
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        live_uuid = query_params.get("liveUuid", [None])[0]

        if not live_uuid:
            logger.error("未能从 URL 提取 liveUuid，程序将退出")
            return None

        m3u8_links = []

        for attempt in range(self.max_retries):
            try:
                if self.browser_type in [BROWSER_TYPE_EDGE, BROWSER_TYPE_CHROME]:
                    logs = self.browser.get_log("performance")
                elif self.browser_type == BROWSER_TYPE_FIREFOX:
                    logs = self.browser.get_log("performance")

                for log in logs:
                    try:
                        if self.browser_type == BROWSER_TYPE_FIREFOX:
                            log_message = str(log)
                            pattern = r'https://[^,\'"]+\.m3u8\?[^\'"]+'
                            found_links = re.findall(pattern, log_message)

                            if found_links:
                                cleaned_link = re.sub(r'[\]\s\\\'"]+$', "", found_links[0])
                                m3u8_links.append(cleaned_link)
                                logger.debug(f"获取到m3u8链接: {cleaned_link}")
                                return m3u8_links
                        else:
                            if "message" in log:
                                log_message = log["message"]
                            else:
                                log_message = str(log)

                            if ".m3u8" in log_message:
                                start_idx = log_message.find('url":"') + len('url":"')
                                end_idx = log_message.find('"', start_idx)
                                m3u8_url = log_message[start_idx:end_idx]

                                if live_uuid in m3u8_url:
                                    logger.debug(f"获取到m3u8链接: {m3u8_url}")
                                    m3u8_links.append(m3u8_url)
                                    return m3u8_links
                    except Exception as e:
                          logger.error(f"处理日志时发生错误: {e}", exc_info=True)

                logger.warning(f"第 {attempt + 1} 次尝试未获取到 m3u8 链接，重试中")
                self._refresh_page()

            except Exception as e:
                logger.error(f"获取 m3u8 链接时发生错误: {e}", exc_info=True)

        return None

    def download_m3u8_file(self, url: str, filename: str, headers: dict) -> str:
        """
        下载 m3u8 文件。

        通过浏览器 JavaScript 执行 fetch 请求下载 m3u8 文件。
        使用浏览器默认请求头（包括已登录的 Cookie），避免跨域问题。

        Args:
            url: m3u8 文件 URL
            filename: 保存的文件名
            headers: 请求头字典（保留参数以兼容接口，但实际不使用）

        Returns:
            m3u8 文件路径

        Raises:
            Exception: 下载失败时
        """
        try:
            m3u8_content = self.browser.driver.execute_script(
                "return fetch(arguments[0], { method: 'GET' }).then(response => response.text())",
                url,
            )

            with open(filename, "w", encoding="utf-8") as f:
                f.write(m3u8_content)

            return filename

        except Exception as e:
            logger.error(f"下载 m3u8 文件时发生错误: {e}", exc_info=True)
            sys.exit(1)

    def extract_prefix(self, url: str) -> str:
        """
        提取基础 URL。

        从 m3u8 链接中提取基础 URL。

        Args:
            url: m3u8 文件 URL

        Returns:
            基础 URL
        """
        pattern = re.compile(r"(https?://[^/]+/live_hp/[0-9a-f-]+)")
        match = pattern.search(url)
        return match.group(1) if match else url

    def _refresh_page(self) -> None:
        """
        刷新页面。

        通过 JavaScript 刷新页面。
        """
        try:
            self.browser.driver.execute_script("location.reload();")
            logger.debug("页面已刷新")
        except Exception as e:
            logger.error(f"刷新页面时发生错误: {e}", exc_info=True)
