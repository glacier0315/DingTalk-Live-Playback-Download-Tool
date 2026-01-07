"""M3U8 文件处理模块。

该模块提供了从钉钉直播页面提取 M3U8 链接、下载 M3U8 文件内容等功能。
支持多种浏览器类型（Chrome、Edge、Firefox）的日志解析。

主要功能：
- 从钉钉直播 URL 提取基础 URL 前缀
- 从浏览器性能日志中提取 M3U8 链接
- 下载 M3U8 文件内容到本地
- 刷新页面以重新获取资源

Example:
    >>> from dingtalk_download import m3u8_utils, browser
    >>> 
    >>> # 创建浏览器实例
    >>> br = browser.create_browser('edge')
    >>> 
    >>> # 提取 URL 前缀
    >>> url = "https://n.dingtalk.com/live_hp/abc123/video.m3u8"
    >>> prefix = m3u8_utils.extract_prefix(url)
    >>> print(prefix)
    'https://n.dingtalk.com/live_hp/abc123'
    >>> 
    >>> # 获取 M3U8 链接
    >>> dingtalk_url = "https://n.dingtalk.com/live?liveUuid=abc123"
    >>> m3u8_links = m3u8_utils.fetch_m3u8_links(br, 'edge', dingtalk_url)
    >>> print(m3u8_links)
    ['https://n.dingtalk.com/live_hp/abc123/video.m3u8']
"""

import json
import logging
import os
import re
import time
from typing import Dict, List, Optional
from urllib.parse import parse_qs, urlparse

import requests

from . import browser

logger = logging.getLogger(__name__)

# 常量定义
MAX_RETRY_ATTEMPTS = 5
M3U8_FILE_EXTENSION = ".m3u8"
FIREFOX_NETWORK_LOG_SCRIPT = """
    var performance = window.performance || window.mozPerformance || 
                      window.msPerformance || window.webkitPerformance || {};
    var network = performance.getEntries() || {};
    return network;
"""

# 支持的浏览器类型
SUPPORTED_BROWSER_TYPES = ['chrome', 'edge', 'firefox']


def extract_prefix(url: str) -> str:
    """从 URL 中提取基础前缀。

    该函数从钉钉直播 URL 中提取基础 URL 前缀，用于后续构建完整的 M3U8 下载链接。
    前缀格式为：https://域名/live_hp/UUID

    Args:
        url: 完整的钉钉直播 URL。

    Returns:
        提取的基础 URL 前缀。如果无法匹配模式，则返回原始 URL。

    Raises:
        ValueError: 如果 URL 为空或不是字符串类型。

    Examples:
        >>> extract_prefix("https://n.dingtalk.com/live_hp/abc123-def456/video.m3u8")
        'https://n.dingtalk.com/live_hp/abc123-def456'
        >>> extract_prefix("https://example.com/video.m3u8")
        'https://example.com/video.m3u8'
    """
    logger.debug(f"extract_prefix called with url='{url}'")

    if not url:
        error_msg = "URL 不能为空"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if not isinstance(url, str):
        error_msg = f"URL 必须是字符串类型，实际类型: {type(url)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    pattern = re.compile(r'(https?://[^/]+/live_hp/[0-9a-f-]+)')
    match = pattern.search(url)

    if match:
        prefix = match.group(1)
        logger.debug(f"提取到 URL 前缀: {prefix}")
        return prefix
    else:
        logger.debug(f"无法匹配 URL 模式，返回原始 URL: {url}")
        return url


def extract_live_uuid(dingtalk_url: str) -> Optional[str]:
    """从钉钉直播 URL 中提取 liveUuid 参数。

    该函数解析钉钉直播 URL 的查询参数，提取 liveUuid 参数值。
    liveUuid 是钉钉直播的唯一标识符。

    Args:
        dingtalk_url: 钉钉直播 URL。

    Returns:
        提取的 liveUuid 参数值。如果 URL 中不包含该参数，则返回 None。

    Raises:
        ValueError: 如果 URL 为空或不是字符串类型。

    Examples:
        >>> extract_live_uuid("https://n.dingtalk.com/live?liveUuid=abc123-def456")
        'abc123-def456'
        >>> extract_live_uuid("https://n.dingtalk.com/live")
        None
    """
    logger.debug(f"extract_live_uuid called with url='{dingtalk_url}'")

    if not dingtalk_url:
        error_msg = "钉钉 URL 不能为空"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if not isinstance(dingtalk_url, str):
        error_msg = f"钉钉 URL 必须是字符串类型，实际类型: {type(dingtalk_url)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    parsed_url = urlparse(dingtalk_url)
    query_params = parse_qs(parsed_url.query)
    live_uuid = query_params.get('liveUuid', [None])[0]

    if live_uuid:
        logger.debug(f"提取到 liveUuid: {live_uuid}")
    else:
        logger.debug("URL 中未找到 liveUuid 参数")

    return live_uuid


