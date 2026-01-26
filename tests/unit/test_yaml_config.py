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
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.config.yaml_config import (
    YamlConfig,
    ConfigError,
    ConfigLoadError,
    ConfigValueError,
    ConfigValidationError,
    CONFIG_SCHEMA,
)


@pytest.fixture(autouse=True)
def reset_singleton():
    """每个测试前重置单例实例"""
    YamlConfig.reset_instance()
    yield
    YamlConfig.reset_instance()


def get_full_test_config():
    """获取完整的测试配置"""
    return {
        "app": {"name": "test_app", "version": "1.0.0", "build_date": "2026年01月26日"},
        "download": {"default_dir": "test_dir", "temp_dir": "temp", "max_retry_count": 5},
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
            "user_agent": "Mozilla/5.0",
            "referer": "https://n.dingtalk.com/",
            "accept": "application/vnd.apple.mpegurl",
            "accept_language": "zh-CN,zh;q=0.9",
            "accept_encoding": "gzip, deflate",
            "connection": "keep-alive",
            "sec_fetch_dest": "document",
            "sec_fetch_mode": "navigate",
            "sec_fetch_site": "same-origin",
            "sec_fetch_user": "?1",
            "upgrade_insecure_requests": "1",
        },
        "n_m3u8dl_re": {
            "executable_path": "assets/bin/N_m3u8DL-RE.exe",
            "ui_language": "zh-CN",
            "temp_dir": "temp",
            "log_dir": "logs",
        },
        "ffmpeg": {
            "executable_path": "assets/bin/ffmpeg.exe",
        },
    }


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
        test_config = get_full_test_config()
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)
        config.load()

        assert config.config["app"]["name"] == "test_app"
        assert config.config["download"]["default_dir"] == "test_dir"
        assert config._loaded is True
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_load_nonexistent_file():
    """测试加载配置 - 文件不存在"""
    non_existent_path = "/non/existent/config.yaml"
    config = YamlConfig(config_file=non_existent_path)

    with pytest.raises(ConfigLoadError):
        config.load()


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
        test_config = get_full_test_config()
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
        test_config = get_full_test_config()
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
        test_config = get_full_test_config()
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
        test_config = get_full_test_config()
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        assert config.get_str("app.name") == "test_app"
        assert config.get_str("app.version") == "1.0.0"
        assert config.get_str("app.build_date") == "2026年01月26日"
        assert config.get_str("nonexistent") == ""
        assert config.get_str("nonexistent", "default") == "default"
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_str_type_error():
    """测试获取字符串类型配置项 - 类型错误"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = get_full_test_config()
        test_config["app"]["name"] = 123
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        with pytest.raises(ConfigValueError):
            config.get_str("app.name")
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_int():
    """测试获取整数类型配置项"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = get_full_test_config()
        test_config["app"]["count"] = 123
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
        test_config = get_full_test_config()
        test_config["app"]["count"] = "456"
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
        test_config = get_full_test_config()
        test_config["app"]["name"] = "test"
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
        test_config = get_full_test_config()
        test_config["app"]["ratio"] = 3.14
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
        test_config = get_full_test_config()
        test_config["app"]["ratio"] = "2.71"
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
        test_config = get_full_test_config()
        test_config["app"]["enabled"] = True
        test_config["app"]["disabled"] = False
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
        test_config = get_full_test_config()
        test_config["app"]["true1"] = "true"
        test_config["app"]["true2"] = "1"
        test_config["app"]["true3"] = "yes"
        test_config["app"]["true4"] = "on"
        test_config["app"]["false1"] = "false"
        test_config["app"]["false2"] = "0"
        test_config["app"]["false3"] = "no"
        test_config["app"]["false4"] = "off"
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
        test_config = get_full_test_config()
        test_config["app"]["name"] = "test"
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
        test_config = get_full_test_config()
        test_config["app"]["items"] = [1, 2, 3]
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
        test_config = get_full_test_config()
        test_config["app"]["name"] = "test"
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
        test_config = get_full_test_config()
        test_config["app"]["settings"] = {"key1": "value1", "key2": "value2"}
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
        test_config = get_full_test_config()
        test_config["app"]["name"] = "test"
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
        test_config = get_full_test_config()
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
        test_config = get_full_test_config()
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)
        config.load()

        assert config.config["app"]["name"] == "test_app"

        updated_config = get_full_test_config()
        updated_config["app"]["name"] = "updated_app"
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
        test_config = get_full_test_config()
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

        with pytest.raises(ConfigValidationError):
            config.load()
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_config_schema():
    """测试CONFIG_SCHEMA定义"""
    assert "app" in CONFIG_SCHEMA
    assert "download" in CONFIG_SCHEMA
    assert "browser" in CONFIG_SCHEMA
    assert "logging" in CONFIG_SCHEMA
    assert "headers" in CONFIG_SCHEMA
    assert "n_m3u8dl_re" in CONFIG_SCHEMA
    assert "ffmpeg" in CONFIG_SCHEMA


