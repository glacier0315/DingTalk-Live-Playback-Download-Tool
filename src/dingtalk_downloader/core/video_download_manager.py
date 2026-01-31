"""
钉钉直播回放下载工具 - 视频下载管理器模块

本模块负责视频下载流程的协调和管理。

作者：项目团队
依赖：logging
创建日期：2026-01-26
修改历史：
    - 2026-01-26: 初始版本，从Downloader类中提取视频下载管理逻辑
"""

import os
import logging
import time
import random
from typing import  Optional
from .cookie_handler import CookieHandler
from .m3u8_parser import M3u8Parser, M3u8ParseError
from ..utils.models import VideoDownloadContext, M3u8Link
from .m3u8_download_service import M3u8DownloadService
from .exceptions import (
    DownloadError,
    BrowserError,
    NetworkError,
)
from ..binary.n_m3u8dl_re import NM3u8DLRE
from ..utils.path_selector import PathSelector
from ..config.constants import (
    VIDEO_DOWNLOAD_MAX_RETRIES,
    VIDEO_DOWNLOAD_RETRY_WAIT_MIN,
    VIDEO_DOWNLOAD_RETRY_WAIT_MAX,
)
logger = logging.getLogger(__name__)


class VideoDownloadManager:
    """
    视频下载管理器类。

    负责协调Cookie获取、m3u8解析、视频下载的整个流程。

    Attributes:
        browser_type: 浏览器类型
        cookie_handler: Cookie处理器
        m3u8_parser: m3u8解析器
        m3u8_download_service: m3u8下载服务
        path_selector: 路径选择器
        n_m3u8dl_re: N_m3u8DL-RE调用器
    """

    def __init__(
        self,
        browser_type: str,
        save_mode: str,
        cookie_handler: Optional[CookieHandler] = None,
        m3u8_parser: Optional[M3u8Parser] = None,
        m3u8_download_service: Optional[M3u8DownloadService] = None,
        path_selector: Optional[PathSelector] = None,
        n_m3u8dl_re: Optional[NM3u8DLRE] = None,
    ):
        """
        初始化视频下载管理器。

        Args:
            browser_type: 浏览器类型（edge/chrome/firefox）
            save_mode: 保存模式（1：默认路径，2：手动选择）
            cookie_handler: Cookie处理器（可选，用于依赖注入）
            m3u8_parser: m3u8解析器（可选，用于依赖注入）
            m3u8_download_service: m3u8下载服务（可选，用于依赖注入）
            path_selector: 路径选择器（可选，用于依赖注入）
            n_m3u8dl_re: NM3u8DLRE实例（可选，用于依赖注入）
        """
        self.browser_type = browser_type
        self.save_mode = save_mode

        self.cookie_handler = cookie_handler
        self.m3u8_parser = m3u8_parser
        self.m3u8_download_service = m3u8_download_service
        self.path_selector = path_selector
        self.n_m3u8dl_re = n_m3u8dl_re

        logger.debug(
            f"视频下载管理器初始化完成 - 浏览器类型: {browser_type}, " f"保存模式: {save_mode}"
        )

    def initialize_download(self, url: str) -> VideoDownloadContext:
        """
        初始化下载环境。

        获取Cookie、请求头和创建m3u8解析器。

        Args:
            url: 钉钉直播回放分享链接

        Returns:
            VideoDownloadContext: 视频下载上下文
        """
        if not self.cookie_handler:
            self.cookie_handler = CookieHandler(self.browser_type)

        if not self.path_selector:
            self.path_selector = PathSelector(self.save_mode)

        cookie_data, headers_data, live_name = self.cookie_handler.get_cookie(url)
        logger.info(f"获取到 Cookie: {cookie_data}")
        logger.info(f"获取到 请求头: {headers_data}")
        logger.info(f"获取到 直播名称: {live_name}")

        if not self.m3u8_parser:
            self.m3u8_parser = M3u8Parser(self.cookie_handler.browser)

        if not self.m3u8_download_service:
            self.m3u8_download_service = M3u8DownloadService(self.m3u8_parser)

        if not self.n_m3u8dl_re:
            self.n_m3u8dl_re = NM3u8DLRE()

        logger.info("m3u8 解析器创建成功")

        return VideoDownloadContext(
            url=url,
            cookie_data=cookie_data,
            headers_data=headers_data,
            live_name=live_name,
            save_mode=self.path_selector.save_mode,
        )

    def process_video(self, context: VideoDownloadContext) -> bool:
        """
        处理单个视频下载。
        下载完成后自动清理临时m3u8文件。
        支持自动重试机制，最大重试20次，每次重试前等待3-10秒。

        Args:
            context: 视频下载上下文

        Returns:
            bool: 下载成功返回True，下载失败返回False
        """
        max_retries = VIDEO_DOWNLOAD_MAX_RETRIES
        m3u8_link = None

        for attempt in range(1, max_retries + 1):
            try:
                m3u8_link = self._attempt_download(context, attempt, max_retries)
                download_success = self._download_video(m3u8_link, context)

                if download_success:
                    logger.info(f"视频下载成功: {context.live_name} (第 {attempt} 次尝试)")
                    return True

                logger.warning(f"视频下载失败: {context.live_name} (第 {attempt} 次尝试)")

            except (DownloadError, BrowserError, NetworkError, M3u8ParseError) as e:
                self._handle_download_exception(context, e, attempt, max_retries)
                if attempt == max_retries:
                    return False
            except Exception as e:
                logger.error(
                    f"处理视频时发生未知错误: {context.live_name} (第 {attempt} 次尝试), 错误: {e}",
                    exc_info=True
                )
                if attempt == max_retries:
                    logger.error(
                        f"已达到最大重试次数 {max_retries}，下载终止: {context.live_name}"
                    )
                    raise DownloadError(f"处理视频失败: {context.live_name}, 错误: {e}") from e
            finally:
                if m3u8_link and m3u8_link.local_file_path:
                    self.m3u8_download_service.cleanup_temp_file(
                        m3u8_link.local_file_path
                    )

        return False

    def _attempt_download(
        self,
        context: VideoDownloadContext,
        attempt: int,
        max_retries: int,
    ) -> M3u8Link:
        """
        尝试下载视频。

        Args:
            context: 视频下载上下文
            attempt: 当前尝试次数
            max_retries: 最大重试次数

        Returns:
            M3u8Link: m3u8链接对象
        """
        if attempt > 1:
            self._prepare_retry(context, attempt)

        m3u8_link = self.m3u8_download_service.fetch_and_download_m3u8(
            context.url, context.get_headers_dict()
        )
        return m3u8_link

    def _prepare_retry(self, context: VideoDownloadContext, attempt: int) -> None:
        """
        准备重试。

        Args:
            context: 视频下载上下文
            attempt: 当前尝试次数
        """
        logger.info(f"第 {attempt} 次尝试下载视频: {context.live_name}")

        random_wait = random.randint(VIDEO_DOWNLOAD_RETRY_WAIT_MIN, VIDEO_DOWNLOAD_RETRY_WAIT_MAX)
        logger.info(f"等待 {random_wait} 秒后重试...")
        time.sleep(random_wait)

        context = self.initialize_download(context.url)

    def _handle_download_exception(
        self,
        context: VideoDownloadContext,
        error: Exception,
        attempt: int,
        max_retries: int,
    ) -> None:
        """
        处理下载异常。

        Args:
            context: 视频下载上下文
            error: 异常对象
            attempt: 当前尝试次数
            max_retries: 最大重试次数
        """
        error_type = type(error).__name__
        logger.error(
            f"{error_type}: {context.live_name} (第 {attempt} 次尝试), 错误: {error}"
        )

        if attempt == max_retries:
            logger.error(
                f"已达到最大重试次数 {max_retries}，下载终止: {context.live_name}"
            )

    def _download_video(
        self,
        m3u8_link: M3u8Link,
        context: VideoDownloadContext,
    ) -> bool:
        """
        下载视频。

        根据保存模式选择保存路径，然后调用N_m3u8DL-RE下载视频。

        Args:
            m3u8_link: m3u8链接对象
            context: 视频下载上下文

        Returns:
            bool: 下载成功返回True，下载失败返回False
        """
        logger.info(f"开始下载视频 - 文件名: {context.live_name}")

        if not m3u8_link.local_file_path:
            logger.error("m3u8 文件路径为空，无法下载视频")
            return False

        if not os.path.exists(m3u8_link.local_file_path):
            logger.error(f"m3u8 文件不存在: {m3u8_link.local_file_path}")
            return False

        logger.info(f"使用本地 m3u8 文件: {m3u8_link.local_file_path}")

        if not self.path_selector:
            self.path_selector = PathSelector(self.save_mode)

        save_dir = self.path_selector.get_save_dir()
        if not save_dir:
            return False

        if not self.n_m3u8dl_re:
            self.n_m3u8dl_re = NM3u8DLRE()

        logger.info("调用 N_m3u8DL-RE 下载视频")
        logger.debug(
            f"下载参数 - m3u8文件: {m3u8_link.local_file_path}, "
            f"保存名称: {context.live_name}, "
            f"保存目录: {save_dir}, "
            f"基础URL: {m3u8_link.prefix}"
        )

        download_success = self.n_m3u8dl_re.download(
            m3u8_link.local_file_path,
            context.live_name,
            save_dir,
            m3u8_link.prefix,
            context.get_cookies_dict(),
            context.get_headers_dict(),
        )

        return download_success

    def close(self) -> None:
        """
        关闭浏览器，释放资源。
        """
        logger.info("开始释放视频下载管理器资源")
        if self.cookie_handler:
            self.cookie_handler.close()
        logger.info("视频下载管理器资源释放完成")

    def cleanup_context(self, context: VideoDownloadContext) -> None:
        """
        清理下载上下文相关资源。

        确保所有资源都被正确清理，包括浏览器、解析器等。

        Args:
            context: 视频下载上下文
        """
        try:
            if context:
                logger.debug(f"清理上下文资源: {context.live_name}")
                
                if hasattr(context, "cookie_data") and context.cookie_data:
                    logger.debug(f"清理Cookie数据: {context.live_name}")
                    
                if hasattr(self, "m3u8_parser") and self.m3u8_parser:
                    logger.debug(f"清理m3u8解析器: {context.live_name}")
                    self.m3u8_parser = None
                    
                if hasattr(self, "m3u8_download_service") and self.m3u8_download_service:
                    logger.debug(f"清理m3u8下载服务: {context.live_name}")
                    self.m3u8_download_service = None
                    
                logger.info(f"上下文资源清理完成: {context.live_name}")
        except Exception as e:
            logger.warning(f"清理上下文资源时发生错误: {context.live_name}, 错误: {e}", exc_info=True)
