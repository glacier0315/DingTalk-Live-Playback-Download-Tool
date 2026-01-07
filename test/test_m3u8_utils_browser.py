#!/usr/bin/env python3
"""测试 M3U8 工具模块的浏览器相关功能"""
import sys
import os
import json
from unittest.mock import Mock, patch, MagicMock, mock_open
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dingtalk_download.m3u8_utils import (
    _try_play_video,
    _get_browser_logs,
    _save_logs_for_debugging,
    _process_log_entry,
    fetch_m3u8_links,
    _validate_m3u8_download_parameters,
    _ensure_directory_exists,
    _fetch_m3u8_content_via_requests
)


class TestTryPlayVideo:
    """测试触发视频播放功能"""

    @patch('dingtalk_download.m3u8_utils.By')
    def test_try_play_video_success_via_video_tag(self, mock_by):
        """测试通过 video 标签成功触发播放"""
        from dingtalk_download.m3u8_utils import _try_play_video

        mock_browser = Mock()
        mock_video_element = Mock()
        mock_browser.find_element.return_value = mock_video_element

        result = _try_play_video(mock_browser)

        assert result is True
        mock_video_element.execute_script.assert_called_once_with("arguments[0].play();", mock_video_element)

    @patch('dingtalk_download.m3u8_utils.By')
    def test_try_play_video_success_via_button(self, mock_by):
        """测试通过播放按钮成功触发播放"""
        from dingtalk_download.m3u8_utils import _try_play_video

        mock_browser = Mock()
        mock_video_element = Mock()
        mock_video_element.execute_script.side_effect = Exception("Video play failed")
        mock_play_button = Mock()
        mock_browser.find_element.side_effect = [mock_video_element, mock_play_button]

        result = _try_play_video(mock_browser)

        assert result is True
        mock_play_button.click.assert_called_once()

    @patch('dingtalk_download.m3u8_utils.By')
    def test_try_play_video_failure(self, mock_by):
        """测试触发播放失败"""
        from dingtalk_download.m3u8_utils import _try_play_video

        mock_browser = Mock()
        mock_video_element = Mock()
        mock_video_element.execute_script.side_effect = Exception("Video play failed")
        mock_browser.find_element.side_effect = Exception("Button not found")

        result = _try_play_video(mock_browser)

        assert result is False

    @patch('dingtalk_download.m3u8_utils.By')
    def test_try_play_video_timeout(self, mock_by):
        """测试等待视频元素超时"""
        from dingtalk_download.m3u8_utils import _try_play_video

        mock_browser = Mock()
        mock_browser.find_element.side_effect = Exception("Timeout")

        result = _try_play_video(mock_browser)

        assert result is False


class TestGetBrowserLogs:
    """测试获取浏览器日志功能"""

    def test_get_browser_logs_chrome(self):
        """测试获取 Chrome 日志"""
        from dingtalk_download.m3u8_utils import _get_browser_logs

        mock_browser = Mock()
        mock_logs = [
            {'message': '{"message": {"params": {"request": {"url": "https://example.com/video.m3u8"}}}}'},
            {'message': '{"message": {"params": {"request": {"url": "https://example.com/segment.ts"}}}}'}
        ]
        mock_browser.get_log.return_value = mock_logs

        logs = _get_browser_logs(mock_browser, 'chrome')

        assert logs == mock_logs
        mock_browser.get_log.assert_called_once_with("performance")

    def test_get_browser_logs_edge(self):
        """测试获取 Edge 日志"""
        from dingtalk_download.m3u8_utils import _get_browser_logs

        mock_browser = Mock()
        mock_logs = [
            {'message': '{"message": {"params": {"request": {"url": "https://example.com/video.m3u8"}}}}'}
        ]
        mock_browser.get_log.return_value = mock_logs

        logs = _get_browser_logs(mock_browser, 'edge')

        assert logs == mock_logs
        mock_browser.get_log.assert_called_once_with("performance")

    def test_get_browser_logs_firefox(self):
        """测试获取 Firefox 日志"""
        from dingtalk_download.m3u8_utils import _get_browser_logs

        mock_browser = Mock()
        mock_logs = [
            {'url': 'https://example.com/video.m3u8'},
            {'url': 'https://example.com/segment.ts'}
        ]
        mock_browser.execute_script.return_value = mock_logs

        logs = _get_browser_logs(mock_browser, 'firefox')

        assert logs == mock_logs
        mock_browser.execute_script.assert_called_once()

    def test_get_browser_logs_unsupported_browser(self):
        """测试不支持的浏览器类型"""
        from dingtalk_download.m3u8_utils import _get_browser_logs

        mock_browser = Mock()

        with pytest.raises(RuntimeError, match="获取浏览器日志失败"):
            _get_browser_logs(mock_browser, 'safari')

    def test_get_browser_logs_error(self):
        """测试获取日志失败"""
        from dingtalk_download.m3u8_utils import _get_browser_logs

        mock_browser = Mock()
        mock_browser.get_log.side_effect = Exception("Get log failed")

        with pytest.raises(RuntimeError, match="获取浏览器日志失败"):
            _get_browser_logs(mock_browser, 'chrome')


