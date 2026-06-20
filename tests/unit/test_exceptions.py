"""Verify the new download exception hierarchy is well-formed."""

import pytest

from dingtalk_downloader.core.exceptions import (
    AuthKeyExpiredError,
    DownloadError,
    DownloadFatalError,
    M3u8ParseError,
    M3u8RefreshError,
    NetworkError,
    NetworkTransientError,
    ProcessSpawnError,
    RecoverableDownloadError,
)


def test_auth_key_expired_is_recoverable_and_download_error():
    assert issubclass(AuthKeyExpiredError, RecoverableDownloadError)
    assert issubclass(AuthKeyExpiredError, DownloadError)


def test_network_transient_is_recoverable_and_download_error():
    assert issubclass(NetworkTransientError, RecoverableDownloadError)
    assert issubclass(NetworkTransientError, DownloadError)


def test_process_spawn_is_recoverable_and_download_error():
    assert issubclass(ProcessSpawnError, RecoverableDownloadError)
    assert issubclass(ProcessSpawnError, DownloadError)


def test_m3u8_refresh_is_recoverable_and_download_error():
    assert issubclass(M3u8RefreshError, RecoverableDownloadError)
    assert issubclass(M3u8RefreshError, DownloadError)


def test_fatal_is_download_error_but_not_recoverable():
    assert issubclass(DownloadFatalError, DownloadError)
    assert not issubclass(DownloadFatalError, RecoverableDownloadError)


def test_old_network_error_still_subclass_of_download_error():
    assert issubclass(NetworkError, DownloadError)


def test_old_m3u8_parse_error_still_subclass_of_download_error():
    assert issubclass(M3u8ParseError, DownloadError)


def test_recoverable_can_be_caught_as_download_error():
    with pytest.raises(DownloadError):
        raise AuthKeyExpiredError("test")
