"""
钉钉直播回放下载工具 - FFmpeg 调用封装模块

本模块负责调用 FFmpeg 工具进行音视频处理。

作者：项目团队
依赖：subprocess
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
"""

import subprocess
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class FFmpegWrapper:
    """
    FFmpeg 调用类，负责调用 FFmpeg 工具。

    该类封装了 FFmpeg 工具的调用逻辑，提供统一的接口供上层模块使用。

    Attributes:
        executable_path (str): 可执行文件路径
    """

    def __init__(self, executable_path: Optional[str] = None):
        """
        初始化 FFmpeg 调用器。

        Args:
            executable_path: 可执行文件路径，默认为 None（使用默认路径）
        """
        import os
        import platform

        if executable_path is None:
            system = platform.system()
            if system == "Windows":
                self.executable_path = os.path.join("assets", "bin", "ffmpeg.exe")
            elif system == "Linux" or system == "Darwin":
                self.executable_path = os.path.join("assets", "bin", "ffmpeg")
            else:
                self.executable_path = "ffmpeg"
        else:
            self.executable_path = executable_path

    def convert(
        self, input_file: str, output_file: str, options: Optional[List[str]] = None
    ) -> bool:
        """
        转换音视频文件。

        构建转换命令并调用 FFmpeg 工具。

        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            options: FFmpeg 选项列表

        Returns:
            转换是否成功

        Raises:
            Exception: 转换失败时
        """
        try:
            command = self.build_command(input_file, output_file, options)
            subprocess.run(command)
            logger.info(f"音视频转换成功完成。输出文件: {output_file}")
            return True
        except Exception as e:
            logger.error(f"转换音视频时发生错误: {e}", exc_info=True)
            return False

    def build_command(
        self, input_file: str, output_file: str, options: Optional[List[str]] = None
    ) -> List[str]:
        """
        构建转换命令。

        构建 FFmpeg 转换命令。

        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            options: FFmpeg 选项列表

        Returns:
            命令列表
        """
        command = [self.executable_path, "-i", input_file]

        if options:
            command.extend(options)

        command.append(output_file)

        return command
