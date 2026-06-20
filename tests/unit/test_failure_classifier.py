"""Tests for the failure classifier (pure function, no IO)."""

import pytest

from dingtalk_downloader.core.exceptions import (
    AuthKeyExpiredError,
    DownloadFatalError,
    NetworkTransientError,
    ProcessSpawnError,
    RecoverableDownloadError,
)
from dingtalk_downloader.core.m3u8dl_process import (
    DownloadFailureKind,
    classify_failure,
)


@pytest.mark.parametrize(
    "stderr_text, expected_kind",
    [
        # AUTH_KEY_EXPIRED variants
        ("HTTP/1.1 403 Forbidden", DownloadFailureKind.AUTH_KEY_EXPIRED),
        ("[error] got status 403", DownloadFailureKind.AUTH_KEY_EXPIRED),
        ("401 Unauthorized", DownloadFailureKind.AUTH_KEY_EXPIRED),
        # NETWORK_TRANSIENT
        ("Connection reset by peer", DownloadFailureKind.NETWORK_TRANSIENT),
        ("Connection aborted", DownloadFailureKind.NETWORK_TRANSIENT),
        ("Could not resolve host", DownloadFailureKind.NETWORK_TRANSIENT),
        ("502 Bad Gateway", DownloadFailureKind.NETWORK_TRANSIENT),
        ("503 Service Unavailable", DownloadFailureKind.NETWORK_TRANSIENT),
        ("504 Gateway Timeout", DownloadFailureKind.NETWORK_TRANSIENT),
        # DISK_FULL
        ("There is not enough space on the disk", DownloadFailureKind.DISK_FULL),
        ("No space left on device", DownloadFailureKind.DISK_FULL),
        ("磁盘空间不足", DownloadFailureKind.DISK_FULL),
        # PERMISSION_DENIED
        ("Access is denied", DownloadFailureKind.PERMISSION_DENIED),
        ("Permission denied", DownloadFailureKind.PERMISSION_DENIED),
        # INVALID_PATH
        ("Could not find a part of the path", DownloadFailureKind.INVALID_PATH),
        ("The system cannot find the path specified", DownloadFailureKind.INVALID_PATH),
        # EXE_MISSING (WindowsError[N] from subprocess + Chinese variant)
        ("WindowsError[2] 系统找不到指定的文件", DownloadFailureKind.EXE_MISSING),
        # SOFT_FAIL
        ("ERROR: segment 12 download failed", DownloadFailureKind.SOFT_FAIL),
        ("Failed to parse manifest", DownloadFailureKind.SOFT_FAIL),
        ("[ErrHttp] chunked transfer error", DownloadFailureKind.SOFT_FAIL),
    ],
)
def test_classify_recognizes_pattern(stderr_text, expected_kind):
    kind, _ = classify_failure(stderr_text, returncode=1)
    assert kind is expected_kind


def test_classify_returns_403_even_with_zero_returncode():
    kind, exc = classify_failure("status 403 Forbidden", returncode=0)
    assert kind is DownloadFailureKind.AUTH_KEY_EXPIRED
    assert isinstance(exc, AuthKeyExpiredError)


def test_classify_priority_disk_full_beats_nonzero():
    # Both DISK_FULL and NONZERO_EXIT could match; DISK_FULL wins
    kind, exc = classify_failure("No space left on device", returncode=42)
    assert kind is DownloadFailureKind.DISK_FULL
    assert isinstance(exc, DownloadFatalError)


def test_classify_falls_back_to_nonzero_exit():
    kind, exc = classify_failure("weird error XYZ", returncode=1)
    assert kind is DownloadFailureKind.NONZERO_EXIT
    assert isinstance(exc, RecoverableDownloadError)


def test_classify_zero_returncode_clean_output_returns_none():
    """returncode=0 + clean output → not a failure (caller passes empty stderr)."""
    kind, exc = classify_failure("", returncode=0)
    assert kind is None
    assert exc is None


def test_classify_unknown_text_with_nonzero_returns_nonzero_exit():
    kind, exc = classify_failure("???random???", returncode=2)
    assert kind is DownloadFailureKind.NONZERO_EXIT
    assert isinstance(exc, RecoverableDownloadError)


def test_classify_is_case_insensitive():
    kind, _ = classify_failure("FORBIDDEN access", returncode=0)
    assert kind is DownloadFailureKind.AUTH_KEY_EXPIRED
