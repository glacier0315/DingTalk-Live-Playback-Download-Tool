"""主程序模块"""
import sys
from .browser import browser, get_browser_cookie, repeat_get_browser_cookie, close_browser
from .link_handler import read_links_file
from .m3u8_utils import fetch_m3u8_links, download_m3u8_file, extract_prefix
from .download_manager import auto_download_m3u8_with_options, download_m3u8_with_options, download_m3u8_with_reused_path
from .utils import validate_input


def repeat_process_links(new_links_dict, browser_obj, browser_type, save_mode):
    total_links = len(new_links_dict)
    print(f"共提取到 {total_links} 个新的钉钉直播回放分享链接。")

    saved_path = None
    for idx, dingtalk_url in new_links_dict.items():
        print(f"正在下载第 {idx + 1} 个视频，共 {total_links} 个视频。")
        cookies_data, m3u8_headers, live_name = repeat_get_browser_cookie(dingtalk_url)
        m3u8_links = fetch_m3u8_links(browser_obj, browser_type, dingtalk_url)

        if m3u8_links:
            for link in m3u8_links:
                m3u8_file = download_m3u8_file(link, 'output.m3u8', m3u8_headers)
                prefix = extract_prefix(link)
                save_name = live_name

                if save_mode == '1':
                    saved_path = auto_download_m3u8_with_options(m3u8_file, save_name, prefix, cookies_data, m3u8_headers)
                elif save_mode == '2':
                    saved_path = download_m3u8_with_reused_path(m3u8_file, save_name, prefix, saved_path, cookies_data, m3u8_headers)

        print('=' * 100)

    return saved_path


def continue_download(saved_path, browser_obj, browser_type):
    continue_option = input("是否继续输入钉钉直播回放链接表格路径进行下载？(按Enter继续，按q退出程序): ")
    if continue_option.lower() == 'q':
        print("程序已退出。")
        if browser_obj:
            close_browser()
        return False, saved_path
    else:
        file_path = input("请输入新的钉钉直播回放链接表格路径（支持CSV或Excel格式，可直接将文件拖放进窗口）: ")
        new_links_dict = read_links_file(file_path)
        print(f"共提取到 {len(new_links_dict)} 个新的钉钉直播回放分享链接。")
        saved_path = repeat_process_links(new_links_dict, browser_obj, browser_type, '1')
        return True, saved_path


def single_mode():
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

        browser_type = {'1': 'edge', '2': 'chrome', '3': 'firefox'}[browser_option]
        browser_obj, cookies_data, m3u8_headers, live_name = get_browser_cookie(dingtalk_url, browser_type)

        while True:
            m3u8_links = fetch_m3u8_links(browser_obj, browser_type, dingtalk_url)

            if m3u8_links:
                for link in m3u8_links:
                    m3u8_file = download_m3u8_file(link, 'output.m3u8', m3u8_headers)
                    prefix = extract_prefix(link)
                    save_name = live_name

                    if save_mode == '1':
                        auto_download_m3u8_with_options(m3u8_file, save_name, prefix, cookies_data, m3u8_headers)
                    elif save_mode == '2':
                        download_m3u8_with_options(m3u8_file, save_name, prefix, cookies_data, m3u8_headers)
            else:
                print("未找到包含 'm3u8' 字符的请求链接。")

            print('=' * 100)
            dingtalk_url = input("请继续输入钉钉直播分享链接，或输入q退出程序: ")
            if dingtalk_url.lower() == 'q':
                if browser_obj:
                    close_browser()
                print("程序已退出。")
                break
            cookies_data, m3u8_headers, live_name = repeat_get_browser_cookie(dingtalk_url)

    except KeyboardInterrupt:
        print("\n程序已被用户终止。")
        if browser:
            close_browser()
        sys.exit(0)

    except Exception as e:
        print(f"发生错误: {e}")
        if browser:
            close_browser()


def batch_mode():
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

        browser_type = {'1': 'edge', '2': 'chrome', '3': 'firefox'}[browser_option]
        total_links = len(links_dict)
        print(f"共提取到 {total_links} 个钉钉直播回放分享链接。")
        
        first_link = next(iter(links_dict.values()))
        browser_obj, cookies_data, m3u8_headers, live_name = get_browser_cookie(first_link, browser_type)
        print(f"正在下载第 1 个视频，共 {total_links} 个视频。")
        m3u8_links = fetch_m3u8_links(browser_obj, browser_type, first_link)

        saved_path = None

        if m3u8_links:
            for link in m3u8_links:
                m3u8_file = download_m3u8_file(link, 'output.m3u8', m3u8_headers)
                prefix = extract_prefix(link)
                save_name = live_name

                if save_mode == '1':
                    saved_path = auto_download_m3u8_with_options(m3u8_file, save_name, prefix, cookies_data, m3u8_headers)
                elif save_mode == '2':
                    saved_path = download_m3u8_with_reused_path(m3u8_file, save_name, prefix, saved_path, cookies_data, m3u8_headers)

        print('=' * 100)
        for idx, dingtalk_url in list(links_dict.items())[1:]:
            print(f"正在下载第 {idx + 1} 个视频，共 {total_links} 个视频。")
            cookies_data, m3u8_headers, live_name = repeat_get_browser_cookie(dingtalk_url)
            m3u8_links = fetch_m3u8_links(browser_obj, browser_type, dingtalk_url)

            if m3u8_links:
                for link in m3u8_links:
                    m3u8_file = download_m3u8_file(link, 'output.m3u8', m3u8_headers)
                    prefix = extract_prefix(link)
                    save_name = live_name

                    if save_mode == '1':
                        saved_path = auto_download_m3u8_with_options(m3u8_file, save_name, prefix, cookies_data, m3u8_headers)
                    elif save_mode == '2':
                        saved_path = download_m3u8_with_reused_path(m3u8_file, save_name, prefix, saved_path, cookies_data, m3u8_headers)
            print('=' * 100)

        while True:
            continue_option = input("是否继续输入钉钉直播回放链接表格路径进行下载？(按Enter继续，按q退出程序): ")
            if continue_option.lower() == 'q':
                print("程序已退出。")
                if browser_obj:
                    close_browser()
                break
            else:
                file_path = input("请输入新的钉钉直播回放链接表格路径（支持CSV或Excel格式，可直接将文件拖放进窗口）: ")
                new_links_dict = read_links_file(file_path)
                saved_path = repeat_process_links(new_links_dict, browser_obj, browser_type, save_mode)

    except KeyboardInterrupt:
        print("\n程序已被用户终止。")
        if browser:
            close_browser()
        sys.exit(0)

    except Exception as e:
        print(f"发生错误: {e}")
        if browser:
            close_browser()


def main():
    print("===============================================")
    print("     欢迎使用钉钉直播回放下载工具 v1.3")
    print("         构建日期：2024年12月18日")
    print("===============================================")

    try:
        download_mode = validate_input(
            "请选择下载模式（输入1：单个视频下载模式，输入2：批量下载模式，直接回车默认选择1）: ", 
            ['1', '2'], default_option='1'
        )
        if download_mode == '1':
            single_mode()
        elif download_mode == '2':
            batch_mode()

    except KeyboardInterrupt:
        print("\n程序已被用户终止。")
        if browser:
            close_browser()
        sys.exit(0)

    except Exception as e:
        print(f"发生错误: {e}")
        if browser:
            close_browser()
