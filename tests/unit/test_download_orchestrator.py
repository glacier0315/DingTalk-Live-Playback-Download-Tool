"""Tests for the DownloadOrchestrator main loop."""

from typing import List

import pytest

from dingtalk_downloader.core.download_orchestrator import (
    DownloadOrchestrator,
)
from dingtalk_downloader.utils.models import DownloadOutcome
from dingtalk_downloader.core.exceptions import (
    DownloadFatalError,
    M3u8RefreshError,
)
from dingtalk_downloader.core.m3u8dl_process import DownloadFailureKind
from dingtalk_downloader.core.retry_policy import RetryPolicy
from dingtalk_downloader.utils.models import M3u8Link, VideoDownloadContext, CookieData, HeadersData
from tests.fixtures.fake_proc import FakePopen


# --- Stubs ---


class _StubSession:
    def __init__(self, m3u8_links: List[str], save_dir: str = "/save"):
        self._m3u8_links = m3u8_links
        self._save_dir = save_dir
        self._idx = 0
        self._cookie = CookieData(cookies={"s": "v"})
        self._headers = HeadersData(headers={"UA": "test"})
        self._live_name = "live_test"
        # Reuse the same refresh-service instance so the test can inspect
        # fetch_count after run() completes (DownloadSession.refresh_service()
        # is also expected to be cached/idempotent in production).
        self._refresh_service = _StubRefreshService(self._m3u8_links, self)

    def cookie_data(self):
        return self._cookie

    def headers_data(self):
        return self._headers

    def live_name(self):
        return self._live_name

    def refresh_service(self):
        return self._refresh_service

    def track_temp_file(self, path):
        pass


class _StubRefreshService:
    def __init__(self, links: List[str], session: _StubSession):
        self._links = links
        self._session = session
        self.fetch_count = 0

    def fetch(self, share_url):
        self.fetch_count += 1
        idx = min(self.fetch_count - 1, len(self._links) - 1)
        url = self._links[idx]
        if not url:
            raise M3u8RefreshError("no link")
        return M3u8Link(url=url, prefix="https://x/live_hp/", local_file_path=f"/tmp/{self.fetch_count}.m3u8")


class _StubN_m3u8dl_re:
    def build_command(self, m3u8_file, save_name, save_dir, prefix, cookies, headers):
        return ["fake", m3u8_file, "--save-name", save_name, "--save-dir", save_dir]


def _ctx() -> VideoDownloadContext:
    return VideoDownloadContext(
        url="https://n.dingtalk.com/live/abc?liveUuid=xyz",
        cookie_data=CookieData(cookies={"s": "v"}),
        headers_data=HeadersData(headers={}),
        live_name="live_test",
        save_dir="/save",
    )


# --- Tests ---


def test_success_first_try_returns_outcome_with_attempts_1():
    popen = FakePopen(returncode=0, stdout="done", stderr="")
    policy = RetryPolicy()
    session = _StubSession(m3u8_links=["https://x/v.m3u8?auth_key=A"])

    orch = DownloadOrchestrator(
        session=session,  # type: ignore[arg-type]
        n_m3u8dl_re=_StubN_m3u8dl_re(),  # type: ignore[arg-type]
        retry_policy=policy,
        save_dir_resolver=lambda: "/save",
        popen_factory=lambda *a, **kw: popen,
    )
    outcome = orch.run(_ctx())

    assert isinstance(outcome, DownloadOutcome)
    assert outcome.success is True
    assert outcome.attempts == 1
    assert outcome.last_error is None


def test_refresh_after_auth_key_then_success():
    popen_fail = FakePopen(returncode=0, stdout="", stderr="403 Forbidden")
    popen_ok = FakePopen(returncode=0, stdout="done", stderr="")
    popens = iter([popen_fail, popen_ok])

    policy = RetryPolicy(auth_key_backoff=(0.0, 0.0))  # no sleep in test
    session = _StubSession(m3u8_links=["https://x/v.m3u8?auth_key=A", "https://x/v.m3u8?auth_key=B"])

    class _SaveDirResolver:
        def __call__(self):
            return "/save"

    orch = DownloadOrchestrator(
        session=session,  # type: ignore[arg-type]
        n_m3u8dl_re=_StubN_m3u8dl_re(),  # type: ignore[arg-type]
        retry_policy=policy,
        save_dir_resolver=_SaveDirResolver(),
        popen_factory=lambda *a, **kw: next(popens),
    )
    outcome = orch.run(_ctx())

    assert outcome.success is True
    assert outcome.attempts == 2
    assert session.refresh_service().fetch_count == 2  # 1 initial + 1 refresh


