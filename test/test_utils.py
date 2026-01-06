"""通用功能测试模块"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dingtalk_download.utils import validate_input, clean_file_path


class TestValidateInput:
    """测试validate_input函数"""
    
    def test_default_option_returned_when_empty_input(self, monkeypatch):
        """测试空输入时返回默认选项"""
        monkeypatch.setattr('builtins.input', lambda x: '')
        result = validate_input("请选择: ", ['1', '2'], default_option='1')
        assert result == '1'
    
    def test_valid_option_returned(self, monkeypatch):
        """测试有效选项被正确返回"""
        inputs = iter(['2'])
        monkeypatch.setattr('builtins.input', lambda x: next(inputs))
        result = validate_input("请选择: ", ['1', '2'])
        assert result == '2'
    
    def test_invalid_input_reprompts(self, monkeypatch):
        """测试无效输入会重新提示"""
        inputs = iter(['3', '1'])
        input_mock = lambda x: next(inputs)
        monkeypatch.setattr('builtins.input', input_mock)
        result = validate_input("请选择: ", ['1', '2'])
        assert result == '1'


class TestCleanFilePath:
    """测试clean_file_path函数"""
    
    def test_removes_surrounding_whitespace(self):
        """测试去除首尾空白"""
        result = clean_file_path("  /path/to/file  ")
        assert result == "/path/to/file"
    
    def test_removes_double_quotes(self):
        """测试去除双引号"""
        result = clean_file_path('"/path/to/file"')
        assert result == "/path/to/file"
    
    def test_removes_single_quotes(self):
        """测试去除单引号"""
        result = clean_file_path("'/path/to/file'")
        assert result == "/path/to/file"
    
    def test_combined_cleanup(self):
        """测试组合清理"""
        result = clean_file_path('  "\'/path/to/file\'"  ')
        assert result == "/path/to/file"
