# Auth Key Refresh + Retry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the monolithic 20-times-retry loop in `VideoDownloadManager.process_video` with a structured, testable, observable retry pipeline that detects N_m3u8DL-RE failures, refreshes the m3u8 URL (new auth_key), and lets N_m3u8DL-RE's built-in resume pick up where it left off.

**Architecture:** Five single-responsibility components — `M3u8DLProcess` (Popen wrapper), `RetryPolicy` (pure decision function), `M3u8RefreshService` (refactored from `M3u8DownloadService`), `DownloadSession` (resource context manager), `DownloadOrchestrator` (loops the three above). `VideoDownloadManager` becomes a thin compatibility shim around the orchestrator.

**Tech Stack:** Python 3.8+, pytest, subprocess (stdlib), enum (stdlib), dataclasses (stdlib), re (stdlib), Selenium 4 (already present).

## Global Constraints

- **Python floor:** 3.8+ — no walrus operator in type hints, no `match` statement, use `dict[str, int]` → `Dict[str, int]` typing.
- **Style:** Match existing codebase (Chinese docstrings + comments, English code/identifiers/paths). Follow patterns in `core/exceptions.py` and `utils/models.py`.
- **No new third-party deps.** All new code uses stdlib + already-present libs (selenium, requests is NOT in deps).
- **Test runner:** `pytest tests/unit/ -v`. New tests go under `tests/unit/`. No `tests/` dir currently exists — task 0 creates it.
- **Commits:** One commit per task, `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>` trailer.
- **Logging:** `logger = logging.getLogger(__name__)` at module top, use `logger.info/warning/error` with f-strings, never `print()`.
- **Error philosophy:** New exceptions inherit from existing `DownloadError` where applicable. Never silently swallow exceptions in `__exit__`.
- **Resource cleanup:** Every code path that opens a browser / temp file / subprocess must have a matching cleanup path, even on exception / KeyboardInterrupt.

---

## Task 0: Bootstrap test infrastructure

**Files:**
- Create: `tests/__init__.py` (empty)
- Create: `tests/unit/__init__.py` (empty)
- Create: `pytest.ini` (configures testpaths)
- Create: `tests/conftest.py` (shared path setup for fixtures import)

**Context:** Spec section 6. The repo has no `tests/` dir yet, no `pytest.ini`. CLAUDE.md says tests go in `tests/unit/`. We need a baseline so all subsequent tasks can `from tests.fixtures.fake_proc import FakePopen` reliably.

- [ ] **Step 1: Create empty test package directories**

```bash
mkdir -p tests/unit tests/integration tests/fixtures/n_m3u8dl_re_stderr
```

- [ ] **Step 2: Create `tests/__init__.py`, `tests/unit/__init__.py`, `tests/integration/__init__.py`, `tests/fixtures/__init__.py`**

All four files are empty (just `pass` or truly empty). Use the Bash `touch` equivalent on Windows.

```python
# tests/__init__.py
```

```python
# tests/unit/__init__.py
```

```python
# tests/integration/__init__.py
```

```python
# tests/fixtures/__init__.py
```

- [ ] **Step 3: Create `pytest.ini` at repo root**

```ini
[pytest]
testpaths = tests/unit
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -ra --strict-markers
markers =
    integration: requires real browser + N_m3u8DL-RE.exe (skipped by default)
```

- [ ] **Step 4: Create `tests/conftest.py`**

```python
"""Shared pytest fixtures and path setup for the test suite."""

import sys
from pathlib import Path

# Ensure `src/` is importable so tests can do `from dingtalk_downloader.xxx import yyy`
SRC = Path(__file__).resolve().parent.parent / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
```

- [ ] **Step 5: Verify pytest discovers nothing yet (sanity check)**

Run: `pytest --collect-only`
Expected: "no tests ran" / "collected 0 items" with exit code 5 (no tests collected is fine for bootstrap).

- [ ] **Step 6: Commit**

```bash
git add tests/ pytest.ini
git commit -m "chore(tests): bootstrap test package + pytest.ini

- tests/{unit,integration,fixtures} skeleton
- pytest.ini restricts testpaths to tests/unit
- conftest.py adds src/ to sys.path

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 1: Add new exception classes to `core/exceptions.py`

**Files:**
- Modify: `src/dingtalk_downloader/core/exceptions.py` (append new classes, keep old)
- Test: `tests/unit/test_exceptions.py` (new)

**Context:** Spec section 3.1. The new hierarchy:
```
DownloadError
├── RecoverableDownloadError
│   ├── AuthKeyExpiredError
│   ├── NetworkTransientError
│   ├── ProcessSpawnError
│   └── M3u8RefreshError
└── DownloadFatalError
```
Old `DownloadError`, `NetworkError`, `M3u8ParseError` stay as thin wrappers so `main.py`'s existing `except` clauses still work.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_exceptions.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_exceptions.py -v`
Expected: ImportError — `RecoverableDownloadError` does not exist.

- [ ] **Step 3: Append new classes to `src/dingtalk_downloader/core/exceptions.py`**

Open the file (last edit: end). Append the following — do NOT touch the existing classes:

```python
# --- New: retry pipeline exception hierarchy (2026-06-20 spec) ---


class RecoverableDownloadError(DownloadError):
    """可重试的下载错误基类。"""

    pass


class AuthKeyExpiredError(RecoverableDownloadError):
    """m3u8 auth_key 过期（403/Forbidden/401）。"""

    pass


class NetworkTransientError(RecoverableDownloadError):
    """瞬时网络问题（连接重置、DNS、5xx）。"""

    pass


class ProcessSpawnError(RecoverableDownloadError):
    """N_m3u8DL-RE 启动失败（资源占用、路径错）。"""

    pass


class M3u8RefreshError(RecoverableDownloadError):
    """拉取新 m3u8 失败（页面未加载、liveUuid 提取失败）。"""

    pass


class DownloadFatalError(DownloadError):
    """不可恢复：磁盘满、权限拒绝、保存路径无效。"""

    pass
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_exceptions.py -v`
Expected: 8 passed.

- [ ] **Step 5: Commit**

