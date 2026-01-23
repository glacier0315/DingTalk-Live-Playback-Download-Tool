"""Mock工具模块

提供各种Mock工具，包括：
- mock_browser: 浏览器Mock工具
- mock_binary: 二进制工具Mock工具
- mock_network: 网络Mock工具
"""

from .mock_browser import (
    MockWebDriver,
    MockBrowserOptions,
    MockBrowserService,
    MockBrowserFactory,
    create_mock_edge_driver,
    create_mock_chrome_driver,
    create_mock_firefox_driver,
    create_mock_browser_factory,
)

from .mock_binary import (
    MockN_m3u8DL_RE,
    MockBinaryTool,
    create_mock_n_m3u8dl_re,
    create_mock_binary_tool,
)

from .mock_network import (
    MockResponse,
    MockRequests,
    MockSession,
    MockCookieJar,
    MockNetworkError,
    MockTimeoutError,
    MockConnectionError,
    create_mock_response,
    create_mock_requests,
    create_mock_session,
    create_mock_cookie_jar,
)

__all__ = [
    # Browser mocks
    "MockWebDriver",
    "MockBrowserOptions",
    "MockBrowserService",
    "MockBrowserFactory",
    "create_mock_edge_driver",
    "create_mock_chrome_driver",
    "create_mock_firefox_driver",
    "create_mock_browser_factory",
    # Binary mocks
    "MockN_m3u8DL_RE",
    "MockBinaryTool",
    "create_mock_n_m3u8dl_re",
    "create_mock_binary_tool",
    # Network mocks
    "MockResponse",
    "MockRequests",
    "MockSession",
    "MockCookieJar",
    "MockNetworkError",
    "MockTimeoutError",
    "MockConnectionError",
    "create_mock_response",
    "create_mock_requests",
    "create_mock_session",
    "create_mock_cookie_jar",
]
