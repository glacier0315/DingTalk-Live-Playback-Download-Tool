"""
钉钉直播回放下载工具 - settings 单元测试

本模块测试配置管理模块。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2026-01-21: 更新为YAML配置
"""

import sys
import os
import yaml
import pytest
import tempfile
from unittest.mock import patch, Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.config.settings import Settings


def test_settings_init_default_path():
    """测试Settings初始化 - 使用默认路径"""
    settings = Settings()

    assert "config" in settings.yaml_config.config_file
    assert "app.yaml" in settings.yaml_config.config_file
    # Settings在初始化时会调用load()，所以_loaded应该为True
    assert settings.yaml_config._loaded is True


def test_settings_init_custom_path():
    """测试Settings初始化 - 使用自定义路径"""
    custom_path = "/custom/config.yaml"
    settings = Settings(config_file=custom_path)

    assert settings.yaml_config.config_file == custom_path


def test_settings_load_existing_file():
    """测试加载配置 - 文件存在"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "test_app"}, "download": {"default_dir": "test_dir"}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        settings = Settings(config_file=path)

        assert settings.yaml_config.config["app"]["name"] == "test_app"
        assert settings.yaml_config.config["download"]["default_dir"] == "test_dir"
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_settings_load_nonexistent_file():
    """测试加载配置 - 文件不存在"""
    non_existent_path = "/non/existent/config.yaml"
    settings = Settings(config_file=non_existent_path)

    assert "app" in settings.yaml_config.config
    assert "download" in settings.yaml_config.config


def test_settings_load_invalid_yaml():
    """测试加载配置 - 无效的YAML"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("invalid yaml content: [")

        settings = Settings(config_file=path)

        assert "app" in settings.yaml_config.config
        assert "download" in settings.yaml_config.config
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_settings_load_io_error():
    """测试加载配置 - IO错误"""
    with patch("builtins.open", side_effect=IOError("Permission denied")):
        settings = Settings(config_file="/test/config.yaml")

        assert "app" in settings.yaml_config.config
        assert "download" in settings.yaml_config.config


def test_settings_save():
    """测试保存配置"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        os.close(fd)
        os.unlink(path)

        settings = Settings(config_file=path)
        settings.set("app.name", "test_app")

        with open(path, "r", encoding="utf-8") as f:
            saved_config = yaml.safe_load(f)

        assert saved_config["app"]["name"] == "test_app"
    finally:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except:
                pass


def test_settings_save_io_error():
    """测试保存配置 - IO错误"""
    with patch("builtins.open", side_effect=IOError("Permission denied")):
        settings = Settings(config_file="/test/config.yaml")
        settings.set("app.name", "test_app")


def test_settings_get_existing_key():
    """测试获取配置项 - 键存在"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "test_app"}, "download": {"default_dir": "test_dir"}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        settings = Settings(config_file=path)

        assert settings.get("app.name") == "test_app"
        assert settings.get("download.default_dir") == "test_dir"
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_settings_get_nonexistent_key():
    """测试获取配置项 - 键不存在"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "test_app"}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        settings = Settings(config_file=path)

        assert settings.get("nonexistent") is None
        assert settings.get("nonexistent", "default") == "default"
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_settings_get_empty_config():
    """测试获取配置项 - 空配置"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        os.close(fd)
        os.unlink(path)

        settings = Settings(config_file=path)

        assert settings.get("any_key") is None
        assert settings.get("any_key", "default") == "default"
    finally:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except:
                pass


def test_settings_set():
    """测试设置配置项"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        os.close(fd)
        os.unlink(path)

        settings = Settings(config_file=path)
        settings.set("app.name", "test_app")

        assert settings.yaml_config.config["app"]["name"] == "test_app"

        with open(path, "r", encoding="utf-8") as f:
            saved_config = yaml.safe_load(f)

        assert saved_config["app"]["name"] == "test_app"
    finally:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except:
                pass


def test_settings_set_multiple():
    """测试设置多个配置项"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        os.close(fd)
        os.unlink(path)

        settings = Settings(config_file=path)
        settings.set("app.name", "test_app")
        settings.set("download.default_dir", "test_dir")
        settings.set("download.max_retry_count", 10)

        assert settings.yaml_config.config["app"]["name"] == "test_app"
        assert settings.yaml_config.config["download"]["default_dir"] == "test_dir"
        assert settings.yaml_config.config["download"]["max_retry_count"] == 10

        with open(path, "r", encoding="utf-8") as f:
            saved_config = yaml.safe_load(f)

        assert saved_config["app"]["name"] == "test_app"
        assert saved_config["download"]["default_dir"] == "test_dir"
        assert saved_config["download"]["max_retry_count"] == 10
    finally:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except:
                pass


def test_settings_set_overwrite():
    """测试设置配置项 - 覆盖现有值"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "old_app"}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            yaml.dump(test_config, f)

        settings = Settings(config_file=path)
        settings.set("app.name", "new_app")

        assert settings.yaml_config.config["app"]["name"] == "new_app"

        with open(path, "r", encoding="utf-8") as f:
            saved_config = yaml.safe_load(f)

        assert saved_config["app"]["name"] == "new_app"
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_settings_set_save_error():
    """测试设置配置项 - 保存失败"""
    with patch("builtins.open", side_effect=IOError("Permission denied")):
        settings = Settings(config_file="/test/config.yaml")
        settings.set("app.name", "test_app")

        assert settings.yaml_config.config["app"]["name"] == "test_app"


def test_settings_load_save_cycle():
    """测试配置加载和保存的完整周期"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        os.close(fd)
        os.unlink(path)

        settings1 = Settings(config_file=path)
        settings1.set("app.name", "test_app")
        settings1.set("download.default_dir", "test_dir")

        settings2 = Settings(config_file=path)

        assert settings2.get("app.name") == "test_app"
        assert settings2.get("download.default_dir") == "test_dir"
    finally:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except:
                pass


def test_settings_complex_values():
    """测试复杂配置值"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        os.close(fd)
        os.unlink(path)

        settings = Settings(config_file=path)
        settings.set("test.list_value", [1, 2, 3])
        settings.set("test.dict_value", {"nested": "value"})
        settings.set("test.number_value", 42)
        settings.set("test.bool_value", True)

        assert settings.get("test.list_value") == [1, 2, 3]
        assert settings.get("test.dict_value") == {"nested": "value"}
        assert settings.get("test.number_value") == 42
        assert settings.get("test.bool_value") is True
    finally:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except:
                pass


def test_settings_migrate_from_json():
    """测试从JSON迁移配置"""
    import json

    fd, json_path = tempfile.mkstemp(suffix=".json")
    fd2, yaml_path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "test_app"}, "download": {"default_dir": "test_dir"}}
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(test_config, f)

        os.close(fd2)
        os.unlink(yaml_path)

        settings = Settings(config_file=yaml_path)
        settings.migrate_from_json(json_path)

        assert settings.get("app.name") == "test_app"
        assert settings.get("download.default_dir") == "test_dir"

        with open(yaml_path, "r", encoding="utf-8") as f:
            saved_config = yaml.safe_load(f)

        assert saved_config["app"]["name"] == "test_app"
        assert saved_config["download"]["default_dir"] == "test_dir"
    finally:
        if os.path.exists(json_path):
            os.unlink(json_path)
        if os.path.exists(yaml_path):
            try:
                os.unlink(yaml_path)
            except:
                pass


def test_settings_migrate_from_json_nonexistent():
    """测试从JSON迁移配置 - 文件不存在"""
    settings = Settings()
    settings.migrate_from_json("/non/existent/config.json")


def test_settings_migrate_from_json_invalid():
    """测试从JSON迁移配置 - 无效JSON"""
    import json

    fd, json_path = tempfile.mkstemp(suffix=".json")
    fd2, yaml_path = tempfile.mkstemp(suffix=".yaml")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("invalid json content")

        os.close(fd2)
        os.unlink(yaml_path)

        settings = Settings(config_file=yaml_path)
        settings.migrate_from_json(json_path)
    finally:
        if os.path.exists(json_path):
            os.unlink(json_path)
        if os.path.exists(yaml_path):
            try:
                os.unlink(yaml_path)
            except:
                pass


def test_settings_backward_compatibility():
    """测试向后兼容性"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        os.close(fd)
        os.unlink(path)

        settings = Settings(config_file=path)

        settings.load()
        settings.save()
        value = settings.get("nonexistent.key", "default")
        settings.set("app.name", "test")

        assert value == "default"
        assert settings.get("app.name") == "test"
    finally:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except:
                pass
