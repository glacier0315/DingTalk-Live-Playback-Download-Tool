"""
钉钉直播回放下载工具 - 配置管理模块

本模块负责管理配置项（向后兼容）。

作者：项目团队
依赖：无
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2026-01-21: 重构为使用YamlConfig
"""

import os
import json
import logging
from typing import Any, Optional
from .yaml_config import YamlConfig

logger = logging.getLogger(__name__)


class Settings:
    """
    配置类，负责管理配置项（向后兼容）。

    该类提供配置项的加载、保存、获取和设置功能，内部使用YamlConfig实现。

    Attributes:
        yaml_config (YamlConfig): YAML配置管理实例
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置。

        Args:
            config_file: 配置文件路径，默认为None（使用默认路径）
        """
        self.yaml_config = YamlConfig(config_file)
        self.load()

    def load(self) -> None:
        """
        加载配置。

        从配置文件中加载配置项，如果配置文件不存在，则使用默认配置。
        """
        self.yaml_config.load()

    def save(self) -> None:
        """
        保存配置。

        将配置项保存到配置文件。
        """
        self.yaml_config.save()

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项。

        Args:
            key: 配置项键
            default: 默认值

        Returns:
            配置项值，如果不存在则返回默认值
        """
        return self.yaml_config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        设置配置项。

        Args:
            key: 配置项键
            value: 配置项值
        """
        self.yaml_config.set(key, value)

    def migrate_from_json(self, json_file: str) -> None:
        """
        从JSON配置文件迁移到YAML。

        Args:
            json_file: JSON配置文件路径
        """
        if not os.path.exists(json_file):
            logger.warning(f"JSON配置文件不存在: {json_file}")
            return

        try:
            with open(json_file, "r", encoding="utf-8") as f:
                json_config = json.load(f)

            for key, value in json_config.items():
                self.yaml_config.set(key, value)

            logger.info(f"配置迁移成功: {json_file} -> {self.yaml_config.config_file}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON配置文件格式错误: {e}")
        except IOError as e:
            logger.error(f"读取JSON配置文件失败: {e}")
