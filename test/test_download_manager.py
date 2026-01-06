"""测试 download_manager 模块。"""
import pytest
import os
import tempfile
import subprocess
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path

from dingtalk_download.download_manager import (
    auto_download_m3u8_with_options,
    download_m3u8_with_options,
    download_m3u8_with_reused_path,
    _validate_download_parameters,
    _build_cookie_header,
    _build_download_command,
    execute_download,
    DEFAULT_DOWNLOAD_DIR
)


class TestValidateDownloadParameters:
    """测试 _validate_download_parameters 函数"""

    def test_validate_all_valid_parameters(self):
        """测试所有参数都有效的情况"""
        with tempfile.TemporaryDirectory() as temp_dir:
            m3u8_file = os.path.join(temp_dir, 'test.m3u8')
            Path(m3u8_file).touch()
            
            _validate_download_parameters(m3u8_file, 'test_video', temp_dir)

    def test_validate_empty_m3u8_file(self):
        """测试空的 M3U8 文件路径"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(ValueError) as exc_info:
                _validate_download_parameters('', 'test_video', temp_dir)
            assert 'M3U8 文件路径不能为空' in str(exc_info.value)

    def test_validate_nonexistent_m3u8_file(self):
        """测试不存在的 M3U8 文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with pytest.raises(FileNotFoundError) as exc_info:
                _validate_download_parameters('nonexistent.m3u8', 'test_video', temp_dir)
            assert 'M3U8 文件不存在' in str(exc_info.value)

    def test_validate_empty_save_name(self):
        """测试空的保存文件名"""
        with tempfile.TemporaryDirectory() as temp_dir:
            m3u8_file = os.path.join(temp_dir, 'test.m3u8')
            Path(m3u8_file).touch()
            
            with pytest.raises(ValueError) as exc_info:
                _validate_download_parameters(m3u8_file, '', temp_dir)
            assert '保存文件名不能为空' in str(exc_info.value)

    def test_validate_empty_save_dir(self):
        """测试空的保存目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            m3u8_file = os.path.join(temp_dir, 'test.m3u8')
            Path(m3u8_file).touch()
            
            with pytest.raises(ValueError) as exc_info:
                _validate_download_parameters(m3u8_file, 'test_video', '')
            assert '保存目录不能为空' in str(exc_info.value)

    def test_validate_nonexistent_save_dir(self):
        """测试不存在的保存目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            m3u8_file = os.path.join(temp_dir, 'test.m3u8')
            Path(m3u8_file).touch()
            
            with pytest.raises(FileNotFoundError) as exc_info:
                _validate_download_parameters(m3u8_file, 'test_video', 'nonexistent_dir')
            assert '保存目录不存在' in str(exc_info.value)

    @pytest.mark.skipif(os.name == 'nt', reason="Windows 权限测试不可靠")
    def test_validate_readonly_save_dir(self):
        """测试只读的保存目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            m3u8_file = os.path.join(temp_dir, 'test.m3u8')
            Path(m3u8_file).touch()
            
            readonly_dir = os.path.join(temp_dir, 'readonly')
            os.makedirs(readonly_dir)
            
            try:
                os.chmod(readonly_dir, 0o444)
                
                with pytest.raises(PermissionError) as exc_info:
                    _validate_download_parameters(m3u8_file, 'test_video', readonly_dir)
                assert '保存目录不可写' in str(exc_info.value)
            finally:
                try:
                    os.chmod(readonly_dir, 0o755)
                except:
                    pass


class TestBuildCookieHeader:
    """测试 _build_cookie_header 函数"""

    def test_build_cookie_header_single_cookie(self):
        """测试构建单个 Cookie 请求头"""
        cookies = {'session_id': 'abc123'}
        result = _build_cookie_header(cookies)
        assert result == 'session_id=abc123'

    def test_build_cookie_header_multiple_cookies(self):
        """测试构建多个 Cookie 请求头"""
        cookies = {
            'session_id': 'abc123',
            'token': 'xyz789',
            'user': 'test'
        }
        result = _build_cookie_header(cookies)
        assert 'session_id=abc123' in result
        assert 'token=xyz789' in result
        assert 'user=test' in result
        assert result.count('; ') == 2

    def test_build_cookie_header_empty_cookies(self):
        """测试空的 Cookie 字典"""
        cookies = {}
        result = _build_cookie_header(cookies)
        assert result == ''


class TestBuildDownloadCommand:
    """测试 _build_download_command 函数"""

    @patch('dingtalk_download.utils.get_executable_name')
    def test_build_command_minimal(self, mock_get_executable):
        """测试构建最小下载命令"""
        mock_get_executable.return_value = 'N_m3u8DL-RE'
        
        command = _build_download_command(
            'test.m3u8',
            'my_video',
            '/videos',
            'https://example.com/',
            None,
            None
        )
        
        assert 'N_m3u8DL-RE' in command
        assert 'test.m3u8' in command
        assert '--save-name' in command
        assert 'my_video' in command
        assert '--save-dir' in command
        assert '/videos' in command
        assert '--base-url' in command
        assert 'https://example.com/' in command

    @patch('dingtalk_download.utils.get_executable_name')
    def test_build_command_with_cookies(self, mock_get_executable):
        """测试带 Cookie 的下载命令"""
        mock_get_executable.return_value = 'N_m3u8DL-RE'
        
        cookies = {'session_id': 'abc123', 'token': 'xyz789'}
        command = _build_download_command(
            'test.m3u8',
            'my_video',
            '/videos',
            'https://example.com/',
            cookies,
            None
        )
        
        assert any('Cookie:' in arg and 'session_id=abc123' in arg for arg in command)

    @patch('dingtalk_download.utils.get_executable_name')
    def test_build_command_with_custom_headers(self, mock_get_executable):
        """测试带自定义请求头的下载命令"""
        mock_get_executable.return_value = 'N_m3u8DL-RE'
        
        headers = {
            'User-Agent': 'Custom Agent',
            'Referer': 'https://custom.com',
            'Accept': 'application/json'
        }
        command = _build_download_command(
            'test.m3u8',
            'my_video',
            '/videos',
            'https://example.com/',
            None,
            headers
        )
        
        assert any('User-Agent: Custom Agent' in arg for arg in command)
        assert any('Referer: https://custom.com' in arg for arg in command)
        assert any('Accept: application/json' in arg for arg in command)

    @patch('dingtalk_download.utils.get_executable_name')
    def test_build_command_default_headers(self, mock_get_executable):
        """测试默认请求头"""
        mock_get_executable.return_value = 'N_m3u8DL-RE'
        
        command = _build_download_command(
            'test.m3u8',
            'my_video',
            '/videos',
            'https://example.com/',
            None,
            None
        )
        
        assert any('User-Agent:' in arg for arg in command)
        assert any('Referer:' in arg for arg in command)
        assert any('Accept:' in arg for arg in command)

    @patch('dingtalk_download.utils.get_executable_name')
    def test_build_command_with_all_supported_headers(self, mock_get_executable):
        """测试所有支持的请求头"""
        mock_get_executable.return_value = 'N_m3u8DL-RE'
        
        headers = {
            'User-Agent': 'Test Agent',
            'Referer': 'https://test.com',
            'Accept': 'text/html',
            'Accept-Language': 'en-US',
            'Accept-Encoding': 'gzip'
        }
        command = _build_download_command(
            'test.m3u8',
            'my_video',
            '/videos',
            'https://example.com/',
            None,
            headers
        )
        
        assert any('User-Agent: Test Agent' in arg for arg in command)
        assert any('Referer: https://test.com' in arg for arg in command)
        assert any('Accept: text/html' in arg for arg in command)
        assert any('Accept-Language: en-US' in arg for arg in command)
        assert any('Accept-Encoding: gzip' in arg for arg in command)


class TestExecuteDownload:
    """测试 execute_download 函数"""

    @patch('dingtalk_download.download_manager.subprocess.run')
    @patch('dingtalk_download.download_manager._validate_download_parameters')
    @patch('dingtalk_download.download_manager._build_download_command')
    def test_execute_download_success(self, mock_build_cmd, mock_validate, mock_subprocess):
        """测试下载成功"""
        mock_build_cmd.return_value = ['N_m3u8DL-RE', 'test.m3u8']
        mock_subprocess.return_value = Mock(stdout='Download complete', stderr='')
        
        with tempfile.TemporaryDirectory() as temp_dir:
            m3u8_file = os.path.join(temp_dir, 'test.m3u8')
            Path(m3u8_file).touch()
            
            result = execute_download(
                m3u8_file,
                'test_video',
                'https://example.com/',
                None,
                None,
                temp_dir
            )
            
            assert result == temp_dir
            mock_validate.assert_called_once()
            mock_build_cmd.assert_called_once()
            mock_subprocess.assert_called_once()

    @patch('dingtalk_download.download_manager.subprocess.run')
    @patch('dingtalk_download.download_manager._validate_download_parameters')
    @patch('dingtalk_download.download_manager._build_download_command')
    def test_execute_download_subprocess_error(self, mock_build_cmd, mock_validate, mock_subprocess):
        """测试子进程错误"""
        mock_build_cmd.return_value = ['N_m3u8DL-RE', 'test.m3u8']
        
        error = subprocess.CalledProcessError(1, 'N_m3u8DL-RE')
        error.stdout = 'Error output'
        error.stderr = 'Error message'
        mock_subprocess.side_effect = error
        
        with tempfile.TemporaryDirectory() as temp_dir:
            m3u8_file = os.path.join(temp_dir, 'test.m3u8')
            Path(m3u8_file).touch()
            
            with pytest.raises(RuntimeError) as exc_info:
                execute_download(
                    m3u8_file,
                    'test_video',
                    'https://example.com/',
                    None,
                    None,
                    temp_dir
                )
            assert '下载失败' in str(exc_info.value)

    @patch('dingtalk_download.download_manager.subprocess.run')
    @patch('dingtalk_download.download_manager._validate_download_parameters')
    @patch('dingtalk_download.download_manager._build_download_command')
    @patch('dingtalk_download.utils.get_executable_name')
    def test_execute_download_executable_not_found(self, mock_get_exec, mock_build_cmd, mock_validate, mock_subprocess):
        """测试可执行文件未找到"""
        mock_get_exec.return_value = 'N_m3u8DL-RE'
        mock_build_cmd.return_value = ['N_m3u8DL-RE', 'test.m3u8']
        mock_subprocess.side_effect = FileNotFoundError('Executable not found')
        
        with tempfile.TemporaryDirectory() as temp_dir:
            m3u8_file = os.path.join(temp_dir, 'test.m3u8')
            Path(m3u8_file).touch()
            
            with pytest.raises(RuntimeError) as exc_info:
                execute_download(
                    m3u8_file,
                    'test_video',
                    'https://example.com/',
                    None,
                    None,
                    temp_dir
                )
            assert '找不到可执行文件' in str(exc_info.value)

    @patch('dingtalk_download.download_manager.subprocess.run')
    @patch('dingtalk_download.download_manager._validate_download_parameters')
    @patch('dingtalk_download.download_manager._build_download_command')
    def test_execute_download_unknown_error(self, mock_build_cmd, mock_validate, mock_subprocess):
        """测试未知错误"""
        mock_build_cmd.return_value = ['N_m3u8DL-RE', 'test.m3u8']
        mock_subprocess.side_effect = Exception('Unknown error')
        
        with tempfile.TemporaryDirectory() as temp_dir:
            m3u8_file = os.path.join(temp_dir, 'test.m3u8')
            Path(m3u8_file).touch()
            
            with pytest.raises(RuntimeError) as exc_info:
                execute_download(
                    m3u8_file,
                    'test_video',
                    'https://example.com/',
                    None,
                    None,
                    temp_dir
                )
            assert '下载过程中发生未知错误' in str(exc_info.value)


class TestAutoDownloadM3u8WithOptions:
    """测试 auto_download_m3u8_with_options 函数"""

    @patch('dingtalk_download.download_manager.download_m3u8_with_options')
    def test_auto_download_creates_downloads_dir(self, mock_download):
        """测试自动下载创建 Downloads 目录"""
        mock_download.return_value = '/downloads'
        
        result = auto_download_m3u8_with_options(
            'test.m3u8',
            'test_video',
            'https://example.com/'
        )
        
        assert result == '/downloads'
        expected_dir = os.path.join(os.getcwd(), DEFAULT_DOWNLOAD_DIR)
        mock_download.assert_called_once_with(
            'test.m3u8',
            'test_video',
            'https://example.com/',
            None,
            None,
            expected_dir
        )

    @patch('dingtalk_download.download_manager.download_m3u8_with_options')
    def test_auto_download_with_cookies_and_headers(self, mock_download):
        """测试带 Cookie 和请求头的自动下载"""
        mock_download.return_value = '/downloads'
        
        cookies = {'session': 'abc123'}
        headers = {'User-Agent': 'Test Agent'}
        
        result = auto_download_m3u8_with_options(
            'test.m3u8',
            'test_video',
            'https://example.com/',
            cookies,
            headers
        )
        
        assert result == '/downloads'
        mock_download.assert_called_once()


class TestDownloadM3u8WithOptions:
    """测试 download_m3u8_with_options 函数"""

    @patch('dingtalk_download.download_manager.execute_download')
    @patch('dingtalk_download.download_manager.filedialog.askdirectory')
    @patch('dingtalk_download.download_manager.tk.Tk')
    def test_download_with_specified_dir(self, mock_tk, mock_filedialog, mock_execute):
        """测试指定保存目录的下载"""
        mock_execute.return_value = '/videos'
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        result = download_m3u8_with_options(
            'test.m3u8',
            'test_video',
            'https://example.com/',
            save_dir='/videos'
        )
        
        assert result == '/videos'
        mock_root.withdraw.assert_called_once()
        mock_filedialog.assert_not_called()
        mock_execute.assert_called_once_with(
            'test.m3u8',
            'test_video',
            'https://example.com/',
            None,
            None,
            '/videos'
        )

    @patch('dingtalk_download.download_manager.execute_download')
    @patch('dingtalk_download.download_manager.filedialog.askdirectory')
    @patch('dingtalk_download.download_manager.tk.Tk')
    def test_download_with_dialog(self, mock_tk, mock_filedialog, mock_execute):
        """测试通过对话框选择目录的下载"""
        mock_execute.return_value = '/selected'
        mock_filedialog.return_value = '/selected'
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        result = download_m3u8_with_options(
            'test.m3u8',
            'test_video',
            'https://example.com/'
        )
        
        assert result == '/selected'
        mock_root.withdraw.assert_called_once()
        mock_filedialog.assert_called_once_with(title="选择保存视频的目录")
        mock_execute.assert_called_once()

    @patch('dingtalk_download.download_manager.execute_download')
    @patch('dingtalk_download.download_manager.filedialog.askdirectory')
    @patch('dingtalk_download.download_manager.tk.Tk')
    def test_download_user_cancels(self, mock_tk, mock_filedialog, mock_execute):
        """测试用户取消选择目录"""
        mock_filedialog.return_value = ''
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        result = download_m3u8_with_options(
            'test.m3u8',
            'test_video',
            'https://example.com/'
        )
        
        assert result is None
        mock_execute.assert_not_called()

    @patch('dingtalk_download.download_manager.execute_download')
    @patch('dingtalk_download.download_manager.filedialog.askdirectory')
    @patch('dingtalk_download.download_manager.tk.Tk')
    def test_download_with_cookies_and_headers(self, mock_tk, mock_filedialog, mock_execute):
        """测试带 Cookie 和请求头的下载"""
        mock_execute.return_value = '/videos'
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        cookies = {'session': 'abc123'}
        headers = {'User-Agent': 'Test Agent'}
        
        result = download_m3u8_with_options(
            'test.m3u8',
            'test_video',
            'https://example.com/',
            cookies,
            headers,
            '/videos'
        )
        
        assert result == '/videos'
        mock_execute.assert_called_once()


class TestDownloadM3u8WithReusedPath:
    """测试 download_m3u8_with_reused_path 函数"""

    @patch('dingtalk_download.download_manager.execute_download')
    def test_download_with_reused_path(self, mock_execute):
        """测试使用复用路径的下载"""
        mock_execute.return_value = '/reused'
        
        result = download_m3u8_with_reused_path(
            'test.m3u8',
            'test_video',
            'https://example.com/',
            '/reused'
        )
        
        assert result == '/reused'
        mock_execute.assert_called_once_with(
            'test.m3u8',
            'test_video',
            'https://example.com/',
            None,
            None,
            '/reused'
        )

    @patch('dingtalk_download.download_manager.execute_download')
    @patch('dingtalk_download.download_manager.filedialog.askdirectory')
    @patch('dingtalk_download.download_manager.tk.Tk')
    def test_download_without_reused_path(self, mock_tk, mock_filedialog, mock_execute):
        """测试不使用复用路径的下载"""
        mock_execute.return_value = '/selected'
        mock_filedialog.return_value = '/selected'
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        result = download_m3u8_with_reused_path(
            'test.m3u8',
            'test_video',
            'https://example.com/',
            None
        )
        
        assert result == '/selected'
        mock_root.withdraw.assert_called_once()
        mock_filedialog.assert_called_once_with(title="选择保存视频的目录")
        mock_execute.assert_called_once()

    @patch('dingtalk_download.download_manager.execute_download')
    @patch('dingtalk_download.download_manager.filedialog.askdirectory')
    @patch('dingtalk_download.download_manager.tk.Tk')
    def test_download_without_reused_path_user_cancels(self, mock_tk, mock_filedialog, mock_execute):
        """测试不使用复用路径时用户取消"""
        mock_filedialog.return_value = ''
        mock_root = Mock()
        mock_tk.return_value = mock_root
        
        result = download_m3u8_with_reused_path(
            'test.m3u8',
            'test_video',
            'https://example.com/',
            None
        )
        
        assert result is None
        mock_execute.assert_not_called()

    @patch('dingtalk_download.download_manager.execute_download')
    def test_download_with_reused_path_and_options(self, mock_execute):
        """测试带选项的复用路径下载"""
        mock_execute.return_value = '/reused'
        
        cookies = {'session': 'abc123'}
        headers = {'User-Agent': 'Test Agent'}
        
        result = download_m3u8_with_reused_path(
            'test.m3u8',
            'test_video',
            'https://example.com/',
            '/reused',
            cookies,
            headers
        )
        
        assert result == '/reused'
        mock_execute.assert_called_once()
