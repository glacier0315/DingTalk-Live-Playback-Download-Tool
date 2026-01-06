"""测试 m3u8_utils.py 模块的单元测试"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Optional


class TestExtractPrefix:
    """测试extract_prefix函数"""

    def test_extract_prefix_from_m3u8_url(self):
        """测试从M3U8 URL提取前缀"""
        from dingtalk_download.m3u8_utils import extract_prefix

        url = "https://example.com/live_hp/abc123-def456-789abc/chunklist.m3u8"
        result = extract_prefix(url)
        assert result == "https://example.com/live_hp/abc123-def456-789abc"

    def test_return_original_url_if_no_match(self):
        """测试没有匹配时返回原始URL"""
        from dingtalk_download.m3u8_utils import extract_prefix

        url = "https://example.com/some/path/file.m3u8"
        result = extract_prefix(url)
        assert result == url

    def test_extract_prefix_empty_url(self):
        """测试空URL"""
        from dingtalk_download.m3u8_utils import extract_prefix

        with pytest.raises(ValueError, match="URL 不能为空"):
            extract_prefix("")

    def test_extract_prefix_non_string_url(self):
        """测试非字符串URL"""
        from dingtalk_download.m3u8_utils import extract_prefix

        with pytest.raises(ValueError, match="URL 必须是字符串类型"):
            extract_prefix(123)


class TestExtractLiveUuid:
    """测试extract_live_uuid函数"""

    def test_extract_live_uuid_from_url(self):
        """测试从URL提取liveUuid"""
        from dingtalk_download.m3u8_utils import extract_live_uuid

        url = "https://n.dingtalk.com/live?liveUuid=abc123"
        result = extract_live_uuid(url)
        assert result == "abc123"

    def test_extract_live_uuid_no_uuid(self):
        """测试URL中没有liveUuid"""
        from dingtalk_download.m3u8_utils import extract_live_uuid

        url = "https://n.dingtalk.com/live"
        result = extract_live_uuid(url)
        assert result is None

    def test_extract_live_uuid_empty_url(self):
        """测试空URL"""
        from dingtalk_download.m3u8_utils import extract_live_uuid

        with pytest.raises(ValueError, match="钉钉 URL 不能为空"):
            extract_live_uuid("")

    def test_extract_live_uuid_non_string_url(self):
        """测试非字符串URL"""
        from dingtalk_download.m3u8_utils import extract_live_uuid

        with pytest.raises(ValueError, match="钉钉 URL 必须是字符串类型"):
            extract_live_uuid(123)


class TestRefreshPageByClick:
    """测试refresh_page_by_click函数"""

    def test_refresh_page_by_click_success(self):
        """测试刷新页面成功"""
        from dingtalk_download.m3u8_utils import refresh_page_by_click

        browser_instance = Mock()

        refresh_page_by_click(browser_instance)

        browser_instance.execute_script.assert_called_once_with("location.reload();")

    def test_refresh_page_by_click_error(self):
        """测试刷新页面错误"""
        from dingtalk_download.m3u8_utils import refresh_page_by_click

        browser_instance = Mock()
        browser_instance.execute_script.side_effect = Exception("Script error")

        with pytest.raises(RuntimeError, match="刷新页面时发生错误"):
            refresh_page_by_click(browser_instance)


class TestValidateBrowserType:
    """测试_validate_browser_type函数"""

    def test_validate_browser_type_valid(self):
        """测试有效的浏览器类型"""
        from dingtalk_download.m3u8_utils import _validate_browser_type

        _validate_browser_type('chrome')
        _validate_browser_type('edge')
        _validate_browser_type('firefox')

    def test_validate_browser_type_invalid(self):
        """测试无效的浏览器类型"""
        from dingtalk_download.m3u8_utils import _validate_browser_type

        with pytest.raises(ValueError, match="不支持的浏览器类型"):
            _validate_browser_type('safari')

    def test_validate_browser_type_empty(self):
        """测试空浏览器类型"""
        from dingtalk_download.m3u8_utils import _validate_browser_type

        with pytest.raises(ValueError, match="不支持的浏览器类型"):
            _validate_browser_type('')


class TestParseFirefoxLog:
    """测试_parse_firefox_log函数"""

    def test_parse_firefox_log_valid(self):
        """测试解析有效的Firefox日志"""
        from dingtalk_download.m3u8_utils import _parse_firefox_log

        log_message = "Network request: https://example.com/video.m3u8?token=abc123"
        result = _parse_firefox_log(log_message)
        assert result == "https://example.com/video.m3u8?token=abc123"

    def test_parse_firefox_log_no_m3u8(self):
        """测试没有M3U8链接的日志"""
        from dingtalk_download.m3u8_utils import _parse_firefox_log

        log_message = "Network request: https://example.com/video.mp4"
        result = _parse_firefox_log(log_message)
        assert result is None

    def test_parse_firefox_log_empty(self):
        """测试空日志"""
        from dingtalk_download.m3u8_utils import _parse_firefox_log

        log_message = ""
        result = _parse_firefox_log(log_message)
        assert result is None


class TestParseChromeEdgeLog:
    """测试_parse_chrome_edge_log函数"""

    def test_parse_chrome_edge_log_valid(self):
        """测试解析有效的Chrome/Edge日志"""
        from dingtalk_download.m3u8_utils import _parse_chrome_edge_log

        log_message = 'Network request: url:"https://example.com/live_hp/abc123/video.m3u8"'
        result = _parse_chrome_edge_log(log_message, 'abc123')
        assert result == "https://example.com/live_hp/abc123/video.m3u8"

    def test_parse_chrome_edge_log_no_m3u8(self):
        """测试没有M3U8链接的日志"""
        from dingtalk_download.m3u8_utils import _parse_chrome_edge_log

        log_message = 'Network request: url:"https://example.com/video.mp4"'
        result = _parse_chrome_edge_log(log_message, 'abc123')
        assert result is None

    def test_parse_chrome_edge_log_no_url(self):
        """测试没有url字段的日志"""
        from dingtalk_download.m3u8_utils import _parse_chrome_edge_log

        log_message = 'Network request: data:"test"'
        result = _parse_chrome_edge_log(log_message, 'abc123')
        assert result is None

    def test_parse_chrome_edge_log_no_uuid(self):
        """测试UUID不匹配"""
        from dingtalk_download.m3u8_utils import _parse_chrome_edge_log

        log_message = 'Network request: url:"https://example.com/live_hp/def456/video.m3u8"'
        result = _parse_chrome_edge_log(log_message, 'abc123')
        assert result is None


class TestProcessLogEntry:
    """测试_process_log_entry函数"""

    @patch('dingtalk_download.m3u8_utils._parse_firefox_log')
    def test_process_log_entry_firefox(self, mock_parse_firefox):
        """测试处理Firefox日志条目"""
        from dingtalk_download.m3u8_utils import _process_log_entry

        log = {'level': 'INFO'}
        mock_parse_firefox.return_value = "https://example.com/video.m3u8"

        result = _process_log_entry(log, 'firefox', 'abc123')
        assert result == "https://example.com/video.m3u8"

    @patch('dingtalk_download.m3u8_utils._parse_chrome_edge_log')
    def test_process_log_entry_chrome(self, mock_parse_chrome_edge):
        """测试处理Chrome日志条目"""
        from dingtalk_download.m3u8_utils import _process_log_entry

        log = {'level': 'INFO'}
        mock_parse_chrome_edge.return_value = "https://example.com/video.m3u8"

        result = _process_log_entry(log, 'chrome', 'abc123')
        assert result == "https://example.com/video.m3u8"


class TestEnsureDirectoryExists:
    """测试_ensure_directory_exists函数"""

    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_ensure_directory_exists_creates(self, mock_exists, mock_makedirs):
        """测试创建目录"""
        from dingtalk_download.m3u8_utils import _ensure_directory_exists

        mock_exists.return_value = False

        _ensure_directory_exists('test/file.m3u8')

        mock_makedirs.assert_called_once()

    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_ensure_directory_exists_exists(self, mock_exists, mock_makedirs):
        """测试目录已存在"""
        from dingtalk_download.m3u8_utils import _ensure_directory_exists

        mock_exists.return_value = True

        _ensure_directory_exists('test/file.m3u8')

        mock_makedirs.assert_not_called()

    @patch('os.makedirs')
    @patch('os.path.exists')
    def test_ensure_directory_exists_error(self, mock_exists, mock_makedirs):
        """测试创建目录失败"""
        from dingtalk_download.m3u8_utils import _ensure_directory_exists

        mock_exists.return_value = False
        mock_makedirs.side_effect = OSError("Permission denied")

        with pytest.raises(RuntimeError, match="创建目录失败"):
            _ensure_directory_exists('test/file.m3u8')


class TestSaveM3u8ContentToFile:
    """测试_save_m3u8_content_to_file函数"""

    @patch('builtins.open', create=True)
    def test_save_m3u8_content_to_file_success(self, mock_open):
        """测试保存M3U8内容成功"""
        from dingtalk_download.m3u8_utils import _save_m3u8_content_to_file

        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        _save_m3u8_content_to_file('test.m3u8', '#EXTM3U\n#EXT-X-VERSION:3')

        mock_file.write.assert_called_once()

    @patch('builtins.open', create=True)
    def test_save_m3u8_content_to_file_error(self, mock_open):
        """测试保存M3U8内容失败"""
        from dingtalk_download.m3u8_utils import _save_m3u8_content_to_file

        mock_open.side_effect = IOError("Permission denied")

        with pytest.raises(IOError, match="保存 M3U8 文件失败"):
            _save_m3u8_content_to_file('test.m3u8', '#EXTM3U\n#EXT-X-VERSION:3')


class TestValidateM3u8DownloadParameters:
    """测试_validate_m3u8_download_parameters函数"""

    def test_validate_m3u8_download_parameters_valid(self):
        """测试有效的参数"""
        from dingtalk_download.m3u8_utils import _validate_m3u8_download_parameters

        _validate_m3u8_download_parameters('https://example.com/video.m3u8', 'output.m3u8', {'Cookie': 'test'})

    def test_validate_m3u8_download_parameters_empty_url(self):
        """测试空URL"""
        from dingtalk_download.m3u8_utils import _validate_m3u8_download_parameters

        with pytest.raises(ValueError, match="URL 不能为空"):
            _validate_m3u8_download_parameters('', 'output.m3u8', {})

    def test_validate_m3u8_download_parameters_empty_filename(self):
        """测试空文件名"""
        from dingtalk_download.m3u8_utils import _validate_m3u8_download_parameters

        with pytest.raises(ValueError, match="文件名不能为空"):
            _validate_m3u8_download_parameters('https://example.com/video.m3u8', '', {})

    def test_validate_m3u8_download_parameters_empty_headers(self):
        """测试空headers"""
        from dingtalk_download.m3u8_utils import _validate_m3u8_download_parameters

        with pytest.raises(ValueError, match="请求头不能为空"):
            _validate_m3u8_download_parameters('https://example.com/video.m3u8', 'output.m3u8', {})

    def test_validate_m3u8_download_parameters_invalid_headers(self):
        """测试无效的headers"""
        from dingtalk_download.m3u8_utils import _validate_m3u8_download_parameters

        with pytest.raises(ValueError, match="请求头必须是字典类型"):
            _validate_m3u8_download_parameters('https://example.com/video.m3u8', 'output.m3u8', 'invalid')

    def test_validate_m3u8_download_parameters_non_string_url(self):
        """测试非字符串URL"""
        from dingtalk_download.m3u8_utils import _validate_m3u8_download_parameters

        with pytest.raises(ValueError, match="URL 必须是字符串类型"):
            _validate_m3u8_download_parameters(123, 'output.m3u8', {})

    def test_validate_m3u8_download_parameters_non_string_filename(self):
        """测试非字符串文件名"""
        from dingtalk_download.m3u8_utils import _validate_m3u8_download_parameters

        with pytest.raises(ValueError, match="文件名必须是字符串类型"):
            _validate_m3u8_download_parameters('https://example.com/video.m3u8', 123, {})


class TestGetBrowserLogs:
    """测试_get_browser_logs函数"""

    @patch('dingtalk_download.m3u8_utils.browser')
    def test_get_browser_logs_chrome(self, mock_browser):
        """测试获取Chrome浏览器日志"""
        from dingtalk_download.m3u8_utils import _get_browser_logs

        browser_instance = Mock()
        browser_instance.get_log.return_value = [{'level': 'INFO'}]

        result = _get_browser_logs(browser_instance, 'chrome')
        assert len(result) == 1

    @patch('dingtalk_download.m3u8_utils.browser')
    def test_get_browser_logs_edge(self, mock_browser):
        """测试获取Edge浏览器日志"""
        from dingtalk_download.m3u8_utils import _get_browser_logs

        browser_instance = Mock()
        browser_instance.get_log.return_value = [{'level': 'INFO'}]

        result = _get_browser_logs(browser_instance, 'edge')
        assert len(result) == 1

    @patch('dingtalk_download.m3u8_utils.browser')
    def test_get_browser_logs_firefox(self, mock_browser):
        """测试获取Firefox浏览器日志"""
        from dingtalk_download.m3u8_utils import _get_browser_logs

        browser_instance = Mock()
        browser_instance.execute_script.return_value = [{'level': 'INFO'}]

        result = _get_browser_logs(browser_instance, 'firefox')
        assert len(result) == 1

    @patch('dingtalk_download.m3u8_utils.browser')
    def test_get_browser_logs_invalid_type(self, mock_browser):
        """测试无效的浏览器类型"""
        from dingtalk_download.m3u8_utils import _get_browser_logs

        browser_instance = Mock()

        with pytest.raises(RuntimeError, match="获取浏览器日志失败"):
            _get_browser_logs(browser_instance, 'safari')

    @patch('dingtalk_download.m3u8_utils.browser')
    def test_get_browser_logs_error(self, mock_browser):
        """测试获取日志失败"""
        from dingtalk_download.m3u8_utils import _get_browser_logs

        browser_instance = Mock()
        browser_instance.get_log.side_effect = Exception("Log error")

        with pytest.raises(RuntimeError, match="获取浏览器日志失败"):
            _get_browser_logs(browser_instance, 'chrome')


class TestFetchM3u8Links:
    """测试fetch_m3u8_links函数"""

    @patch('dingtalk_download.m3u8_utils._process_log_entry')
    @patch('dingtalk_download.m3u8_utils._get_browser_logs')
    @patch('dingtalk_download.m3u8_utils.extract_live_uuid')
    @patch('dingtalk_download.m3u8_utils._validate_browser_type')
    def test_fetch_m3u8_links_success(self, mock_validate, mock_extract, mock_get_logs, mock_process):
        """测试成功获取M3U8链接"""
        from dingtalk_download.m3u8_utils import fetch_m3u8_links

        mock_extract.return_value = 'abc123'
        mock_get_logs.return_value = [{'level': 'INFO'}]
        mock_process.return_value = 'https://example.com/video.m3u8'

        browser_instance = Mock()
        result = fetch_m3u8_links(browser_instance, 'chrome', 'https://n.dingtalk.com/live?liveUuid=abc123')

        assert result == ['https://example.com/video.m3u8']

    @patch('dingtalk_download.m3u8_utils.extract_live_uuid')
    def test_fetch_m3u8_links_no_uuid(self, mock_extract):
        """测试没有UUID"""
        from dingtalk_download.m3u8_utils import fetch_m3u8_links

        mock_extract.return_value = None

        browser_instance = Mock()
        result = fetch_m3u8_links(browser_instance, 'chrome', 'https://n.dingtalk.com/live')

        assert result is None

    @patch('dingtalk_download.m3u8_utils.refresh_page_by_click')
    @patch('dingtalk_download.m3u8_utils._process_log_entry')
    @patch('dingtalk_download.m3u8_utils._get_browser_logs')
    @patch('dingtalk_download.m3u8_utils.extract_live_uuid')
    @patch('dingtalk_download.m3u8_utils._validate_browser_type')
    def test_fetch_m3u8_links_retry(self, mock_validate, mock_extract, mock_get_logs, mock_process, mock_refresh):
        """测试重试机制"""
        from dingtalk_download.m3u8_utils import fetch_m3u8_links

        mock_extract.return_value = 'abc123'
        mock_get_logs.return_value = [{'level': 'INFO'}]
        mock_process.side_effect = [None, 'https://example.com/video.m3u8']

        browser_instance = Mock()
        result = fetch_m3u8_links(browser_instance, 'chrome', 'https://n.dingtalk.com/live?liveUuid=abc123')

        assert result == ['https://example.com/video.m3u8']
        assert mock_refresh.call_count == 1


class TestFetchM3u8ContentViaBrowser:
    """测试_fetch_m3u8_content_via_browser函数"""

    @patch('dingtalk_download.m3u8_utils.browser')
    def test_fetch_m3u8_content_success(self, mock_browser):
        """测试成功获取M3U8内容"""
        from dingtalk_download.m3u8_utils import _fetch_m3u8_content_via_browser

        mock_browser.browser.execute_script.return_value = '#EXTM3U\n#EXT-X-VERSION:3'

        result = _fetch_m3u8_content_via_browser('https://example.com/video.m3u8', {'Cookie': 'test'})

        assert result == '#EXTM3U\n#EXT-X-VERSION:3'

    @patch('dingtalk_download.m3u8_utils.browser')
    def test_fetch_m3u8_content_empty(self, mock_browser):
        """测试获取空内容"""
        from dingtalk_download.m3u8_utils import _fetch_m3u8_content_via_browser

        mock_browser.browser.execute_script.return_value = ''

        with pytest.raises(RuntimeError, match="下载的 M3U8 内容为空"):
            _fetch_m3u8_content_via_browser('https://example.com/video.m3u8', {'Cookie': 'test'})

    @patch('dingtalk_download.m3u8_utils.browser')
    def test_fetch_m3u8_content_error(self, mock_browser):
        """测试获取内容失败"""
        from dingtalk_download.m3u8_utils import _fetch_m3u8_content_via_browser

        mock_browser.browser.execute_script.side_effect = Exception("Fetch error")

        with pytest.raises(RuntimeError, match="获取 M3U8 内容失败"):
            _fetch_m3u8_content_via_browser('https://example.com/video.m3u8', {'Cookie': 'test'})


class TestDownloadM3u8File:
    """测试download_m3u8_file函数"""

    @patch('dingtalk_download.m3u8_utils._save_m3u8_content_to_file')
    @patch('dingtalk_download.m3u8_utils._fetch_m3u8_content_via_browser')
    @patch('dingtalk_download.m3u8_utils._ensure_directory_exists')
    @patch('dingtalk_download.m3u8_utils._validate_m3u8_download_parameters')
    def test_download_m3u8_file_success(self, mock_validate, mock_ensure, mock_fetch, mock_save):
        """测试成功下载M3U8文件"""
        from dingtalk_download.m3u8_utils import download_m3u8_file

        mock_fetch.return_value = '#EXTM3U\n#EXT-X-VERSION:3'

        result = download_m3u8_file('https://example.com/video.m3u8', 'output.m3u8', {'Cookie': 'test'})

        assert result == 'output.m3u8'

    @patch('dingtalk_download.m3u8_utils._validate_m3u8_download_parameters')
    def test_download_m3u8_file_invalid_params(self, mock_validate):
        """测试无效参数"""
        from dingtalk_download.m3u8_utils import download_m3u8_file

        mock_validate.side_effect = ValueError("Invalid parameters")

        with pytest.raises(ValueError, match="Invalid parameters"):
            download_m3u8_file('', 'output.m3u8', {})
