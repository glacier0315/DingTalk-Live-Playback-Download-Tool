"""
钉钉直播回放下载工具 - 依赖工厂模块

本模块负责创建和管理各种依赖实例，实现依赖注入和工厂模式。

作者：项目团队
依赖：logging
创建日期：2026-01-28
修改历史：
    - 2026-01-28: 初始版本，实现依赖工厂模式
"""

import logging
from typing import Dict
from .cookie_handler import CookieHandler
from .m3u8_parser import M3u8Parser
from .m3u8_download_service import M3u8DownloadService
from ..utils.path_selector import PathSelector
from ..binary.n_m3u8dl_re import NM3u8DLRE

logger = logging.getLogger(__name__)


class DependencyFactory:
    """
    依赖工厂类。

    负责创建和管理各种依赖实例，使用单例模式确保相同参数返回相同实例。

    Attributes:
        _instances: 实例缓存字典
    """

    def __init__(self):
        """初始化依赖工厂。"""
        self._instances: Dict[str, object] = {}
        logger.debug("依赖工厂初始化完成")

    def get_cookie_handler(self, browser_type: str) -> CookieHandler:
        """
        获取Cookie处理器实例。

        Args:
            browser_type: 浏览器类型（edge/chrome/firefox）

        Returns:
            CookieHandler: Cookie处理器实例
        """
        key = f"cookie_handler_{browser_type}"
        if key not in self._instances:
            self._instances[key] = CookieHandler(browser_type)
            logger.debug(f"创建Cookie处理器实例 - 浏览器类型: {browser_type}")
        return self._instances[key]

    def get_m3u8_parser(self, browser_driver) -> M3u8Parser:
        """
        获取m3u8解析器实例。

        Args:
            browser_driver: 浏览器驱动实例

        Returns:
            M3u8Parser: m3u8解析器实例
        """
        key = f"m3u8_parser_{id(browser_driver)}"
        if key not in self._instances:
            self._instances[key] = M3u8Parser(browser_driver)
            logger.debug(f"创建m3u8解析器实例 - 浏览器驱动ID: {id(browser_driver)}")
        return self._instances[key]

    def get_path_selector(self, save_mode: str) -> PathSelector:
        """
        获取路径选择器实例。

        Args:
            save_mode: 保存模式（1：默认路径，2：手动选择）

        Returns:
            PathSelector: 路径选择器实例
        """
        key = f"path_selector_{save_mode}"
        if key not in self._instances:
            self._instances[key] = PathSelector(save_mode)
            logger.debug(f"创建路径选择器实例 - 保存模式: {save_mode}")
        return self._instances[key]

    def get_n_m3u8dl_re(self) -> NM3u8DLRE:
        """
        获取NM3u8DLRE实例。

        Returns:
            NM3u8DLRE: NM3u8DLRE实例
        """
        key = "n_m3u8dl_re"
        if key not in self._instances:
            self._instances[key] = NM3u8DLRE()
            logger.debug("创建NM3u8DLRE实例")
        return self._instances[key]

    def get_m3u8_download_service(self, m3u8_parser: M3u8Parser) -> M3u8DownloadService:
        """
        获取m3u8下载服务实例。

        Args:
            m3u8_parser: m3u8解析器实例

        Returns:
            M3u8DownloadService: m3u8下载服务实例
        """
        key = f"m3u8_download_service_{id(m3u8_parser)}"
        if key not in self._instances:
            self._instances[key] = M3u8DownloadService(m3u8_parser)
            logger.debug(f"创建m3u8下载服务实例 - 解析器ID: {id(m3u8_parser)}")
        return self._instances[key]

    def clear_instances(self) -> None:
        """
        清除所有缓存的实例。

        用于测试或需要重新创建实例的场景。
        """
        self._instances.clear()
        logger.debug("清除所有缓存的依赖实例")

    def get_instance_count(self) -> int:
        """
        获取当前缓存的实例数量。

        Returns:
            int: 实例数量
        """
        return len(self._instances)
