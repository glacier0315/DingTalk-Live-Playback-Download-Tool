"""Tests for FileValidator: 7 _check_* helpers 覆盖全部失败/成功路径。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from dingtalk_downloader.utils import file_validator
from dingtalk_downloader.utils.file_validator import FileValidator


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def in_cwd(tmp_path, monkeypatch):
    """把 CWD 切到 tmp_path，测试结束后自动恢复。"""
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def make_csv(in_cwd):
    """在 cwd 内创建一个 CSV 文件，可指定大小。"""

    def _make(name="data.csv", size_bytes=10, content=None):
        if content is None:
            content = b"a,b\n1,2\n"
        p = in_cwd / name
        # 写入指定大小（必要时填充）
        if size_bytes <= len(content):
            data = content[:size_bytes]
        else:
            data = content + b"\x00" * (size_bytes - len(content))
        p.write_bytes(data)
        return p

    return _make


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


class TestHappyPath:
    def test_validate_csv_passes(self, make_csv):
        path = str(make_csv("data.csv", size_bytes=10))
        assert FileValidator.validate_file_path(path) == path

    def test_validate_xlsx_passes(self, in_cwd):
        # 不必是真实 xlsx；扩展名通过即放行
        p = in_cwd / "data.xlsx"
        p.write_bytes(b"PK\x03\x04" + b"\x00" * 100)
        result = FileValidator.validate_file_path(str(p))
        assert result == str(p)

    def test_validate_xls_passes(self, in_cwd):
        p = in_cwd / "data.xls"
        p.write_bytes(b"\xd0\xcf\x11\xe0" + b"\x00" * 100)
        result = FileValidator.validate_file_path(str(p))
        assert result == str(p)

    def test_validate_returns_stripped_path(self, make_csv):
        path = f"  {make_csv('data.csv')}  "
        result = FileValidator.validate_file_path(path)
        assert result == str(make_csv("data.csv"))


# ---------------------------------------------------------------------------
# 路径遍历
# ---------------------------------------------------------------------------


class TestPathTraversal:
    def test_rejects_absolute_path_outside_cwd(self, in_cwd):
        # Windows: C:\Windows\System32\notepad.exe （绝对且不在 cwd）
        # Linux: /etc/passwd
        if sys.platform == "win32":
            outside = "C:\\Windows\\System32\\drivers\\etc\\hosts"
        else:
            outside = "/etc/passwd"
        with pytest.raises(ValueError, match="路径遍历"):
            FileValidator.validate_file_path(outside)

    def test_rejects_parent_dir_reference_via_relative_to(self, in_cwd, tmp_path):
        # 创建 cwd 之外的子目录
        outside_dir = tmp_path.parent / "outside"
        outside_dir.mkdir(exist_ok=True)
        outside_file = outside_dir / "data.csv"
        outside_file.write_bytes(b"a,b\n1,2\n")
        # 用绝对路径但尝试相对 cwd 解析（会落在 cwd 之外）
        with pytest.raises(ValueError, match="路径遍历"):
            FileValidator.validate_file_path(str(outside_file))

    def test_rejects_double_dot_in_path(self, in_cwd):
        # 路径里含 ".." 字面量 → 会被 relative_to 检查
        # 注意 absolute() 后再 relative_to(cwd) 仍可能含 ..
        with pytest.raises(ValueError, match="父目录引用|路径遍历"):
            FileValidator.validate_file_path(str(in_cwd / ".." / "data.csv"))

    def test_accepts_relative_path_inside_cwd(self, in_cwd):
        p = in_cwd / "data.csv"
        p.write_bytes(b"a,b\n")
        # 相对路径也可通过
        result = FileValidator.validate_file_path("data.csv")
        assert result == "data.csv"

    @pytest.mark.skipif(
        sys.platform == "win32", reason="Windows symlink 需要管理员权限"
    )
    def test_rejects_symlink_pointing_outside_cwd(self, in_cwd, tmp_path):
        """符号链接指向 cwd 之外 → 仍会被 absolute() 边界检查拒绝。"""
        # 在 cwd 内放一个符号链接，指向 cwd 之外
        outside_dir = tmp_path.parent / "outside_for_symlink"
        outside_dir.mkdir(exist_ok=True)
        outside_file = outside_dir / "data.csv"
        outside_file.write_bytes(b"a,b\n")
        link = in_cwd / "link.csv"
        link.symlink_to(outside_file)
        with pytest.raises(ValueError, match="路径遍历"):
            FileValidator.validate_file_path(str(link))


# ---------------------------------------------------------------------------
# 扩展名
# ---------------------------------------------------------------------------


class TestExtension:
    def test_rejects_unsupported_extension(self, in_cwd):
        p = in_cwd / "data.txt"
        p.write_bytes(b"hello")
        with pytest.raises(ValueError, match="文件格式不支持"):
            FileValidator.validate_file_path(str(p))

    def test_rejects_no_extension(self, in_cwd):
        p = in_cwd / "data"
        p.write_bytes(b"hello")
        with pytest.raises(ValueError, match="文件格式不支持"):
            FileValidator.validate_file_path(str(p))

    def test_accepts_uppercase_extension(self, in_cwd):
        p = in_cwd / "DATA.CSV"
        p.write_bytes(b"a,b\n")
        result = FileValidator.validate_file_path(str(p))
        assert result == str(p)

    def test_accepts_xlsx_uppercase(self, in_cwd):
        p = in_cwd / "DATA.XLSX"
        p.write_bytes(b"x" * 50)
        result = FileValidator.validate_file_path(str(p))
        assert result == str(p)


# ---------------------------------------------------------------------------
# 存在性 / 类型
# ---------------------------------------------------------------------------


class TestExistenceAndType:
    def test_rejects_nonexistent_file(self, in_cwd):
        p = in_cwd / "missing.csv"
        with pytest.raises(FileNotFoundError, match="文件不存在"):
            FileValidator.validate_file_path(str(p))

    def test_rejects_directory(self, in_cwd):
        # 目录加 .csv 后缀以便通过 _check_file_extension
        d = in_cwd / "subdir.csv"
        d.mkdir()
        with pytest.raises(ValueError, match="路径不是文件"):
            FileValidator.validate_file_path(str(d))


# ---------------------------------------------------------------------------
# 大小
# ---------------------------------------------------------------------------


class TestSize:
    def test_rejects_empty_file(self, in_cwd):
        p = in_cwd / "empty.csv"
        p.write_bytes(b"")
        with pytest.raises(ValueError, match="文件为空"):
            FileValidator.validate_file_path(str(p))

    def test_rejects_oversize_file(self, in_cwd, monkeypatch):
        # 临时把 MAX_FILE_SIZE 调小到 100 字节
        monkeypatch.setattr(file_validator, "MAX_FILE_SIZE", 100)
        p = in_cwd / "big.csv"
        p.write_bytes(b"a" * 101)
        with pytest.raises(ValueError, match="文件过大"):
            FileValidator.validate_file_path(str(p))

    def test_accepts_size_at_limit(self, in_cwd, monkeypatch):
        monkeypatch.setattr(file_validator, "MAX_FILE_SIZE", 100)
        p = in_cwd / "ok.csv"
        p.write_bytes(b"a" * 100)
        result = FileValidator.validate_file_path(str(p))
        assert result == str(p)


# ---------------------------------------------------------------------------
# 可读性
# ---------------------------------------------------------------------------


class TestReadability:
    def test_rejects_unreadable_file(self, in_cwd, monkeypatch):
        p = in_cwd / "locked.csv"
        p.write_bytes(b"a,b\n")

        # 拦截 os.access：返回 False 表示不可读
        def _no_access(*args, **kwargs):
            return False

        monkeypatch.setattr(os, "access", _no_access)
        with pytest.raises(PermissionError, match="文件不可读"):
            FileValidator.validate_file_path(str(p))


# ---------------------------------------------------------------------------
# 空输入
# ---------------------------------------------------------------------------


class TestEmptyInput:
    def test_rejects_empty_string(self):
        with pytest.raises(ValueError, match="文件路径不能为空"):
            FileValidator.validate_file_path("")

    def test_rejects_whitespace_only(self):
        # validate_file_path 内部先 strip → 空 → _check_path_not_empty 抛错
        with pytest.raises(ValueError, match="文件路径不能为空"):
            FileValidator.validate_file_path("   ")


# ---------------------------------------------------------------------------
# 私有 helper 单测（白盒）
# ---------------------------------------------------------------------------


class TestPrivateHelpers:
    def test_check_path_not_empty(self):
        with pytest.raises(ValueError, match="文件路径不能为空"):
            FileValidator._check_path_not_empty("")

    def test_check_file_extension_lowercase(self):
        # _check_file_extension 不查文件存在
        FileValidator._check_file_extension("foo.csv")  # 不抛

    def test_check_file_extension_unsupported(self):
        with pytest.raises(ValueError, match="文件格式不支持"):
            FileValidator._check_file_extension("foo.pdf")

    def test_check_file_exists_missing(self, in_cwd):
        with pytest.raises(FileNotFoundError):
            FileValidator._check_file_exists(str(in_cwd / "nope.csv"))

    def test_check_is_file_with_directory(self, in_cwd):
        d = in_cwd / "subdir"
        d.mkdir()
        with pytest.raises(ValueError, match="路径不是文件"):
            FileValidator._check_is_file(str(d))

    def test_check_file_size_zero(self, in_cwd):
        p = in_cwd / "zero.csv"
        p.write_bytes(b"")
        with pytest.raises(ValueError, match="文件为空"):
            FileValidator._check_file_size(str(p))

    def test_check_file_size_too_big(self, in_cwd, monkeypatch):
        monkeypatch.setattr(file_validator, "MAX_FILE_SIZE", 10)
        p = in_cwd / "toobig.csv"
        p.write_bytes(b"a" * 11)
        with pytest.raises(ValueError, match="文件过大"):
            FileValidator._check_file_size(str(p))
