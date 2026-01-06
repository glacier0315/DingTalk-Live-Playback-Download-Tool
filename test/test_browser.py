"""测试 browser.py 模块的单元测试"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, Optional


class TestGetBrowserOptions:
    """测试get_browser_options函数"""

    def test_edge_options_configured(self):
        """测试Edge浏览器选项配置"""
        from dingtalk_download.browser import get_browser_options

        result = get_browser_options('edge')
        assert result is not None
        assert isinstance(result, dict)
        assert result['type'] == 'edge'

    def test_chrome_options_configured(self):
        """测试Chrome浏览器选项配置"""
        from dingtalk_download.browser import get_browser_options

        result = get_browser_options('chrome')
        assert result is not None
        assert isinstance(result, dict)
        assert result['type'] == 'chrome'

    def test_firefox_options_configured(self):
        """测试Firefox浏览器选项配置"""
        from dingtalk_download.browser import get_browser_options

        result = get_browser_options('firefox')
        assert result is not None
        assert isinstance(result, dict)
        assert result['type'] == 'firefox'

    def test_invalid_browser_raises_error(self):
        """测试无效浏览器类型抛出错误"""
        from dingtalk_download.browser import get_browser_options

        with pytest.raises(ValueError, match="不支持的浏览器类型"):
            get_browser_options('invalid_browser')


class TestExtractRequestHeaders:
    """测试_extract_request_headers函数"""

    def test_extract_request_headers_success(self):
        """测试提取请求头成功"""
        from dingtalk_download.browser import _extract_request_headers

        browser = Mock()
        browser.execute_script.side_effect = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'https://n.dingtalk.com/'
        ]

        result = _extract_request_headers(browser, 'https://example.com')

        assert 'User-Agent' in result
        assert 'Referer' in result
        assert 'Accept' in result

    def test_extract_request_headers_error(self):
        """测试提取请求头错误"""
        from dingtalk_download.browser import _extract_request_headers

        browser = Mock()
        browser.execute_script.side_effect = Exception("Script error")

        result = _extract_request_headers(browser, 'https://example.com')

        assert result is not None
        assert 'User-Agent' in result


class TestExtractLiveName:
    """测试_extract_live_name函数"""

    def test_extract_live_name_success(self):
        """测试提取直播名称成功"""
        from dingtalk_download.browser import _extract_live_name

        browser = Mock()
        mock_element = Mock()
        mock_element.text = 'Test Live Name'
        browser.find_element.return_value = mock_element

        result = _extract_live_name(browser)

        assert result == 'Test Live Name'

    def test_extract_live_name_default(self):
        """测试提取直播名称失败返回默认值"""
        from dingtalk_download.browser import _extract_live_name

        browser = Mock()
        browser.find_element.side_effect = Exception("Element not found")

        result = _extract_live_name(browser)

        assert result is not None
        assert isinstance(result, str)


class TestExtractCookies:
    """测试_extract_cookies函数"""

    def test_extract_cookies_success(self):
        """测试提取Cookie成功"""
        from dingtalk_download.browser import _extract_cookies

        browser = Mock()
        mock_cookie1 = {'name': 'session', 'value': 'abc123'}
        mock_cookie2 = {'name': 'token', 'value': 'def456'}
        browser.get_cookies.return_value = [mock_cookie1, mock_cookie2]

        result = _extract_cookies(browser)

        assert result == {'session': 'abc123', 'token': 'def456'}

    def test_extract_cookies_empty(self):
        """测试没有Cookie"""
        from dingtalk_download.browser import _extract_cookies

        browser = Mock()
        browser.get_cookies.return_value = []

        result = _extract_cookies(browser)

        assert result == {}


class TestGetBrowserCookie:
    """测试get_browser_cookie函数"""

    @patch('dingtalk_download.browser.create_browser')
    @patch('dingtalk_download.browser._extract_request_headers')
    @patch('dingtalk_download.browser._extract_live_name')
    @patch('dingtalk_download.browser._extract_cookies')
    @patch('builtins.input')
    def test_get_browser_cookie_success(
        self,
        mock_input,
        mock_extract_cookies,
        mock_extract_live_name,
        mock_extract_headers,
        mock_create_browser
    ):
        """测试获取浏览器Cookie成功"""
        from dingtalk_download.browser import get_browser_cookie

        mock_browser = Mock()
        mock_create_browser.return_value = mock_browser
        mock_extract_headers.return_value = {'User-Agent': 'Mozilla/5.0'}
        mock_extract_live_name.return_value = 'Test Live'
        mock_extract_cookies.return_value = {'session': 'abc123'}

        url = 'https://example.com'

        browser, cookies, headers, live_name = get_browser_cookie(url)

        assert cookies == {'session': 'abc123'}
        assert headers == {'User-Agent': 'Mozilla/5.0'}
        assert live_name == 'Test Live'


class TestRepeatGetBrowserCookie:
    """测试repeat_get_browser_cookie函数"""

    @patch('dingtalk_download.browser._extract_live_name')
    @patch('dingtalk_download.browser._extract_cookies')
    @patch('dingtalk_download.browser.WebDriverWait')
    @patch('builtins.input')
    def test_repeat_get_browser_cookie_success(
        self,
        mock_input,
        mock_wait,
        mock_extract_cookies,
        mock_extract_live_name
    ):
        """测试重复获取浏览器Cookie成功"""
        from dingtalk_download import browser as browser_module
        from dingtalk_download.browser import repeat_get_browser_cookie

        mock_browser = Mock()
        def execute_script_side_effect(script, *args):
            if 'isNaN' in script:
                return False
            elif 'fetch' in script:
                return {'User-Agent': 'Mozilla/5.0'}
            return None
        
        mock_browser.execute_script = execute_script_side_effect
        browser_module.browser = mock_browser
        mock_extract_live_name.return_value = 'Test Live'
        mock_extract_cookies.return_value = {'session': 'abc123'}
        mock_wait.return_value.until.side_effect = lambda fn: fn(mock_browser)

        url = 'https://example.com'

        cookies, headers, live_name = repeat_get_browser_cookie(url)

        assert cookies == {'session': 'abc123'}
        assert headers == {'User-Agent': 'Mozilla/5.0'}
        assert live_name == 'Test Live'

    @patch('dingtalk_download.browser._extract_live_name')
    @patch('dingtalk_download.browser._extract_cookies')
    @patch('dingtalk_download.browser.WebDriverWait')
    @patch('builtins.input')
    def test_repeat_get_browser_cookie_failure(
        self,
        mock_input,
        mock_wait,
        mock_extract_cookies,
        mock_extract_live_name
    ):
        """测试重复获取浏览器Cookie失败"""
        from dingtalk_download import browser as browser_module
        from dingtalk_download.browser import repeat_get_browser_cookie

        mock_browser = Mock()
        mock_browser.execute_script.side_effect = Exception("Timeout")
        browser_module.browser = mock_browser
        mock_extract_cookies.side_effect = Exception("Cookie error")

        url = 'https://example.com'

        with pytest.raises(RuntimeError, match="重复获取Cookie时发生错误"):
            repeat_get_browser_cookie(url)
