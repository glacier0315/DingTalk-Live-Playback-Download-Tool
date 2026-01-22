"""浏览器Mock工具模块

提供浏览器相关的Mock工具，用于测试浏览器自动化功能。
"""

from unittest.mock import MagicMock, Mock, PropertyMock
from typing import Dict, List, Optional, Any


class MockWebDriver:
    """Mock WebDriver类"""

    def __init__(self, browser_type: str = "edge"):
        """初始化Mock WebDriver

        Args:
            browser_type: 浏览器类型 (edge, chrome, firefox)
        """
        self.browser_type = browser_type
        self._cookies = []
        self._current_url = "https://live.dingtalk.com/test"
        self._title = "Test Live Page"
        self._page_source = "<html><body>Mock Page</body></html>"
        self._window_handles = ["window1"]
        self._current_window_handle = "window1"
        self._execute_script_results = {}
        self._find_element_results = {}
        self._find_elements_results = {}
        self._screenshot_results = None
        self._is_closed = False

    def get_cookies(self) -> List[Dict[str, Any]]:
        """获取所有Cookie"""
        return self._cookies

    def add_cookie(self, cookie: Dict[str, Any]) -> None:
        """添加Cookie"""
        self._cookies.append(cookie)

    def delete_cookie(self, name: str) -> None:
        """删除Cookie"""
        self._cookies = [c for c in self._cookies if c.get("name") != name]

    def delete_all_cookies(self) -> None:
        """删除所有Cookie"""
        self._cookies = []

    def get(self, url: str) -> None:
        """导航到指定URL"""
        self._current_url = url

    def current_url(self) -> str:
        """获取当前URL"""
        return self._current_url

    def title(self) -> str:
        """获取页面标题"""
        return self._title

    def page_source(self) -> str:
        """获取页面源代码"""
        return self._page_source

    def close(self) -> None:
        """关闭当前窗口"""
        self._is_closed = True

    def quit(self) -> None:
        """退出浏览器"""
        self._is_closed = True

    def execute_script(self, script: str, *args) -> Any:
        """执行JavaScript"""
        return self._execute_script_results.get(script, None)

    def execute_async_script(self, script: str, *args) -> Any:
        """执行异步JavaScript"""
        return self._execute_script_results.get(script, None)

    def find_element(self, by: str, value: str) -> Mock:
        """查找单个元素"""
        key = f"{by}:{value}"
        return self._find_element_results.get(key, Mock())

    def find_elements(self, by: str, value: str) -> List[Mock]:
        """查找多个元素"""
        key = f"{by}:{value}"
        return self._find_elements_results.get(key, [])

    def save_screenshot(self, filename: str) -> bool:
        """保存截图"""
        return True

    def get_screenshot_as_png(self) -> bytes:
        """获取截图PNG数据"""
        return b"\x89PNG\r\n\x1a\n"

    def get_screenshot_as_base64(self) -> str:
        """获取截图Base64数据"""
        return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="

    def set_page_load_timeout(self, time_to_wait: float) -> None:
        """设置页面加载超时"""
        pass

    def set_script_timeout(self, time_to_wait: float) -> None:
        """设置脚本执行超时"""
        pass

    def implicitly_wait(self, time_to_wait: float) -> None:
        """设置隐式等待"""
        pass

    def switch_to_window(self, window_name: str) -> None:
        """切换到指定窗口"""
        self._current_window_handle = window_name

    def switch_to_frame(self, frame_reference: Any) -> None:
        """切换到指定框架"""
        pass

    def switch_to_default_content(self) -> None:
        """切换到默认内容"""
        pass

    def switch_to_alert(self) -> Mock:
        """切换到警告框"""
        return Mock()

    def back(self) -> None:
        """后退"""
        pass

    def forward(self) -> None:
        """前进"""
        pass

    def refresh(self) -> None:
        """刷新"""
        pass

    def maximize_window(self) -> None:
        """最大化窗口"""
        pass

    def set_window_size(self, width: int, height: int) -> None:
        """设置窗口大小"""
        pass

    def set_window_position(self, x: int, y: int) -> None:
        """设置窗口位置"""
        pass

    def get_window_size(self) -> Dict[str, int]:
        """获取窗口大小"""
        return {"width": 1920, "height": 1080}

    def get_window_position(self) -> Dict[str, int]:
        """获取窗口位置"""
        return {"x": 0, "y": 0}

    def get_window_rect(self) -> Dict[str, int]:
        """获取窗口矩形"""
        return {"x": 0, "y": 0, "width": 1920, "height": 1080}

    def set_window_rect(self, x: int, y: int, width: int, height: int) -> None:
        """设置窗口矩形"""
        pass

    @property
    def window_handles(self) -> List[str]:
        """获取所有窗口句柄"""
        return self._window_handles

    @property
    def current_window_handle(self) -> str:
        """获取当前窗口句柄"""
        return self._current_window_handle

    @property
    def session_id(self) -> str:
        """获取会话ID"""
        return "mock_session_id"

    @property
    def capabilities(self) -> Dict[str, Any]:
        """获取浏览器能力"""
        return {
            "browserName": self.browser_type,
            "browserVersion": "1.0.0",
            "platformName": "Windows",
        }


