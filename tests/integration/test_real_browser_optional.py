"""Sanity test: 验证 N_m3u8DL-RE.exe 能正常响应 --help。"""

from __future__ import annotations

import subprocess

import pytest

pytestmark = pytest.mark.integration


def test_nm3u8dl_re_help_flag_works(n_m3u8dl_re_path):
    """`N_m3u8DL-RE.exe --help` 返回 0 且 stdout 含 N_m3u8DL-RE 字样。"""
    result = subprocess.run(
        [n_m3u8dl_re_path, "--help"],
        capture_output=True,
        text=True,
        timeout=10,
        encoding="utf-8",
        errors="replace",
    )
    assert result.returncode == 0, (
        f"非零退出码: rc={result.returncode}, stderr={result.stderr[:200]}"
    )
    out = result.stdout.lower()
    assert "n_m3u8dl-re" in out or "n_m3u8dlcli" in out, (
        f"未识别 N_m3u8DL-RE 输出: {result.stdout[:300]}"
    )