class TestSaveLogsForDebugging:
    """测试保存日志用于调试功能"""

    @patch('dingtalk_download.m3u8_utils.time.strftime')
    @patch('dingtalk_download.m3u8_utils.os.makedirs')
    @patch('dingtalk_download.m3u8_utils.open', new_callable=mock_open)
    def test_save_logs_for_debugging(self, mock_file, mock_makedirs, mock_strftime):
        """测试保存日志"""
        from dingtalk_download.m3u8_utils import _save_logs_for_debugging

        mock_strftime.return_value = "20241218_120000"
        mock_logs = [
            {'message': '{"message": {"params": {"request": {"url": "https://example.com/video.m3u8"}}}}'}
        ]

        _save_logs_for_debugging(mock_logs, 'chrome', 1, 'abc123')

        mock_makedirs.assert_called_once_with("Logs", exist_ok=True)
        mock_file.assert_called_once()
        expected_filename = "Logs/browser_logs_chrome_attempt1_20241218_120000.json"
        assert mock_file.call_args[0][0] == expected_filename

    @patch('dingtalk_download.m3u8_utils.time.strftime')
    @patch('dingtalk_download.m3u8_utils.os.makedirs')
    @patch('dingtalk_download.m3u8_utils.open', new_callable=mock_open)
    def test_save_logs_for_debugging_without_live_uuid(self, mock_file, mock_makedirs, mock_strftime):
        """测试保存日志（无直播 UUID）"""
        from dingtalk_download.m3u8_utils import _save_logs_for_debugging

        mock_strftime.return_value = "20241218_120000"
        mock_logs = [{'message': 'test'}]

        _save_logs_for_debugging(mock_logs, 'edge', 2)

        mock_makedirs.assert_called_once_with("Logs", exist_ok=True)
        mock_file.assert_called_once()


class TestProcessLogEntry:
    """测试处理日志条目功能"""

    def test_process_log_entry_with_url(self):
        """测试处理包含 URL 的日志条目"""
        from dingtalk_download.m3u8_utils import _process_log_entry

        log_entry = {
            'message': json.dumps({
                "message": {
                    "params": {
                        "request": {
                            "url": "https://example.com/live_hp/abc123/video.m3u8"
                        }
                    }
                }
            })
        }

        url = _process_log_entry(log_entry, 'chrome', 'abc123')

        assert url == "https://example.com/live_hp/abc123/video.m3u8"

    def test_process_log_entry_without_url(self):
        """测试处理不包含 URL 的日志条目"""
        from dingtalk_download.m3u8_utils import _process_log_entry

        log_entry = {
            'message': json.dumps({
                "message": {
                    "params": {
                        "request": {
                            "url": "https://example.com/image.jpg"
                        }
                    }
                }
            })
        }

        url = _process_log_entry(log_entry, 'chrome', 'abc123')

        assert url is None

    def test_process_log_entry_invalid_json(self):
        """测试处理无效 JSON 的日志条目"""
        from dingtalk_download.m3u8_utils import _process_log_entry

        log_entry = {
            'message': 'invalid json'
        }

        url = _process_log_entry(log_entry, 'chrome', 'abc123')

        assert url is None

    def test_process_log_entry_missing_message(self):
        """测试缺少 message 字段的日志条目"""
        from dingtalk_download.m3u8_utils import _process_log_entry

        log_entry = {}

        url = _process_log_entry(log_entry, 'chrome', 'abc123')

        assert url is None


