"""
钉钉直播回放下载工具 - HeaderManager单元测试

本模块测试HeaderManager的各项功能。

作者：项目团队
依赖：pytest, unittest.mock
创建日期：2026-01-22
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from dingtalk_downloader.config.header_manager import HeaderManager


class TestHeaderManagerInit:
    """测试HeaderManager初始化"""

    def test_init_default_path(self):
        """测试使用默认配置文件路径初始化"""
        manager = HeaderManager()
        assert manager.config is not None
        assert manager._headers_cache is not None
        assert manager._override_headers is not None

    def test_init_custom_path(self):
        """测试使用自定义配置文件路径初始化"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
            f.write("""
headers:
  user_agent: "Test User-Agent"
  referer: "https://test.com/"
""")
        
        try:
            manager = HeaderManager(config_path)
            assert manager.config.config_file == config_path
        finally:
            os.unlink(config_path)

    def test_init_loads_headers(self):
        """测试初始化时加载请求头"""
        manager = HeaderManager()
        assert len(manager._headers_cache) > 0
        assert "User-Agent" in manager._headers_cache
        assert "Referer" in manager._headers_cache


class TestHeaderManagerLoadHeaders:
    """测试请求头加载功能"""

    def test_load_headers_from_config(self):
        """测试从配置文件加载请求头"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
            f.write("""
headers:
  user_agent: "Mozilla/5.0 Test"
  referer: "https://test.com/"
  accept: "text/html"
