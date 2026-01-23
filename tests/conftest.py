"""pytest配置文件

提供全局fixture和pytest钩子函数。
"""

import pytest
import sys
from pathlib import Path
from typing import Generator, Any
from unittest.mock import MagicMock, patch, Mock

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def project_root_path() -> Path:
    """获取项目根目录路径"""
    return project_root


@pytest.fixture(scope="session")
def src_path(project_root_path: Path) -> Path:
    """获取源代码目录路径"""
    return project_root_path / "src"


@pytest.fixture(scope="session")
def tests_path(project_root_path: Path) -> Path:
    """获取测试目录路径"""
    return project_root_path / "tests"


@pytest.fixture(scope="session")
def fixtures_path(tests_path: Path) -> Path:
    """获取fixtures目录路径"""
    return tests_path / "fixtures"


@pytest.fixture(scope="session")
def mocks_path(tests_path: Path) -> Path:
    """获取mocks目录路径"""
    return tests_path / "mocks"


@pytest.fixture(scope="session")
def unit_tests_path(tests_path: Path) -> Path:
    """获取单元测试目录路径"""
    return tests_path / "unit"


@pytest.fixture(scope="session")
def integration_tests_path(tests_path: Path) -> Path:
    """获取集成测试目录路径"""
    return tests_path / "integration"


@pytest.fixture(scope="session")
def output_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """创建测试输出目录"""
    return tmp_path_factory.mktemp("output")


@pytest.fixture(scope="function")
def mock_logger(mocker) -> MagicMock:
    """Mock日志记录器"""
    logger = mocker.MagicMock()
    logger.debug = mocker.MagicMock()
    logger.info = mocker.MagicMock()
    logger.warning = mocker.MagicMock()
    logger.error = mocker.MagicMock()
    logger.critical = mocker.MagicMock()
    logger.exception = mocker.MagicMock()
    return logger


@pytest.fixture(scope="function")
def mock_config(mocker) -> MagicMock:
    """Mock配置对象"""
    config = mocker.MagicMock()
    config.get = mocker.MagicMock(return_value="mock_value")
    config.get.side_effect = lambda key, default=None: {
        "output_dir": "output",
        "browser": "edge",
        "timeout": 30,
        "retry": 3,
        "max_workers": 4,
        "download_dir": "downloads",
        "log_level": "INFO",
    }.get(key, default)
    config.set = mocker.MagicMock()
    config.save = mocker.MagicMock()
    config.load = mocker.MagicMock()
    return config


@pytest.fixture(scope="function")
def mock_file_reader(mocker) -> MagicMock:
    """Mock文件读取器"""
    reader = mocker.MagicMock()
    reader.read_csv = mocker.MagicMock(
        return_value=[{"url": "https://live.dingtalk.com/123456789", "name": "Test"}]
    )
    reader.read_excel = mocker.MagicMock(
        return_value=[{"url": "https://live.dingtalk.com/987654321", "name": "Test"}]
    )
    reader.read_txt = mocker.MagicMock(return_value=["https://live.dingtalk.com/111222333"])
    return reader


@pytest.fixture(scope="function")
def mock_validator(mocker) -> MagicMock:
    """Mock验证器"""
    validator = mocker.MagicMock()
    validator.validate_url = mocker.MagicMock(return_value=True)
    validator.validate_email = mocker.MagicMock(return_value=True)
    validator.validate_file = mocker.MagicMock(return_value=True)
    validator.validate_path = mocker.MagicMock(return_value=True)
    return validator


@pytest.fixture(scope="function")
def mock_path_helper(mocker) -> MagicMock:
    """Mock路径助手"""
    helper = mocker.MagicMock()
    helper.get_output_dir = mocker.MagicMock(return_value="output")
    helper.get_filename = mocker.MagicMock(return_value="test.mp4")
    helper.ensure_dir = mocker.MagicMock()
    helper.join = mocker.MagicMock(side_effect=lambda *args: "/".join(map(str, args)))
    return helper


@pytest.fixture(scope="function")
def mock_progress_callback(mocker) -> MagicMock:
    """Mock进度回调函数"""
    callback = mocker.MagicMock()
    callback.__call__ = mocker.MagicMock()
    return callback


@pytest.fixture(scope="function")
def mock_event_emitter(mocker) -> MagicMock:
    """Mock事件发射器"""
    emitter = mocker.MagicMock()
    emitter.emit = mocker.MagicMock()
    emitter.on = mocker.MagicMock()
    emitter.off = mocker.MagicMock()
    emitter.once = mocker.MagicMock()
    emitter.remove_listener = mocker.MagicMock()
    emitter.remove_all_listeners = mocker.MagicMock()
    return emitter


@pytest.fixture(scope="function")
def sample_live_urls() -> list:
    """示例直播URL列表"""
    return [
        "https://live.dingtalk.com/123456789",
        "https://live.dingtalk.com/987654321",
        "https://live.dingtalk.com/111222333",
    ]


@pytest.fixture(scope="function")
def sample_m3u8_content() -> str:
    """示例M3U8内容"""
    return """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXTINF:10.0,
segment1.ts
#EXTINF:10.0,
segment2.ts
#EXTINF:10.0,
segment3.ts
#EXT-X-ENDLIST
"""


@pytest.fixture(scope="function")
def sample_nested_m3u8_content() -> str:
    """示例嵌套M3U8内容"""
    return """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=1280x720
720p.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=2000000,RESOLUTION=1920x1080
1080p.m3u8
"""


