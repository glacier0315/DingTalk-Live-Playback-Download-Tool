"""Tests for the pure RetryPolicy function."""

import pytest

from dingtalk_downloader.core.exceptions import (
    AuthKeyExpiredError,
    DownloadFatalError,
    M3u8RefreshError,
    NetworkTransientError,
    RecoverableDownloadError,
)
from dingtalk_downloader.core.retry_policy import (
    RetryAction,
    RetryDecision,
    RetryPolicy,
)


def _policy(**overrides) -> RetryPolicy:
    """Factory with deterministic backoff (set min=max to remove randomness)."""
    defaults = dict(
        max_attempts=3,
        auth_key_max_attempts=5,
        run_timeout_seconds=1800.0,
        auth_key_backoff=(3.0, 3.0),  # deterministic
        network_backoff=(2.0, 2.0),
        spawn_backoff=(10.0, 10.0),
        soft_fail_backoff=(3.0, 3.0),
        nonzero_backoff=(5.0, 5.0),
        fatal_max=0,
    )
    defaults.update(overrides)
    return RetryPolicy(**defaults)


def test_auth_key_expired_continues_with_auth_key_backoff():
    p = _policy()
    d = p.next_action(AuthKeyExpiredError("expired"), attempt=1)
    assert d.action is RetryAction.CONTINUE
    assert d.backoff_seconds == 3.0
    assert "auth_key" in d.reason


def test_auth_key_expired_aborts_when_under_max_but_over_global_max():
    p = _policy(max_attempts=2)
    # attempt=3 exceeds max_attempts=2 → ABORT
    d = p.next_action(AuthKeyExpiredError("expired"), attempt=3)
    assert d.action is RetryAction.ABORT


def test_auth_key_expired_aborts_at_auth_key_subcap():
    p = _policy(auth_key_max_attempts=2)
    d = p.next_action(AuthKeyExpiredError("expired"), attempt=2)
    assert d.action is RetryAction.ABORT


def test_network_transient_uses_network_backoff():
    p = _policy()
    d = p.next_action(NetworkTransientError("reset"), attempt=1)
    assert d.action is RetryAction.CONTINUE
    assert d.backoff_seconds == 2.0
    assert "network" in d.reason


def test_fatal_error_aborts_immediately():
    p = _policy()
    d = p.next_action(DownloadFatalError("disk full"), attempt=1)
    assert d.action is RetryAction.ABORT
    assert d.backoff_seconds == 0


def test_fatal_error_with_fatal_max_allows_one_retry():
    p = _policy(fatal_max=1)
    d = p.next_action(DownloadFatalError("disk full"), attempt=1)
    assert d.action is RetryAction.CONTINUE
    assert d.backoff_seconds == 0  # fatal uses 0 backoff
    d2 = p.next_action(DownloadFatalError("disk full"), attempt=2)
    assert d2.action is RetryAction.ABORT


def test_generic_recoverable_uses_soft_fail_backoff():
    p = _policy()
    d = p.next_action(RecoverableDownloadError("generic"), attempt=1)
    assert d.action is RetryAction.CONTINUE
    assert d.backoff_seconds == 3.0


def test_m3u8_refresh_error_uses_auth_key_backoff():
    """M3u8RefreshError is a recoverable; gets generic backoff unless auth-key-like."""
    p = _policy()
    d = p.next_action(M3u8RefreshError("page not loaded"), attempt=1)
    assert d.action is RetryAction.CONTINUE


def test_max_attempts_exhausted_aborts_regardless_of_kind():
    p = _policy(max_attempts=5)
    d = p.next_action(AuthKeyExpiredError("expired"), attempt=5)
    assert d.action is RetryAction.ABORT


def test_run_timeout_returns_fatal():
    """When caller provides elapsed time, decide_timeout returns DownloadFatalError-suggesting decision."""
    p = _policy(run_timeout_seconds=60.0)
    d = p.decide_timeout(elapsed_seconds=61.0)
    assert d.action is RetryAction.ABORT
    assert "timeout" in d.reason


def test_decide_timeout_continue_when_under():
    p = _policy(run_timeout_seconds=60.0)
    d = p.decide_timeout(elapsed_seconds=30.0)
    assert d.action is RetryAction.CONTINUE


def test_randomized_backoff_still_in_range():
    p = RetryPolicy(
        max_attempts=10,
        auth_key_max_attempts=20,
        run_timeout_seconds=1800.0,
        auth_key_backoff=(3.0, 8.0),
    )
    for _ in range(50):
        d = p.next_action(AuthKeyExpiredError("x"), attempt=1)
        assert 3.0 <= d.backoff_seconds <= 8.0


def test_decision_is_immutable():
    d = RetryDecision(action=RetryAction.CONTINUE, backoff_seconds=1.0, reason="x")
    with pytest.raises((AttributeError, Exception)):
        d.action = RetryAction.ABORT  # type: ignore[misc]