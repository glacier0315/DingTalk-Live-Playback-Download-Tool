"""二进制工具Mock工具模块

提供二进制工具相关的Mock工具，用于测试FFmpeg、N_m3u8DL-RE等功能。
"""

from unittest.mock import MagicMock, Mock
from typing import Dict, List, Optional, Any, Union
from pathlib import Path


class MockFFmpegWrapper:
    """Mock FFmpeg包装器类"""

    def __init__(self, executable_path: str = "ffmpeg"):
        """初始化Mock FFmpeg包装器

        Args:
            executable_path: FFmpeg可执行文件路径
        """
        self.executable_path = executable_path
        self._is_available = True
        self._version = "5.0.0"
        self._convert_results = {}
        self._merge_results = {}
        self._extract_results = {}
        self._command_history = []

    def check_available(self) -> bool:
        """检查FFmpeg是否可用"""
        return self._is_available

    def get_version(self) -> str:
        """获取FFmpeg版本"""
        return self._version

    def convert(self, input_file: str, output_file: str, options: Dict[str, Any] = None) -> bool:
        """转换视频格式

        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            options: 转换选项

        Returns:
            是否成功
        """
        command = ["convert", input_file, output_file]
        if options:
            command.append(str(options))
        self._command_history.append(command)
        return self._convert_results.get(input_file, True)

    def merge(
        self, input_files: List[str], output_file: str, options: Dict[str, Any] = None
    ) -> bool:
        """合并视频文件

        Args:
            input_files: 输入文件列表
            output_file: 输出文件路径
            options: 合并选项

        Returns:
            是否成功
        """
        command = ["merge"] + input_files + [output_file]
        if options:
            command.append(str(options))
        self._command_history.append(command)
        return self._merge_results.get(tuple(input_files), True)

    def extract(self, input_file: str, output_file: str, options: Dict[str, Any] = None) -> bool:
        """提取视频片段

        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            options: 提取选项

        Returns:
            是否成功
        """
        command = ["extract", input_file, output_file]
        if options:
            command.append(str(options))
        self._command_history.append(command)
        return self._extract_results.get(input_file, True)

    def get_info(self, file_path: str) -> Dict[str, Any]:
        """获取视频文件信息

        Args:
            file_path: 文件路径

        Returns:
            视频信息字典
        """
        return {
            "duration": 3600,
            "width": 1920,
            "height": 1080,
            "fps": 30,
            "codec": "h264",
            "bitrate": 5000000,
            "audio_codec": "aac",
            "audio_bitrate": 128000,
        }

    def get_duration(self, file_path: str) -> float:
        """获取视频时长

        Args:
            file_path: 文件路径

        Returns:
            时长（秒）
        """
        return 3600.0

    def get_thumbnail(self, file_path: str, output_file: str, timestamp: float = 0) -> bool:
        """获取视频缩略图

        Args:
            file_path: 视频文件路径
            output_file: 输出文件路径
            timestamp: 时间戳（秒）

        Returns:
            是否成功
        """
        return True

    def crop(
        self, input_file: str, output_file: str, x: int, y: int, width: int, height: int
    ) -> bool:
        """裁剪视频

        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            x: 起始X坐标
            y: 起始Y坐标
            width: 宽度
            height: 高度

        Returns:
            是否成功
        """
        return True

    def resize(self, input_file: str, output_file: str, width: int, height: int) -> bool:
        """调整视频大小

        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            width: 宽度
            height: 高度

        Returns:
            是否成功
        """
        return True

    def add_watermark(
        self, input_file: str, watermark_file: str, output_file: str, options: Dict[str, Any] = None
    ) -> bool:
        """添加水印

        Args:
            input_file: 输入文件路径
            watermark_file: 水印文件路径
            output_file: 输出文件路径
            options: 水印选项

        Returns:
            是否成功
        """
        return True

    def set_volume(self, input_file: str, output_file: str, volume: float) -> bool:
        """设置音量

        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            volume: 音量（0-2）

        Returns:
            是否成功
        """
        return True

    def trim(self, input_file: str, output_file: str, start: float, end: float) -> bool:
        """裁剪视频时长

        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            start: 开始时间（秒）
            end: 结束时间（秒）

        Returns:
            是否成功
        """
        return True

    @property
    def command_history(self) -> List[List[str]]:
        """获取命令历史"""
        return self._command_history

    def set_convert_result(self, input_file: str, result: bool) -> None:
        """设置转换结果

        Args:
            input_file: 输入文件路径
            result: 结果
        """
        self._convert_results[input_file] = result

    def set_merge_result(self, input_files: List[str], result: bool) -> None:
        """设置合并结果

        Args:
            input_files: 输入文件列表
            result: 结果
        """
        self._merge_results[tuple(input_files)] = result

    def set_extract_result(self, input_file: str, result: bool) -> None:
        """设置提取结果

        Args:
            input_file: 输入文件路径
            result: 结果
        """
        self._extract_results[input_file] = result


