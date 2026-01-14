"""
钉钉直播回放下载工具 - 主程序入口

本模块是程序的入口，负责协调各模块。

作者：项目团队
依赖：无
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
"""

import sys
from typing import Dict
from .core.downloader import Downloader
from .utils.validator import validate_input
from .utils.file_reader import FileReader
from .config.constants import (
    BROWSER_OPTION_MAP,
    DOWNLOAD_MODE_MAP,
    SAVE_MODE_MAP,
    BROWSER_TYPE_EDGE,
    DOWNLOAD_MODE_SINGLE,
    DOWNLOAD_MODE_BATCH,
    SAVE_MODE_DEFAULT,
    SAVE_MODE_MANUAL
)


def single_mode() -> None:
    """
    单个视频下载模式。

    功能：
        - 获取用户输入（链接、保存模式、浏览器类型）
        - 调用下载器下载视频
        - 支持继续输入新链接

    输入：
        - 钉钉直播回放分享链接
        - 保存模式（1：默认路径，2：手动选择）
        - 浏览器类型（1：Edge，2：Chrome，3：Firefox）

    输出：
        - 下载的视频文件

    异常：
        - KeyboardInterrupt：用户中断
        - Exception：其他异常
    """
    try:
        dingtalk_url = input("请输入钉钉直播回放分享链接: ")
        save_mode = validate_input(
            "请选择保存模式（输入1：保存到程序默认路径，输入2：手动选择保存路径模式，直接回车默认选择1）: ",
            ['1', '2'],
            default_option='1'
        )
        browser_option = validate_input(
            "请选择您使用的浏览器（输入1：Edge，输入2：Chrome，输入3：Firefox，直接回车默认选择1）: ",
            ['1', '2', '3'],
            default_option='1'
        )

        browser_type = BROWSER_OPTION_MAP[browser_option]
        downloader = Downloader(browser_type, save_mode)
        downloader.download_single_video(dingtalk_url)

    except KeyboardInterrupt:
        print("\n程序已被用户终止。")
        sys.exit(0)

    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)


def batch_mode() -> None:
    """
    批量下载模式。

    功能：
        - 获取用户输入（文件路径、保存模式、浏览器类型）
        - 读取文件中的链接
        - 调用下载器批量下载视频
        - 支持继续输入新文件

    输入：
        - 文件路径（CSV/Excel）
        - 保存模式（1：默认路径，2：手动选择）
        - 浏览器类型（1：Edge，2：Chrome，3：Firefox）

    输出：
        - 下载的视频文件

    异常：
        - KeyboardInterrupt：用户中断
        - Exception：其他异常
    """
    try:
        file_path = input("请输入钉钉直播回放链接表格路径（支持CSV或Excel格式，可直接将文件拖放进窗口）: ")
        links_dict = FileReader(file_path).read_links()
        save_mode = validate_input(
            "请选择保存模式（输入1：保存到程序默认路径，输入2：手动选择保存路径模式，直接回车默认选择1）: ",
            ['1', '2'],
            default_option='1'
        )
        browser_option = validate_input(
            "请选择您使用的浏览器（输入1：Edge，输入2：Chrome，输入3：Firefox，直接回车默认选择1）: ",
            ['1', '2', '3'],
            default_option='1'
        )

        browser_type = BROWSER_OPTION_MAP[browser_option]
        downloader = Downloader(browser_type, save_mode)
        downloader.download_batch_videos(links_dict)

    except KeyboardInterrupt:
        print("\n程序已被用户终止。")
        sys.exit(0)

    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)


def main() -> None:
    """
    主程序入口。

    显示欢迎信息，获取用户输入的下载模式，调用相应的下载函数。
    """
    print("=" * 47)
    print("     欢迎使用钉钉直播回放下载工具 v1.3")
    print("         构建日期：2024年12月18日")
    print("=" * 47)

    try:
        download_mode = validate_input(
            "请选择下载模式（输入1：单个视频下载模式，输入2：批量下载模式，直接回车默认选择1）: ",
            ['1', '2'],
            default_option='1'
        )

        if download_mode == DOWNLOAD_MODE_SINGLE:
            single_mode()
        elif download_mode == DOWNLOAD_MODE_BATCH:
            batch_mode()

    except KeyboardInterrupt:
        print("\n程序已被用户终止。")
        sys.exit(0)

    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
