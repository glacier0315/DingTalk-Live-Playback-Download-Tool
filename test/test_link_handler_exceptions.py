"""测试 link_handler 模块的异常处理"""
import pytest
from dingtalk_download import link_handler


class TestCleanFilePathExceptions:
    """测试 clean_file_path 函数的异常处理"""
    
    def test_empty_string_raises_value_error(self):
        """测试空字符串抛出 ValueError"""
        with pytest.raises(ValueError) as exc_info:
            link_handler.clean_file_path("")
        
        assert "文件路径不能为空" in str(exc_info.value)
    
    def test_none_raises_value_error(self):
        """测试 None 抛出 ValueError"""
        with pytest.raises(ValueError) as exc_info:
            link_handler.clean_file_path(None)
        
        assert "文件路径不能为空" in str(exc_info.value)
    
    def test_whitespace_only_raises_value_error(self):
        """测试仅空白字符抛出 ValueError"""
        with pytest.raises(ValueError) as exc_info:
            link_handler.clean_file_path("   ")
        
        assert "清理后的文件路径为空" in str(exc_info.value)
    
    def test_non_string_type_raises_value_error(self):
        """测试非字符串类型抛出 ValueError"""
        with pytest.raises(ValueError) as exc_info:
            link_handler.clean_file_path(123)
        
        assert "文件路径必须是字符串类型" in str(exc_info.value)
    
    def test_list_type_raises_value_error(self):
        """测试列表类型抛出 ValueError"""
        with pytest.raises(ValueError) as exc_info:
            link_handler.clean_file_path(["path"])
        
        assert "文件路径必须是字符串类型" in str(exc_info.value)
    
    def test_dict_type_raises_value_error(self):
        """测试字典类型抛出 ValueError"""
        with pytest.raises(ValueError) as exc_info:
            link_handler.clean_file_path({"path": "value"})
        
        assert "文件路径必须是字符串类型" in str(exc_info.value)
    
    def test_removes_double_quotes(self):
        """测试移除双引号"""
        result = link_handler.clean_file_path('"path/to/file.csv"')
        assert result == "path/to/file.csv"
    
    def test_removes_single_quotes(self):
        """测试移除单引号"""
        result = link_handler.clean_file_path("'path/to/file.csv'")
        assert result == "path/to/file.csv"
    
    def test_removes_whitespace(self):
        """测试移除周围空白"""
        result = link_handler.clean_file_path("  path/to/file.csv  ")
        assert result == "path/to/file.csv"
    
    def test_removes_combined_quotes_and_whitespace(self):
        """测试移除组合的引号和空白"""
        result = link_handler.clean_file_path('  "path/to/file.csv"  ')
        assert result == "path/to/file.csv"
    
    def test_valid_path_unchanged(self):
        """测试有效路径保持不变"""
        result = link_handler.clean_file_path("path/to/file.csv")
        assert result == "path/to/file.csv"
    
    def test_path_with_spaces_inside(self):
        """测试保留内部空格"""
        result = link_handler.clean_file_path("path/to/my file.csv")
        assert result == "path/to/my file.csv"
    
    def test_windows_path(self):
        """测试 Windows 路径"""
        result = link_handler.clean_file_path('C:\\Users\\Test\\file.csv')
        assert result == "C:\\Users\\Test\\file.csv"
    
    def test_windows_path_with_quotes(self):
        """测试带引号的 Windows 路径"""
        result = link_handler.clean_file_path('"C:\\Users\\Test\\file.csv"')
        assert result == "C:\\Users\\Test\\file.csv"


class TestExtractLiveUuidExceptions:
    """测试 extract_live_uuid 函数的异常处理"""
    
    def test_extract_from_valid_url(self):
        """测试从有效 URL 提取 liveUuid"""
        url = "https://n.dingtalk.com/live_hp/abc123?liveUuid=xyz789&other=value"
        result = link_handler.extract_live_uuid(url)
        assert result == "xyz789"
    
    def test_returns_none_for_missing_liveUuid(self):
        """测试缺少 liveUuid 时返回 None"""
        url = "https://n.dingtalk.com/live_hp/abc123?other=value"
        result = link_handler.extract_live_uuid(url)
        assert result is None
    
    def test_returns_none_for_empty_query(self):
        """测试空查询参数时返回 None"""
        url = "https://n.dingtalk.com/live_hp/abc123"
        result = link_handler.extract_live_uuid(url)
        assert result is None
    
    def test_handles_multiple_liveUuid_values(self):
        """测试处理多个 liveUuid 值（返回第一个）"""
        url = "https://n.dingtalk.com/live_hp/abc123?liveUuid=first&liveUuid=second"
        result = link_handler.extract_live_uuid(url)
        assert result == "first"
    
    def test_handles_url_encoded_uuid(self):
        """测试处理 URL 编码的 UUID"""
        url = "https://n.dingtalk.com/live_hp/abc123?liveUuid=test%20uuid"
        result = link_handler.extract_live_uuid(url)
        assert result == "test uuid"
