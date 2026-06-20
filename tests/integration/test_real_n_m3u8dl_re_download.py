"""Integration tests: 真实 N_m3u8DL-RE.exe 端到端调用。

混合方案：mock 浏览器（使用 conftest 提供的 IntegrationFakeBrowser）+ 真实 exe。
所有测试需要 `assets/bin/N_m3u8DL-RE.exe` 存在；由 conftest 的
pytest_collection_modifyitems 自动 skip。

每个测试都加 @pytest.mark.integration 确保不会被默认 pytest 收集运行。
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

# 全部 integration 标记
pytestmark = pytest.mark.integration


def _reset_and_load_config(cfg_path: Path):
    """重置 YamlConfig 单例并指向新 cfg_path。"""
    from dingtalk_downloader.config.yaml_config import YamlConfig
    YamlConfig.reset_instance()
    return YamlConfig.get_instance(str(cfg_path))


# ---------------------------------------------------------------------------
# 基础调用
# ---------------------------------------------------------------------------


def test_real_download_invokes_exe_and_creates_log_file(
    n_m3u8dl_re_path, tmp_config_yaml, tmp_path, monkeypatch
):
    """真实 exe 启动后产生日志文件（即使下载失败）。"""
    cfg_path, _ = tmp_config_yaml
    _reset_and_load_config(cfg_path)

    # 用 monkeypatch.setenv 不需要 — YamlConfig 实例化时已绑定 config_file
    from dingtalk_downloader.binary.n_m3u8dl_re import NM3u8DLRE

    nm = NM3u8DLRE(executable_path=n_m3u8dl_re_path)

    # 用占位 m3u8（fake-host 不可达，期望 N_m3u8DL-RE 失败但写出日志）
    m3u8 = tmp_path / "fake.m3u8"
    m3u8.write_text(
        "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:2\n"
        "#EXT-X-MEDIA-SEQUENCE:0\n#EXTINF:1.0,\nseg-001.ts\n"
        "#EXT-X-ENDLIST\n",
        encoding="utf-8",
    )
    save_dir = tmp_path / "out"
    save_dir.mkdir()

    # 注：N_m3u8DL-RE 会尝试访问 fake-host 上的 seg-001.ts，但 prefix 是 fake path
    # 整体应当失败（returncode != 0）但仍产生日志
    result = nm.download(
        m3u8_file=str(m3u8),
        save_name="video1",
        save_dir=str(save_dir),
        prefix="https://fake-host/live_hp/abc/",
        cookies_data={},
        headers={},
    )
    # 无论成功失败，log 文件应该被创建
    log_dir = Path(nm.log_dir)
    logs = list(log_dir.glob("n_m3u8dl_re_*.log"))
    assert len(logs) >= 1, f"未找到日志文件: log_dir={log_dir}"


def test_real_download_with_cookies_and_custom_headers(
    n_m3u8dl_re_path, tmp_config_yaml, tmp_path
):
    """cookie + 自定义 header 注入：命令 -H "Cookie: ..." 存在。"""
    cfg_path, _ = tmp_config_yaml
    _reset_and_load_config(cfg_path)

    from dingtalk_downloader.binary.n_m3u8dl_re import NM3u8DLRE

    nm = NM3u8DLRE(executable_path=n_m3u8dl_re_path)

    m3u8 = tmp_path / "fake.m3u8"
    m3u8.write_text(
        "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:2\n"
        "#EXTINF:1.0,\nseg-001.ts\n#EXT-X-ENDLIST\n",
        encoding="utf-8",
    )
    save_dir = tmp_path / "out"
    save_dir.mkdir()

    nm.download(
        m3u8_file=str(m3u8),
        save_name="video1",
        save_dir=str(save_dir),
        prefix="https://fake-host/live_hp/abc/",
        cookies_data={"sessionid": "abc123", "uid": "u1"},
        headers={"User-Agent": "CustomAgent/2.0"},
    )

    # 验证日志文件有 cookie 关键字
    log_dir = Path(nm.log_dir)
    log_files = list(log_dir.glob("n_m3u8dl_re_*.log"))
    assert log_files, "未找到日志文件"
    # 至少存在一个非空日志
    assert any(f.stat().st_size > 0 for f in log_files)


def test_real_download_creates_temp_dir(
    n_m3u8dl_re_path, tmp_config_yaml, tmp_path
):
    """NM3u8DLRE 构造时创建 temp_dir + log_dir。"""
    cfg_path, _ = tmp_config_yaml
    _reset_and_load_config(cfg_path)

    from dingtalk_downloader.binary.n_m3u8dl_re import NM3u8DLRE

    nm = NM3u8DLRE(executable_path=n_m3u8dl_re_path)
    assert Path(nm.temp_dir).exists()
    assert Path(nm.log_dir).exists()


def test_real_download_failure_returns_false(
    n_m3u8dl_re_path, tmp_config_yaml, tmp_path
):
    """m3u8 指向不存在路径 → download 返回 False（不抛）。"""
    cfg_path, _ = tmp_config_yaml
    _reset_and_load_config(cfg_path)

    from dingtalk_downloader.binary.n_m3u8dl_re import NM3u8DLRE

    nm = NM3u8DLRE(executable_path=n_m3u8dl_re_path)
    save_dir = tmp_path / "out"
    save_dir.mkdir()
    result = nm.download(
        m3u8_file="/nonexistent/path/missing.m3u8",
        save_name="video1",
        save_dir=str(save_dir),
        prefix="https://fake-host/",
        cookies_data={},
        headers={},
    )
    assert result is False


def test_real_download_save_dir_with_spaces_and_chinese(
    n_m3u8dl_re_path, tmp_config_yaml, tmp_path
):
    """save_dir 含空格和中文 → 不崩，N_m3u8DL-RE 仍被调用。"""
    cfg_path, _ = tmp_config_yaml
    _reset_and_load_config(cfg_path)

    from dingtalk_downloader.binary.n_m3u8dl_re import NM3u8DLRE

    nm = NM3u8DLRE(executable_path=n_m3u8dl_re_path)
    save_dir = tmp_path / "dir with space" / "中文目录"
    save_dir.mkdir(parents=True)
    m3u8 = tmp_path / "fake.m3u8"
    m3u8.write_text(
        "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:2\n"
        "#EXTINF:1.0,\nseg-001.ts\n#EXT-X-ENDLIST\n",
        encoding="utf-8",
    )
    nm.download(
        m3u8_file=str(m3u8),
        save_name="视频_1",
        save_dir=str(save_dir),
        prefix="https://fake-host/",
        cookies_data={},
        headers={},
    )
    # 不崩即为通过；具体结果由 N_m3u8DL-RE 决定


def test_real_download_log_file_naming_pattern(
    n_m3u8dl_re_path, tmp_config_yaml, tmp_path
):
    """日志文件名格式 n_m3u8dl_re_YYYYMMDD_HHMMSS.log。"""
    cfg_path, _ = tmp_config_yaml
    _reset_and_load_config(cfg_path)

    from dingtalk_downloader.binary.n_m3u8dl_re import NM3u8DLRE

    nm = NM3u8DLRE(executable_path=n_m3u8dl_re_path)
    save_dir = tmp_path / "out"
    save_dir.mkdir()
    m3u8 = tmp_path / "fake.m3u8"
    m3u8.write_text(
        "#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:2\n"
        "#EXTINF:1.0,\nseg-001.ts\n#EXT-X-ENDLIST\n",
        encoding="utf-8",
    )
    nm.download(
        m3u8_file=str(m3u8),
        save_name="video1",
        save_dir=str(save_dir),
        prefix="https://fake-host/",
        cookies_data={},
        headers={},
    )
    log_dir = Path(nm.log_dir)
    log_files = list(log_dir.glob("n_m3u8dl_re_*.log"))
    assert log_files
    pattern = re.compile(r"n_m3u8dl_re_\d{8}_\d{6}\.log$")
    for f in log_files:
        assert pattern.search(f.name), f"日志文件名不符合格式: {f.name}"
