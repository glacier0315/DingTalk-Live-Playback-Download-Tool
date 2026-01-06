"""测试 main 模块。"""
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from io import StringIO
import sys

from dingtalk_download.main import (
    repeat_process_links,
    continue_download,
    _download_single_video,
    _download_batch_video,
    _print_welcome_message,
    APP_VERSION,
    BUILD_DATE,
    APP_NAME,
    DEFAULT_M3U8_FILENAME,
    BROWSER_TYPE_MAPPING,
    SEPARATOR_LINE,
    EXIT_COMMAND
)


class TestRepeatProcessLinks:
    """测试 repeat_process_links 函数"""

    @patch('dingtalk_download.main.repeat_get_browser_cookie')
    @patch('dingtalk_download.main.fetch_m3u8_links')
    @patch('dingtalk_download.main.download_m3u8_file')
    @patch('dingtalk_download.main.extract_prefix')
    @patch('dingtalk_download.main.auto_download_m3u8_with_options')
    def test_repeat_process_links_success_mode1(self, mock_auto_download, mock_extract, mock_download, mock_fetch, mock_cookie):
        """测试批量处理链接成功，保存模式1"""
        mock_cookie.return_value = ({'session': 'abc'}, {'User-Agent': 'Test'}, 'Live1')
        mock_fetch.return_value = ['https://example.com/video.m3u8']
        mock_download.return_value = 'video.m3u8'
        mock_extract.return_value = 'https://example.com/'
        mock_auto_download.return_value = '/downloads'

        links_dict = {0: 'https://n.dingtalk.com/live1'}
        browser_obj = Mock()

        result = repeat_process_links(links_dict, browser_obj, 'edge', '1')

        assert result == '/downloads'
        mock_cookie.assert_called_once_with('https://n.dingtalk.com/live1')
        mock_fetch.assert_called_once()
        mock_auto_download.assert_called_once()

    @patch('dingtalk_download.main.repeat_get_browser_cookie')
    @patch('dingtalk_download.main.fetch_m3u8_links')
    @patch('dingtalk_download.main.download_m3u8_file')
    @patch('dingtalk_download.main.extract_prefix')
    @patch('dingtalk_download.main.download_m3u8_with_reused_path')
    def test_repeat_process_links_success_mode2(self, mock_reused_download, mock_extract, mock_download, mock_fetch, mock_cookie):
        """测试批量处理链接成功，保存模式2"""
        mock_cookie.return_value = ({'session': 'abc'}, {'User-Agent': 'Test'}, 'Live1')
        mock_fetch.return_value = ['https://example.com/video.m3u8']
        mock_download.return_value = 'video.m3u8'
        mock_extract.return_value = 'https://example.com/'
        mock_reused_download.return_value = '/downloads'

        links_dict = {0: 'https://n.dingtalk.com/live1'}
        browser_obj = Mock()

        result = repeat_process_links(links_dict, browser_obj, 'edge', '2')

        assert result == '/downloads'
        mock_reused_download.assert_called_once()

    @patch('dingtalk_download.main.repeat_get_browser_cookie')
    @patch('dingtalk_download.main.fetch_m3u8_links')
    def test_repeat_process_links_no_m3u8_links(self, mock_fetch, mock_cookie):
        """测试批量处理链接，没有找到M3U8链接"""
        mock_cookie.return_value = ({'session': 'abc'}, {'User-Agent': 'Test'}, 'Live1')
        mock_fetch.return_value = []

        links_dict = {0: 'https://n.dingtalk.com/live1'}
        browser_obj = Mock()

        result = repeat_process_links(links_dict, browser_obj, 'edge', '1')

        assert result is None

    def test_repeat_process_links_empty_dict(self):
        """测试批量处理空链接字典"""
        with pytest.raises(ValueError) as exc_info:
            repeat_process_links({}, Mock(), 'edge', '1')
        assert '链接字典不能为空' in str(exc_info.value)

    def test_repeat_process_links_invalid_save_mode(self):
        """测试批量处理链接，无效的保存模式"""
        links_dict = {0: 'https://n.dingtalk.com/live1'}
        with pytest.raises(ValueError) as exc_info:
            repeat_process_links(links_dict, Mock(), 'edge', '3')
        assert '无效的保存模式' in str(exc_info.value)

    @patch('dingtalk_download.main.repeat_get_browser_cookie')
    @patch('dingtalk_download.main.fetch_m3u8_links')
    def test_repeat_process_links_error(self, mock_fetch, mock_cookie):
        """测试批量处理链接时发生错误"""
        mock_cookie.side_effect = Exception("Cookie error")

        links_dict = {0: 'https://n.dingtalk.com/live1'}
        browser_obj = Mock()

        with pytest.raises(RuntimeError) as exc_info:
            repeat_process_links(links_dict, browser_obj, 'edge', '1')
        assert '处理链接' in str(exc_info.value)


