"""Mock测试Fixture模块

提供通用的Mock工具和辅助函数，用于测试中的各种mock场景。
"""

import pytest
from unittest.mock import MagicMock, Mock, patch
from pathlib import Path
from typing import Any, Dict, List, Optional


@pytest.fixture
def mock_response():
    """Mock HTTP响应对象"""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "<html>Mock Response</html>"
    mock_resp.content = b"Mock Content"
    mock_resp.json.return_value = {"status": "success"}
    mock_resp.headers = {"Content-Type": "text/html"}
    return mock_resp


@pytest.fixture
def mock_response_error():
    """Mock HTTP错误响应"""
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.text = "Not Found"
    mock_resp.raise_for_status.side_effect = Exception("404 Not Found")
    return mock_resp


@pytest.fixture
def mock_response_timeout():
    """Mock HTTP超时响应"""
    mock_resp = MagicMock()
    mock_resp.status_code = 408
    mock_resp.text = "Request Timeout"
    mock_resp.raise_for_status.side_effect = Exception("Request Timeout")
    return mock_resp


@pytest.fixture
def mock_requests(mocker):
    """Mock requests库"""
    mock_requests = mocker.MagicMock()
    mock_requests.get.return_value = MagicMock(status_code=200, text="Success")
    mock_requests.post.return_value = MagicMock(status_code=200, text="Success")
    mock_requests.Session.return_value = MagicMock()
    return mock_requests


@pytest.fixture
def mock_subprocess(mocker):
    """Mock subprocess模块"""
    mock_subprocess = mocker.MagicMock()
    mock_subprocess.run.return_value = MagicMock(
        returncode=0, stdout="Success", stderr="", args=["mock_command"]
    )
    mock_subprocess.Popen.return_value = MagicMock(
        poll=lambda: 0, wait=lambda: None, communicate=lambda: ("Success", "")
    )
    return mock_subprocess


@pytest.fixture
def mock_os(mocker):
    """Mock os模块"""
    mock_os = mocker.MagicMock()
    mock_os.path.exists.return_value = True
    mock_os.path.isfile.return_value = True
    mock_os.path.isdir.return_value = True
    mock_os.path.join.side_effect = lambda *args: "/".join(args)
    mock_os.makedirs.return_value = None
    mock_os.remove.return_value = None
    mock_os.rmdir.return_value = None
    return mock_os


@pytest.fixture
def mock_pathlib(mocker):
    """Mock pathlib模块"""
    mock_path = mocker.MagicMock()
    mock_path.Path = Path
    mock_path.Path.return_value.exists.return_value = True
    mock_path.Path.return_value.is_file.return_value = True
    mock_path.Path.return_value.is_dir.return_value = True
    mock_path.Path.return_value.mkdir.return_value = None
    mock_path.Path.return_value.write_text.return_value = None
    mock_path.Path.return_value.read_text.return_value = "Mock Content"
    return mock_path


@pytest.fixture
def mock_logger(mocker):
    """Mock日志记录器"""
    mock_logger = mocker.MagicMock()
    mock_logger.debug = MagicMock()
    mock_logger.info = MagicMock()
    mock_logger.warning = MagicMock()
    mock_logger.error = MagicMock()
    mock_logger.critical = MagicMock()
    return mock_logger


@pytest.fixture
def mock_config():
    """Mock配置对象"""
    mock_config = MagicMock()
    mock_config.get.return_value = "mock_value"
    mock_config.get.side_effect = lambda key, default=None: {
        "output_dir": "output",
        "browser": "edge",
        "timeout": 30,
        "retry": 3,
    }.get(key, default)
    return mock_config


@pytest.fixture
def mock_file_reader():
    """Mock文件读取器"""
    mock_reader = MagicMock()
    mock_reader.read_csv.return_value = [
        {"url": "https://live.dingtalk.com/123456789", "name": "Test"}
    ]
    mock_reader.read_excel.return_value = [
        {"url": "https://live.dingtalk.com/987654321", "name": "Test"}
    ]
    mock_reader.read_txt.return_value = ["https://live.dingtalk.com/111222333"]
    return mock_reader


@pytest.fixture
def mock_downloader():
    """Mock下载器"""
    mock_downloader = MagicMock()
    mock_downloader.download.return_value = True
    mock_downloader.download_batch.return_value = [
        {"url": "https://live.dingtalk.com/123456789", "success": True}
    ]
    mock_downloader.parse_link.return_value = {
        "url": "https://live.dingtalk.com/123456789",
        "name": "Test Live",
    }
    return mock_downloader


@pytest.fixture
def mock_m3u8_parser():
    """Mock M3U8解析器"""
    mock_parser = MagicMock()
    mock_parser.parse.return_value = {
        "segments": ["segment1.ts", "segment2.ts", "segment3.ts"],
        "base_url": "https://example.com/",
        "duration": 30,
    }
    mock_parser.extract_base_url.return_value = "https://example.com/"
    mock_parser.extract_m3u8_links.return_value = ["https://example.com/playlist.m3u8"]
    return mock_parser


@pytest.fixture
def mock_ffmpeg_wrapper():
    """Mock FFmpeg包装器"""
    mock_ffmpeg = MagicMock()
    mock_ffmpeg.convert.return_value = True
    mock_ffmpeg.merge.return_value = True
    mock_ffmpeg.check_available.return_value = True
    return mock_ffmpeg


@pytest.fixture
def mock_n_m3u8dl_re():
    """Mock N_m3u8DL-RE工具"""
    mock_tool = MagicMock()
    mock_tool.download.return_value = True
    mock_tool.check_available.return_value = True
    mock_tool.get_version.return_value = "1.0.0"
    return mock_tool


