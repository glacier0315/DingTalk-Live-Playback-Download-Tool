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
import shutil
from unittest.mock import patch, Mock
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.utils.file_reader import FileReader


@pytest.fixture
def test_dir(tmp_path, monkeypatch):
    """创建测试目录,在项目根目录下"""
    test_dir = tmp_path / "test_files"
    test_dir.mkdir()
    monkeypatch.chdir(tmp_path)
    return test_dir


@pytest.fixture
def sample_csv_file(test_dir):
    """创建测试用的 CSV 文件"""
    path = test_dir / "test.csv"
    with open(path, "w", encoding="utf-8") as f:
        f.write("link\n")
        f.write("https://n.dingtalk.com/test1\n")
        f.write("https://n.dingtalk.com/test2\n")
    return str(path)


@pytest.fixture
def sample_excel_file(test_dir):
    """创建测试用的 Excel 文件"""
    import pandas as pd

    path = test_dir / "test.xlsx"
    df = pd.DataFrame({"link": ["https://n.dingtalk.com/test1", "https://n.dingtalk.com/test2"]})
    df.to_excel(path, index=False)
    return str(path)


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


def test_file_reader_csv_with_different_encoding(test_dir):
    """测试读取不同编码的 CSV 文件"""
    path = test_dir / "test_gbk.csv"
    with open(path, "w", encoding="gbk") as f:
        f.write("link\n")
        f.write("https://n.dingtalk.com/test1\n")
        f.write("https://n.dingtalk.com/test2\n")

    reader = FileReader(str(path))
    links = reader.read_links()
    assert len(links) == 2


def test_file_reader_csv_no_links(test_dir):
    """测试读取没有有效链接的 CSV 文件"""
    from dingtalk_downloader.utils.file_reader import FileReaderError

    path = test_dir / "test_no_links.csv"
    with open(path, "w", encoding="utf-8") as f:
        f.write("link\n")
        f.write("https://example.com/test1\n")
        f.write("https://example.com/test2\n")

    reader = FileReader(str(path))

    with pytest.raises(FileReaderError) as exc_info:
        reader.read_links()

    assert "未找到有效的钉钉直播链接" in str(exc_info.value)


def test_file_reader_excel_multiple_sheets(test_dir):
    """测试读取多工作表的 Excel 文件"""
    import pandas as pd

    path = test_dir / "test_multi.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df1 = pd.DataFrame({"link": ["https://n.dingtalk.com/test1"]})
        df2 = pd.DataFrame({"link": ["https://n.dingtalk.com/test2"]})
        df1.to_excel(writer, sheet_name="Sheet1", index=False)
        df2.to_excel(writer, sheet_name="Sheet2", index=False)

    reader = FileReader(str(path))
    links = reader.read_links()
    assert len(links) >= 1
    assert (
        "https://n.dingtalk.com/test1" in links.values()
        or "https://n.dingtalk.com/test2" in links.values()
    )
