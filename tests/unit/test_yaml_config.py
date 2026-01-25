"""
钉钉直播回放下载工具 - yaml_config 单元测试

本模块测试YAML配置管理模块。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2026-01-21
修改历史：
    - 2026-01-21: 初始版本
    - 2026-01-25: 添加单例模式、线程安全、类型安全访问接口测试
"""

import sys
import os
import yaml
import pytest
import tempfile
import threading
import time
from unittest.mock import patch, Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.config.yaml_config import (
    YamlConfig,
    ConfigError,
    ConfigLoadError,
    ConfigValueError,
    ConfigValidationError,
)


@pytest.fixture(autouse=True)
def reset_singleton():
    """每个测试前重置单例实例"""
    YamlConfig.reset_instance()
    yield
    YamlConfig.reset_instance()


def test_yaml_config_singleton():
    """测试单例模式"""
    config1 = YamlConfig()
    config2 = YamlConfig()

    assert config1 is config2
    assert id(config1) == id(config2)


def test_yaml_config_get_instance():
    """测试get_instance方法"""
    config1 = YamlConfig.get_instance()
    config2 = YamlConfig.get_instance()

    assert config1 is config2


def test_yaml_config_reset_instance():
    """测试reset_instance方法"""
    config1 = YamlConfig()
    YamlConfig.reset_instance()
    config2 = YamlConfig()

    assert config1 is not config2


def test_yaml_config_init_default_path():
    """测试YamlConfig初始化 - 使用默认路径"""
    config = YamlConfig()

    assert config.config == {}
    assert "config" in config.config_file
    assert "app.yaml" in config.config_file
    assert config._loaded is False


def test_yaml_config_init_custom_path():
    """测试YamlConfig初始化 - 使用自定义路径"""
    custom_path = "/custom/config.yaml"
    config = YamlConfig(config_file=custom_path)

    assert config.config == {}
    assert config.config_file == custom_path
    assert config._loaded is False


def test_yaml_config_load_existing_file():
    """测试加载配置 - 文件存在"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "test"}, "download": {"default_dir": "test_dir"}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)
        config.load()

        assert config.config["app"]["name"] == "test"
        assert config.config["download"]["default_dir"] == "test_dir"
        assert config._loaded is True
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_load_nonexistent_file():
    """测试加载配置 - 文件不存在"""
    non_existent_path = "/non/existent/config.yaml"
    config = YamlConfig(config_file=non_existent_path)
    config.load()

    assert config._loaded is True
    assert "app" in config.config
    assert "download" in config.config


def test_yaml_config_load_invalid_yaml():
    """测试加载配置 - 无效的YAML"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("invalid yaml content: [")

        config = YamlConfig(config_file=path)

        with pytest.raises(ConfigLoadError):
            config.load()
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_load_io_error():
    """测试加载配置 - IO错误"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("test: value")

        with patch("builtins.open", side_effect=IOError("Permission denied")):
            config = YamlConfig(config_file=path)

            with pytest.raises(ConfigLoadError):
                config.load()
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_existing_key():
    """测试获取配置项 - 键存在"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "test_app"}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        assert config.get("app.name") == "test_app"
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_nonexistent_key():
    """测试获取配置项 - 键不存在"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "test_app"}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        assert config.get("nonexistent") is None
        assert config.get("nonexistent", "default") == "default"
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_nested():
    """测试获取嵌套配置项"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {
            "app": {"name": "test_app"},
            "download": {"default_dir": "test_dir"},
        }
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        assert config.get("download.default_dir") == "test_dir"
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_str():
    """测试获取字符串类型配置项"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "test_app"}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        assert config.get_str("app.name") == "test_app"
        assert config.get_str("nonexistent") == ""
        assert config.get_str("nonexistent", "default") == "default"
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_str_type_error():
    """测试获取字符串类型配置项 - 类型错误"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"count": 123}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        with pytest.raises(ConfigValueError):
            config.get_str("app.count")
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_int():
    """测试获取整数类型配置项"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"count": 123}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        assert config.get_int("app.count") == 123
        assert config.get_int("nonexistent") == 0
        assert config.get_int("nonexistent", 10) == 10
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_int_from_string():
    """测试从字符串获取整数"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"count": "456"}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        assert config.get_int("app.count") == 456
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_int_type_error():
    """测试获取整数类型配置项 - 类型错误"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "test"}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        with pytest.raises(ConfigValueError):
            config.get_int("app.name")
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_float():
    """测试获取浮点数类型配置项"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"ratio": 3.14}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        assert config.get_float("app.ratio") == 3.14
        assert config.get_float("nonexistent") == 0.0
        assert config.get_float("nonexistent", 1.5) == 1.5
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_float_from_string():
    """测试从字符串获取浮点数"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"ratio": "2.71"}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        assert config.get_float("app.ratio") == 2.71
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_bool():
    """测试获取布尔类型配置项"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"enabled": True, "disabled": False}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        assert config.get_bool("app.enabled") is True
        assert config.get_bool("app.disabled") is False
        assert config.get_bool("nonexistent") is False
        assert config.get_bool("nonexistent", True) is True
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_bool_from_string():
    """测试从字符串获取布尔值"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {
            "app": {
                "true1": "true",
                "true2": "1",
                "true3": "yes",
                "true4": "on",
                "false1": "false",
                "false2": "0",
                "false3": "no",
                "false4": "off",
            }
        }
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        assert config.get_bool("app.true1") is True
        assert config.get_bool("app.true2") is True
        assert config.get_bool("app.true3") is True
        assert config.get_bool("app.true4") is True
        assert config.get_bool("app.false1") is False
        assert config.get_bool("app.false2") is False
        assert config.get_bool("app.false3") is False
        assert config.get_bool("app.false4") is False
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_bool_type_error():
    """测试获取布尔类型配置项 - 类型错误"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "test"}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        with pytest.raises(ConfigValueError):
            config.get_bool("app.name")
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_list():
    """测试获取列表类型配置项"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"items": [1, 2, 3]}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        assert config.get_list("app.items") == [1, 2, 3]
        assert config.get_list("nonexistent") == []
        assert config.get_list("nonexistent", [4, 5]) == [4, 5]
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_list_type_error():
    """测试获取列表类型配置项 - 类型错误"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "test"}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        with pytest.raises(ConfigValueError):
            config.get_list("app.name")
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_dict():
    """测试获取字典类型配置项"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"settings": {"key1": "value1", "key2": "value2"}}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        assert config.get_dict("app.settings") == {"key1": "value1", "key2": "value2"}
        assert config.get_dict("nonexistent") == {}
        assert config.get_dict("nonexistent", {"key": "value"}) == {"key": "value"}
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_dict_type_error():
    """测试获取字典类型配置项 - 类型错误"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "test"}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        with pytest.raises(ConfigValueError):
            config.get_dict("app.name")
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_nested_method():
    """测试get_nested方法"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "test_app"}, "download": {"default_dir": "test_dir"}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        assert config.get_nested(["app", "name"]) == "test_app"
        assert config.get_nested(["download", "default_dir"]) == "test_dir"
        assert config.get_nested(["nonexistent"], "default") == "default"
    finally:
        if os.path.exists(path):
            os.unlink(path)

def test_yaml_config_reload():
    """测试重新加载配置"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "test_app"}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)
        config.load()

        assert config.config["app"]["name"] == "test_app"

        updated_config = {"app": {"name": "updated_app"}}
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(updated_config, f)

        config.reload()

        assert config.config["app"]["name"] == "updated_app"
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_validate():
    """测试配置验证"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {
            "app": {"name": "test"},
            "download": {"default_dir": "test_dir"},
            "browser": {"default_type": "edge"},
            "logging": {"level": "INFO"},
        }
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)
        config.load()

        assert config.validate() is True
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_validate_invalid():
    """测试配置验证 - 无效配置"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {
            "app": {"name": "test"},
        }
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)
        config.load()

        # 手动删除必需的配置部分以触发验证失败
        del config.config["download"]
        del config.config["logging"]

        with pytest.raises(ConfigValidationError):
            config.validate()
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_default_config():
    """测试默认配置"""
    config = YamlConfig()

    assert "app" in config.default_config
    assert "download" in config.default_config
    assert "logging" in config.default_config
    assert "headers" in config.default_config
    assert "n_m3u8dl_re" in config.default_config