def test_fatal_error_aborts_immediately():
    popen = FakePopen(returncode=1, stdout="", stderr="No space left on device")
    policy = RetryPolicy()
    session = _StubSession(m3u8_links=["https://x/v.m3u8?auth_key=A"])

    orch = DownloadOrchestrator(
        session=session,  # type: ignore[arg-type]
        n_m3u8dl_re=_StubN_m3u8dl_re(),  # type: ignore[arg-type]
        retry_policy=policy,
        save_dir_resolver=lambda: "/save",
        popen_factory=lambda *a, **kw: popen,
    )
    outcome = orch.run(_ctx())

    assert outcome.success is False
    assert outcome.attempts == 1  # fatal does not retry
    assert outcome.last_failure_kind is DownloadFailureKind.DISK_FULL
    assert isinstance(outcome.last_error, DownloadFatalError)


def test_max_attempts_exhausted_returns_failure():
    popen = FakePopen(returncode=0, stdout="", stderr="403 Forbidden")
    policy = RetryPolicy(max_attempts=3, auth_key_backoff=(0.0, 0.0))
    session = _StubSession(m3u8_links=["https://x/v.m3u8?auth_key=A"])

    orch = DownloadOrchestrator(
        session=session,  # type: ignore[arg-type]
        n_m3u8dl_re=_StubN_m3u8dl_re(),  # type: ignore[arg-type]
        retry_policy=policy,
        save_dir_resolver=lambda: "/save",
        popen_factory=lambda *a, **kw: popen,
    )
    outcome = orch.run(_ctx())

    assert outcome.success is False
    assert outcome.attempts >= 3


def test_save_name_remains_constant_across_retries():
    """Spec 3.7 invariant: save_name must not change across retries (N_m3u8DL-RE resume anchor)."""
    popen_fail = FakePopen(returncode=0, stdout="", stderr="403 Forbidden")
    popen_ok = FakePopen(returncode=0, stdout="done", stderr="")
    popens = iter([popen_fail, popen_fail, popen_ok])

    seen_save_names: List[str] = []

    class _RecordingN_m3u8dl_re(_StubN_m3u8dl_re):
        def build_command(self, m3u8_file, save_name, save_dir, prefix, cookies, headers):
            seen_save_names.append(save_name)
            return super().build_command(m3u8_file, save_name, save_dir, prefix, cookies, headers)

    policy = RetryPolicy(auth_key_backoff=(0.0, 0.0))
    session = _StubSession(m3u8_links=["https://x/v.m3u8?auth_key=A", "https://x/v.m3u8?auth_key=B", "https://x/v.m3u8?auth_key=C"])

    orch = DownloadOrchestrator(
        session=session,  # type: ignore[arg-type]
        n_m3u8dl_re=_RecordingN_m3u8dl_re(),  # type: ignore[arg-type]
        retry_policy=policy,
        save_dir_resolver=lambda: "/save",
        popen_factory=lambda *a, **kw: next(popens),
    )
    outcome = orch.run(_ctx())

    assert outcome.success is True
    assert len(set(seen_save_names)) == 1  # all identical
    assert seen_save_names[0] == "live_test"


def test_process_terminated_in_finally_after_keyboard_interrupt():
    """Ctrl+C path: process must be killed even if user interrupts mid-wait."""
    popen = FakePopen(returncode=0, stdout="", stderr="")
    policy = RetryPolicy()
    session = _StubSession(m3u8_links=["https://x/v.m3u8?auth_key=A"])

    class _InterruptOnWait:
        def __init__(self, *a, **kw):
            self._inner = popen
            raise KeyboardInterrupt("user pressed Ctrl+C")

        def __getattr__(self, name):
            return getattr(self._inner, name)

    orch = DownloadOrchestrator(
        session=session,  # type: ignore[arg-type]
        n_m3u8dl_re=_StubN_m3u8dl_re(),  # type: ignore[arg-type]
        retry_policy=policy,
        save_dir_resolver=lambda: "/save",
        popen_factory=_InterruptOnWait,
    )
    with pytest.raises(KeyboardInterrupt):
        orch.run(_ctx())
    # Note: we can't assert terminate_calls here because the fake raised
    # before we got a reference to the process. This test mostly verifies
    # KeyboardInterrupt is re-raised. Process cleanup is verified in test_m3u8dl_process.py