class MockN_m3u8DL_RE:
    """Mock N_m3u8DL-RE工具类"""

    def __init__(self, executable_path: str = "N_m3u8DL-RE"):
        """初始化Mock N_m3u8DL-RE工具

        Args:
            executable_path: N_m3u8DL-RE可执行文件路径
        """
        self.executable_path = executable_path
        self._is_available = True
        self._version = "1.0.0"
        self._download_results = {}
        self._command_history = []

    def check_available(self) -> bool:
        """检查N_m3u8DL-RE是否可用"""
        return self._is_available

    def get_version(self) -> str:
        """获取N_m3u8DL-RE版本"""
        return self._version

    def download(self, url: str, output_file: str, options: Dict[str, Any] = None) -> bool:
        """下载M3U8视频

        Args:
            url: M3U8 URL
            output_file: 输出文件路径
            options: 下载选项

        Returns:
            是否成功
        """
        command = ["download", url, output_file]
        if options:
            command.append(str(options))
        self._command_history.append(command)
        return self._download_results.get(url, True)

    def download_with_headers(
        self, url: str, output_file: str, headers: Dict[str, str], options: Dict[str, Any] = None
    ) -> bool:
        """使用HTTP头下载M3U8视频

        Args:
            url: M3U8 URL
            output_file: 输出文件路径
            headers: HTTP头
            options: 下载选项

        Returns:
            是否成功
        """
        command = ["download", url, output_file, "headers", str(headers)]
        if options:
            command.append(str(options))
        self._command_history.append(command)
        return self._download_results.get(url, True)

    def download_with_proxy(
        self, url: str, output_file: str, proxy: str, options: Dict[str, Any] = None
    ) -> bool:
        """使用代理下载M3U8视频

        Args:
            url: M3U8 URL
            output_file: 输出文件路径
            proxy: 代理地址
            options: 下载选项

        Returns:
            是否成功
        """
        command = ["download", url, output_file, "proxy", proxy]
        if options:
            command.append(str(options))
        self._command_history.append(command)
        return self._download_results.get(url, True)

    def download_with_key(
        self, url: str, output_file: str, key: str, iv: str, options: Dict[str, Any] = None
    ) -> bool:
        """使用解密密钥下载M3U8视频

        Args:
            url: M3U8 URL
            output_file: 输出文件路径
            key: 解密密钥
            iv: 初始化向量
            options: 下载选项

        Returns:
            是否成功
        """
        command = ["download", url, output_file, "key", key, "iv", iv]
        if options:
            command.append(str(options))
        self._command_history.append(command)
        return self._download_results.get(url, True)

    def get_info(self, url: str) -> Dict[str, Any]:
        """获取M3U8信息

        Args:
            url: M3U8 URL

        Returns:
            M3U8信息字典
        """
        return {
            "url": url,
            "duration": 3600,
            "segments": 360,
            "bandwidth": 5000000,
            "resolution": "1920x1080",
            "codec": "h264",
            "audio_codec": "aac",
        }

    def parse_m3u8(self, url: str) -> Dict[str, Any]:
        """解析M3U8文件

        Args:
            url: M3U8 URL

        Returns:
            解析结果字典
        """
        return {
            "url": url,
            "segments": [
                "https://example.com/segment1.ts",
                "https://example.com/segment2.ts",
                "https://example.com/segment3.ts",
            ],
            "base_url": "https://example.com/",
            "duration": 30,
        }

    def get_segments(self, url: str) -> List[str]:
        """获取M3U8片段列表

        Args:
            url: M3U8 URL

        Returns:
            片段URL列表
        """
        return [
            "https://example.com/segment1.ts",
            "https://example.com/segment2.ts",
            "https://example.com/segment3.ts",
        ]

    def download_segment(self, segment_url: str, output_file: str) -> bool:
        """下载单个片段

        Args:
            segment_url: 片段URL
            output_file: 输出文件路径

        Returns:
            是否成功
        """
        return True

    def merge_segments(self, segment_files: List[str], output_file: str) -> bool:
        """合并片段

        Args:
            segment_files: 片段文件列表
            output_file: 输出文件路径

        Returns:
            是否成功
        """
        return True

    @property
    def command_history(self) -> List[List[str]]:
        """获取命令历史"""
        return self._command_history

    def set_download_result(self, url: str, result: bool) -> None:
        """设置下载结果

        Args:
            url: URL
            result: 结果
        """
        self._download_results[url] = result


