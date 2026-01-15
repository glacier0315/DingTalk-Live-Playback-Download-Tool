"""
钉钉直播回放下载工具 - validator 单元测试

本模块测试输入验证工具函数。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
"""

import sys
import os
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.utils.validator import validate_input


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
