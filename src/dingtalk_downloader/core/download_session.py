"""DownloadSession —— 一次下载涉及的所有资源的 context manager。

用 with 块包住，自动清理：
- CookieHandler 持有的 browser
- 本次下载产生的所有 temp m3u8 文件

不参与重试决策。
"""

import logging
import os
from typing import List, Optional

from .cookie_handler import CookieHandler
from .m3u8_download_service import M3u8RefreshService
from ..utils.models import CookieData, HeadersData

logger = logging.getLogger(__name__)


class DownloadSession:
    """一次完整下载的资源容器。"""

    def __init__(
        self,
        browser_type: str,
        save_mode: str,
        url: Optional[str] = None,
        cookie_handler: Optional[CookieHandler] = None,
    ):
        self.browser_type = browser_type
        self.save_mode = save_mode
        self._url = url
        self._cookie_handler = cookie_handler
        self._cookie_data: Optional[CookieData] = None
        self._headers_data: Optional[HeadersData] = None
        self._live_name: Optional[str] = None
        self._refresh_service: Optional[M3u8RefreshService] = None
        self._temp_files: List[str] = []

    def __enter__(self) -> "DownloadSession":
        if self._cookie_handler is None:
            self._cookie_handler = CookieHandler(self.browser_type)
        # 关键修复：必须把真实分享 URL 传给 CookieHandler 让浏览器导航到该页，
        # 否则后续 m3u8 刷新会去翻 "placeholder" 这种空页。
        nav_url = self._url if self._url else "about:blank"
        cookie_data, headers_data, live_name = self._cookie_handler.get_cookie(nav_url)
        self._cookie_data = cookie_data
        self._headers_data = headers_data
        self._live_name = live_name
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # 1. 清 temp 文件
        for path in self._temp_files:
            try:
                if path and os.path.exists(path):
                    os.remove(path)
                    logger.debug(f"已清理 temp: {path}")
            except Exception as e:
                logger.warning(f"清理 temp 失败: {path}, {e}")
        # 2. 关 browser
        try:
            if self._cookie_handler is not None:
                self._cookie_handler.close()
        except Exception as e:
            logger.warning(f"关闭 CookieHandler 失败: {e}")
        # 3. 不吞异常
        return None

    # --- accessors ---

    def cookie_data(self) -> CookieData:
        if self._cookie_data is None:
            raise RuntimeError("session not entered (call cookie_data inside `with` block)")
        return self._cookie_data

    def headers_data(self) -> HeadersData:
        if self._headers_data is None:
            raise RuntimeError("session not entered (call headers_data inside `with` block)")
        return self._headers_data

    def live_name(self) -> str:
        if self._live_name is None:
            raise RuntimeError("session not entered (call live_name inside `with` block)")
        return self._live_name

    def refresh_service(self) -> M3u8RefreshService:
        if self._refresh_service is None:
            if self._cookie_handler is None:
                raise RuntimeError(
                    "session not entered (call refresh_service inside `with` block)"
                )
            self._refresh_service = M3u8RefreshService(
                browser=self._cookie_handler.browser,
            )
        return self._refresh_service

    def track_temp_file(self, path: str) -> None:
        self._temp_files.append(path)