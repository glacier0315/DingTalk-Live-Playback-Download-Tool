"""M3U8文件处理模块"""
import re
from urllib.parse import urlparse, parse_qs
from . import browser


def extract_prefix(url):
    pattern = re.compile(r'(https?://[^/]+/live_hp/[0-9a-f-]+)')
    match = pattern.search(url)
    return match.group(1) if match else url


def fetch_m3u8_links(browser, browser_type, dingtalk_url):
    m3u8_links = []
    live_uuid = extract_live_uuid(dingtalk_url)

    if not live_uuid:
        print("未能从 URL 提取 liveUuid，程序将退出。")
        return None

    for attempt in range(5):
        try:
            if browser_type == 'chrome' or browser_type == 'edge':
                logs = browser.get_log("performance")
            elif browser_type == 'firefox':
                logs = browser.execute_script("""
                    var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {};
                    var network = performance.getEntries() || {};
                    return network;
                """)

            for log in logs:
                try:
                    if browser_type == 'firefox':
                        log_message = str(log)
                        pattern = r'https://[^,\'"]+\.m3u8\?[^\'"]+'
                        found_links = re.findall(pattern, log_message)

                        if found_links:
                            cleaned_link = re.sub(r'[\]\s\\\'"]+$', '', found_links[0])
                            m3u8_links.append(cleaned_link)
                            print(f"获取到m3u8链接: {cleaned_link}")
                            return m3u8_links

                    else:
                        if 'message' in log:
                            log_message = log['message']
                        else:
                            log_message = str(log)

                        if '.m3u8' in log_message:
                            start_idx = log_message.find("url\":\"") + len("url\":\"")
                            end_idx = log_message.find("\"", start_idx)
                            m3u8_url = log_message[start_idx:end_idx]

                            if live_uuid in m3u8_url:
                                print(f"获取到m3u8链接: {m3u8_url}")
                                m3u8_links.append(m3u8_url)
                                return m3u8_links

                except Exception as e:
                    print(f"处理日志时发生错误: {e}")

            print(f"第 {attempt + 1} 次尝试未获取到 m3u8 链接，重试中...")
            refresh_page_by_click(browser)

        except Exception as e:
            print(f"获取 m3u8 链接时发生错误: {e}")
    
    return None


def download_m3u8_file(url: str, filename: str, headers: dict) -> str:
    """
    下载 M3U8 文件内容并保存到本地
    
    Args:
        url: M3U8 文件 URL
        filename: 本地保存文件名
        headers: 请求头字典
    
    Returns:
        保存的文件名
    
    Raises:
        ValueError: 如果参数无效
        PermissionError: 如果文件写入权限不足
        RuntimeError: 如果下载或保存失败
    """
    import os
    
    # 参数验证
    if not url:
        raise ValueError("URL 不能为空")
    
    if not filename:
        raise ValueError("文件名不能为空")
    
    if not headers:
        raise ValueError("请求头不能为空")
    
    # 检查文件目录是否存在
    file_dir = os.path.dirname(filename)
    if file_dir and not os.path.exists(file_dir):
        try:
            os.makedirs(file_dir, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"创建目录失败: {file_dir}") from e
    
    # 检查文件写入权限
    if file_dir and not os.access(file_dir, os.W_OK):
        raise PermissionError(f"目录不可写: {file_dir}")
    
    try:
        m3u8_content = browser.browser.execute_script(
            "return fetch(arguments[0], { method: 'GET', headers: arguments[1] }).then(response => response.text())", 
            url
        )
        
        if not m3u8_content:
            raise RuntimeError("下载的 M3U8 内容为空")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(m3u8_content)
        
        return filename
    
    except Exception as e:
        if isinstance(e, (ValueError, PermissionError, RuntimeError)):
            raise
        raise RuntimeError(f"下载 M3U8 文件失败: {e}") from e


def refresh_page_by_click(browser):
    try:
        browser.execute_script("location.reload();")
        print("页面已刷新")
    except Exception as e:
        print(f"刷新页面时发生错误: {e}")


def extract_live_uuid(dingtalk_url):
    parsed_url = urlparse(dingtalk_url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get('liveUuid', [None])[0]
