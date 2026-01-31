"""
钉钉直播回放下载工具 - m3u8 解析模块

本模块负责从浏览器网络日志中提取 m3u8 链接和基础 URL。

作者：项目团队
依赖：selenium, re, urllib.parse
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2025-01-15: 添加日志记录
    - 2026-01-21: 重构-消除魔法数字,优化日志处理
    - 2026-01-22: 重构-移除sys.exit调用,改为抛出M3u8ParseError
"""

import re
import logging
from urllib.parse import urlparse, parse_qs
from ..browser.browser_driver import BrowserDriver
from ..config.constants import MAX_RETRY_COUNT
from .exceptions import M3u8ParseError

logger = logging.getLogger(__name__)

FIRST_ELEMENT_INDEX = 0
LOG_TYPE_PERFORMANCE = "performance"


class M3u8Parser:
    """
    m3u8 解析类，负责提取 m3u8 链接和基础 URL。

    该类封装了从浏览器网络日志中提取 m3u8 链接的逻辑，
    支持 Edge、Chrome、Firefox 三种浏览器。

    Attributes:
        browser: 浏览器实例
        max_retries: 最大重试次数
    """

    def __init__(
        self,
        browser: BrowserDriver,
        max_retries: int = MAX_RETRY_COUNT,
    ):
        """
        初始化 m3u8 解析器。

        Args:
            browser: 浏览器实例
            max_retries: 最大重试次数，默认为 5
        """
        self.browser = browser
        self.max_retries = max_retries

    def fetch_m3u8_link(self, url: str) -> str:
        """
        从浏览器网络日志中提取 m3u8 链接。

        从用户输入的 URL 中提取 liveUuid，然后从浏览器网络日志中提取包含 liveUuid 的 m3u8 链接。

        Args:
            url: 钉钉直播回放分享链接

        Returns:
            m3u8 链接，如果提取失败则返回 None,
            提取到的 m3u8 链接列表长度为 1 时，返回该链接；
            提取到的 m3u8 链接列表长度大于 1 时，返回最后一个链接。


        Raises:
            Exception: 提取失败时
        """
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        live_uuid = query_params.get("liveUuid", [None])[FIRST_ELEMENT_INDEX]

        if not live_uuid:
            logger.error("未能从 URL 提取 liveUuid")
            raise M3u8ParseError("未能从 URL 提取 liveUuid 参数")

        for attempt in range(self.max_retries):
            try:
                logger.info(f"第 {attempt + 1} 次尝试获取到 m3u8 链接")
                self._refresh_page()
                logs = self.browser.get_log(LOG_TYPE_PERFORMANCE)
                logger.info(f"从浏览器日志中提取到 {len(logs)} 个 性能日志")
                m3u8_links = self.browser.extract_m3u8_links_from_logs(logs, live_uuid)
                if not m3u8_links:
                    logger.warning(f"第 {attempt + 1} 次尝试未获取到 m3u8 链接")
                    continue

                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"提取到的 m3u8 链接: {m3u8_links}")
                # 预期仅 1 个 m3u8 链接，返回最后一个
                if len(m3u8_links) >= 1:
                    logger.info(
                        f"提取到 {len(m3u8_links)} 个 m3u8 链接，预期仅 1 个, "
                        f"返回最后一个链接: {m3u8_links[-1]}"
                    )
                    return m3u8_links[-1]
            except Exception as e:
                logger.error(f"第 {attempt + 1} 次尝试获取 m3u8 链接时发生错误: {e}", exc_info=True)

        logger.warning(f"经过 {self.max_retries} 次重试后仍未获取到 m3u8 链接")
        raise M3u8ParseError(f"经过 {self.max_retries} 次重试后仍未获取到 m3u8 链接")

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
            M3u8ParseError: 下载失败时
        """
        try:
            script = (
                "return fetch(arguments[0], { method: 'GET' })" ".then(response => response.text())"
            )
            m3u8_content = self.browser.driver.execute_script(
                script,
                url,
            )

            with open(filename, "w", encoding="utf-8") as f:
                f.write(m3u8_content)

            logger.info(f"m3u8 文件下载成功: {filename}")
            return filename

        except Exception as e:
            logger.error(
                f"下载 m3u8 文件时发生错误: {e}, "
                f"URL: {url}, "
                f"文件名: {filename}",
                exc_info=True
            )
            raise M3u8ParseError(
                f"下载m3u8文件失败: {e}。"
                f"URL: {url}, "
                f"文件名: {filename}"
            ) from e

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
