"""
钉钉直播回放下载工具 - YAML配置管理模块

本模块负责管理YAML格式的配置文件。
采用单例模式确保配置文件在应用生命周期内仅被加载一次。

作者：项目团队
依赖：yaml, os, typing, logging, threading
创建日期：2026-01-21
修改历史：
    - 2026-01-21: 初始版本
    - 2026-01-21: 优化配置文件路径，使用CONFIG_FILE_PATH常量
    - 2026-01-25: 实现单例模式和线程安全，添加类型安全访问接口
"""

import os
import yaml
import logging
import threading
from typing import Any, Dict, List, Optional, TypeVar, Type
from ..config.constants import CONFIG_FILE_PATH

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ConfigError(Exception):
    """配置异常基类"""

    def __init__(self, message: str, key: Optional[str] = None):
        """
        初始化配置异常

        Args:
            message: 错误信息
            key: 相关的配置键
        """
        self.message = message
        self.key = key
        if key:
            super().__init__(f"{message} (key: {key})")
        else:
            super().__init__(message)


class ConfigLoadError(ConfigError):
    """配置加载异常"""

    pass


class ConfigValueError(ConfigError):
    """配置值异常"""

    pass


class ConfigValidationError(ConfigError):
    """配置验证异常"""

    pass


class YamlConfig:
    """
    YAML配置管理类，负责管理YAML格式的配置文件。

    采用单例模式确保配置文件在应用生命周期内仅被加载一次。
    支持线程安全的并发访问。

    Attributes:
        config (dict): 配置字典
        config_file (str): 配置文件路径
        default_config (dict): 默认配置
        _loaded (bool): 配置是否已加载
        _lock (threading.RLock): 线程锁
        _instance (YamlConfig): 单例实例
    """

    _instance: Optional["YamlConfig"] = None
    _lock: threading.RLock = threading.RLock()

    def __new__(cls, config_file: Optional[str] = None) -> "YamlConfig":
        """
        单例模式实现，确保全局只有一个YamlConfig实例。

        Args:
            config_file: 配置文件路径，仅首次创建时有效

        Returns:
            YamlConfig单例实例
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._initialize(config_file)
                    cls._instance = instance
                    logger.debug("YamlConfig单例实例创建成功")
        return cls._instance

    def _initialize(self, config_file: Optional[str] = None) -> None:
        """
        初始化实例属性。

        Args:
            config_file: 配置文件路径
        """
        self.config: Dict[str, Any] = {}
        self._loaded: bool = False

        if config_file is None:
            self.config_file = CONFIG_FILE_PATH
        else:
            self.config_file = config_file

        self.default_config = self._load_default_config()
        logger.debug(f"YamlConfig初始化完成，配置文件路径: {self.config_file}")

    def load(self) -> None:
        """
        加载配置文件。

        从配置文件中加载配置项，如果配置文件不存在，则使用默认配置。
        如果配置文件不存在，则自动创建配置文件目录和默认配置文件。
        线程安全，确保只加载一次。
        """
        with self._lock:
            if self._loaded:
                logger.debug("配置已加载，跳过重复加载")
                return

            logger.info(f"开始加载配置文件: {self.config_file}")
            user_config = {}

            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, "r", encoding="utf-8") as f:
                        user_config = yaml.safe_load(f) or {}
                    logger.info(f"配置文件加载成功: {self.config_file}")
                except yaml.YAMLError as e:
                    error_msg = f"配置文件格式错误: {e}，使用默认配置"
                    logger.error(error_msg)
                    raise ConfigLoadError(error_msg) from e
                except IOError as e:
                    error_msg = f"读取配置文件失败: {e}，使用默认配置"
                    logger.error(error_msg)
                    raise ConfigLoadError(error_msg) from e
            else:
                logger.warning(f"配置文件不存在: {self.config_file}")
                logger.info(f"自动创建配置文件目录: {os.path.dirname(self.config_file)}")
                try:
                    os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                    logger.info("配置文件目录创建成功")
                except Exception as e:
                    error_msg = f"创建配置文件目录失败: {e}"
                    logger.error(error_msg)
                    raise ConfigLoadError(error_msg) from e

            self.config = self._merge_configs(user_config, self.default_config)
            self._loaded = True
            logger.info("配置加载完成")

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

    def get_str(self, key: str, default: str = "") -> str:
        """
        获取字符串类型配置项。

        Args:
            key: 配置项键
            default: 默认值

        Returns:
            字符串类型的配置项值

        Raises:
            ConfigValueError: 配置值不是字符串类型
        """
        value = self.get(key, default)
        if value is None:
            return default
        if not isinstance(value, str):
            raise ConfigValueError(f"配置值类型错误，期望str，实际{type(value).__name__}", key)
        return value

    def get_int(self, key: str, default: int = 0) -> int:
        """
        获取整数类型配置项。

        Args:
            key: 配置项键
            default: 默认值

        Returns:
            整数类型的配置项值

        Raises:
            ConfigValueError: 配置值不是整数类型
        """
        value = self.get(key, default)
        if value is None:
            return default
        if isinstance(value, bool):
            raise ConfigValueError(f"配置值类型错误，bool不能转换为int", key)
        try:
            return int(value)
        except (ValueError, TypeError) as e:
            raise ConfigValueError(f"配置值无法转换为int: {value}", key) from e

    def get_float(self, key: str, default: float = 0.0) -> float:
        """
        获取浮点数类型配置项。

        Args:
            key: 配置项键
            default: 默认值

        Returns:
            浮点数类型的配置项值

        Raises:
            ConfigValueError: 配置值不是浮点数类型
        """
        value = self.get(key, default)
        if value is None:
            return default
        try:
            return float(value)
        except (ValueError, TypeError) as e:
            raise ConfigValueError(f"配置值无法转换为float: {value}", key) from e

    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        获取布尔类型配置项。

        Args:
            key: 配置项键
            default: 默认值

        Returns:
            布尔类型的配置项值

        Raises:
            ConfigValueError: 配置值不是布尔类型
        """
        value = self.get(key, default)
        if value is None:
            return default
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.lower() in ("true", "1", "yes", "on"):
                return True
            if value.lower() in ("false", "0", "no", "off"):
                return False
        raise ConfigValueError(f"配置值无法转换为bool: {value}", key)

    def get_list(self, key: str, default: Optional[List[Any]] = None) -> List[Any]:
        """
        获取列表类型配置项。

        Args:
            key: 配置项键
            default: 默认值

        Returns:
            列表类型的配置项值

        Raises:
            ConfigValueError: 配置值不是列表类型
        """
        if default is None:
            default = []
        value = self.get(key, default)
        if value is None:
            return default
        if not isinstance(value, list):
            raise ConfigValueError(f"配置值类型错误，期望list，实际{type(value).__name__}", key)
        return value

    def get_dict(self, key: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        获取字典类型配置项。

        Args:
            key: 配置项键
            default: 默认值

        Returns:
            字典类型的配置项值

        Raises:
            ConfigValueError: 配置值不是字典类型
        """
        if default is None:
            default = {}
        value = self.get(key, default)
        if value is None:
            return default
        if not isinstance(value, dict):
            raise ConfigValueError(f"配置值类型错误，期望dict，实际{type(value).__name__}", key)
        return value

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

        with self._lock:
            current = self.config
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return default
            return current

    def reload(self) -> None:
        """
        重新加载配置文件。

        清空当前配置，重新从文件加载。
        线程安全。
        """
        with self._lock:
            logger.info("开始重新加载配置文件")
            self.config = {}
            self._loaded = False
            self.load()
            logger.info("配置文件重新加载成功")

    def validate(self) -> bool:
        """
        验证配置有效性。

        Returns:
            验证结果，True表示配置有效，False表示配置无效

        Raises:
            ConfigValidationError: 配置验证失败
        """
        if not self._loaded:
            self.load()

        try:
            required_sections = ["app", "download", "logging"]
            missing_sections = []

            for section in required_sections:
                if section not in self.config:
                    missing_sections.append(section)

            if missing_sections:
                error_msg = f"配置缺少必要部分: {', '.join(missing_sections)}"
                logger.error(error_msg)
                raise ConfigValidationError(error_msg)

            logger.info("配置验证通过")
            return True

        except ConfigValidationError:
            raise
        except Exception as e:
            error_msg = f"配置验证失败: {e}"
            logger.error(error_msg)
            raise ConfigValidationError(error_msg) from e

    @classmethod
    def get_instance(cls, config_file: Optional[str] = None) -> "YamlConfig":
        """
        获取YamlConfig单例实例。

        Args:
            config_file: 配置文件路径，仅首次创建时有效

        Returns:
            YamlConfig单例实例
        """
        return cls(config_file)

    @classmethod
    def reset_instance(cls) -> None:
        """
        重置单例实例。

        主要用于测试场景，清除当前单例实例。
        """
        with cls._lock:
            cls._instance = None
            logger.debug("YamlConfig单例实例已重置")

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
                "temp_dir": "temp",
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
                "connection": "keep-alive",
                "sec_fetch_dest": "document",
                "sec_fetch_mode": "navigate",
                "sec_fetch_site": "same-origin",
                "sec_fetch_user": "?1",
                "upgrade_insecure_requests": "1",
            },
            "n_m3u8dl_re": {
                "temp_dir": "temp",
                "log_dir": "logs",
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
