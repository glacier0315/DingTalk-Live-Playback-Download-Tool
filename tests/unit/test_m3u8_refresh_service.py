"""Tests for the refactored M3u8RefreshService (formerly M3u8DownloadService)."""

import pytest

from dingtalk_downloader.core.exceptions import M3u8RefreshError
from dingtalk_downloader.core.m3u8_download_service import M3u8RefreshService  # noqa: E402
from dingtalk_downloader.utils.models import M3u8Link
from tests.fixtures.fake_browser import FakeBrowser


def test_fetch_returns_m3u8_link_with_new_path():
    browser = FakeBrowser(m3u8_links=["https://x/v.m3u8?auth_key=NEW"])
    svc = M3u8RefreshService(browser=browser, file_manager=None)  # type: ignore[arg-type]

    link = svc.fetch("https://n.dingtalk.com/live/abc?liveUuid=xyz")
    assert isinstance(link, M3u8Link)
    assert link.url == "https://x/v.m3u8?auth_key=NEW"
    assert link.local_file_path is not None
    assert len(link.local_file_path) > 0


def test_fetch_raises_m3u8_refresh_error_when_no_links():
    browser = FakeBrowser(m3u8_links=[])
    svc = M3u8RefreshService(browser=browser, file_manager=None)  # type: ignore[arg-type]

    with pytest.raises(M3u8RefreshError):
        svc.fetch("https://n.dingtalk.com/live/abc?liveUuid=xyz")


def test_fetch_retries_on_first_failure():
    browser = FakeBrowser(
        m3u8_links=["", "", "https://x/v.m3u8?auth_key=THIRD"],
    )
    svc = M3u8RefreshService(browser=browser, file_manager=None, max_attempts=5)  # type: ignore[arg-type]
    link = svc.fetch("https://n.dingtalk.com/live/abc?liveUuid=xyz")
    assert link.url == "https://x/v.m3u8?auth_key=THIRD"
    assert browser.refresh_count >= 2


def test_fetch_generates_unique_local_path_each_call():
    browser = FakeBrowser(m3u8_links=["https://x/v.m3u8?auth_key=A"])
    svc = M3u8RefreshService(browser=browser, file_manager=None)  # type: ignore[arg-type]
    p1 = svc.fetch("https://n.dingtalk.com/live/abc?liveUuid=xyz").local_file_path
    p2 = svc.fetch("https://n.dingtalk.com/live/abc?liveUuid=xyz").local_file_path
    assert p1 != p2