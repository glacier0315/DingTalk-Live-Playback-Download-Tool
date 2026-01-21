"""
钉钉直播回放下载工具 - yaml_config 单元测试

本模块测试YAML配置管理模块。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2026-01-21
修改历史：
    - 2026-01-21: 初始版本
"""

import sys
import os
import yaml
import pytest
import tempfile
from unittest.mock import patch, Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.config.yaml_config import YamlConfig


def test_yaml_config_init_default_path():
    """测试YamlConfig初始化 - 使用默认路径"""
    config = YamlConfig()
    
    assert config.config == {}
    assert ".dingtalk_downloader" in config.config_file
    assert "config.yaml" in config.config_file
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
        test_config = {
            "app": {"name": "test"},
            "download": {"default_dir": "test_dir"}
        }
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
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
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write("invalid yaml content: [")
        
        config = YamlConfig(config_file=path)
        config.load()
        
        assert config._loaded is True
        assert "app" in config.config
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_load_io_error():
    """测试加载配置 - IO错误"""
    with patch('builtins.open', side_effect=IOError("Permission denied")):
        config = YamlConfig(config_file="/test/config.yaml")
        config.load()
        
        assert config._loaded is True
        assert "app" in config.config


def test_yaml_config_save():
    """测试保存配置"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        os.close(fd)
        os.unlink(path)
        
        config = YamlConfig(config_file=path)
        config.set("app.name", "test_app")
        
        with open(path, 'r', encoding='utf-8') as f:
            saved_config = yaml.safe_load(f)
        
        assert saved_config["app"]["name"] == "test_app"
    finally:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except:
                pass


def test_yaml_config_save_io_error():
    """测试保存配置 - IO错误"""
    with patch('builtins.open', side_effect=IOError("Permission denied")):
        config = YamlConfig(config_file="/test/config.yaml")
        config.set("app.name", "test_app")


def test_yaml_config_get_existing_key():
    """测试获取配置项 - 键存在"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "test_app"}}
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
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
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
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
            "download": {"default_dir": "test_dir", "max_retry_count": 10}
        }
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f)
        
        config = YamlConfig(config_file=path)
        
        assert config.get("download.default_dir") == "test_dir"
        assert config.get("download.max_retry_count") == 10
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_set():
    """测试设置配置项"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        os.close(fd)
        os.unlink(path)
        
        config = YamlConfig(config_file=path)
        config.set("app.name", "test_app")
        
        assert config.config["app"]["name"] == "test_app"
        
        with open(path, 'r', encoding='utf-8') as f:
            saved_config = yaml.safe_load(f)
        
        assert saved_config["app"]["name"] == "test_app"
    finally:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except:
                pass


def test_yaml_config_set_nested():
    """测试设置嵌套配置项"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        os.close(fd)
        os.unlink(path)
        
        config = YamlConfig(config_file=path)
        config.set("download.default_dir", "test_dir")
        config.set("download.max_retry_count", 10)
        
        assert config.config["download"]["default_dir"] == "test_dir"
        assert config.config["download"]["max_retry_count"] == 10
    finally:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except:
                pass


def test_yaml_config_set_overwrite():
    """测试设置配置项 - 覆盖现有值"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "old_app"}}
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f)
        
        config = YamlConfig(config_file=path)
        config.set("app.name", "new_app")
        
        assert config.config["app"]["name"] == "new_app"
        
        with open(path, 'r', encoding='utf-8') as f:
            saved_config = yaml.safe_load(f)
        
        assert saved_config["app"]["name"] == "new_app"
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_get_nested_method():
    """测试get_nested方法"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {
            "app": {"name": "test_app"},
            "download": {"default_dir": "test_dir"}
        }
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f)
        
        config = YamlConfig(config_file=path)
        
        assert config.get_nested(["app", "name"]) == "test_app"
        assert config.get_nested(["download", "default_dir"]) == "test_dir"
        assert config.get_nested(["nonexistent"], "default") == "default"
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_set_nested_method():
    """测试set_nested方法"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        os.close(fd)
        os.unlink(path)
        
        config = YamlConfig(config_file=path)
        config.set_nested(["app", "name"], "test_app")
        config.set_nested(["download", "default_dir"], "test_dir")
        
        assert config.config["app"]["name"] == "test_app"
        assert config.config["download"]["default_dir"] == "test_dir"
    finally:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except:
                pass


def test_yaml_config_reload():
    """测试重新加载配置"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "test_app"}}
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f)
        
        config = YamlConfig(config_file=path)
        config.load()
        
        assert config.config["app"]["name"] == "test_app"
        
        updated_config = {"app": {"name": "updated_app"}}
        with open(path, 'w', encoding='utf-8') as f:
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
            "logging": {"level": "INFO"}
        }
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
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
            "download": {"default_dir": "test_dir"},
            "browser": {"default_type": "edge"},
            "logging": {"level": "INFO"}
        }
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f)
        
        config = YamlConfig(config_file=path)
        config.load()
        
        assert config.validate() is True
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_yaml_config_default_config():
    """测试默认配置"""
    config = YamlConfig()
    config.load()
    
    assert "app" in config.default_config
    assert "download" in config.default_config
    assert "browser" in config.default_config
    assert "logging" in config.default_config
    assert "headers" in config.default_config
    assert "n_m3u8dl_re" in config.default_config
    assert "ffmpeg" in config.default_config


def test_yaml_config_merge_configs():
    """测试配置合并"""
    config = YamlConfig()
    
    user_config = {
        "app": {"name": "user_app"},
        "download": {"max_retry_count": 10}
    }
    
    default_config = {
        "app": {"name": "default_app", "version": "1.0"},
        "download": {"default_dir": "Downloads", "max_retry_count": 5},
        "browser": {"default_type": "edge"}
    }
    
    merged = config._merge_configs(user_config, default_config)
    
    assert merged["app"]["name"] == "user_app"
    assert merged["app"]["version"] == "1.0"
    assert merged["download"]["default_dir"] == "Downloads"
    assert merged["download"]["max_retry_count"] == 10
    assert merged["browser"]["default_type"] == "edge"


def test_yaml_config_lazy_loading():
    """测试延迟加载"""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    try:
        test_config = {"app": {"name": "test_app"}}
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            yaml.dump(test_config, f)
        
        config = YamlConfig(config_file=path)
        
        assert config._loaded is False
        
        value = config.get("app.name")
        
        assert config._loaded is True
        assert value == "test_app"
    finally:
        if os.path.exists(path):
            os.unlink(path)