def refresh_page_by_click(browser_instance: browser.webdriver.Remote) -> None:
    """通过 JavaScript 刷新浏览器页面。

    该函数使用浏览器的 execute_script 方法执行 JavaScript 代码来刷新页面。
    这是一种更可靠的页面刷新方式，特别是在某些自动化场景中。

    Args:
        browser_instance: 浏览器实例（Selenium WebDriver 对象）。

    Raises:
        RuntimeError: 如果刷新页面时发生错误。

    Examples:
        >>> from selenium import webdriver
        >>> driver = webdriver.Edge()
        >>> driver.get("https://example.com")
        >>> refresh_page_by_click(driver)
        >>> # 页面已刷新
    """
    logger.info("开始刷新页面")

    try:
        browser_instance.execute_script("location.reload();")
        logger.info("页面刷新成功")
    except Exception as e:
        error_msg = f"刷新页面时发生错误: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e


def _validate_browser_type(browser_type: str) -> None:
    """验证浏览器类型是否支持。

    Args:
        browser_type: 浏览器类型字符串。

    Raises:
        ValueError: 如果浏览器类型不支持。
    """
    if browser_type not in SUPPORTED_BROWSER_TYPES:
        error_msg = f"不支持的浏览器类型: {browser_type}. 支持的类型: {', '.join(SUPPORTED_BROWSER_TYPES)}"
        logger.error(error_msg)
        raise ValueError(error_msg)


def _try_play_video(browser_instance: browser.webdriver.Remote) -> bool:
    """尝试点击播放按钮以触发视频加载。

    Args:
        browser_instance: 浏览器实例。

    Returns:
        如果成功触发视频播放则返回 True，否则返回 False。
    """
    try:
        from selenium.webdriver.common.by import By
        
        logger.info("尝试触发视频播放...")
        
        try:
            video_element = browser_instance.find_element(By.TAG_NAME, "video")
            browser_instance.execute_script("arguments[0].play();", video_element)
            logger.info("成功触发视频播放")
            print("🎬 已尝试触发视频播放")
            return True
        except Exception as e:
            logger.warning(f"通过 video 标签触发播放失败: {e}")
        
        try:
            play_button = browser_instance.find_element(By.CSS_SELECTOR, "[class*='play'], [class*='Play']")
            play_button.click()
            logger.info("成功点击播放按钮")
            print("🎬 已尝试点击播放按钮")
            return True
        except Exception as e:
            logger.warning(f"点击播放按钮失败: {e}")
        
        logger.info("未能触发视频播放，可能视频已在播放或需要手动操作")
        return False
    
    except Exception as e:
        logger.warning(f"尝试触发视频播放时发生错误: {e}")
        return False


def _get_browser_logs(
    browser_instance: browser.webdriver.Remote,
    browser_type: str
) -> List:
    """根据浏览器类型获取日志。

    Args:
        browser_instance: 浏览器实例。
        browser_type: 浏览器类型。

    Returns:
        日志列表。不同浏览器返回的日志格式不同。

    Raises:
        RuntimeError: 如果获取日志失败。
    """
    logger.debug(f"获取 {browser_type} 浏览器日志")

    try:
        if browser_type in ['chrome', 'edge']:
            logs = browser_instance.get_log("performance")
            logger.debug(f"获取到 {len(logs)} 条性能日志")
            return logs
        elif browser_type == 'firefox':
            logs = browser_instance.execute_script(FIREFOX_NETWORK_LOG_SCRIPT)
            logger.debug(f"获取到 {len(logs)} 条网络日志")
            return logs
        else:
            error_msg = f"不支持的浏览器类型: {browser_type}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"获取浏览器日志失败: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e


def _save_logs_for_debugging(
    logs: List,
    browser_type: str,
    attempt: int,
    live_uuid: Optional[str] = None
) -> None:
    """保存日志到文件用于调试。

    Args:
        logs: 日志列表。
        browser_type: 浏览器类型。
        attempt: 尝试次数。
        live_uuid: 直播 UUID（可选）。
    """
    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"Logs/browser_logs_{browser_type}_attempt{attempt}_{timestamp}.json"
        
        os.makedirs("Logs", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'browser_type': browser_type,
                'attempt': attempt,
                'live_uuid': live_uuid,
                'log_count': len(logs),
                'logs': logs[:100] if len(logs) > 100 else logs
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"日志已保存到: {filename}")
        print(f"💾 日志已保存到: {filename}")
    except Exception as e:
        logger.error(f"保存日志失败: {e}")


