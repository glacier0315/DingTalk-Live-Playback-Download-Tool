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


def test_fetch_raises_m3u8_refresh_error_on_none_content(monkeypatch, tmp_path):
    """Minor 8 回归：浏览器 fetch 返回 None 时，必须抛 M3u8RefreshError。

    之前的行为是写入空文件，让 N_m3u8DL-RE 拿到无效 m3u8 失败。
    现在应该抛出明确的语义错误。
    """
    browser = FakeBrowser(m3u8_links=["https://x/v.m3u8?auth_key=Z"])
    # 让 fetch 调用返回 None（模拟浏览器 fetch 失败）
    browser.driver.execute_script = lambda script, *args: None

    svc = M3u8RefreshService(browser=browser, file_manager=None)  # type: ignore[arg-type]
    monkeypatch.setattr(svc, "_download_m3u8", svc._download_m3u8)
    # 直接调用 _download_m3u8 验证 None-content 路径
    with pytest.raises(M3u8RefreshError) as exc_info:
        svc._download_m3u8("https://x/v.m3u8?auth_key=Z")
    assert "浏览器 fetch 失败" in str(exc_info.value)


def test_download_m3u8_logs_debug_when_cleanup_oserror(monkeypatch, tmp_path, caplog):
    """None-content 防御性清理遇 OSError 必须记 debug 日志，不静默吞错。

    之前 ``except OSError: pass`` 会无声吞掉；现在 ``logger.debug`` 留痕。
    """
    import os

    from dingtalk_downloader.core import m3u8_download_service as mod

    browser = FakeBrowser(m3u8_links=["https://x/v.m3u8?auth_key=Z"])
    # 让 fetch 返回 None 触发防御性清理分支
    browser.driver.execute_script = lambda script, *args: None
    # 把 local_path 上的 os.remove 替换为抛 OSError
    monkeypatch.setattr(
        mod.os, "remove", lambda *a, **kw: (_ for _ in ()).throw(OSError("locked"))
    )
    # 让 os.path.exists 报告文件存在（让清理分支进入 remove 调用）
    monkeypatch.setattr(mod.os.path, "exists", lambda *a, **kw: True)

    svc = M3u8RefreshService(browser=browser, file_manager=None)  # type: ignore[arg-type]
    with caplog.at_level("DEBUG", logger="dingtalk_downloader.core.m3u8_download_service"):
        with pytest.raises(M3u8RefreshError):
            svc._download_m3u8("https://x/v.m3u8?auth_key=Z")
    assert any(
        "清理残留空 m3u8 文件失败" in rec.message and "OSError" in rec.message
        for rec in caplog.records
    ), f"未捕获到 debug 日志，实际记录: {[r.message for r in caplog.records]}"