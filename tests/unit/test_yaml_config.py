"""
钉钉直播回放下载工具 - yaml_config 单元测试

本模块测试YAML配置管理类。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2026-01-29
修改历史：
    - 2026-01-29: 初始版本
"""

import sys
import os
import pytest
import tempfile
import yaml
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.config.yaml_config import (
    YamlConfig,
    ConfigLoadError,
    ConfigValueError,
    ConfigValidationError,
)


@pytest.fixture
def temp_config_file(tmp_path):
    """创建临时配置文件"""
    config_data = {
        "app": {
            "name": "钉钉直播回放下载工具",
            "version": "1.5.0",
            "build_date": "2026年01月26日",
        },
        "download": {
            "default_dir": "downloads",
            "temp_dir": "temp",
            "max_retry_count": 3,
        },
        "browser": {
            "default_type": "edge",
            "headless": True,
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
            "accept": "application/vnd.apple.mpegurl, text/plain, */*",
            "accept_language": "zh-CN,zh;q=0.9,en;q=0.8",
            "accept_encoding": "gzip, deflate, br",
            "connection": "keep-alive",
            "sec_fetch_dest": "document",
            "sec_fetch_mode": "navigate",
            "sec_fetch_site": "none",
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

    config_file = tmp_path / "test_config.yaml"
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f)

    return str(config_file)


def test_yaml_config_load_success(temp_config_file):
    """测试成功加载配置文件"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    assert config._loaded is True
    assert config.config is not None
    assert "app" in config.config
    assert "download" in config.config


def test_yaml_config_load_file_not_found():
    """测试配置文件不存在"""
    YamlConfig.reset_instance()
    with pytest.raises(ConfigLoadError) as exc_info:
        YamlConfig("nonexistent.yaml")

    assert "配置文件不存在" in str(exc_info.value)


def test_yaml_config_load_invalid_yaml(tmp_path):
    """测试无效的YAML格式"""
    invalid_file = tmp_path / "invalid.yaml"
    with open(invalid_file, "w", encoding="utf-8") as f:
        f.write("invalid: yaml: content: [")

    YamlConfig.reset_instance()
    with pytest.raises(ConfigLoadError) as exc_info:
        YamlConfig(str(invalid_file))

    assert "配置文件格式错误" in str(exc_info.value)


def test_yaml_config_get_nested_value(temp_config_file):
    """测试获取嵌套配置值"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    name = config.get("app.name")
    assert name == "钉钉直播回放下载工具"

    default_dir = config.get("download.default_dir")
    assert default_dir == "downloads"


def test_yaml_config_get_with_default(temp_config_file):
    """测试获取配置值（带默认值）"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    value = config.get("nonexistent.key", "default_value")
    assert value == "default_value"


def test_yaml_config_get_str(temp_config_file):
    """测试获取字符串类型配置值"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    name = config.get_str("app.name")
    assert name == "钉钉直播回放下载工具"
    assert isinstance(name, str)


def test_yaml_config_get_str_with_default(temp_config_file):
    """测试获取字符串类型配置值（带默认值）"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    value = config.get_str("nonexistent.key", "default")
    assert value == "default"


def test_yaml_config_get_str_type_error(temp_config_file):
    """测试获取字符串类型配置值（类型错误）"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    with pytest.raises(ConfigValueError) as exc_info:
        config.get_str("browser.headless")

    assert "错误" in str(exc_info.value)


def test_yaml_config_get_int(temp_config_file):
    """测试获取整数类型配置值"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    timeout = config.get_int("browser.timeout")
    assert timeout == 30
    assert isinstance(timeout, int)


def test_yaml_config_get_int_with_default(temp_config_file):
    """测试获取整数类型配置值（带默认值）"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    value = config.get_int("nonexistent.key", 10)
    assert value == 10


def test_yaml_config_get_int_type_error(temp_config_file):
    """测试获取整数类型配置值（类型错误）"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    with pytest.raises(ConfigValueError) as exc_info:
        config.get_int("app.name")

    assert "无法转换为int" in str(exc_info.value)


def test_yaml_config_get_bool(temp_config_file):
    """测试获取布尔类型配置值"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    headless = config.get_bool("browser.headless")
    assert headless is True
    assert isinstance(headless, bool)


def test_yaml_config_get_bool_with_default(temp_config_file):
    """测试获取布尔类型配置值（带默认值）"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    value = config.get_bool("nonexistent.key", False)
    assert value is False


def test_yaml_config_get_bool_string_true(temp_config_file):
    """测试获取布尔类型配置值（字符串true）"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    with patch.object(config, "get", return_value="true"):
        value = config.get_bool("test.key")
        assert value is True


def test_yaml_config_get_bool_string_false(temp_config_file):
    """测试获取布尔类型配置值（字符串false）"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    with patch.object(config, "get", return_value="false"):
        value = config.get_bool("test.key")
        assert value is False


def test_yaml_config_get_dict(temp_config_file):
    """测试获取字典类型配置值"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    headers = config.get_dict("headers")
    assert isinstance(headers, dict)
    assert "user_agent" in headers


def test_yaml_config_get_dict_with_default(temp_config_file):
    """测试获取字典类型配置值（带默认值）"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    value = config.get_dict("nonexistent.key", {"default": "value"})
    assert value == {"default": "value"}


def test_yaml_config_get_dict_type_error(temp_config_file):
    """测试获取字典类型配置值（类型错误）"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    with pytest.raises(ConfigValueError) as exc_info:
        config.get_dict("app.name")

    assert "配置值类型错误" in str(exc_info.value)


def test_yaml_config_validate_missing_required_field(tmp_path):
    """测试验证缺失必填字段"""
    config_data = {
        "app": {
            "name": "测试",
            "version": "1.0.0",
            "build_date": "2026-01-01",
        },
        "download": {
            "default_dir": "downloads",
            "temp_dir": "temp",
            "max_retry_count": 3,
        },
    }

    config_file = tmp_path / "incomplete.yaml"
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f)

    YamlConfig.reset_instance()
    with pytest.raises(ConfigValidationError) as exc_info:
        YamlConfig(str(config_file))

    assert "缺少必填配置项" in str(exc_info.value)