def test_config_schema_required():
    """测试CONFIG_SCHEMA必填项"""
    assert CONFIG_SCHEMA["app"]["required"] is True
    assert CONFIG_SCHEMA["download"]["required"] is True
    assert CONFIG_SCHEMA["browser"]["required"] is True
    assert CONFIG_SCHEMA["logging"]["required"] is True
    assert CONFIG_SCHEMA["headers"]["required"] is True
    assert CONFIG_SCHEMA["n_m3u8dl_re"]["required"] is True
    assert CONFIG_SCHEMA["ffmpeg"]["required"] is True


def test_config_schema_fields():
    """测试CONFIG_SCHEMA字段定义"""
    assert "fields" in CONFIG_SCHEMA["app"]
    assert "name" in CONFIG_SCHEMA["app"]["fields"]
    assert "version" in CONFIG_SCHEMA["app"]["fields"]
    assert "build_date" in CONFIG_SCHEMA["app"]["fields"]
    assert CONFIG_SCHEMA["app"]["fields"]["name"]["required"] is True
    assert CONFIG_SCHEMA["app"]["fields"]["name"]["type"] == str
    assert CONFIG_SCHEMA["app"]["fields"]["version"]["required"] is True
    assert CONFIG_SCHEMA["app"]["fields"]["version"]["type"] == str
    assert CONFIG_SCHEMA["app"]["fields"]["build_date"]["required"] is True
    assert CONFIG_SCHEMA["app"]["fields"]["build_date"]["type"] == str


def test_config_validate_missing_required():
    """测试配置验证 - 缺少必填项"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {
            "app": {"name": "test"},
        }
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        with pytest.raises(ConfigValidationError) as exc_info:
            config.load()

        assert "缺少必填配置项" in str(exc_info.value)
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_config_validate_missing_build_date():
    """测试配置验证 - 缺少build_date"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {
            "app": {"name": "test_app", "version": "1.0.0"},
        }
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        with pytest.raises(ConfigValidationError) as exc_info:
            config.load()

        assert "缺少必填配置项" in str(exc_info.value)
        assert "build_date" in str(exc_info.value)
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_config_validate_type_error():
    """测试配置验证 - 类型错误"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = get_full_test_config()
        test_config["app"]["name"] = 123
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        with pytest.raises(ConfigValueError) as exc_info:
            config.load()

        assert "配置项类型错误" in str(exc_info.value)
        assert "期望类型: str" in str(exc_info.value)
        assert "实际类型: int" in str(exc_info.value)
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_config_validate_range_error():
    """测试配置验证 - 值超出范围"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = get_full_test_config()
        test_config["download"]["max_retry_count"] = 200
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        with pytest.raises(ConfigValueError) as exc_info:
            config.load()

        assert "配置值过大" in str(exc_info.value)
        assert "最大值: 100" in str(exc_info.value)
        assert "实际值: 200" in str(exc_info.value)
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_config_validate_choices_error():
    """测试配置验证 - 值不在选项中"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = get_full_test_config()
        test_config["browser"]["default_type"] = "safari"
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        config = YamlConfig(config_file=path)

        with pytest.raises(ConfigValueError) as exc_info:
            config.load()

        assert "配置值无效" in str(exc_info.value)
        assert "可选值:" in str(exc_info.value)
        assert "实际值: safari" in str(exc_info.value)
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
