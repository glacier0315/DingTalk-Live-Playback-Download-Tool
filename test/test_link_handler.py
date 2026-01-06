"""链接处理测试模块"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, mock_open

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dingtalk_download.link_handler import read_links_file, extract_live_uuid


class TestReadLinksFile:
    """测试read_links_file函数"""
    
    def test_read_csv_with_valid_links(self, tmp_path):
        """测试读取包含有效链接的CSV文件"""
        csv_content = "url\nhttps://n.dingtalk.com/live?liveUuid=test123\nhttps://n.dingtalk.com/live?liveUuid=abc456"
        file_path = tmp_path / "links.csv"
        file_path.write_text(csv_content, encoding='utf-8')
        
        result = read_links_file(str(file_path))
        assert len(result) == 2
        assert any("test123" in url for url in result.values())
        assert any("abc456" in url for url in result.values())
    
    def test_read_csv_with_gbk_encoding(self, tmp_path):
        """测试读取GBK编码的CSV文件"""
        csv_content = "url\nhttps://n.dingtalk.com/live?liveUuid=test123"
        file_path = tmp_path / "links.csv"
        file_path.write_text(csv_content, encoding='gbk')
        
        result = read_links_file(str(file_path))
        assert len(result) == 1
    
    def test_read_excel_file(self, tmp_path):
        """测试读取Excel文件"""
        try:
            import pandas as pd
            from openpyxl import Workbook
            
            wb = Workbook()
            ws = wb.active
            ws['A1'] = 'url'
            ws['A2'] = 'https://n.dingtalk.com/live?liveUuid=test123'
            
            file_path = tmp_path / "links.xlsx"
            wb.save(str(file_path))
            
            result = read_links_file(str(file_path))
            assert len(result) == 1
        except ImportError:
            pytest.skip("openpyxl not installed")
    
    def test_invalid_file_format_raises_systemexit(self, tmp_path):
        """测试不支持的文件格式会调用sys.exit"""
        file_path = tmp_path / "links.txt"
        file_path.write_text("some content")
        
        with pytest.raises(SystemExit) as excinfo:
            read_links_file(str(file_path))
        assert excinfo.value.code == 1
    
    def test_no_valid_links_raises_systemexit(self, tmp_path):
        """测试没有有效链接时调用sys.exit"""
        csv_content = "url\nhttps://example.com/not-dingtalk"
        file_path = tmp_path / "links.csv"
        file_path.write_text(csv_content, encoding='utf-8')
        
        with pytest.raises(SystemExit) as excinfo:
            read_links_file(str(file_path))
        assert excinfo.value.code == 1


class TestExtractLiveUuid:
    """测试extract_live_uuid函数"""
    
    def test_extract_from_valid_url(self):
        """测试从有效URL提取liveUuid"""
        url = "https://n.dingtalk.com/live?liveUuid=abc123-def456"
        result = extract_live_uuid(url)
        assert result == "abc123-def456"
    
    def test_returns_none_for_missing_liveUuid(self):
        """测试没有liveUuid时返回None"""
        url = "https://n.dingtalk.com/live"
        result = extract_live_uuid(url)
        assert result is None