def test_yaml_config_validate_invalid_type(tmp_path):
    """测试验证无效类型"""
    config_data = {
        "app": {
            "name": "测试",
            "version": "1.0.0",
            "build_date": "2026-01-01",
        },
        "browser": {
            "default_type": "edge",
            "headless": "not_a_bool",
            "timeout": 30,
        },
        "download": {
            "default_dir": "downloads",
            "temp_dir": "temp",
            "max_retry_count": 3,
        },
    }

    config_file = tmp_path / "invalid_type.yaml"
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f)

    YamlConfig.reset_instance()
    with pytest.raises(ConfigValueError) as exc_info:
        YamlConfig(str(config_file))

    assert "配置项类型错误" in str(exc_info.value)


def test_yaml_config_validate_invalid_choice(tmp_path):
    """测试验证无效选项"""
    config_data = {
        "app": {
            "name": "测试",
            "version": "1.0.0",
            "build_date": "2026-01-01",
        },
        "browser": {
            "default_type": "invalid_browser",
            "headless": True,
            "timeout": 30,
        },
        "download": {
            "default_dir": "downloads",
            "temp_dir": "temp",
            "max_retry_count": 3,
        },
    }

    config_file = tmp_path / "invalid_choice.yaml"
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f)

    YamlConfig.reset_instance()
    with pytest.raises(ConfigValueError) as exc_info:
        YamlConfig(str(config_file))

    assert "配置值无效" in str(exc_info.value)


def test_yaml_config_validate_out_of_range(tmp_path):
    """测试验证值超出范围"""
    config_data = {
        "app": {
            "name": "测试",
            "version": "1.0.0",
            "build_date": "2026-01-01",
        },
        "browser": {
            "default_type": "edge",
            "headless": True,
            "timeout": 500,
        },
        "download": {
            "default_dir": "downloads",
            "temp_dir": "temp",
            "max_retry_count": 3,
        },
    }

    config_file = tmp_path / "out_of_range.yaml"
    with open(config_file, "w", encoding="utf-8") as f:
        yaml.dump(config_data, f)

    YamlConfig.reset_instance()
    with pytest.raises(ConfigValueError) as exc_info:
        YamlConfig(str(config_file))

    assert "配置值过大" in str(exc_info.value)


