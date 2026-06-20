"""Tests for DependencyFactory: 单例/缓存语义 + clear_instances + id(browser) key。"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import pytest
import yaml

from dingtalk_downloader.core.cookie_handler import CookieHandler
from dingtalk_downloader.core.dependency_factory import DependencyFactory
from dingtalk_downloader.core.m3u8_download_service import M3u8RefreshService
from dingtalk_downloader.binary.n_m3u8dl_re import NM3u8DLRE
from dingtalk_downloader.config.yaml_config import YamlConfig
from dingtalk_downloader.utils.path_selector import PathSelector


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_yaml_singleton():
    YamlConfig.reset_instance()
    yield
    YamlConfig.reset_instance()


def _valid_config(tmp_path: Path) -> dict:
    return {
        "app": {"name": "x", "version": "1.0", "build_date": "2026-01-01"},
        "download": {
            "default_dir": str(tmp_path / "Downloads"),
            "temp_dir": str(tmp_path / "temp"),
            "max_retry_count": 5,
        },
        "browser": {"default_type": "edge", "headless": False, "timeout": 30},
        "logging": {
            "level": "INFO",
            "dir": str(tmp_path / "logs"),
            "max_bytes": 10485760,
            "backup_count": 5,
            "retention_days": 30,
        },
        "headers": {
            "user_agent": "Test/1.0",
            "referer": "https://n.dingtalk.com/",
            "accept": "*/*",
            "accept_language": "zh-CN",
            "accept_encoding": "identity",
            "connection": "keep-alive",
            "sec_fetch_dest": "video",
            "sec_fetch_mode": "cors",
            "sec_fetch_site": "same-origin",
            "sec_fetch_user": "?1",
            "upgrade_insecure_requests": "1",
        },
        "n_m3u8dl_re": {
            "executable_path": "fake-exe",
            "ui_language": "zh-CN",
            "temp_dir": str(tmp_path / "nm_temp"),
            "log_dir": str(tmp_path / "nm_logs"),
        },
        "ffmpeg": {"executable_path": "fake-ffmpeg"},
    }


@pytest.fixture
def factory(tmp_path):
    """初始化 YamlConfig + 返回新的 DependencyFactory。"""
    cfg = tmp_path / "app.yaml"
    cfg.write_text(
        yaml.safe_dump(_valid_config(tmp_path), allow_unicode=True),
        encoding="utf-8",
    )
    YamlConfig.reset_instance()
    # 显式 load 以触发依赖构造
    YamlConfig.get_instance()
    return DependencyFactory()


# ---------------------------------------------------------------------------
# 测试
# ---------------------------------------------------------------------------


class TestFactoryBasics:
    def test_factory_init_starts_empty(self, factory):
        assert factory.get_instance_count() == 0

    def test_instance_count_reflects_additions(self, factory):
        factory.get_cookie_handler("edge")
        assert factory.get_instance_count() == 1
        factory.get_cookie_handler("chrome")
        assert factory.get_instance_count() == 2
        # 已存在的 key 重复调用不增加
        factory.get_cookie_handler("edge")
        assert factory.get_instance_count() == 2


class TestGetCookieHandler:
    def test_caches_by_browser_type(self, factory):
        a = factory.get_cookie_handler("edge")
        b = factory.get_cookie_handler("edge")
        assert a is b
        assert isinstance(a, CookieHandler)

    def test_different_types_return_different_instances(self, factory):
        edge = factory.get_cookie_handler("edge")
        chrome = factory.get_cookie_handler("chrome")
        firefox = factory.get_cookie_handler("firefox")
        assert edge is not chrome
        assert chrome is not firefox
        assert edge is not firefox

    def test_cache_key_collision_safe_across_types(self, factory):
        """cookie_handler_edge 和 path_selector_edge 不应冲突。"""
        ch = factory.get_cookie_handler("edge")
        ps = factory.get_path_selector("edge")  # save_mode 也叫 "edge"，不应冲突
        # 它们的 key 不同（cookie_handler_edge vs path_selector_edge）
        # 但断言 count = 2
        assert factory.get_instance_count() == 2
        assert ch is not ps


class TestGetPathSelector:
    def test_caches_by_save_mode(self, factory):
        a = factory.get_path_selector("1")
        b = factory.get_path_selector("1")
        assert a is b
        assert isinstance(a, PathSelector)

    def test_different_save_modes_return_different(self, factory):
        s1 = factory.get_path_selector("1")
        s2 = factory.get_path_selector("2")
        assert s1 is not s2


class TestGetNM3u8DLRE:
    def test_singleton(self, factory):
        a = factory.get_n_m3u8dl_re()
        b = factory.get_n_m3u8dl_re()
        assert a is b
        assert isinstance(a, NM3u8DLRE)

    def test_counted_as_one_instance(self, factory):
        factory.get_n_m3u8dl_re()
        factory.get_n_m3u8dl_re()
        assert factory.get_instance_count() == 1


class TestGetM3u8RefreshService:
    def test_caches_by_browser_id(self, factory):
        """id(browser) 作为 key，同一对象两次调用返回同一 service。"""
        browser = Mock()
        a = factory.get_m3u8_refresh_service(browser)
        b = factory.get_m3u8_refresh_service(browser)
        assert a is b
        assert isinstance(a, M3u8RefreshService)

    def test_different_browsers_return_different_services(self, factory):
        b1 = Mock()
        b2 = Mock()
        s1 = factory.get_m3u8_refresh_service(b1)
        s2 = factory.get_m3u8_refresh_service(b2)
        assert s1 is not s2

    def test_id_is_used_as_cache_key(self, factory):
        """两个等值 Mock id 不同 → 产生两个 service。"""
        m1 = Mock()
        m2 = Mock()
        # 强制相同 id 不能（id 是 CPython 对象内存地址）
        # 仅验证两个不同 Mock 不会撞 key
        assert id(m1) != id(m2)
        s1 = factory.get_m3u8_refresh_service(m1)
        s2 = factory.get_m3u8_refresh_service(m2)
        assert s1 is not s2


class TestClearInstances:
    def test_clear_empties_cache(self, factory):
        factory.get_cookie_handler("edge")
        factory.get_path_selector("1")
        factory.get_n_m3u8dl_re()
        assert factory.get_instance_count() == 3

        factory.clear_instances()
        assert factory.get_instance_count() == 0

    def test_after_clear_new_instances_created(self, factory):
        first = factory.get_cookie_handler("edge")
        factory.clear_instances()
        second = factory.get_cookie_handler("edge")
        # 新实例（构造时通常会重置内部状态）— 这里只断言 is not
        assert first is not second

    def test_clear_is_idempotent(self, factory):
        factory.clear_instances()
        factory.clear_instances()
        assert factory.get_instance_count() == 0
