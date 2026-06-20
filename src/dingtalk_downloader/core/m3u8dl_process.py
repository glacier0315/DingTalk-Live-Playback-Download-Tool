"""N_m3u8DL-RE 子进程包装 + 失败分类器骨架。

本任务（T2）只放 enum 和 RunResult 数据类；classify_failure 完整实现在 T5，
M3u8DLProcess 完整实现在 T6。
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

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


@dataclass(frozen=True)
class RunResult:
    """M3u8DLProcess.wait 的返回值（在 T6 完整使用，T2 占位）。"""

    returncode: int
    stdout_tail: str
    stderr_tail: str
    failure_kind: Optional[DownloadFailureKind]
    error: Optional[Exception]