class TestContinueDownload:
    """测试 continue_download 函数"""

    @patch('dingtalk_download.main.close_browser')
    @patch('builtins.input')
    def test_continue_download_exit(self, mock_input, mock_close):
        """测试用户选择退出"""
        mock_input.return_value = 'q'

        should_continue, saved_path = continue_download('/old_path', Mock(), 'edge')

        assert should_continue is False
        assert saved_path == '/old_path'
        mock_close.assert_called_once()

    @patch('dingtalk_download.main.read_links_file')
    @patch('dingtalk_download.main.repeat_process_links')
    @patch('builtins.input')
    def test_continue_download_continue(self, mock_input, mock_repeat, mock_read):
        """测试用户选择继续"""
        mock_input.side_effect = ['', 'new_links.csv']
        mock_read.return_value = {0: 'https://n.dingtalk.com/live1'}
        mock_repeat.return_value = '/new_path'

        should_continue, saved_path = continue_download('/old_path', Mock(), 'edge')

        assert should_continue is True
        assert saved_path == '/new_path'
        mock_read.assert_called_once_with('new_links.csv')

    @patch('dingtalk_download.main.read_links_file')
    @patch('builtins.input')
    def test_continue_download_error(self, mock_input, mock_read):
        """测试继续下载时发生错误"""
        mock_input.side_effect = ['', 'invalid.csv']
        mock_read.side_effect = Exception("Read error")

        should_continue, saved_path = continue_download('/old_path', Mock(), 'edge')

        assert should_continue is False
        assert saved_path == '/old_path'


class TestDownloadSingleVideo:
    """测试 _download_single_video 函数"""

    @patch('dingtalk_download.main.fetch_m3u8_links')
    @patch('dingtalk_download.main.download_m3u8_file')
    @patch('dingtalk_download.main.extract_prefix')
    @patch('dingtalk_download.main.auto_download_m3u8_with_options')
    def test_download_single_video_success_mode1(self, mock_auto_download, mock_extract, mock_download, mock_fetch):
        """测试下载单个视频成功，保存模式1"""
        mock_fetch.return_value = ['https://example.com/video.m3u8']
        mock_download.return_value = 'video.m3u8'
        mock_extract.return_value = 'https://example.com/'
        mock_auto_download.return_value = '/downloads'

        browser_obj = Mock()
        cookies = {'session': 'abc'}
        headers = {'User-Agent': 'Test'}

        _download_single_video('https://n.dingtalk.com/live1', browser_obj, 'edge', '1', cookies, headers, 'Live1')

        mock_auto_download.assert_called_once()

    @patch('dingtalk_download.main.fetch_m3u8_links')
    @patch('dingtalk_download.main.download_m3u8_file')
    @patch('dingtalk_download.main.extract_prefix')
    @patch('dingtalk_download.main.download_m3u8_with_options')
    def test_download_single_video_success_mode2(self, mock_download_options, mock_extract, mock_download, mock_fetch):
        """测试下载单个视频成功，保存模式2"""
        mock_fetch.return_value = ['https://example.com/video.m3u8']
        mock_download.return_value = 'video.m3u8'
        mock_extract.return_value = 'https://example.com/'

        browser_obj = Mock()
        cookies = {'session': 'abc'}
        headers = {'User-Agent': 'Test'}

        _download_single_video('https://n.dingtalk.com/live1', browser_obj, 'edge', '2', cookies, headers, 'Live1')

        mock_download_options.assert_called_once()

    @patch('dingtalk_download.main.fetch_m3u8_links')
    def test_download_single_video_no_m3u8_links(self, mock_fetch):
        """测试下载单个视频，没有找到M3U8链接"""
        mock_fetch.return_value = []

        browser_obj = Mock()
        cookies = {'session': 'abc'}
        headers = {'User-Agent': 'Test'}

        _download_single_video('https://n.dingtalk.com/live1', browser_obj, 'edge', '1', cookies, headers, 'Live1')


