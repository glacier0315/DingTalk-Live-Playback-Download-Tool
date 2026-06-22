"""Tests for M3u8DLProcess subprocess wrapper."""

import os
import subprocess
import tempfile

import pytest

from dingtalk_downloader.core.exceptions import (
    AuthKeyExpiredError,
    DownloadFatalError,
    RecoverableDownloadError,
)
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


def _make_process(popen: FakePopen, log_path: str = "/tmp/fake-{ts}.log") -> M3u8DLProcess:
    """Construct M3u8DLProcess with a popen_factory that returns the given FakePopen."""
    return M3u8DLProcess(
        n_m3u8dl_re=_FakeN_m3u8dl_re(),  # type: ignore[arg-type]
        log_path=log_path,
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


# ----------------------------------------------------------------------------
# --log-file-path 行为：N_m3u8DL-RE 把 403/分片校验失败等关键诊断写到日志文件，
# stdout/stderr 几乎为空。下面 3 个用例验证 wait() 现在能正确读这个文件。
# ----------------------------------------------------------------------------


def test_wait_detects_403_in_log_file_when_stdout_clean():
    """回归用例：复现 2026-06-20 误判"下载成功"的 bug。

    子进程 stdout/stderr 为空、returncode=0，但 N_m3u8DL-RE 在 log 文件里写了
    大量 403 Forbidden 与"分片数量校验不通过"。修复后应识别为 AUTH_KEY_EXPIRED。
    """
    log_text = (
        "20:03:41.522 INFO : [0x101]: Audio, aac ([15][0][0][0])\n"
        "20:03:41.651 EXTRA: Ah oh!\n"
        "RetryCount => 3\n"
        "Exception  => Response status code does not indicate success: 403 (Forbidden).\n"
        "Url        => https://dtliving-bj-dingpan.dingtalk.com/live/abc/16.ts\n"
        "20:03:41.651 EXTRA: Ah oh!\n"
        "RetryCount => 3\n"
        "Exception  => Response status code does not indicate success: 403 (Forbidden).\n"
        "Url        => https://dtliving-bj-dingpan.dingtalk.com/live/abc/33.ts\n"
        "20:04:01.515 EXTRA: The retry attempts have been exhausted and the download of this segment has failed.\n"
        "20:04:01.644 ERROR: 分片数量校验不通过, 共189个,已下载20.\n"
        "20:04:01.645 ERROR: Failed\n"
    )
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".log", delete=False, encoding="utf-8"
    ) as f:
        f.write(log_text)
        log_path = f.name
    try:
        popen = FakePopen(returncode=0, stdout="", stderr="")
        proc = _make_process(popen, log_path=log_path)
        proc.start("a.m3u8", "v", "/s", "https://x/", {}, {})
        result = proc.wait()

        assert result.returncode == 0
        assert result.log_tail == log_text  # 完整 log 已注入 RunResult
        # 优先命中 AUTH_KEY_EXPIRED（\b403\b 模式先于 SOFT_FAIL 的 \berror\b）
        assert result.failure_kind is DownloadFailureKind.AUTH_KEY_EXPIRED
        assert isinstance(result.error, AuthKeyExpiredError)
    finally:
        os.unlink(log_path)


def test_wait_detects_segment_validation_error_in_log_file():
    """当 log 含 ERROR: Failed 但没有 403 关键字时，应归类 SOFT_FAIL。"""
    log_text = (
        "20:03:41.522 INFO : [0x101]: Audio, aac ([15][0][0][0])\n"
        "20:04:01.644 ERROR: 分片数量校验不通过, 共189个,已下载20.\n"
        "20:04:01.645 ERROR: Failed\n"
    )
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".log", delete=False, encoding="utf-8"
    ) as f:
        f.write(log_text)
        log_path = f.name
    try:
        popen = FakePopen(returncode=0, stdout="", stderr="")
        proc = _make_process(popen, log_path=log_path)
        proc.start("a.m3u8", "v", "/s", "https://x/", {}, {})
        result = proc.wait()

        assert result.failure_kind is DownloadFailureKind.SOFT_FAIL
        assert isinstance(result.error, RecoverableDownloadError)
    finally:
        os.unlink(log_path)


def test_wait_handles_missing_log_file_gracefully():
    """log 文件不存在 → 不崩，且 stdout/stderr 仍能正常判定。

    即使 log_path 指向不存在的路径，wait() 也不应抛异常；clean exit 时仍判 None。
    """
    popen = FakePopen(returncode=0, stdout="downloaded", stderr="")
    proc = _make_process(popen, log_path="/nonexistent/path/to/fake.log")
    proc.start("a.m3u8", "v", "/s", "https://x/", {}, {})
    result = proc.wait()

    assert result.returncode == 0
    assert result.log_tail == ""
    assert result.failure_kind is None
    assert result.error is None


