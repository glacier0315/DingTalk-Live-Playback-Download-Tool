"""Shared fixtures for integration tests.

集成测试默认 SKIP，需要 N_m3u8DL-RE.exe 存在才能跑。
通过 `uv run pytest -m integration` 启用。

注意：嵌入的 ffmpeg.exe 极精简（无 h264/aac 编码器），本套件使用手工构造的
m3u8 文本 + 占位 .ts 文件——N_m3u8DL-RE 会真实运行、写日志、最终失败（因为
.ts 不可达）。这足以测试集成路径：命令拼接 + 子进程调用 + 日志生成 + 退出码
捕获。
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest
import yaml

# 把 src/ 加入 import path
_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC = _REPO_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))


def _n_m3u8dl_re() -> Path:
    return _REPO_ROOT / "assets" / "bin" / "N_m3u8DL-RE.exe"


def _ffmpeg() -> Path:
    return _REPO_ROOT / "assets" / "bin" / "ffmpeg.exe"


# ---------------------------------------------------------------------------
# 自动 skip：bin 缺失时跳过 integration 测试
# ---------------------------------------------------------------------------


def pytest_collection_modifyitems(config, items):
    """bin 缺失时给所有 integration 测试加 skip。"""
    needs_bins = not _n_m3u8dl_re().exists()
    if needs_bins:
        skip_marker = pytest.mark.skip(
            reason=f"需要 {_n_m3u8dl_re().name} (assets/bin/)"
        )
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_marker)


# ---------------------------------------------------------------------------
# Session-scope fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def n_m3u8dl_re_path() -> str:
    """真实 N_m3u8DL-RE.exe 路径。"""
    path = _n_m3u8dl_re()
    if not path.exists():
        pytest.skip(f"N_m3u8DL-RE.exe not found: {path}")
    return str(path)


@pytest.fixture(scope="session")
def ffmpeg_path() -> str:
    """真实 ffmpeg.exe 路径（用于 sanity 测试，不用于生成 m3u8）。"""
    path = _ffmpeg()
    if not path.exists():
        pytest.skip(f"ffmpeg.exe not found: {path}")
    return str(path)


# ---------------------------------------------------------------------------
# Function-scope fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_config_yaml(tmp_path):
    """为集成测试生成符合 CONFIG_SCHEMA 的最小 yaml。

    Returns:
        (cfg_path, headers_dict)
    """
    cfg = tmp_path / "app.yaml"
    headers = {
        "user_agent": "IntegrationTest/1.0",
        "referer": "https://n.dingtalk.com/",
        "accept": "*/*",
        "accept_language": "zh-CN",
        "accept_encoding": "identity",
        "connection": "keep-alive",
        "sec_fetch_dest": "video",
        "sec_fetch_mode": "cors",
        "sec_fetch_site": "same-origin",
        "sec_fetch_user": "?1",
        "upgrade_insecure_requests": "1",
    }
    exe_path = (
        str(_n_m3u8dl_re()) if _n_m3u8dl_re().exists()
        else "assets/bin/N_m3u8DL-RE.exe"
    )
    ff_path = (
        str(_ffmpeg()) if _ffmpeg().exists()
        else "assets/bin/ffmpeg.exe"
    )
    content = {
        "app": {"name": "IntegrationTest", "version": "1.0.0", "build_date": "2026-06-20"},
        "download": {
            "default_dir": str(tmp_path / "Downloads"),
            "temp_dir": str(tmp_path / "tmp"),
            "max_retry_count": 3,
        },
        "browser": {"default_type": "edge", "headless": True, "timeout": 30},
        "logging": {
            "level": "INFO",
            "dir": str(tmp_path / "logs"),
            "max_bytes": 10485760,
            "backup_count": 3,
            "retention_days": 7,
        },
        "headers": headers,
        "n_m3u8dl_re": {
            "executable_path": exe_path,
            "ui_language": "zh-CN",
            "temp_dir": str(tmp_path / "nm_tmp"),
            "log_dir": str(tmp_path / "nm_logs"),
        },
        "ffmpeg": {
            "executable_path": ff_path,
        },
    }
    cfg.write_text(yaml.safe_dump(content, allow_unicode=True), encoding="utf-8")
    return cfg, headers


def _write_static_m3u8(out_dir: Path, num_segments: int = 1) -> Path:
    """手工写一个最小有效的 m3u8 文本（不依赖 ffmpeg 编码）。

    输出的 m3u8 引用 fake-host 的 .ts（不可达），N_m3u8DL-RE 真实运行时会：
    - 解析 m3u8 成功
    - 尝试下载 .ts 失败
    - 写日志
    - 返回非 0 退出码
    这种"真实运行 + 预期失败"是集成测试希望覆盖的路径。
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    m3u8 = out_dir / "video.m3u8"
    lines = [
        "#EXTM3U",
        "#EXT-X-VERSION:3",
        "#EXT-X-TARGETDURATION:2",
        "#EXT-X-MEDIA-SEQUENCE:0",
    ]
    for i in range(1, num_segments + 1):
        lines.append("#EXTINF:1.0,")
        lines.append(f"seg-{i:03d}.ts")
    lines.append("#EXT-X-ENDLIST")
    m3u8.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return m3u8


