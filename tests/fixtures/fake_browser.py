"""可脚本化的 BrowserDriver 替身。"""

from typing import List, Optional


class FakeBrowser:
    """替代真实 BrowserDriver 的替身。

    Notes:
    - 真实 `BrowserDriver.extract_m3u8_links_from_logs` 默认实现会过滤
      `live_uuid in url` 的链接，但本测试夹具里的链接故意不含 live_uuid。
      因此夹具版本**直接返回所有链接**（绕过 live_uuid 过滤），让上层
      服务/调用者专注于重试/落盘逻辑。
    - `.driver` 属性模拟 selenium WebDriver，主要供 `execute_script` 调用。
    """

    def __init__(
        self,
        *,
        m3u8_links: Optional[List[str]] = None,
    ):
        self._m3u8_links = m3u8_links or []
        self.refresh_count = 0
        self.calls: List[str] = []
        self.driver = _FakeWebDriver(self)

    def _next_link(self) -> str:
        if not self._m3u8_links:
            return ""
        idx = min(self.refresh_count, len(self._m3u8_links) - 1)
        return self._m3u8_links[idx]

    def navigate(self, url: str) -> None:
        self.calls.append(f"navigate:{url}")

    def get_log(self, log_type: str):
        link = self._next_link()
        self.refresh_count += 1
        if link:
            return [{"message": f'{{"url": "{link}"}}'}]
        return []

    def extract_m3u8_links_from_logs(self, logs, live_uuid):
        # 测试夹具：忽略 live_uuid 过滤，始终返回当前链接（如果有）。
        link = self._next_link()
        return [link] if link else []

    def execute_script(self, script: str, *args):
        if args:
            return f"#EXTM3U\n#EXT-X-VERSION:3\n{args[0]}/seg-001.ts\n"
        return None

    def quit(self) -> None:
        pass

    def get_cookies(self):
        return [{"name": "session", "value": "fake"}]


class _FakeWebDriver:
    """最小 selenium WebDriver 替身 —— 仅支持 execute_script。"""

    def __init__(self, browser: FakeBrowser):
        self._browser = browser

    def execute_script(self, script: str, *args):
        return self._browser.execute_script(script, *args)