def test_yaml_config_merge_configs():
    """测试配置合并"""
    config = YamlConfig()

    user_config = {"app": {"name": "user_app"}, "download": {"default_dir": "user_dir"}}

    default_config = {
        "app": {"name": "default_app", "version": "1.0"},
        "download": {"default_dir": "Downloads", "temp_dir": "temp"},
    }

    merged = config._merge_configs(user_config, default_config)

    assert merged["app"]["name"] == "user_app"
    assert merged["app"]["version"] == "1.0"
    assert merged["download"]["default_dir"] == "user_dir"
    assert merged["download"]["temp_dir"] == "temp"


def test_yaml_config_lazy_loading():
    """测试延迟加载"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "test_app"}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        assert config._loaded is False

        value = config.get("app.name")

        assert config._loaded is True
        assert value == "test_app"
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_thread_safety():
    """测试线程安全性"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "test_app"}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        results = []
        errors = []

        def worker():
            try:
                config = YamlConfig(config_file=path)
                value = config.get("app.name")
                results.append(value)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert all(r == "test_app" for r in results)
    finally:
        if os.path.exists(path):
            os.unlink(path)





def test_yaml_config_no_duplicate_load():
    """测试不重复加载"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "test_app"}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)
        config.load()
        first_load_id = id(config.config)

        config.load()
        config.load()
        config.load()

        assert id(config.config) == first_load_id
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_config_error():
    """测试ConfigError异常"""
    error = ConfigError("Test error", "test.key")
    assert str(error) == "Test error (key: test.key)"
    assert error.message == "Test error"
    assert error.key == "test.key"


def test_config_error_without_key():
    """测试ConfigError异常 - 无键"""
    error = ConfigError("Test error")
    assert str(error) == "Test error"
    assert error.message == "Test error"
    assert error.key is None


def test_config_load_error():
    """测试ConfigLoadError异常"""
    error = ConfigLoadError("Load failed", "load.key")
    assert isinstance(error, ConfigError)
    assert "Load failed" in str(error)


def test_config_value_error():
    """测试ConfigValueError异常"""
    error = ConfigValueError("Invalid value", "value.key")
    assert isinstance(error, ConfigError)
    assert "Invalid value" in str(error)


def test_config_validation_error():
    """测试ConfigValidationError异常"""
    error = ConfigValidationError("Validation failed", "validation.key")
    assert isinstance(error, ConfigError)
    assert "Validation failed" in str(error)
