"""
钉钉直播回放下载工具 - YAML配置管理模块

本模块负责管理YAML格式的配置文件。
采用单例模式确保配置文件在应用生命周期内仅被加载一次。
支持配置验证，确保配置值的有效性和完整性。

作者：项目团队
依赖：yaml, os, typing, logging, threading
创建日期：2026-01-21
修改历史：
    - 2026-01-21: 初始版本
    - 2026-01-21: 优化配置文件路径，使用CONFIG_FILE_PATH常量
    - 2026-01-25: 实现单例模式和线程安全，添加类型安全访问接口
    - 2026-01-25: 移除硬编码默认值，实现配置验证机制
"""

import os
import yaml
import logging
import threading
from typing import Any, Dict, List, Optional, TypeVar
from ..config.constants import CONFIG_FILE_PATH

logger = logging.getLogger(__name__)

T = TypeVar("T")

CONFIG_SCHEMA = {
    "app": {
        "required": True,
        "type": dict,
        "fields": {
            "name": {"required": True, "type": str},
            "version": {"required": True, "type": str},
            "build_date": {"required": True, "type": str},
        },
    },
    "download": {
        "required": True,
        "type": dict,
        "fields": {
            "default_dir": {"required": True, "type": str},
            "temp_dir": {"required": True, "type": str},
            "max_retry_count": {"required": True, "type": int, "min": 1, "max": 100},
        },
    },
    "browser": {
        "required": True,
        "type": dict,
        "fields": {
            "default_type": {
                "required": True,
                "type": str,
                "choices": ["edge", "chrome", "firefox"],
            },
            "headless": {"required": True, "type": bool},
            "timeout": {"required": True, "type": int, "min": 1, "max": 300},
        },
    },
    "logging": {
        "required": True,
        "type": dict,
        "fields": {
            "level": {
                "required": True,
                "type": str,
                "choices": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            },
            "dir": {"required": True, "type": str},
            "max_bytes": {"required": True, "type": int, "min": 1024},
            "backup_count": {"required": True, "type": int, "min": 1, "max": 100},
            "retention_days": {"required": True, "type": int, "min": 1, "max": 365},
        },
    },
    "headers": {
        "required": True,
        "type": dict,
        "fields": {
            "user_agent": {"required": True, "type": str},
            "referer": {"required": True, "type": str},
            "accept": {"required": True, "type": str},
            "accept_language": {"required": True, "type": str},
            "accept_encoding": {"required": True, "type": str},
            "connection": {"required": True, "type": str},
            "sec_fetch_dest": {"required": True, "type": str},
            "sec_fetch_mode": {"required": True, "type": str},
            "sec_fetch_site": {"required": True, "type": str},
            "sec_fetch_user": {"required": True, "type": str},
            "upgrade_insecure_requests": {"required": True, "type": str},
        },
    },
    "n_m3u8dl_re": {
        "required": True,
        "type": dict,
        "fields": {
            "executable_path": {"required": True, "type": str},
            "ui_language": {"required": True, "type": str},
            "temp_dir": {"required": True, "type": str},
            "log_dir": {"required": True, "type": str},
        },
    },
    "ffmpeg": {
        "required": True,
        "type": dict,
        "fields": {
            "executable_path": {"required": True, "type": str},
        },
    },
}


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
    支持配置验证，确保配置值的有效性和完整性。

    Attributes:
        config (dict): 配置字典
        config_file (str): 配置文件路径
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
                    instance.load()
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

        logger.debug(f"YamlConfig初始化完成，配置文件路径: {self.config_file}")

    def load(self) -> None:
        """
        加载配置文件。

        从配置文件中加载配置项，如果配置文件不存在则抛出异常。
        加载完成后自动验证配置有效性。
        线程安全，确保只加载一次。
        """
        with self._lock:
            if self._loaded:
                logger.debug("配置已加载，跳过重复加载")
                return

            logger.info(f"开始加载配置文件: {self.config_file}")

            if not os.path.exists(self.config_file):
                error_msg = f"配置文件不存在: {self.config_file}"
                logger.error(error_msg)
                raise ConfigLoadError(error_msg)

            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config = yaml.safe_load(f) or {}
                logger.info(f"配置文件加载成功: {self.config_file}")
            except yaml.YAMLError as e:
                error_msg = f"配置文件格式错误: {e}"
                logger.error(error_msg)
                raise ConfigLoadError(error_msg) from e
            except IOError as e:
                error_msg = f"读取配置文件失败: {e}"
                logger.error(error_msg)
                raise ConfigLoadError(error_msg) from e

            self._validate_config(self.config, CONFIG_SCHEMA)

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
            raise ConfigValueError(f"配置值类型错误，bool不能转换为int: {key}", key)
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

    def _validate_config(
        self, config: Dict[str, Any], schema: Dict[str, Any], path: str = ""
    ) -> None:
        """
        验证配置是否符合schema定义。

        Args:
            config: 配置字典
            schema: 配置schema
            path: 当前配置路径（用于错误信息）

        Raises:
            ConfigValidationError: 必填项缺失
            ConfigValueError: 类型不匹配、值超出范围、值不在选项中
        """
        for key, field_schema in schema.items():
            current_path = f"{path}.{key}" if path else key

            if field_schema.get("required", False) and key not in config:
                raise ConfigValidationError(f"缺少必填配置项: {current_path}")

            if key not in config:
                continue

            value = config[key]

            expected_type = field_schema.get("type")
            if expected_type and not isinstance(value, expected_type):
                raise ConfigValueError(
                    f"配置项类型错误: {current_path}, 期望类型: "
                    f"{expected_type.__name__}, 实际类型: {type(value).__name__}",
                    current_path,
                )

            if "min" in field_schema and value < field_schema["min"]:
                raise ConfigValueError(
                    f"配置值过小: {current_path}, 最小值: {field_schema['min']}, 实际值: {value}",
                    current_path,
                )

            if "max" in field_schema and value > field_schema["max"]:
                raise ConfigValueError(
                    f"配置值过大: {current_path}, 最大值: {field_schema['max']}, 实际值: {value}",
                    current_path,
                )

            if "choices" in field_schema and value not in field_schema["choices"]:
                raise ConfigValueError(
                    f"配置值无效: {current_path}, 可选值: {field_schema['choices']}, 实际值: {value}",
                    current_path,
                )

            if "fields" in field_schema and isinstance(value, dict):
                self._validate_config(value, field_schema["fields"], current_path)

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
            验证结果，True表示配置有效

        Raises:
            ConfigValidationError: 配置验证失败
        """
        if not self._loaded:
            self.load()

        self._validate_config(self.config, CONFIG_SCHEMA)
        logger.info("配置验证通过")
        return True

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
