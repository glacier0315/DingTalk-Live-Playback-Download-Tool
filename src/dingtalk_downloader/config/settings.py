"""
钉钉直播回放下载工具 - 配置管理模块

本模块负责管理配置项。

作者：项目团队
依赖：无
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
"""

import os
import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class Settings:
    """
    配置类，负责管理配置项。

    该类提供配置项的加载、保存、获取和设置功能。

    Attributes:
        config (dict): 配置字典
        config_file (str): 配置文件路径
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置。

        Args:
            config_file: 配置文件路径，默认为 None（使用默认路径）
        """
        self.config = {}
        if config_file is None:
            config_dir = os.path.join(os.path.expanduser("~"), ".dingtalk_downloader")
            os.makedirs(config_dir, exist_ok=True)
            self.config_file = os.path.join(config_dir, "config.json")
        else:
            self.config_file = config_file
        self.load()

    def load(self) -> None:
        """
        加载配置。

        从配置文件中加载配置项，如果配置文件不存在，则使用默认配置。
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"加载配置文件失败: {e}", exc_info=True)
                self.config = {}
        else:
            self.config = {}

    def save(self) -> None:
        """
        保存配置。

        将配置项保存到配置文件。
        """
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except IOError as e:
            logger.error(f"保存配置文件失败: {e}", exc_info=True)

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项。

        Args:
            key: 配置项键
            default: 默认值

        Returns:
            配置项值，如果不存在则返回默认值
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        设置配置项。

        Args:
            key: 配置项键
            value: 配置项值
        """
        self.config[key] = value
        self.save()
