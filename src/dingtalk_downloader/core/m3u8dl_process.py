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
    """包住 N_m3u8DL-RE 子进程，支持流式监控与优雅终止。

    永远不重试；只负责启动、等、报告、终止。
    通过 popen_factory 注入 subprocess.Popen，便于测试。
    """

    def __init__(
        self,
        n_m3u8dl_re,  # NM3u8DLRE — 避免循环导入，不做类型标注
        log_path: str,
        popen_factory=__import__("subprocess").Popen,
    ):
        self._n_m3u8dl_re = n_m3u8dl_re
        self._log_path = log_path
        self._popen_factory = popen_factory
        self._proc = None
        self._waited = False
        self.last_command: list = []

    def start(
        self,
        m3u8_file: str,
        save_name: str,
        save_dir: str,
        prefix: str,
        cookies: dict,
        headers: dict,
    ) -> None:
        """启动 N_m3u8DL-RE 子进程。"""
        command = self._n_m3u8dl_re.build_command(
            m3u8_file, save_name, save_dir, prefix, cookies, headers
        )
        self.last_command = command
        logger.debug(f"执行命令: {' '.join(command)}")
        # 改写 --log-file-path 为本次 log_path
        if "--log-file-path" in command:
            idx = command.index("--log-file-path")
            if idx + 1 < len(command):
                command[idx + 1] = self._log_path
        self._proc = self._popen_factory(command, capture_output=True, text=True)

    def wait(self, timeout: Optional[float] = None) -> RunResult:
        """等待子进程结束并返回 RunResult。

        双保险判定失败：
        1. returncode != 0 → 扫 stderr 关键字
        2. returncode == 0 但 stderr 命中无结果 → 扫 stdout 关键字（处理 403
           内嵌在输出里、但 stderr 却被静默的情况）
        注意：returncode == 0 且 stderr 为空 → 不再扫 stdout，避免对正常
        输出（如 "downloaded"）误判为 NONZERO_EXIT。
        """
        if self._proc is None:
            raise RuntimeError("M3u8DLProcess.start() must be called before wait()")

        stdout, stderr = self._proc.communicate(timeout=timeout)
        # 用 poll() 取 returncode：兼容真实 subprocess.Popen（communicate 后会设好）
        # 和 FakePopen（只有 poll() 暴露 _returncode）
        polled = self._proc.poll()
        returncode = polled if polled is not None else 0
        self._waited = True

        stdout_tail = (stdout or "")[-2048:]
        stderr_tail = (stderr or "")[-2048:]

        # 双保险：先看 stderr，再看 stdout
        failure_kind, error = classify_failure(stderr_tail, returncode)
        # 只有在以下情况才回退扫描 stdout：
        #   - returncode != 0（肯定出错了，找一下关键字定位原因）
        #   - stderr 非空但 classify_failure 没匹配（可能 403 内嵌在 stdout）
        # 避免对"downloaded"这类正常输出误判为失败
        if failure_kind is None and stdout_tail and (
            returncode != 0 or stderr_tail.strip()
        ):
            failure_kind, error = classify_failure(stdout_tail, returncode)

        if failure_kind is not None and error is None:
            # classify_failure 已经在 stderr 上调用过；这里只是兜底
            error = RecoverableDownloadError(f"unknown failure, rc={returncode}")

        return RunResult(
            returncode=returncode,
            stdout_tail=stdout_tail,
            stderr_tail=stderr_tail,
            failure_kind=failure_kind,
            error=error,
        )

    def terminate(self, grace_seconds: float = 5.0) -> None:
        """SIGTERM → 等 grace_seconds → 若仍存活则 SIGKILL。"""
        if self._proc is None:
            return
        try:
            self._proc.terminate()
            # 等 grace_seconds；用 is_alive() 判断是否仍存活
            # （FakePopen 没有 wait(timeout)，poll() 在 alive 时也只返回 None）
            import time

            deadline = time.monotonic() + grace_seconds
            while time.monotonic() < deadline:
                if not self.is_alive():
                    return
                time.sleep(min(0.05, max(0.0, deadline - time.monotonic())))
            # 子进程不响应 SIGTERM，升级到 SIGKILL
            if self.is_alive():
                try:
                    self._proc.kill()
                except Exception:
                    logger.warning("M3u8DLProcess kill() 也失败，子进程可能仍存活")
        except Exception as e:
            logger.warning(f"M3u8DLProcess.terminate() 异常: {e}")

    def is_alive(self) -> bool:
        if self._proc is None:
            return False
        if self._waited:
            return False
        return self._proc.poll() is None
