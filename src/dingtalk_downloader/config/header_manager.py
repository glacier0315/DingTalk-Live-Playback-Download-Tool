"""
钉钉直播回放下载工具 - 请求头管理模块

本模块负责统一管理请求头配置，支持动态覆盖机制。
使用YamlConfig单例模式确保配置只加载一次。

作者：项目团队
依赖：typing, logging
创建日期：2026-01-22
修改历史：
    - 2026-01-22: 初始版本，实现请求头配置加载与动态覆盖
    - 2026-01-25: 使用YamlConfig单例模式
"""

import logging
from typing import Dict, Optional
from .yaml_config import YamlConfig

logger = logging.getLogger(__name__)


class HeaderManager:
    """
    请求头管理器，负责统一管理请求头配置。

    该类提供请求头的加载、获取、覆盖功能，支持动态修改请求头配置。

    Attributes:
        config (YamlConfig): 配置管理实例
        _headers_cache (Dict[str, str]): 请求头缓存
        _override_headers (Dict[str, str]): 覆盖请求头
    """

    def __init__(self):
        """
        初始化请求头管理器。

        Args:
            config_file: 配置文件路径，默认为None（使用默认路径）
        """
        self.config = YamlConfig.get_instance()
        self._headers_cache: Dict[str, str] = {}
        self._override_headers: Dict[str, str] = {}

        # 初始化请求头缓存
        self._load_headers()

        logger.debug("请求头管理器初始化完成")

    def _load_headers(self) -> None:
        """
        从配置文件加载请求头到缓存。
        """
        try:
            # 配置文件中的请求头字段映射
            header_mapping = {
                "user_agent": "User-Agent",
                "referer": "Referer",
                "accept": "Accept",
                "accept_language": "Accept-Language",
                "accept_encoding": "Accept-Encoding",
                "connection": "Connection",
                "sec_fetch_dest": "Sec-Fetch-Dest",
                "sec_fetch_mode": "Sec-Fetch-Mode",
                "sec_fetch_site": "Sec-Fetch-Site",
                "sec_fetch_user": "Sec-Fetch-User",
                "upgrade_insecure_requests": "Upgrade-Insecure-Requests",
            }

            headers_config = self.config.get("headers", {})
            self._headers_cache.clear()

            for config_key, header_name in header_mapping.items():
                if config_key in headers_config:
                    self._headers_cache[header_name] = headers_config[config_key]
                    logger.debug(f"加载请求头: {header_name}")

            logger.debug(f"成功加载 {len(self._headers_cache)} 个请求头")

        except Exception as e:
            logger.error(f"加载请求头配置失败: {e}", exc_info=True)
            raise

    def get_headers(self, include_overrides: bool = True) -> Dict[str, str]:
        """
        获取请求头字典。

        Args:
            include_overrides: 是否包含覆盖的请求头，默认为True

        Returns:
            请求头字典
        """
        headers = self._headers_cache.copy()

        if include_overrides:
            # 应用覆盖的请求头（优先级更高）
            headers.update(self._override_headers)

        logger.debug(f"获取请求头字典，共 {len(headers)} 个请求头")
        return headers

    def get_header(
        self, name: str, default: Optional[str] = None, include_overrides: bool = True
    ) -> Optional[str]:
        """
        获取单个请求头。

        Args:
            name: 请求头名称
            default: 默认值
            include_overrides: 是否包含覆盖的请求头，默认为True

        Returns:
            请求头值，如果不存在则返回默认值
        """
        if include_overrides and name in self._override_headers:
            return self._override_headers[name]

        return self._headers_cache.get(name, default)

    def reload_config(self) -> None:
        """
        重新加载配置文件。

        清除当前缓存，重新从配置文件加载请求头。
        保留覆盖的请求头。
        """
        logger.info("重新加载请求头配置")
        self.config.reload()
        self._load_headers()
        logger.info("请求头配置重新加载完成")
