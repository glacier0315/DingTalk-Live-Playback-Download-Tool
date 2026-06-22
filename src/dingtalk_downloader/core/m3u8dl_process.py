"""N_m3u8DL-RE 子进程包装 + 失败分类器。

- DownloadFailureKind: 失败原因枚举
- classify_failure: 纯函数，根据 stderr/returncode 分类
- M3u8DLProcess: 在 task 6 实现
"""

import logging
import os
import re
import subprocess
import time
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
from ..config.constants import RUN_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)


# 截取 stdout/stderr 尾部时保留的字节数（约 2 KiB），用于 RunResult 注入诊断信息
LOG_TAIL_BYTES = 2048


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
    # 不要求行首：N_m3u8DL-RE 的运行日志每行带 "HH:MM:SS.mmm " 前缀，
    # 仅靠 ^ 会漏掉 "20:04:01.644 ERROR: Failed" 这种真实失败行。
    (DownloadFailureKind.SOFT_FAIL, r"\berror\b\s*:", RecoverableDownloadError),
    (DownloadFailureKind.SOFT_FAIL, r"\bfailed\b", RecoverableDownloadError),
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
    log_tail: str
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
        popen_factory=subprocess.Popen,
    ):
        self._n_m3u8dl_re = n_m3u8dl_re
        self._log_path = log_path
        self._popen_factory = popen_factory
        self._proc = None
        self._waited = False
        self.last_command: list = []
        # 缓存 save_dir/save_name 供 wait() 做"金标准"成功判定：
        # save_dir 下若已存在 <save_name>.mp4 / <save_name>/<save_name>.mp4
        # 则 N_m3u8DL-RE 一定成功合并过——直接覆盖任何 NONZERO_EXIT 兜底判定。
        self._save_dir: Optional[str] = None
        self._save_name: Optional[str] = None

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
        self._save_dir = save_dir
        self._save_name = save_name
        logger.debug(f"执行命令: {' '.join(command)}")
        # 改写 --log-file-path 为本次 log_path
        if "--log-file-path" in command:
            idx = command.index("--log-file-path")
            if idx + 1 < len(command):
                command[idx + 1] = self._log_path
        # 用 stdout=PIPE/stderr=PIPE 而非 capture_output=True 以兼容 Python <3.7
        self._proc = self._popen_factory(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def wait(
        self,
        timeout: Optional[float] = None,
        on_timeout_grace_seconds: float = 5.0,
    ) -> RunResult:
        """等待子进程结束并返回 RunResult。

        判定优先级（成功信号先于失败关键字）：
        0. **强成功信号**（覆盖一切）：
           a. 金标准：save_dir 下已存在最终 mp4（说明 N_m3u8DL-RE 已经合并完成）
           b. 辅助：log 含 "INFO : Done" 且不含真实失败关键字
        1. 失败关键字扫描：N_m3u8DL-RE 的运行日志文件（最完整诊断流）
        2. 子进程 stderr。
        3. returncode（兜底 NONZERO_EXIT）。

        强成功信号是关键：ffmpeg 合并阶段常因 Non-monotonous DTS 等无害警告
        让 returncode 非 0、走 NONZERO_EXIT 兜底，从而误判已经成功的下载，
        触发 retry → refresh m3u8 → 旧分片因新 auth_key 失效被全部丢弃。

        Args:
            timeout: 等待子进程结束的最长秒数；``None`` 时使用 ``RUN_TIMEOUT_SECONDS``
                （30 分钟）。超时后调用 ``terminate(grace_seconds)`` 强杀子进程，
                并返回 ``failure_kind=NONZERO_EXIT`` 的 RunResult。
            on_timeout_grace_seconds: 超时后给子进程的优雅退出时间（秒）。
        """
        if self._proc is None:
            raise RuntimeError("M3u8DLProcess.start() must be called before wait()")

        effective_timeout = (
            timeout if timeout is not None else float(RUN_TIMEOUT_SECONDS)
        )
        try:
            stdout, stderr = self._proc.communicate(timeout=effective_timeout)
        except subprocess.TimeoutExpired:
            logger.warning(
                f"M3u8DLProcess.wait() 超时（>{effective_timeout:.1f}s），"
                f"调用 terminate(grace={on_timeout_grace_seconds:.1f}s) 强杀子进程"
            )
            self.terminate(grace_seconds=on_timeout_grace_seconds)
            # terminate 之后再读一次 stdout/stderr；可能为 None（子进程已死）
            try:
                stdout, stderr = self._proc.communicate(timeout=1.0)
            except Exception:
                stdout, stderr = "", ""
            # 超时必然视为失败（沿用 NONZERO_EXIT 兜底语义）
            return RunResult(
                returncode=-1,
                stdout_tail=(stdout or "")[-LOG_TAIL_BYTES:],
                stderr_tail=(stderr or "")[-LOG_TAIL_BYTES:],
                log_tail=self._read_log_tail(self._log_path),
                failure_kind=DownloadFailureKind.NONZERO_EXIT,
                error=RecoverableDownloadError(
                    f"wait() timed out after {effective_timeout:.1f}s"
                ),
            )

        # 用 poll() 取 returncode：兼容真实 subprocess.Popen（communicate 后会设好）
        # 和 FakePopen（只有 poll() 暴露 _returncode）
        polled = self._proc.poll()
        returncode = polled if polled is not None else 0
        self._waited = True

        stdout_tail = (stdout or "")[-LOG_TAIL_BYTES:]
        stderr_tail = (stderr or "")[-LOG_TAIL_BYTES:]
        log_tail = self._read_log_tail(self._log_path)

        # 强成功信号：金标准（mp4 文件存在） + 辅助（log 含 INFO : Done 且无失败关键字）
        if self._has_final_mp4() or self._is_done_success(log_tail):
            return RunResult(
                returncode=returncode,
                stdout_tail=stdout_tail,
                stderr_tail=stderr_tail,
                log_tail=log_tail,
                failure_kind=None,
                error=None,
            )

        # 把 log_tail 注入诊断流（log_tail 信息最完整，优先级最高）
        # 同时保留 stderr_tail 在 RunResult 里给上层做 warn 日志
        combined_diag = log_tail or ""
        if stderr_tail:
            combined_diag = combined_diag + "\n" + stderr_tail if combined_diag else stderr_tail

        # 先扫 log + stderr；只在前面没匹配时才回退到 stdout
        failure_kind, error = classify_failure(combined_diag, returncode)
        if failure_kind is None and stdout_tail and (
            returncode != 0 or combined_diag.strip()
        ):
            failure_kind, error = classify_failure(stdout_tail, returncode)

        if failure_kind is not None and error is None:
            # classify_failure 已经在 stderr 上调用过；这里只是兜底
            error = RecoverableDownloadError(f"unknown failure, rc={returncode}")

        return RunResult(
            returncode=returncode,
            stdout_tail=stdout_tail,
            stderr_tail=stderr_tail,
            log_tail=log_tail,
            failure_kind=failure_kind,
            error=error,
        )

    def _has_final_mp4(self) -> bool:
        """金标准：save_dir 下存在最终 mp4 → N_m3u8DL-RE 已成功合并。

        N_m3u8DL-RE 在 --save-dir 下输出 <save_name>.mp4（单流）或
        <save_name>/<save_name>.mp4（多流/带子目录）。两个位置都检查。
        """
        if not self._save_dir or not self._save_name:
            return False
        candidates = [
            os.path.join(self._save_dir, f"{self._save_name}.mp4"),
            os.path.join(self._save_dir, self._save_name, f"{self._save_name}.mp4"),
        ]
        return any(os.path.isfile(p) for p in candidates)

    @staticmethod
    def _is_done_success(log_text: str) -> bool:
        """辅助强成功信号：log 含 'INFO : Done' 且无真实失败关键字。

        N_m3u8DL-RE 完成合并后必打 INFO : Done（唯一明确成功标志）。
        若同时含 ERROR: Failed / 分片数量校验不通过 / 403 等真实失败关键字，
        则视为失败，避免对"部分合并后才出错"的场景误判成功。
        """
        if not log_text:
            return False
        if not re.search(r"INFO\s*:\s*Done", log_text):
            return False
        failure_markers = (
            r"分片数量校验不通过",
            r"ERROR\s*:\s*Failed",
            r"\b403\b",
        )
        for pattern in failure_markers:
            if re.search(pattern, log_text):
                return False
        return True

    def _read_log_tail(self, path: Optional[str], max_bytes: int = 65536) -> str:
        """读取 N_m3u8DL-RE 写入的运行日志尾部。

        N_m3u8DL-RE 把 403、RetryCount、"ERROR: 分片数量校验不通过" 等关键诊断
        信息写到 --log-file-path 指向的文件（而不是 stdout/stderr）。要正确
        判定失败，必须读这个文件。

        异常一律吞掉：文件不存在/被锁/权限不足都视作"无 log 内容"，让 classify
        继续走 stderr/stdout 路径，不让日志读取本身把 wait() 拖崩。
        """
        if not path:
            return ""
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                f.seek(0, 2)
                size = f.tell()
                if size > max_bytes:
                    f.seek(size - max_bytes)
                else:
                    f.seek(0)
                return f.read()
        except (OSError, IOError) as e:
            logger.debug(f"_read_log_tail 读取失败 [{type(e).__name__}]: {e}")
            return ""

    def terminate(self, grace_seconds: float = 5.0) -> None:
        """SIGTERM → 等 grace_seconds → 若仍存活则 SIGKILL。"""
        if self._proc is None:
            return
        try:
            self._proc.terminate()
            # 等 grace_seconds；用 is_alive() 判断是否仍存活
            # （FakePopen 没有 wait(timeout)，poll() 在 alive 时也只返回 None）
            deadline = time.monotonic() + grace_seconds
            while time.monotonic() < deadline:
                if not self.is_alive():
                    return
                time.sleep(min(0.05, max(0.0, deadline - time.monotonic())))
            # 子进程不响应 SIGTERM，升级到 SIGKILL
            if self.is_alive():
                try:
                    self._proc.kill()
                except Exception as e:
                    # 区分异常类型便于诊断（OSError/SubprocessError vs 其他）
                    logger.warning(
                        f"M3u8DLProcess kill() 异常 [{type(e).__name__}]: "
                        f"{e} — 子进程可能仍存活"
                    )
        except Exception as e:
            logger.warning(
                f"M3u8DLProcess.terminate() 异常 [{type(e).__name__}]: {e}"
            )

    def is_alive(self) -> bool:
        if self._proc is None:
            return False
        if self._waited:
            return False
        return self._proc.poll() is None
