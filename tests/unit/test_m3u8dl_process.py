"""Tests for M3u8DLProcess subprocess wrapper."""

import pytest

from dingtalk_downloader.core.exceptions import AuthKeyExpiredError, DownloadFatalError
from dingtalk_downloader.core.m3u8dl_process import (
    DownloadFailureKind,
    M3u8DLProcess,
    RunResult,
)
from tests.fixtures.fake_proc import FakePopen


class _FakeN_m3u8dl_re:
    """Stand-in for NM3u8DLRE — only build_command is used."""

    def build_command(self, m3u8_file, save_name, save_dir, prefix, cookies, headers):
        return [
            "fake-exe",
            m3u8_file,
            "--save-name", save_name,
            "--save-dir", save_dir,
            "--base-url", prefix,
            "--log-file-path", "/tmp/fake.log",
        ]


def _make_process(popen: FakePopen) -> M3u8DLProcess:
    """Construct M3u8DLProcess with a popen_factory that returns the given FakePopen."""
    return M3u8DLProcess(
        n_m3u8dl_re=_FakeN_m3u8dl_re(),  # type: ignore[arg-type]
        log_path="/tmp/fake-{ts}.log",
        popen_factory=lambda *a, **kw: popen,
    )


def test_start_records_command_and_creates_proc():
    popen = FakePopen(returncode=0, stdout="ok", stderr="")
    proc = _make_process(popen)
    proc.start("a.m3u8", "video1", "/save", "https://x/live/", {}, {})

    assert proc.last_command[:1] == ["fake-exe"]
    assert "--save-name" in proc.last_command
    assert proc.is_alive() is True


def test_wait_returns_run_result_with_no_failure_on_clean_exit():
    popen = FakePopen(returncode=0, stdout="downloaded", stderr="")
    proc = _make_process(popen)
    proc.start("a.m3u8", "video1", "/save", "https://x/live/", {}, {})
    result = proc.wait()

    assert isinstance(result, RunResult)
    assert result.returncode == 0
    assert result.failure_kind is None
    assert result.error is None


def test_wait_detects_403_in_stderr():
    popen = FakePopen(returncode=0, stdout="", stderr="HTTP/1.1 403 Forbidden")
    proc = _make_process(popen)
    proc.start("a.m3u8", "v", "/s", "https://x/", {}, {})
    result = proc.wait()

    assert result.failure_kind is DownloadFailureKind.AUTH_KEY_EXPIRED
    assert isinstance(result.error, AuthKeyExpiredError)


def test_wait_detects_disk_full():
    popen = FakePopen(returncode=1, stdout="", stderr="No space left on device")
    proc = _make_process(popen)
    proc.start("a.m3u8", "v", "/s", "https://x/", {}, {})
    result = proc.wait()

    assert result.failure_kind is DownloadFailureKind.DISK_FULL
    assert isinstance(result.error, DownloadFatalError)


def test_wait_classifies_nonzero_with_no_keyword():
    popen = FakePopen(returncode=7, stdout="", stderr="mysterious crash")
    proc = _make_process(popen)
    proc.start("a.m3u8", "v", "/s", "https://x/", {}, {})
    result = proc.wait()

    assert result.failure_kind is DownloadFailureKind.NONZERO_EXIT


def test_terminate_calls_sigterm_then_marks_dead():
    popen = FakePopen(returncode=0, stdout="", stderr="")
    proc = _make_process(popen)
    proc.start("a.m3u8", "v", "/s", "https://x/", {}, {})
    proc.terminate(grace_seconds=0.01)  # short grace for test speed

    assert popen.terminate_calls == 1
    assert popen.kill_calls == 0  # grace elapsed but process is "dead" after terminate
    assert proc.is_alive() is False


def test_is_alive_true_before_wait():
    popen = FakePopen(returncode=0, stdout="", stderr="")
    proc = _make_process(popen)
    proc.start("a.m3u8", "v", "/s", "https://x/", {}, {})
    assert proc.is_alive() is True


def test_is_alive_false_after_wait():
    popen = FakePopen(returncode=0, stdout="", stderr="")
    proc = _make_process(popen)
    proc.start("a.m3u8", "v", "/s", "https://x/", {}, {})
    proc.wait()
    assert proc.is_alive() is False


def test_terminate_before_start_is_safe():
    popen = FakePopen(returncode=0, stdout="", stderr="")
    proc = _make_process(popen)
    proc.terminate(grace_seconds=0.01)  # should not raise
    assert popen.terminate_calls == 0  # nothing to terminate