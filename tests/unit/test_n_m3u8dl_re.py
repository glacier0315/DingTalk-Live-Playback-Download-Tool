"""
N_m3u8DL_RE 单元测试
"""

import subprocess
import pytest
from unittest.mock import patch, Mock
from dingtalk_downloader.binary.n_m3u8dl_re import NM3u8DLRE


class TestNM3u8DLREInit:
    """测试 NM3u8DLRE 初始化"""

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_init_default_windows(self, mock_ensure, mock_config):
        """测试 Windows 系统默认初始化"""
        import os

        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            "n_m3u8dl_re.executable_path": os.path.join("assets", "bin", "N_m3u8DL-RE.exe"),
            "n_m3u8dl_re.temp_dir": "temp",
            "n_m3u8dl_re.log_dir": "logs",
            "n_m3u8dl_re.ui_language": "zh-CN",
        }.get(key, default)
        mock_config.return_value = mock_config_instance
        dl = NM3u8DLRE()

        assert dl.executable_path == os.path.join("assets", "bin", "N_m3u8DL-RE.exe")
        assert dl.temp_dir == "temp"
        assert dl.log_dir == "logs"

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_init_default_linux(self, mock_ensure, mock_config):
        """测试 Linux 系统默认初始化"""
        import os

        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            "n_m3u8dl_re.executable_path": os.path.join("assets", "bin", "N_m3u8DL-RE"),
            "n_m3u8dl_re.temp_dir": "temp",
            "n_m3u8dl_re.log_dir": "logs",
            "n_m3u8dl_re.ui_language": "zh-CN",
        }.get(key, default)
        mock_config.return_value = mock_config_instance
        dl = NM3u8DLRE()

        assert dl.executable_path == os.path.join("assets", "bin", "N_m3u8DL-RE")
        assert dl.temp_dir == "temp"
        assert dl.log_dir == "logs"

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_init_default_macos(self, mock_ensure, mock_config):
        """测试 macOS 系统默认初始化"""
        import os

        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            "n_m3u8dl_re.executable_path": os.path.join("assets", "bin", "N_m3u8DL-RE"),
            "n_m3u8dl_re.temp_dir": "temp",
            "n_m3u8dl_re.log_dir": "logs",
            "n_m3u8dl_re.ui_language": "zh-CN",
        }.get(key, default)
        mock_config.return_value = mock_config_instance
        dl = NM3u8DLRE()

        assert dl.executable_path == os.path.join("assets", "bin", "N_m3u8DL-RE")
        assert dl.temp_dir == "temp"
        assert dl.log_dir == "logs"

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_init_custom_path(self, mock_ensure, mock_config):
        """测试自定义路径初始化"""
        custom_path = "/path/to/N_m3u8DL-RE"
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        dl = NM3u8DLRE(executable_path=custom_path)
        assert dl.executable_path == custom_path
        assert dl.temp_dir == "temp"
        assert dl.log_dir == "logs"


