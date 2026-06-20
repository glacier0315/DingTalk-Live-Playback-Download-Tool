"""DownloadOrchestrator —— 单次下载的状态机。"""

import logging
import time
from typing import Callable, Optional

from .m3u8dl_process import DownloadFailureKind, M3u8DLProcess
from .retry_policy import RetryAction, RetryPolicy
from ..binary.n_m3u8dl_re import NM3u8DLRE
from ..utils.models import DownloadOutcome, M3u8Link, VideoDownloadContext
from .download_session import DownloadSession
from .exceptions import DownloadFatalError

logger = logging.getLogger(__name__)


class DownloadOrchestrator:
    """编排一次完整下载：拉 m3u8 → 启动子进程 → 监控 → 失败时刷新 → 续传。"""

    def __init__(
        self,
        session: DownloadSession,
        *,
        n_m3u8dl_re: NM3u8DLRE,
        retry_policy: RetryPolicy,
        save_dir_resolver: Callable[[], Optional[str]],
        popen_factory=__import__("subprocess").Popen,
        log_path_factory: Optional[Callable[[], str]] = None,
    ):
        self._session = session
        self._n_m3u8dl_re = n_m3u8dl_re
        self._policy = retry_policy
        self._save_dir_resolver = save_dir_resolver
        self._popen_factory = popen_factory
        self._log_path_factory = log_path_factory or _default_log_path

    def run(self, context: VideoDownloadContext) -> DownloadOutcome:
        save_dir = self._save_dir_resolver()
        if not save_dir:
            logger.error("save_dir 为空，无法下载")
            return DownloadOutcome(
                success=False,
                attempts=0,
                last_failure_kind=None,
                last_error=DownloadFatalError("save_dir 为空"),
                elapsed_seconds=0.0,
            )

        # live_name comes from the session (DOM-extracted) — NOT from context
        save_name = self._session.live_name()
        refresh = self._session.refresh_service()
        m3u8_link = refresh.fetch(context.url)
        self._session.track_temp_file(m3u8_link.local_file_path)

        attempt = 0
        last_error: Optional[Exception] = None
        last_kind: Optional[DownloadFailureKind] = None
        process: Optional[M3u8DLProcess] = None
        start_time = time.monotonic()

        try:
            while True:
                attempt += 1

                # 1. 超时检查
                elapsed = time.monotonic() - start_time
                timeout_decision = self._policy.decide_timeout(elapsed)
                if timeout_decision.action is RetryAction.ABORT:
                    raise DownloadFatalError(timeout_decision.reason)

                # 2. 启动子进程
                process = M3u8DLProcess(
                    n_m3u8dl_re=self._n_m3u8dl_re,
                    log_path=self._log_path_factory(),
                    popen_factory=self._popen_factory,
                )
                process.start(
                    m3u8_file=m3u8_link.local_file_path,
                    save_name=save_name,
                    save_dir=save_dir,
                    prefix=m3u8_link.prefix,
                    cookies=self._session.cookie_data().to_dict(),
                    headers=self._session.headers_data().to_dict(),
                )

                logger.info(
                    f"[attempt {attempt}] 启动 N_m3u8DL-RE save_name={save_name}"
                )

                # 3. 等子进程
                result = process.wait()

                # 4. 成功？
                if result.failure_kind is None:
                    logger.info(f"下载成功 (attempt {attempt}, 耗时 {elapsed:.1f}s)")
                    return DownloadOutcome(
                        success=True,
                        attempts=attempt,
                        last_failure_kind=None,
                        last_error=None,
                        elapsed_seconds=elapsed,
                    )

                # 5. 失败 → 决策
                last_error = result.error
                last_kind = result.failure_kind
                # N_m3u8DL-RE 把 403/分片失败/ERROR 等关键诊断写到 --log-file-path
                # 指向的文件，stdout/stderr 几乎为空；log_tail 比 stderr_tail 信息更全。
                logger.warning(
                    f"[retry {attempt}] failure_kind={last_kind.value}, "
                    f"stderr_tail={result.stderr_tail[-200:]!r}, "
                    f"log_tail={result.log_tail[-200:]!r}"
                )

                decision = self._policy.next_action(last_error, attempt)
                logger.info(
                    f"[retry {attempt}] decision={decision.action.value}, "
                    f"backoff={decision.backoff_seconds:.1f}s, reason={decision.reason}"
                )

                if decision.action is RetryAction.ABORT:
                    return DownloadOutcome(
                        success=False,
                        attempts=attempt,
                        last_failure_kind=last_kind,
                        last_error=last_error,
                        elapsed_seconds=elapsed,
                    )

                if decision.backoff_seconds > 0:
                    time.sleep(decision.backoff_seconds)

                # 6. 拉新 m3u8
                logger.info(f"[retry {attempt}] refreshing m3u8 from URL: {context.url}")
                m3u8_link = refresh.fetch(context.url)
                self._session.track_temp_file(m3u8_link.local_file_path)

        except KeyboardInterrupt:
            logger.warning("用户中断，正在终止子进程...")
            raise
        finally:
            if process is not None and process.is_alive():
                process.terminate(grace_seconds=2.0)


def _default_log_path() -> str:
    """默认 N_m3u8DL-RE 日志路径，每次返回新时间戳。"""
    import os
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, f"n_m3u8dl_re_{ts}.log")
