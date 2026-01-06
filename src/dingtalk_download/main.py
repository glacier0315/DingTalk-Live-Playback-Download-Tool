"""主程序模块。

该模块提供钉钉直播回放下载工具的主入口点，包括：
- 单个视频下载模式
- 批量下载模式
- 用户交互界面
- 下载流程协调

该模块负责协调浏览器操作、链接处理、M3U8 下载和文件保存等各个模块的工作。
"""
import logging
import sys
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from .browser import browser, get_browser_cookie, repeat_get_browser_cookie, close_browser
from .link_handler import read_links_file
from .m3u8_utils import fetch_m3u8_links, download_m3u8_file, extract_prefix
from .download_manager import auto_download_m3u8_with_options, download_m3u8_with_options, download_m3u8_with_reused_path
from .utils import validate_input

if TYPE_CHECKING:
    from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver


logger = logging.getLogger(__name__)


APP_VERSION = "1.3"
BUILD_DATE = "2024年12月18日"
APP_NAME = "钉钉直播回放下载工具"
DEFAULT_M3U8_FILENAME = "output.m3u8"
BROWSER_TYPE_MAPPING = {
    '1': 'edge',
    '2': 'chrome',
    '3': 'firefox'
}
SEPARATOR_LINE = '=' * 100
EXIT_COMMAND = 'q'


def repeat_process_links(
    new_links_dict: Dict[int, str],
    browser_obj: 'RemoteWebDriver',
    browser_type: str,
    save_mode: str
) -> Optional[str]:
    """批量处理多个钉钉直播回放链接的下载。

    该函数遍历所有提供的链接，依次获取浏览器 Cookie、M3U8 链接，
    并根据保存模式下载视频文件。

    Args:
        new_links_dict: 包含钉钉直播回放链接的字典，键为索引，值为链接。
        browser_obj: 浏览器实例（Selenium WebDriver 对象）。
        browser_type: 浏览器类型，支持 'edge'、'chrome'、'firefox'。
        save_mode: 保存模式，'1' 表示保存到默认路径，'2' 表示手动选择路径。

    Returns:
        最后一个视频的保存路径。如果下载失败，则返回 None。

    Raises:
        ValueError: 如果链接字典为空或保存模式无效。
        RuntimeError: 如果下载过程中发生错误。

    Examples:
        >>> from selenium import webdriver
        >>> driver = webdriver.Edge()
        >>> links = {0: "https://n.dingtalk.com/live?liveUuid=abc123"}
        >>> path = repeat_process_links(links, driver, 'edge', '1')
        >>> print(path)
        'C:/Downloads/video.mp4'
    """
    if not new_links_dict:
        error_msg = "链接字典不能为空"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if save_mode not in ['1', '2']:
        error_msg = f"无效的保存模式: {save_mode}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    total_links = len(new_links_dict)
    logger.info(f"开始批量处理 {total_links} 个链接")

    saved_path: Optional[str] = None

    for idx, dingtalk_url in new_links_dict.items():
        logger.info(f"正在下载第 {idx + 1} 个视频，共 {total_links} 个视频")

        try:
            cookies_data, m3u8_headers, live_name = repeat_get_browser_cookie(dingtalk_url)
            m3u8_links = fetch_m3u8_links(browser_obj, browser_type, dingtalk_url)

            if m3u8_links:
                for link in m3u8_links:
                    m3u8_file = download_m3u8_file(link, DEFAULT_M3U8_FILENAME, m3u8_headers)
                    prefix = extract_prefix(link)
                    save_name = live_name

                    if save_mode == '1':
                        saved_path = auto_download_m3u8_with_options(
                            m3u8_file, save_name, prefix, cookies_data, m3u8_headers
                        )
                    elif save_mode == '2':
                        saved_path = download_m3u8_with_reused_path(
                            m3u8_file, save_name, prefix, saved_path, cookies_data, m3u8_headers
                        )

                    logger.info(f"视频下载完成: {save_name}")
            else:
                logger.warning(f"未找到 {dingtalk_url} 的 M3U8 链接")

            logger.info(SEPARATOR_LINE)

        except Exception as e:
            error_msg = f"处理链接 {dingtalk_url} 时发生错误: {e}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e

    logger.info(f"批量处理完成，共处理 {total_links} 个链接")
    return saved_path