class TestNM3u8DLREEnsureDirectoriesExist:
    """测试目录创建"""

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_ensure_directories_exist(self, mock_ensure, mock_config):
        """测试目录创建逻辑"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        assert mock_ensure.call_count == 2
        mock_ensure.assert_any_call("temp")
        mock_ensure.assert_any_call("logs")

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_ensure_directories_exist_failure(self, mock_ensure, mock_config):
        """测试目录创建失败"""
        mock_ensure.side_effect = Exception("无法创建目录")
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        with pytest.raises(Exception) as exc_info:
            NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        assert "无法创建目录" in str(exc_info.value)


class TestNM3u8DLREGetLogFilePath:
    """测试日志文件路径生成"""

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_get_log_file_path(self, mock_ensure, mock_config):
        """测试日志文件路径生成"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        log_path = dl._get_log_file_path()
        assert log_path.startswith("logs")
        assert "n_m3u8dl_re_" in log_path
        assert ".log" in log_path

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_get_log_file_path_unique(self, mock_ensure, mock_config):
        """测试日志文件路径唯一性"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        log_path1 = dl._get_log_file_path()
        import time

        time.sleep(1.0)
        log_path2 = dl._get_log_file_path()
        assert log_path1 != log_path2


class TestNM3u8DLREBuildCommand:
    """测试构建命令"""

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_build_command_basic(self, mock_ensure, mock_config):
        """测试构建基本命令"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        command = dl.build_command(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=None,
            headers=None,
        )

        assert "N_m3u8DL-RE.exe" in command
        assert "test.m3u8" in command
        assert "--save-name" in command
        assert "output" in command
        assert "--save-dir" in command
        assert "/downloads" in command
        assert "--base-url" in command
        assert "https://example.com" in command
        assert "--tmp-dir" in command
        assert "--log-file-path" in command

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_build_command_with_dirs(self, mock_ensure, mock_config):
        """测试构建包含目录参数的命令"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        command = dl.build_command(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=None,
            headers=None,
        )

        assert "--tmp-dir" in command
        assert "temp" in command
        assert "--log-file-path" in command
        assert any("n_m3u8dl_re_" in arg for arg in command)
        assert any(".log" in arg for arg in command)

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_build_command_with_cookies(self, mock_ensure, mock_config):
        """测试构建带 Cookie 的命令"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        cookies = {"session": "abc123", "token": "xyz789"}
        command = dl.build_command(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=cookies,
            headers=None,
        )

        assert any("Cookie:" in arg for arg in command)
        assert any("session=abc123" in arg for arg in command)
        assert any("token=xyz789" in arg for arg in command)

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_build_command_with_headers(self, mock_ensure, mock_config):
        """测试构建带请求头的命令"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://example.com",
            "Accept": "application/json",
            "Accept-Language": "zh-CN",
            "Accept-Encoding": "gzip",
        }
        command = dl.build_command(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=None,
            headers=headers,
        )

        assert any("User-Agent:" in arg for arg in command)
        assert any("Referer:" in arg for arg in command)
        assert any("Accept:" in arg for arg in command)
        assert any("Accept-Language:" in arg for arg in command)
        assert any("Accept-Encoding:" in arg for arg in command)

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_build_command_headers_no_user_agent(self, mock_ensure, mock_config):
        """测试请求头中缺少 User-Agent"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        headers = {"Referer": "https://example.com"}
        command = dl.build_command(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=None,
            headers=headers,
        )

        assert any("Referer:" in arg for arg in command)
        assert any(
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            in arg
            for arg in command
        )
        assert any(
            "Accept: application/vnd.apple.mpegurl, text/plain, */*" in arg for arg in command
        )

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_build_command_headers_no_referer(self, mock_ensure, mock_config):
        """测试请求头中缺少 Referer（使用默认值）"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        headers = {"User-Agent": "Mozilla/5.0"}
        command = dl.build_command(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=None,
            headers=headers,
        )

        assert any("User-Agent:" in arg for arg in command)
        assert any("Referer: https://n.dingtalk.com/" in arg for arg in command)

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_build_command_no_headers(self, mock_ensure, mock_config):
        """测试没有请求头（使用默认值）"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        command = dl.build_command(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=None,
            headers=None,
        )

        assert any("User-Agent:" in arg for arg in command)
        assert any("Referer:" in arg for arg in command)
        assert any("Accept:" in arg for arg in command)

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_build_command_with_all_params(self, mock_ensure, mock_config):
        """测试带所有参数的命令"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        cookies = {"session": "abc123"}
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://example.com",
            "Accept": "application/json",
        }
        command = dl.build_command(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=cookies,
            headers=headers,
        )

        assert "test.m3u8" in command
        assert any("Cookie:" in arg for arg in command)
        assert any("User-Agent:" in arg for arg in command)
        assert any("Referer:" in arg for arg in command)
        assert any("Accept:" in arg for arg in command)

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_build_command_custom_executable(self, mock_ensure, mock_config):
        """测试自定义可执行文件路径"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        dl = NM3u8DLRE(executable_path="/custom/path/N_m3u8DL-RE")
        command = dl.build_command(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=None,
            headers=None,
        )

        assert command[0] == "/custom/path/N_m3u8DL-RE"


class TestNM3u8DLREDownload:
    """测试下载功能"""

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run")
    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_download_success(self, mock_ensure, mock_config, mock_run):
        """测试下载成功"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="INFO: 下载成功", stderr=""
        )
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        result = dl.download(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=None,
            headers=None,
        )

        assert result is True
        mock_run.assert_called_once()

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run")
    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_download_with_cookies(self, mock_ensure, mock_config, mock_run):
        """测试带 Cookie 的下载"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="INFO: 下载成功", stderr=""
        )
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        cookies = {"session": "abc123"}
        result = dl.download(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=cookies,
            headers=None,
        )

        assert result is True
        mock_run.assert_called_once()

        call_args = mock_run.call_args[0][0]
        assert any("Cookie:" in arg for arg in call_args)

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run")
    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_download_with_headers(self, mock_ensure, mock_config, mock_run):
        """测试带请求头的下载"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="INFO: 下载成功", stderr=""
        )
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        headers = {"User-Agent": "Mozilla/5.0"}
        result = dl.download(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=None,
            headers=headers,
        )

        assert result is True
        mock_run.assert_called_once()

        call_args = mock_run.call_args[0][0]
        assert any("User-Agent:" in arg for arg in call_args)

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run")
    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_download_failure(self, mock_ensure, mock_config, mock_run):
        """测试下载失败"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        mock_run.side_effect = Exception("Download error")
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        result = dl.download(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=None,
            headers=None,
        )

        assert result is False

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run")
    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_download_command_structure(self, mock_ensure, mock_config, mock_run):
        """测试下载命令结构"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        dl.download(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=None,
            headers=None,
        )

        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "N_m3u8DL-RE.exe"
        assert "test.m3u8" in call_args
        assert "--ui-language" in call_args
        assert "zh-CN" in call_args


class TestNM3u8DLREIntegration:
    """测试集成场景"""

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run")
    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_full_workflow(self, mock_ensure, mock_config, mock_run):
        """测试完整工作流程"""
        import os

        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: {
            "n_m3u8dl_re.executable_path": os.path.join("assets", "bin", "N_m3u8DL-RE.exe"),
            "n_m3u8dl_re.temp_dir": "temp",
            "n_m3u8dl_re.log_dir": "logs",
            "n_m3u8dl_re.ui_language": "zh-CN",
        }.get(key, default)
        mock_config.return_value = mock_config_instance
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="INFO: 下载成功", stderr=""
        )
        dl = NM3u8DLRE()

        assert dl.executable_path == os.path.join("assets", "bin", "N_m3u8DL-RE.exe")

        command = dl.build_command(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data={"session": "abc123"},
            headers={"User-Agent": "Mozilla/5.0"},
        )

        assert "test.m3u8" in command
        assert any("Cookie:" in arg for arg in command)
        result = dl.download(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data={"session": "abc123"},
            headers={"User-Agent": "Mozilla/5.0"},
        )

        assert result is True
        mock_run.assert_called_once()

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run")
    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_multiple_downloads(self, mock_ensure, mock_config, mock_run):
        """测试多次下载"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="INFO: 下载成功", stderr=""
        )
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")

        result1 = dl.download("test1.m3u8", "output1", "/downloads", "https://example.com")
        result2 = dl.download("test2.m3u8", "output2", "/downloads", "https://example.com")
        result3 = dl.download("test3.m3u8", "output3", "/downloads", "https://example.com")

        assert result1 is True
        assert result2 is True
        assert result3 is True
        assert mock_run.call_count == 3


