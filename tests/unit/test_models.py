"""Tests for the new DownloadOutcome value object + DownloadFailureKind enum."""

import pytest

from dingtalk_downloader.core.exceptions import AuthKeyExpiredError, DownloadFatalError
from dingtalk_downloader.core.m3u8dl_process import DownloadFailureKind
from dingtalk_downloader.utils.models import DownloadOutcome


def test_success_outcome_construction():
    o = DownloadOutcome(
        success=True,
        attempts=2,
        last_failure_kind=None,
        last_error=None,
        elapsed_seconds=12.5,
    )
    assert o.success is True
    assert o.attempts == 2
    assert o.elapsed_seconds == 12.5


def test_failure_outcome_carries_diagnostics():
    err = AuthKeyExpiredError("m3u8 v3 expired")
    o = DownloadOutcome(
        success=False,
        attempts=50,
        last_failure_kind=DownloadFailureKind.AUTH_KEY_EXPIRED,
        last_error=err,
        elapsed_seconds=1800.0,
    )
    assert o.success is False
    assert o.last_failure_kind is DownloadFailureKind.AUTH_KEY_EXPIRED
    assert o.last_error is err
    assert o.attempts == 50


def test_outcome_rejects_non_int_attempts():
    with pytest.raises(ValueError, match="attempts"):
        DownloadOutcome(
            success=True,
            attempts="two",  # type: ignore[arg-type]
            last_failure_kind=None,
            last_error=None,
            elapsed_seconds=1.0,
        )


def test_outcome_rejects_negative_attempts():
    with pytest.raises(ValueError, match="attempts"):
        DownloadOutcome(
            success=True,
            attempts=-1,
            last_failure_kind=None,
            last_error=None,
            elapsed_seconds=1.0,
        )


def test_failure_kind_has_expected_values():
    # Enum is fully defined in T2 (not stub) per pre-flight decision
    assert DownloadFailureKind.AUTH_KEY_EXPIRED.value == "auth_key_expired"
    assert DownloadFailureKind.NETWORK_TRANSIENT.value == "network_transient"
    assert DownloadFailureKind.DISK_FULL.value == "disk_full"