class TestDownloadBatchVideo:
    """测试 _download_batch_video 函数"""

    @patch('dingtalk_download.main.repeat_get_browser_cookie')
    @patch('dingtalk_download.main.fetch_m3u8_links')
    @patch('dingtalk_download.main.download_m3u8_file')
    @patch('dingtalk_download.main.extract_prefix')
    @patch('dingtalk_download.main.auto_download_m3u8_with_options')
    def test_download_batch_video_success_mode1(self, mock_auto_download, mock_extract, mock_download, mock_fetch, mock_cookie):
        """测试批量下载单个视频成功，保存模式1"""
        mock_cookie.return_value = ({'session': 'abc'}, {'User-Agent': 'Test'}, 'Live1')
        mock_fetch.return_value = ['https://example.com/video.m3u8']
        mock_download.return_value = 'video.m3u8'
        mock_extract.return_value = 'https://example.com/'
        mock_auto_download.return_value = '/downloads'

        browser_obj = Mock()

        result = _download_batch_video('https://n.dingtalk.com/live1', browser_obj, 'edge', '1', None)

        assert result == '/downloads'
        mock_auto_download.assert_called_once()

    @patch('dingtalk_download.main.repeat_get_browser_cookie')
    @patch('dingtalk_download.main.fetch_m3u8_links')
    @patch('dingtalk_download.main.download_m3u8_file')
    @patch('dingtalk_download.main.extract_prefix')
    @patch('dingtalk_download.main.download_m3u8_with_reused_path')
    def test_download_batch_video_success_mode2(self, mock_reused_download, mock_extract, mock_download, mock_fetch, mock_cookie):
        """测试批量下载单个视频成功，保存模式2"""
        mock_cookie.return_value = ({'session': 'abc'}, {'User-Agent': 'Test'}, 'Live1')
        mock_fetch.return_value = ['https://example.com/video.m3u8']
        mock_download.return_value = 'video.m3u8'
        mock_extract.return_value = 'https://example.com/'
        mock_reused_download.return_value = '/downloads'

        browser_obj = Mock()

        result = _download_batch_video('https://n.dingtalk.com/live1', browser_obj, 'edge', '2', '/old_path')

        assert result == '/downloads'
        mock_reused_download.assert_called_once()

    @patch('dingtalk_download.main.repeat_get_browser_cookie')
    @patch('dingtalk_download.main.fetch_m3u8_links')
    def test_download_batch_video_no_m3u8_links(self, mock_fetch, mock_cookie):
        """测试批量下载单个视频，没有找到M3U8链接"""
        mock_cookie.return_value = ({'session': 'abc'}, {'User-Agent': 'Test'}, 'Live1')
        mock_fetch.return_value = []

        browser_obj = Mock()

        result = _download_batch_video('https://n.dingtalk.com/live1', browser_obj, 'edge', '1', None)

        assert result is None


class TestPrintWelcomeMessage:
    """测试 _print_welcome_message 函数"""

    @patch('builtins.print')
    def test_print_welcome_message(self, mock_print):
        """测试打印欢迎消息"""
        _print_welcome_message()

        assert mock_print.call_count == 4
        calls = mock_print.call_args_list
        
        assert '=' * 47 in str(calls[0])
        assert APP_NAME in str(calls[1])
        assert APP_VERSION in str(calls[1])
        assert BUILD_DATE in str(calls[2])
        assert '=' * 47 in str(calls[3])


class TestConstants:
    """测试常量定义"""

    def test_app_version(self):
        """测试应用版本常量"""
        assert APP_VERSION == "1.3"

    def test_build_date(self):
        """测试构建日期常量"""
        assert BUILD_DATE == "2024年12月18日"

    def test_app_name(self):
        """测试应用名称常量"""
        assert APP_NAME == "钉钉直播回放下载工具"

    def test_default_m3u8_filename(self):
        """测试默认M3U8文件名常量"""
        assert DEFAULT_M3U8_FILENAME == "output.m3u8"

    def test_browser_type_mapping(self):
        """测试浏览器类型映射常量"""
        assert BROWSER_TYPE_MAPPING == {
            '1': 'edge',
            '2': 'chrome',
            '3': 'firefox'
        }

    def test_separator_line(self):
        """测试分隔线常量"""
        assert SEPARATOR_LINE == '=' * 100

    def test_exit_command(self):
        """测试退出命令常量"""
        assert EXIT_COMMAND == 'q'