def _parse_firefox_log(log_message: str) -> Optional[str]:
    """解析 Firefox 浏览器的日志消息，提取 M3U8 链接。

    Args:
        log_message: Firefox 日志消息字符串。

    Returns:
        提取的 M3U8 链接，如果未找到则返回 None。
    """
    pattern = rf'https://[^,\'"]+{re.escape(M3U8_FILE_EXTENSION)}\?[^\'"]+'
    found_links = re.findall(pattern, log_message)

    if found_links:
        cleaned_link = re.sub(r'[\]\s\\\'"]+$', '', found_links[0])
        logger.debug(f"从 Firefox 日志中提取到 M3U8 链接: {cleaned_link}")
        return cleaned_link

    return None


def _parse_chrome_edge_log(log_message: str, live_uuid: str) -> Optional[str]:
    """解析 Chrome 或 Edge 浏览器的日志消息，提取 M3U8 链接。

    Args:
        log_message: Chrome 或 Edge 日志消息字符串。
        live_uuid: 直播 UUID，用于验证链接的有效性。

    Returns:
        提取的 M3U8 链接，如果未找到或 UUID 不匹配则返回 None。
    """
    if M3U8_FILE_EXTENSION not in log_message:
        return None

    try:
        log_data = json.loads(log_message)
        
        if 'message' not in log_data:
            return None
        
        message = log_data['message']
        if 'params' not in message:
            return None
        
        params = message['params']
        
        m3u8_url = None
        
        if 'request' in params and 'url' in params['request']:
            m3u8_url = params['request']['url']
        elif 'response' in params and 'url' in params['response']:
            m3u8_url = params['response']['url']

        if m3u8_url and live_uuid in m3u8_url:
            logger.info(f"从 Chrome/Edge 日志中提取到 M3U8 链接: {m3u8_url}")
            return m3u8_url
        elif m3u8_url:
            logger.debug(f"找到的 M3U8 链接不包含 liveUuid: {live_uuid}")
            return None
        else:
            return None

    except Exception as e:
        logger.warning(f"解析 Chrome/Edge 日志时发生错误: {e}")
        return None


def _process_log_entry(
    log: Dict,
    browser_type: str,
    live_uuid: str
) -> Optional[str]:
    """处理单个日志条目，尝试提取 M3U8 链接。

    Args:
        log: 日志条目（字典或字符串）。
        browser_type: 浏览器类型。
        live_uuid: 直播 UUID。

    Returns:
        提取的 M3U8 链接，如果未找到则返回 None。
    """
    try:
        if browser_type == 'firefox':
            log_message = str(log)
            logger.debug(f"处理 Firefox 日志条目，长度: {len(log_message)}")
            return _parse_firefox_log(log_message)
        else:
            if isinstance(log, dict) and 'message' in log:
                log_message = log['message']
                logger.debug(f"处理 Chrome/Edge 日志条目，message 长度: {len(log_message)}")
            else:
                log_message = str(log)
                logger.debug(f"处理 Chrome/Edge 日志条目（非字典），长度: {len(log_message)}")

            return _parse_chrome_edge_log(log_message, live_uuid)

    except Exception as e:
        logger.warning(f"处理日志条目时发生错误: {e}")
        return None