# ----------------------------------------------------------------------------
# 强成功信号：N_m3u8DL-RE 完成合并后打 "INFO : Done"。这之前只有 ffmpeg 的
# Non-monotonous DTS 警告（无害），没有 403/Failed/分片校验不通过。
# classify_failure 之前走 NONZERO_EXIT 兜底 → 触发 retry → refresh m3u8 →
# 已下载分片全部因 auth_key 失效被丢弃 → 视频被重复下载。下面 4 个用例锁定
# "INFO : Done + 无失败关键字 → 成功" 的判定。
# ----------------------------------------------------------------------------


def test_wait_done_signal_marks_success_when_no_failure_keyword():
    """回归：复现 2026-06-20 attempt 10 的日志（INFO : Done + ffmpeg DTS 警告）。

    log 末尾含 INFO : Done 但无 ERROR/Failed/分片校验不通过 → 必须判成功，
    即便 stderr 含 ffmpeg 警告（这些警告无伤大雅）。
    """
    log_text = (
        "20:29:33.611 INFO : [0x100]: Video, h264 ([27][0][0][0]), 1080x1920\n"
        "20:29:33.612 INFO : [0x101]: Audio, aac ([15][0][0][0]), 66 kb/s\n"
        "20:29:34.623 INFO : 调用ffmpeg合并中...\n"
        "20:29:35.840 WARN : [mp4 @ 04096080] Non-monotonous DTS in output stream 0:0\n"
        "20:29:37.025 INFO : Done\n"
    )
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".log", delete=False, encoding="utf-8"
    ) as f:
        f.write(log_text)
        log_path = f.name
    try:
        popen = FakePopen(returncode=0, stdout="", stderr="ffmpeg: DTS warning")
        proc = _make_process(popen, log_path=log_path)
        proc.start("a.m3u8", "video1", "/save", "https://x/", {}, {})
        result = proc.wait()

        # 关键断言：含 INFO : Done + 无失败关键字 → 判成功
        assert result.failure_kind is None
        assert result.error is None
    finally:
        os.unlink(log_path)


def test_wait_done_with_segment_validation_still_fails():
    """log 同时含 Done 与 分片校验不通过 → 仍判失败（Done 不覆盖真实失败）。"""
    log_text = (
        "20:29:35.840 WARN : [mp4 @ 04096080] Non-monotonous DTS\n"
        "20:29:37.025 INFO : Done\n"
        "20:29:37.026 ERROR: 分片数量校验不通过, 共189个,已下载20.\n"
        "20:29:37.027 ERROR: Failed\n"
    )
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".log", delete=False, encoding="utf-8"
    ) as f:
        f.write(log_text)
        log_path = f.name
    try:
        popen = FakePopen(returncode=0, stdout="", stderr="")
        proc = _make_process(popen, log_path=log_path)
        proc.start("a.m3u8", "v", "/s", "https://x/", {}, {})
        result = proc.wait()

        assert result.failure_kind is DownloadFailureKind.SOFT_FAIL
        assert isinstance(result.error, RecoverableDownloadError)
    finally:
        os.unlink(log_path)


def test_wait_done_with_403_still_fails():
    """log 同时含 Done 与 403 → 仍判 AUTH_KEY_EXPIRED。"""
    log_text = (
        "20:29:37.025 INFO : Done\n"
        "20:29:37.026 WARN : Response status code does not indicate success: 403 (Forbidden).\n"
        "20:29:37.027 ERROR: Failed\n"
    )
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".log", delete=False, encoding="utf-8"
    ) as f:
        f.write(log_text)
        log_path = f.name
    try:
        popen = FakePopen(returncode=0, stdout="", stderr="")
        proc = _make_process(popen, log_path=log_path)
        proc.start("a.m3u8", "v", "/s", "https://x/", {}, {})
        result = proc.wait()

        assert result.failure_kind is DownloadFailureKind.AUTH_KEY_EXPIRED
        assert isinstance(result.error, AuthKeyExpiredError)
    finally:
        os.unlink(log_path)


