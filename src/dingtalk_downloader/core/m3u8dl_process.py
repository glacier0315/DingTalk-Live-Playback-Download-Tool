"""N_m3u8DL-RE 子进程包装 + 失败分类器。

- DownloadFailureKind: 失败原因枚举
- classify_failure: 纯函数，根据 stderr/returncode 分类
- M3u8DLProcess: 在 task 6 实现
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from .exceptions import (
    AuthKeyExpiredError,
    DownloadFatalError,
    NetworkTransientError,
    ProcessSpawnError,
    RecoverableDownloadError,
)

logger = logging.getLogger(__name__)


class DownloadFailureKind(Enum):
    """下载失败原因分类。"""

    AUTH_KEY_EXPIRED = "auth_key_expired"
    NETWORK_TRANSIENT = "network_transient"
    DISK_FULL = "disk_full"
    PERMISSION_DENIED = "permission_denied"
    INVALID_PATH = "invalid_path"
    EXE_MISSING = "exe_missing"
    SOFT_FAIL = "soft_fail"
    NONZERO_EXIT = "nonzero_exit"
    UNKNOWN = "unknown"


# 关键字 → 失败类型（按优先级排序：先匹配先生效）
_FAILURE_PATTERNS: Tuple[Tuple[DownloadFailureKind, str, type], ...] = (
    # DISK_FULL
    (DownloadFailureKind.DISK_FULL, r"there is not enough space", DownloadFatalError),
    (DownloadFailureKind.DISK_FULL, r"no space left", DownloadFatalError),
    (DownloadFailureKind.DISK_FULL, r"disk full", DownloadFatalError),
    (DownloadFailureKind.DISK_FULL, r"磁盘空间不足", DownloadFatalError),
    # PERMISSION_DENIED
    (DownloadFailureKind.PERMISSION_DENIED, r"access is denied", DownloadFatalError),
    (DownloadFailureKind.PERMISSION_DENIED, r"permission denied", DownloadFatalError),
    (DownloadFailureKind.PERMISSION_DENIED, r"unauthorizedaccess", DownloadFatalError),
    # INVALID_PATH
    (DownloadFailureKind.INVALID_PATH, r"could not find a part of the path", DownloadFatalError),
    (DownloadFailureKind.INVALID_PATH, r"the system cannot find the path", DownloadFatalError),
    (DownloadFailureKind.INVALID_PATH, r"invalid filename", DownloadFatalError),
    # EXE_MISSING
    (DownloadFailureKind.EXE_MISSING, r"windowserror\[2\]", ProcessSpawnError),
    (DownloadFailureKind.EXE_MISSING, r"系统找不到指定的文件", ProcessSpawnError),
    # NETWORK_TRANSIENT
    (DownloadFailureKind.NETWORK_TRANSIENT, r"connection reset", NetworkTransientError),
    (DownloadFailureKind.NETWORK_TRANSIENT, r"connection aborted", NetworkTransientError),
    (DownloadFailureKind.NETWORK_TRANSIENT, r"timeout", NetworkTransientError),
    (DownloadFailureKind.NETWORK_TRANSIENT, r"could not resolve", NetworkTransientError),
    (DownloadFailureKind.NETWORK_TRANSIENT, r"502 bad gateway", NetworkTransientError),
    (DownloadFailureKind.NETWORK_TRANSIENT, r"503 service", NetworkTransientError),
    (DownloadFailureKind.NETWORK_TRANSIENT, r"504 gateway", NetworkTransientError),
    # AUTH_KEY_EXPIRED
    (DownloadFailureKind.AUTH_KEY_EXPIRED, r"\b403\b", AuthKeyExpiredError),
    (DownloadFailureKind.AUTH_KEY_EXPIRED, r"forbidden", AuthKeyExpiredError),
    (DownloadFailureKind.AUTH_KEY_EXPIRED, r"unauthorized", AuthKeyExpiredError),
    (DownloadFailureKind.AUTH_KEY_EXPIRED, r"\b401\b", AuthKeyExpiredError),
    # SOFT_FAIL
    (DownloadFailureKind.SOFT_FAIL, r"^error:", RecoverableDownloadError),
    (DownloadFailureKind.SOFT_FAIL, r"^failed", RecoverableDownloadError),
    (DownloadFailureKind.SOFT_FAIL, r"\[errhttp\]", RecoverableDownloadError),
)


def classify_failure(
    stderr_text: str, returncode: int
) -> Tuple[Optional[DownloadFailureKind], Optional[Exception]]:
    """根据 stderr 文本和 returncode 分类失败原因。

    优先级：DISK_FULL > PERMISSION_DENIED > INVALID_PATH > EXE_MISSING
           > NETWORK_TRANSIENT > AUTH_KEY_EXPIRED > SOFT_FAIL

    Returns:
        (kind, exception)。如果 returncode=0 且 stderr 没关键字 → (None, None)
    """
    if returncode == 0 and not stderr_text.strip():
        return (None, None)

    haystack = stderr_text.lower() if stderr_text else ""

    for kind, pattern, exc_type in _FAILURE_PATTERNS:
        if re.search(pattern, haystack, re.IGNORECASE | re.MULTILINE):
            return (kind, exc_type(f"N_m3u8DL-RE failed: {kind.value}"))

    # 没匹配上关键字
    if returncode == 0:
        # returncode=0 但有 stderr 输出（且不是关键字命中）→ 仍按 NONZERO_EXIT 处理
        # 实际生产中这很少见；保守起见当作可恢复
        return (DownloadFailureKind.NONZERO_EXIT, RecoverableDownloadError("nonzero_exit"))
    return (DownloadFailureKind.NONZERO_EXIT, RecoverableDownloadError("nonzero_exit"))


@dataclass(frozen=True)
class RunResult:
    """M3u8DLProcess.wait 的返回值。"""

    returncode: int
    stdout_tail: str
    stderr_tail: str
    failure_kind: Optional[DownloadFailureKind]
    error: Optional[Exception]


# M3u8DLProcess 完整实现在 task 6
class M3u8DLProcess:
    """占位 —— task 6 实现。"""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("M3u8DLProcess is implemented in task 6")
