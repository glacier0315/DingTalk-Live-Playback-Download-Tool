"""
钉钉直播回放下载工具 - YAML配置管理模块

本模块负责管理YAML格式的配置文件。

作者：项目团队
依赖：yaml, os, typing, logging
创建日期：2026-01-21
修改历史：
    - 2026-01-21: 初始版本
"""

import os
import yaml
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class YamlConfig:
    """
    YAML配置管理类，负责管理YAML格式的配置文件。

    该类提供配置项的加载、保存、获取和设置功能，支持嵌套配置。

    Attributes:
        config (dict): 配置字典
        config_file (str): 配置文件路径
        default_config (dict): 默认配置
        _loaded (bool): 配置是否已加载
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        初始化YamlConfig实例。

        Args:
            config_file: 配置文件路径，默认为None（使用默认路径）
        """
        self.config: Dict[str, Any] = {}
        self._loaded: bool = False

        if config_file is None:
            config_dir = os.path.join(os.path.expanduser("~"), ".dingtalk_downloader")
            os.makedirs(config_dir, exist_ok=True)
            self.config_file = os.path.join(config_dir, "config.yaml")
        else:
            self.config_file = config_file

        self.default_config = self._load_default_config()

    def load(self) -> None:
        """
        加载配置文件。

        从配置文件中加载配置项，如果配置文件不存在，则使用默认配置。
        """
        user_config = {}

        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    user_config = yaml.safe_load(f) or {}
                logger.info(f"配置文件加载成功: {self.config_file}")
            except yaml.YAMLError as e:
                logger.error(f"配置文件格式错误: {e}，使用默认配置")
                user_config = {}
            except IOError as e:
                logger.error(f"读取配置文件失败: {e}，使用默认配置")
                user_config = {}
        else:
            logger.warning(f"配置文件不存在: {self.config_file}，使用默认配置")

        self.config = self._merge_configs(user_config, self.default_config)
        self._loaded = True

    def save(self) -> None:
        """
        保存配置。

        将配置项保存到配置文件。
        """
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    self.config, f, allow_unicode=True, default_flow_style=False, sort_keys=False
                )
            logger.info(f"配置文件保存成功: {self.config_file}")
        except IOError as e:
            logger.error(f"保存配置文件失败: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项。

        Args:
            key: 配置项键，支持点号分隔的嵌套键（如"download.default_dir"）
            default: 默认值

        Returns:
            配置项值，如果不存在则返回默认值
        """
        if not self._loaded:
            self.load()

        keys = key.split(".")
        return self.get_nested(keys, default)

    def set(self, key: str, value: Any) -> None:
        """
        设置配置项。

        Args:
            key: 配置项键，支持点号分隔的嵌套键
            value: 配置项值
        """
        if not self._loaded:
            self.load()

        keys = key.split(".")
        self.set_nested(keys, value)
        self.save()

    def get_nested(self, keys: List[str], default: Any = None) -> Any:
        """
        获取嵌套配置项。

        Args:
            keys: 键列表
            default: 默认值

        Returns:
            配置项值，如果不存在则返回默认值
        """
        if not self._loaded:
            self.load()

        current = self.config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    def set_nested(self, keys: List[str], value: Any) -> None:
        """
        设置嵌套配置项。

        Args:
            keys: 键列表
            value: 配置项值
        """
        if not self._loaded:
            self.load()

        current = self.config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    def reload(self) -> None:
        """
        重新加载配置文件。

        清空当前配置，重新从文件加载。
        """
        self.config = {}
        self._loaded = False
        self.load()
        logger.info("配置文件重新加载成功")

    def validate(self) -> bool:
        """
        验证配置有效性。

        Returns:
            验证结果，True表示配置有效，False表示配置无效
        """
        if not self._loaded:
            self.load()

        try:
            if "app" not in self.config:
                logger.error("配置缺少app部分")
                return False

            if "download" not in self.config:
                logger.error("配置缺少download部分")
                return False

            if "browser" not in self.config:
                logger.error("配置缺少browser部分")
                return False

            if "logging" not in self.config:
                logger.error("配置缺少logging部分")
                return False

            logger.info("配置验证通过")
            return True
        except Exception as e:
            logger.error(f"配置验证失败: {e}")
            return False

    def _load_default_config(self) -> Dict[str, Any]:
        """
        加载默认配置。

        Returns:
            默认配置字典
        """
        return {
            "app": {
                "name": "钉钉直播回放下载工具",
                "version": "1.5.0",
            },
            "download": {
                "default_dir": "Downloads",
                "temp_m3u8_file": "output.m3u8",
                "max_retry_count": 5,
            },
            "browser": {
                "default_type": "edge",
                "headless": False,
                "timeout": 30,
            },
            "logging": {
                "level": "INFO",
                "dir": "logs",
                "max_bytes": 10485760,
                "backup_count": 5,
                "retention_days": 30,
            },
            "headers": {
                "user_agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                "referer": "https://n.dingtalk.com/",
                "accept": "application/vnd.apple.mpegurl, text/plain, */*",
                "accept_language": "zh-CN,zh;q=0.9,en;q=0.8",
                "accept_encoding": "gzip, deflate, br",
            },
            "n_m3u8dl_re": {
                "executable_path": "assets/bin/N_m3u8DL-RE.exe",
                "ui_language": "zh-CN",
            },
            "ffmpeg": {
                "executable_path": "assets/bin/ffmpeg.exe",
            },
        }

    def _merge_configs(
        self, user_config: Dict[str, Any], default_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        合并配置。

        将用户配置与默认配置合并，用户配置优先。

        Args:
            user_config: 用户配置
            default_config: 默认配置

        Returns:
            合并后的配置
        """
        merged = default_config.copy()

        for key, value in user_config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(value, merged[key])
            else:
                merged[key] = value

        return merged