@pytest.fixture(scope="function")
def sample_cookies() -> list:
    """示例Cookie列表"""
    return [
        {"name": "session_id", "value": "abc123", "domain": ".dingtalk.com"},
        {"name": "user_token", "value": "token456", "domain": ".dingtalk.com"},
        {"name": "csrf_token", "value": "csrf789", "domain": ".dingtalk.com"},
    ]


@pytest.fixture(scope="function")
def sample_headers() -> dict:
    """示例HTTP头"""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cookie": "session_id=abc123; user_token=token456",
    }


@pytest.fixture(scope="function")
def sample_config() -> dict:
    """示例配置"""
    return {
        "output_dir": "output",
        "browser": "edge",
        "timeout": 30,
        "retry": 3,
        "max_workers": 4,
        "download_dir": "downloads",
        "log_level": "INFO",
        "use_proxy": False,
        "proxy_url": "",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        },
    }


@pytest.fixture(scope="function")
def mock_subprocess(mocker) -> MagicMock:
    """Mock subprocess模块"""
    mock_subprocess = mocker.MagicMock()
    mock_subprocess.run.return_value = MagicMock(
        returncode=0, stdout="Success", stderr="", args=["mock_command"]
    )
    mock_subprocess.Popen.return_value = MagicMock(
        poll=lambda: 0, wait=lambda: None, communicate=lambda: ("Success", ""), returncode=0
    )
    mock_subprocess.PIPE = mocker.MagicMock()
    mock_subprocess.DEVNULL = mocker.MagicMock()
    return mock_subprocess


@pytest.fixture(scope="function")
def mock_thread_pool(mocker) -> MagicMock:
    """Mock线程池"""
    pool = mocker.MagicMock()
    pool.submit.return_value = MagicMock()
    pool.map.return_value = []
    pool.shutdown.return_value = None
    return pool


@pytest.fixture(scope="function")
def mock_process_pool(mocker) -> MagicMock:
    """Mock进程池"""
    pool = mocker.MagicMock()
    pool.submit.return_value = MagicMock()
    pool.map.return_value = []
    pool.shutdown.return_value = None
    return pool


@pytest.fixture(scope="function")
def mock_queue(mocker) -> MagicMock:
    """Mock队列"""
    queue = mocker.MagicMock()
    queue.put.return_value = None
    queue.get.return_value = "mock_item"
    queue.empty.return_value = False
    queue.qsize.return_value = 10
    queue.task_done.return_value = None
    queue.join.return_value = None
    return queue


@pytest.fixture(scope="function")
def mock_lock(mocker) -> MagicMock:
    """Mock锁"""
    lock = mocker.MagicMock()
    lock.acquire.return_value = True
    lock.release.return_value = None
    lock.__enter__ = mocker.MagicMock(return_value=None)
    lock.__exit__ = mocker.MagicMock(return_value=None)
    return lock


@pytest.fixture(scope="function")
def mock_semaphore(mocker) -> MagicMock:
    """Mock信号量"""
    sem = mocker.MagicMock()
    sem.acquire.return_value = True
    sem.release.return_value = None
    sem.__enter__ = mocker.MagicMock(return_value=None)
    sem.__exit__ = mocker.MagicMock(return_value=None)
    return sem


@pytest.fixture(scope="function")
def mock_event(mocker) -> MagicMock:
    """Mock事件"""
    event = mocker.MagicMock()
    event.is_set.return_value = False
    event.set.return_value = None
    event.clear.return_value = None
    event.wait.return_value = True
    return event


@pytest.fixture(scope="function")
def mock_timer(mocker) -> MagicMock:
    """Mock定时器"""
    timer = mocker.MagicMock()
    timer.start.return_value = None
    timer.cancel.return_value = None
    timer.is_alive.return_value = True
    return timer


@pytest.fixture(scope="function")
def mock_thread(mocker) -> MagicMock:
    """Mock线程"""
    thread = mocker.MagicMock()
    thread.start.return_value = None
    thread.join.return_value = None
    thread.is_alive.return_value = False
    return thread


@pytest.fixture(scope="function")
def mock_process(mocker) -> MagicMock:
    """Mock进程"""
    process = mocker.MagicMock()
    process.start.return_value = None
    process.join.return_value = None
    process.is_alive.return_value = False
    process.terminate.return_value = None
    process.kill.return_value = None
    return process


def pytest_configure(config):
    """pytest配置钩子"""
    config.addinivalue_line("markers", "unit: 单元测试")
    config.addinivalue_line("markers", "integration: 集成测试")
    config.addinivalue_line("markers", "slow: 慢速测试")
    config.addinivalue_line("markers", "browser: 浏览器相关测试")
    config.addinivalue_line("markers", "network: 网络相关测试")
    config.addinivalue_line("markers", "file: 文件相关测试")
    config.addinivalue_line("markers", "cookie: Cookie相关测试")
    config.addinivalue_line("markers", "m3u8: M3U8相关测试")
    config.addinivalue_line("markers", "downloader: 下载器相关测试")
    config.addinivalue_line("markers", "binary: 二进制工具相关测试")
    config.addinivalue_line("markers", "settings: 设置相关测试")
    config.addinivalue_line("markers", "main: 主程序相关测试")


def pytest_collection_modifyitems(config, items):
    """修改测试收集钩子"""
    for item in items:
        # 为所有测试添加标记
        if "tests/unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "tests/integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


@pytest.fixture(autouse=True)
def setup_test_environment():
    """自动设置测试环境"""
    # 在每个测试前执行
    yield
    # 在每个测试后执行
    pass