class MockBinaryTool:
    """Mock通用二进制工具类"""

    def __init__(self, name: str, executable_path: str = None):
        """初始化Mock二进制工具

        Args:
            name: 工具名称
            executable_path: 可执行文件路径
        """
        self.name = name
        self.executable_path = executable_path or name
        self._is_available = True
        self._version = "1.0.0"
        self._command_results = {}
        self._command_history = []

    def check_available(self) -> bool:
        """检查工具是否可用"""
        return self._is_available

    def get_version(self) -> str:
        """获取工具版本"""
        return self._version

    def execute(self, command: List[str], options: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行命令

        Args:
            command: 命令列表
            options: 选项

        Returns:
            执行结果字典
        """
        self._command_history.append(command)
        return {"success": True, "stdout": "", "stderr": "", "returncode": 0}

    def execute_with_output(self, command: List[str], options: Dict[str, Any] = None) -> str:
        """执行命令并获取输出

        Args:
            command: 命令列表
            options: 选项

        Returns:
            标准输出
        """
        self._command_history.append(command)
        return ""

    def execute_with_returncode(self, command: List[str], options: Dict[str, Any] = None) -> int:
        """执行命令并获取返回码

        Args:
            command: 命令列表
            options: 选项

        Returns:
            返回码
        """
        self._command_history.append(command)
        return 0

    @property
    def command_history(self) -> List[List[str]]:
        """获取命令历史"""
        return self._command_history

    def set_command_result(self, command: str, result: Dict[str, Any]) -> None:
        """设置命令结果

        Args:
            command: 命令字符串
            result: 结果字典
        """
        self._command_results[command] = result


def create_mock_ffmpeg(executable_path: str = "ffmpeg") -> MockFFmpegWrapper:
    """创建Mock FFmpeg包装器

    Args:
        executable_path: FFmpeg可执行文件路径

    Returns:
        MockFFmpegWrapper实例
    """
    return MockFFmpegWrapper(executable_path)


def create_mock_n_m3u8dl_re(executable_path: str = "N_m3u8DL-RE") -> MockN_m3u8DL_RE:
    """创建Mock N_m3u8DL-RE工具

    Args:
        executable_path: N_m3u8DL-RE可执行文件路径

    Returns:
        MockN_m3u8DL_RE实例
    """
    return MockN_m3u8DL_RE(executable_path)


def create_mock_binary_tool(name: str, executable_path: str = None) -> MockBinaryTool:
    """创建Mock二进制工具

    Args:
        name: 工具名称
        executable_path: 可执行文件路径

    Returns:
        MockBinaryTool实例
    """
    return MockBinaryTool(name, executable_path)
