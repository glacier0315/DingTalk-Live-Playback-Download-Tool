"""
钉钉直播回放下载工具 - 下载器核心模块

本模块负责协调 Cookie 获取、m3u8 解析、视频下载。

作者：项目团队
依赖：无
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2025-01-15: 添加日志记录
    - 2026-01-21: 重构-拆分过长方法,提取m3u8下载逻辑,移除sys.exit调用,完善类型注解
"""

import os
import tkinter as tk
from tkinter import filedialog
from typing import Dict, Optional, Tuple
import logging
from ..core.cookie_handler import CookieHandler
from ..core.m3u8_parser import M3u8Parser
from ..binary.n_m3u8dl_re import NM3u8DLRE
from ..utils.path_helper import ensure_dir_exists
from ..config.constants import (
    SAVE_MODE_DEFAULT,
    SAVE_MODE_MANUAL,
    DEFAULT_DOWNLOAD_DIR,
    TEMP_M3U8_FILE,
)

logger = logging.getLogger(__name__)


class DownloadError(Exception):
    """下载异常"""

    pass


class Downloader:
    """
    下载器类，负责协调 Cookie 获取、m3u8 解析、视频下载。

    该类封装了单个视频下载和批量下载的逻辑。

    Attributes:
        browser_type: 浏览器类型
        save_mode: 保存模式
        cookie_handler: Cookie 处理器
        m3u8_parser: m3u8 解析器
        n_m3u8dl_re: N_m3u8DL-RE 调用器
        saved_path: 已选择的保存路径
    """

    def __init__(self, browser_type: str, save_mode: str):
        """
        初始化下载器。

        Args:
            browser_type: 浏览器类型（edge/chrome/firefox）
            save_mode: 保存模式（1：默认路径，2：手动选择）
        """
        self.browser_type = browser_type
        self.save_mode = save_mode
        self.cookie_handler = CookieHandler(browser_type)
        self.m3u8_parser = None
        self.n_m3u8dl_re = NM3u8DLRE()
        self.saved_path = None

        logger.info(f"下载器初始化完成 - 浏览器类型: {browser_type}, 保存模式: {save_mode}")

    def _fetch_and_download_m3u8(
        self,
        url: str,
        m3u8_headers: Dict[str, str],
    ) -> Tuple[str, str]:
        """
        获取并下载m3u8文件。

        Args:
            url: 钉钉直播回放分享链接
            m3u8_headers: 请求头字典

        Returns:
            tuple: (m3u8_file, prefix)

        Raises:
            DownloadError: 获取或下载失败时
        """
        logger.info("开始获取 m3u8 链接")
        m3u8_links = self.m3u8_parser.fetch_m3u8_links(url)

        if not m3u8_links:
            raise DownloadError("未找到m3u8链接")

        logger.info(f"获取到 {len(m3u8_links)} 个 m3u8 链接")

        m3u8_file = self.m3u8_parser.download_m3u8_file(
            m3u8_links[0], TEMP_M3U8_FILE, m3u8_headers
        )
        logger.info(f"m3u8 文件下载成功: {m3u8_file}")

        prefix = self.m3u8_parser.extract_prefix(m3u8_links[0])
        logger.info(f"提取到基础 URL: {prefix}")

        return m3u8_file, prefix

    def _process_single_video(
        self,
        url: str,
        cookies_data: Dict[str, str],
        m3u8_headers: Dict[str, str],
        live_name: str,
    ) -> bool:
        """
        处理单个视频下载。

        Args:
            url: 钉钉直播回放分享链接
            cookies_data: Cookie 字典
            m3u8_headers: 请求头字典
            live_name: 直播视频名称

        Returns:
            bool: 下载成功返回 True，下载失败返回 False
        """
        try:
            m3u8_file, prefix = self._fetch_and_download_m3u8(url, m3u8_headers)

            download_success = self._download_video(
                m3u8_file, live_name, prefix, cookies_data, m3u8_headers
            )

            if download_success:
                logger.info(f"视频下载完成: {live_name}")
            else:
                logger.error(f"视频下载失败: {live_name}")

            return download_success

        except Exception as e:
            logger.error(f"处理视频时发生错误: {e}", exc_info=True)
            raise DownloadError(f"处理视频失败: {e}") from e

    def download_single_video(self, url: str) -> None:
        """
        下载单个视频。

        协调 Cookie 获取、m3u8 解析、视频下载。

        Args:
            url: 钉钉直播回放分享链接

        Raises:
            DownloadError: 下载失败时
        """
        logger.info("开始下载单个视频")

        try:
            browser, cookies_data, m3u8_headers, live_name = self.cookie_handler.get_cookie(url)
            logger.info(f"获取到 Cookie 和请求头 - 直播名称: {live_name}")

            self.m3u8_parser = M3u8Parser(browser, self.browser_type)
            logger.info("m3u8 解析器创建成功")

            while True:
                try:
                    self._process_single_video(url, cookies_data, m3u8_headers, live_name)
                except DownloadError as e:
                    logger.error(f"视频下载失败: {e}")
                    print(f"下载失败: {e}")

                url = input("请继续输入钉钉直播分享链接，或输入q退出程序: ")
                if url.lower() == "q":
                    logger.info("用户选择退出程序")
                    self.close()
                    print("程序已退出。")
                    break
                logger.info(f"用户输入新链接: {url}")
                cookies_data, m3u8_headers, live_name = self.cookie_handler.repeat_get_cookie(url)
                logger.info(f"获取到 Cookie 和请求头，直播名称: {live_name}")

        except KeyboardInterrupt:
            logger.warning("用户中断下载")
            print("\n程序已被用户终止。")
            self.close()
            raise
        except Exception as e:
            logger.error(f"下载单个视频时发生错误: {e}", exc_info=True)
            raise DownloadError(f"下载单个视频失败: {e}") from e

    def download_batch_videos(self, urls: Dict[int, str]) -> None:
        """
        批量下载视频。

        协调 Cookie 获取、m3u8 解析、视频下载。

        Args:
            urls: 链接字典 {index: url}

        Raises:
            DownloadError: 下载失败时
        """
        logger.info(f"开始批量下载视频，共 {len(urls)} 个链接")

        try:
            total_links = len(urls)

            first_link = next(iter(urls.values()))
            browser, cookies_data, m3u8_headers, live_name = self.cookie_handler.get_cookie(
                first_link
            )
            logger.info(f"获取到 Cookie 和请求头，直播名称: {live_name}")

            self.m3u8_parser = M3u8Parser(browser, self.browser_type)
            logger.info("m3u8 解析器创建成功")

            logger.info(f"正在下载第 1 个视频，共 {total_links} 个视频")

            try:
                m3u8_file, prefix = self._fetch_and_download_m3u8(first_link, m3u8_headers)
                self._download_video(m3u8_file, live_name, prefix, cookies_data, m3u8_headers)
                logger.info(f"视频下载完成: {live_name}")
            except DownloadError as e:
                logger.error(f"第 1 个视频下载失败: {e}")

            print("=" * 100)
            logger.info("第 1 个视频下载完成")

            for idx, dingtalk_url in list(urls.items())[1:]:
                logger.info(f"正在下载第 {idx + 1} 个视频，共 {total_links} 个视频")

                cookies_data, m3u8_headers, live_name = self.cookie_handler.repeat_get_cookie(
                    dingtalk_url
                )
                logger.info(f"获取到 Cookie 和请求头，直播名称: {live_name}")

                try:
                    m3u8_file, prefix = self._fetch_and_download_m3u8(dingtalk_url, m3u8_headers)
                    self._download_video(m3u8_file, live_name, prefix, cookies_data, m3u8_headers)
                    logger.info(f"视频下载完成: {live_name}")
                except DownloadError as e:
                    logger.error(f"第 {idx + 1} 个视频下载失败: {e}")

                logger.info(f"第 {idx + 1} 个视频下载完成")

            self._continue_download()

        except KeyboardInterrupt:
            logger.warning("用户中断批量下载")
            print("\n程序已被用户终止。")
            self.close()
            raise
        except Exception as e:
            logger.error(f"批量下载视频时发生错误: {e}", exc_info=True)
            raise DownloadError(f"批量下载失败: {e}") from e

    def _download_video(
        self,
        m3u8_file: str,
        save_name: str,
        prefix: str,
        cookies_data: Dict[str, str],
        m3u8_headers: Dict[str, str],
    ) -> bool:
        """
        下载视频。

        根据保存模式选择保存路径，然后调用 N_m3u8DL-RE 下载视频。

        Args:
            m3u8_file: m3u8 文件路径
            save_name: 保存文件名
            prefix: 基础 URL
            cookies_data: Cookie 字典
            m3u8_headers: 请求头字典

        Returns:
            bool: 下载成功返回 True，下载失败返回 False
        """
        logger.info(f"开始下载视频 - 文件名: {save_name}")

        if self.save_mode == SAVE_MODE_DEFAULT:
            save_dir = self._get_default_download_dir()
            logger.info(f"使用默认保存目录: {save_dir}")
        elif self.save_mode == SAVE_MODE_MANUAL:
            save_dir = self._get_manual_download_dir()
            logger.info(f"使用手动选择目录: {save_dir}")
        else:
            logger.error(f"无效的保存模式: {self.save_mode}")
            return False

        if not save_dir:
            logger.warning("用户取消了目录选择")
            print("用户取消了选择。视频下载已中止。")
            return False

        logger.info("调用 N_m3u8DL-RE 下载视频")
        download_success = self.n_m3u8dl_re.download(
            m3u8_file, save_name, save_dir, prefix, cookies_data, m3u8_headers
        )

        if download_success:
            self.saved_path = save_dir
            return True
        else:
            logger.error(f"视频下载失败 - 文件名: {save_name}")
            return False

    def _get_default_download_dir(self) -> str:
        """
        获取默认下载目录。

        返回项目根目录下的 Downloads 目录。

        Returns:
            默认下载目录路径
        """
        base_dir = os.getcwd()
        downloads_dir = os.path.join(base_dir, DEFAULT_DOWNLOAD_DIR)
        ensure_dir_exists(downloads_dir)
        logger.debug(f"默认下载目录: {downloads_dir}")
        return downloads_dir

    def _get_manual_download_dir(self) -> Optional[str]:
        """
        获取手动选择的下载目录。

        弹出文件选择对话框，让用户选择保存目录。

        Returns:
            用户选择的目录路径，如果用户取消则返回 None
        """
        root = tk.Tk()
        root.withdraw()
        save_dir = filedialog.askdirectory(title="选择保存视频的目录")
        root.destroy()
        logger.debug(f"用户选择的目录: {save_dir}")
        return save_dir

    def _continue_download(self) -> None:
        """
        继续下载新的钉钉直播回放链接。

        询问用户是否继续输入新的链接文件进行下载。
        """
        logger.info("进入继续下载循环")

        while True:
            continue_option = input(
                "是否继续输入钉钉直播回放链接表格路径进行下载？(按Enter继续，按q退出程序): "
            )
            if continue_option.lower() == "q":
                logger.info("用户选择退出程序")
                print("程序已退出。")
                self.close()
                break
            else:
                logger.info("用户选择继续下载")
                from ..utils.file_reader import FileReader

                file_path = input(
                    "请输入新的钉钉直播回放链接表格路径（支持CSV或Excel格式，可直接将文件拖放进窗口）: "
                )
                logger.info("用户已输入文件路径")

                new_links_dict = FileReader(file_path).read_links()
                logger.info(f"从文件中读取到 {len(new_links_dict)} 个链接")

                self.download_batch_videos(new_links_dict)

    def close(self) -> None:
        """
        关闭浏览器，释放资源。
        """
        logger.info("开始释放下载器资源")
        if self.cookie_handler:
            self.cookie_handler.close()
        logger.info("下载器资源释放完成")
