"""Tests for NM3u8DLRE.build_command + download subprocess behavior."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from dingtalk_downloader.binary.n_m3u8dl_re import NM3u8DLRE
from dingtalk_downloader.config.yaml_config import YamlConfig


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_yaml_singleton():
    YamlConfig.reset_instance()
    yield
    YamlConfig.reset_instance()


def _valid_config(tmp_path: Path) -> dict:
    return {
        "app": {"name": "x", "version": "1.0", "build_date": "2026-01-01"},
        "download": {
            "default_dir": str(tmp_path / "Downloads"),
            "temp_dir": str(tmp_path / "temp"),
            "max_retry_count": 5,
        },
        "browser": {
            "default_type": "edge",
            "headless": False,
            "timeout": 30,
        },
        "logging": {
            "level": "INFO",
            "dir": str(tmp_path / "logs"),
            "max_bytes": 10485760,
            "backup_count": 5,
            "retention_days": 30,
        },
        "headers": {
            "user_agent": "Test/1.0",
            "referer": "https://n.dingtalk.com/",
            "accept": "*/*",
            "accept_language": "zh-CN",
            "accept_encoding": "identity",
            "connection": "keep-alive",
            "sec_fetch_dest": "video",
            "sec_fetch_mode": "cors",
            "sec_fetch_site": "same-origin",
            "sec_fetch_user": "?1",
            "upgrade_insecure_requests": "1",
        },
        "n_m3u8dl_re": {
            "executable_path": "fake-exe",
            "ui_language": "zh-CN",
            "temp_dir": str(tmp_path / "nm_temp"),
            "log_dir": str(tmp_path / "nm_logs"),
        },
        "ffmpeg": {"executable_path": "fake-ffmpeg"},
    }


@pytest.fixture
def nm(tmp_path):
    """构造一个 YamlConfig + NM3u8DLRE 实例（fake-exe）。"""
    cfg_path = tmp_path / "app.yaml"
    cfg_path.write_text(
        yaml.safe_dump(_valid_config(tmp_path), allow_unicode=True),
        encoding="utf-8",
    )
    YamlConfig.reset_instance()
    return NM3u8DLRE(executable_path="fake-exe")


# ---------------------------------------------------------------------------
# build_command
# ---------------------------------------------------------------------------


class TestBuildCommand:
    def test_basic_position_and_flags(self, nm):
        cmd = nm.build_command(
            m3u8_file="/tmp/a.m3u8",
            save_name="video1",
            save_dir="/save",
            prefix="https://x/live_hp/abc/",
            cookies_data=None,
            headers=None,
        )
        # 前 9 项是固定 flag 结构
        expected_head = [
            "fake-exe",
            "/tmp/a.m3u8",
            "--ui-language", "zh-CN",
            "--save-name", "video1",
            "--save-dir", "/save",
            "--base-url", "https://x/live_hp/abc/",
            "--tmp-dir", nm.temp_dir,
        ]
        assert cmd[: len(expected_head)] == expected_head
        # log-file-path 是第 9/10 项
        assert cmd[len(expected_head)] == "--log-file-path"
        # log 路径以 nm.log_dir + n_m3u8dl_re_<ts>.log 形式
        log_path = cmd[len(expected_head) + 1]
        assert log_path.startswith(nm.log_dir)
        assert re.search(r"n_m3u8dl_re_\d{8}_\d{6}\.log$", log_path)

    def test_command_is_list_of_strings(self, nm):
        cmd = nm.build_command("/a.m3u8", "v", "/s", "p", None, None)
        assert all(isinstance(x, str) for x in cmd)

    def test_cookies_merged_into_single_cookie_header(self, nm):
        cmd = nm.build_command(
            "/a.m3u8", "v", "/s", "p",
            cookies_data={"a": "1", "b": "2"},
            headers=None,
        )
        # 找 -H "Cookie: ..." 子串
        cookie_flags = [
            cmd[i + 1] for i, x in enumerate(cmd) if x == "-H" and cmd[i + 1].startswith("Cookie: ")
        ]
        assert len(cookie_flags) == 1
        cookie_str = cookie_flags[0]
        assert "a=1" in cookie_str
        assert "b=2" in cookie_str
        assert cookie_str.startswith("Cookie: ")

    def test_no_cookie_header_when_cookies_empty(self, nm):
        for cookies in (None, {}):
            cmd = nm.build_command("/a.m3u8", "v", "/s", "p", cookies, None)
            assert not any(
                x.startswith("Cookie: ") for x in cmd if x.startswith("Cookie")
            )
            # 强断言：不存在 Cookie: 子串
            assert not any("Cookie:" in c for c in cmd)

    def test_extra_headers_override_defaults(self, nm, monkeypatch):
        """传入 headers 时覆盖 header_manager.get_headers 中的同名 key。"""
        # 让 default headers 包含一个我们能识别的占位 User-Agent
        monkeypatch.setattr(
            nm.header_manager, "get_headers",
            lambda include_overrides=True: {"User-Agent": "DEFAULT", "Referer": "DEFAULT-REF"}
        )
        cmd = nm.build_command(
            "/a.m3u8", "v", "/s", "p", None,
            headers={"User-Agent": "OVERRIDE"},
        )
        # 找所有 -H User-Agent 子串，应该只有 1 个，且为 OVERRIDE
        ua_values = [
            cmd[i + 1].split(": ", 1)[1]
            for i, x in enumerate(cmd)
            if x == "-H" and cmd[i + 1].startswith("User-Agent: ")
        ]
        assert ua_values == ["OVERRIDE"]
        # Referer 不被覆盖，仍保留
        ref_values = [
            cmd[i + 1].split(": ", 1)[1]
            for i, x in enumerate(cmd)
            if x == "-H" and cmd[i + 1].startswith("Referer: ")
        ]
        assert ref_values == ["DEFAULT-REF"]

    def test_default_headers_appended_when_no_override(self, nm):
        cmd = nm.build_command("/a.m3u8", "v", "/s", "p", None, None)
        # 11 个 header manager 默认项会展开为 11 个 -H key: value
        header_keys = [
            cmd[i + 1].split(": ", 1)[0]
            for i, x in enumerate(cmd)
            if x == "-H"
        ]
        # 应至少包含 User-Agent / Referer / Accept 等
        for expected in ("User-Agent", "Referer", "Accept", "Accept-Language"):
            assert expected in header_keys, f"missing header {expected}"

    def test_base_url_and_save_paths_passed_through(self, nm):
        prefix = "https://x.example.com/live_hp/abc-123-uuid/"
        save_dir = "/save/dir with space/"
        save_name = "video_名_1"
        cmd = nm.build_command("/a.m3u8", save_name, save_dir, prefix, None, None)
        assert prefix in cmd
        assert save_dir in cmd
        assert save_name in cmd

    def test_log_file_path_under_log_dir(self, nm):
        cmd = nm.build_command("/a.m3u8", "v", "/s", "p", None, None)
        log_path = cmd[cmd.index("--log-file-path") + 1]
        assert log_path.startswith(nm.log_dir)
        assert re.match(r".*n_m3u8dl_re_\d{8}_\d{6}\.log$", log_path)

    def test_log_file_path_timestamp_changes_between_calls(self, nm):
        """两次调用产生不同 log 文件（基于 datetime.now 时间戳）。"""
        import time as _time
        # 强制两次调用间隔 > 1s，确保时间戳字符串不同
        cmd1 = nm.build_command("/a.m3u8", "v", "/s", "p", None, None)
        _time.sleep(1.1)
        cmd2 = nm.build_command("/a.m3u8", "v", "/s", "p", None, None)
        log1 = cmd1[cmd1.index("--log-file-path") + 1]
        log2 = cmd2[cmd2.index("--log-file-path") + 1]
        assert log1 != log2


# ---------------------------------------------------------------------------
# download (subprocess mock)
# ---------------------------------------------------------------------------


class TestDownload:
    def _fake_completed(self, returncode=0, stdout="ok", stderr=""):
        return subprocess.CompletedProcess(
            args=[], returncode=returncode, stdout=stdout, stderr=stderr
        )

    def test_download_returns_true_on_clean_exit(self, nm, monkeypatch):
        monkeypatch.setattr(
            "dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run",
            lambda *a, **kw: self._fake_completed(0, "downloaded", ""),
        )
        assert nm.download("/a.m3u8", "v", "/s", "p", {}, {}) is True

    def test_download_returns_false_on_nonzero_returncode(self, nm, monkeypatch):
        monkeypatch.setattr(
            "dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run",
            lambda *a, **kw: self._fake_completed(1, "", ""),
        )
        assert nm.download("/a.m3u8", "v", "/s", "p", {}, {}) is False

    def test_download_returns_false_when_stdout_contains_error_marker(
        self, nm, monkeypatch
    ):
        monkeypatch.setattr(
            "dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run",
            lambda *a, **kw: self._fake_completed(0, "ERROR: something", ""),
        )
        assert nm.download("/a.m3u8", "v", "/s", "p", {}, {}) is False

    def test_download_returns_false_when_stderr_contains_failed(
        self, nm, monkeypatch
    ):
        monkeypatch.setattr(
            "dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run",
            lambda *a, **kw: self._fake_completed(0, "", "Download Failed"),
        )
        assert nm.download("/a.m3u8", "v", "/s", "p", {}, {}) is False

    def test_download_returns_false_on_subprocess_exception(self, nm, monkeypatch):
        def _raise(*a, **kw):
            raise OSError("binary missing")

        monkeypatch.setattr(
            "dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run", _raise
        )
        assert nm.download("/a.m3u8", "v", "/s", "p", {}, {}) is False

    def test_download_invokes_subprocess_with_build_command(self, nm, monkeypatch):
        captured = {}

        def _capture(*a, **kw):
            captured["args"] = a
            captured["kwargs"] = kw
            return self._fake_completed(0, "ok", "")

        monkeypatch.setattr(
            "dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run", _capture
        )
        nm.download("/a.m3u8", "video1", "/save", "p", {}, {})
        expected_cmd = nm.build_command("/a.m3u8", "video1", "/save", "p", {}, {})
        # 第一个位置参数应当是命令列表
        assert list(captured["args"][0]) == expected_cmd

    def test_download_uses_text_capture(self, nm, monkeypatch):
        captured = {}

        def _capture(*a, **kw):
            captured.update(kw)
            return self._fake_completed(0, "ok", "")

        monkeypatch.setattr(
            "dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run", _capture
        )
        nm.download("/a.m3u8", "v", "/s", "p", {}, {})
        assert captured.get("capture_output") is True
        assert captured.get("text") is True


# ---------------------------------------------------------------------------
# __init__ / 目录创建
# ---------------------------------------------------------------------------


class TestInit:
    def test_init_creates_temp_and_log_dirs(self, tmp_path):
        cfg_path = tmp_path / "app.yaml"
        cfg_path.write_text(
            yaml.safe_dump(_valid_config(tmp_path), allow_unicode=True),
            encoding="utf-8",
        )
        YamlConfig.reset_instance()
        nm = NM3u8DLRE(executable_path="fake-exe")
        assert Path(nm.temp_dir).exists()
        assert Path(nm.log_dir).exists()

    def test_init_falls_back_to_defaults_when_config_missing(self, tmp_path, monkeypatch):
        """yaml 里缺 temp_dir / log_dir → 用 'temp' / 'logs' 默认值。"""
        cfg = _valid_config(tmp_path)
        cfg["n_m3u8dl_re"].pop("temp_dir")
        cfg["n_m3u8dl_re"].pop("log_dir")
        cfg_path = tmp_path / "app.yaml"
        cfg_path.write_text(
            yaml.safe_dump(cfg, allow_unicode=True), encoding="utf-8"
        )
        YamlConfig.reset_instance()
        # 拦截 ensure_dir_exists 避免在 cwd 创建真实目录
        monkeypatch.setattr(
            "dingtalk_downloader.utils.path_helper.ensure_dir_exists",
            lambda _p: None,
        )
        nm = NM3u8DLRE(executable_path="fake-exe")
        assert nm.temp_dir == "temp"
        assert nm.log_dir == "logs"

    def test_init_propagates_dir_creation_error(self, tmp_path, monkeypatch):
        cfg_path = tmp_path / "app.yaml"
        cfg_path.write_text(
            yaml.safe_dump(_valid_config(tmp_path), allow_unicode=True),
            encoding="utf-8",
        )
        YamlConfig.reset_instance()
        monkeypatch.setattr(
            "dingtalk_downloader.utils.path_helper.ensure_dir_exists",
            lambda _p: (_ for _ in ()).throw(OSError("permission denied")),
        )
        with pytest.raises(OSError, match="permission denied"):
            NM3u8DLRE(executable_path="fake-exe")
