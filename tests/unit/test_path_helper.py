"""
钉钉直播回放下载工具 - path_helper 单元测试

本模块测试路径处理工具函数。

作者：项目团队
依赖：pytest
创建日期：2026-01-29
修改历史：
    - 2026-01-29: 初始版本
"""

import sys
import os
import pytest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.utils.path_helper import clean_file_path, join_paths, ensure_dir_exists


def test_clean_file_path_normal():
    """测试清理正常文件路径"""
    path = "test/path/file.txt"
    result = clean_file_path(path)
    assert result == "test/path/file.txt"


def test_clean_file_path_with_quotes():
    """测试清理带引号的文件路径"""
    path = '"test/path/file.txt"'
    result = clean_file_path(path)
    assert result == "test/path/file.txt"


def test_clean_file_path_with_single_quotes():
    """测试清理带单引号的文件路径"""
    path = "'test/path/file.txt'"
    result = clean_file_path(path)
    assert result == "test/path/file.txt"


def test_clean_file_path_with_spaces():
    """测试清理带空格的文件路径"""
    path = "  test/path/file.txt  "
    result = clean_file_path(path)
    assert result == "test/path/file.txt"


def test_clean_file_path_with_quotes_and_spaces():
    """测试清理带引号和空格的文件路径"""
    path = '  " test/path/file.txt "  '
    result = clean_file_path(path)
    assert result == " test/path/file.txt "


def test_clean_file_path_empty():
    """测试清理空路径"""
    path = ""
    result = clean_file_path(path)
    assert result == ""


def test_join_paths_two():
    """测试拼接两个路径"""
    result = join_paths("dir1", "dir2")
    assert result == os.path.join("dir1", "dir2")


def test_join_paths_three():
    """测试拼接三个路径"""
    result = join_paths("dir1", "dir2", "dir3")
    assert result == os.path.join("dir1", "dir2", "dir3")


def test_join_paths_multiple():
    """测试拼接多个路径"""
    result = join_paths("dir1", "dir2", "dir3", "dir4")
    assert result == os.path.join("dir1", "dir2", "dir3", "dir4")


def test_join_paths_empty():
    """测试拼接空路径"""
    result = join_paths("")
    assert result == ""


def test_ensure_dir_exists_new_dir(tmp_path):
    """测试确保目录存在（新建目录）"""
    new_dir = tmp_path / "new_directory"
    assert not new_dir.exists()
    
    ensure_dir_exists(str(new_dir))
    
    assert new_dir.exists()


def test_ensure_dir_exists_existing_dir(tmp_path):
    """测试确保目录存在（已存在目录）"""
    existing_dir = tmp_path / "existing_directory"
    existing_dir.mkdir()
    assert existing_dir.exists()
    
    ensure_dir_exists(str(existing_dir))
    
    assert existing_dir.exists()


def test_ensure_dir_exists_nested(tmp_path):
    """测试确保目录存在（嵌套目录）"""
    nested_dir = tmp_path / "level1" / "level2" / "level3"
    assert not nested_dir.exists()
    
    ensure_dir_exists(str(nested_dir))
    
    assert nested_dir.exists()


def test_ensure_dir_exists_with_spaces(tmp_path):
    """测试确保目录存在（带空格的目录名）"""
    dir_with_spaces = tmp_path / "directory with spaces"
    assert not dir_with_spaces.exists()
    
    ensure_dir_exists(str(dir_with_spaces))
    
    assert dir_with_spaces.exists()