def fetch_m3u8_links(
    browser_instance: browser.webdriver.Remote,
    browser_type: str,
    dingtalk_url: str
) -> Optional[List[str]]:
    """从浏览器日志中获取 M3U8 链接。

    该函数从浏览器的性能日志或网络日志中提取 M3U8 视频链接。
    支持多次重试，每次重试前会刷新页面。

    Args:
        browser_instance: 浏览器实例（Selenium WebDriver 对象）。
        browser_type: 浏览器类型，支持 'chrome'、'edge'、'firefox'。
        dingtalk_url: 钉钉直播 URL。

    Returns:
        包含 M3U8 链接的列表。如果成功获取到链接，列表包含一个或多个链接；
        如果失败，则返回 None。

    Raises:
        ValueError: 如果浏览器类型不支持或 URL 无效。
        RuntimeError: 如果获取日志时发生错误。

    Examples:
        >>> from selenium import webdriver
        >>> driver = webdriver.Edge()
        >>> driver.get("https://n.dingtalk.com/live?liveUuid=abc123")
        >>> links = fetch_m3u8_links(driver, 'edge', 'https://n.dingtalk.com/live?liveUuid=abc123')
        >>> print(links)
        ['https://n.dingtalk.com/live_hp/abc123/video.m3u8']
    """
    logger.info(f"开始获取 M3U8 链接，浏览器类型: {browser_type}，URL: {dingtalk_url}")

    m3u8_links: List[str] = []
    live_uuid = extract_live_uuid(dingtalk_url)

    if not live_uuid:
        error_msg = "未能从 URL 提取 liveUuid"
        logger.error(error_msg)
        print(f"❌ {error_msg}")
        return None

    logger.debug(f"提取到 liveUuid: {live_uuid}")
    print(f"✓ 成功提取 liveUuid: {live_uuid}")

    _validate_browser_type(browser_type)

    for attempt in range(MAX_RETRY_ATTEMPTS):
        try:
            logger.info(f"第 {attempt + 1} 次尝试获取 M3U8 链接")
            print(f"\n🔄 第 {attempt + 1} 次尝试获取 M3U8 链接...")

            if attempt == 0:
                logger.info("等待视频元素加载...")
                print("⏳ 等待视频元素加载...")
                
                try:
                    from selenium.webdriver.support.ui import WebDriverWait
                    WebDriverWait(browser_instance, 20).until(
                        lambda driver: driver.execute_script(
                            "return isNaN(document.querySelector('video')?.duration)"
                        ) == False
                    )
                    logger.info("视频元素已加载")
                    print("✓ 视频元素已加载")
                except Exception as e:
                    logger.warning(f"等待视频加载超时: {e}")
                    print(f"⚠️  等待视频加载超时: {e}")
                    input("请在页面加载后，按Enter键继续...")
                
                _try_play_video(browser_instance)
                print("⏳ 等待 5 秒让视频开始加载...")
                time.sleep(5)

            logs = _get_browser_logs(browser_instance, browser_type)
            logger.info(f"获取到 {len(logs)} 条日志")
            print(f"📊 获取到 {len(logs)} 条日志")

            _save_logs_for_debugging(logs, browser_type, attempt + 1, live_uuid)

            m3u8_count = 0
            for idx, log in enumerate(logs):
                m3u8_url = _process_log_entry(log, browser_type, live_uuid)

                if m3u8_url:
                    logger.info(f"成功获取到 M3U8 链接: {m3u8_url}")
                    print(f"✅ 成功获取到 M3U8 链接: {m3u8_url}")
                    m3u8_links.append(m3u8_url)
                    return m3u8_links
                
                if idx < 10:
                    logger.debug(f"已处理 {idx + 1} 条日志，暂未找到 M3U8 链接")

            logger.warning(f"第 {attempt + 1} 次尝试未获取到 M3U8 链接，准备重试")
            print(f"⚠️  第 {attempt + 1} 次尝试未获取到 M3U8 链接")
            
            if attempt < MAX_RETRY_ATTEMPTS - 1:
                print("🔄 准备刷新页面重试...")
                refresh_page_by_click(browser_instance)

        except Exception as e:
            error_msg = f"获取 M3U8 链接时发生错误: {e}"
            logger.error(error_msg, exc_info=True)
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg) from e

    error_msg = f"经过 {MAX_RETRY_ATTEMPTS} 次尝试仍未获取到 M3U8 链接"
    logger.error(error_msg)
    print(f"\n❌ {error_msg}")
    print(f"💡 调试提示：请确保：")
    print(f"   1. 钉钉直播页面已完全加载")
    print(f"   2. 浏览器已登录钉钉账户")
    print(f"   3. 直播回放链接有效且可访问")
    print(f"   4. 网络连接正常")
    return None


def _validate_m3u8_download_parameters(
    url: str,
    filename: str,
    headers: Dict[str, str]
) -> None:
    """验证 M3U8 下载参数。

    Args:
        url: M3U8 文件 URL。
        filename: 本地保存文件名。
        headers: 请求头字典。

    Raises:
        ValueError: 如果参数无效。
    """
    if not url:
        error_msg = "URL 不能为空"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if not isinstance(url, str):
        error_msg = f"URL 必须是字符串类型，实际类型: {type(url)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if not filename:
        error_msg = "文件名不能为空"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if not isinstance(filename, str):
        error_msg = f"文件名必须是字符串类型，实际类型: {type(filename)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if not headers:
        error_msg = "请求头不能为空"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if not isinstance(headers, dict):
        error_msg = f"请求头必须是字典类型，实际类型: {type(headers)}"
        logger.error(error_msg)
        raise ValueError(error_msg)


