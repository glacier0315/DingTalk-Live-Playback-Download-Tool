"""Verify VideoDownloadManager thin-wrapper compatibility."""

from unittest.mock import patch

import pytest

from dingtalk_downloader.core.video_download_manager import VideoDownloadManager
from dingtalk_downloader.core.exceptions import AuthKeyExpiredError
from dingtalk_downloader.core.m3u8dl_process import DownloadFailureKind
from dingtalk_downloader.utils.models import (
    CookieData,
    DownloadOutcome,
    HeadersData,
    VideoDownloadContext,
)


def _ctx():
    return VideoDownloadContext(
        url="https://n.dingtalk.com/live/abc?liveUuid=xyz",
        cookie_data=CookieData(cookies={"s": "v"}),
        headers_data=HeadersData(headers={}),
        live_name="live",
        save_dir="/save",
        save_mode="1",
    )


def test_process_video_delegates_to_orchestrator_and_returns_bool():
    mgr = VideoDownloadManager(browser_type="edge", save_mode="1")
    fake_outcome = DownloadOutcome(
        success=True, attempts=1, last_failure_kind=None, last_error=None, elapsed_seconds=1.0
    )

    with patch(
        "dingtalk_downloader.core.video_download_manager.DownloadOrchestrator"
    ) as MockOrch, patch(
        "dingtalk_downloader.core.video_download_manager.DownloadSession"
    ) as MockSession:
        MockOrch.return_value.run.return_value = fake_outcome
        result = mgr.process_video(_ctx())

    assert result is True
    MockSession.assert_called_once()
    MockOrch.assert_called_once()
    MockOrch.return_value.run.assert_called_once()


def test_process_video_returns_false_on_failure_outcome():
    mgr = VideoDownloadManager(browser_type="edge", save_mode="1")
    fake_outcome = DownloadOutcome(
        success=False,
        attempts=3,
        last_failure_kind=DownloadFailureKind.AUTH_KEY_EXPIRED,
        last_error=AuthKeyExpiredError("expired"),
        elapsed_seconds=10.0,
    )

    with patch(
        "dingtalk_downloader.core.video_download_manager.DownloadOrchestrator"
    ) as MockOrch, patch(
        "dingtalk_downloader.core.video_download_manager.DownloadSession"
    ) as MockSession:
        MockOrch.return_value.run.return_value = fake_outcome
        result = mgr.process_video(_ctx())

    assert result is False


def test_initialize_download_returns_minimal_context():
    """initialize_download stays as a back-compat shim returning a minimal context."""
    mgr = VideoDownloadManager(browser_type="edge", save_mode="1")
    ctx = mgr.initialize_download("https://n.dingtalk.com/live/abc?liveUuid=xyz")
    assert ctx.url == "https://n.dingtalk.com/live/abc?liveUuid=xyz"
    assert ctx.save_mode == "1"
    # save_dir is resolved by path_selector — may be None in default mode without a real selector
    # live_name is a placeholder; real value comes from session inside process_video


def test_close_is_safe_when_never_initialized():
    mgr = VideoDownloadManager(browser_type="edge", save_mode="1")
    mgr.close()  # should not raise


def test_cleanup_context_is_safe_with_none():
    mgr = VideoDownloadManager(browser_type="edge", save_mode="1")
    mgr.cleanup_context(None)  # should not raise
