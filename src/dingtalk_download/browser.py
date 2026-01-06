"""浏览器配置和操作模块"""
import sys
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BrowserManager:
    """浏览器管理器，负责浏览器实例的生命周期管理"""
    
    def __init__(self):
        self._browser: Optional[webdriver.Remote] = None
    
    def create_browser(self, browser_type: str) -> webdriver.Remote:
        """创建浏览器实例"""
        try:
            options_config = get_browser_options(browser_type)
            
            if options_config is None:
                raise ValueError(f"无法获取浏览器配置: {browser_type}")
            
            if browser_type == 'edge':
                self._browser = webdriver.Edge(options=options_config['options'])
            elif browser_type == 'chrome':
                self._browser = webdriver.Chrome(options=options_config['options'])
            elif browser_type == 'firefox':
                self._browser = webdriver.Firefox(options=options_config['options'])
            else:
                raise ValueError(f"不支持的浏览器类型: {browser_type}")
            
            return self._browser
        except Exception as e:
            raise RuntimeError(f"创建浏览器失败: {e}") from e
    
    def get_browser(self) -> Optional[webdriver.Remote]:
        """获取当前浏览器实例"""
        return self._browser
    
    def close_browser(self):
        """关闭浏览器实例"""
        if self._browser:
            self._browser.quit()
            self._browser = None


# 全局浏览器管理器实例（向后兼容）
browser_manager = BrowserManager()
browser = None  # 保留全局变量以保持向后兼容性


def get_browser_options(browser_type):
    if browser_type == 'edge':
        edge_options = webdriver.EdgeOptions()
        edge_options.add_argument('--disable-usb-device-event-log')
        edge_options.add_argument('--ignore-certificate-errors')
        edge_options.add_argument('--disable-logging')
        edge_options.add_argument('--disable_ssl_verification')
        edge_options.add_argument('--log-level=3')
        edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        edge_options.set_capability("ms:loggingPrefs", {"performance": "ALL"})
        return {'options': edge_options, 'type': 'edge'}
    
    elif browser_type == 'chrome':
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-usb-device-event-log')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--log-level=3')
        chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        return {'options': chrome_options, 'type': 'chrome'}
    
    elif browser_type == 'firefox':
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
        return {'options': firefox_options, 'type': 'firefox'}
    
    else:
        raise ValueError(f"不支持的浏览器类型: {browser_type}")


def create_browser(browser_type: str):
    """创建浏览器实例（向后兼容函数）"""
    global browser
    browser = browser_manager.create_browser(browser_type)
    return browser


def close_browser():
    """关闭浏览器实例（向后兼容函数）"""
    global browser
    browser_manager.close_browser()
    browser = None


def get_browser_cookie(url, browser_type='edge'):
    global browser
    try:
        browser = create_browser(browser_type)
        browser.get(url)
        input("请在浏览器中登录钉钉账户后，按Enter键继续...")

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
        except Exception as e:
            print(f"获取请求头信息时发生错误: {e}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://n.dingtalk.com/',
                'Accept': 'application/vnd.apple.mpegurl, text/plain, */*'
            }
            print("使用默认请求头")
        
        try:
            live_name = browser.find_element(By.XPATH, '//*[@id="live-room"]/div[1]/div[1]/h3').text
        except Exception as e:
            print(f"XPath 获取失败: {e}")
            try:
                live_name = browser.find_element(By.CLASS_NAME, "vwi5-oG8").text
            except Exception as e:
                print(f"CSS Selector 获取失败: {e}")
                live_name = "直播视频名称不可获取"
        
        print(f"直播名称: {live_name}")

        cookies = browser.get_cookies()
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}

        return browser, cookie_dict, headers, live_name

    except Exception as e:
        print(f"获取Cookie时发生错误: {e}")
        if browser:
            browser.quit()
        sys.exit(1)


def repeat_get_browser_cookie(url):
    global browser
    try:
        if browser is None:
            return get_browser_cookie(url)
        
        browser.get(url)
        try:
            WebDriverWait(browser, 20).until(
                lambda driver: driver.execute_script("return isNaN(document.querySelector('video')?.duration)") == False
            )
        except Exception as e:
            input("未能确定页面是否成功加载。请在页面加载后，按Enter键继续...")
        
        headers = browser.execute_script(
            "return Object.fromEntries(new Headers(fetch(arguments[0], { method: 'GET' })).entries())", url
        )
        
        try:
            live_name = browser.find_element(By.XPATH, '//*[@id="live-room"]/div[1]/div[1]/h3').text
        except Exception as e:
            print(f"XPath 获取失败: {e}")
            try:
                live_name = browser.find_element(By.CLASS_NAME, "vwi5-oG8").text
            except Exception as e:
                print(f"CSS Selector 获取失败: {e}")
                live_name = "直播视频名称不可获取"
        
        print(f"直播名称: {live_name}")

        cookies = browser.get_cookies()
        cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}

        return cookie_dict, headers, live_name

    except Exception as e:
        print(f"重复获取Cookie时发生错误: {e}")
        if browser:
            browser.quit()
        sys.exit(1)
