"""
钉钉直播回放下载工具 - validator 单元测试

本模块测试输入验证工具函数。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2026-01-22: 新增URL验证测试
"""

import sys
import os
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.utils.validator import validate_input, validate_dingtalk_url


@patch("builtins.input")
def test_validate_input_valid_option(mock_input):
    """测试验证有效输入"""
    mock_input.return_value = "1"
    result = validate_input("请选择: ", ["1", "2", "3"])
    assert result == "1"


@patch("builtins.input")
def test_validate_input_default_option(mock_input):
    """测试验证默认选项"""
    mock_input.return_value = ""
    result = validate_input("请选择: ", ["1", "2", "3"], default_option="1")
    assert result == "1"


@patch("builtins.input")
@patch("builtins.print")
def test_validate_input_invalid_option(mock_print, mock_input):
    """测试验证无效输入"""
    mock_input.side_effect = ["4", "1"]
    result = validate_input("请选择: ", ["1", "2", "3"])
    assert result == "1"
    assert mock_print.call_count == 1


@patch("builtins.input")
@patch("builtins.print")
def test_validate_input_eof_error_with_default(mock_print, mock_input):
    """测试 EOFError - 有默认选项"""
    mock_input.side_effect = EOFError()
    result = validate_input("请选择: ", ["1", "2", "3"], default_option="1")
    assert result == "1"
    mock_print.assert_called()


@patch("builtins.input")
def test_validate_input_eof_error_without_default(mock_input):
    """测试 EOFError - 无默认选项"""
    mock_input.side_effect = EOFError()
    with pytest.raises(EOFError):
        validate_input("请选择: ", ["1", "2", "3"])


@patch("builtins.input")
@patch("builtins.print")
def test_validate_input_keyboard_interrupt(mock_print, mock_input):
    """测试 KeyboardInterrupt"""
    mock_input.side_effect = KeyboardInterrupt()
    with pytest.raises(KeyboardInterrupt):
        validate_input("请选择: ", ["1", "2", "3"])
    mock_print.assert_called()


def test_validate_dingtalk_url_valid_https():
    """测试验证有效的HTTPS钉钉直播链接"""
    url = "https://n.dingtalk.com/d/live/1234567890abcdef1234567890abcdef?liveUuid=12345678-1234-1234-1234-1234567890ab"
    result = validate_dingtalk_url(url)
    assert result == url


def test_validate_dingtalk_url_valid_http():
    """测试验证有效的HTTP钉钉直播链接"""
    url = "http://n.dingtalk.com/d/live/1234567890abcdef1234567890abcdef?liveUuid=12345678-1234-1234-1234-1234567890ab"
    result = validate_dingtalk_url(url)
    assert result == url


def test_validate_dingtalk_url_missing_scheme():
    """测试验证缺少协议的URL"""
    url = "n.dingtalk.com/d/live/1234567890abcdef1234567890abcdef?liveUuid=12345678-1234-1234-1234-1234567890ab"
    with pytest.raises(ValueError) as exc_info:
        validate_dingtalk_url(url)
    assert "URL缺少协议" in str(exc_info.value)


def test_validate_dingtalk_url_invalid_scheme():
    """测试验证无效协议的URL"""
    url = "ftp://n.dingtalk.com/d/live/1234567890abcdef1234567890abcdef?liveUuid=12345678-1234-1234-1234-1234567890ab"
    with pytest.raises(ValueError) as exc_info:
        validate_dingtalk_url(url)
    assert "仅支持 http 和 https 协议" in str(exc_info.value)


def test_validate_dingtalk_url_missing_netloc():
    """测试验证缺少域名的URL"""
    url = "https:///d/live/1234567890abcdef1234567890abcdef?liveUuid=12345678-1234-1234-1234-1234567890ab"
    with pytest.raises(ValueError) as exc_info:
        validate_dingtalk_url(url)
    assert "URL缺少域名" in str(exc_info.value)


def test_validate_dingtalk_url_invalid_netloc():
    """测试验证无效域名的URL"""
    url = "https://example.com/d/live/1234567890abcdef1234567890abcdef?liveUuid=12345678-1234-1234-1234-1234567890ab"
    with pytest.raises(ValueError) as exc_info:
        validate_dingtalk_url(url)
    assert "仅支持钉钉直播链接 (n.dingtalk.com)" in str(exc_info.value)


def test_validate_dingtalk_url_missing_path():
    """测试验证缺少路径的URL"""
    url = "https://n.dingtalk.com?liveUuid=12345678-1234-1234-1234-1234567890ab"
    with pytest.raises(ValueError) as exc_info:
        validate_dingtalk_url(url)
    assert "URL缺少路径" in str(exc_info.value)


def test_validate_dingtalk_url_missing_live_uuid():
    """测试验证缺少liveUuid参数的URL"""
    url = "https://n.dingtalk.com/d/live/1234567890abcdef1234567890abcdef"
    with pytest.raises(ValueError) as exc_info:
        validate_dingtalk_url(url)
    assert "链接缺少 liveUuid 参数" in str(exc_info.value)


def test_validate_dingtalk_url_empty_live_uuid():
    """测试验证liveUuid参数为空的URL"""
    url = "https://n.dingtalk.com/d/live/1234567890abcdef1234567890abcdef?liveUuid="
    with pytest.raises(ValueError):
        validate_dingtalk_url(url)


def test_validate_dingtalk_url_invalid_live_uuid_format():
    """测试验证liveUuid格式无效的URL"""
    url = "https://n.dingtalk.com/d/live/1234567890abcdef1234567890abcdef?liveUuid=invalid-uuid"
    with pytest.raises(ValueError) as exc_info:
        validate_dingtalk_url(url)
    assert "liveUuid 格式无效" in str(exc_info.value)


def test_validate_dingtalk_url_invalid_live_uuid_too_short():
    """测试验证liveUuid过短的URL"""
    url = "https://n.dingtalk.com/d/live/1234567890abcdef1234567890abcdef?liveUuid=123"
    with pytest.raises(ValueError) as exc_info:
        validate_dingtalk_url(url)
    assert "liveUuid 格式无效" in str(exc_info.value)


def test_validate_dingtalk_url_valid_live_uuid_lowercase():
    """测试验证liveUuid为小写的URL"""
    url = "https://n.dingtalk.com/d/live/1234567890abcdef1234567890abcdef?liveUuid=12345678-1234-1234-1234-1234567890ab"
    result = validate_dingtalk_url(url)
    assert result == url


def test_validate_dingtalk_url_valid_live_uuid_uppercase():
    """测试验证liveUuid包含大写的URL"""
    url = "https://n.dingtalk.com/d/live/1234567890abcdef1234567890abcdef?liveUuid=12345678-1234-1234-1234-1234567890AB"
    with pytest.raises(ValueError) as exc_info:
        validate_dingtalk_url(url)
    assert "liveUuid 格式无效" in str(exc_info.value)