def test_wait_existing_mp4_marks_success_even_without_done_signal():
    """金标准：save_dir 下存在最终 mp4 → 强成功。

    防止 N_m3u8DL-RE 改了日志格式（去掉 INFO : Done）或改名（如 .mkv）后
    又回到误判失败的状况。
    """
    with tempfile.TemporaryDirectory() as save_dir:
        # 模拟 N_m3u8DL-RE 已经合并好的 mp4
        mp4_path = os.path.join(save_dir, "video1.mp4")
        with open(mp4_path, "wb") as f:
            f.write(b"fake mp4 content")

        # log 没有任何成功/失败关键字（理论上不应该发生，但兜底）
        log_text = "20:29:33.611 INFO : [0x100]: Video, h264\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".log", delete=False, encoding="utf-8"
        ) as f:
            f.write(log_text)
            log_path = f.name
        try:
            popen = FakePopen(returncode=0, stdout="", stderr="")
            proc = _make_process(popen, log_path=log_path)
            proc.start("a.m3u8", "video1", save_dir, "https://x/", {}, {})
            result = proc.wait()

            # mp4 存在 → 即使 log 没 Done 也判成功
            assert result.failure_kind is None
            assert result.error is None
        finally:
            os.unlink(log_path)


def test_wait_existing_mp4_inside_save_name_dir_marks_success():
    """N_m3u8DL-RE 也可能输出 <save_dir>/<save_name>/<save_name>.mp4（带子目录）。"""
    with tempfile.TemporaryDirectory() as save_dir:
        nested_dir = os.path.join(save_dir, "video1")
        os.makedirs(nested_dir)
        mp4_path = os.path.join(nested_dir, "video1.mp4")
        with open(mp4_path, "wb") as f:
            f.write(b"fake mp4 content")

        log_text = "20:29:33.611 INFO : [0x100]: Video, h264\n"
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".log", delete=False, encoding="utf-8"
        ) as f:
            f.write(log_text)
            log_path = f.name
        try:
            popen = FakePopen(returncode=0, stdout="", stderr="")
            proc = _make_process(popen, log_path=log_path)
            proc.start("a.m3u8", "video1", save_dir, "https://x/", {}, {})
            result = proc.wait()

            assert result.failure_kind is None
            assert result.error is None
        finally:
            os.unlink(log_path)


# ---------------------------------------------------------------------------
# wait() 超时守护（Phase B）：communicate 抛 TimeoutExpired → 调 terminate →
# 返回 NONZERO_EXIT 的 RunResult（2026-06-20 spec 兜底语义）。
# ---------------------------------------------------------------------------


class _TimeoutPopen:
    """FakePopen 变体：第一次 communicate 抛 TimeoutExpired，第二次返回空。"""

    def __init__(self):
        self.terminate_calls = 0
        self.kill_calls = 0
        self.communicate_calls = 0
        # first_timeout 记录第一次 communicate 的 timeout（被 TimeoutExpired 覆盖之前）
        self.first_timeout = None

    def communicate(self, timeout=None):
        self.communicate_calls += 1
        if self.communicate_calls == 1:
            self.first_timeout = timeout
            raise subprocess.TimeoutExpired(cmd=["fake"], timeout=timeout)
        return ("", "")

    def poll(self):
        return -1

    def terminate(self):
        self.terminate_calls += 1

    def kill(self):
        self.kill_calls += 1


def test_wait_times_out_terminates_and_returns_nonzero():
    """communicate 超时 → 调 terminate(grace) → 返回 NONZERO_EXIT RunResult。"""
    popen = _TimeoutPopen()
    proc = _make_process(popen)
    proc.start("a.m3u8", "video1", "/save", "https://x/", {}, {})
    result = proc.wait(timeout=0.01, on_timeout_grace_seconds=0.01)

    assert popen.terminate_calls == 1
    assert result.failure_kind is DownloadFailureKind.NONZERO_EXIT
    assert isinstance(result.error, RecoverableDownloadError)
    assert "timed out" in str(result.error)
    # 第一次 communicate 收到的 timeout 应等于 effective_timeout
    assert popen.first_timeout == 0.01


def test_wait_default_timeout_uses_run_timeout_seconds():
    """不显式传 timeout 时，effective_timeout 应使用 RUN_TIMEOUT_SECONDS（30 分钟）。"""
    from dingtalk_downloader.config.constants import RUN_TIMEOUT_SECONDS

    popen = _TimeoutPopen()
    proc = _make_process(popen)
    proc.start("a.m3u8", "video1", "/save", "https://x/", {}, {})
    result = proc.wait()  # 不传 timeout

    assert popen.terminate_calls == 1
    assert popen.first_timeout == float(RUN_TIMEOUT_SECONDS)
    assert result.failure_kind is DownloadFailureKind.NONZERO_EXIT