class TestNM3u8DLREDownloadStatus:
    """测试下载状态判断"""

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run")
    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_download_success_no_errors(self, mock_ensure, mock_config, mock_run):
        """测试下载成功，无错误"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="INFO: 下载成功", stderr=""
        )
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        result = dl.download(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=None,
            headers=None,
        )

        assert result is True
        assert mock_run.call_args[1]["capture_output"] is True
        assert mock_run.call_args[1]["text"] is True

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run")
    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_download_failure_nonzero_exit_code(self, mock_ensure, mock_config, mock_run):
        """测试下载失败，退出码非0"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr="ERROR: 下载失败"
        )
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        result = dl.download(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=None,
            headers=None,
        )

        assert result is False

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run")
    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_download_failure_error_in_output(self, mock_ensure, mock_config, mock_run):
        """测试下载失败，输出包含ERROR:"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="ERROR: 分片数量校验不通过, 共144个,已下载18.", stderr=""
        )
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        result = dl.download(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=None,
            headers=None,
        )

        assert result is False

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run")
    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_download_failure_failed_in_output(self, mock_ensure, mock_config, mock_run):
        """测试下载失败，输出包含Failed"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="ERROR: Failed", stderr=""
        )
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        result = dl.download(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=None,
            headers=None,
        )

        assert result is False

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run")
    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_download_failure_403_errors(self, mock_ensure, mock_config, mock_run):
        """测试下载失败，403错误"""
        output = """INFO: 开始下载
WARN: Response status code does not indicate success: 403 (Forbidden).
ERROR: 分片数量校验不通过, 共144个,已下载18.
ERROR: Failed"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=output, stderr=""
        )
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        result = dl.download(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=None,
            headers=None,
        )

        assert result is False

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run")
    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_download_success_with_warnings(self, mock_ensure, mock_config, mock_run):
        """测试下载成功，有WARN但无ERROR"""
        output = """INFO: 开始下载
WARN: 读取媒体信息...
INFO: 下载完成"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=output, stderr=""
        )
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        result = dl.download(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=None,
            headers=None,
        )

        assert result is True

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run")
    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_download_failure_exception(self, mock_ensure, mock_config, mock_run):
        """测试下载失败，抛出异常"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        mock_run.side_effect = Exception("下载过程中发生错误")
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        result = dl.download(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=None,
            headers=None,
        )

        assert result is False

    @patch("dingtalk_downloader.binary.n_m3u8dl_re.subprocess.run")
    @patch("dingtalk_downloader.binary.n_m3u8dl_re.YamlConfig")
    @patch("dingtalk_downloader.utils.path_helper.ensure_dir_exists")
    def test_download_capture_output(self, mock_ensure, mock_config, mock_run):
        """测试捕获输出"""
        mock_config_instance = Mock()
        mock_config_instance.get.side_effect = lambda key, default=None: default
        mock_config.return_value = mock_config_instance
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="INFO: 下载成功", stderr=""
        )
        dl = NM3u8DLRE(executable_path="N_m3u8DL-RE.exe")
        dl.download(
            m3u8_file="test.m3u8",
            save_name="output",
            save_dir="/downloads",
            prefix="https://example.com",
            cookies_data=None,
            headers=None,
        )

        assert mock_run.called
        call_kwargs = mock_run.call_args[1]
        assert "capture_output" in call_kwargs
        assert call_kwargs["capture_output"] is True
        assert "text" in call_kwargs
        assert call_kwargs["text"] is True