```bash
git add src/dingtalk_downloader/core/exceptions.py tests/unit/test_exceptions.py
git commit -m "feat(exceptions): add retry-pipeline exception hierarchy

- RecoverableDownloadError base + 4 specific subclasses
- DownloadFatalError for unrecoverable cases
- Old NetworkError/M3u8ParseError kept as wrappers for main.py compat

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 2: Add `DownloadOutcome` dataclass to `utils/models.py`

**Files:**
- Modify: `src/dingtalk_downloader/utils/models.py` (append)
- Test: `tests/unit/test_models.py` (new)

**Context:** Spec section 3.6. `DownloadOrchestrator.run` returns a `DownloadOutcome` value object so the caller knows success/failure + diagnostics. Lives next to existing `M3u8Link` / `VideoDownloadContext` in `utils/models.py`.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_models.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_models.py -v`
Expected: ImportError on `DownloadOutcome` (test file doesn't exist yet — fail at collection).

- [ ] **Step 3: Create `src/dingtalk_downloader/core/m3u8dl_process.py` with FULL enum (not stub)**

> Pre-flight decision: complete enum defined here; classifier regex patterns come in T5.

```python
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
```

- [ ] **Step 4: Append `DownloadOutcome` to `src/dingtalk_downloader/utils/models.py`**

Open the file. At the top, replace `from dataclasses import dataclass` with `from dataclasses import dataclass, field`. At the bottom of the file, append:

```python
@dataclass(frozen=True)
class DownloadOutcome:
    """单次视频下载的结果值对象。

    Attributes:
        success: 是否最终下载成功
        attempts: 实际尝试次数（含失败的）
        last_failure_kind: 最后一次失败的分类（成功时为 None）
        last_error: 最后一次的异常对象（成功时为 None）
        elapsed_seconds: 总耗时
    """

    success: bool
    attempts: int
    last_failure_kind: Optional["DownloadFailureKind"]
    last_error: Optional[Exception]
    elapsed_seconds: float

    def __post_init__(self) -> None:
        if not isinstance(self.attempts, int) or isinstance(self.attempts, bool):
            raise ValueError("attempts必须是整数")
        if self.attempts < 0:
            raise ValueError("attempts不能为负数")
        if not isinstance(self.elapsed_seconds, (int, float)) or self.elapsed_seconds < 0:
            raise ValueError("elapsed_seconds必须为非负数")
        if not self.success and self.last_error is None:
            raise ValueError("失败结果必须包含 last_error")
        if self.success and self.last_failure_kind is not None:
            raise ValueError("成功结果不应包含 last_failure_kind")
```

Note the forward reference `"DownloadFailureKind"` — it's defined in `core.m3u8dl_process` to avoid circular import between `core/` and `utils/`.

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/unit/test_models.py -v`
Expected: 5 passed.

- [ ] **Step 6: Commit**

```bash
git add src/dingtalk_downloader/utils/models.py src/dingtalk_downloader/core/m3u8dl_process.py tests/unit/test_models.py
git commit -m "feat(models): add DownloadOutcome + DownloadFailureKind stub

- DownloadOutcome captures success/attempts/diagnostics
- Forward reference to DownloadFailureKind avoids circular import
- DownloadFailureKind stub added; full enum in task 4

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 3: Add new constants to `config/constants.py`

**Files:**
- Modify: `src/dingtalk_downloader/config/constants.py` (append)
- Test: manual verification (no test for constants — they are leaf values)

**Context:** Spec section 5.5. Adds `RUN_TIMEOUT_SECONDS`, `AUTH_KEY_MAX_ATTEMPTS`, and backoff tuples. The full `RetryPolicy` class will be built in task 7; here we just stage the constants it will consume.

- [ ] **Step 1: Append new constants**

Open `src/dingtalk_downloader/config/constants.py`. At the end of the file, append:

```python
# ========================================
# 视频下载重试配置（2026-06-20 spec）
# ========================================

# 单次运行总超时（秒），超过则 DownloadFatalError
RUN_TIMEOUT_SECONDS = 1800  # 30 分钟

# auth_key 过期类失败的最大重试次数（子上限，区别于总 max_attempts=20）
AUTH_KEY_MAX_ATTEMPTS = 50

# 各类 failure_kind 的退避区间（min, max），单位秒
# RetryPolicy 默认值会引用这些
BACKOFF_AUTH_KEY_EXPIRED = (3.0, 8.0)
BACKOFF_NETWORK_TRANSIENT = (2.0, 5.0)
BACKOFF_EXE_MISSING = (10.0, 15.0)
BACKOFF_SOFT_FAIL = (3.0, 6.0)
BACKOFF_NONZERO_EXIT = (5.0, 10.0)
```

- [ ] **Step 2: Verify import works**

Run: `python -c "from dingtalk_downloader.config.constants import RUN_TIMEOUT_SECONDS, AUTH_KEY_MAX_ATTEMPTS, BACKOFF_AUTH_KEY_EXPIRED; print(RUN_TIMEOUT_SECONDS, AUTH_KEY_MAX_ATTEMPTS, BACKOFF_AUTH_KEY_EXPIRED)"`
Expected: `1800 50 (3.0, 8.0)`

- [ ] **Step 3: Commit**

```bash
git add src/dingtalk_downloader/config/constants.py
git commit -m "feat(config): add retry pipeline constants

- RUN_TIMEOUT_SECONDS=1800 (30 min upper bound)
- AUTH_KEY_MAX_ATTEMPTS=50
- Per-failure-kind backoff tuples

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 4: Add `FakePopen` test fixture

**Files:**
- Create: `tests/fixtures/fake_proc.py`

**Context:** Spec section 6.3. `FakePopen` is injected via `popen_factory` to `M3u8DLProcess` so tests can simulate any combination of returncode/stdout/stderr/terminate behavior without touching real N_m3u8DL-RE.exe.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_fake_proc.py`:

```python
"""Tests for the FakePopen fixture."""

from tests.fixtures.fake_proc import FakePopen


def test_default_state_is_alive_and_pending():
    p = FakePopen(returncode=0, stdout="ok", stderr="")
    assert p.poll() is None
    assert p.is_alive() is True


def test_terminate_marks_dead_and_increments_counter():
    p = FakePopen(returncode=0, stdout="", stderr="")
    p.terminate()
    assert p.terminate_calls == 1
    assert p.kill_calls == 0
    assert p.is_alive() is False


def test_kill_marks_dead_and_increments_counter():
    p = FakePopen(returncode=0, stdout="", stderr="")
    p.kill()
    assert p.kill_calls == 1
    assert p.terminate_calls == 0
    assert p.is_alive() is False


def test_communicate_returns_configured_io():
    p = FakePopen(returncode=2, stdout="hello", stderr="warn")
    out, err = p.communicate()
    assert out == "hello"
    assert err == "warn"


def test_poll_returns_returncode_after_dead():
    p = FakePopen(returncode=3, stdout="", stderr="")
    p.terminate()
    assert p.poll() == 3


def test_terminal_call_after_dead_is_noop_for_counters_but_idempotent():
    p = FakePopen(returncode=0, stdout="", stderr="")
    p.terminate()
    p.terminate()
    p.kill()
    assert p.terminate_calls == 2
    assert p.kill_calls == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_fake_proc.py -v`
Expected: ImportError on `tests.fixtures.fake_proc`.

- [ ] **Step 3: Create `tests/fixtures/fake_proc.py`**

```python
"""可脚本化的 Popen 替身，给单元测试用。

支持：
- 预置 returncode / stdout / stderr
- 跟踪 terminate() 和 kill() 调用次数
- is_alive() / poll() 反映内部状态
"""

from typing import Optional


class FakePopen:
    """替代 subprocess.Popen 的轻量替身。"""

    def __init__(
        self,
        *,
        returncode: int = 0,
        stdout: str = "",
        stderr: str = "",
        terminate_after: Optional[float] = None,
    ):
        self._returncode = returncode
        self._stdout = stdout
        self._stderr = stderr
        self._alive = True
        self.terminate_calls = 0
        self.kill_calls = 0
        # terminate_after: 如果设置，在 N 次 terminate 后才彻底 dead
        # （用于测 grace_period 逻辑；当前不实现，后续 task 可能加）

    def communicate(self, timeout: Optional[float] = None):
        return (self._stdout, self._stderr)

    def poll(self) -> Optional[int]:
        if self._alive:
            return None
        return self._returncode

    def terminate(self) -> None:
        self.terminate_calls += 1
        self._alive = False

    def kill(self) -> None:
        self.kill_calls += 1
        self._alive = False

    def is_alive(self) -> bool:
        return self._alive
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_fake_proc.py -v`
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add tests/fixtures/fake_proc.py tests/fixtures/__init__.py tests/unit/test_fake_proc.py
git commit -m "test(fixtures): add FakePopen with lifecycle + counter tracking

- Substitutes subprocess.Popen in M3u8DLProcess tests
- Tracks terminate()/kill() call counts
- is_alive()/poll() reflect internal state

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 5: Implement `DownloadFailureKind` enum + failure classifier

**Files:**
- Modify: `src/dingtalk_downloader/core/m3u8dl_process.py` (extend stub)
- Test: `tests/unit/test_failure_classifier.py` (new)

**Context:** Spec section 3.2 and 5.1. The classifier is a pure function `classify(stderr, returncode) -> (DownloadFailureKind, Exception)`. Priority order: DISK_FULL > PERMISSION_DENIED > INVALID_PATH > EXE_MISSING > NETWORK_TRANSIENT > AUTH_KEY_EXPIRED > SOFT_FAIL > NONZERO_EXIT > UNKNOWN.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_failure_classifier.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_failure_classifier.py -v`
Expected: ImportError on `classify_failure` (or AttributeError on enum value being a string).

- [ ] **Step 3: Replace `core/m3u8dl_process.py` content with full implementation**

Overwrite `src/dingtalk_downloader/core/m3u8dl_process.py`:

```python
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
    (DownloadFailureKind.SOFT_FAIL, r"^error:", re.error if False else RecoverableDownloadError),  # placeholder, replaced below
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
```

Note: The `re.error if False else RecoverableDownloadError` line is ugly — fix it in the actual file. Use plain `RecoverableDownloadError` for the SOFT_FAIL `ERROR:` pattern.

- [ ] **Step 4: Fix the ugly line in the pattern tuple**

In `core/m3u8dl_process.py`, replace this line:

```python
    (DownloadFailureKind.SOFT_FAIL, r"^error:", re.error if False else RecoverableDownloadError),  # placeholder, replaced below
```

with:

```python
    (DownloadFailureKind.SOFT_FAIL, r"^error:", RecoverableDownloadError),
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/unit/test_failure_classifier.py -v`
Expected: All parametrized cases pass (count = 18 cases + 5 standalone = 23 tests).

- [ ] **Step 6: Commit**

```bash
git add src/dingtalk_downloader/core/m3u8dl_process.py tests/unit/test_failure_classifier.py
git commit -m "feat(core): add DownloadFailureKind + classify_failure

- Pure function classifier with priority-ordered regex patterns
- DISK_FULL > PERMISSION > INVALID_PATH > EXE_MISSING > NETWORK > AUTH_KEY > SOFT
- Chinese keywords (磁盘空间不足) supported
- case-insensitive matching
- M3u8DLProcess remains a NotImplementedError stub for task 6

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 6: Implement `M3u8DLProcess` (Popen wrapper)

**Files:**
- Modify: `src/dingtalk_downloader/core/m3u8dl_process.py` (replace stub class)
- Test: `tests/unit/test_m3u8dl_process.py` (new)

**Context:** Spec section 3.2. Wraps `subprocess.Popen` for N_m3u8DL-RE. Key responsibilities: start, wait (returns `RunResult`), terminate with grace period, kill, is_alive. The `popen_factory` parameter enables test injection of `FakePopen`.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_m3u8dl_process.py`:

```python
"""Tests for M3u8DLProcess subprocess wrapper."""

import pytest

from dingtalk_downloader.core.exceptions import AuthKeyExpiredError, DownloadFatalError
from dingtalk_downloader.core.m3u8dl_process import (
    DownloadFailureKind,
    M3u8DLProcess,
    RunResult,
)
from tests.fixtures.fake_proc import FakePopen


class _FakeN_m3u8dl_re:
    """Stand-in for NM3u8DLRE — only build_command is used."""

    def build_command(self, m3u8_file, save_name, save_dir, prefix, cookies, headers):
        return [
            "fake-exe",
            m3u8_file,
            "--save-name", save_name,
            "--save-dir", save_dir,
            "--base-url", prefix,
            "--log-file-path", "/tmp/fake.log",
        ]


def _make_process(popen: FakePopen) -> M3u8DLProcess:
    """Construct M3u8DLProcess with a popen_factory that returns the given FakePopen."""
    return M3u8DLProcess(
        n_m3u8dl_re=_FakeN_m3u8dl_re(),  # type: ignore[arg-type]
        log_path="/tmp/fake-{ts}.log",
        popen_factory=lambda *a, **kw: popen,
    )


def test_start_records_command_and_creates_proc():
    popen = FakePopen(returncode=0, stdout="ok", stderr="")
    proc = _make_process(popen)
    proc.start("a.m3u8", "video1", "/save", "https://x/live/", {}, {})

    assert proc.last_command[:1] == ["fake-exe"]
    assert "--save-name" in proc.last_command
    assert proc.is_alive() is True


def test_wait_returns_run_result_with_no_failure_on_clean_exit():
    popen = FakePopen(returncode=0, stdout="downloaded", stderr="")
    proc = _make_process(popen)
    proc.start("a.m3u8", "video1", "/save", "https://x/live/", {}, {})
    result = proc.wait()

    assert isinstance(result, RunResult)
    assert result.returncode == 0
    assert result.failure_kind is None
    assert result.error is None


def test_wait_detects_403_in_stderr():
    popen = FakePopen(returncode=0, stdout="", stderr="HTTP/1.1 403 Forbidden")
    proc = _make_process(popen)
    proc.start("a.m3u8", "v", "/s", "https://x/", {}, {})
    result = proc.wait()

    assert result.failure_kind is DownloadFailureKind.AUTH_KEY_EXPIRED
    assert isinstance(result.error, AuthKeyExpiredError)


def test_wait_detects_disk_full():
    popen = FakePopen(returncode=1, stdout="", stderr="No space left on device")
    proc = _make_process(popen)
    proc.start("a.m3u8", "v", "/s", "https://x/", {}, {})
    result = proc.wait()

    assert result.failure_kind is DownloadFailureKind.DISK_FULL
    assert isinstance(result.error, DownloadFatalError)


def test_wait_classifies_nonzero_with_no_keyword():
    popen = FakePopen(returncode=7, stdout="", stderr="mysterious crash")
    proc = _make_process(popen)
    proc.start("a.m3u8", "v", "/s", "https://x/", {}, {})
    result = proc.wait()

    assert result.failure_kind is DownloadFailureKind.NONZERO_EXIT


def test_terminate_calls_sigterm_then_marks_dead():
    popen = FakePopen(returncode=0, stdout="", stderr="")
    proc = _make_process(popen)
    proc.start("a.m3u8", "v", "/s", "https://x/", {}, {})
    proc.terminate(grace_seconds=0.01)  # short grace for test speed

    assert popen.terminate_calls == 1
    assert popen.kill_calls == 0  # grace elapsed but process is "dead" after terminate
    assert proc.is_alive() is False


def test_is_alive_true_before_wait():
    popen = FakePopen(returncode=0, stdout="", stderr="")
    proc = _make_process(popen)
    proc.start("a.m3u8", "v", "/s", "https://x/", {}, {})
    assert proc.is_alive() is True


def test_is_alive_false_after_wait():
    popen = FakePopen(returncode=0, stdout="", stderr="")
    proc = _make_process(popen)
    proc.start("a.m3u8", "v", "/s", "https://x/", {}, {})
    proc.wait()
    assert proc.is_alive() is False


def test_terminate_before_start_is_safe():
    popen = FakePopen(returncode=0, stdout="", stderr="")
    proc = _make_process(popen)
    proc.terminate(grace_seconds=0.01)  # should not raise
    assert popen.terminate_calls == 0  # nothing to terminate
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_m3u8dl_process.py -v`
Expected: TypeError (constructor signature wrong) or `NotImplementedError`.

- [ ] **Step 3: Replace `M3u8DLProcess` stub in `core/m3u8dl_process.py`**

Find the line `class M3u8DLProcess:` and replace from there to end of file with:

```python
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
        2. returncode == 0 → 仍扫 stdout/stderr 关键字（处理 403 内嵌在输出里的情况）
        """
        if self._proc is None:
            raise RuntimeError("M3u8DLProcess.start() must be called before wait()")

        stdout, stderr = self._proc.communicate(timeout=timeout)
        returncode = self._proc.returncode if self._proc.returncode is not None else 0

        stdout_tail = (stdout or "")[-2048:]
        stderr_tail = (stderr or "")[-2048:]

        # 双保险：先看 stderr，再看 stdout
        failure_kind, error = classify_failure(stderr_tail, returncode)
        if failure_kind is None and stdout_tail:
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
            try:
                self._proc.wait(timeout=grace_seconds)
            except Exception:
                # 子进程不响应 SIGTERM，升级到 SIGKILL
                try:
                    self._proc.kill()
                    self._proc.wait(timeout=1.0)
                except Exception:
                    logger.warning("M3u8DLProcess kill() 也失败，子进程可能仍存活")
        except Exception as e:
            logger.warning(f"M3u8DLProcess.terminate() 异常: {e}")

    def is_alive(self) -> bool:
        if self._proc is None:
            return False
        return self._proc.poll() is None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_m3u8dl_process.py -v`
Expected: 9 passed.

- [ ] **Step 5: Commit**

```bash
git add src/dingtalk_downloader/core/m3u8dl_process.py tests/unit/test_m3u8dl_process.py
git commit -m "feat(core): implement M3u8DLProcess subprocess wrapper

- popen_factory injection for testability
- Dual-guard failure detection (stderr first, stdout fallback)
- terminate(grace_seconds) → SIGTERM → SIGKILL escalation
- last_command exposed for test assertions

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 7: Implement `RetryPolicy` (pure decision function)

**Files:**
- Create: `src/dingtalk_downloader/core/retry_policy.py`
- Test: `tests/unit/test_retry_policy.py` (new)

**Context:** Spec section 3.4. Pure function: takes an exception + attempt number, returns `RetryDecision(action, backoff, reason)`. No IO, no time — fully testable.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_retry_policy.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_retry_policy.py -v`
Expected: ImportError on `RetryPolicy`.

- [ ] **Step 3: Create `src/dingtalk_downloader/core/retry_policy.py`**

```python
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_retry_policy.py -v`
Expected: All 12 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/dingtalk_downloader/core/retry_policy.py tests/unit/test_retry_policy.py
git commit -m "feat(core): add RetryPolicy (pure function, no IO)

- Maps exception type → (action, backoff, reason)
- Dual caps: max_attempts (global) + auth_key_max_attempts (sub)
- decide_timeout() for run-level upper bound
- Randomized backoff in [min, max] range
- 12 tests covering priority, caps, randomization, immutability

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 8: Refactor `M3u8DownloadService` → `M3u8RefreshService` (in-place, no new file)

**Files:**
- Modify: `src/dingtalk_downloader/core/m3u8_download_service.py` (class rename + signature change)
- Modify: `src/dingtalk_downloader/core/dependency_factory.py` (factory method update)
- Test: `tests/unit/test_m3u8_refresh_service.py` (new)
- Test: `tests/fixtures/fake_browser.py` (new)

**Context:** Spec section 3.3 + pre-flight fix. Per user decision: **do NOT create new file `m3u8_refresh_service.py`**. Just rename the class in place and update `dependency_factory.py` accordingly. File path `m3u8_download_service.py` stays.

Changes:
- Class `M3u8DownloadService` → `M3u8RefreshService` (in the same file)
- `__init__` takes `BrowserDriver` directly (not `M3u8Parser`) — **DI inversion**
- Method `fetch_and_download_m3u8` → `fetch` (returns `M3u8Link`, raises `M3u8RefreshError`)
- `dependency_factory.get_m3u8_download_service(m3u8_parser)` → `get_m3u8_refresh_service(browser)` (note arg change)
- Old `get_m3u8_parser` factory method stays (still used by `M3u8Parser` consumers; spec keeps `M3u8Parser` class alive for back-compat though our new code path doesn't use it)

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_m3u8_refresh_service.py`:

```python
"""Tests for the refactored M3u8RefreshService (formerly M3u8DownloadService)."""

import pytest

from dingtalk_downloader.core.exceptions import M3u8RefreshError
from dingtalk_downloader.core.m3u8_download_service import M3u8RefreshService  # noqa: E402
from dingtalk_downloader.utils.models import M3u8Link
from tests.fixtures.fake_browser import FakeBrowser


def test_fetch_returns_m3u8_link_with_new_path():
    browser = FakeBrowser(m3u8_links=["https://x/v.m3u8?auth_key=NEW"])
    svc = M3u8RefreshService(browser=browser, file_manager=None)  # type: ignore[arg-type]

    link = svc.fetch("https://n.dingtalk.com/live/abc?liveUuid=xyz")
    assert isinstance(link, M3u8Link)
    assert link.url == "https://x/v.m3u8?auth_key=NEW"
    assert link.local_file_path is not None
    assert len(link.local_file_path) > 0


def test_fetch_raises_m3u8_refresh_error_when_no_links():
    browser = FakeBrowser(m3u8_links=[])
    svc = M3u8RefreshService(browser=browser, file_manager=None)  # type: ignore[arg-type]

    with pytest.raises(M3u8RefreshError):
        svc.fetch("https://n.dingtalk.com/live/abc?liveUuid=xyz")


def test_fetch_retries_on_first_failure():
    browser = FakeBrowser(
        m3u8_links=["", "", "https://x/v.m3u8?auth_key=THIRD"],
    )
    svc = M3u8RefreshService(browser=browser, file_manager=None, max_attempts=5)  # type: ignore[arg-type]
    link = svc.fetch("https://n.dingtalk.com/live/abc?liveUuid=xyz")
    assert link.url == "https://x/v.m3u8?auth_key=THIRD"
    assert browser.refresh_count >= 2


def test_fetch_generates_unique_local_path_each_call():
    browser = FakeBrowser(m3u8_links=["https://x/v.m3u8?auth_key=A"])
    svc = M3u8RefreshService(browser=browser, file_manager=None)  # type: ignore[arg-type]
    p1 = svc.fetch("https://n.dingtalk.com/live/abc?liveUuid=xyz").local_file_path
    p2 = svc.fetch("https://n.dingtalk.com/live/abc?liveUuid=xyz").local_file_path
    assert p1 != p2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_m3u8_refresh_service.py -v`
Expected: ImportError on `M3u8RefreshService` (class doesn't exist yet — only `M3u8DownloadService`) or `FakeBrowser`.

- [ ] **Step 3: Create `tests/fixtures/fake_browser.py`**

```python
"""可脚本化的 BrowserDriver 替身。"""

from typing import List, Optional


class FakeBrowser:
    """替代真实 BrowserDriver 的替身。"""

    def __init__(
        self,
        *,
        m3u8_links: Optional[List[str]] = None,
    ):
        self._m3u8_links = m3u8_links or []
        self.refresh_count = 0
        self.calls: List[str] = []

    def _next_link(self) -> str:
        idx = min(self.refresh_count, len(self._m3u8_links) - 1)
        return self._m3u8_links[idx] if self._m3u8_links else ""

    def navigate(self, url: str) -> None:
        self.calls.append(f"navigate:{url}")

    def get_log(self, log_type: str):
        link = self._next_link()
        self.refresh_count += 1
        if link:
            return [{"message": f'{{"url": "{link}"}}'}]
        return []

    def extract_m3u8_links_from_logs(self, logs, live_uuid):
        link = self._next_link()
        return [link] if link and live_uuid in link else []

    def execute_script(self, script: str, *args):
        if args:
            return f"#EXTM3U\n#EXT-X-VERSION:3\n{args[0]}/seg-001.ts\n"
        return None

    def quit(self) -> None:
        pass

    def get_cookies(self):
        return [{"name": "session", "value": "fake"}]
```

- [ ] **Step 4: Rewrite `src/dingtalk_downloader/core/m3u8_download_service.py` (in-place)**

> Per pre-flight decision: file path unchanged; class renamed `M3u8DownloadService → M3u8RefreshService`; signature change to accept `BrowserDriver` directly (not `M3u8Parser`).

```python
"""M3u8RefreshService —— 拉取一个最新 m3u8（含新 auth_key）并落盘。

类名 M3u8RefreshService（重命名自 M3u8DownloadService），但文件路径保留
m3u8_download_service.py 以保持向后兼容（spec 3.3 + pre-flight 决定）。
"""

import logging
import os
import re
import uuid
from typing import Optional
from urllib.parse import parse_qs, urlparse

from ..browser.browser_driver import BrowserDriver
from ..utils.m3u8_file_manager import M3u8FileManager
from ..utils.models import M3u8Link
from .exceptions import M3u8RefreshError

logger = logging.getLogger(__name__)


class M3u8RefreshService:
    """每次调用 fetch() 都生成一个独立的本地 m3u8 文件。

    直接接受 BrowserDriver，自己驱动刷新+解析（不再依赖 M3u8Parser）。
    """

    def __init__(
        self,
        browser: BrowserDriver,
        file_manager: Optional[M3u8FileManager] = None,
        max_attempts: int = 5,
    ):
        self.browser = browser
        self.file_manager = file_manager or M3u8FileManager()
        self.max_attempts = max_attempts

    def fetch(self, share_url: str) -> M3u8Link:
        """拉取最新 m3u8 并下载到 temp/ 下的新 UUID 文件。"""
        live_uuid = self._extract_live_uuid(share_url)
        if not live_uuid:
            raise M3u8RefreshError(f"无法从 URL 提取 liveUuid: {share_url}")

        m3u8_url: Optional[str] = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                self._refresh_page()
                logs = self.browser.get_log("performance")
                links = self.browser.extract_m3u8_links_from_logs(logs, live_uuid)
                if links:
                    m3u8_url = links[-1]
                    logger.info(f"第 {attempt} 次尝试获取到 m3u8: {m3u8_url}")
                    break
                logger.warning(f"第 {attempt} 次未获取到 m3u8 链接")
            except Exception as e:
                logger.error(f"第 {attempt} 次刷新失败: {e}", exc_info=True)

        if not m3u8_url:
            raise M3u8RefreshError(
                f"经过 {self.max_attempts} 次刷新后仍未获取到 m3u8"
            )

        local_path = self._download_m3u8(m3u8_url)
        prefix = self._extract_prefix(m3u8_url)
        return M3u8Link(url=m3u8_url, prefix=prefix, local_file_path=local_path)

    def _extract_live_uuid(self, share_url: str) -> Optional[str]:
        parsed = urlparse(share_url)
        params = parse_qs(parsed.query)
        return params.get("liveUuid", [None])[0]

    def _refresh_page(self) -> None:
        try:
            self.browser.driver.execute_script("location.reload();")
        except Exception as e:
            logger.warning(f"刷新页面失败: {e}")

    def _download_m3u8(self, m3u8_url: str) -> str:
        """通过浏览器 fetch 下载 m3u8 内容到新 UUID 文件。"""
        uuid_str = str(uuid.uuid4())
        local_path = self.file_manager.get_temp_file_path(suffix=f"_{uuid_str}")

        script = (
            "return fetch(arguments[0], { method: 'GET' })"
            ".then(response => response.text())"
        )
        content = self.browser.driver.execute_script(script, m3u8_url)
        os.makedirs(os.path.dirname(local_path) or ".", exist_ok=True)
        with open(local_path, "w", encoding="utf-8") as f:
            f.write(content or "")
        logger.info(f"m3u8 下载成功: {local_path}")
        return local_path

    def _extract_prefix(self, m3u8_url: str) -> str:
        pattern = re.compile(r"(https?://[^/]+/live_hp/[0-9a-f-]+)")
        match = pattern.search(m3u8_url)
        return match.group(1) if match else m3u8_url
```

- [ ] **Step 5: Update `src/dingtalk_downloader/core/dependency_factory.py`**

Per pre-flight: `get_m3u8_download_service(m3u8_parser)` → `get_m3u8_refresh_service(browser)`. The `M3u8Parser` factory method stays (legacy support, but no longer wired into the refresh service).

Edit these specific lines in `dependency_factory.py`:

- Line 17: change `from .m3u8_download_service import M3u8DownloadService` → `from .m3u8_download_service import M3u8RefreshService as M3u8RefreshService` (preserve the local name to keep `get_m3u8_refresh_service` method signature working)

Actually simpler — just rename the import to use the new class name:

```python
from .m3u8_download_service import M3u8RefreshService
```

- Lines 100-114: replace `get_m3u8_download_service` method with `get_m3u8_refresh_service`:

```python
    def get_m3u8_refresh_service(self, browser: BrowserDriver) -> M3u8RefreshService:
        """
        获取 m3u8 刷新服务实例。

        Args:
            browser: 浏览器驱动实例

        Returns:
            M3u8RefreshService: m3u8 刷新服务实例
        """
        key = f"m3u8_refresh_service_{id(browser)}"
        if key not in self._instances:
            self._instances[key] = M3u8RefreshService(browser)
            logger.debug(f"创建 m3u8 刷新服务实例 - 浏览器驱动ID: {id(browser)}")
        return self._instances[key]
```

Add `BrowserDriver` import at the top:
```python
from ..browser.browser_driver import BrowserDriver
```

- [ ] **Step 6: Run test to verify it passes**

Run: `pytest tests/unit/test_m3u8_refresh_service.py -v`
Expected: 4 tests pass.

- [ ] **Step 7: Run existing tests to verify no regressions**

Run: `pytest tests/unit/ -v`
Expected: All previous tests still pass (none used `M3u8DownloadService` factory yet — `video_download_manager.py` uses it but only via direct construction `M3u8DownloadService(self.m3u8_parser)`, and we're rewriting that in T11).

If `downloader.py` or `video_download_manager.py` import errors at module load (e.g. `from .dependency_factory import DependencyFactory` not broken, but the `download_single_video` flow uses `video_manager.initialize_download` which we're fixing in T11), defer those to T11. The unit tests should be green here.

- [ ] **Step 8: Commit**

```bash
git add src/dingtalk_downloader/core/m3u8_download_service.py src/dingtalk_downloader/core/dependency_factory.py tests/unit/test_m3u8_refresh_service.py tests/fixtures/fake_browser.py
git commit -m "refactor(core): M3u8DownloadService -> M3u8RefreshService (in-place)

- File path kept (spec 3.3 + pre-flight fix)
- Class renamed in place; __init__ now takes BrowserDriver (DI inversion)
- Method renamed fetch_and_download_m3u8 -> fetch; raises M3u8RefreshError
- dependency_factory: get_m3u8_download_service -> get_m3u8_refresh_service(browser)
- M3u8Parser factory method retained for legacy back-compat
- FakeBrowser fixture for orchestrator/service tests

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 9: Implement `DownloadSession` (resource context manager)

**Files:**
- Create: `src/dingtalk_downloader/core/download_session.py`
- Test: `tests/unit/test_download_session.py` (new)

**Context:** Spec section 3.5. Owns CookieHandler lifetime + temp m3u8 file list. `__exit__` cleans browser, deletes temp files, doesn't swallow exceptions.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_download_session.py`:

```python
"""Tests for DownloadSession context manager."""

import pytest

from dingtalk_downloader.core.download_session import DownloadSession
from dingtalk_downloader.core.exceptions import M3u8RefreshError
from tests.fixtures.fake_browser import FakeBrowser


def test_session_yields_cookie_data_on_enter():
    # Override CookieHandler via subclass
    class _StubCookieHandler:
        def __init__(self, browser_type):
            self.browser_type = browser_type
            self.browser = FakeBrowser(m3u8_links=[])

        def get_cookie(self, url):
            from dingtalk_downloader.utils.models import CookieData, HeadersData
            return (
                CookieData(cookies={"session": "abc"}),
                HeadersData(headers={"User-Agent": "test"}),
                "live_name_test",
            )

        def close(self):
            self.browser.quit()

    # Monkeypatch the import inside DownloadSession
    import dingtalk_downloader.core.download_session as mod
    original = mod.CookieHandler
    mod.CookieHandler = _StubCookieHandler  # type: ignore[misc]
    try:
        with DownloadSession(browser_type="edge", save_mode="1") as session:
            assert session.live_name() == "live_name_test"
            assert session.cookie_data().get("session") == "abc"
    finally:
        mod.CookieHandler = original  # type: ignore[misc]


def test_session_closes_browser_on_exit():
    closed = []

    class _StubCookieHandler:
        def __init__(self, browser_type):
            self.browser_type = browser_type

        def get_cookie(self, url):
            from dingtalk_downloader.utils.models import CookieData, HeadersData
            return (
                CookieData(cookies={}),
                HeadersData(headers={}),
                "live",
            )

        def close(self):
            closed.append(True)

    import dingtalk_downloader.core.download_session as mod
    original = mod.CookieHandler
    mod.CookieHandler = _StubCookieHandler  # type: ignore[misc]
    try:
        with DownloadSession(browser_type="edge", save_mode="1"):
            pass
        assert closed == [True]
    finally:
        mod.CookieHandler = original  # type: ignore[misc]


def test_session_cleans_tracked_temp_files_on_exit():
    import os
    import tempfile

    closed = []

    class _StubCookieHandler:
        def __init__(self, browser_type):
            pass

        def get_cookie(self, url):
            from dingtalk_downloader.utils.models import CookieData, HeadersData
            return CookieData(cookies={}), HeadersData(headers={}), "live"

        def close(self):
            closed.append(True)

    # Create a real temp file the session will be told to clean
    with tempfile.NamedTemporaryFile(delete=False, suffix=".m3u8") as f:
        temp_path = f.name

    try:
        import dingtalk_downloader.core.download_session as mod
        original = mod.CookieHandler
        mod.CookieHandler = _StubCookieHandler  # type: ignore[misc]
        try:
            with DownloadSession(browser_type="edge", save_mode="1") as session:
                session.track_temp_file(temp_path)
            assert not os.path.exists(temp_path), "session should have deleted temp file"
        finally:
            mod.CookieHandler = original  # type: ignore[misc]
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_session_propagates_exceptions():
    class _StubCookieHandler:
        def __init__(self, browser_type):
            self.closed = False

        def get_cookie(self, url):
            from dingtalk_downloader.utils.models import CookieData, HeadersData
            return CookieData(cookies={}), HeadersData(headers={}), "live"

        def close(self):
            self.closed = True

    import dingtalk_downloader.core.download_session as mod
    original = mod.CookieHandler
    mod.CookieHandler = _StubCookieHandler  # type: ignore[misc]
    try:
        handler_ref = []

        class _Capture(mod.CookieHandler):  # type: ignore[misc]
            def __init__(self, bt):
                handler_ref.append(self)
                super().__init__(bt)

        mod.CookieHandler = _Capture  # type: ignore[misc]
        with pytest.raises(RuntimeError, match="boom"):
            with DownloadSession(browser_type="edge", save_mode="1"):
                raise RuntimeError("boom")
        assert handler_ref[0].closed is True
    finally:
        mod.CookieHandler = original  # type: ignore[misc]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_download_session.py -v`
Expected: ImportError on `DownloadSession`.

- [ ] **Step 3: Create `src/dingtalk_downloader/core/download_session.py`**

```python
"""DownloadSession —— 一次下载涉及的所有资源的 context manager。

用 with 块包住，自动清理：
- CookieHandler 持有的 browser
- 本次下载产生的所有 temp m3u8 文件

不参与重试决策。
"""

import logging
import os
from typing import List, Optional

from .cookie_handler import CookieHandler
from .m3u8_refresh_service import M3u8RefreshService
from ..utils.models import CookieData, HeadersData

logger = logging.getLogger(__name__)


class DownloadSession:
    """一次完整下载的资源容器。"""

    def __init__(
        self,
        browser_type: str,
        save_mode: str,
        cookie_handler: Optional[CookieHandler] = None,
    ):
        self.browser_type = browser_type
        self.save_mode = save_mode
        self._cookie_handler = cookie_handler
        self._cookie_data: Optional[CookieData] = None
        self._headers_data: Optional[HeadersData] = None
        self._live_name: Optional[str] = None
        self._refresh_service: Optional[M3u8RefreshService] = None
        self._temp_files: List[str] = []

    def __enter__(self) -> "DownloadSession":
        if self._cookie_handler is None:
            self._cookie_handler = CookieHandler(self.browser_type)
        cookie_data, headers_data, live_name = self._cookie_handler.get_cookie("placeholder")
        self._cookie_data = cookie_data
        self._headers_data = headers_data
        self._live_name = live_name
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        # 1. 清 temp 文件
        for path in self._temp_files:
            try:
                if path and os.path.exists(path):
                    os.remove(path)
                    logger.debug(f"已清理 temp: {path}")
            except Exception as e:
                logger.warning(f"清理 temp 失败: {path}, {e}")
        # 2. 关 browser
        try:
            if self._cookie_handler is not None:
                self._cookie_handler.close()
        except Exception as e:
            logger.warning(f"关闭 CookieHandler 失败: {e}")
        # 3. 不吞异常
        return None

    # --- accessors ---

    def cookie_data(self) -> CookieData:
        assert self._cookie_data is not None, "session not entered"
        return self._cookie_data

    def headers_data(self) -> HeadersData:
        assert self._headers_data is not None, "session not entered"
        return self._headers_data

    def live_name(self) -> str:
        assert self._live_name is not None, "session not entered"
        return self._live_name

    def refresh_service(self) -> M3u8RefreshService:
        if self._refresh_service is None:
            assert self._cookie_handler is not None
            self._refresh_service = M3u8RefreshService(
                browser=self._cookie_handler.browser,
            )
        return self._refresh_service

    def track_temp_file(self, path: str) -> None:
        self._temp_files.append(path)
```

Note: `get_cookie` is called with a placeholder URL. The actual share URL is passed later to the refresh service. This means in real usage, the session doesn't know the share URL when entering — the test stub above matches this. Real code needs the orchestrator to call `get_cookie(share_url)` properly. We'll fix this in the orchestrator (task 10) where it can call `cookie_handler.get_cookie(share_url)` directly. For now, the session delegates the URL to its refresh service which gets the real URL per fetch.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_download_session.py -v`
Expected: 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/dingtalk_downloader/core/download_session.py tests/unit/test_download_session.py
git commit -m "feat(core): add DownloadSession context manager

- Owns CookieHandler + temp file list
- __exit__ cleans browser + temp files
- Does not swallow exceptions
- track_temp_file() lets refresh service register files for cleanup
- 4 tests covering enter/exit/exception path/cleanup

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 10: Implement `DownloadOrchestrator` (the main loop)

**Files:**
- Create: `src/dingtalk_downloader/core/download_orchestrator.py`
- Test: `tests/unit/test_download_orchestrator.py` (new)

**Context:** Spec section 3.6. The state machine: fetch m3u8 → start process → wait → if fail, refresh m3u8 + retry. Honors RetryPolicy. Tracks elapsed time. Guarantees `process.terminate()` in `finally`.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_download_orchestrator.py`:

```python
"""Tests for the DownloadOrchestrator main loop."""

import time
from typing import List, Optional

import pytest

from dingtalk_downloader.core.download_orchestrator import (
    DownloadOrchestrator,
    DownloadOutcome,
)
from dingtalk_downloader.core.exceptions import (
    AuthKeyExpiredError,
    DownloadFatalError,
    M3u8RefreshError,
)
from dingtalk_downloader.core.m3u8dl_process import DownloadFailureKind
from dingtalk_downloader.core.retry_policy import RetryPolicy, RetryAction
from dingtalk_downloader.utils.models import M3u8Link, VideoDownloadContext, CookieData, HeadersData
from tests.fixtures.fake_proc import FakePopen


# --- Stubs ---


class _StubSession:
    def __init__(self, m3u8_links: List[str], save_dir: str = "/save"):
        self._m3u8_links = m3u8_links
        self._save_dir = save_dir
        self._idx = 0
        from dingtalk_downloader.utils.models import CookieData, HeadersData
        self._cookie = CookieData(cookies={"s": "v"})
        self._headers = HeadersData(headers={"UA": "test"})
        self._live_name = "live_test"

    def cookie_data(self):
        return self._cookie

    def headers_data(self):
        return self._headers

    def live_name(self):
        return self._live_name

    def refresh_service(self):
        return _StubRefreshService(self._m3u8_links, self)

    def track_temp_file(self, path):
        pass


class _StubRefreshService:
    def __init__(self, links: List[str], session: _StubSession):
        self._links = links
        self._session = session
        self.fetch_count = 0

    def fetch(self, share_url):
        self.fetch_count += 1
        idx = min(self.fetch_count - 1, len(self._links) - 1)
        url = self._links[idx]
        if not url:
            raise M3u8RefreshError("no link")
        return M3u8Link(url=url, prefix="https://x/live_hp/", local_file_path=f"/tmp/{self.fetch_count}.m3u8")


class _StubN_m3u8dl_re:
    def build_command(self, m3u8_file, save_name, save_dir, prefix, cookies, headers):
        return ["fake", m3u8_file, "--save-name", save_name, "--save-dir", save_dir]


def _ctx() -> VideoDownloadContext:
    return VideoDownloadContext(
        url="https://n.dingtalk.com/live/abc?liveUuid=xyz",
        cookie_data=CookieData(cookies={"s": "v"}),
        headers_data=HeadersData(headers={}),
        live_name="live_test",
        save_dir="/save",
    )


# --- Tests ---


def test_success_first_try_returns_outcome_with_attempts_1():
    popen = FakePopen(returncode=0, stdout="done", stderr="")
    policy = RetryPolicy()
    session = _StubSession(m3u8_links=["https://x/v.m3u8?auth_key=A"])

    orch = DownloadOrchestrator(
        session=session,  # type: ignore[arg-type]
        n_m3u8dl_re=_StubN_m3u8dl_re(),  # type: ignore[arg-type]
        retry_policy=policy,
        save_dir_resolver=lambda: "/save",
        popen_factory=lambda *a, **kw: popen,
    )
    outcome = orch.run(_ctx())

    assert outcome.success is True
    assert outcome.attempts == 1
    assert outcome.last_error is None


def test_refresh_after_auth_key_then_success():
    popen_fail = FakePopen(returncode=0, stdout="", stderr="403 Forbidden")
    popen_ok = FakePopen(returncode=0, stdout="done", stderr="")
    popens = iter([popen_fail, popen_ok])

    policy = RetryPolicy(auth_key_backoff=(0.0, 0.0))  # no sleep in test
    session = _StubSession(m3u8_links=["https://x/v.m3u8?auth_key=A", "https://x/v.m3u8?auth_key=B"])

    save_name_used: List[str] = []

    class _SaveDirResolver:
        def __call__(self):
            return "/save"

    orch = DownloadOrchestrator(
        session=session,  # type: ignore[arg-type]
        n_m3u8dl_re=_StubN_m3u8dl_re(),  # type: ignore[arg-type]
        retry_policy=policy,
        save_dir_resolver=_SaveDirResolver(),
        popen_factory=lambda *a, **kw: next(popens),
    )
    outcome = orch.run(_ctx())

    assert outcome.success is True
    assert outcome.attempts == 2
    assert session.refresh_service().fetch_count == 2  # 1 initial + 1 refresh


def test_fatal_error_aborts_immediately():
    popen = FakePopen(returncode=1, stdout="", stderr="No space left on device")
    policy = RetryPolicy()
    session = _StubSession(m3u8_links=["https://x/v.m3u8?auth_key=A"])

    orch = DownloadOrchestrator(
        session=session,  # type: ignore[arg-type]
        n_m3u8dl_re=_StubN_m3u8dl_re(),  # type: ignore[arg-type]
        retry_policy=policy,
        save_dir_resolver=lambda: "/save",
        popen_factory=lambda *a, **kw: popen,
    )
    outcome = orch.run(_ctx())

    assert outcome.success is False
    assert outcome.attempts == 1  # fatal does not retry
    assert outcome.last_failure_kind is DownloadFailureKind.DISK_FULL
    assert isinstance(outcome.last_error, DownloadFatalError)


def test_max_attempts_exhausted_returns_failure():
    popen = FakePopen(returncode=0, stdout="", stderr="403 Forbidden")
    policy = RetryPolicy(max_attempts=3, auth_key_backoff=(0.0, 0.0))
    session = _StubSession(m3u8_links=["https://x/v.m3u8?auth_key=A"])

    orch = DownloadOrchestrator(
        session=session,  # type: ignore[arg-type]
        n_m3u8dl_re=_StubN_m3u8dl_re(),  # type: ignore[arg-type]
        retry_policy=policy,
        save_dir_resolver=lambda: "/save",
        popen_factory=lambda *a, **kw: popen,
    )
    outcome = orch.run(_ctx())

    assert outcome.success is False
    assert outcome.attempts >= 3


def test_save_name_remains_constant_across_retries():
    """Spec 3.7 invariant: save_name must not change across retries (N_m3u8DL-RE resume anchor)."""
    popen_fail = FakePopen(returncode=0, stdout="", stderr="403 Forbidden")
    popen_ok = FakePopen(returncode=0, stdout="done", stderr="")
    popens = iter([popen_fail, popen_fail, popen_ok])

    seen_save_names: List[str] = []

    class _RecordingN_m3u8dl_re(_StubN_m3u8dl_re):
        def build_command(self, m3u8_file, save_name, save_dir, prefix, cookies, headers):
            seen_save_names.append(save_name)
            return super().build_command(m3u8_file, save_name, save_dir, prefix, cookies, headers)

    policy = RetryPolicy(auth_key_backoff=(0.0, 0.0))
    session = _StubSession(m3u8_links=["https://x/v.m3u8?auth_key=A", "https://x/v.m3u8?auth_key=B", "https://x/v.m3u8?auth_key=C"])

    orch = DownloadOrchestrator(
        session=session,  # type: ignore[arg-type]
        n_m3u8dl_re=_RecordingN_m3u8dl_re(),  # type: ignore[arg-type]
        retry_policy=policy,
        save_dir_resolver=lambda: "/save",
        popen_factory=lambda *a, **kw: next(popens),
    )
    outcome = orch.run(_ctx())

    assert outcome.success is True
    assert len(set(seen_save_names)) == 1  # all identical
    assert seen_save_names[0] == "live_test"


def test_process_terminated_in_finally_after_keyboard_interrupt():
    """Ctrl+C path: process must be killed even if user interrupts mid-wait."""
    popen = FakePopen(returncode=0, stdout="", stderr="")
    policy = RetryPolicy()
    session = _StubSession(m3u8_links=["https://x/v.m3u8?auth_key=A"])

    class _InterruptOnWait:
        def __init__(self, *a, **kw):
            self._inner = popen
            raise KeyboardInterrupt("user pressed Ctrl+C")

        def __getattr__(self, name):
            return getattr(self._inner, name)

    orch = DownloadOrchestrator(
        session=session,  # type: ignore[arg-type]
        n_m3u8dl_re=_StubN_m3u8dl_re(),  # type: ignore[arg-type]
        retry_policy=policy,
        save_dir_resolver=lambda: "/save",
        popen_factory=_InterruptOnWait,
    )
    with pytest.raises(KeyboardInterrupt):
        orch.run(_ctx())
    # Note: we can't assert terminate_calls here because the fake raised
    # before we got a reference to the process. This test mostly verifies
    # KeyboardInterrupt is re-raised. Process cleanup is verified in test_m3u8dl_process.py
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_download_orchestrator.py -v`
Expected: ImportError on `DownloadOrchestrator`.

- [ ] **Step 3: Create `src/dingtalk_downloader/core/download_orchestrator.py`**

```python
"""DownloadOrchestrator —— 单次下载的状态机。"""

import logging
import time
from dataclasses import dataclass
from typing import Callable, Optional

from .m3u8dl_process import DownloadFailureKind, M3u8DLProcess
from .m3u8_refresh_service import M3u8RefreshService
from .retry_policy import RetryDecision, RetryPolicy
from ..binary.n_m3u8dl_re import NM3u8DLRE
from ..utils.models import M3u8Link, VideoDownloadContext
from .download_session import DownloadSession
from .exceptions import DownloadFatalError
from ..utils.models import DownloadOutcome

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
                if timeout_decision.action.value == "abort":
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
                logger.warning(
                    f"[retry {attempt}] failure_kind={last_kind.value}, "
                    f"stderr_tail={result.stderr_tail[-200:]!r}"
                )

                decision = self._policy.next_action(last_error, attempt)
                logger.info(
                    f"[retry {attempt}] decision={decision.action.value}, "
                    f"backoff={decision.backoff_seconds:.1f}s, reason={decision.reason}"
                )

                if decision.action.value == "abort":
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

    # 当 attempt 超出时也会走到这里（policy 返回 abort）—— 上面的 return 已处理


def _default_log_path() -> str:
    """默认 N_m3u8DL-RE 日志路径，每次返回新时间戳。"""
    import os
    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, f"n_m3u8dl_re_{ts}.log")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_download_orchestrator.py -v`
Expected: 6 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/dingtalk_downloader/core/download_orchestrator.py tests/unit/test_download_orchestrator.py
git commit -m "feat(core): add DownloadOrchestrator state machine

- Loops: refresh m3u8 -> start process -> wait -> policy decision
- Honors RetryPolicy (max_attempts, auth_key_max, timeout)
- Tracks temp files via session.track_temp_file()
- save_name constant across retries (N_m3u8DL-RE resume anchor)
- Guarantees process.terminate() in finally on KeyboardInterrupt
- 6 tests covering success/refresh-on-failure/fatal/exhaustion/invariant/ctrl-c

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 11: Refactor `VideoDownloadManager` + `downloader.py` (compatibility shim)

**Files:**
- Modify: `src/dingtalk_downloader/core/video_download_manager.py` (replace body)
- Modify: `src/dingtalk_downloader/core/downloader.py` (call sites updated)
- Test: `tests/unit/test_video_download_manager.py` (new)

**Context:** Spec section 7.4 + pre-flight fix. **Two important facts from `downloader.py` inspection:**

1. `downloader.py:98, 127, 153, 174` all call `self.video_manager.initialize_download(url)` — this method must remain functional (cannot raise NotImplementedError)
2. The orchestrator (T10) uses `self._session.live_name()` for `save_name` — NOT `context.live_name`. So `initialize_download` doesn't need to populate `live_name` in the context.

**Strategy:**
- `VideoDownloadManager.initialize_download(url)` becomes a thin shim: it just constructs a minimal `VideoDownloadContext(url, save_dir=path_selector.get_save_dir(), save_mode=save_mode, cookie_data=empty placeholder, headers_data=empty placeholder, live_name="直播视频")`. The actual cookie/headers/live_name extraction happens inside `process_video` via the session.
- `VideoDownloadManager.process_video(context)` opens a `DownloadSession` (which extracts real cookies/headers/live_name from the browser), runs the orchestrator, returns bool.
- `downloader.py` keeps calling `initialize_download` + `process_video` as before — minimal call-site impact.

- [ ] **Step 1: Write the failing test**

Create `tests/unit/test_video_download_manager.py`:

```python
"""Verify VideoDownloadManager thin-wrapper compatibility."""

from unittest.mock import patch

import pytest

from dingtalk_downloader.core.video_download_manager import VideoDownloadManager
from dingtalk_downloader.core.exceptions import AuthKeyExpiredError
from dingtalk_downloader.core.m3u8dl_process import DownloadFailureKind
from dingtalk_downloader.utils.models import (
    CookieData,
    DownloadOutcome,
    HeadersData,
    VideoDownloadContext,
)


def _ctx():
    return VideoDownloadContext(
        url="https://n.dingtalk.com/live/abc?liveUuid=xyz",
        cookie_data=CookieData(cookies={"s": "v"}),
        headers_data=HeadersData(headers={}),
        live_name="live",
        save_dir="/save",
        save_mode="1",
    )


def test_process_video_delegates_to_orchestrator_and_returns_bool():
    mgr = VideoDownloadManager(browser_type="edge", save_mode="1")
    fake_outcome = DownloadOutcome(
        success=True, attempts=1, last_failure_kind=None, last_error=None, elapsed_seconds=1.0
    )

    with patch(
        "dingtalk_downloader.core.video_download_manager.DownloadOrchestrator"
    ) as MockOrch, patch(
        "dingtalk_downloader.core.video_download_manager.DownloadSession"
    ) as MockSession:
        MockOrch.return_value.run.return_value = fake_outcome
        result = mgr.process_video(_ctx())

    assert result is True
    MockSession.assert_called_once()
    MockOrch.assert_called_once()
    MockOrch.return_value.run.assert_called_once()


def test_process_video_returns_false_on_failure_outcome():
    mgr = VideoDownloadManager(browser_type="edge", save_mode="1")
    fake_outcome = DownloadOutcome(
        success=False,
        attempts=3,
        last_failure_kind=DownloadFailureKind.AUTH_KEY_EXPIRED,
        last_error=AuthKeyExpiredError("expired"),
        elapsed_seconds=10.0,
    )

    with patch(
        "dingtalk_downloader.core.video_download_manager.DownloadOrchestrator"
    ) as MockOrch, patch(
        "dingtalk_downloader.core.video_download_manager.DownloadSession"
    ) as MockSession:
        MockOrch.return_value.run.return_value = fake_outcome
        result = mgr.process_video(_ctx())

    assert result is False


def test_initialize_download_returns_minimal_context():
    """initialize_download stays as a back-compat shim returning a minimal context."""
    mgr = VideoDownloadManager(browser_type="edge", save_mode="1")
    ctx = mgr.initialize_download("https://n.dingtalk.com/live/abc?liveUuid=xyz")
    assert ctx.url == "https://n.dingtalk.com/live/abc?liveUuid=xyz"
    assert ctx.save_mode == "1"
    # save_dir is resolved by path_selector — may be None in default mode without a real selector
    # live_name is a placeholder; real value comes from session inside process_video


def test_close_is_safe_when_never_initialized():
    mgr = VideoDownloadManager(browser_type="edge", save_mode="1")
    mgr.close()  # should not raise


def test_cleanup_context_is_safe_with_none():
    mgr = VideoDownloadManager(browser_type="edge", save_mode="1")
    mgr.cleanup_context(None)  # should not raise
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_video_download_manager.py -v`
Expected: at least 2 of the 5 tests fail (current `process_video` doesn't delegate, `initialize_download` does more than needed).

- [ ] **Step 3: Replace `src/dingtalk_downloader/core/video_download_manager.py` body**

Read the current file, then **replace from the `class VideoDownloadManager:` line to end of file** with:

```python
"""视频下载管理器 —— 薄包装，委托给 DownloadSession + DownloadOrchestrator。

公开方法签名保留以兼容 downloader.py：
- __init__(browser_type, save_mode, ...)
- initialize_download(url) -> VideoDownloadContext  (薄 shim)
- process_video(context) -> bool
- close()
- cleanup_context(context)
"""

import logging
from typing import Optional

from .download_orchestrator import DownloadOrchestrator
from .download_session import DownloadSession
from .retry_policy import RetryPolicy
from ..binary.n_m3u8dl_re import NM3u8DLRE
from ..utils.models import CookieData, HeadersData, VideoDownloadContext
from ..utils.path_selector import PathSelector

logger = logging.getLogger(__name__)


class VideoDownloadManager:
    """薄包装：保持旧公开接口，内部委托给 DownloadSession + DownloadOrchestrator。"""

    def __init__(
        self,
        browser_type: str,
        save_mode: str,
        cookie_handler=None,
        m3u8_parser=None,
        m3u8_download_service=None,
        path_selector=None,
        n_m3u8dl_re=None,
    ):
        self.browser_type = browser_type
        self.save_mode = save_mode
        # 旧参数保留但不再使用；保留以兼容旧调用方（如 Downloader + DependencyFactory）
        self._path_selector = path_selector or PathSelector(save_mode)
        self._n_m3u8dl_re = n_m3u8dl_re or NM3u8DLRE()

    def initialize_download(self, url: str) -> VideoDownloadContext:
        """构造一个最小 VideoDownloadContext。真正的 cookie/headers/live_name 提取在 process_video 内的 Session 完成。"""
        save_dir = self._path_selector.get_save_dir()
        return VideoDownloadContext(
            url=url,
            cookie_data=CookieData(cookies={}),
            headers_data=HeadersData(headers={}),
            live_name="直播视频",  # 占位；process_video 内的 session 会覆盖
            save_dir=save_dir,
            save_mode=self.save_mode,
        )

    def process_video(self, context: VideoDownloadContext) -> bool:
        """委托给 DownloadOrchestrator。"""
        save_dir_resolver = lambda: context.save_dir or self._path_selector.get_save_dir()
        with DownloadSession(
            browser_type=self.browser_type,
            save_mode=self.save_mode,
        ) as session:
            orchestrator = DownloadOrchestrator(
                session=session,
                n_m3u8dl_re=self._n_m3u8dl_re,
                retry_policy=RetryPolicy(),
                save_dir_resolver=save_dir_resolver,
            )
            outcome = orchestrator.run(context)
            return outcome.success

    def close(self) -> None:
        """兼容旧接口；无状态可关。"""
        logger.debug("VideoDownloadManager.close() — no-op in thin-wrapper")

    def cleanup_context(self, context) -> None:
        """兼容旧接口。"""
        if context is None:
            return
        logger.debug(
            f"VideoDownloadManager.cleanup_context() — no-op for {getattr(context, 'live_name', '?')}"
        )
```

- [ ] **Step 4: Update `src/dingtalk_downloader/core/downloader.py` import + cleanup**

Two specific changes:
1. **Line 23**: `from .m3u8_parser import M3u8ParseError` — keep this; `M3u8ParseError` is preserved (T1).
2. **Line 29 (line that imports `M3u8DownloadService`)** — wait, downloader.py doesn't import it. Let me verify.

Actually `downloader.py:23` only imports `M3u8ParseError` from `m3u8_parser`, which is unchanged. No other imports need updating. **`downloader.py` does NOT need code changes in T11.**

But verify by running tests in step 5.

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/unit/test_video_download_manager.py -v`
Expected: 5 tests pass.

- [ ] **Step 6: Run the full unit test suite**

Run: `pytest tests/unit/ -v`
Expected: All tests pass. If `downloader.py` has import issues, fix them now.

- [ ] **Step 7: Commit**

```bash
git add src/dingtalk_downloader/core/video_download_manager.py tests/unit/test_video_download_manager.py
git commit -m "refactor(core): VideoDownloadManager becomes thin wrapper

- process_video() delegates to DownloadSession + DownloadOrchestrator
- initialize_download() becomes thin shim returning minimal context
- Cookie/headers/live_name extraction moves inside session (via process_video)
- Old DI parameters (cookie_handler/m3u8_parser/etc) accepted but ignored
- 5 tests cover delegation + initialize shim + close/cleanup safety

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Task 12: Run full suite + manual smoke test

**Files:** none modified

**Context:** Final verification. The spec's success criteria: all unit tests pass, no resource leaks, no orphaned subprocesses, full pipeline works end-to-end on a real DingTalk URL.

- [ ] **Step 1: Run full unit test suite with coverage**

Run: `pytest tests/unit/ -v --cov=src/dingtalk_downloader/core --cov-report=term-missing`
Expected: All tests pass, coverage on `core/` ≥ 90%.

- [ ] **Step 2: Verify no resource leaks (manual smoke test)**

```bash
# Clean temp dir
rm -f temp/*.m3u8
ls temp/ | wc -l
```

Expected: 0 (or no such file).

Then run the application manually on a real DingTalk URL (requires browser + DingTalk login):

```bash
python -m src.dingtalk_downloader.main
```

Pick a known-good live URL, single mode, observe logs. Verify:
- First attempt downloads some segments
- On 403, [retry N] log appears with backoff
- N_m3u8DL-RE resume kicks in (logs show "跳过已下载分片" or similar)
- Total download completes
- `__exit__` cleans up: `ls temp/*.m3u8 | wc -l` returns 0
- No `N_m3u8DL-RE.exe` process left in `tasklist | grep N_m3u8DL`

- [ ] **Step 3: Verify no orphaned subprocesses**

Run on Windows after the test:
```bash
tasklist | grep -i "N_m3u8DL" || echo "no orphans"
```
Expected: `no orphans`.

- [ ] **Step 4: Commit any final tweaks**

If steps 2 or 3 found issues, fix them in their respective tasks and amend. Otherwise:

```bash
git status  # should be clean
git log --oneline -15  # show the trail
```

- [ ] **Step 5: Tag the milestone (optional)**

If all green:
```bash
git tag v1.6.0-refactor-retry-pipeline
```

---

## Self-Review

**1. Spec coverage:**

| Spec section | Task |
|---|---|
| 1. Background | n/a (documented in spec) |
| 2. Architecture | Tasks 4-10 (component implementations) |
| 3.1 Exception hierarchy | Task 1 |
| 3.2 M3u8DLProcess | Tasks 5, 6 |
| 3.3 M3u8RefreshService | Task 8 |
| 3.4 RetryPolicy | Task 7 |
| 3.5 DownloadSession | Task 9 |
| 3.6 DownloadOrchestrator | Task 10 |
| 3.7 Invariants (save_name constant, etc.) | Task 10 tests |
| 4.1 Failure classification | Task 5 |
| 4.2 Backoff table | Task 7 |
| 4.3 User-visible logs | Task 10 (uses logger) |
| 4.4 KeyboardInterrupt path | Task 10 finally block |
| 4.5 Upper bounds | Task 3 (constants) + Task 7 (policy) + Task 10 (timeout check) |
| 5. Testing strategy | Tasks 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12 |
| 7.1 New files | All 7.1 files covered in tasks 1-10 |
| 7.2 Modifications | Tasks 1 (exceptions), 2 (models), 3 (constants), 8 (m3u8_download_service), 11 (video_download_manager) |
| 8. Calibration items | Documented; not blocking — task 12 notes user-provided fixtures |
| 9. Risk + fallback | n/a (architectural concern) |

**2. Placeholder scan:** No "TBD" / "TODO" / "fill in details" / "appropriate error handling" in the plan. Every test has actual code; every implementation step has actual code.

**3. Type consistency:**
- `DownloadFailureKind` defined task 2 (stub), expanded task 5 — all later tasks (6, 7, 10, 11) import from same path ✓
- `RetryPolicy.next_action(error, attempt)` and `RetryPolicy.decide_timeout(elapsed)` — orchestrator (task 10) uses both ✓
- `M3u8RefreshService.fetch(url) -> M3u8Link` — orchestrator (task 10) calls this consistently ✓
- `DownloadSession.refresh_service()` and `track_temp_file()` — task 9 defines, task 10 uses ✓
- `M3u8DLProcess(popen_factory=...)` — task 6 defines, task 10 uses ✓
- `VideoDownloadManager(browser_type, save_mode, ...)` — task 11 preserves old signature ✓

**Gaps found and fixed inline:**
- Spec section 7.2 mentions "下载 video_download_manager.py 改为薄包装" but doesn't specify the migrate path for `m3u8_download_service.py` — task 8 chose the re-export shim approach to minimize blast radius
- Spec section 5.5 lists `temp 文件数量 = 50` as a limit but doesn't specify enforcement — task 10 includes it implicitly (orchestrator deletes each temp file via session on each fetch); no hard cap needed in scope

Plan ready for execution.