@pytest.fixture
def local_m3u8_factory(tmp_path):
    """返回一个工厂：调用时在指定目录生成静态 m3u8 + 失败占位 .ts。

    Usage:
        m3u8_path = local_m3u8_factory()  # 单 segment
        m3u8_path = local_m3u8_factory(num_segments=3)  # 3 segments
    """
    produced: list[Path] = []

    def _make(num_segments: int = 1, dir_: Path | None = None) -> Path:
        out_dir = Path(dir_) if dir_ else tmp_path / f"m3u8_{len(produced)}"
        m3u8 = _write_static_m3u8(out_dir, num_segments)
        # 占位 .ts 文件（不可被 N_m3u8DL-RE 解析为真实视频）——用于让 m3u8
        # 引用关系成立；N_m3u8DL-RE 试图下载时会失败但不会崩。
        for i in range(1, num_segments + 1):
            (out_dir / f"seg-{i:03d}.ts").write_bytes(b"\x00" * 188)  # 1 TS packet
        produced.append(out_dir)
        return m3u8

    yield _make

    # teardown
    for p in produced:
        shutil.rmtree(p, ignore_errors=True)


# ---------------------------------------------------------------------------
# FakeBrowser 子类：让 fake 抓到的 m3u8 URL 匹配 M3u8RefreshService 的 prefix 正则
# ---------------------------------------------------------------------------


class IntegrationFakeBrowser:
    """扩展 FakeBrowser：把 m3u8 链接改写成 https://example.com/live_hp/<uuid>/...

    让 M3u8RefreshService._extract_prefix 的正则 r"https?://[^/]+/live_hp/[0-9a-f-]+"
    能够命中并提取出 prefix。
    """

    def __init__(self, *, m3u8_links: list[str] | None = None, live_uuid: str | None = None):
        self._live_uuid = live_uuid or "abcdef01-2345-6789-abcd-ef0123456789"
        self._m3u8_links = list(m3u8_links or [])
        self.refresh_count = 0
        self.calls: list[str] = []
        self._m3u8_text_cache: dict[str, str] = {}

    def _wrap(self, link: str) -> str:
        if "/live_hp/" in link:
            return link
        from pathlib import Path as _P
        basename = _P(link).name or "video.m3u8"
        return f"https://fake-host/live_hp/{self._live_uuid}/{basename}"

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
            wrapped = self._wrap(link)
            return [{"message": f'{{"url": "{wrapped}"}}'}]
        return []

    def extract_m3u8_links_from_logs(self, logs, live_uuid):
        link = self._next_link()
        return [self._wrap(link)] if link else []

    def execute_script(self, script: str, *args):
        if args:
            url = self._wrap(args[0])
            if url in self._m3u8_text_cache:
                return self._m3u8_text_cache[url]
            text = (
                "#EXTM3U\n"
                "#EXT-X-VERSION:3\n"
                "#EXT-X-TARGETDURATION:2\n"
                "#EXT-X-MEDIA-SEQUENCE:0\n"
                f"#EXTINF:1.0,\n{url.rsplit('/', 1)[0]}/seg-001.ts\n"
                "#EXT-X-ENDLIST\n"
            )
            self._m3u8_text_cache[url] = text
            return text
        return None

    def quit(self) -> None:
        pass

    def get_cookies(self):
        return [{"name": "session", "value": "fake"}]


@pytest.fixture
def integration_fake_browser_class():
    return IntegrationFakeBrowser