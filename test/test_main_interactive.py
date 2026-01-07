#!/usr/bin/env python3
"""测试主程序模块的交互式输入逻辑"""
import sys
import os
from unittest.mock import Mock, patch, MagicMock, call
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dingtalk_download.main import (
    single_mode,
    batch_mode,
    main,
    continue_download,
    repeat_process_links,
    BROWSER_TYPE_MAPPING,
    EXIT_COMMAND
)


class TestSingleMode:
    """测试单个视频下载模式"""

    @patch('builtins.input')
    @patch('dingtalk_download.main.get_browser_cookie')
    @patch('dingtalk_download.main._download_single_video')
    @patch('dingtalk_download.main.close_browser')
    def test_single_mode_success(self, mock_close, mock_download, mock_get_cookie, mock_input):
        """测试单个视频下载成功流程"""
        from dingtalk_download.main import single_mode

        mock_input.side_effect = [
            'https://n.dingtalk.com/live?liveUuid=abc123',
            '1',
            '1',
            'q'
        ]

        mock_browser = Mock()
        mock_get_cookie.return_value = (mock_browser, {'cookie': 'test'}, {'header': 'test'}, 'test_video')

        single_mode()

        assert mock_get_cookie.call_count == 1
        assert mock_download.call_count == 1
        assert mock_close.call_count == 1

    @patch('builtins.input')
    @patch('dingtalk_download.main.get_browser_cookie')
    @patch('dingtalk_download.main._download_single_video')
    @patch('dingtalk_download.main.close_browser')
    def test_single_mode_with_error(self, mock_close, mock_download, mock_get_cookie, mock_input):
        """测试单个视频下载错误处理"""
        from dingtalk_download.main import single_mode

        mock_input.side_effect = [
            'https://n.dingtalk.com/live?liveUuid=abc123',
            '1',
            '1',
            'q'
        ]

        mock_browser = Mock()
        mock_get_cookie.return_value = (mock_browser, {'cookie': 'test'}, {'header': 'test'}, 'test_video')
        mock_download.side_effect = Exception("Download failed")

        single_mode()

        assert mock_get_cookie.call_count == 1
        assert mock_download.call_count == 1
        assert mock_close.call_count == 1

    @patch('builtins.input')
    @patch('dingtalk_download.main.get_browser_cookie')
    @patch('dingtalk_download.main._download_single_video')
    @patch('dingtalk_download.main.close_browser')
    @patch('dingtalk_download.main.sys.exit')
    def test_single_mode_keyboard_interrupt(self, mock_exit, mock_close, mock_download, mock_get_cookie, mock_input):
        """测试 Ctrl+C 中断"""
        from dingtalk_download.main import single_mode
        from dingtalk_download import browser as browser_module

        mock_input.side_effect = [
            'https://n.dingtalk.com/live?liveUuid=abc123',
            '1',
            '1',
            KeyboardInterrupt()
        ]

        mock_browser = Mock()

        def mock_get_cookie_func(url, browser_type):
            browser_module.browser = mock_browser
            return (mock_browser, {'cookie': 'test'}, {'header': 'test'}, 'test_video')

        mock_get_cookie.side_effect = mock_get_cookie_func

        single_mode()

        assert mock_close.call_count == 1
        mock_exit.assert_called_once_with(0)

    @patch('builtins.input')
    @patch('dingtalk_download.main.get_browser_cookie')
    @patch('dingtalk_download.main._download_single_video')
    @patch('dingtalk_download.main.repeat_get_browser_cookie')
    @patch('dingtalk_download.main.close_browser')
    def test_single_mode_multiple_downloads(self, mock_close, mock_repeat_get, mock_download, mock_get_cookie, mock_input):
        """测试多个视频下载"""
        from dingtalk_download.main import single_mode

        mock_input.side_effect = [
            'https://n.dingtalk.com/live?liveUuid=abc123',
            '1',
            '1',
            'https://n.dingtalk.com/live?liveUuid=def456',
            'q'
        ]

        mock_browser = Mock()
        mock_get_cookie.return_value = (mock_browser, {'cookie': 'test'}, {'header': 'test'}, 'test_video')
        mock_repeat_get.return_value = ({'cookie': 'test2'}, {'header': 'test2'}, 'test_video2')

        single_mode()

        assert mock_get_cookie.call_count == 1
        assert mock_repeat_get.call_count == 1
        assert mock_download.call_count == 2
        assert mock_close.call_count == 1


