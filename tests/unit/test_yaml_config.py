"""Tests for YamlConfig singleton + CONFIG_SCHEMA validation + typed getters."""

from __future__ import annotations

import threading
from pathlib import Path

import pytest
import yaml

from dingtalk_downloader.config.yaml_config import (
    CONFIG_SCHEMA,
    ConfigError,
    ConfigLoadError,
    ConfigValidationError,
    ConfigValueError,
    YamlConfig,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def _reset_yaml_singleton():
    """每个测试前后重置 YamlConfig 单例，避免污染其它测试。"""
    YamlConfig.reset_instance()
    yield
    YamlConfig.reset_instance()


@pytest.fixture
def write_yaml(tmp_path):
    """Helper: 写入 yaml 内容并返回 Path。"""

    def _w(name: str, content: dict) -> Path:
        p = tmp_path / name
        p.write_text(yaml.safe_dump(content, allow_unicode=True), encoding="utf-8")
        return p

    return _w


def _valid_config(tmp_path: Path, **overrides) -> dict:
    """返回一份满足 CONFIG_SCHEMA 的最小合规 dict。"""
    cfg = {
        "app": {"name": "x", "version": "1.0", "build_date": "2026-01-01"},
        "download": {
            "default_dir": str(tmp_path / "Downloads"),
            "temp_dir": str(tmp_path / "temp"),
            "max_retry_count": 5,
        },
        "browser": {
            "default_type": "edge",
            "headless": False,
            "timeout": 30,
        },
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
            "executable_path": "assets/bin/N_m3u8DL-RE.exe",
            "ui_language": "zh-CN",
            "temp_dir": "temp",
            "log_dir": "logs",
        },
        "ffmpeg": {
            "executable_path": "assets/bin/ffmpeg.exe",
        },
    }
    # 浅层 merge（只支持顶层 key，不深 merge；测试中按需整体覆盖）
    for k, v in overrides.items():
        cfg[k] = v
    return cfg


@pytest.fixture
def valid_yaml_path(tmp_path) -> Path:
    """写入合规 yaml 并返回路径。"""
    p = tmp_path / "app.yaml"
    p.write_text(
        yaml.safe_dump(_valid_config(tmp_path), allow_unicode=True),
        encoding="utf-8",
    )
    return p


# ---------------------------------------------------------------------------
# 单例语义
# ---------------------------------------------------------------------------


class TestSingleton:
    def test_singleton_returns_same_instance(self, valid_yaml_path):
        a = YamlConfig(str(valid_yaml_path))
        b = YamlConfig(str(valid_yaml_path))
        assert a is b

    def test_get_instance_delegates_to_constructor(self, valid_yaml_path):
        a = YamlConfig.get_instance(str(valid_yaml_path))
        b = YamlConfig.get_instance(str(valid_yaml_path))
        assert a is b

    def test_singleton_ignores_second_config_file_arg(self, valid_yaml_path, tmp_path):
        first = YamlConfig(str(valid_yaml_path))
        # 第二次传另一个路径，单例仍返回首次
        other = tmp_path / "other.yaml"
        other.write_text("{}", encoding="utf-8")
        second = YamlConfig(str(other))
        assert first is second
        assert second.config_file == str(valid_yaml_path)

    def test_singleton_logs_debug_when_ignoring_second_config_file(
        self, valid_yaml_path, tmp_path, caplog
    ):
        """后续传入的 config_file 被忽略时，应输出 debug 日志便于诊断。"""
        other = tmp_path / "other.yaml"
        other.write_text("{}", encoding="utf-8")
        with caplog.at_level("DEBUG"):
            YamlConfig(str(valid_yaml_path))
            YamlConfig(str(other))
        # 至少一条 debug 提到"忽略"且引用了被忽略路径的文件名（路径分隔符在 Windows/POSIX 不同）
        other_name = other.name
        assert any(
            "忽略" in rec.message and other_name in rec.message
            for rec in caplog.records
        ), f"未捕获到 debug 日志，实际记录: {[r.message for r in caplog.records]}"

    def test_reset_instance_clears_cache(self, valid_yaml_path):
        first = YamlConfig(str(valid_yaml_path))
        first._loaded = True
        YamlConfig.reset_instance()
        # 重建后 _loaded 应为 False
        new = YamlConfig(str(valid_yaml_path))
        assert new is not first
        assert new._loaded is True  # __new__ 会自动 load
        assert new.config_file == str(valid_yaml_path)

    def test_singleton_thread_safe_under_concurrent_init(self, tmp_path):
        """并发初始化只产生一个实例。"""
        path = tmp_path / "app.yaml"
        path.write_text(
            yaml.safe_dump(_valid_config(tmp_path), allow_unicode=True),
            encoding="utf-8",
        )
        YamlConfig.reset_instance()
        results = []
        lock = threading.Lock()

        def worker():
            inst = YamlConfig(str(path))
            with lock:
                results.append(id(inst))

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(set(results)) == 1, f"期望单例，实际拿到 {set(results)}"


