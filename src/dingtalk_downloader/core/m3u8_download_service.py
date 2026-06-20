"""M3u8RefreshService —— 拉取一个最新 m3u8（含新 auth_key）并落盘。

类名 M3u8RefreshService（重命名自 M3u8DownloadService），但文件路径保留
m3u8_download_service.py 以保持向后兼容（spec 3.3 + pre-flight 决定）。
"""

import logging
import os
import re
import uuid
from typing import Optional
from urllib.parse import parse_qs, urlparse

from ..browser.browser_driver import BrowserDriver
from ..utils.m3u8_file_manager import M3u8FileManager
from ..utils.models import M3u8Link
from .exceptions import M3u8RefreshError

logger = logging.getLogger(__name__)


class M3u8RefreshService:
    """每次调用 fetch() 都生成一个独立的本地 m3u8 文件。

    直接接受 BrowserDriver，自己驱动刷新+解析（不再依赖 M3u8Parser）。
    """

    def __init__(
        self,
        browser: BrowserDriver,
        file_manager: Optional[M3u8FileManager] = None,
        max_attempts: int = 5,
    ):
        self.browser = browser
        self.file_manager = file_manager or M3u8FileManager()
        self.max_attempts = max_attempts

    def fetch(self, share_url: str) -> M3u8Link:
        """拉取最新 m3u8 并下载到 temp/ 下的新 UUID 文件。"""
        live_uuid = self._extract_live_uuid(share_url)
        if not live_uuid:
            raise M3u8RefreshError(f"无法从 URL 提取 liveUuid: {share_url}")

        m3u8_url: Optional[str] = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                self._refresh_page()
                logs = self.browser.get_log("performance")
                links = self.browser.extract_m3u8_links_from_logs(logs, live_uuid)
                if links:
                    m3u8_url = links[-1]
                    logger.info(f"第 {attempt} 次尝试获取到 m3u8: {m3u8_url}")
                    break
                logger.warning(f"第 {attempt} 次未获取到 m3u8 链接")
            except Exception as e:
                logger.error(f"第 {attempt} 次刷新失败: {e}", exc_info=True)

        if not m3u8_url:
            raise M3u8RefreshError(
                f"经过 {self.max_attempts} 次刷新后仍未获取到 m3u8"
            )

        local_path = self._download_m3u8(m3u8_url)
        prefix = self._extract_prefix(m3u8_url)
        return M3u8Link(url=m3u8_url, prefix=prefix, local_file_path=local_path)

    def _extract_live_uuid(self, share_url: str) -> Optional[str]:
        parsed = urlparse(share_url)
        params = parse_qs(parsed.query)
        return params.get("liveUuid", [None])[0]

    def _refresh_page(self) -> None:
        try:
            self.browser.driver.execute_script("location.reload();")
        except Exception as e:
            logger.warning(f"刷新页面失败: {e}")

    def _download_m3u8(self, m3u8_url: str) -> str:
        """通过浏览器 fetch 下载 m3u8 内容到新 UUID 文件。

        浏览器 fetch 失败时（execute_script 返回 None），抛 M3u8RefreshError
        并清理可能残留的空文件，避免下游 N_m3u8DL-RE 拿到无效 m3u8。
        """
        uuid_str = str(uuid.uuid4())
        # Brief specifies unique UUID-suffixed path per call. M3u8FileManager
        # 不接受 suffix kwarg，所以这里直接拼出文件名再用 temp_dir。
        filename = f"_{uuid_str}.m3u8"
        local_path = os.path.join(self.file_manager.temp_dir, filename)

        script = (
            "return fetch(arguments[0], { method: 'GET' })"
            ".then(response => response.text())"
        )
        content = self.browser.driver.execute_script(script, m3u8_url)
        if not content:
            # fetch 失败或返回 None/空串 — 防御性清理空文件
            try:
                if os.path.exists(local_path):
                    os.remove(local_path)
            except OSError:
                pass
            raise M3u8RefreshError(
                f"浏览器 fetch 失败，未获取到 m3u8 内容: {m3u8_url}"
            )
        os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"m3u8 下载成功: {local_path}")
        return local_path

    def _extract_prefix(self, m3u8_url: str) -> str:
        pattern = re.compile(r"(https?://[^/]+/live_hp/[0-9a-f-]+)")
        match = pattern.search(m3u8_url)
        return match.group(1) if match else m3u8_url