class TestBatchMode:
    """测试批量下载模式"""

    @patch('builtins.input')
    @patch('dingtalk_download.main.read_links_file')
    @patch('dingtalk_download.main.get_browser_cookie')
    @patch('dingtalk_download.main._download_batch_video')
    @patch('dingtalk_download.main.continue_download')
    def test_batch_mode_success(self, mock_continue, mock_download, mock_get_cookie, mock_read, mock_input):
        """测试批量下载成功流程"""
        from dingtalk_download.main import batch_mode

        mock_input.side_effect = [
            'test_links.csv',
            '1',
            '1'
        ]

        mock_read.return_value = {
            0: 'https://n.dingtalk.com/live?liveUuid=abc123',
            1: 'https://n.dingtalk.com/live?liveUuid=def456'
        }

        mock_browser = Mock()
        mock_get_cookie.return_value = (mock_browser, {'cookie': 'test'}, {'header': 'test'}, 'test_video')
        mock_download.return_value = '/path/to/video.mp4'
        mock_continue.return_value = (False, '/path/to/video.mp4')

        batch_mode()

        assert mock_read.call_count == 1
        assert mock_get_cookie.call_count == 1
        assert mock_download.call_count == 2
        assert mock_continue.call_count == 1

    @patch('builtins.input')
    @patch('dingtalk_download.main.read_links_file')
    @patch('dingtalk_download.main.get_browser_cookie')
    @patch('dingtalk_download.main._download_batch_video')
    @patch('dingtalk_download.main.continue_download')
    def test_batch_mode_with_error(self, mock_continue, mock_download, mock_get_cookie, mock_read, mock_input):
        """测试批量下载错误处理"""
        from dingtalk_download.main import batch_mode

        mock_input.side_effect = [
            'test_links.csv',
            '1',
            '1'
        ]

        mock_read.return_value = {
            0: 'https://n.dingtalk.com/live?liveUuid=abc123',
            1: 'https://n.dingtalk.com/live?liveUuid=def456'
        }

        mock_browser = Mock()
        mock_get_cookie.return_value = (mock_browser, {'cookie': 'test'}, {'header': 'test'}, 'test_video')
        mock_download.side_effect = ['/path/to/video1.mp4', Exception("Download failed")]
        mock_continue.return_value = (False, '/path/to/video1.mp4')

        batch_mode()

        assert mock_read.call_count == 1
        assert mock_get_cookie.call_count == 1
        assert mock_download.call_count == 2
        assert mock_continue.call_count == 1

    @patch('builtins.input')
    @patch('dingtalk_download.main.read_links_file')
    @patch('dingtalk_download.main.get_browser_cookie')
    @patch('dingtalk_download.main._download_batch_video')
    @patch('dingtalk_download.main.continue_download')
    @patch('dingtalk_download.main.close_browser')
    @patch('dingtalk_download.main.sys.exit')
    def test_batch_mode_keyboard_interrupt(self, mock_exit, mock_close, mock_continue, mock_download, mock_get_cookie, mock_read, mock_input):
        """测试批量下载中断"""
        from dingtalk_download.main import batch_mode
        from dingtalk_download import browser as browser_module

        mock_input.side_effect = [
            'test_links.csv',
            '1',
            '1',
            KeyboardInterrupt()
        ]

        mock_read.return_value = {
            0: 'https://n.dingtalk.com/live?liveUuid=abc123'
        }

        mock_browser = Mock()

        def mock_get_cookie_func(url, browser_type):
            browser_module.browser = mock_browser
            return (mock_browser, {'cookie': 'test'}, {'header': 'test'}, 'test_video')

        mock_get_cookie.side_effect = mock_get_cookie_func
        mock_continue.return_value = (False, '/path/to/video.mp4')

        batch_mode()

        assert mock_close.call_count == 1
        mock_exit.assert_called_once_with(0)


class TestMainFunction:
    """测试主程序入口"""

    @patch('builtins.input')
    @patch('dingtalk_download.main.single_mode')
    def test_main_single_mode(self, mock_single_mode, mock_input):
        """测试主程序选择单个模式"""
        from dingtalk_download.main import main

        mock_input.return_value = '1'

        main()

        mock_single_mode.assert_called_once()

    @patch('builtins.input')
    @patch('dingtalk_download.main.batch_mode')
    def test_main_batch_mode(self, mock_batch_mode, mock_input):
        """测试主程序选择批量模式"""
        from dingtalk_download.main import main

        mock_input.return_value = '2'

        main()

        mock_batch_mode.assert_called_once()

    @patch('builtins.input')
    @patch('dingtalk_download.main.close_browser')
    @patch('dingtalk_download.main.sys.exit')
    def test_main_keyboard_interrupt(self, mock_exit, mock_close, mock_input):
        """测试主程序中断"""
        from dingtalk_download.main import main
        from dingtalk_download import browser as browser_module

        mock_input.side_effect = KeyboardInterrupt()

        mock_browser = Mock()
        with patch.object(browser_module, 'browser', mock_browser):
            main()

        assert mock_close.call_count == 0
        mock_exit.assert_called_once_with(0)