class MockBrowserOptions:
    """Mock浏览器选项类"""

    def __init__(self, browser_type: str = "edge"):
        """初始化Mock浏览器选项

        Args:
            browser_type: 浏览器类型
        """
        self.browser_type = browser_type
        self._arguments = []
        self._preferences = {}
        self._experimental_options = {}
        self._capabilities = {}

    def add_argument(self, argument: str) -> None:
        """添加命令行参数"""
        self._arguments.append(argument)

    def set_preference(self, key: str, value: Any) -> None:
        """设置首选项"""
        self._preferences[key] = value

    def add_experimental_option(self, key: str, value: Any) -> None:
        """添加实验性选项"""
        self._experimental_options[key] = value

    def set_capability(self, key: str, value: Any) -> None:
        """设置能力"""
        self._capabilities[key] = value

    def to_capabilities(self) -> Dict[str, Any]:
        """转换为能力字典"""
        return self._capabilities

    @property
    def arguments(self) -> List[str]:
        """获取所有参数"""
        return self._arguments

    @property
    def preferences(self) -> Dict[str, Any]:
        """获取所有首选项"""
        return self._preferences

    @property
    def experimental_options(self) -> Dict[str, Any]:
        """获取所有实验性选项"""
        return self._experimental_options


class MockBrowserService:
    """Mock浏览器服务类"""

    def __init__(self, executable_path: str = None, port: int = 0):
        """初始化Mock浏览器服务

        Args:
            executable_path: 可执行文件路径
            port: 端口号
        """
        self.executable_path = executable_path
        self.port = port
        self._is_running = False
        self._process = None

    def start(self) -> None:
        """启动服务"""
        self._is_running = True

    def stop(self) -> None:
        """停止服务"""
        self._is_running = False

    @property
    def is_running(self) -> bool:
        """服务是否运行中"""
        return self._is_running

    @property
    def service_url(self) -> str:
        """获取服务URL"""
        return f"http://localhost:{self.port}"


class MockBrowserFactory:
    """Mock浏览器工厂类"""

    def __init__(self):
        """初始化Mock浏览器工厂"""
        self._drivers = {}
        self._options = {}

    def create_driver(
        self, browser_type: str = "edge", options: MockBrowserOptions = None
    ) -> MockWebDriver:
        """创建浏览器驱动

        Args:
            browser_type: 浏览器类型
            options: 浏览器选项

        Returns:
            MockWebDriver实例
        """
        driver = MockWebDriver(browser_type)
        self._drivers[browser_type] = driver
        if options:
            self._options[browser_type] = options
        return driver

    def get_driver(self, browser_type: str) -> Optional[MockWebDriver]:
        """获取浏览器驱动

        Args:
            browser_type: 浏览器类型

        Returns:
            MockWebDriver实例或None
        """
        return self._drivers.get(browser_type)

    def close_all(self) -> None:
        """关闭所有驱动"""
        for driver in self._drivers.values():
            driver.quit()
        self._drivers.clear()

    def create_options(self, browser_type: str = "edge") -> MockBrowserOptions:
        """创建浏览器选项

        Args:
            browser_type: 浏览器类型

        Returns:
            MockBrowserOptions实例
        """
        options = MockBrowserOptions(browser_type)
        self._options[browser_type] = options
        return options


def create_mock_edge_driver(cookies: List[Dict[str, Any]] = None) -> MockWebDriver:
    """创建Mock Edge浏览器驱动

    Args:
        cookies: Cookie列表

    Returns:
        MockWebDriver实例
    """
    driver = MockWebDriver("edge")
    if cookies:
        for cookie in cookies:
            driver.add_cookie(cookie)
    return driver


def create_mock_chrome_driver(cookies: List[Dict[str, Any]] = None) -> MockWebDriver:
    """创建Mock Chrome浏览器驱动

    Args:
        cookies: Cookie列表

    Returns:
        MockWebDriver实例
    """
    driver = MockWebDriver("chrome")
    if cookies:
        for cookie in cookies:
            driver.add_cookie(cookie)
    return driver


def create_mock_firefox_driver(cookies: List[Dict[str, Any]] = None) -> MockWebDriver:
    """创建Mock Firefox浏览器驱动

    Args:
        cookies: Cookie列表

    Returns:
        MockWebDriver实例
    """
    driver = MockWebDriver("firefox")
    if cookies:
        for cookie in cookies:
            driver.add_cookie(cookie)
    return driver


def create_mock_browser_factory() -> MockBrowserFactory:
    """创建Mock浏览器工厂

    Returns:
        MockBrowserFactory实例
    """
    return MockBrowserFactory()
