"""
钉钉直播回放下载工具 - path_helper 单元测试

本模块测试路径处理工具函数。

作者：项目团队
依赖：pytest
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.utils.path_helper import clean_file_path, join_paths


def test_clean_file_path_with_quotes():
    """测试清理包含引号的路径"""
    path = '"test/path/file.txt"'
    result = clean_file_path(path)
    assert result == "test/path/file.txt"


def test_clean_file_path_with_single_quotes():
    """测试清理包含单引号的路径"""
    path = "'test/path/file.txt'"
    result = clean_file_path(path)
    assert result == "test/path/file.txt"


def test_clean_file_path_with_spaces():
    """测试清理包含空格的路径"""
    path = "  test/path/file.txt  "
    result = clean_file_path(path)
    assert result == "test/path/file.txt"


def test_clean_file_path_normal():
    """测试清理正常路径"""
    path = "test/path/file.txt"
    result = clean_file_path(path)
    assert result == "test/path/file.txt"


def test_join_paths():
    """测试拼接路径"""
    import os

    result = join_paths("test", "path", "file.txt")
    expected = os.path.join("test", "path", "file.txt")
    assert result == expected


def test_join_paths_single():
    """测试拼接单个路径"""
    result = join_paths("test")
    assert result == "test"
