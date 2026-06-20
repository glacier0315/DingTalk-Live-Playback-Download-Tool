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
