"""浏览器测试Fixture模块

提供浏览器相关的测试fixture，包括mock浏览器驱动和浏览器工厂。
"""

import pytest
from unittest.mock import MagicMock, Mock


@pytest.fixture
def mock_edge_driver():
    """Mock Edge浏览器驱动"""
    mock_driver = MagicMock()
    mock_driver.get_cookies.return_value = [
        {"name": "test_cookie", "value": "test_value", "domain": ".dingtalk.com"}
    ]
    mock_driver.current_url = "https://live.dingtalk.com/test"
    mock_driver.title = "Test Live Page"
    return mock_driver


@pytest.fixture
def mock_chrome_driver():
    """Mock Chrome浏览器驱动"""
    mock_driver = MagicMock()
    mock_driver.get_cookies.return_value = [
        {"name": "chrome_cookie", "value": "chrome_value", "domain": ".dingtalk.com"}
    ]
    mock_driver.current_url = "https://live.dingtalk.com/test"
    mock_driver.title = "Test Live Page"
    return mock_driver


@pytest.fixture
def mock_firefox_driver():
    """Mock Firefox浏览器驱动"""
    mock_driver = MagicMock()
    mock_driver.get_cookies.return_value = [
        {"name": "firefox_cookie", "value": "firefox_value", "domain": ".dingtalk.com"}
    ]
    mock_driver.current_url = "https://live.dingtalk.com/test"
    mock_driver.title = "Test Live Page"
    return mock_driver


@pytest.fixture
def mock_browser_factory():
    """Mock浏览器工厂"""
    mock_factory = MagicMock()
    mock_driver = MagicMock()
    mock_driver.get_cookies.return_value = [
        {"name": "factory_cookie", "value": "factory_value", "domain": ".dingtalk.com"}
    ]
    mock_factory.create_driver.return_value = mock_driver
    return mock_factory


@pytest.fixture
def mock_selenium_options():
    """Mock Selenium浏览器选项"""
    mock_options = MagicMock()
    mock_options.add_argument = MagicMock()
    mock_options.set_preference = MagicMock()
    return mock_options


@pytest.fixture
def mock_webdriver(mocker):
    """Mock Selenium WebDriver"""
    mock_webdriver = mocker.MagicMock()
    mock_webdriver.Chrome = MagicMock(return_value=MagicMock())
    mock_webdriver.Firefox = MagicMock(return_value=MagicMock())
    mock_webdriver.Edge = MagicMock(return_value=MagicMock())
    return mock_webdriver


@pytest.fixture
def sample_cookies():
    """示例Cookie数据"""
    return [
        {"name": "session_id", "value": "abc123", "domain": ".dingtalk.com", "path": "/"},
        {"name": "user_token", "value": "token456", "domain": ".dingtalk.com", "path": "/"},
        {"name": "csrf_token", "value": "csrf789", "domain": ".dingtalk.com", "path": "/"},
    ]


@pytest.fixture
def sample_live_url():
    """示例直播URL"""
    return "https://live.dingtalk.com/123456789"


@pytest.fixture
def sample_live_page_content():
    """示例直播页面内容"""
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Test Live Page</title></head>
    <body>
        <div class="live-info">
            <h1>Test Live Stream</h1>
            <div class="live-name">测试直播</div>
        </div>
    </body>
    </html>
    """
