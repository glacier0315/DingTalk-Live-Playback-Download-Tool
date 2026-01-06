"""浏览器配置和操作模块。

该模块提供了浏览器实例的创建、配置和管理功能，支持 Chrome、Edge 和 Firefox 浏览器。
主要功能包括：
- 浏览器实例的生命周期管理
- 浏览器选项的配置
- Cookie 和请求头的提取
- 直播名称的提取

Example:
    >>> from dingtalk_download.browser import BrowserManager
    >>> manager = BrowserManager()
    >>> browser = manager.create_browser('edge')
    >>> # 使用浏览器...
    >>> manager.close_browser()
"""
import sys
import logging
from typing import Optional, Dict, Any, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


logger = logging.getLogger(__name__)


# 浏览器类型常量
BROWSER_TYPE_EDGE = 'edge'
BROWSER_TYPE_CHROME = 'chrome'
BROWSER_TYPE_FIREFOX = 'firefox'

SUPPORTED_BROWSER_TYPES = [BROWSER_TYPE_EDGE, BROWSER_TYPE_CHROME, BROWSER_TYPE_FIREFOX]

# 默认请求头配置
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://n.dingtalk.com/',
    'Accept': 'application/vnd.apple.mpegurl, text/plain, */*'
}

# 直播名称提取选择器
LIVE_NAME_XPATH = '//*[@id="live-room"]/div[1]/div[1]/h3'
LIVE_NAME_CLASS = 'vwi5-oG8'
DEFAULT_LIVE_NAME = '直播视频名称不可获取'


class BrowserManager:
    """浏览器管理器，负责浏览器实例的生命周期管理。
    
    该类提供了浏览器实例的创建、获取和关闭功能，支持多种浏览器类型。
    使用单例模式确保整个应用程序中只有一个浏览器实例。
    
    Attributes:
        _browser: 当前浏览器实例，可能为 None。
    
    Example:
        >>> manager = BrowserManager()
        >>> browser = manager.create_browser('edge')
        >>> # 使用浏览器...
        >>> manager.close_browser()
    """
    
    def __init__(self) -> None:
        """初始化浏览器管理器。
        
        创建一个新的浏览器管理器实例，初始时没有浏览器实例。
        """
        self._browser: Optional[webdriver.Remote] = None
        logger.debug("BrowserManager 初始化完成")
    
    def create_browser(self, browser_type: str) -> webdriver.Remote:
        """创建浏览器实例。
        
        根据指定的浏览器类型创建并配置浏览器实例。
        支持的浏览器类型包括：edge、chrome、firefox。
        
        Args:
            browser_type: 浏览器类型，支持 'edge'、'chrome' 或 'firefox'。
        
        Returns:
            配置好的浏览器实例。
        
        Raises:
            ValueError: 如果浏览器类型不支持或无法获取浏览器配置。
            RuntimeError: 如果创建浏览器实例失败。
        
        Examples:
            >>> manager = BrowserManager()
            >>> browser = manager.create_browser('edge')
            >>> isinstance(browser, webdriver.Edge)
            True
        """
        logger.info(f"开始创建浏览器实例，类型: {browser_type}")
        
        try:
            options_config = get_browser_options(browser_type)
            
            if options_config is None:
                error_msg = f"无法获取浏览器配置: {browser_type}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            if browser_type == BROWSER_TYPE_EDGE:
                self._browser = webdriver.Edge(options=options_config['options'])
            elif browser_type == BROWSER_TYPE_CHROME:
                self._browser = webdriver.Chrome(options=options_config['options'])
            elif browser_type == BROWSER_TYPE_FIREFOX:
                self._browser = webdriver.Firefox(options=options_config['options'])
            else:
                error_msg = f"不支持的浏览器类型: {browser_type}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"成功创建浏览器实例: {browser_type}")
            return self._browser
        
        except ValueError:
            raise
        except Exception as e:
            error_msg = f"创建浏览器失败: {e}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e
    
    def get_browser(self) -> Optional[webdriver.Remote]:
        """获取当前浏览器实例。
        
        返回当前管理的浏览器实例。如果没有创建浏览器实例，则返回 None。
        
        Returns:
            当前浏览器实例，如果不存在则返回 None。
        
        Examples:
            >>> manager = BrowserManager()
            >>> manager.get_browser() is None
            True
            >>> manager.create_browser('edge')
            >>> manager.get_browser() is not None
            True
        """
        logger.debug("获取浏览器实例")
        return self._browser
    
    def close_browser(self) -> None:
        """关闭浏览器实例。
        
        如果存在浏览器实例，则关闭它并释放资源。
        如果没有浏览器实例，则不执行任何操作。
        
        Examples:
            >>> manager = BrowserManager()
            >>> manager.create_browser('edge')
            >>> manager.close_browser()
            >>> manager.get_browser() is None
            True
        """
        if self._browser:
            logger.info("关闭浏览器实例")
            self._browser.quit()
            self._browser = None
        else:
            logger.debug("没有浏览器实例需要关闭")


