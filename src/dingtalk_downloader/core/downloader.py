"""
钉钉直播回放下载工具 - 下载器核心模块

本模块负责协调视频下载流程，作为外观类提供统一接口。

作者：项目团队
依赖：无
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2025-01-15: 添加日志记录
    - 2026-01-21: 重构-拆分过长方法,提取m3u8下载逻辑,移除sys.exit调用,完善类型注解
    - 2026-01-26: 重构-提取VideoDownloadManager、PathSelector、M3u8DownloadService类，简化职责
"""

import logging
from typing import Dict, Optional, Tuple, Any
from .cookie_handler import CookieError
from .m3u8_parser import M3u8ParseError
from .video_download_manager import VideoDownloadManager
from .user_interaction_controller import UserInteractionController
from ..utils.models import VideoDownloadContext
from .exceptions import (
    DownloadError,
    BrowserError,
    NetworkError,
    ValidationError,
)
from ..utils.validator import validate_required_input, validate_dingtalk_url
logger = logging.getLogger(__name__)


class Downloader:
    """
    下载器类，作为外观类提供统一接口。

    该类封装了单个视频下载和批量下载的逻辑，
    通过VideoDownloadManager、UserInteractionController等辅助类实现功能。

    Attributes:
        video_manager: 视频下载管理器
        browser_type: 浏览器类型
        save_mode: 保存模式
        user_controller: 用户交互控制器
    """

    def __init__(
        self,
        browser_type: str,
        save_mode: str,
        user_controller: UserInteractionController,
    ):
        """
        初始化下载器。

        Args:
            browser_type: 浏览器类型（edge/chrome/firefox）
            save_mode: 保存模式（1：默认路径，2：手动选择）
            user_controller: 用户交互控制器
        """
        self.browser_type = browser_type
        self.save_mode = save_mode
        self.video_manager = VideoDownloadManager(browser_type, save_mode)
        self.user_controller = user_controller

        logger.info(f"下载器初始化完成 - 浏览器类型: {browser_type}, 保存模式: {save_mode}")

    def download_single_video(self, url: str) -> None:
        """
        下载单个视频。

        协调Cookie获取、m3u8解析、视频下载。

        Args:
            url: 钉钉直播回放分享链接

        Raises:
            DownloadError: 下载失败时
        """
        logger.info("开始下载单个视频")

        context = None
        try:
            context = self.video_manager.initialize_download(url)
            while True:
                try:
                    self.video_manager.process_video(context)
                except DownloadError as e:
                    logger.error(f"视频下载失败: {e}")
                    print(f"下载失败: {e}")
                except BrowserError as e:
                    logger.error(f"浏览器操作失败: {e}")
                    print(f"浏览器操作失败: {e}")
                except NetworkError as e:
                    logger.error(f"网络请求失败: {e}")
                    print(f"网络请求失败: {e}")
                except ValidationError as e:
                    logger.error(f"输入验证失败: {e}")
                    print(f"输入验证失败: {e}")

                new_url = self.user_controller.get_user_input(
                    "请继续输入钉钉直播分享链接，或输入q退出程序: ",
                    validation_func=lambda x: (x.lower() == "q" or validate_dingtalk_url(x)),
                    error_message="输入不正确，请重新输入。",
                    input_name="钉钉直播分享链接",
                )

                if new_url.lower() == "q":
                    logger.info("用户选择退出程序")
                    self.close()
                    print("程序已退出。")
                    break
                context = self.video_manager.repeat_get_context(new_url)
        except KeyboardInterrupt:
            logger.warning("用户中断下载")
            print("\n程序已被用户终止。")
            self.close()
            raise
        except (CookieError, M3u8ParseError) as e:
            logger.error(f"初始化下载失败: {e}", exc_info=True)
            raise DownloadError(f"初始化下载失败: {e}") from e
        except Exception as e:
            logger.error(f"下载单个视频时发生未知错误: {e}", exc_info=True)
            raise DownloadError(f"下载单个视频失败: {e}") from e
        finally:
            if context:
                self.video_manager.cleanup_context(context)

    def _download_first_video(self, first_url: str) -> None:
        """
        下载第一个视频。

        Args:
            first_url: 第一个链接
        """
        logger.info("正在下载第 1 个视频，共 1 个视频")

        try:
            context = self.video_manager.initialize_download(first_url)
            self.video_manager.process_video(context)
            logger.info(f"视频下载完成: {context.live_name}")
        except DownloadError as e:
            logger.error(f"第 1 个视频下载失败: {e}")

        print("=" * 100)
        logger.info("第 1 个视频下载完成")

    def _download_remaining_videos(self, urls: Dict[int, str], total_links: int) -> None:
        """
        下载剩余的视频。

        Args:
            urls: 链接字典
            total_links: 总链接数
        """
        for idx, dingtalk_url in list(urls.items())[1:]:
            logger.info(f"正在下载第 {idx + 1} 个视频，共 {total_links} 个视频")

            try:
                context = self.video_manager.repeat_get_context(dingtalk_url)
                logger.info(f"获取到 Cookie 和请求头，直播名称: {context.live_name}")

                self.video_manager.process_video(context)
                logger.info(f"视频下载完成: {context.live_name}")
            except DownloadError as e:
                logger.error(f"第 {idx + 1} 个视频下载失败: {e}")

            logger.info(f"第 {idx + 1} 个视频下载完成")

    def download_batch_videos(self, urls: Dict[int, str]) -> None:
        """
        批量下载视频。

        协调Cookie获取、m3u8解析、视频下载。

        Args:
            urls: 链接字典 {index: url}

        Raises:
            DownloadError: 下载失败时
        """
        logger.info(f"开始批量下载视频，共 {len(urls)} 个链接")

        try:
            total_links = len(urls)

            first_link = next(iter(urls.values()))
            self._download_first_video(first_link)
            self._download_remaining_videos(urls, total_links)

            self._continue_download()

        except KeyboardInterrupt:
            logger.warning("用户中断批量下载")
            print("\n程序已被用户终止。")
            self.close()
            raise
        except Exception as e:
            logger.error(f"批量下载视频时发生错误: {e}", exc_info=True)
            raise DownloadError(f"批量下载失败: {e}") from e

    def _continue_download(self) -> None:
        """
        继续下载新的钉钉直播回放链接。

        询问用户是否继续输入新的链接文件进行下载。
        """
        logger.info("进入继续下载循环")

        while True:
            if not self.user_controller.ask_continue_download():
                logger.info("用户选择退出程序")
                self.close()
                break
            else:
                logger.info("用户选择继续下载")
                from ..utils.file_reader import FileReader

                file_path = self.user_controller.ask_file_path()
                if file_path is None:
                    logger.info("用户选择退出程序")
                    self.close()
                    break

                logger.info("用户已输入文件路径")

                new_links_dict = FileReader(file_path).read_links()
                logger.info(f"从文件中读取到 {len(new_links_dict)} 个链接")

                self.download_batch_videos(new_links_dict)

    def close(self) -> None:
        """
        关闭浏览器，释放资源。
        """
        logger.info("开始释放下载器资源")
        if self.video_manager:
            self.video_manager.close()
        logger.debug("下载器资源释放完成")
