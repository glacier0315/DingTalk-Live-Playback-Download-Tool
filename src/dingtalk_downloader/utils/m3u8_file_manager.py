"""
钉钉直播回放下载工具 - M3U8文件管理模块

本模块负责统一管理m3u8文件的存储路径和动态文件名生成。

作者：项目团队
依赖：uuid, os, logging, typing
创建日期：2026-01-22
修改历史：
    - 2026-01-22: 初始版本，实现m3u8文件路径管理和动态文件名生成
"""

import os
import uuid
import logging
from typing import Optional
from ..config.yaml_config import YamlConfig
from ..utils.path_helper import ensure_dir_exists

logger = logging.getLogger(__name__)


class M3u8FileManager:
    """
    M3U8文件管理器，负责统一管理m3u8文件的存储路径和动态文件名生成。

    该类提供m3u8文件路径的获取、验证、自动创建目录和动态文件名生成功能。

    Attributes:
        config (YamlConfig): 配置管理实例
        temp_dir (str): m3u8临时文件目录
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        初始化M3U8文件管理器。

        Args:
            config_file: 配置文件路径，默认为None（使用默认路径）
        """
        self.config = YamlConfig(config_file)
        self.config.load()
        self.temp_dir = self._resolve_temp_dir()

        # 确保临时目录存在
        self._ensure_temp_dir_exists()

        logger.debug("M3U8文件管理器初始化完成")
        logger.debug(f"临时目录: {self.temp_dir}")

    def _resolve_temp_dir(self) -> str:
        """
        解析临时目录路径。

        支持绝对路径和相对路径，相对路径相对于项目根目录。

        Returns:
            解析后的临时目录路径
        """
        temp_dir_config = self.config.get("download.temp_dir", "temp")

        if os.path.isabs(temp_dir_config):
            return temp_dir_config
        else:
            return os.path.join(os.getcwd(), temp_dir_config)

    def _ensure_temp_dir_exists(self) -> None:
        """
        确保临时目录存在。

        如果目录不存在，则自动创建完整的目录结构。
        """
        try:
            ensure_dir_exists(self.temp_dir)
            logger.debug(f"临时目录已就绪: {self.temp_dir}")
        except Exception as e:
            logger.error(f"创建临时目录失败: {e}")
            raise

    def generate_filename(self, prefix: Optional[str] = None) -> str:
        """
        生成基于UUID的动态文件名。

        Args:
            prefix: 文件名前缀，默认为None

        Returns:
            生成的文件名，格式为"{prefix}{uuid}.m3u8"或"{uuid}.m3u8"
        """
        unique_id = str(uuid.uuid4())

        if prefix:
            filename = f"{prefix}_{unique_id}.m3u8"
        else:
            filename = f"{unique_id}.m3u8"

        logger.debug(f"生成文件名: {filename}")
        return filename

    def get_temp_file_path(self, filename: Optional[str] = None) -> str:
        """
        获取临时文件的完整路径。

        Args:
            filename: 文件名，如果为None则自动生成

        Returns:
            临时文件的完整路径
        """
        if filename is None:
            filename = self.generate_filename()

        file_path = os.path.join(self.temp_dir, filename)
        logger.debug(f"临时文件路径: {file_path}")
        return file_path

    def get_temp_dir(self) -> str:
        """
        获取临时目录路径。

        Returns:
            临时目录路径
        """
        return self.temp_dir

    def _resolve_path(self, path: str) -> str:
        """
        解析路径。

        支持绝对路径和相对路径。

        Args:
            path: 路径字符串

        Returns:
            解析后的路径
        """
        if os.path.isabs(path):
            return path
        else:
            return os.path.join(os.getcwd(), path)