def test_yaml_config_reload(temp_config_file):
    """测试重新加载配置"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    original_name = config.get_str("app.name")
    assert original_name == "钉钉直播回放下载工具"

    config.reload()

    reloaded_name = config.get_str("app.name")
    assert reloaded_name == "钉钉直播回放下载工具"


def test_yaml_config_singleton(temp_config_file):
    """测试单例模式"""
    YamlConfig.reset_instance()

    config1 = YamlConfig(temp_config_file)
    config2 = YamlConfig.get_instance()

    assert config1 is config2


def test_yaml_config_reset_instance(temp_config_file):
    """测试重置单例实例"""
    YamlConfig.reset_instance()

    config1 = YamlConfig(temp_config_file)
    YamlConfig.reset_instance()

    config2 = YamlConfig(temp_config_file)

    assert config1 is not config2


def test_yaml_config_validate(temp_config_file):
    """测试验证配置"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    result = config.validate()
    assert result is True


def test_yaml_config_get_nested(temp_config_file):
    """测试获取嵌套配置"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    keys = ["app", "name"]
    value = config.get_nested(keys)
    assert value == "钉钉直播回放下载工具"

    keys = ["nonexistent", "key"]
    value = config.get_nested(keys, "default")
    assert value == "default"


def test_yaml_config_load_twice(temp_config_file):
    """测试重复加载配置文件"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    # 第一次加载已在初始化时完成
    assert config._loaded is True

    # 再次调用 load 不应该重复加载
    config.load()
    assert config._loaded is True


def test_yaml_config_get_float(temp_config_file):
    """测试获取浮点数类型配置值"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    # 添加一个浮点数配置
    config.config["test_float"] = 3.14

    value = config.get_float("test_float")
    assert value == 3.14
    assert isinstance(value, float)


def test_yaml_config_get_float_with_default(temp_config_file):
    """测试获取浮点数类型配置值（带默认值）"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    value = config.get_float("nonexistent.key", 2.5)
    assert value == 2.5


def test_yaml_config_get_float_error(temp_config_file):
    """测试获取浮点数类型配置值（转换错误）"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    with pytest.raises(ConfigValueError) as exc_info:
        config.get_float("app.name")

    assert "无法转换为float" in str(exc_info.value)


def test_yaml_config_get_bool_none(temp_config_file):
    """测试获取布尔类型配置值（None情况）"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    value = config.get_bool("nonexistent.key", False)
    assert value is False


def test_yaml_config_get_bool_invalid(temp_config_file):
    """测试获取布尔类型配置值（无效转换）"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    # 使用 patch 模拟返回一个无法转换的值
    with patch.object(config, "get", return_value=123):
        with pytest.raises(ConfigValueError) as exc_info:
            config.get_bool("test.key")

        assert "无法转换为bool" in str(exc_info.value)


def test_yaml_config_get_list(temp_config_file):
    """测试获取列表类型配置值"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    # 添加一个列表配置
    config.config["test_list"] = ["item1", "item2", "item3"]

    value = config.get_list("test_list")
    assert isinstance(value, list)
    assert len(value) == 3


def test_yaml_config_get_list_with_default(temp_config_file):
    """测试获取列表类型配置值（带默认值）"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    value = config.get_list("nonexistent.key", ["default"])
    assert value == ["default"]


def test_yaml_config_get_list_error(temp_config_file):
    """测试获取列表类型配置值（类型错误）"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    with pytest.raises(ConfigValueError) as exc_info:
        config.get_list("app.name")

    assert "配置值类型错误" in str(exc_info.value)


def test_yaml_config_get_int_bool_error(temp_config_file):
    """测试获取整数类型配置值（bool不能转换为int）"""
    YamlConfig.reset_instance()
    config = YamlConfig(temp_config_file)

    # 使用 patch 模拟返回一个 bool 值
    with patch.object(config, "get", return_value=True):
        with pytest.raises(ConfigValueError) as exc_info:
            config.get_int("test.key")

        assert "bool不能转换为int" in str(exc_info.value)


def test_yaml_config_io_error(tmp_path):
    """测试IO错误读取配置文件"""
    import stat

    # 创建一个无法读取的文件（没有权限）
    config_file = tmp_path / "unreadable.yaml"
    config_file.write_text("test: value")

    # Windows 上的权限设置不同，我们使用 mock 来模拟 IOError
    YamlConfig.reset_instance()

    with patch("builtins.open", side_effect=IOError("Permission denied")):
        with pytest.raises(ConfigLoadError) as exc_info:
            YamlConfig(str(config_file))

        assert "读取配置文件失败" in str(exc_info.value)
