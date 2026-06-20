"""Tests for DownloadSession context manager."""

import pytest

from dingtalk_downloader.core.download_session import DownloadSession
from dingtalk_downloader.core.exceptions import M3u8RefreshError
from tests.fixtures.fake_browser import FakeBrowser


def test_session_yields_cookie_data_on_enter():
    # Override CookieHandler via subclass
    class _StubCookieHandler:
        def __init__(self, browser_type):
            self.browser_type = browser_type
            self.browser = FakeBrowser(m3u8_links=[])

        def get_cookie(self, url):
            from dingtalk_downloader.utils.models import CookieData, HeadersData
            return (
                CookieData(cookies={"session": "abc"}),
                HeadersData(headers={"User-Agent": "test"}),
                "live_name_test",
            )

        def close(self):
            self.browser.quit()

    # Monkeypatch the import inside DownloadSession
    import dingtalk_downloader.core.download_session as mod
    original = mod.CookieHandler
    mod.CookieHandler = _StubCookieHandler  # type: ignore[misc]
    try:
        with DownloadSession(browser_type="edge", save_mode="1") as session:
            assert session.live_name() == "live_name_test"
            assert session.cookie_data().get("session") == "abc"
    finally:
        mod.CookieHandler = original  # type: ignore[misc]


def test_session_closes_browser_on_exit():
    closed = []

    class _StubCookieHandler:
        def __init__(self, browser_type):
            self.browser_type = browser_type

        def get_cookie(self, url):
            from dingtalk_downloader.utils.models import CookieData, HeadersData
            return (
                CookieData(cookies={}),
                HeadersData(headers={}),
                "live",
            )

        def close(self):
            closed.append(True)

    import dingtalk_downloader.core.download_session as mod
    original = mod.CookieHandler
    mod.CookieHandler = _StubCookieHandler  # type: ignore[misc]
    try:
        with DownloadSession(browser_type="edge", save_mode="1"):
            pass
        assert closed == [True]
    finally:
        mod.CookieHandler = original  # type: ignore[misc]


def test_session_cleans_tracked_temp_files_on_exit():
    import os
    import tempfile

    closed = []

    class _StubCookieHandler:
        def __init__(self, browser_type):
            pass

        def get_cookie(self, url):
            from dingtalk_downloader.utils.models import CookieData, HeadersData
            return CookieData(cookies={}), HeadersData(headers={}), "live"

        def close(self):
            closed.append(True)

    # Create a real temp file the session will be told to clean
    with tempfile.NamedTemporaryFile(delete=False, suffix=".m3u8") as f:
        temp_path = f.name

    try:
        import dingtalk_downloader.core.download_session as mod
        original = mod.CookieHandler
        mod.CookieHandler = _StubCookieHandler  # type: ignore[misc]
        try:
            with DownloadSession(browser_type="edge", save_mode="1") as session:
                session.track_temp_file(temp_path)
            assert not os.path.exists(temp_path), "session should have deleted temp file"
        finally:
            mod.CookieHandler = original  # type: ignore[misc]
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_session_propagates_exceptions():
    class _StubCookieHandler:
        def __init__(self, browser_type):
            self.closed = False

        def get_cookie(self, url):
            from dingtalk_downloader.utils.models import CookieData, HeadersData
            return CookieData(cookies={}), HeadersData(headers={}), "live"

        def close(self):
            self.closed = True

    import dingtalk_downloader.core.download_session as mod
    original = mod.CookieHandler
    mod.CookieHandler = _StubCookieHandler  # type: ignore[misc]
    try:
        handler_ref = []

        class _Capture(mod.CookieHandler):  # type: ignore[misc]
            def __init__(self, bt):
                handler_ref.append(self)
                super().__init__(bt)

        mod.CookieHandler = _Capture  # type: ignore[misc]
        with pytest.raises(RuntimeError, match="boom"):
            with DownloadSession(browser_type="edge", save_mode="1"):
                raise RuntimeError("boom")
        assert handler_ref[0].closed is True
    finally:
        mod.CookieHandler = original  # type: ignore[misc]


def test_session_passes_real_url_to_cookie_handler():
    """Bug 1 regression: DownloadSession must forward the real share URL
    to CookieHandler.get_cookie(url), not the literal "placeholder" string.
    """
    captured_urls = []

    class _StubCookieHandler:
        def __init__(self, browser_type):
            self.browser_type = browser_type
            self.browser = FakeBrowser(m3u8_links=[])

        def get_cookie(self, url):
            captured_urls.append(url)
            from dingtalk_downloader.utils.models import CookieData, HeadersData
            return (
                CookieData(cookies={"session": "abc"}),
                HeadersData(headers={"User-Agent": "test"}),
                "live_name_test",
            )

        def close(self):
            self.browser.quit()

    import dingtalk_downloader.core.download_session as mod
    original = mod.CookieHandler
    mod.CookieHandler = _StubCookieHandler  # type: ignore[misc]
    try:
        real_url = "https://n.dingtalk.com/live/abc?liveUuid=01234567-89ab-cdef-0123-456789abcdef"
        with DownloadSession(
            browser_type="edge", save_mode="1", url=real_url
        ) as session:
            assert session.live_name() == "live_name_test"
        assert captured_urls == [real_url], (
            f"expected get_cookie to receive the real URL, got {captured_urls!r}"
        )
        assert "placeholder" not in captured_urls[0]
    finally:
        mod.CookieHandler = original  # type: ignore[misc]


def test_session_uses_injected_cookie_handler():
    """Bug 2 regression: DownloadSession must use the supplied cookie_handler
    instance instead of constructing a new one.
    """
    from dingtalk_downloader.utils.models import CookieData, HeadersData

    class _CustomHandler:
        def __init__(self):
            self.used = False
            self.closed = False

        def get_cookie(self, url):
            self.used = True
            return CookieData(cookies={"k": "v"}), HeadersData(headers={}), "name"

        def close(self):
            self.closed = True

    custom = _CustomHandler()
    with DownloadSession(
        browser_type="edge",
        save_mode="1",
        cookie_handler=custom,
        url="https://n.dingtalk.com/live/x?liveUuid=01234567-89ab-cdef-0123-456789abcdef",
    ) as session:
        assert session.cookie_data().get("k") == "v"
    assert custom.used is True, "injected cookie_handler was not used"
    assert custom.closed is True, "injected cookie_handler was not closed on exit"