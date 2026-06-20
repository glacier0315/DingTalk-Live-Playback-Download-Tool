"""Integration smoke tests: 真实 N_m3u8DL-RE.exe 端到端调用。

混合方案：mock 浏览器 + 真实 exe。
目的：覆盖从 fake m3u8 → NM3u8DLRE.build_command → 子进程启动 → 日志写入
的完整链路。

注：完整 orchestrator (DownloadSession + DownloadOrchestrator) 测试涉及的
跨模块 mock 太多（cookie_handler.browser / live_name_resolver 等），且 1s
占位 m3u8 不可被 N_m3u8DL-RE 真实解码，所以本套件聚焦在"子进程被真实启动 +
日志文件正确生成"的最小端到端验证。
"""

from __future__ import annotations

import re
import time
from pathlib import Path

import pytest

# 全部 integration 标记
pytestmark = pytest.mark.integration


def _reset_and_load_config(cfg_path: Path):
    from dingtalk_downloader.config.yaml_config import YamlConfig
    YamlConfig.reset_instance()
    return YamlConfig.get_instance(str(cfg_path))


# ---------------------------------------------------------------------------
# 端到端 smoke
# ---------------------------------------------------------------------------


def test_nm3u8dl_re_subprocess_integration(
    n_m3u8dl_re_path, tmp_config_yaml, tmp_path
):
    """NM3u8DLRE 调用真实 exe + 传 cookie + 传 custom header + log 文件命名。"""
    cfg_path, _ = tmp_config_yaml
    _reset_and_load_config(cfg_path)

    from dingtalk_downloader.binary.n_m3u8dl_re import NM3u8DLRE

    nm = NM3u8DLRE(executable_path=n_m3u8dl_re_path)

    # 写一个最小 m3u8：引用 fake-host 上的 .ts（不可达 → 真实 exe 会失败）
    m3u8 = tmp_path / "video.m3u8"
    m3u8.write_text(
        "#EXTM3U\n"
        "#EXT-X-VERSION:3\n"
        "#EXT-X-TARGETDURATION:2\n"
        "#EXT-X-MEDIA-SEQUENCE:0\n"
        "#EXTINF:1.0,\nseg-001.ts\n"
        "#EXT-X-ENDLIST\n",
        encoding="utf-8",
    )
    save_dir = tmp_path / "output"
    save_dir.mkdir()

    # 真实调用（必然失败，但日志会被写入）
    result = nm.download(
        m3u8_file=str(m3u8),
        save_name="integration_test",
        save_dir=str(save_dir),
        prefix="https://fake-host/live_hp/abcdef01-2345-6789-abcd-ef0123456789/",
        cookies_data={"sessionid": "itest123", "uid": "u-itest"},
        headers={"X-Custom-Header": "IntegrationTest"},
    )

    # 1. 不抛异常（即使失败）
    assert result is False or result is True  # 任意布尔值即可

    # 2. 日志文件存在且符合命名规则
    log_dir = Path(nm.log_dir)
    assert log_dir.exists()
    log_files = list(log_dir.glob("n_m3u8dl_re_*.log"))
    assert log_files, f"未找到日志文件: {log_dir}"
    pattern = re.compile(r"n_m3u8dl_re_\d{8}_\d{6}\.log$")
    for f in log_files:
        assert pattern.search(f.name), f"日志文件名不符合格式: {f.name}"

    # 3. 日志非空（N_m3u8DL-RE 至少写出 banner）
    assert any(f.stat().st_size > 0 for f in log_files)


def test_nm3u8dl_re_handles_invalid_executable_gracefully(
    tmp_config_yaml, tmp_path
):
    """executable_path 指向不存在路径 → download 返回 False 而非崩溃。"""
    cfg_path, _ = tmp_config_yaml
    _reset_and_load_config(cfg_path)

    from dingtalk_downloader.binary.n_m3u8dl_re import NM3u8DLRE

    nm = NM3u8DLRE(executable_path="C:/nonexistent/fake-exe.exe")
    save_dir = tmp_path / "out"
    save_dir.mkdir()
    result = nm.download(
        m3u8_file=str(tmp_path / "x.m3u8"),
        save_name="v",
        save_dir=str(save_dir),
        prefix="p",
        cookies_data={},
        headers={},
    )
    assert result is False


def test_build_command_with_real_exe_includes_expected_flags(
    n_m3u8dl_re_path, tmp_config_yaml, tmp_path
):
    """build_command 产物能匹配 N_m3u8DL-RE.exe 真实命令行格式。"""
    cfg_path, _ = tmp_config_yaml
    _reset_and_load_config(cfg_path)

    from dingtalk_downloader.binary.n_m3u8dl_re import NM3u8DLRE

    nm = NM3u8DLRE(executable_path=n_m3u8dl_re_path)
    cmd = nm.build_command(
        m3u8_file="/tmp/a.m3u8",
        save_name="video1",
        save_dir=str(tmp_path / "save"),
        prefix="https://fake-host/live_hp/abc/",
        cookies_data={"sid": "x"},
        headers={"X-Test": "1"},
    )
    # 1. exe 路径是真实路径
    assert cmd[0] == n_m3u8dl_re_path
    # 2. ui-language / save-name / save-dir / base-url / tmp-dir / log-file-path 齐
    for flag in ("--ui-language", "--save-name", "--save-dir", "--base-url",
                 "--tmp-dir", "--log-file-path"):
        assert flag in cmd, f"missing flag {flag}"
    # 3. -H "Cookie: sid=x"
    cookie_idx = cmd.index("-H")
    assert cmd[cookie_idx + 1].startswith("Cookie: ")
    assert "sid=x" in cmd[cookie_idx + 1]
    # 4. -H "X-Test: 1" 存在
    x_test_idx = None
    for i, c in enumerate(cmd):
        if c == "-H" and cmd[i + 1].startswith("X-Test: "):
            x_test_idx = i
            break
    assert x_test_idx is not None, "X-Test header not in command"
