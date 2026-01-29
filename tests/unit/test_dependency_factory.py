"""
钉钉直播回放下载工具 - dependency_factory 单元测试

本模块测试依赖工厂类。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2026-01-28
修改历史：
    - 2026-01-28: 初始版本
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.core.dependency_factory import DependencyFactory
from dingtalk_downloader.config.constants import BROWSER_TYPE_EDGE


@pytest.fixture
def dependency_factory():
    """创建依赖工厂实例"""
    return DependencyFactory()


@pytest.fixture
def mock_browser_driver():
    """创建模拟的浏览器驱动"""
    browser = Mock()
    browser.get_cookies.return_value = [{"name": "test", "value": "value"}]
    return browser


def test_dependency_factory_init(dependency_factory):
    """测试依赖工厂初始化"""
    assert dependency_factory._instances == {}
    assert dependency_factory.get_instance_count() == 0


@patch("dingtalk_downloader.core.dependency_factory.CookieHandler")
def test_get_cookie_handler_first_call(mock_cookie_handler_class, dependency_factory):
    """测试首次获取Cookie处理器"""
    mock_cookie_handler = Mock()
    mock_cookie_handler_class.return_value = mock_cookie_handler

    result = dependency_factory.get_cookie_handler(BROWSER_TYPE_EDGE)

    assert result == mock_cookie_handler
    mock_cookie_handler_class.assert_called_once_with(BROWSER_TYPE_EDGE)
    assert dependency_factory.get_instance_count() == 1


@patch("dingtalk_downloader.core.dependency_factory.CookieHandler")
def test_get_cookie_handler_cached(mock_cookie_handler_class, dependency_factory):
    """测试获取缓存的Cookie处理器"""
    mock_cookie_handler = Mock()
    mock_cookie_handler_class.return_value = mock_cookie_handler

    result1 = dependency_factory.get_cookie_handler(BROWSER_TYPE_EDGE)
    result2 = dependency_factory.get_cookie_handler(BROWSER_TYPE_EDGE)

    assert result1 == result2
    mock_cookie_handler_class.assert_called_once()
    assert dependency_factory.get_instance_count() == 1


@patch("dingtalk_downloader.core.dependency_factory.CookieHandler")
def test_get_cookie_handler_different_browser(mock_cookie_handler_class, dependency_factory):
    """测试获取不同浏览器的Cookie处理器"""
    mock_cookie_handler_edge = Mock()
    mock_cookie_handler_chrome = Mock()

    def cookie_handler_side_effect(browser_type):
        if browser_type == "edge":
            return mock_cookie_handler_edge
        elif browser_type == "chrome":
            return mock_cookie_handler_chrome
        return Mock()

    mock_cookie_handler_class.side_effect = cookie_handler_side_effect

    result_edge = dependency_factory.get_cookie_handler("edge")
    result_chrome = dependency_factory.get_cookie_handler("chrome")

    assert result_edge == mock_cookie_handler_edge
    assert result_chrome == mock_cookie_handler_chrome
    assert result_edge != result_chrome
    assert dependency_factory.get_instance_count() == 2


@patch("dingtalk_downloader.core.dependency_factory.M3u8Parser")
def test_get_m3u8_parser_first_call(mock_m3u8_parser_class, dependency_factory, mock_browser_driver):
    """测试首次获取m3u8解析器"""
    mock_m3u8_parser = Mock()
    mock_m3u8_parser_class.return_value = mock_m3u8_parser

    result = dependency_factory.get_m3u8_parser(mock_browser_driver)

    assert result == mock_m3u8_parser
    mock_m3u8_parser_class.assert_called_once_with(mock_browser_driver)
    assert dependency_factory.get_instance_count() == 1


@patch("dingtalk_downloader.core.dependency_factory.M3u8Parser")
def test_get_m3u8_parser_cached(mock_m3u8_parser_class, dependency_factory, mock_browser_driver):
    """测试获取缓存的m3u8解析器"""
    mock_m3u8_parser = Mock()
    mock_m3u8_parser_class.return_value = mock_m3u8_parser

    result1 = dependency_factory.get_m3u8_parser(mock_browser_driver)
    result2 = dependency_factory.get_m3u8_parser(mock_browser_driver)

    assert result1 == result2
    mock_m3u8_parser_class.assert_called_once()
    assert dependency_factory.get_instance_count() == 1


@patch("dingtalk_downloader.core.dependency_factory.M3u8Parser")
def test_get_m3u8_parser_different_driver(mock_m3u8_parser_class, dependency_factory):
    """测试获取不同浏览器驱动的m3u8解析器"""
    mock_m3u8_parser1 = Mock()
    mock_m3u8_parser2 = Mock()

    call_count = [0]

    def m3u8_parser_side_effect(browser_driver):
        call_count[0] += 1
        if call_count[0] == 1:
            return mock_m3u8_parser1
        else:
            return mock_m3u8_parser2

    mock_m3u8_parser_class.side_effect = m3u8_parser_side_effect

    browser_driver1 = Mock()
    browser_driver2 = Mock()

    result1 = dependency_factory.get_m3u8_parser(browser_driver1)
    result2 = dependency_factory.get_m3u8_parser(browser_driver2)

    assert result1 == mock_m3u8_parser1
    assert result2 == mock_m3u8_parser2
    assert result1 != result2
    assert dependency_factory.get_instance_count() == 2


@patch("dingtalk_downloader.core.dependency_factory.PathSelector")
def test_get_path_selector_first_call(mock_path_selector_class, dependency_factory):
    """测试首次获取路径选择器"""
    mock_path_selector = Mock()
    mock_path_selector_class.return_value = mock_path_selector

    result = dependency_factory.get_path_selector("1")

    assert result == mock_path_selector
    mock_path_selector_class.assert_called_once_with("1")
    assert dependency_factory.get_instance_count() == 1


@patch("dingtalk_downloader.core.dependency_factory.PathSelector")
def test_get_path_selector_cached(mock_path_selector_class, dependency_factory):
    """测试获取缓存的路径选择器"""
    mock_path_selector = Mock()
    mock_path_selector_class.return_value = mock_path_selector

    result1 = dependency_factory.get_path_selector("1")
    result2 = dependency_factory.get_path_selector("1")

    assert result1 == result2
    mock_path_selector_class.assert_called_once()
    assert dependency_factory.get_instance_count() == 1


@patch("dingtalk_downloader.core.dependency_factory.PathSelector")
def test_get_path_selector_different_mode(mock_path_selector_class, dependency_factory):
    """测试获取不同保存模式的路径选择器"""
    mock_path_selector1 = Mock()
    mock_path_selector2 = Mock()

    def path_selector_side_effect(save_mode):
        if save_mode == "1":
            return mock_path_selector1
        elif save_mode == "2":
            return mock_path_selector2
        return Mock()

    mock_path_selector_class.side_effect = path_selector_side_effect

    result1 = dependency_factory.get_path_selector("1")
    result2 = dependency_factory.get_path_selector("2")

    assert result1 == mock_path_selector1
    assert result2 == mock_path_selector2
    assert result1 != result2
    assert dependency_factory.get_instance_count() == 2


@patch("dingtalk_downloader.core.dependency_factory.NM3u8DLRE")
def test_get_n_m3u8dl_re_first_call(mock_n_m3u8dl_re_class, dependency_factory):
    """测试首次获取NM3u8DLRE实例"""
    mock_n_m3u8dl_re = Mock()
    mock_n_m3u8dl_re_class.return_value = mock_n_m3u8dl_re

    result = dependency_factory.get_n_m3u8dl_re()

    assert result == mock_n_m3u8dl_re
    mock_n_m3u8dl_re_class.assert_called_once()
    assert dependency_factory.get_instance_count() == 1


@patch("dingtalk_downloader.core.dependency_factory.NM3u8DLRE")
def test_get_n_m3u8dl_re_cached(mock_n_m3u8dl_re_class, dependency_factory):
    """测试获取缓存的NM3u8DLRE实例"""
    mock_n_m3u8dl_re = Mock()
    mock_n_m3u8dl_re_class.return_value = mock_n_m3u8dl_re

    result1 = dependency_factory.get_n_m3u8dl_re()
    result2 = dependency_factory.get_n_m3u8dl_re()

    assert result1 == result2
    mock_n_m3u8dl_re_class.assert_called_once()
    assert dependency_factory.get_instance_count() == 1


@patch("dingtalk_downloader.core.dependency_factory.M3u8DownloadService")
def test_get_m3u8_download_service_first_call(
    mock_m3u8_download_service_class, dependency_factory, mock_browser_driver
):
    """测试首次获取m3u8下载服务"""
    mock_m3u8_parser = Mock()
    mock_m3u8_download_service = Mock()
    mock_m3u8_download_service_class.return_value = mock_m3u8_download_service

    with patch.object(
        dependency_factory,
        "get_m3u8_parser",
        return_value=mock_m3u8_parser,
    ):
        result = dependency_factory.get_m3u8_download_service(mock_browser_driver)

    assert result == mock_m3u8_download_service
    mock_m3u8_download_service_class.assert_called_once()
    assert dependency_factory.get_instance_count() == 1


@patch("dingtalk_downloader.core.dependency_factory.M3u8DownloadService")
def test_get_m3u8_download_service_cached(
    mock_m3u8_download_service_class, dependency_factory, mock_browser_driver
):
    """测试获取缓存的m3u8下载服务"""
    mock_m3u8_parser = Mock()
    mock_m3u8_download_service = Mock()
    mock_m3u8_download_service_class.return_value = mock_m3u8_download_service

    with patch.object(dependency_factory, "get_m3u8_parser", return_value=mock_m3u8_parser):
        result1 = dependency_factory.get_m3u8_download_service(mock_browser_driver)
        result2 = dependency_factory.get_m3u8_download_service(mock_browser_driver)

    assert result1 == result2
    mock_m3u8_download_service_class.assert_called_once()
    assert dependency_factory.get_instance_count() == 1


@patch("dingtalk_downloader.core.dependency_factory.M3u8DownloadService")
def test_get_m3u8_download_service_different_parser(
    mock_m3u8_download_service_class, dependency_factory
):
    """测试获取不同解析器的m3u8下载服务"""
    mock_m3u8_parser1 = Mock()
    mock_m3u8_parser2 = Mock()
    mock_m3u8_download_service1 = Mock()
    mock_m3u8_download_service2 = Mock()

    call_count = [0]

    def m3u8_download_service_side_effect(m3u8_parser):
        call_count[0] += 1
        if call_count[0] == 1:
            return mock_m3u8_download_service1
        else:
            return mock_m3u8_download_service2

    mock_m3u8_download_service_class.side_effect = m3u8_download_service_side_effect

    browser_driver1 = Mock()
    browser_driver2 = Mock()

    with patch.object(
        dependency_factory,
        "get_m3u8_parser",
        side_effect=[mock_m3u8_parser1, mock_m3u8_parser2],
    ):
        result1 = dependency_factory.get_m3u8_download_service(browser_driver1)
        result2 = dependency_factory.get_m3u8_download_service(browser_driver2)

    assert result1 == mock_m3u8_download_service1
    assert result2 == mock_m3u8_download_service2
    assert result1 != result2
    assert dependency_factory.get_instance_count() == 2


def test_clear_instances(dependency_factory):
    """测试清除所有缓存的实例"""
    dependency_factory._instances = {"test": Mock()}

    dependency_factory.clear_instances()

    assert dependency_factory._instances == {}
    assert dependency_factory.get_instance_count() == 0


def test_get_instance_count(dependency_factory):
    """测试获取实例数量"""
    assert dependency_factory.get_instance_count() == 0

    dependency_factory._instances = {"test1": Mock(), "test2": Mock()}

    assert dependency_factory.get_instance_count() == 2


@patch("dingtalk_downloader.core.dependency_factory.CookieHandler")
@patch("dingtalk_downloader.core.dependency_factory.PathSelector")
@patch("dingtalk_downloader.core.dependency_factory.NM3u8DLRE")
def test_multiple_dependencies_cached(
    mock_n_m3u8dl_re_class,
    mock_path_selector_class,
    mock_cookie_handler_class,
    dependency_factory,
):
    """测试多个依赖实例的缓存"""
    mock_cookie_handler = Mock()
    mock_path_selector = Mock()
    mock_n_m3u8dl_re = Mock()

    mock_cookie_handler_class.return_value = mock_cookie_handler
    mock_path_selector_class.return_value = mock_path_selector
    mock_n_m3u8dl_re_class.return_value = mock_n_m3u8dl_re

    dependency_factory.get_cookie_handler(BROWSER_TYPE_EDGE)
    dependency_factory.get_path_selector("1")
    dependency_factory.get_n_m3u8dl_re()

    assert dependency_factory.get_instance_count() == 3

    result1 = dependency_factory.get_cookie_handler(BROWSER_TYPE_EDGE)
    result2 = dependency_factory.get_path_selector("1")
    result3 = dependency_factory.get_n_m3u8dl_re()

    assert result1 == mock_cookie_handler
    assert result2 == mock_path_selector
    assert result3 == mock_n_m3u8dl_re

    assert dependency_factory.get_instance_count() == 3
