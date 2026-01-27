"""
钉钉直播回放下载工具 - N_m3u8DL-RE 调用封装模块

本模块负责调用 N_m3u8DL-RE 工具下载 m3u8 视频流。

作者：项目团队
依赖：subprocess, platform
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2025-01-15: 添加日志记录
"""

import subprocess
import os
import logging
from typing import Dict, Optional, List
from ..config.yaml_config import YamlConfig
from ..config.header_manager import HeaderManager

logger = logging.getLogger(__name__)


class NM3u8DLRE:
    """
    N_m3u8DL-RE 调用类，负责调用 N_m3u8DL-RE 工具。

    该类封装了 N_m3u8DL-RE 工具的调用逻辑，提供统一的接口供上层模块使用。

    Attributes:
        executable_path (str): 可执行文件路径
        temp_dir (str): 临时文件目录
        log_dir (str): 日志文件目录
        header_manager (HeaderManager): 请求头管理器
    """

    def __init__(self, executable_path: Optional[str] = None):
        """
        初始化 N_m3u8DL-RE 调用器。

        Args:
            executable_path: 可执行文件路径，默认为 None（自动查找）
        """
        config = YamlConfig.get_instance()

        if executable_path is None:
            self.executable_path = config.get("n_m3u8dl_re.executable_path")
        else:
            self.executable_path = executable_path

        self.temp_dir = config.get("n_m3u8dl_re.temp_dir", "temp")
        self.log_dir = config.get("n_m3u8dl_re.log_dir", "logs")
        self.ui_language = config.get("n_m3u8dl_re.ui_language", "zh-CN")
        self.header_manager = HeaderManager()

        self._ensure_directories_exist()

        logger.debug("N_m3u8DL-RE 调用器初始化完成")
        logger.debug(f"可执行文件: {self.executable_path}")
        logger.debug(f"临时目录: {self.temp_dir}")
        logger.debug(f"日志目录: {self.log_dir}")

    def _ensure_directories_exist(self) -> None:
        """
        确保临时目录和日志目录存在。

        如果目录不存在，则自动创建。
        """
        from ..utils.path_helper import ensure_dir_exists

        try:
            ensure_dir_exists(self.temp_dir)
            logger.debug(f"临时目录已就绪: {self.temp_dir}")
        except Exception as e:
            logger.error(f"创建临时目录失败: {e}")
            raise

        try:
            ensure_dir_exists(self.log_dir)
            logger.debug(f"日志目录已就绪: {self.log_dir}")
        except Exception as e:
            logger.error(f"创建日志目录失败: {e}")
            raise

    def _get_log_file_path(self) -> str:
        """
        获取日志文件路径。

        使用时间戳确保日志文件唯一性。

        Returns:
            日志文件完整路径
        """
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_name = f"n_m3u8dl_re_{timestamp}.log"
        log_file_path = os.path.join(self.log_dir, log_file_name)
        return log_file_path

    def download(
        self,
        m3u8_file: str,
        save_name: str,
        save_dir: str,
        prefix: str,
        cookies_data: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        下载 m3u8 视频。

        构建下载命令并调用 N_m3u8DL-RE 工具。

        Args:
            m3u8_file: m3u8 文件路径
            save_name: 保存文件名
            save_dir: 保存目录
            prefix: 基础 URL
            cookies_data: Cookie 字典
            headers: 请求头字典

        Returns:
            下载是否成功

        Raises:
            Exception: 下载失败时
        """
        logger.info(f"开始下载视频 - 文件名: {save_name}, 保存目录: {save_dir}")

        try:
            command = self.build_command(
                m3u8_file, save_name, save_dir, prefix, cookies_data, headers
            )
            logger.debug(f"执行命令: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True)

            if result.returncode != 0:
                logger.error(f"视频下载失败 - 子进程退出码: {result.returncode}")
                return False

            output = result.stdout + result.stderr

            if "ERROR:" in output or "Failed" in output:
                error_lines = []
                for line in output.split("\n"):
                    if "ERROR:" in line or "Failed" in line:
                        error_lines.append(line.strip())
                error_info = "\n".join(error_lines)
                logger.error("视频下载失败")
                if error_info:
                    logger.error(f"错误信息:\n{error_info}")
                return False

            logger.info(f"视频下载成功完成。文件保存路径: {save_dir}")
            return True
        except Exception as e:
            logger.error(f"下载视频时发生错误: {e}", exc_info=True)
            return False

    def build_command(
        self,
        m3u8_file: str,
        save_name: str,
        save_dir: str,
        prefix: str,
        cookies_data: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        """
        构建下载命令。

        构建 N_m3u8DL-RE 下载命令，包括文件名、保存目录、基础 URL、Cookie、请求头、临时目录和日志文件路径。

        Args:
            m3u8_file: m3u8 文件路径
            save_name: 保存文件名
            save_dir: 保存目录
            prefix: 基础 URL
            cookies_data: Cookie 字典
            headers: 请求头字典

        Returns:
            命令列表
        """
        command = [
            self.executable_path,
            m3u8_file,
            "--ui-language",
            self.ui_language,
            "--save-name",
            save_name,
            "--save-dir",
            save_dir,
            "--base-url",
            prefix,
            "--tmp-dir",
            self.temp_dir,
            "--log-file-path",
            self._get_log_file_path(),
        ]

        self._add_headers_to_command(command, headers, cookies_data)

        return command

    def _add_headers_to_command(
        self,
        command: List[str],
        headers: Optional[Dict[str, str]],
        cookies_data: Optional[Dict[str, str]],
    ) -> None:
        """
        添加请求头到命令。

        Args:
            command: 命令列表
            headers: 请求头字典
            cookies_data: Cookie 字典
        """

        if cookies_data:
            cookie_string = "; ".join(f"{name}={value}" for name, value in cookies_data.items())
            command.extend(["-H", f"Cookie: {cookie_string}"])
            logger.debug("已添加请求头，Cookie: ...")

        merged_headers = self.header_manager.get_headers()
        if headers:
            merged_headers.update(headers)

        for key, value in merged_headers.items():
            command.extend(["-H", f"{key}: {value}"])
            logger.debug(f"已添加请求头，{key}: {value}")