def continue_download(
    saved_path: Optional[str],
    browser_obj: Optional['RemoteWebDriver'],
    browser_type: str
) -> Tuple[bool, Optional[str]]:
    """询问用户是否继续下载并处理新的链接文件。

    该函数询问用户是否要继续下载新的视频链接，如果用户选择继续，
    则读取新的链接文件并处理下载。

    Args:
        saved_path: 上一个视频的保存路径。
        browser_obj: 浏览器实例（Selenium WebDriver 对象）。
        browser_type: 浏览器类型，支持 'edge'、'chrome'、'firefox'。

    Returns:
        一个元组，包含两个元素：
        - 第一个元素为布尔值，表示是否继续下载（True 表示继续，False 表示退出）
        - 第二个元素为字符串或 None，表示最新的保存路径

    Examples:
        >>> from selenium import webdriver
        >>> driver = webdriver.Edge()
        >>> should_continue, path = continue_download(None, driver, 'edge')
        >>> print(should_continue)
        False
    """
    continue_option = input("是否继续输入钉钉直播回放链接表格路径进行下载？(按Enter继续，按q退出程序): ")

    if continue_option.lower() == EXIT_COMMAND:
        logger.info("用户选择退出程序")
        print("程序已退出。")
        if browser_obj:
            close_browser()
        return False, saved_path

    try:
        file_path = input("请输入新的钉钉直播回放链接表格路径（支持CSV或Excel格式，可直接将文件拖放进窗口）: ")
        new_links_dict = read_links_file(file_path)
        logger.info(f"共提取到 {len(new_links_dict)} 个新的钉钉直播回放分享链接")
        saved_path = repeat_process_links(new_links_dict, browser_obj, browser_type, '1')
        return True, saved_path

    except Exception as e:
        error_msg = f"继续下载时发生错误: {e}"
        logger.error(error_msg, exc_info=True)
        print(f"发生错误: {e}")
        return False, saved_path


def _download_single_video(
    dingtalk_url: str,
    browser_obj: 'RemoteWebDriver',
    browser_type: str,
    save_mode: str,
    cookies_data: Dict[str, str],
    m3u8_headers: Dict[str, str],
    live_name: str
) -> None:
    """下载单个钉钉直播回放视频。

    该函数获取 M3U8 链接并下载视频文件。

    Args:
        dingtalk_url: 钉钉直播回放分享链接。
        browser_obj: 浏览器实例（Selenium WebDriver 对象）。
        browser_type: 浏览器类型，支持 'edge'、'chrome'、'firefox'。
        save_mode: 保存模式，'1' 表示保存到默认路径，'2' 表示手动选择路径。
        cookies_data: 浏览器 Cookie 数据。
        m3u8_headers: M3U8 请求头。
        live_name: 直播名称。

    Raises:
        RuntimeError: 如果下载过程中发生错误。
    """
    logger.info(f"开始下载视频: {live_name}")

    m3u8_links = fetch_m3u8_links(browser_obj, browser_type, dingtalk_url)

    if m3u8_links:
        for link in m3u8_links:
            m3u8_file = download_m3u8_file(link, DEFAULT_M3U8_FILENAME, m3u8_headers)
            prefix = extract_prefix(link)
            save_name = live_name

            if save_mode == '1':
                auto_download_m3u8_with_options(m3u8_file, save_name, prefix, cookies_data, m3u8_headers)
            elif save_mode == '2':
                download_m3u8_with_options(m3u8_file, save_name, prefix, cookies_data, m3u8_headers)

            logger.info(f"视频下载完成: {save_name}")
    else:
        logger.warning(f"未找到包含 'm3u8' 字符的请求链接")
        print("未找到包含 'm3u8' 字符的请求链接。")