class TestFetchM3u8Links:
    """测试获取 M3U8 链接功能"""

    @patch('dingtalk_download.m3u8_utils._try_play_video')
    @patch('dingtalk_download.m3u8_utils._get_browser_logs')
    @patch('dingtalk_download.m3u8_utils._process_log_entry')
    @patch('dingtalk_download.m3u8_utils.extract_live_uuid')
    @patch('dingtalk_download.m3u8_utils._validate_browser_type')
    def test_fetch_m3u8_links_success(self, mock_validate, mock_extract, mock_process, mock_get_logs, mock_trigger):
        """测试成功获取 M3U8 链接"""
        from dingtalk_download.m3u8_utils import fetch_m3u8_links

        mock_browser = Mock()
        mock_get_logs.return_value = [
            {'message': 'log1'},
            {'message': 'log2'}
        ]
        mock_process.side_effect = [
            'https://example.com/live_hp/abc123/video.m3u8',
            None
        ]
        mock_extract.return_value = 'abc123'

        links = fetch_m3u8_links(mock_browser, 'edge', 'https://n.dingtalk.com/live?liveUuid=abc123')

        assert links == ['https://example.com/live_hp/abc123/video.m3u8']
        assert mock_trigger.call_count == 1
        assert mock_get_logs.call_count == 1
        assert mock_process.call_count == 2

    @patch('dingtalk_download.m3u8_utils._try_play_video')
    @patch('dingtalk_download.m3u8_utils._get_browser_logs')
    @patch('dingtalk_download.m3u8_utils._process_log_entry')
    @patch('dingtalk_download.m3u8_utils.extract_live_uuid')
    @patch('dingtalk_download.m3u8_utils._validate_browser_type')
    @patch('dingtalk_download.m3u8_utils.refresh_page_by_click')
    def test_fetch_m3u8_links_retry(self, mock_refresh, mock_validate, mock_extract, mock_process, mock_get_logs, mock_trigger):
        """测试重试获取 M3U8 链接"""
        from dingtalk_download.m3u8_utils import fetch_m3u8_links

        mock_browser = Mock()
        mock_get_logs.return_value = []
        mock_extract.return_value = 'abc123'

        links = fetch_m3u8_links(mock_browser, 'edge', 'https://n.dingtalk.com/live?liveUuid=abc123')

        assert links is None
        assert mock_trigger.call_count == 5
        assert mock_get_logs.call_count == 5
        assert mock_refresh.call_count == 4

    @patch('dingtalk_download.m3u8_utils._try_play_video')
    @patch('dingtalk_download.m3u8_utils._get_browser_logs')
    @patch('dingtalk_download.m3u8_utils.extract_live_uuid')
    @patch('dingtalk_download.m3u8_utils._validate_browser_type')
    def test_fetch_m3u8_links_error(self, mock_validate, mock_extract, mock_get_logs, mock_trigger):
        """测试获取 M3U8 链接时发生错误"""
        from dingtalk_download.m3u8_utils import fetch_m3u8_links

        mock_browser = Mock()
        mock_get_logs.side_effect = Exception("Get logs failed")
        mock_extract.return_value = 'abc123'

        with pytest.raises(RuntimeError, match="获取 M3U8 链接时发生错误"):
            fetch_m3u8_links(mock_browser, 'edge', 'https://n.dingtalk.com/live?liveUuid=abc123')


class TestValidateM3u8DownloadParameters:
    """测试验证 M3U8 下载参数功能"""

    def test_validate_m3u8_download_parameters_success(self):
        """测试验证成功"""
        from dingtalk_download.m3u8_utils import _validate_m3u8_download_parameters

        _validate_m3u8_download_parameters(
            'https://example.com/video.m3u8',
            'output.m3u8',
            {'User-Agent': 'test'}
        )

    def test_validate_m3u8_download_parameters_empty_url(self):
        """测试空 URL"""
        from dingtalk_download.m3u8_utils import _validate_m3u8_download_parameters

        with pytest.raises(ValueError, match="URL 不能为空"):
            _validate_m3u8_download_parameters(
                '',
                'output.m3u8',
                {'User-Agent': 'test'}
            )

    def test_validate_m3u8_download_parameters_invalid_url_type(self):
        """测试无效的 URL 类型"""
        from dingtalk_download.m3u8_utils import _validate_m3u8_download_parameters

        with pytest.raises(ValueError, match="URL 必须是字符串类型"):
            _validate_m3u8_download_parameters(
                123,
                'output.m3u8',
                {'User-Agent': 'test'}
            )

    def test_validate_m3u8_download_parameters_empty_filename(self):
        """测试空文件名"""
        from dingtalk_download.m3u8_utils import _validate_m3u8_download_parameters

        with pytest.raises(ValueError, match="文件名不能为空"):
            _validate_m3u8_download_parameters(
                'https://example.com/video.m3u8',
                '',
                {'User-Agent': 'test'}
            )

    def test_validate_m3u8_download_parameters_invalid_filename_type(self):
        """测试无效的文件名类型"""
        from dingtalk_download.m3u8_utils import _validate_m3u8_download_parameters

        with pytest.raises(ValueError, match="文件名必须是字符串类型"):
            _validate_m3u8_download_parameters(
                'https://example.com/video.m3u8',
                123,
                {'User-Agent': 'test'}
            )

    def test_validate_m3u8_download_parameters_invalid_headers_type(self):
        """测试无效的请求头类型"""
        from dingtalk_download.m3u8_utils import _validate_m3u8_download_parameters

        with pytest.raises(ValueError, match="请求头必须是字典类型"):
            _validate_m3u8_download_parameters(
                'https://example.com/video.m3u8',
                'output.m3u8',
                'invalid'
            )


