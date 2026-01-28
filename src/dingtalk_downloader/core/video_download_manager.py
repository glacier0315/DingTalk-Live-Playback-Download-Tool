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
from typing import Dict, Optional
from .cookie_handler import CookieHandler, CookieError
from .m3u8_parser import M3u8Parser, M3u8ParseError
from ..utils.models import CookieData, HeadersData, VideoDownloadContext, M3u8Link
from .m3u8_download_service import M3u8DownloadService
from .exceptions import (
    DownloadError,
    BrowserError,
    NetworkError,
    ValidationError,
)
from ..binary.n_m3u8dl_re import NM3u8DLRE
from ..utils.path_selector import PathSelector
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

    def __init__(self, browser_type: str, save_mode: str):
        """
        初始化视频下载管理器。

        Args:
            browser_type: 浏览器类型（edge/chrome/firefox）
            save_mode: 保存模式（1：默认路径，2：手动选择）
        """
        self.browser_type = browser_type
        self.cookie_handler = CookieHandler(browser_type)
        self.m3u8_parser: Optional[M3u8Parser] = None
        self.m3u8_download_service: Optional[M3u8DownloadService] = None
        self.path_selector = PathSelector(save_mode)
        self.n_m3u8dl_re = NM3u8DLRE()

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
        browser, cookie_data, headers_data, live_name = self.cookie_handler.get_cookie(url)
        logger.info(f"获取到 Cookie 和请求头 - 直播名称: {live_name}")

        self.m3u8_parser = M3u8Parser(browser)
        self.m3u8_download_service = M3u8DownloadService(self.m3u8_parser)
        logger.info("m3u8 解析器创建成功")

        return VideoDownloadContext(
            url=url,
            cookie_data=cookie_data,
            headers_data=headers_data,
            live_name=live_name,
            save_mode=self.path_selector.save_mode,
        )

    def repeat_get_context(self, url: str) -> VideoDownloadContext:
        """
        重复获取下载上下文。

        使用已有的浏览器实例重复获取Cookie和请求头信息。

        Args:
            url: 钉钉直播回放分享链接

        Returns:
            VideoDownloadContext: 视频下载上下文
        """
        cookie_data, headers_data, live_name = self.cookie_handler.repeat_get_cookie(url)
        logger.info(f"获取到 Cookie 和请求头，直播名称: {live_name}")

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

        Args:
            context: 视频下载上下文

        Returns:
            bool: 下载成功返回True，下载失败返回False
        """
        m3u8_link = None
        try:
            m3u8_link = self.m3u8_download_service.fetch_and_download_m3u8(
                context.url, context.get_headers_dict()
            )

            download_success = self._download_video(m3u8_link, context)
            if download_success:
                logger.info(f"视频下载完成: {context.live_name}")
            else:
                logger.error(f"视频下载失败: {context.live_name}")

            return download_success
        except DownloadError as e:
            logger.error(f"视频下载失败: {context.live_name}, 错误: {e}")
            return False
        except BrowserError as e:
            logger.error(f"浏览器操作失败: {context.live_name}, 错误: {e}")
            return False
        except NetworkError as e:
            logger.error(f"网络请求失败: {context.live_name}, 错误: {e}")
            return False
        except M3u8ParseError as e:
            logger.error(f"m3u8解析失败: {context.live_name}, 错误: {e}")
            return False
        except Exception as e:
            logger.error(f"处理视频时发生未知错误: {context.live_name}, 错误: {e}", exc_info=True)
            raise DownloadError(f"处理视频失败: {context.live_name}, 错误: {e}") from e
        finally:
            if m3u8_link and m3u8_link.local_file_path:
                self.m3u8_download_service.cleanup_temp_file(
                    m3u8_link.local_file_path
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

        save_dir = self.path_selector.get_save_dir()
        if not save_dir:
            return False

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
