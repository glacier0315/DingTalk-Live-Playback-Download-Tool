"""
钉钉直播回放下载工具 - m3u8下载服务模块

本模块负责m3u8文件的下载逻辑。

作者：项目团队
依赖：logging
创建日期：2026-01-26
修改历史：
    - 2026-01-26: 初始版本，从Downloader类中提取m3u8下载逻辑
"""

import os
import logging
from .m3u8_parser import M3u8Parser
from ..utils.models import M3u8Link
from .exceptions import DownloadError
from ..utils.m3u8_file_manager import M3u8FileManager

logger = logging.getLogger(__name__)


class M3u8DownloadService:
    """
    m3u8下载服务类。

    负责获取和下载m3u8文件。

    Attributes:
        m3u8_parser: m3u8解析器
        m3u8_file_manager: m3u8文件管理器
    """

    def __init__(self, m3u8_parser: M3u8Parser):
        """
        初始化m3u8下载服务。

        Args:
            m3u8_parser: m3u8解析器实例
        """
        self.m3u8_parser = m3u8_parser
        self.m3u8_file_manager = M3u8FileManager()
        logger.debug("m3u8下载服务初始化完成")

    def fetch_and_download_m3u8(
        self,
        url: str,
        m3u8_headers: dict,
    ) -> M3u8Link:
        """
        获取并下载m3u8文件。
        下载完成后自动清理临时文件。

        Args:
            url: 钉钉直播回放分享链接
            m3u8_headers: 请求头字典

        Returns:
            M3u8Link: m3u8链接对象，包含URL和本地文件路径

        Raises:
            DownloadError: 获取或下载失败时
        """
        m3u8_link = self.m3u8_parser.fetch_m3u8_link(url)
        logger.info(f"获取到 m3u8 链接: {m3u8_link}")

        m3u8_file = self.m3u8_file_manager.get_temp_file_path()
        logger.debug(f"准备下载 m3u8 文件到: {m3u8_file}")

        try:
            m3u8_file = self.m3u8_parser.download_m3u8_file(m3u8_link, m3u8_file, m3u8_headers)

            if not m3u8_file or not os.path.exists(m3u8_file):
                raise DownloadError(f"m3u8 文件下载失败或文件不存在: {m3u8_file}")

            file_size = os.path.getsize(m3u8_file)
            logger.debug(f"m3u8 文件大小: {file_size} bytes")

        except Exception as e:
            logger.error(f"下载 m3u8 文件时发生错误: {e}", exc_info=True)
            raise DownloadError(f"下载 m3u8 文件失败: {e}") from e

        prefix = self.m3u8_parser.extract_prefix(m3u8_link)
        logger.info(f"提取到基础 URL: {prefix}")

        return M3u8Link(url=m3u8_link, prefix=prefix, local_file_path=m3u8_file)

    def cleanup_temp_file(self, file_path: str) -> None:
        """
        清理临时m3u8文件。

        Args:
            file_path: 临时文件路径
        """
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"已清理临时文件: {file_path}")
        except Exception as e:
            logger.warning(f"清理临时文件失败: {file_path}, 错误: {e}")
