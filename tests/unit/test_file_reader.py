"""
钉钉直播回放下载工具 - file_reader 单元测试

本模块测试文件读取工具类。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
"""

import sys
import os
import pytest
import tempfile
from unittest.mock import patch, Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.utils.file_reader import FileReader


@pytest.fixture
def sample_csv_file():
    """创建测试用的 CSV 文件"""
    fd, path = tempfile.mkstemp(suffix=".csv")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write("link\n")
            f.write("https://n.dingtalk.com/test1\n")
            f.write("https://n.dingtalk.com/test2\n")
        yield path
    finally:
        if os.path.exists(path):
            os.unlink(path)


@pytest.fixture
def sample_excel_file():
    """创建测试用的 Excel 文件"""
    import pandas as pd
    
    fd, path = tempfile.mkstemp(suffix=".xlsx")
    try:
        df = pd.DataFrame(
            {"link": ["https://n.dingtalk.com/test1", "https://n.dingtalk.com/test2"]}
        )
        df.to_excel(path, index=False)
        yield path
    finally:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except PermissionError:
                pass


def test_file_reader_csv(sample_csv_file):
    """测试读取 CSV 文件"""
    reader = FileReader(sample_csv_file)
    links = reader.read_links()
    assert len(links) == 2
    assert "https://n.dingtalk.com/test1" in links.values()
    assert "https://n.dingtalk.com/test2" in links.values()


def test_file_reader_excel(sample_excel_file):
    """测试读取 Excel 文件"""
    reader = FileReader(sample_excel_file)
    links = reader.read_links()
    assert len(links) == 2
    assert "https://n.dingtalk.com/test1" in links.values()
    assert "https://n.dingtalk.com/test2" in links.values()


def test_file_reader_invalid_format():
    """测试读取不支持的文件格式"""
    with pytest.raises(ValueError):
        FileReader("test.txt")


def test_file_reader_clean_file_path():
    """测试清理文件路径"""
    path = '"test/path/file.txt"'
    result = FileReader.clean_file_path(path)
    assert result == "test/path/file.txt"


def test_file_reader_clean_file_path_with_spaces():
    """测试清理带空格的文件路径"""
    path = '  " test/path/file.txt "  '
    result = FileReader.clean_file_path(path)
    assert result == " test/path/file.txt "


def test_file_reader_csv_with_different_encoding(sample_csv_file):
    """测试读取不同编码的 CSV 文件"""
    with open(sample_csv_file, 'w', encoding='gbk') as f:
        f.write("link\n")
        f.write("https://n.dingtalk.com/test1\n")
        f.write("https://n.dingtalk.com/test2\n")
    
    reader = FileReader(sample_csv_file)
    links = reader.read_links()
    assert len(links) == 2


def test_file_reader_csv_no_links():
    """测试读取没有有效链接的 CSV 文件"""
    from dingtalk_downloader.utils.file_reader import FileReaderError
    
    fd, path = tempfile.mkstemp(suffix=".csv")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write("link\n")
            f.write("https://example.com/test1\n")
            f.write("https://example.com/test2\n")
        
        reader = FileReader(path)
        
        with pytest.raises(FileReaderError) as exc_info:
            reader.read_links()
        
        assert "未找到有效的钉钉直播链接" in str(exc_info.value)
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_file_reader_excel_multiple_sheets():
    """测试读取多工作表的 Excel 文件"""
    import pandas as pd
    
    fd, path = tempfile.mkstemp(suffix=".xlsx")
    try:
        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            df1 = pd.DataFrame({"link": ["https://n.dingtalk.com/test1"]})
            df2 = pd.DataFrame({"link": ["https://n.dingtalk.com/test2"]})
            df1.to_excel(writer, sheet_name='Sheet1', index=False)
            df2.to_excel(writer, sheet_name='Sheet2', index=False)
        
        reader = FileReader(path)
        links = reader.read_links()
        assert len(links) >= 1
        assert "https://n.dingtalk.com/test1" in links.values() or "https://n.dingtalk.com/test2" in links.values()
    finally:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except PermissionError:
                pass
