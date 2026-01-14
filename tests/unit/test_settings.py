"""
钉钉直播回放下载工具 - settings 单元测试

本模块测试配置管理模块。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
"""

import sys
import os
import json
import pytest
import tempfile
from unittest.mock import patch, Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.config.settings import Settings


def test_settings_init_default_path():
    """测试Settings初始化 - 使用默认路径"""
    settings = Settings()
    
    assert settings.config == {}
    assert ".dingtalk_downloader" in settings.config_file
    assert "config.json" in settings.config_file


def test_settings_init_custom_path():
    """测试Settings初始化 - 使用自定义路径"""
    custom_path = "/custom/config.json"
    settings = Settings(config_file=custom_path)
    
    assert settings.config == {}
    assert settings.config_file == custom_path


def test_settings_load_existing_file():
    """测试加载配置 - 文件存在"""
    fd, path = tempfile.mkstemp(suffix=".json")
    try:
        test_config = {"key1": "value1", "key2": "value2"}
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(test_config, f)
        
        settings = Settings(config_file=path)
        
        assert settings.config == test_config
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_settings_load_nonexistent_file():
    """测试加载配置 - 文件不存在"""
    non_existent_path = "/non/existent/config.json"
    settings = Settings(config_file=non_existent_path)
    
    assert settings.config == {}


def test_settings_load_invalid_json():
    """测试加载配置 - 无效的JSON"""
    fd, path = tempfile.mkstemp(suffix=".json")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write("invalid json content")
        
        settings = Settings(config_file=path)
        
        assert settings.config == {}
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_settings_load_io_error():
    """测试加载配置 - IO错误"""
    with patch('builtins.open', side_effect=IOError("Permission denied")):
        settings = Settings(config_file="/test/config.json")
        
        assert settings.config == {}


def test_settings_save():
    """测试保存配置"""
    fd, path = tempfile.mkstemp(suffix=".json")
    try:
        os.close(fd)
        os.unlink(path)
        
        settings = Settings(config_file=path)
        settings.config = {"key1": "value1", "key2": "value2"}
        settings.save()
        
        with open(path, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)
        
        assert saved_config == {"key1": "value1", "key2": "value2"}
    finally:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except:
                pass


def test_settings_save_io_error():
    """测试保存配置 - IO错误"""
    with patch('builtins.open', side_effect=IOError("Permission denied")):
        settings = Settings(config_file="/test/config.json")
        settings.config = {"key1": "value1"}
        
        settings.save()


def test_settings_get_existing_key():
    """测试获取配置项 - 键存在"""
    fd, path = tempfile.mkstemp(suffix=".json")
    try:
        test_config = {"key1": "value1", "key2": "value2"}
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(test_config, f)
        
        settings = Settings(config_file=path)
        
        assert settings.get("key1") == "value1"
        assert settings.get("key2") == "value2"
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_settings_get_nonexistent_key():
    """测试获取配置项 - 键不存在"""
    fd, path = tempfile.mkstemp(suffix=".json")
    try:
        test_config = {"key1": "value1"}
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(test_config, f)
        
        settings = Settings(config_file=path)
        
        assert settings.get("nonexistent") is None
        assert settings.get("nonexistent", "default") == "default"
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_settings_get_empty_config():
    """测试获取配置项 - 空配置"""
    fd, path = tempfile.mkstemp(suffix=".json")
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
    fd, path = tempfile.mkstemp(suffix=".json")
    try:
        os.close(fd)
        os.unlink(path)
        
        settings = Settings(config_file=path)
        settings.set("key1", "value1")
        
        assert settings.config["key1"] == "value1"
        
        with open(path, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)
        
        assert saved_config["key1"] == "value1"
    finally:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except:
                pass


def test_settings_set_multiple():
    """测试设置多个配置项"""
    fd, path = tempfile.mkstemp(suffix=".json")
    try:
        os.close(fd)
        os.unlink(path)
        
        settings = Settings(config_file=path)
        settings.set("key1", "value1")
        settings.set("key2", "value2")
        settings.set("key3", "value3")
        
        assert settings.config["key1"] == "value1"
        assert settings.config["key2"] == "value2"
        assert settings.config["key3"] == "value3"
        
        with open(path, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)
        
        assert saved_config == {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }
    finally:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except:
                pass


def test_settings_set_overwrite():
    """测试设置配置项 - 覆盖现有值"""
    fd, path = tempfile.mkstemp(suffix=".json")
    try:
        test_config = {"key1": "old_value"}
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(test_config, f)
        
        settings = Settings(config_file=path)
        settings.set("key1", "new_value")
        
        assert settings.config["key1"] == "new_value"
        
        with open(path, 'r', encoding='utf-8') as f:
            saved_config = json.load(f)
        
        assert saved_config["key1"] == "new_value"
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_settings_set_save_error():
    """测试设置配置项 - 保存失败"""
    with patch('builtins.open', side_effect=IOError("Permission denied")):
        settings = Settings(config_file="/test/config.json")
        settings.set("key1", "value1")
        
        assert settings.config["key1"] == "value1"


def test_settings_load_save_cycle():
    """测试配置加载和保存的完整周期"""
    fd, path = tempfile.mkstemp(suffix=".json")
    try:
        os.close(fd)
        os.unlink(path)
        
        settings1 = Settings(config_file=path)
        settings1.set("key1", "value1")
        settings1.set("key2", "value2")
        
        settings2 = Settings(config_file=path)
        
        assert settings2.get("key1") == "value1"
        assert settings2.get("key2") == "value2"
    finally:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except:
                pass


def test_settings_complex_values():
    """测试复杂配置值"""
    fd, path = tempfile.mkstemp(suffix=".json")
    try:
        os.close(fd)
        os.unlink(path)
        
        settings = Settings(config_file=path)
        settings.set("list_value", [1, 2, 3])
        settings.set("dict_value", {"nested": "value"})
        settings.set("number_value", 42)
        settings.set("bool_value", True)
        
        assert settings.get("list_value") == [1, 2, 3]
        assert settings.get("dict_value") == {"nested": "value"}
        assert settings.get("number_value") == 42
        assert settings.get("bool_value") is True
    finally:
        if os.path.exists(path):
            try:
                os.unlink(path)
            except:
                pass