def single_mode() -> None:
    """单个视频下载模式。

    该模式允许用户逐个输入钉钉直播回放链接并下载视频。
    用户可以选择保存模式和浏览器类型。

    该函数会循环提示用户输入链接，直到用户输入退出命令。

    Raises:
        KeyboardInterrupt: 如果用户按下 Ctrl+C 终止程序。
        Exception: 如果下载过程中发生错误。
    """
    logger.info("进入单个视频下载模式")

    try:
        dingtalk_url = input("请输入钉钉直播回放分享链接: ")
        save_mode = validate_input(
            "请选择保存模式（输入1：保存到程序默认路径，输入2：手动选择保存路径模式，直接回车默认选择1）: ",
            ['1', '2'], default_option='1'
        )
        browser_option = validate_input(
            "请选择您使用的浏览器（输入1：Edge，输入2：Chrome，输入3：Firefox，直接回车默认选择1）: ",
            ['1', '2', '3'], default_option='1'
        )

        browser_type = BROWSER_TYPE_MAPPING[browser_option]
        browser_obj, cookies_data, m3u8_headers, live_name = get_browser_cookie(dingtalk_url, browser_type)

        while True:
            try:
                _download_single_video(
                    dingtalk_url, browser_obj, browser_type, save_mode,
                    cookies_data, m3u8_headers, live_name
                )

                logger.info(SEPARATOR_LINE)
                dingtalk_url = input("请继续输入钉钉直播分享链接，或输入q退出程序: ")

                if dingtalk_url.lower() == EXIT_COMMAND:
                    logger.info("用户选择退出程序")
                    if browser_obj:
                        close_browser()
                    print("程序已退出。")
                    break

                cookies_data, m3u8_headers, live_name = repeat_get_browser_cookie(dingtalk_url)

            except Exception as e:
                error_msg = f"下载视频时发生错误: {e}"
                logger.error(error_msg, exc_info=True)
                print(f"发生错误: {e}")
                dingtalk_url = input("请继续输入钉钉直播分享链接，或输入q退出程序: ")

                if dingtalk_url.lower() == EXIT_COMMAND:
                    logger.info("用户选择退出程序")
                    if browser_obj:
                        close_browser()
                    print("程序已退出。")
                    break

                cookies_data, m3u8_headers, live_name = repeat_get_browser_cookie(dingtalk_url)

    except KeyboardInterrupt:
        logger.info("程序被用户终止")
        print("\n程序已被用户终止。")
        if browser:
            close_browser()
        sys.exit(0)

    except Exception as e:
        error_msg = f"单个视频下载模式发生错误: {e}"
        logger.error(error_msg, exc_info=True)
        print(f"发生错误: {e}")
        if browser:
            close_browser()


def _download_batch_video(
    dingtalk_url: str,
    browser_obj: 'RemoteWebDriver',
    browser_type: str,
    save_mode: str,
    saved_path: Optional[str]
) -> Optional[str]:
    """下载批量模式中的单个视频。

    该函数获取 M3U8 链接并下载视频文件，用于批量下载模式。

    Args:
        dingtalk_url: 钉钉直播回放分享链接。
        browser_obj: 浏览器实例（Selenium WebDriver 对象）。
        browser_type: 浏览器类型，支持 'edge'、'chrome'、'firefox'。
        save_mode: 保存模式，'1' 表示保存到默认路径，'2' 表示手动选择路径。
        saved_path: 上一个视频的保存路径。

    Returns:
        当前视频的保存路径。如果下载失败，则返回 None。

    Raises:
        RuntimeError: 如果下载过程中发生错误。
    """
    cookies_data, m3u8_headers, live_name = repeat_get_browser_cookie(dingtalk_url)
    m3u8_links = fetch_m3u8_links(browser_obj, browser_type, dingtalk_url)

    if m3u8_links:
        for link in m3u8_links:
            m3u8_file = download_m3u8_file(link, DEFAULT_M3U8_FILENAME, m3u8_headers)
            prefix = extract_prefix(link)
            save_name = live_name

            if save_mode == '1':
                saved_path = auto_download_m3u8_with_options(
                    m3u8_file, save_name, prefix, cookies_data, m3u8_headers
                )
            elif save_mode == '2':
                saved_path = download_m3u8_with_reused_path(
                    m3u8_file, save_name, prefix, saved_path, cookies_data, m3u8_headers
                )

            logger.info(f"视频下载完成: {save_name}")

    return saved_path