# ---------------------------------------------------------------------------
# Load 行为
# ---------------------------------------------------------------------------


class TestLoad:
    def test_load_raises_config_load_error_when_file_missing(self, tmp_path):
        missing = tmp_path / "nope.yaml"
        with pytest.raises(ConfigLoadError, match="配置文件不存在"):
            YamlConfig(str(missing))

    def test_load_raises_config_load_error_on_invalid_yaml(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("key: : invalid", encoding="utf-8")  # YAML 解析错误
        with pytest.raises(ConfigLoadError, match="配置文件格式错误"):
            YamlConfig(str(bad))

    def test_load_raises_config_load_error_on_io_error(self, tmp_path, monkeypatch):
        path = tmp_path / "app.yaml"
        path.write_text("app: {}", encoding="utf-8")

        def _raise(*a, **kw):
            raise IOError("disk error")

        monkeypatch.setattr("builtins.open", _raise)
        with pytest.raises(ConfigLoadError, match="读取配置文件失败"):
            YamlConfig(str(path))

    def test_load_idempotent_when_already_loaded(self, valid_yaml_path, monkeypatch):
        inst = YamlConfig(str(valid_yaml_path))
        # 二次调用 load 应当跳过；用 monkeypatch 验证 open 未被再次调用
        from unittest.mock import patch as _patch

        with _patch("builtins.open") as mock_open:
            inst.load()  # 已经 _loaded，不应再 open
            mock_open.assert_not_called()

    def test_reload_clears_and_re_reads(self, valid_yaml_path, write_yaml):
        inst = YamlConfig(str(valid_yaml_path))
        # 修改文件 → reload 后新值可见
        new_cfg = _valid_config(valid_yaml_path.parent)
        new_cfg["app"]["name"] = "modified"
        write_yaml("app.yaml", new_cfg)
        inst.reload()
        assert inst.get("app.name") == "modified"


# ---------------------------------------------------------------------------
# Schema 校验
# ---------------------------------------------------------------------------


class TestSchemaValidation:
    def test_valid_minimal_yaml_passes(self, tmp_path):
        path = tmp_path / "app.yaml"
        path.write_text(
            yaml.safe_dump(_valid_config(tmp_path), allow_unicode=True),
            encoding="utf-8",
        )
        # 不抛异常 = 通过
        inst = YamlConfig(str(path))
        assert inst.validate() is True

    @pytest.mark.parametrize(
        "missing_key",
        ["app", "download", "browser", "logging", "headers", "n_m3u8dl_re", "ffmpeg"],
    )
    def test_missing_top_level_required_key(self, tmp_path, missing_key):
        cfg = _valid_config(tmp_path)
        cfg.pop(missing_key)
        path = tmp_path / "app.yaml"
        path.write_text(yaml.safe_dump(cfg, allow_unicode=True), encoding="utf-8")
        with pytest.raises(
            (ConfigValidationError, ConfigValueError),
            match=missing_key,
        ):
            YamlConfig(str(path))

    @pytest.mark.parametrize(
        "field_path",
        [
            "app.name",
            "app.version",
            "app.build_date",
            "download.default_dir",
            "download.temp_dir",
            "download.max_retry_count",
            "browser.default_type",
            "browser.headless",
            "browser.timeout",
            "logging.level",
            "logging.dir",
            "logging.max_bytes",
            "logging.backup_count",
            "logging.retention_days",
            "n_m3u8dl_re.executable_path",
            "n_m3u8dl_re.ui_language",
            "n_m3u8dl_re.temp_dir",
            "n_m3u8dl_re.log_dir",
            "ffmpeg.executable_path",
        ],
    )
    def test_missing_required_nested_field(self, tmp_path, field_path):
        cfg = _valid_config(tmp_path)
        parts = field_path.split(".")
        # 逐层 pop
        cur = cfg
        for p in parts[:-1]:
            cur = cur[p]
        cur.pop(parts[-1])
        path = tmp_path / "app.yaml"
        path.write_text(yaml.safe_dump(cfg, allow_unicode=True), encoding="utf-8")
        with pytest.raises(
            (ConfigValidationError, ConfigValueError),
            match=field_path,
        ):
            YamlConfig(str(path))

    def test_type_mismatch_int_field(self, tmp_path):
        cfg = _valid_config(tmp_path)
        cfg["download"]["max_retry_count"] = "not-a-number"
        path = tmp_path / "app.yaml"
        path.write_text(yaml.safe_dump(cfg, allow_unicode=True), encoding="utf-8")
        with pytest.raises(ConfigValueError, match="download.max_retry_count"):
            YamlConfig(str(path))

    def test_int_min_violation(self, tmp_path):
        cfg = _valid_config(tmp_path)
        cfg["download"]["max_retry_count"] = 0
        path = tmp_path / "app.yaml"
        path.write_text(yaml.safe_dump(cfg, allow_unicode=True), encoding="utf-8")
        with pytest.raises(ConfigValueError, match="最小值"):
            YamlConfig(str(path))

    def test_int_max_violation(self, tmp_path):
        cfg = _valid_config(tmp_path)
        cfg["download"]["max_retry_count"] = 101
        path = tmp_path / "app.yaml"
        path.write_text(yaml.safe_dump(cfg, allow_unicode=True), encoding="utf-8")
        with pytest.raises(ConfigValueError, match="最大值"):
            YamlConfig(str(path))

    @pytest.mark.parametrize(
        "field,value",
        [
            ("browser.default_type", "safari"),
            ("logging.level", "VERBOSE"),
        ],
    )
    def test_choices_violation(self, tmp_path, field, value):
        cfg = _valid_config(tmp_path)
        parts = field.split(".")
        cur = cfg
        for p in parts[:-1]:
            cur = cur[p]
        cur[parts[-1]] = value
        path = tmp_path / "app.yaml"
        path.write_text(yaml.safe_dump(cfg, allow_unicode=True), encoding="utf-8")
        with pytest.raises(ConfigValueError, match=field):
            YamlConfig(str(path))

    def test_validate_public_method_returns_true(self, valid_yaml_path):
        inst = YamlConfig(str(valid_yaml_path))
        assert inst.validate() is True

    def test_validate_raises_when_corrupted_in_memory(self, valid_yaml_path):
        inst = YamlConfig(str(valid_yaml_path))
        inst.config["browser"] = []  # 故意破坏类型
        with pytest.raises(ConfigValueError, match="browser"):
            inst.validate()

    def test_schema_keys_match_known_sections(self):
        # 防回归：CONFIG_SCHEMA 顶层 key 清单被多个模块依赖
        expected = {
            "app",
            "download",
            "browser",
            "logging",
            "headers",
            "n_m3u8dl_re",
            "ffmpeg",
        }
        assert set(CONFIG_SCHEMA.keys()) == expected


# ---------------------------------------------------------------------------
# Getter 行为
# ---------------------------------------------------------------------------


class TestGetters:
    def test_get_with_dotted_key(self, valid_yaml_path, tmp_path):
        inst = YamlConfig(str(valid_yaml_path))
        assert inst.get("download.default_dir") == str(tmp_path / "Downloads")

    def test_get_returns_default_when_missing(self, valid_yaml_path):
        inst = YamlConfig(str(valid_yaml_path))
        assert inst.get("nope.deep.key", "X") == "X"

    def test_get_nested_empty_keys(self, valid_yaml_path):
        """空 keys 列表 → 循环不执行，current 保持为整个 config。"""
        inst = YamlConfig(str(valid_yaml_path))
        assert inst.get_nested([]) == inst.config

    def test_get_str_returns_default_when_value_none(self, valid_yaml_path):
        inst = YamlConfig(str(valid_yaml_path))
        # yaml 中键存在但 value 为 null → get_str 返回 default
        inst.config["download"]["max_retry_count"] = None
        assert inst.get_str("download.max_retry_count", "fallback") == "fallback"

    def test_get_str_raises_on_non_str(self, valid_yaml_path):
        inst = YamlConfig(str(valid_yaml_path))
        with pytest.raises(ConfigValueError, match="期望str"):
            inst.get_str("download.max_retry_count")

    def test_get_int_converts_string_digits(self, valid_yaml_path):
        inst = YamlConfig(str(valid_yaml_path))
        inst.config["download"]["max_retry_count"] = "42"
        assert inst.get_int("download.max_retry_count") == 42

    def test_get_int_rejects_bool_true(self, valid_yaml_path):
        inst = YamlConfig(str(valid_yaml_path))
        inst.config["download"]["max_retry_count"] = True
        with pytest.raises(ConfigValueError, match="bool不能转换为int"):
            inst.get_int("download.max_retry_count")

    def test_get_int_rejects_unparseable_string(self, valid_yaml_path):
        inst = YamlConfig(str(valid_yaml_path))
        inst.config["download"]["max_retry_count"] = "abc"
        with pytest.raises(ConfigValueError, match="无法转换为int"):
            inst.get_int("download.max_retry_count")

    def test_get_float_accepts_int(self, valid_yaml_path):
        inst = YamlConfig(str(valid_yaml_path))
        inst.config["logging"]["max_bytes"] = 1024
        assert inst.get_float("logging.max_bytes") == 1024.0

    def test_get_float_accepts_str(self, valid_yaml_path):
        inst = YamlConfig(str(valid_yaml_path))
        inst.config["logging"]["max_bytes"] = "3.14"
        assert inst.get_float("logging.max_bytes") == pytest.approx(3.14)

    @pytest.mark.parametrize("value", ["true", "1", "yes", "on", "TRUE", "Yes", "ON"])
    def test_get_bool_accepts_true_variants(self, valid_yaml_path, value):
        inst = YamlConfig(str(valid_yaml_path))
        inst.config["browser"]["headless"] = value
        assert inst.get_bool("browser.headless") is True

    @pytest.mark.parametrize("value", ["false", "0", "no", "off", "FALSE", "No", "OFF"])
    def test_get_bool_accepts_false_variants(self, valid_yaml_path, value):
        inst = YamlConfig(str(valid_yaml_path))
        inst.config["browser"]["headless"] = value
        assert inst.get_bool("browser.headless") is False

    def test_get_bool_rejects_garbage_string(self, valid_yaml_path):
        inst = YamlConfig(str(valid_yaml_path))
        inst.config["browser"]["headless"] = "maybe"
        with pytest.raises(ConfigValueError, match="无法转换为bool"):
            inst.get_bool("browser.headless")

    def test_get_list_raises_on_non_list(self, valid_yaml_path):
        inst = YamlConfig(str(valid_yaml_path))
        with pytest.raises(ConfigValueError, match="期望list"):
            inst.get_list("app")

    def test_get_dict_raises_on_non_dict(self, valid_yaml_path):
        inst = YamlConfig(str(valid_yaml_path))
        with pytest.raises(ConfigValueError, match="期望dict"):
            inst.get_dict("app.name")

    def test_get_triggers_autoload_when_not_loaded(self, valid_yaml_path, monkeypatch):
        """绕过 __new__ 的自动 load，手动模拟未加载状态。"""
        inst = YamlConfig(str(valid_yaml_path))
        inst._loaded = False
        inst.config = {}
        # 重新调 get 应当自动 load
        assert inst.get("app.name") == "x"


# ---------------------------------------------------------------------------
# 异常类
# ---------------------------------------------------------------------------


class TestConfigExceptionClasses:
    def test_config_error_with_key_message_includes_key(self):
        exc = ConfigError("bad", key="foo")
        assert "bad" in str(exc)
        assert "foo" in str(exc)
        assert exc.key == "foo"

    def test_config_error_without_key_message_only(self):
        exc = ConfigError("bad")
        assert str(exc) == "bad"
        assert exc.key is None

    def test_subclass_inheritance(self):
        for cls in (ConfigLoadError, ConfigValueError, ConfigValidationError):
            assert issubclass(cls, ConfigError)
            assert issubclass(cls, Exception)