def _ensure_directory_exists(filename: str) -> None:
    """确保文件目录存在，如果不存在则创建。

    Args:
        filename: 文件路径。

    Raises:
        RuntimeError: 如果创建目录失败。
        PermissionError: 如果目录不可写。
    """
    file_dir = os.path.dirname(filename)

    if not file_dir:
        logger.debug("文件名不包含目录路径，跳过目录检查")
        return

    if not os.path.exists(file_dir):
        try:
            os.makedirs(file_dir, exist_ok=True)
            logger.info(f"创建目录: {file_dir}")
        except Exception as e:
            error_msg = f"创建目录失败: {file_dir}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e

    if not os.access(file_dir, os.W_OK):
        error_msg = f"目录不可写: {file_dir}"
        logger.error(error_msg)
        raise PermissionError(error_msg)


def _fetch_m3u8_content_via_requests(
    url: str,
    headers: Dict[str, str],
    cookies: Optional[Dict[str, str]] = None
) -> str:
    """使用 requests 库获取 M3U8 文件内容。

    Args:
        url: M3U8 文件 URL。
        headers: 请求头字典。
        cookies: Cookie 字典（可选）。

    Returns:
        M3U8 文件内容。

    Raises:
        RuntimeError: 如果获取内容失败或内容为空。
    """
    logger.debug(f"通过 requests 获取 M3U8 内容，URL: {url}")

    try:
        response = requests.get(
            url,
            headers=headers,
            cookies=cookies,
            timeout=30
        )
        response.raise_for_status()
        
        m3u8_content = response.text
        
        if not m3u8_content:
            error_msg = "下载的 M3U8 内容为空"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        logger.debug(f"成功获取 M3U8 内容，长度: {len(m3u8_content)} 字符")
        return m3u8_content

    except requests.exceptions.RequestException as e:
        error_msg = f"获取 M3U8 内容失败: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e


def _save_m3u8_content_to_file(filename: str, content: str) -> None:
    """将 M3U8 内容保存到文件。

    Args:
        filename: 文件路径。
        content: M3U8 文件内容。

    Raises:
        IOError: 如果文件写入失败。
    """
    logger.debug(f"保存 M3U8 内容到文件: {filename}")

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"M3U8 文件保存成功: {filename}")
    except IOError as e:
        error_msg = f"保存 M3U8 文件失败: {e}"
        logger.error(error_msg, exc_info=True)
        raise IOError(error_msg) from e


def download_m3u8_file(
    url: str,
    filename: str,
    headers: Dict[str, str],
    cookies: Optional[Dict[str, str]] = None
) -> str:
    """下载 M3U8 文件内容并保存到本地。

    该函数通过 requests 库获取 M3U8 文件内容，
    然后将内容保存到指定的本地文件中。

    Args:
        url: M3U8 文件 URL。
        filename: 本地保存文件名（包含完整路径）。
        headers: 请求头字典，包含必要的认证信息。
        cookies: Cookie 字典（可选），包含必要的认证信息。

    Returns:
        保存的文件路径。

    Raises:
        ValueError: 如果参数无效（URL、文件名或请求头为空或类型错误）。
        PermissionError: 如果文件目录不可写。
        RuntimeError: 如果下载或保存失败。

    Examples:
        >>> url = "https://n.dingtalk.com/live_hp/abc123/video.m3u8"
        >>> filename = "d:\\\\videos\\\\video.m3u8"
        >>> headers = {"User-Agent": "Mozilla/5.0"}
        >>> cookies = {"session": "abc123"}
        >>> result = download_m3u8_file(url, filename, headers, cookies)
        >>> print(result)
        'd:\\\\videos\\\\video.m3u8'
    """
    logger.info(f"开始下载 M3U8 文件，URL: {url}，保存到: {filename}")

    try:
        _validate_m3u8_download_parameters(url, filename, headers)
        _ensure_directory_exists(filename)
        m3u8_content = _fetch_m3u8_content_via_requests(url, headers, cookies)
        _save_m3u8_content_to_file(filename, m3u8_content)

        logger.info(f"M3U8 文件下载并保存成功: {filename}")
        return filename

    except (ValueError, PermissionError, RuntimeError, IOError) as e:
        logger.error(f"下载 M3U8 文件失败: {e}")
        raise
    except Exception as e:
        error_msg = f"下载 M3U8 文件时发生未知错误: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e