def batch_mode() -> None:
    """批量下载模式。

    该模式允许用户从 CSV 或 Excel 文件中读取多个钉钉直播回放链接并批量下载。
    用户可以选择保存模式和浏览器类型。

    该函数会循环处理所有链接，并询问用户是否继续下载新的文件。

    Raises:
        KeyboardInterrupt: 如果用户按下 Ctrl+C 终止程序。
        Exception: 如果下载过程中发生错误。
    """
    logger.info("进入批量下载模式")

    try:
        file_path = input("请输入钉钉直播回放链接表格路径（支持CSV或Excel格式，可直接将文件拖放进窗口）: ")
        links_dict = read_links_file(file_path)

        save_mode = validate_input(
            "请选择保存模式（输入1：保存到程序默认路径，输入2：手动选择保存路径模式，直接回车默认选择1）: ",
            ['1', '2'], default_option='1'
        )
        browser_option = validate_input(
            "请选择您使用的浏览器（输入1：Edge，输入2：Chrome，输入3：Firefox，直接回车默认选择1）: ",
            ['1', '2', '3'], default_option='1'
        )

        browser_type = BROWSER_TYPE_MAPPING[browser_option]
        total_links = len(links_dict)
        logger.info(f"共提取到 {total_links} 个钉钉直播回放分享链接")
        print(f"共提取到 {total_links} 个钉钉直播回放分享链接。")

        first_link = next(iter(links_dict.values()))
        browser_obj, cookies_data, m3u8_headers, live_name = get_browser_cookie(first_link, browser_type)

        logger.info(f"正在下载第 1 个视频，共 {total_links} 个视频")
        print(f"正在下载第 1 个视频，共 {total_links} 个视频。")

        saved_path = _download_batch_video(first_link, browser_obj, browser_type, save_mode, None)
        logger.info(SEPARATOR_LINE)
        print(SEPARATOR_LINE)

        for idx, dingtalk_url in list(links_dict.items())[1:]:
            logger.info(f"正在下载第 {idx + 1} 个视频，共 {total_links} 个视频")
            print(f"正在下载第 {idx + 1} 个视频，共 {total_links} 个视频。")

            try:
                saved_path = _download_batch_video(dingtalk_url, browser_obj, browser_type, save_mode, saved_path)
            except Exception as e:
                error_msg = f"下载第 {idx + 1} 个视频时发生错误: {e}"
                logger.error(error_msg, exc_info=True)
                print(f"发生错误: {e}")

            logger.info(SEPARATOR_LINE)
            print(SEPARATOR_LINE)

        while True:
            should_continue, saved_path = continue_download(saved_path, browser_obj, browser_type)
            if not should_continue:
                break

    except KeyboardInterrupt:
        logger.info("程序被用户终止")
        print("\n程序已被用户终止。")
        if browser:
            close_browser()
        sys.exit(0)

    except Exception as e:
        error_msg = f"批量下载模式发生错误: {e}"
        logger.error(error_msg, exc_info=True)
        print(f"发生错误: {e}")
        if browser:
            close_browser()


def _print_welcome_message() -> None:
    """打印欢迎消息。

    该函数显示应用程序的名称、版本和构建日期。
    """
    print("=" * 47)
    print(f"     欢迎使用{APP_NAME} v{APP_VERSION}")
    print(f"         构建日期：{BUILD_DATE}")
    print("=" * 47)


def main() -> None:
    """主程序入口点。

    该函数是应用程序的入口点，负责：
    1. 显示欢迎消息
    2. 询问用户选择下载模式
    3. 调用相应的下载模式函数
    4. 处理异常和用户中断

    支持的下载模式：
    - 单个视频下载模式（模式 1）
    - 批量下载模式（模式 2）

    Raises:
        KeyboardInterrupt: 如果用户按下 Ctrl+C 终止程序。
        Exception: 如果程序运行过程中发生错误。
    """
    logger.info("程序启动")
    _print_welcome_message()

    try:
        download_mode = validate_input(
            "请选择下载模式（输入1：单个视频下载模式，输入2：批量下载模式，直接回车默认选择1）: ",
            ['1', '2'], default_option='1'
        )

        if download_mode == '1':
            logger.info("用户选择单个视频下载模式")
            single_mode()
        elif download_mode == '2':
            logger.info("用户选择批量下载模式")
            batch_mode()

    except KeyboardInterrupt:
        logger.info("程序被用户终止")
        print("\n程序已被用户终止。")
        if browser:
            close_browser()
        sys.exit(0)

    except Exception as e:
        error_msg = f"主程序发生错误: {e}"
        logger.error(error_msg, exc_info=True)
        print(f"发生错误: {e}")
        if browser:
            close_browser()


if __name__ == "__main__":
    main()
