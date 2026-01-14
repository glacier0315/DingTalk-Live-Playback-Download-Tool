"""
钉钉直播回放下载工具 - 下载器核心模块

本模块负责协调 Cookie 获取、m3u8 解析、视频下载。

作者：项目团队
依赖：无
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
"""

import sys
import os
import tkinter as tk
from tkinter import filedialog
from typing import Dict, Optional
from ..core.cookie_handler import CookieHandler
from ..core.m3u8_parser import M3u8Parser
from ..binary.n_m3u8dl_re import NM3u8DLRE
from ..utils.path_helper import ensure_dir_exists
from ..config.constants import SAVE_MODE_DEFAULT, SAVE_MODE_MANUAL, DEFAULT_DOWNLOAD_DIR, TEMP_M3U8_FILE


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

    def download_single_video(self, url: str) -> None:
        """
        下载单个视频。

        协调 Cookie 获取、m3u8 解析、视频下载。

        Args:
            url: 钉钉直播回放分享链接

        Raises:
            Exception: 下载失败时
        """
        try:
            browser, cookies_data, m3u8_headers, live_name = self.cookie_handler.get_cookie(url)
            self.m3u8_parser = M3u8Parser(browser, self.browser_type)

            while True:
                m3u8_links = self.m3u8_parser.fetch_m3u8_links(url)

                if m3u8_links:
                    for link in m3u8_links:
                        m3u8_file = self.m3u8_parser.download_m3u8_file(link, TEMP_M3U8_FILE, m3u8_headers)
                        prefix = self.m3u8_parser.extract_prefix(link)
                        self._download_video(m3u8_file, live_name, prefix, cookies_data, m3u8_headers)
                else:
                    print("未找到包含 'm3u8' 字符的请求链接。")

                print('=' * 100)
                url = input("请继续输入钉钉直播分享链接，或输入q退出程序: ")
                if url.lower() == 'q':
                    self.close()
                    print("程序已退出。")
                    break
                cookies_data, m3u8_headers, live_name = self.cookie_handler.repeat_get_cookie(url)

        except KeyboardInterrupt:
            print("\n程序已被用户终止。")
            self.close()
            sys.exit(0)

        except Exception as e:
            print(f"发生错误: {e}")
            self.close()

    def download_batch_videos(self, urls: Dict[int, str]) -> None:
        """
        批量下载视频。

        协调 Cookie 获取、m3u8 解析、视频下载。

        Args:
            urls: 链接字典 {index: url}

        Raises:
            Exception: 下载失败时
        """
        try:
            total_links = len(urls)
            print(f"共提取到 {total_links} 个钉钉直播回放分享链接。")

            first_link = next(iter(urls.values()))
            browser, cookies_data, m3u8_headers, live_name = self.cookie_handler.get_cookie(first_link)
            self.m3u8_parser = M3u8Parser(browser, self.browser_type)

            print(f"正在下载第 1 个视频，共 {total_links} 个视频。")
            m3u8_links = self.m3u8_parser.fetch_m3u8_links(first_link)

            if m3u8_links:
                for link in m3u8_links:
                    m3u8_file = self.m3u8_parser.download_m3u8_file(link, TEMP_M3U8_FILE, m3u8_headers)
                    prefix = self.m3u8_parser.extract_prefix(link)
                    self._download_video(m3u8_file, live_name, prefix, cookies_data, m3u8_headers)

            print('=' * 100)

            for idx, dingtalk_url in list(urls.items())[1:]:
                print(f"正在下载第 {idx + 1} 个视频，共 {total_links} 个视频。")
                cookies_data, m3u8_headers, live_name = self.cookie_handler.repeat_get_cookie(dingtalk_url)
                m3u8_links = self.m3u8_parser.fetch_m3u8_links(dingtalk_url)

                if m3u8_links:
                    for link in m3u8_links:
                        m3u8_file = self.m3u8_parser.download_m3u8_file(link, TEMP_M3U8_FILE, m3u8_headers)
                        prefix = self.m3u8_parser.extract_prefix(link)
                        self._download_video(m3u8_file, live_name, prefix, cookies_data, m3u8_headers)
                print('=' * 100)

            self._continue_download()

        except KeyboardInterrupt:
            print("\n程序已被用户终止。")
            self.close()
            sys.exit(0)

        except Exception as e:
            print(f"发生错误: {e}")
            self.close()

    def _download_video(self, m3u8_file: str, save_name: str, prefix: str,
                     cookies_data: Dict[str, str], m3u8_headers: Dict[str, str]) -> None:
        """
        下载视频。

        根据保存模式选择保存路径，然后调用 N_m3u8DL-RE 下载视频。

        Args:
            m3u8_file: m3u8 文件路径
            save_name: 保存文件名
            prefix: 基础 URL
            cookies_data: Cookie 字典
            m3u8_headers: 请求头字典
        """
        if self.save_mode == SAVE_MODE_DEFAULT:
            save_dir = self._get_default_download_dir()
        elif self.save_mode == SAVE_MODE_MANUAL:
            save_dir = self._get_manual_download_dir()
        else:
            print("无效的保存模式")
            return

        if not save_dir:
            print("用户取消了选择。视频下载已中止。")
            return

        self.n_m3u8dl_re.download(m3u8_file, save_name, save_dir, prefix, cookies_data, m3u8_headers)
        self.saved_path = save_dir

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
        return save_dir

    def _continue_download(self) -> None:
        """
        继续下载新的钉钉直播回放链接。

        询问用户是否继续输入新的链接文件进行下载。
        """
        while True:
            continue_option = input("是否继续输入钉钉直播回放链接表格路径进行下载？(按Enter继续，按q退出程序): ")
            if continue_option.lower() == 'q':
                print("程序已退出。")
                self.close()
                break
            else:
                from ..utils.file_reader import FileReader
                file_path = input("请输入新的钉钉直播回放链接表格路径（支持CSV或Excel格式，可直接将文件拖放进窗口）: ")
                new_links_dict = FileReader(file_path).read_links()
                self.download_batch_videos(new_links_dict)

    def close(self) -> None:
        """
        关闭浏览器，释放资源。
        """
        if self.cookie_handler:
            self.cookie_handler.close()
