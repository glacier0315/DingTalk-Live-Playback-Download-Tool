"""
FFmpegWrapper 单元测试
"""

import pytest
from unittest.mock import patch, Mock
from dingtalk_downloader.binary.ffmpeg_wrapper import FFmpegWrapper


class TestFFmpegWrapperInit:
    """测试 FFmpegWrapper 初始化"""

    def test_init_default_path(self):
        """测试使用默认路径初始化"""
        wrapper = FFmpegWrapper()
        assert wrapper.executable_path == "ffmpeg"

    def test_init_custom_path(self):
        """测试使用自定义路径初始化"""
        custom_path = "/path/to/ffmpeg"
        wrapper = FFmpegWrapper(executable_path=custom_path)
        assert wrapper.executable_path == custom_path


class TestFFmpegWrapperBuildCommand:
    """测试构建命令"""

    def test_build_command_basic(self):
        """测试构建基本命令"""
        wrapper = FFmpegWrapper()
        command = wrapper.build_command("input.mp4", "output.mp4", None)
        
        assert command == ["ffmpeg", "-i", "input.mp4", "output.mp4"]

    def test_build_command_with_options(self):
        """测试构建带选项的命令"""
        wrapper = FFmpegWrapper()
        options = ["-c:v", "libx264", "-c:a", "aac"]
        command = wrapper.build_command("input.mp4", "output.mp4", options)
        
        expected = ["ffmpeg", "-i", "input.mp4", "-c:v", "libx264", "-c:a", "aac", "output.mp4"]
        assert command == expected

    def test_build_command_empty_options(self):
        """测试空选项列表"""
        wrapper = FFmpegWrapper()
        command = wrapper.build_command("input.mp4", "output.mp4", [])
        
        assert command == ["ffmpeg", "-i", "input.mp4", "output.mp4"]

    def test_build_command_custom_executable(self):
        """测试自定义可执行文件路径"""
        wrapper = FFmpegWrapper(executable_path="/custom/path/ffmpeg")
        command = wrapper.build_command("input.mp4", "output.mp4", None)
        
        assert command == ["/custom/path/ffmpeg", "-i", "input.mp4", "output.mp4"]


class TestFFmpegWrapperConvert:
    """测试转换功能"""

    @patch('dingtalk_downloader.binary.ffmpeg_wrapper.subprocess.run')
    def test_convert_success(self, mock_run):
        """测试转换成功"""
        wrapper = FFmpegWrapper()
        result = wrapper.convert("input.mp4", "output.mp4", None)
        
        assert result is True
        mock_run.assert_called_once()

    @patch('dingtalk_downloader.binary.ffmpeg_wrapper.subprocess.run')
    def test_convert_with_options(self, mock_run):
        """测试带选项的转换"""
        wrapper = FFmpegWrapper()
        options = ["-c:v", "libx264"]
        result = wrapper.convert("input.mp4", "output.mp4", options)
        
        assert result is True
        mock_run.assert_called_once()
        
        call_args = mock_run.call_args[0][0]
        assert "-c:v" in call_args
        assert "libx264" in call_args

    @patch('dingtalk_downloader.binary.ffmpeg_wrapper.subprocess.run')
    def test_convert_failure(self, mock_run):
        """测试转换失败"""
        mock_run.side_effect = Exception("FFmpeg error")
        wrapper = FFmpegWrapper()
        result = wrapper.convert("input.mp4", "output.mp4", None)
        
        assert result is False

    @patch('dingtalk_downloader.binary.ffmpeg_wrapper.subprocess.run')
    def test_convert_with_custom_executable(self, mock_run):
        """测试使用自定义可执行文件转换"""
        wrapper = FFmpegWrapper(executable_path="/custom/path/ffmpeg")
        result = wrapper.convert("input.mp4", "output.mp4", None)
        
        assert result is True
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "/custom/path/ffmpeg"

    @patch('dingtalk_downloader.binary.ffmpeg_wrapper.subprocess.run')
    def test_convert_command_structure(self, mock_run):
        """测试转换命令结构"""
        wrapper = FFmpegWrapper()
        wrapper.convert("input.mp4", "output.mp4", None)
        
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "ffmpeg"
        assert "-i" in call_args
        assert "input.mp4" in call_args
        assert "output.mp4" in call_args


class TestFFmpegWrapperIntegration:
    """测试集成场景"""

    @patch('dingtalk_downloader.binary.ffmpeg_wrapper.subprocess.run')
    def test_full_workflow(self, mock_run):
        """测试完整工作流程"""
        wrapper = FFmpegWrapper(executable_path="/usr/bin/ffmpeg")
        
        command = wrapper.build_command("input.mp4", "output.mp4", ["-c:v", "libx264"])
        assert command[0] == "/usr/bin/ffmpeg"
        assert "-c:v" in command
        
        result = wrapper.convert("input.mp4", "output.mp4", ["-c:v", "libx264"])
        assert result is True
        mock_run.assert_called_once()

    @patch('dingtalk_downloader.binary.ffmpeg_wrapper.subprocess.run')
    def test_multiple_conversions(self, mock_run):
        """测试多次转换"""
        wrapper = FFmpegWrapper()
        
        result1 = wrapper.convert("input1.mp4", "output1.mp4", None)
        result2 = wrapper.convert("input2.mp4", "output2.mp4", None)
        result3 = wrapper.convert("input3.mp4", "output3.mp4", None)
        
        assert result1 is True
        assert result2 is True
        assert result3 is True
        assert mock_run.call_count == 3