class TestContinueDownload:
    """测试继续下载逻辑"""

    @patch('builtins.input')
    @patch('dingtalk_download.main.read_links_file')
    @patch('dingtalk_download.main.repeat_process_links')
    @patch('dingtalk_download.main.close_browser')
    def test_continue_download_with_new_links(self, mock_close, mock_repeat, mock_read, mock_input):
        """测试继续下载新链接"""
        from dingtalk_download.main import continue_download

        mock_input.side_effect = [
            '',
            'new_links.csv'
        ]

        mock_read.return_value = {
            0: 'https://n.dingtalk.com/live?liveUuid=abc123'
        }

        mock_repeat.return_value = '/path/to/new_video.mp4'

        should_continue, saved_path = continue_download(None, Mock(), 'edge')

        assert should_continue is True
        assert saved_path == '/path/to/new_video.mp4'
        assert mock_read.call_count == 1
        assert mock_repeat.call_count == 1

    @patch('builtins.input')
    @patch('dingtalk_download.main.close_browser')
    def test_continue_download_exit(self, mock_close, mock_input):
        """测试退出继续下载"""
        from dingtalk_download.main import continue_download

        mock_input.return_value = 'q'

        should_continue, saved_path = continue_download('/path/to/video.mp4', Mock(), 'edge')

        assert should_continue is False
        assert saved_path == '/path/to/video.mp4'
        assert mock_close.call_count == 1

    @patch('builtins.input')
    @patch('dingtalk_download.main.read_links_file')
    @patch('dingtalk_download.main.close_browser')
    def test_continue_download_with_error(self, mock_close, mock_read, mock_input):
        """测试继续下载时发生错误"""
        from dingtalk_download.main import continue_download

        mock_input.side_effect = [
            '',
            'invalid_links.csv'
        ]

        mock_read.side_effect = Exception("File not found")

        should_continue, saved_path = continue_download('/path/to/video.mp4', Mock(), 'edge')

        assert should_continue is False
        assert saved_path == '/path/to/video.mp4'
        assert mock_close.call_count == 0


class TestRepeatProcessLinks:
    """测试重复处理链接"""

    @patch('dingtalk_download.main.repeat_get_browser_cookie')
    @patch('dingtalk_download.main.fetch_m3u8_links')
    @patch('dingtalk_download.main.download_m3u8_file')
    @patch('dingtalk_download.main.auto_download_m3u8_with_options')
    def test_repeat_process_links_success(self, mock_auto_download, mock_download_m3u8, mock_fetch, mock_get_cookie):
        """测试成功重复处理链接"""
        from dingtalk_download.main import repeat_process_links

        links_dict = {
            0: 'https://n.dingtalk.com/live?liveUuid=abc123',
            1: 'https://n.dingtalk.com/live?liveUuid=def456'
        }

        mock_get_cookie.return_value = ({'cookie': 'test'}, {'header': 'test'}, 'test_video')
        mock_fetch.return_value = ['https://example.com/video.m3u8']
        mock_download_m3u8.return_value = '/path/to/video.m3u8'
        mock_auto_download.return_value = '/path/to/video.mp4'

        saved_path = repeat_process_links(links_dict, Mock(), 'edge', '1')

        assert saved_path == '/path/to/video.mp4'
        assert mock_get_cookie.call_count == 2
        assert mock_fetch.call_count == 2
        assert mock_download_m3u8.call_count == 2
        assert mock_auto_download.call_count == 2

    def test_repeat_process_links_empty_dict(self):
        """测试空链接字典"""
        from dingtalk_download.main import repeat_process_links

        with pytest.raises(ValueError, match="链接字典不能为空"):
            repeat_process_links({}, Mock(), 'edge', '1')

    def test_repeat_process_links_invalid_save_mode(self):
        """测试无效的保存模式"""
        from dingtalk_download.main import repeat_process_links

        links_dict = {0: 'https://n.dingtalk.com/live?liveUuid=abc123'}

        with pytest.raises(ValueError, match="无效的保存模式"):
            repeat_process_links(links_dict, Mock(), 'edge', '3')

    @patch('dingtalk_download.main.repeat_get_browser_cookie')
    @patch('dingtalk_download.main.fetch_m3u8_links')
    def test_repeat_process_links_no_m3u8_links(self, mock_fetch, mock_get_cookie):
        """测试没有找到 M3U8 链接"""
        from dingtalk_download.main import repeat_process_links

        links_dict = {0: 'https://n.dingtalk.com/live?liveUuid=abc123'}

        mock_get_cookie.return_value = ({'cookie': 'test'}, {'header': 'test'}, 'test_video')
        mock_fetch.return_value = []

        saved_path = repeat_process_links(links_dict, Mock(), 'edge', '1')

        assert saved_path is None
        assert mock_get_cookie.call_count == 1
        assert mock_fetch.call_count == 1

    @patch('dingtalk_download.main.repeat_get_browser_cookie')
    @patch('dingtalk_download.main.fetch_m3u8_links')
    @patch('dingtalk_download.main.download_m3u8_file')
    def test_repeat_process_links_with_error(self, mock_download_m3u8, mock_fetch, mock_get_cookie):
        """测试处理链接时发生错误"""
        from dingtalk_download.main import repeat_process_links

        links_dict = {0: 'https://n.dingtalk.com/live?liveUuid=abc123'}

        mock_get_cookie.return_value = ({'cookie': 'test'}, {'header': 'test'}, 'test_video')
        mock_fetch.return_value = ['https://example.com/video.m3u8']
        mock_download_m3u8.side_effect = Exception("Download failed")

        with pytest.raises(RuntimeError, match="处理链接"):
            repeat_process_links(links_dict, Mock(), 'edge', '1')
