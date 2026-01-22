"""网络Mock工具模块

提供网络相关的Mock工具，用于测试HTTP请求、Cookie处理等功能。
"""

from unittest.mock import MagicMock, Mock
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urlparse


class MockResponse:
    """Mock HTTP响应类"""

    def __init__(self, status_code: int = 200, text: str = "", content: bytes = b""):
        """初始化Mock响应

        Args:
            status_code: HTTP状态码
            text: 响应文本
            content: 响应内容（二进制）
        """
        self.status_code = status_code
        self.text = text
        self.content = content
        self._headers = {}
        self._cookies = {}
        self._json_data = {}
        self._url = "https://example.com"
        self._encoding = "utf-8"
        self._elapsed = Mock()
        self._elapsed.total_seconds.return_value = 0.1

    def json(self) -> Dict[str, Any]:
        """获取JSON数据"""
        return self._json_data

    def raise_for_status(self) -> None:
        """如果状态码不是2xx，抛出异常"""
        if 400 <= self.status_code < 600:
            raise Exception(f"HTTP Error {self.status_code}")

    @property
    def headers(self) -> Dict[str, str]:
        """获取响应头"""
        return self._headers

    @headers.setter
    def headers(self, value: Dict[str, str]):
        """设置响应头"""
        self._headers = value

    @property
    def cookies(self) -> Dict[str, str]:
        """获取Cookie"""
        return self._cookies

    @cookies.setter
    def cookies(self, value: Dict[str, str]):
        """设置Cookie"""
        self._cookies = value

    @property
    def url(self) -> str:
        """获取URL"""
        return self._url

    @url.setter
    def url(self, value: str):
        """设置URL"""
        self._url = value

    @property
    def encoding(self) -> str:
        """获取编码"""
        return self._encoding

    @encoding.setter
    def encoding(self, value: str):
        """设置编码"""
        self._encoding = value

    @property
    def elapsed(self) -> Mock:
        """获取耗时"""
        return self._elapsed

    def set_json_data(self, data: Dict[str, Any]) -> None:
        """设置JSON数据

        Args:
            data: JSON数据
        """
        self._json_data = data

    def add_header(self, key: str, value: str) -> None:
        """添加响应头

        Args:
            key: 键
            value: 值
        """
        self._headers[key] = value

    def add_cookie(self, name: str, value: str) -> None:
        """添加Cookie

        Args:
            name: Cookie名称
            value: Cookie值
        """
        self._cookies[name] = value


class MockRequests:
    """Mock requests库类"""

    def __init__(self):
        """初始化Mock requests"""
        self._responses = {}
        self._sessions = {}
        self._request_history = []
        self._default_response = MockResponse()

    def get(
        self,
        url: str,
        params: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
        cookies: Dict[str, str] = None,
        timeout: int = 30,
        **kwargs,
    ) -> MockResponse:
        """发送GET请求

        Args:
            url: URL
            params: 查询参数
            headers: 请求头
            cookies: Cookie
            timeout: 超时时间
            **kwargs: 其他参数

        Returns:
            MockResponse实例
        """
        self._request_history.append(
            {
                "method": "GET",
                "url": url,
                "params": params,
                "headers": headers,
                "cookies": cookies,
                "timeout": timeout,
                "kwargs": kwargs,
            }
        )
        return self._responses.get(url, self._default_response)

    def post(
        self,
        url: str,
        data: Any = None,
        json: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
        cookies: Dict[str, str] = None,
        timeout: int = 30,
        **kwargs,
    ) -> MockResponse:
        """发送POST请求

        Args:
            url: URL
            data: 请求数据
            json: JSON数据
            headers: 请求头
            cookies: Cookie
            timeout: 超时时间
            **kwargs: 其他参数

        Returns:
            MockResponse实例
        """
        self._request_history.append(
            {
                "method": "POST",
                "url": url,
                "data": data,
                "json": json,
                "headers": headers,
                "cookies": cookies,
                "timeout": timeout,
                "kwargs": kwargs,
            }
        )
        return self._responses.get(url, self._default_response)

    def put(
        self,
        url: str,
        data: Any = None,
        json: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
        cookies: Dict[str, str] = None,
        timeout: int = 30,
        **kwargs,
    ) -> MockResponse:
        """发送PUT请求

        Args:
            url: URL
            data: 请求数据
            json: JSON数据
            headers: 请求头
            cookies: Cookie
            timeout: 超时时间
            **kwargs: 其他参数

        Returns:
            MockResponse实例
        """
        self._request_history.append(
            {
                "method": "PUT",
                "url": url,
                "data": data,
                "json": json,
                "headers": headers,
                "cookies": cookies,
                "timeout": timeout,
                "kwargs": kwargs,
            }
        )
        return self._responses.get(url, self._default_response)

    def delete(
        self,
        url: str,
        headers: Dict[str, str] = None,
        cookies: Dict[str, str] = None,
        timeout: int = 30,
        **kwargs,
    ) -> MockResponse:
        """发送DELETE请求

        Args:
            url: URL
            headers: 请求头
            cookies: Cookie
            timeout: 超时时间
            **kwargs: 其他参数

        Returns:
            MockResponse实例
        """
        self._request_history.append(
            {
                "method": "DELETE",
                "url": url,
                "headers": headers,
                "cookies": cookies,
                "timeout": timeout,
                "kwargs": kwargs,
            }
        )
        return self._responses.get(url, self._default_response)

    def head(
        self,
        url: str,
        headers: Dict[str, str] = None,
        cookies: Dict[str, str] = None,
        timeout: int = 30,
        **kwargs,
    ) -> MockResponse:
        """发送HEAD请求

        Args:
            url: URL
            headers: 请求头
            cookies: Cookie
            timeout: 超时时间
            **kwargs: 其他参数

        Returns:
            MockResponse实例
        """
        self._request_history.append(
            {
                "method": "HEAD",
                "url": url,
                "headers": headers,
                "cookies": cookies,
                "timeout": timeout,
                "kwargs": kwargs,
            }
        )
        return self._responses.get(url, self._default_response)

    def Session(self) -> "MockSession":
        """创建会话

        Returns:
            MockSession实例
        """
        session = MockSession()
        self._sessions[id(session)] = session
        return session

    def set_response(self, url: str, response: MockResponse) -> None:
        """设置URL对应的响应

        Args:
            url: URL
            response: MockResponse实例
        """
        self._responses[url] = response

    def set_default_response(self, response: MockResponse) -> None:
        """设置默认响应

        Args:
            response: MockResponse实例
        """
        self._default_response = response

    @property
    def request_history(self) -> List[Dict[str, Any]]:
        """获取请求历史"""
        return self._request_history

    def clear_history(self) -> None:
        """清空请求历史"""
        self._request_history.clear()


