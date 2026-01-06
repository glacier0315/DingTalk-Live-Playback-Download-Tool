"""测试 utils 模块的异常处理"""
import pytest
from unittest.mock import patch, MagicMock
from dingtalk_download import utils


class TestValidateInputExceptions:
    """测试 validate_input 函数的异常处理"""
    
    def test_empty_prompt_raises_value_error(self):
        """测试空提示信息抛出 ValueError"""
        with pytest.raises(ValueError) as exc_info:
            utils.validate_input("", ['1', '2'])
        
        assert "提示信息不能为空" in str(exc_info.value)
    
    def test_none_prompt_raises_value_error(self):
        """测试 None 提示信息抛出 ValueError"""
        with pytest.raises(ValueError) as exc_info:
            utils.validate_input(None, ['1', '2'])
        
        assert "提示信息不能为空" in str(exc_info.value)
    
    def test_non_string_prompt_raises_type_error(self):
        """测试非字符串提示信息抛出 TypeError"""
        with pytest.raises(TypeError) as exc_info:
            utils.validate_input(123, ['1', '2'])
        
        assert "提示信息必须是字符串类型" in str(exc_info.value)
    
    def test_empty_valid_options_raises_value_error(self):
        """测试空有效选项列表抛出 ValueError"""
        with pytest.raises(ValueError) as exc_info:
            utils.validate_input("请选择:", [])
        
        assert "有效选项列表不能为空" in str(exc_info.value)
    
    def test_none_valid_options_raises_type_error(self):
        """测试 None 有效选项列表抛出 TypeError"""
        with pytest.raises(TypeError) as exc_info:
            utils.validate_input("请选择:", None)
        
        assert "有效选项必须是列表类型" in str(exc_info.value)
    
    def test_non_list_valid_options_raises_type_error(self):
        """测试非列表有效选项抛出 TypeError"""
        with pytest.raises(TypeError) as exc_info:
            utils.validate_input("请选择:", "1,2")
        
        assert "有效选项必须是列表类型" in str(exc_info.value)
    
    def test_default_option_not_in_valid_options_raises_value_error(self):
        """测试默认选项不在有效选项中抛出 ValueError"""
        with pytest.raises(ValueError) as exc_info:
            utils.validate_input("请选择:", ['1', '2'], '3')
        
        assert "默认选项 '3' 不在有效选项列表中" in str(exc_info.value)
    
    @patch('builtins.input', return_value='1')
    def test_valid_option_returns_choice(self, mock_input):
        """测试有效选项返回选择"""
        result = utils.validate_input("请选择:", ['1', '2', '3'])
        assert result == '1'
    
    @patch('builtins.input', return_value='')
    def test_empty_input_returns_default_option(self, mock_input):
        """测试空输入返回默认选项"""
        result = utils.validate_input("请选择:", ['1', '2', '3'], '1')
        assert result == '1'
    
    @patch('builtins.input', side_effect=['invalid', '2'])
    def test_invalid_input_prompts_retry(self, mock_input):
        """测试无效输入提示重试"""
        result = utils.validate_input("请选择:", ['1', '2', '3'])
        assert result == '2'
        assert mock_input.call_count == 2


class TestGetExecutableNameExceptions:
    """测试 get_executable_name 函数的异常处理"""
    
    @patch('dingtalk_download.utils.platform.system', return_value='Windows')
    def test_windows_returns_correct_name(self, mock_system):
        """测试 Windows 返回正确的可执行文件名"""
        result = utils.get_executable_name()
        assert result == 'N_m3u8DL-RE.exe'
    
    @patch('dingtalk_download.utils.platform.system', return_value='Linux')
    def test_linux_returns_correct_name(self, mock_system):
        """测试 Linux 返回正确的可执行文件名"""
        result = utils.get_executable_name()
        assert result == './N_m3u8DL-RE'
    
    @patch('dingtalk_download.utils.platform.system', return_value='Darwin')
    def test_macos_returns_correct_name(self, mock_system):
        """测试 macOS (Darwin) 返回正确的可执行文件名"""
        result = utils.get_executable_name()
        assert result == './N_m3u8DL-RE'
    
    @patch('dingtalk_download.utils.platform.system', return_value='UnsupportedOS')
    def test_unsupported_os_raises_runtime_error(self, mock_system):
        """测试不支持的操作系统抛出 RuntimeError"""
        with pytest.raises(RuntimeError) as exc_info:
            utils.get_executable_name()
        
        assert "不支持的操作系统: UnsupportedOS" in str(exc_info.value)
    
    @patch('dingtalk_download.utils.platform.system', return_value='')
    def test_empty_os_raises_runtime_error(self, mock_system):
        """测试空操作系统抛出 RuntimeError"""
        with pytest.raises(RuntimeError) as exc_info:
            utils.get_executable_name()
        
        assert "不支持的操作系统:" in str(exc_info.value)
