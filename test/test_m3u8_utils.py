"""M3U8处理测试模块"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dingtalk_download.m3u8_utils import extract_prefix


class TestExtractPrefix:
    """测试extract_prefix函数"""
    
    def test_extract_prefix_from_m3u8_url(self):
        """测试从M3U8 URL提取前缀"""
        url = "https://example.com/live_hp/abc123-def456-789abc/chunklist.m3u8"
        result = extract_prefix(url)
        assert result == "https://example.com/live_hp/abc123-def456-789abc"
    
    def test_return_original_url_if_no_match(self):
        """测试没有匹配时返回原始URL"""
        url = "https://example.com/some/path/file.m3u8"
        result = extract_prefix(url)
        assert result == url
