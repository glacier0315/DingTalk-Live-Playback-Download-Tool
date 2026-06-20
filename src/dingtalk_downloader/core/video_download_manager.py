"""视频下载管理器 —— 薄包装，委托给 DownloadSession + DownloadOrchestrator。

公开方法签名保留以兼容 downloader.py：
- __init__(browser_type, save_mode, ...)
- initialize_download(url) -> VideoDownloadContext  (薄 shim)
- process_video(context) -> bool
- close()
- cleanup_context(context)
"""

import logging
from typing import Optional

from .download_orchestrator import DownloadOrchestrator
from .download_session import DownloadSession
from .retry_policy import RetryPolicy
from ..binary.n_m3u8dl_re import NM3u8DLRE
from ..utils.models import CookieData, HeadersData, VideoDownloadContext
from ..utils.path_selector import PathSelector

logger = logging.getLogger(__name__)


class VideoDownloadManager:
    """薄包装：保持旧公开接口，内部委托给 DownloadSession + DownloadOrchestrator。"""

    def __init__(
        self,
        browser_type: str,
        save_mode: str,
        cookie_handler=None,
        m3u8_parser=None,
        m3u8_download_service=None,
        path_selector=None,
        n_m3u8dl_re=None,
    ):
        self.browser_type = browser_type
        self.save_mode = save_mode
        # 旧参数保留但不再使用；保留以兼容旧调用方（如 Downloader + DependencyFactory）
        self._path_selector = path_selector or PathSelector(save_mode)
        self._n_m3u8dl_re = n_m3u8dl_re or NM3u8DLRE()

    def initialize_download(self, url: str) -> VideoDownloadContext:
        """构造一个最小 VideoDownloadContext。真正的 cookie/headers/live_name 提取在 process_video 内的 Session 完成。"""
        save_dir = self._path_selector.get_save_dir()
        return VideoDownloadContext(
            url=url,
            cookie_data=CookieData(cookies={}),
            headers_data=HeadersData(headers={}),
            live_name="直播视频",  # 占位；process_video 内的 session 会覆盖
            save_dir=save_dir,
            save_mode=self.save_mode,
        )

    def process_video(self, context: VideoDownloadContext) -> bool:
        """委托给 DownloadOrchestrator。"""
        save_dir_resolver = lambda: context.save_dir or self._path_selector.get_save_dir()
        with DownloadSession(
            browser_type=self.browser_type,
            save_mode=self.save_mode,
        ) as session:
            orchestrator = DownloadOrchestrator(
                session=session,
                n_m3u8dl_re=self._n_m3u8dl_re,
                retry_policy=RetryPolicy(),
                save_dir_resolver=save_dir_resolver,
            )
            outcome = orchestrator.run(context)
            return outcome.success

    def close(self) -> None:
        """兼容旧接口；无状态可关。"""
        logger.debug("VideoDownloadManager.close() — no-op in thin-wrapper")

    def cleanup_context(self, context) -> None:
        """兼容旧接口。"""
        if context is None:
            return
        logger.debug(
            f"VideoDownloadManager.cleanup_context() — no-op for {getattr(context, 'live_name', '?')}"
        )
