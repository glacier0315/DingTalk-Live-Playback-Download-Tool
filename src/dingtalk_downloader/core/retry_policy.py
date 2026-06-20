"""RetryPolicy —— 纯函数式重试决策。"""

import random
from dataclasses import dataclass
from enum import Enum
from typing import Tuple

from .exceptions import (
    AuthKeyExpiredError,
    DownloadFatalError,
    M3u8RefreshError,
    NetworkTransientError,
    ProcessSpawnError,
    RecoverableDownloadError,
)


class RetryAction(Enum):
    CONTINUE = "continue"
    ABORT = "abort"


@dataclass(frozen=True)
class RetryDecision:
    action: RetryAction
    backoff_seconds: float
    reason: str


class RetryPolicy:
    """根据异常类型与已重试次数返回下一步动作。

    纯函数：不发起 IO、不读时钟（除 decide_timeout 由调用方传入 elapsed）。
    """

    def __init__(
        self,
        *,
        max_attempts: int = 20,
        auth_key_max_attempts: int = 50,
        run_timeout_seconds: float = 1800.0,
        auth_key_backoff: Tuple[float, float] = (3.0, 8.0),
        network_backoff: Tuple[float, float] = (2.0, 5.0),
        spawn_backoff: Tuple[float, float] = (10.0, 15.0),
        soft_fail_backoff: Tuple[float, float] = (3.0, 6.0),
        nonzero_backoff: Tuple[float, float] = (5.0, 10.0),
        fatal_max: int = 0,
    ):
        self.max_attempts = max_attempts
        self.auth_key_max_attempts = auth_key_max_attempts
        self.run_timeout_seconds = run_timeout_seconds
        self._backoffs = {
            "auth_key": auth_key_backoff,
            "network": network_backoff,
            "spawn": spawn_backoff,
            "soft": soft_fail_backoff,
            "nonzero": nonzero_backoff,
        }
        self.fatal_max = fatal_max

    def next_action(self, error: Exception, attempt: int) -> RetryDecision:
        # 1. 全局上限
        if attempt > self.max_attempts:
            return RetryDecision(RetryAction.ABORT, 0.0, f"max_attempts={self.max_attempts} exceeded")

        # 2. 致命错误
        if isinstance(error, DownloadFatalError):
            if attempt <= self.fatal_max:
                return RetryDecision(RetryAction.CONTINUE, 0.0, "fatal:retry-once")
            return RetryDecision(RetryAction.ABORT, 0.0, f"fatal:{type(error).__name__}")

        # 3. 各类可重试异常
        if isinstance(error, AuthKeyExpiredError):
            if attempt >= self.auth_key_max_attempts:
                return RetryDecision(RetryAction.ABORT, 0.0, f"auth_key_max={self.auth_key_max_attempts}")
            return self._continue("auth_key", self._backoffs["auth_key"])

        if isinstance(error, NetworkTransientError):
            return self._continue("network", self._backoffs["network"])

        if isinstance(error, ProcessSpawnError):
            return self._continue("spawn", self._backoffs["spawn"])

        if isinstance(error, M3u8RefreshError):
            return self._continue("m3u8_refresh", self._backoffs["network"])

        if isinstance(error, RecoverableDownloadError):
            return self._continue("recoverable", self._backoffs["soft"])

        # 未知异常 → 保守 abort
        return RetryDecision(RetryAction.ABORT, 0.0, f"unknown:{type(error).__name__}")

    def decide_timeout(self, elapsed_seconds: float) -> RetryDecision:
        if elapsed_seconds > self.run_timeout_seconds:
            return RetryDecision(RetryAction.ABORT, 0.0, f"timeout:>{self.run_timeout_seconds}s")
        return RetryDecision(RetryAction.CONTINUE, 0.0, "under_timeout")

    def _continue(self, reason_prefix: str, backoff_range: Tuple[float, float]) -> RetryDecision:
        lo, hi = backoff_range
        backoff = random.uniform(lo, hi) if lo != hi else lo
        return RetryDecision(RetryAction.CONTINUE, backoff, f"{reason_prefix}_backoff")