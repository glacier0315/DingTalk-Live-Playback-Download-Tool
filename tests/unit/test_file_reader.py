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

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.utils.file_reader import FileReader


@pytest.fixture
def sample_csv_file():
    """创建测试用的 CSV 文件"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8") as f:
        f.write("link\n")
        f.write("https://n.dingtalk.com/test1\n")
        f.write("https://n.dingtalk.com/test2\n")
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def sample_excel_file():
    """创建测试用的 Excel 文件"""
    import pandas as pd

    with tempfile.NamedTemporaryFile(mode="w", suffix=".xlsx", delete=False) as f:
        df = pd.DataFrame(
            {"link": ["https://n.dingtalk.com/test1", "https://n.dingtalk.com/test2"]}
        )
        df.to_excel(f.name, index=False)
        yield f.name
    os.unlink(f.name)


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