class MockSession:
    """Mock会话类"""

    def __init__(self):
        """初始化Mock会话"""
        self._cookies = {}
        self._headers = {}
        self._responses = {}
        self._request_history = []
        self._default_response = MockResponse()

    def get(
        self,
        url: str,
        params: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
        timeout: int = 30,
        **kwargs,
    ) -> MockResponse:
        """发送GET请求

        Args:
            url: URL
            params: 查询参数
            headers: 请求头
            timeout: 超时时间
            **kwargs: 其他参数

        Returns:
            MockResponse实例
        """
        self._request_history.append(
            {
                "method": "GET",
                "url": url,
                "params": params,
                "headers": headers,
                "timeout": timeout,
                "kwargs": kwargs,
            }
        )
        return self._responses.get(url, self._default_response)

    def post(
        self,
        url: str,
        data: Any = None,
        json: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
        timeout: int = 30,
        **kwargs,
    ) -> MockResponse:
        """发送POST请求

        Args:
            url: URL
            data: 请求数据
            json: JSON数据
            headers: 请求头
            timeout: 超时时间
            **kwargs: 其他参数

        Returns:
            MockResponse实例
        """
        self._request_history.append(
            {
                "method": "POST",
                "url": url,
                "data": data,
                "json": json,
                "headers": headers,
                "timeout": timeout,
                "kwargs": kwargs,
            }
        )
        return self._responses.get(url, self._default_response)

    def put(
        self,
        url: str,
        data: Any = None,
        json: Dict[str, Any] = None,
        headers: Dict[str, str] = None,
        timeout: int = 30,
        **kwargs,
    ) -> MockResponse:
        """发送PUT请求

        Args:
            url: URL
            data: 请求数据
            json: JSON数据
            headers: 请求头
            timeout: 超时时间
            **kwargs: 其他参数

        Returns:
            MockResponse实例
        """
        self._request_history.append(
            {
                "method": "PUT",
                "url": url,
                "data": data,
                "json": json,
                "headers": headers,
                "timeout": timeout,
                "kwargs": kwargs,
            }
        )
        return self._responses.get(url, self._default_response)

    def delete(
        self, url: str, headers: Dict[str, str] = None, timeout: int = 30, **kwargs
    ) -> MockResponse:
        """发送DELETE请求

        Args:
            url: URL
            headers: 请求头
            timeout: 超时时间
            **kwargs: 其他参数

        Returns:
            MockResponse实例
        """
        self._request_history.append(
            {
                "method": "DELETE",
                "url": url,
                "headers": headers,
                "timeout": timeout,
                "kwargs": kwargs,
            }
        )
        return self._responses.get(url, self._default_response)

    def close(self) -> None:
        """关闭会话"""
        pass

    @property
    def cookies(self) -> Dict[str, str]:
        """获取Cookie"""
        return self._cookies

    @property
    def headers(self) -> Dict[str, str]:
        """获取请求头"""
        return self._headers

    def set_response(self, url: str, response: MockResponse) -> None:
        """设置URL对应的响应

        Args:
            url: URL
            response: MockResponse实例
        """
        self._responses[url] = response

    def set_default_response(self, response: MockResponse) -> None:
        """设置默认响应

        Args:
            response: MockResponse实例
        """
        self._default_response = response

    @property
    def request_history(self) -> List[Dict[str, Any]]:
        """获取请求历史"""
        return self._request_history

    def clear_history(self) -> None:
        """清空请求历史"""
        self._request_history.clear()