# 全局浏览器管理器实例（向后兼容）
browser_manager = BrowserManager()
browser = None  # 保留全局变量以保持向后兼容性


def get_browser_options(browser_type: str) -> Optional[Dict[str, Any]]:
    """获取浏览器选项配置。
    
    根据指定的浏览器类型返回相应的浏览器选项配置。
    配置包括禁用日志、忽略证书错误等常用设置。
    
    Args:
        browser_type: 浏览器类型，支持 'edge'、'chrome' 或 'firefox'。
    
    Returns:
        包含浏览器选项和类型的字典，格式为 {'options': options, 'type': browser_type}。
        如果浏览器类型不支持，返回 None。
    
    Raises:
        ValueError: 如果浏览器类型不支持。
    
    Examples:
        >>> config = get_browser_options('edge')
        >>> config['type']
        'edge'
        >>> isinstance(config['options'], webdriver.EdgeOptions)
        True
    """
    logger.debug(f"获取浏览器选项配置: {browser_type}")
    
    if browser_type == BROWSER_TYPE_EDGE:
        return _get_edge_options()
    elif browser_type == BROWSER_TYPE_CHROME:
        return _get_chrome_options()
    elif browser_type == BROWSER_TYPE_FIREFOX:
        return _get_firefox_options()
    else:
        error_msg = f"不支持的浏览器类型: {browser_type}"
        logger.error(error_msg)
        raise ValueError(error_msg)


def _get_edge_options() -> Dict[str, Any]:
    """获取 Edge 浏览器选项配置。
    
    配置 Edge 浏览器的启动参数和日志设置。
    
    Returns:
        包含 Edge 选项和类型的字典。
    
    Examples:
        >>> config = _get_edge_options()
        >>> config['type']
        'edge'
    """
    logger.debug("配置 Edge 浏览器选项")
    
    edge_options = webdriver.EdgeOptions()
    edge_options.add_argument('--disable-usb-device-event-log')
    edge_options.add_argument('--ignore-certificate-errors')
    edge_options.add_argument('--disable-logging')
    edge_options.add_argument('--disable_ssl_verification')
    edge_options.add_argument('--log-level=3')
    edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    edge_options.set_capability("ms:loggingPrefs", {"performance": "ALL"})
    
    return {'options': edge_options, 'type': BROWSER_TYPE_EDGE}


def _get_chrome_options() -> Dict[str, Any]:
    """获取 Chrome 浏览器选项配置。
    
    配置 Chrome 浏览器的启动参数和日志设置。
    
    Returns:
        包含 Chrome 选项和类型的字典。
    
    Examples:
        >>> config = _get_chrome_options()
        >>> config['type']
        'chrome'
    """
    logger.debug("配置 Chrome 浏览器选项")
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-usb-device-event-log')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--disable-logging')
    chrome_options.add_argument('--log-level=3')
    chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    
    return {'options': chrome_options, 'type': BROWSER_TYPE_CHROME}


def _get_firefox_options() -> Dict[str, Any]:
    """获取 Firefox 浏览器选项配置。
    
    配置 Firefox 浏览器的启动参数和日志设置。
    
    Returns:
        包含 Firefox 选项和类型的字典。
    
    Examples:
        >>> config = _get_firefox_options()
        >>> config['type']
        'firefox'
    """
    logger.debug("配置 Firefox 浏览器选项")
    
    firefox_options = webdriver.FirefoxOptions()
    firefox_options.add_argument('--disable-usb-device-event-log')
    firefox_options.add_argument('--ignore-certificate-errors')
    firefox_options.add_argument('--disable-logging')
    firefox_options.add_argument('--log-level=3')
    firefox_options.set_capability('moz:firefoxOptions', {
        'log': {
            'level': 'ALL',
            'browser': 'ALL',
        }
    })
    
    return {'options': firefox_options, 'type': BROWSER_TYPE_FIREFOX}