@pytest.fixture
def mock_settings():
    """Mock设置对象"""
    mock_settings = MagicMock()
    mock_settings.get.return_value = "mock_value"
    mock_settings.load.return_value = None
    mock_settings.save.return_value = None
    return mock_settings


@pytest.fixture
def mock_validator():
    """Mock验证器"""
    mock_validator = MagicMock()
    mock_validator.validate_url.return_value = True
    mock_validator.validate_email.return_value = True
    mock_validator.validate_file.return_value = True
    return mock_validator


@pytest.fixture
def mock_path_helper():
    """Mock路径助手"""
    mock_helper = MagicMock()
    mock_helper.get_output_dir.return_value = "output"
    mock_helper.get_filename.return_value = "test.mp4"
    mock_helper.ensure_dir.return_value = None
    return mock_helper


@pytest.fixture
def mock_exception():
    """Mock异常对象"""
    mock_exc = MagicMock()
    mock_exc.__str__ = lambda self: "Mock Exception"
    mock_exc.__repr__ = lambda self: "Mock Exception()"
    return mock_exc


@pytest.fixture
def mock_network_error():
    """Mock网络错误"""
    mock_error = MagicMock()
    mock_error.__str__ = lambda self: "Network Error"
    mock_error.__repr__ = lambda self: "Network Error()"
    return mock_error


@pytest.fixture
def mock_file_error():
    """Mock文件错误"""
    mock_error = MagicMock()
    mock_error.__str__ = lambda self: "File Error"
    mock_error.__repr__ = lambda self: "File Error()"
    return mock_error


@pytest.fixture
def mock_timeout_error():
    """Mock超时错误"""
    mock_error = MagicMock()
    mock_error.__str__ = lambda self: "Timeout Error"
    mock_error.__repr__ = lambda self: "Timeout Error()"
    return mock_error


@pytest.fixture
def mock_retry_decorator():
    """Mock重试装饰器"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


@pytest.fixture
def mock_progress_callback():
    """Mock进度回调函数"""
    mock_callback = MagicMock()
    mock_callback.return_value = None
    return mock_callback


@pytest.fixture
def mock_event_emitter():
    """Mock事件发射器"""
    mock_emitter = MagicMock()
    mock_emitter.emit = MagicMock()
    mock_emitter.on = MagicMock()
    mock_emitter.off = MagicMock()
    return mock_emitter


@pytest.fixture
def mock_async_executor():
    """Mock异步执行器"""
    mock_executor = MagicMock()
    mock_executor.submit.return_value = MagicMock()
    mock_executor.map.return_value = []
    mock_executor.shutdown.return_value = None
    return mock_executor


@pytest.fixture
def mock_thread_pool(mocker):
    """Mock线程池"""
    mock_pool = mocker.MagicMock()
    mock_pool.submit.return_value = MagicMock()
    mock_pool.map.return_value = []
    mock_pool.shutdown.return_value = None
    return mock_pool


@pytest.fixture
def mock_process_pool(mocker):
    """Mock进程池"""
    mock_pool = mocker.MagicMock()
    mock_pool.submit.return_value = MagicMock()
    mock_pool.map.return_value = []
    mock_pool.shutdown.return_value = None
    return mock_pool


@pytest.fixture
def mock_queue():
    """Mock队列"""
    mock_q = MagicMock()
    mock_q.put.return_value = None
    mock_q.get.return_value = "mock_item"
    mock_q.empty.return_value = False
    mock_q.qsize.return_value = 10
    return mock_q


@pytest.fixture
def mock_lock():
    """Mock锁"""
    mock_lock = MagicMock()
    mock_lock.acquire.return_value = True
    mock_lock.release.return_value = None
    mock_lock.__enter__ = MagicMock(return_value=None)
    mock_lock.__exit__ = MagicMock(return_value=None)
    return mock_lock


@pytest.fixture
def mock_semaphore():
    """Mock信号量"""
    mock_sem = MagicMock()
    mock_sem.acquire.return_value = True
    mock_sem.release.return_value = None
    return mock_sem


@pytest.fixture
def mock_event():
    """Mock事件"""
    mock_event = MagicMock()
    mock_event.is_set.return_value = False
    mock_event.set.return_value = None
    mock_event.clear.return_value = None
    mock_event.wait.return_value = True
    return mock_event


@pytest.fixture
def mock_condition():
    """Mock条件变量"""
    mock_cond = MagicMock()
    mock_cond.acquire.return_value = True
    mock_cond.release.return_value = None
    mock_cond.wait.return_value = True
    mock_cond.notify.return_value = None
    mock_cond.notify_all.return_value = None
    return mock_cond


@pytest.fixture
def mock_timer():
    """Mock定时器"""
    mock_timer = MagicMock()
    mock_timer.start.return_value = None
    mock_timer.cancel.return_value = None
    mock_timer.is_alive.return_value = True
    return mock_timer


@pytest.fixture
def mock_thread(mocker):
    """Mock线程"""
    mock_thread = mocker.MagicMock()
    mock_thread.start.return_value = None
    mock_thread.join.return_value = None
    mock_thread.is_alive.return_value = False
    return mock_thread


@pytest.fixture
def mock_process(mocker):
    """Mock进程"""
    mock_process = mocker.MagicMock()
    mock_process.start.return_value = None
    mock_process.join.return_value = None
    mock_process.is_alive.return_value = False
    mock_process.terminate.return_value = None
    mock_process.kill.return_value = None
    return mock_process