class MockCookieJar:
    """Mock Cookie Jar类"""

    def __init__(self):
        """初始化Mock Cookie Jar"""
        self._cookies = {}

    def set(self, name: str, value: str, domain: str = "", path: str = "/") -> None:
        """设置Cookie

        Args:
            name: Cookie名称
            value: Cookie值
            domain: 域名
            path: 路径
        """
        key = f"{domain}:{path}:{name}"
        self._cookies[key] = {"name": name, "value": value, "domain": domain, "path": path}

    def get(self, name: str, domain: str = "", path: str = "/") -> Optional[str]:
        """获取Cookie值

        Args:
            name: Cookie名称
            domain: 域名
            path: 路径

        Returns:
            Cookie值或None
        """
        key = f"{domain}:{path}:{name}"
        return self._cookies.get(key, {}).get("value")

    def get_dict(self, domain: str = "", path: str = "/") -> Dict[str, str]:
        """获取所有Cookie

        Args:
            domain: 域名
            path: 路径

        Returns:
            Cookie字典
        """
        result = {}
        for key, cookie in self._cookies.items():
            if (not domain or cookie["domain"] == domain) and (not path or cookie["path"] == path):
                result[cookie["name"]] = cookie["value"]
        return result

    def clear(self, domain: str = "", path: str = "", name: str = "") -> None:
        """清除Cookie

        Args:
            domain: 域名
            path: 路径
            name: Cookie名称
        """
        if name:
            keys_to_remove = [k for k in self._cookies if k.endswith(f":{name}")]
            for key in keys_to_remove:
                del self._cookies[key]
        elif domain or path:
            keys_to_remove = []
            for key, cookie in self._cookies.items():
                if (not domain or cookie["domain"] == domain) and (
                    not path or cookie["path"] == path
                ):
                    keys_to_remove.append(key)
            for key in keys_to_remove:
                del self._cookies[key]
        else:
            self._cookies.clear()

    def __len__(self) -> int:
        """获取Cookie数量"""
        return len(self._cookies)

    def __iter__(self):
        """迭代Cookie"""
        return iter(self._cookies.values())


class MockNetworkError(Exception):
    """Mock网络错误"""

    def __init__(self, message: str = "Network Error", status_code: int = 0):
        """初始化网络错误

        Args:
            message: 错误消息
            status_code: 状态码
        """
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class MockTimeoutError(Exception):
    """Mock超时错误"""

    def __init__(self, message: str = "Timeout Error", timeout: int = 30):
        """初始化超时错误

        Args:
            message: 错误消息
            timeout: 超时时间
        """
        self.message = message
        self.timeout = timeout
        super().__init__(message)


class MockConnectionError(Exception):
    """Mock连接错误"""

    def __init__(self, message: str = "Connection Error"):
        """初始化连接错误

        Args:
            message: 错误消息
        """
        self.message = message
        super().__init__(message)


def create_mock_response(
    status_code: int = 200, text: str = "", content: bytes = b""
) -> MockResponse:
    """创建Mock响应

    Args:
        status_code: HTTP状态码
        text: 响应文本
        content: 响应内容（二进制）

    Returns:
        MockResponse实例
    """
    return MockResponse(status_code, text, content)


def create_mock_requests() -> MockRequests:
    """创建Mock requests

    Returns:
        MockRequests实例
    """
    return MockRequests()


def create_mock_session() -> MockSession:
    """创建Mock会话

    Returns:
        MockSession实例
    """
    return MockSession()


def create_mock_cookie_jar() -> MockCookieJar:
    """创建Mock Cookie Jar

    Returns:
        MockCookieJar实例
    """
    return MockCookieJar()