def create_browser(browser_type: str) -> Optional[webdriver.Remote]:
    """创建浏览器实例（向后兼容函数）。
    
    该函数用于向后兼容，创建浏览器实例并更新全局变量。
    建议使用 BrowserManager 类的实例方法。
    
    Args:
        browser_type: 浏览器类型，支持 'edge'、'chrome' 或 'firefox'。
    
    Returns:
        创建的浏览器实例。
    
    Examples:
        >>> browser = create_browser('edge')
        >>> browser is not None
        True
    """
    global browser
    logger.info(f"创建浏览器实例（向后兼容）: {browser_type}")
    browser = browser_manager.create_browser(browser_type)
    return browser


def close_browser() -> None:
    """关闭浏览器实例（向后兼容函数）。
    
    该函数用于向后兼容，关闭浏览器实例并清空全局变量。
    建议使用 BrowserManager 类的实例方法。
    
    Examples:
        >>> create_browser('edge')
        >>> close_browser()
        >>> browser is None
        True
    """
    global browser
    logger.info("关闭浏览器实例（向后兼容）")
    browser_manager.close_browser()
    browser = None


def _extract_request_headers(browser: webdriver.Remote, url: str) -> Dict[str, str]:
    """从浏览器中提取请求头信息。
    
    尝试从浏览器中提取 User-Agent 和 Referer 等请求头信息。
    如果提取失败，则使用默认的请求头配置。
    
    Args:
        browser: 浏览器实例。
        url: 目标 URL。
    
    Returns:
        包含请求头信息的字典。
    
    Examples:
        >>> headers = _extract_request_headers(browser, 'https://example.com')
        >>> 'User-Agent' in headers
        True
    """
    logger.debug("尝试从浏览器提取请求头信息")
    
    try:
        user_agent = browser.execute_script("return navigator.userAgent")
        referer = browser.execute_script("return document.referrer")
        
        headers = {
            'User-Agent': user_agent,
            'Referer': referer if referer else 'https://n.dingtalk.com/',
            'Accept': 'application/vnd.apple.mpegurl, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        }
        logger.info("成功从浏览器提取请求头信息")
        return headers
    
    except Exception as e:
        logger.warning(f"获取请求头信息时发生错误: {e}，使用默认请求头")
        return DEFAULT_HEADERS.copy()


def _extract_live_name(browser: webdriver.Remote) -> str:
    """从浏览器页面中提取直播名称。
    
    尝试使用多种方式从页面中提取直播名称：
    1. 首先尝试使用 XPath 选择器
    2. 如果失败，尝试使用 CSS 类选择器
    3. 如果都失败，返回默认名称
    
    Args:
        browser: 浏览器实例。
    
    Returns:
        直播名称字符串。如果提取失败，返回默认名称。
    
    Examples:
        >>> live_name = _extract_live_name(browser)
        >>> isinstance(live_name, str)
        True
    """
    logger.debug("尝试提取直播名称")
    
    try:
        live_name = browser.find_element(By.XPATH, LIVE_NAME_XPATH).text
        logger.info(f"使用 XPath 成功提取直播名称: {live_name}")
        return live_name
    except Exception as e:
        logger.warning(f"XPath 获取直播名称失败: {e}，尝试使用 CSS 选择器")
        try:
            live_name = browser.find_element(By.CLASS_NAME, LIVE_NAME_CLASS).text
            logger.info(f"使用 CSS 选择器成功提取直播名称: {live_name}")
            return live_name
        except Exception as e:
            logger.warning(f"CSS Selector 获取直播名称失败: {e}，使用默认名称")
            return DEFAULT_LIVE_NAME


def _extract_cookies(browser: webdriver.Remote) -> Dict[str, str]:
    """从浏览器中提取所有 Cookie。
    
    将浏览器的 Cookie 列表转换为字典格式。
    
    Args:
        browser: 浏览器实例。
    
    Returns:
        包含 Cookie 名称和值的字典。
    
    Examples:
        >>> cookies = _extract_cookies(browser)
        >>> isinstance(cookies, dict)
        True
    """
    logger.debug("提取浏览器 Cookie")
    cookies = browser.get_cookies()
    cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
    logger.info(f"成功提取 {len(cookie_dict)} 个 Cookie")
    return cookie_dict


def get_browser_cookie(
    url: str,
    browser_type: str = BROWSER_TYPE_EDGE
) -> Tuple[webdriver.Remote, Dict[str, str], Dict[str, str], str]:
    """获取浏览器的 Cookie、请求头和直播名称。
    
    创建浏览器实例，导航到指定 URL，等待用户登录后提取 Cookie、请求头和直播名称。
    这是首次获取 Cookie 的函数。
    
    Args:
        url: 钉钉直播回放链接 URL。
        browser_type: 浏览器类型，默认为 'edge'。
    
    Returns:
        包含四个元素的元组：
        - browser: 浏览器实例
        - cookie_dict: Cookie 字典
        - headers: 请求头字典
        - live_name: 直播名称
    
    Raises:
        RuntimeError: 如果获取 Cookie 过程中发生错误。
    
    Examples:
        >>> browser, cookies, headers, live_name = get_browser_cookie('https://n.dingtalk.com/...')
        >>> isinstance(cookies, dict)
        True
        >>> isinstance(headers, dict)
        True
        >>> isinstance(live_name, str)
        True
    """
    global browser
    logger.info(f"开始获取浏览器 Cookie，URL: {url}，浏览器类型: {browser_type}")
    
    try:
        browser = create_browser(browser_type)
        browser.get(url)
        logger.info(f"已导航到 URL: {url}")
        
        input("请在浏览器中登录钉钉账户后，按Enter键继续...")
        logger.info("用户已完成登录")
        
        headers = _extract_request_headers(browser, url)
        live_name = _extract_live_name(browser)
        cookie_dict = _extract_cookies(browser)
        
        logger.info(f"成功获取 Cookie 和请求头，直播名称: {live_name}")
        return browser, cookie_dict, headers, live_name
    
    except Exception as e:
        error_msg = f"获取Cookie时发生错误: {e}"
        logger.error(error_msg, exc_info=True)
        if browser:
            browser.quit()
            browser = None
        raise RuntimeError(error_msg) from e


def repeat_get_browser_cookie(url: str) -> Tuple[Dict[str, str], Dict[str, str], str]:
    """重复获取浏览器的 Cookie、请求头和直播名称。
    
    使用已存在的浏览器实例重新获取 Cookie、请求头和直播名称。
    如果浏览器实例不存在，则调用 get_browser_cookie 函数创建新实例。
    
    Args:
        url: 钉钉直播回放链接 URL。
    
    Returns:
        包含三个元素的元组：
        - cookie_dict: Cookie 字典
        - headers: 请求头字典
        - live_name: 直播名称
    
    Raises:
        RuntimeError: 如果获取 Cookie 过程中发生错误。
    
    Examples:
        >>> cookies, headers, live_name = repeat_get_browser_cookie('https://n.dingtalk.com/...')
        >>> isinstance(cookies, dict)
        True
        >>> isinstance(headers, dict)
        True
        >>> isinstance(live_name, str)
        True
    """
    global browser
    logger.info(f"重复获取浏览器 Cookie，URL: {url}")
    
    try:
        if browser is None:
            logger.info("浏览器实例不存在，调用 get_browser_cookie 创建新实例")
            browser, cookie_dict, headers, live_name = get_browser_cookie(url)
            return cookie_dict, headers, live_name
        
        browser.get(url)
        logger.info(f"已导航到 URL: {url}")
        
        try:
            WebDriverWait(browser, 20).until(
                lambda driver: driver.execute_script("return isNaN(document.querySelector('video')?.duration)") == False
            )
            logger.info("页面视频元素已加载")
        except Exception as e:
            logger.warning(f"未能确定页面是否成功加载: {e}")
            input("未能确定页面是否成功加载。请在页面加载后，按Enter键继续...")
        
        headers = browser.execute_script(
            "return Object.fromEntries(new Headers(fetch(arguments[0], { method: 'GET' })).entries())", url
        )
        logger.info("成功获取请求头")
        
        live_name = _extract_live_name(browser)
        cookie_dict = _extract_cookies(browser)
        
        logger.info(f"成功重复获取 Cookie 和请求头，直播名称: {live_name}")
        return cookie_dict, headers, live_name
    
    except Exception as e:
        error_msg = f"重复获取Cookie时发生错误: {e}"
        logger.error(error_msg, exc_info=True)
        if browser:
            browser.quit()
            browser = None
        raise RuntimeError(error_msg) from e