""")
        
        try:
            manager = HeaderManager(config_path)
            assert manager._headers_cache["User-Agent"] == "Mozilla/5.0 Test"
            assert manager._headers_cache["Referer"] == "https://test.com/"
            assert manager._headers_cache["Accept"] == "text/html"
        finally:
            os.unlink(config_path)

    def test_load_headers_mapping(self):
        """测试配置键到请求头的映射"""
        manager = HeaderManager()
        assert "User-Agent" in manager._headers_cache
        assert "Referer" in manager._headers_cache
        assert "Accept" in manager._headers_cache
        assert "Accept-Language" in manager._headers_cache
        assert "Accept-Encoding" in manager._headers_cache
        assert "Connection" in manager._headers_cache
        assert "Sec-Fetch-Dest" in manager._headers_cache
        assert "Sec-Fetch-Mode" in manager._headers_cache
        assert "Sec-Fetch-Site" in manager._headers_cache
        assert "Sec-Fetch-User" in manager._headers_cache
        assert "Upgrade-Insecure-Requests" in manager._headers_cache


class TestHeaderManagerGetHeaders:
    """测试获取请求头功能"""

    def test_get_headers_without_overrides(self):
        """测试获取请求头（不包含覆盖）"""
        manager = HeaderManager()
        headers = manager.get_headers(include_overrides=False)
        assert isinstance(headers, dict)
        assert len(headers) > 0

    def test_get_headers_with_overrides(self):
        """测试获取请求头（包含覆盖）"""
        manager = HeaderManager()
        manager.set_header("X-Custom-Header", "CustomValue", is_override=True)
        headers = manager.get_headers(include_overrides=True)
        assert "X-Custom-Header" in headers
        assert headers["X-Custom-Header"] == "CustomValue"

    def test_get_headers_override_priority(self):
        """测试覆盖请求头的优先级"""
        manager = HeaderManager()
        original_value = manager.get_header("User-Agent")
        manager.set_header("User-Agent", "Overridden User-Agent", is_override=True)
        headers = manager.get_headers(include_overrides=True)
        assert headers["User-Agent"] == "Overridden User-Agent"
        assert manager._headers_cache["User-Agent"] == original_value

    def test_get_headers_returns_copy(self):
        """测试获取请求头返回副本"""
        manager = HeaderManager()
        headers1 = manager.get_headers()
        headers2 = manager.get_headers()
        assert headers1 is not headers2


class TestHeaderManagerGetHeader:
    """测试获取单个请求头功能"""

    def test_get_header_existing(self):
        """测试获取存在的请求头"""
        manager = HeaderManager()
        user_agent = manager.get_header("User-Agent")
        assert user_agent is not None
        assert isinstance(user_agent, str)

    def test_get_header_nonexistent(self):
        """测试获取不存在的请求头"""
        manager = HeaderManager()
        value = manager.get_header("X-Nonexistent-Header")
        assert value is None

    def test_get_header_with_default(self):
        """测试获取请求头（带默认值）"""
        manager = HeaderManager()
        value = manager.get_header("X-Nonexistent-Header", "default_value")
        assert value == "default_value"

    def test_get_header_override_priority(self):
        """测试覆盖请求头的优先级"""
        manager = HeaderManager()
        manager.set_header("User-Agent", "Overridden", is_override=True)
        value = manager.get_header("User-Agent", include_overrides=True)
        assert value == "Overridden"
        value = manager.get_header("User-Agent", include_overrides=False)
        assert value != "Overridden"


class TestHeaderManagerSetHeader:
    """测试设置请求头功能"""

    def test_set_header_as_override(self):
        """测试设置覆盖请求头"""
        manager = HeaderManager()
        manager.set_header("X-Custom", "Value", is_override=True)
        assert "X-Custom" in manager._override_headers
        assert manager._override_headers["X-Custom"] == "Value"

    def test_set_header_as_cache(self):
        """测试设置缓存请求头"""
        manager = HeaderManager()
        manager.set_header("X-Custom", "Value", is_override=False)
        assert "X-Custom" in manager._headers_cache
        assert manager._headers_cache["X-Custom"] == "Value"

    def test_set_header_overwrite_override(self):
        """测试覆盖已存在的请求头"""
        manager = HeaderManager()
        manager.set_header("X-Custom", "Value1", is_override=True)
        manager.set_header("X-Custom", "Value2", is_override=True)
        assert manager._override_headers["X-Custom"] == "Value2"

    def test_set_header_overwrite_cache(self):
        """测试覆盖缓存中的请求头"""
        manager = HeaderManager()
        original_value = manager._headers_cache.get("User-Agent")
        manager.set_header("User-Agent", "New Value", is_override=False)
        assert manager._headers_cache["User-Agent"] == "New Value"
        assert manager._headers_cache["User-Agent"] != original_value


class TestHeaderManagerRemoveHeader:
    """测试移除请求头功能"""

    def test_remove_header_from_overrides(self):
        """测试从覆盖请求头中移除"""
        manager = HeaderManager()
        manager.set_header("X-Custom", "Value", is_override=True)
        result = manager.remove_header("X-Custom", from_overrides=True)
        assert result is True
        assert "X-Custom" not in manager._override_headers

    def test_remove_header_from_cache(self):
        """测试从缓存中移除请求头"""
        manager = HeaderManager()
        manager.set_header("X-Custom", "Value", is_override=False)
        result = manager.remove_header("X-Custom", from_overrides=False)
        assert result is True
        assert "X-Custom" not in manager._headers_cache

    def test_remove_header_nonexistent(self):
        """测试移除不存在的请求头"""
        manager = HeaderManager()
        result = manager.remove_header("X-Nonexistent", from_overrides=True)
        assert result is False

    def test_remove_header_from_both(self):
        """测试同时从覆盖和缓存中移除"""
        manager = HeaderManager()
        manager.set_header("X-Custom", "Override", is_override=True)
        manager.set_header("X-Custom", "Cache", is_override=False)
        
        manager.remove_header("X-Custom", from_overrides=True)
        manager.remove_header("X-Custom", from_overrides=False)
        
        assert "X-Custom" not in manager._override_headers
        assert "X-Custom" not in manager._headers_cache


class TestHeaderManagerClearOverrides:
    """测试清除覆盖请求头功能"""

    def test_clear_overrides(self):
        """测试清除所有覆盖请求头"""
        manager = HeaderManager()
        manager.set_header("X-Custom1", "Value1", is_override=True)
        manager.set_header("X-Custom2", "Value2", is_override=True)
        manager.set_header("X-Custom3", "Value3", is_override=True)
        
        assert len(manager._override_headers) == 3
        
        manager.clear_overrides()
        
        assert len(manager._override_headers) == 0

    def test_clear_overrides_preserves_cache(self):
        """测试清除覆盖请求头不影响缓存"""
        manager = HeaderManager()
        cache_size = len(manager._headers_cache)
        
        manager.set_header("X-Custom", "Value", is_override=True)
        manager.clear_overrides()
        
        assert len(manager._headers_cache) == cache_size


class TestHeaderManagerGetOverrideHeaders:
    """测试获取覆盖请求头功能"""

    def test_get_override_headers_empty(self):
        """测试获取空的覆盖请求头"""
        manager = HeaderManager()
        overrides = manager.get_override_headers()
        assert isinstance(overrides, dict)
        assert len(overrides) == 0

    def test_get_override_headers_with_values(self):
        """测试获取有值的覆盖请求头"""
        manager = HeaderManager()
        manager.set_header("X-Custom1", "Value1", is_override=True)
        manager.set_header("X-Custom2", "Value2", is_override=True)
        
        overrides = manager.get_override_headers()
        assert len(overrides) == 2
        assert overrides["X-Custom1"] == "Value1"
        assert overrides["X-Custom2"] == "Value2"

    def test_get_override_headers_returns_copy(self):
        """测试获取覆盖请求头返回副本"""
        manager = HeaderManager()
        manager.set_header("X-Custom", "Value", is_override=True)
        
        overrides1 = manager.get_override_headers()
        overrides2 = manager.get_override_headers()
        
        assert overrides1 is not overrides2


class TestHeaderManagerReloadConfig:
    """测试重新加载配置功能"""

    def test_reload_config(self):
        """测试重新加载配置"""
        manager = HeaderManager()
        original_cache_size = len(manager._headers_cache)
        
        manager.set_header("X-Custom", "Value", is_override=False)
        manager.reload_config()
        
        assert len(manager._headers_cache) == original_cache_size
        assert "X-Custom" not in manager._headers_cache

    def test_reload_config_preserves_overrides(self):
        """测试重新加载配置保留覆盖请求头"""
        manager = HeaderManager()
        manager.set_header("X-Custom", "Value", is_override=True)
        
        manager.reload_config()
        
        assert "X-Custom" in manager._override_headers
        assert manager._override_headers["X-Custom"] == "Value"


class TestHeaderManagerMergeHeaders:
    """测试合并请求头功能"""

    def test_merge_headers_as_override(self):
        """测试合并请求头作为覆盖"""
        manager = HeaderManager()
        additional = {
            "X-Custom1": "Value1",
            "X-Custom2": "Value2"
        }
        
        result = manager.merge_headers(additional, is_override=True)
        
        assert "X-Custom1" in manager._override_headers
        assert "X-Custom2" in manager._override_headers
        assert "X-Custom1" in result
        assert "X-Custom2" in result

    def test_merge_headers_as_cache(self):
        """测试合并请求头到缓存"""
        manager = HeaderManager()
        additional = {
            "X-Custom1": "Value1",
            "X-Custom2": "Value2"
        }
        
        result = manager.merge_headers(additional, is_override=False)
        
        assert "X-Custom1" in manager._headers_cache
        assert "X-Custom2" in manager._headers_cache
        assert "X-Custom1" in result
        assert "X-Custom2" in result

    def test_merge_headers_overwrites(self):
        """测试合并请求头覆盖已存在的值"""
        manager = HeaderManager()
        manager.set_header("X-Custom", "OldValue", is_override=True)
        
        additional = {"X-Custom": "NewValue"}
        manager.merge_headers(additional, is_override=True)
        
        assert manager._override_headers["X-Custom"] == "NewValue"


class TestHeaderManagerValidateHeaders:
    """测试验证请求头功能"""

    def test_validate_headers_valid(self):
        """测试验证有效的请求头"""
        manager = HeaderManager()
        result = manager.validate_headers()
        assert result is True

    def test_validate_headers_missing_user_agent(self):
        """测试验证缺少User-Agent"""
        manager = HeaderManager()
        manager.remove_header("User-Agent", from_overrides=False)
        result = manager.validate_headers()
        assert result is False

    def test_validate_headers_missing_referer(self):
        """测试验证缺少Referer"""
        manager = HeaderManager()
        manager.remove_header("Referer", from_overrides=False)
        result = manager.validate_headers()
        assert result is False

    def test_validate_headers_missing_accept(self):
        """测试验证缺少Accept"""
        manager = HeaderManager()
        manager.remove_header("Accept", from_overrides=False)
        result = manager.validate_headers()
        assert result is False

    def test_validate_headers_with_overrides(self):
        """测试验证包含覆盖的请求头"""
        manager = HeaderManager()
        manager.remove_header("User-Agent", from_overrides=False)
        manager.set_header("User-Agent", "Override UA", is_override=True)
        result = manager.validate_headers()
        assert result is True


class TestHeaderManagerGetHeaderInfo:
    """测试获取请求头信息功能"""

    def test_get_header_info(self):
        """测试获取请求头信息"""
        manager = HeaderManager()
        manager.set_header("X-Custom", "Value", is_override=True)
        
        info = manager.get_header_info()
        
        assert isinstance(info, dict)
        assert "total_headers" in info
        assert "override_headers" in info
        assert "headers" in info
        assert "overrides" in info
        assert info["total_headers"] > 0
        assert info["override_headers"] == 1
        assert "X-Custom" in info["overrides"]

    def test_get_header_info_empty_overrides(self):
        """测试获取请求头信息（无覆盖）"""
        manager = HeaderManager()
        
        info = manager.get_header_info()
        
        assert info["override_headers"] == 0
        assert len(info["overrides"]) == 0


class TestHeaderManagerEdgeCases:
    """测试边界情况"""

    def test_empty_config_file(self):
        """测试空配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
            f.write("")
        
        try:
            manager = HeaderManager(config_path)
            assert len(manager._headers_cache) > 0
        finally:
            os.unlink(config_path)

    def test_config_file_without_headers_section(self):
        """测试没有headers部分的配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
            f.write("""
app:
  name: "Test"
""")
        
        try:
            manager = HeaderManager(config_path)
            assert len(manager._headers_cache) > 0
        finally:
            os.unlink(config_path)

    def test_special_characters_in_header_value(self):
        """测试请求头值中的特殊字符"""
        manager = HeaderManager()
        special_value = "Value with spaces, commas; and/slashes"
        manager.set_header("X-Special", special_value, is_override=True)
        
        value = manager.get_header("X-Special")
        assert value == special_value

    def test_unicode_in_header_value(self):
        """测试请求头值中的Unicode字符"""
        manager = HeaderManager()
        unicode_value = "测试中文"
        manager.set_header("X-Unicode", unicode_value, is_override=True)
        
        value = manager.get_header("X-Unicode")
        assert value == unicode_value