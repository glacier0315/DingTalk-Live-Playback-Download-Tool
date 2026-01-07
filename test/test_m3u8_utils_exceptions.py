"""测试 m3u8_utils 模块的异常处理"""
import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from dingtalk_download import m3u8_utils


class TestDownloadM3u8FileExceptions:
    """测试 download_m3u8_file 函数的异常处理"""
    
    def test_empty_url_raises_value_error(self):
        """测试空 URL 抛出 ValueError"""
        with pytest.raises(ValueError) as exc_info:
            m3u8_utils.download_m3u8_file("", "test.m3u8", {"User-Agent": "test"})
        
        assert "URL 不能为空" in str(exc_info.value)
    
    def test_none_url_raises_value_error(self):
        """测试 None URL 抛出 ValueError"""
        with pytest.raises(ValueError) as exc_info:
            m3u8_utils.download_m3u8_file(None, "test.m3u8", {"User-Agent": "test"})
        
        assert "URL 不能为空" in str(exc_info.value)
    
    def test_empty_filename_raises_value_error(self):
        """测试空文件名抛出 ValueError"""
        with pytest.raises(ValueError) as exc_info:
            m3u8_utils.download_m3u8_file("http://example.com/test.m3u8", "", {"User-Agent": "test"})
        
        assert "文件名不能为空" in str(exc_info.value)
    
    def test_none_filename_raises_value_error(self):
        """测试 None 文件名抛出 ValueError"""
        with pytest.raises(ValueError) as exc_info:
            m3u8_utils.download_m3u8_file("http://example.com/test.m3u8", None, {"User-Agent": "test"})
        
        assert "文件名不能为空" in str(exc_info.value)
    
    def test_empty_headers_raises_value_error(self):
        """测试空请求头抛出 ValueError"""
        with pytest.raises(ValueError) as exc_info:
            m3u8_utils.download_m3u8_file("http://example.com/test.m3u8", "test.m3u8", {})
        
        assert "请求头不能为空" in str(exc_info.value)
    
    def test_none_headers_raises_value_error(self):
        """测试 None 请求头抛出 ValueError"""
        with pytest.raises(ValueError) as exc_info:
            m3u8_utils.download_m3u8_file("http://example.com/test.m3u8", "test.m3u8", None)
        
        assert "请求头不能为空" in str(exc_info.value)
    
    def test_directory_not_writable_raises_permission_error(self):
        """测试目录不可写抛出 PermissionError"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # 创建一个只读目录
            readonly_dir = os.path.join(tmpdir, "readonly")
            os.makedirs(readonly_dir)
            
            # 在 Windows 上设置只读属性
            if os.name == 'nt':
                import stat
                os.chmod(readonly_dir, stat.S_IREAD)
            else:
                # 在 Unix 系统上设置只读权限
                os.chmod(readonly_dir, 0o444)
            
            filepath = os.path.join(readonly_dir, "test.m3u8")
            
            with pytest.raises((PermissionError, RuntimeError)) as exc_info:
                m3u8_utils.download_m3u8_file(
                    "http://example.com/test.m3u8",
                    filepath,
                    {"User-Agent": "test"}
                )
            
            # 恢复权限以便清理
            if os.name == 'nt':
                os.chmod(readonly_dir, stat.S_IWRITE | stat.S_IREAD)
            else:
                os.chmod(readonly_dir, 0o755)
    
    def test_empty_content_raises_runtime_error(self):
        """测试空内容抛出 RuntimeError"""
        with patch('dingtalk_download.m3u8_utils.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = ""
            mock_get.return_value = mock_response
            
            with tempfile.TemporaryDirectory() as tmpdir:
                filepath = os.path.join(tmpdir, "test.m3u8")
                
                with pytest.raises(RuntimeError) as exc_info:
                    m3u8_utils.download_m3u8_file(
                        "http://example.com/test.m3u8",
                        filepath,
                        {"User-Agent": "test"}
                    )
                
                assert "下载的 M3U8 内容为空" in str(exc_info.value)
    
    def test_none_content_raises_runtime_error(self):
        """测试 None 内容抛出 RuntimeError"""
        with patch('dingtalk_download.m3u8_utils.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = None
            mock_get.return_value = mock_response
            
            with tempfile.TemporaryDirectory() as tmpdir:
                filepath = os.path.join(tmpdir, "test.m3u8")
                
                with pytest.raises(RuntimeError) as exc_info:
                    m3u8_utils.download_m3u8_file(
                        "http://example.com/test.m3u8",
                        filepath,
                        {"User-Agent": "test"}
                    )
                
                assert "下载的 M3U8 内容为空" in str(exc_info.value)
    
    def test_successful_download_with_valid_parameters(self):
        """测试有效参数成功下载"""
        test_content = "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:10\n"
        
        with patch('dingtalk_download.m3u8_utils.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = test_content
            mock_get.return_value = mock_response
            
            with tempfile.TemporaryDirectory() as tmpdir:
                filepath = os.path.join(tmpdir, "test.m3u8")
                
                result = m3u8_utils.download_m3u8_file(
                    "http://example.com/test.m3u8",
                    filepath,
                    {"User-Agent": "test"}
                )
                
                assert result == filepath
                assert os.path.exists(filepath)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    assert content == test_content
    
    def test_creates_directory_if_not_exists(self):
        """测试自动创建不存在的目录"""
        test_content = "#EXTM3U\n#EXT-X-VERSION:3\n"
        
        with patch('dingtalk_download.m3u8_utils.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = test_content
            mock_get.return_value = mock_response
            
            with tempfile.TemporaryDirectory() as tmpdir:
                new_dir = os.path.join(tmpdir, "new", "nested", "dir")
                filepath = os.path.join(new_dir, "test.m3u8")
                
                assert not os.path.exists(new_dir)
                
                result = m3u8_utils.download_m3u8_file(
                    "http://example.com/test.m3u8",
                    filepath,
                    {"User-Agent": "test"}
                )
                
                assert result == filepath
                assert os.path.exists(new_dir)
                assert os.path.exists(filepath)
    
    def test_execute_script_exception_raises_runtime_error(self):
        """测试 requests 异常抛出 RuntimeError"""
        import requests
        
        with patch('dingtalk_download.m3u8_utils.requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("网络请求失败")
            
            with tempfile.TemporaryDirectory() as tmpdir:
                filepath = os.path.join(tmpdir, "test.m3u8")
                
                with pytest.raises(RuntimeError) as exc_info:
                    m3u8_utils.download_m3u8_file(
                        "http://example.com/test.m3u8",
                        filepath,
                        {"User-Agent": "test"}
                    )
                
                assert "获取 M3U8 内容失败" in str(exc_info.value)
                assert "网络请求失败" in str(exc_info.value)