class TestEnsureDirectoryExists:
    """测试确保目录存在功能"""

    @patch('dingtalk_download.m3u8_utils.os.path.exists')
    @patch('dingtalk_download.m3u8_utils.os.makedirs')
    @patch('dingtalk_download.m3u8_utils.os.access')
    def test_ensure_directory_exists_create(self, mock_access, mock_makedirs, mock_exists):
        """测试创建目录"""
        from dingtalk_download.m3u8_utils import _ensure_directory_exists

        mock_exists.return_value = False

        _ensure_directory_exists('/path/to/output.m3u8')

        mock_makedirs.assert_called_once_with('/path/to', exist_ok=True)

    @patch('dingtalk_download.m3u8_utils.os.path.exists')
    @patch('dingtalk_download.m3u8_utils.os.access')
    def test_ensure_directory_exists_already_exists(self, mock_access, mock_exists):
        """测试目录已存在"""
        from dingtalk_download.m3u8_utils import _ensure_directory_exists

        mock_exists.return_value = True
        mock_access.return_value = True

        _ensure_directory_exists('/path/to/output.m3u8')

    @patch('dingtalk_download.m3u8_utils.os.path.exists')
    @patch('dingtalk_download.m3u8_utils.os.makedirs')
    def test_ensure_directory_exists_create_error(self, mock_makedirs, mock_exists):
        """测试创建目录失败"""
        from dingtalk_download.m3u8_utils import _ensure_directory_exists

        mock_exists.return_value = False
        mock_makedirs.side_effect = Exception("Create failed")

        with pytest.raises(RuntimeError, match="创建目录失败"):
            _ensure_directory_exists('/path/to/output.m3u8')

    @patch('dingtalk_download.m3u8_utils.os.path.exists')
    @patch('dingtalk_download.m3u8_utils.os.access')
    def test_ensure_directory_exists_not_writable(self, mock_access, mock_exists):
        """测试目录不可写"""
        from dingtalk_download.m3u8_utils import _ensure_directory_exists

        mock_exists.return_value = True
        mock_access.return_value = False

        with pytest.raises(PermissionError, match="目录不可写"):
            _ensure_directory_exists('/path/to/output.m3u8')

    def test_ensure_directory_exists_no_directory(self):
        """测试文件名不包含目录"""
        from dingtalk_download.m3u8_utils import _ensure_directory_exists

        _ensure_directory_exists('output.m3u8')


class TestFetchM3u8ContentViaRequests:
    """测试通过 requests 获取 M3U8 内容功能"""

    @patch('dingtalk_download.m3u8_utils.requests.get')
    def test_fetch_m3u8_content_success(self, mock_get):
        """测试成功获取 M3U8 内容"""
        from dingtalk_download.m3u8_utils import _fetch_m3u8_content_via_requests

        mock_response = Mock()
        mock_response.text = '#EXTM3U\n#EXT-X-VERSION:3'
        mock_get.return_value = mock_response

        content = _fetch_m3u8_content_via_requests(
            'https://example.com/video.m3u8',
            {'User-Agent': 'test'},
            {'cookie': 'test'}
        )

        assert content == '#EXTM3U\n#EXT-X-VERSION:3'
        mock_get.assert_called_once_with(
            'https://example.com/video.m3u8',
            headers={'User-Agent': 'test'},
            cookies={'cookie': 'test'},
            timeout=30
        )

    @patch('dingtalk_download.m3u8_utils.requests.get')
    def test_fetch_m3u8_content_empty(self, mock_get):
        """测试获取内容为空"""
        from dingtalk_download.m3u8_utils import _fetch_m3u8_content_via_requests

        mock_response = Mock()
        mock_response.text = ''
        mock_get.return_value = mock_response

        with pytest.raises(RuntimeError, match="下载的 M3U8 内容为空"):
            _fetch_m3u8_content_via_requests(
                'https://example.com/video.m3u8',
                {'User-Agent': 'test'}
            )

    @patch('dingtalk_download.m3u8_utils.requests.get')
    def test_fetch_m3u8_content_error(self, mock_get):
        """测试获取内容失败"""
        from dingtalk_download.m3u8_utils import _fetch_m3u8_content_via_requests
        import requests

        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        with pytest.raises(RuntimeError, match="获取 M3U8 内容失败"):
            _fetch_m3u8_content_via_requests(
                'https://example.com/video.m3u8',
                {'User-Agent': 'test'}
            )

    @patch('dingtalk_download.m3u8_utils.requests.get')
    def test_fetch_m3u8_content_http_error(self, mock_get):
        """测试 HTTP 错误"""
        from dingtalk_download.m3u8_utils import _fetch_m3u8_content_via_requests
        import requests

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        with pytest.raises(RuntimeError, match="获取 M3U8 内容失败"):
            _fetch_m3u8_content_via_requests(
                'https://example.com/video.m3u8',
                {'User-Agent': 'test'}
            )
