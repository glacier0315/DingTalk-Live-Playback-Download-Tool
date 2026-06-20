"""Tests for utils.validator: validate_dingtalk_url / validate_input / validate_required_input."""

from __future__ import annotations

import builtins
from unittest.mock import patch

import pytest

from dingtalk_downloader.utils.validator import (
    validate_dingtalk_url,
    validate_input,
    validate_required_input,
    validate_file_path,
)

VALID_UUID = "abcdef01-2345-6789-abcd-ef0123456789"
VALID_URL = f"https://n.dingtalk.com/live/abc?liveUuid={VALID_UUID}"


# ---------------------------------------------------------------------------
# validate_dingtalk_url
# ---------------------------------------------------------------------------


class TestValidateDingtalkUrl:
    def test_valid_https_url_passes(self):
        assert validate_dingtalk_url(VALID_URL) == VALID_URL

    def test_valid_http_url_passes(self):
        url = f"http://n.dingtalk.com/live/abc?liveUuid={VALID_UUID}"
        assert validate_dingtalk_url(url) == url

    def test_rejects_empty_url(self):
        with pytest.raises(ValueError, match="URL缺少协议"):
            validate_dingtalk_url("")

    def test_rejects_missing_scheme(self):
        url = f"n.dingtalk.com/live/abc?liveUuid={VALID_UUID}"
        with pytest.raises(ValueError, match="URL缺少协议"):
            validate_dingtalk_url(url)

    @pytest.mark.parametrize("scheme", ["ftp", "file", "javascript"])
    def test_rejects_non_http_scheme(self, scheme):
        url = f"{scheme}://n.dingtalk.com/live/abc?liveUuid={VALID_UUID}"
        with pytest.raises(ValueError, match="仅支持 http 和 https"):
            validate_dingtalk_url(url)

    def test_rejects_missing_netloc(self):
        # urlparse("https://?liveUuid=...") → scheme=https, netloc=''
        with pytest.raises(ValueError, match="URL缺少域名"):
            validate_dingtalk_url(f"https://?liveUuid={VALID_UUID}")

    @pytest.mark.parametrize(
        "netloc", ["m.dingtalk.com", "dingtalk.com", "evil.com", "n.dingtalk.com.evil.com"]
    )
    def test_rejects_wrong_domain(self, netloc):
        url = f"https://{netloc}/live/abc?liveUuid={VALID_UUID}"
        with pytest.raises(ValueError, match="钉钉直播链接"):
            validate_dingtalk_url(url)

    def test_rejects_missing_path(self):
        url = f"https://n.dingtalk.com?liveUuid={VALID_UUID}"
        with pytest.raises(ValueError, match="URL缺少路径"):
            validate_dingtalk_url(url)

    def test_rejects_missing_live_uuid_param(self):
        url = "https://n.dingtalk.com/live/abc?other=1"
        with pytest.raises(ValueError, match="缺少 liveUuid"):
            validate_dingtalk_url(url)

    def test_rejects_empty_live_uuid_branch_is_unreachable_via_urlparse(self):
        """注：parse_qs 默认 keep_blank_values=False → liveUuid= 会被丢弃，
        实际触发的是 test_rejects_missing_live_uuid_param 分支。
        "liveUuid 参数为空" 这条 dead code 分支无法通过正常 URL 触发。
        """

    @pytest.mark.parametrize(
        "bad_uuid",
        [
            "abcdef01-2345-6789-abcd-ef012345678",  # 35 字符
            "abcdef01-2345-6789-abcd-ef0123456789a",  # 37 字符
            "ABCDEF01-2345-6789-ABCD-EF0123456789",  # 大写
            "gbcdef01-2345-6789-abcd-ef0123456789",  # 非法字符 g
            "abcdef01_2345_6789_abcd_ef0123456789",  # 用下划线
        ],
    )
    def test_rejects_malformed_live_uuid(self, bad_uuid):
        url = f"https://n.dingtalk.com/live/abc?liveUuid={bad_uuid}"
        with pytest.raises(ValueError, match="liveUuid 格式无效"):
            validate_dingtalk_url(url)

    @pytest.mark.parametrize(
        "good_uuid",
        [
            "00000000-0000-0000-0000-000000000000",
            "ffffffff-ffff-ffff-ffff-ffffffffffff",
            "01234567-89ab-cdef-0123-456789abcdef",
        ],
    )
    def test_accepts_various_valid_uuids(self, good_uuid):
        url = f"https://n.dingtalk.com/live/abc?liveUuid={good_uuid}"
        assert validate_dingtalk_url(url) == url


# ---------------------------------------------------------------------------
# validate_input
# ---------------------------------------------------------------------------


def _make_input(responses: list, raises_after: list = None):
    """构造 input stub：依次返回 responses 中的值；可选 raises_after 在某 index 后抛异常。"""
    queue = list(responses)
    raises = list(raises_after or [])
    call_count = {"n": 0}

    def fake_input(prompt=""):
        idx = call_count["n"]
        call_count["n"] += 1
        if idx < len(raises):
            exc = raises[idx]
            raise exc
        if idx < len(queue):
            return queue[idx]
        # 默认行为：所有输入用完后再被调用 → 抛 EOFError 终止循环
        raise EOFError()

    return fake_input, call_count


class TestValidateInput:
    def test_returns_valid_choice_immediately(self):
        fake, _ = _make_input(["1"])
        with patch.object(builtins, "input", fake):
            result = validate_input("> ", ["1", "2"])
        assert result == "1"

    def test_retries_until_valid(self):
        fake, calls = _make_input(["3", "3", "2"])
        with patch.object(builtins, "input", fake):
            result = validate_input("> ", ["1", "2"])
        assert result == "2"
        assert calls["n"] == 3

    def test_empty_input_uses_default_option(self):
        fake, _ = _make_input(["", "1"])
        with patch.object(builtins, "input", fake):
            result = validate_input("> ", ["1", "2"], default_option="1")
        assert result == "1"

    def test_validation_func_rejects_then_accepts(self):
        fake, _ = _make_input(["a", "12"])
        with patch.object(builtins, "input", fake):
            result = validate_input(
                "> ", ["12", "abc"],  # 合法选项必须包含 12
                validation_func=lambda s: s.isdigit(),
            )
        assert result == "12"

    def test_validation_func_custom_error_message(self):
        fake, _ = _make_input(["a", "1"])
        with patch.object(builtins, "input", fake):
            result = validate_input(
                "> ", ["1", "2"],
                validation_func=lambda s: s.isdigit(),
                error_message="请输入数字!",
            )
        assert result == "1"

    def test_eof_returns_default_when_provided(self):
        fake, _ = _make_input([], raises_after=[EOFError()])
        with patch.object(builtins, "input", fake):
            result = validate_input("> ", ["1", "2"], default_option="1")
        assert result == "1"

    def test_eof_without_default_raises(self):
        fake, _ = _make_input([], raises_after=[EOFError()])
        with patch.object(builtins, "input", fake):
            with pytest.raises(EOFError):
                validate_input("> ", ["1", "2"])

    def test_keyboard_interrupt_re_raises(self):
        fake, _ = _make_input([], raises_after=[KeyboardInterrupt()])
        with patch.object(builtins, "input", fake):
            with pytest.raises(KeyboardInterrupt):
                validate_input("> ", ["1", "2"], default_option="1")

    def test_other_exception_propagates(self):
        """非 EOF/KeyboardInterrupt 异常不被吞，直接向上传播。"""
        fake, _ = _make_input([], raises_after=[ValueError("unexpected")])
        with patch.object(builtins, "input", fake):
            with pytest.raises(ValueError, match="unexpected"):
                validate_input("> ", ["1", "2"])


# ---------------------------------------------------------------------------
# validate_required_input
# ---------------------------------------------------------------------------


class TestValidateRequiredInput:
    def test_returns_input_after_strip(self):
        fake, _ = _make_input(["  hello  "])
        with patch.object(builtins, "input", fake):
            assert validate_required_input("> ") == "hello"

    def test_retries_on_empty(self):
        fake, _ = _make_input(["", "  ", "ok"])
        with patch.object(builtins, "input", fake):
            assert validate_required_input("> ") == "ok"

    def test_validation_func_accepts_valid(self):
        fake, _ = _make_input(["good"])
        with patch.object(builtins, "input", fake):
            assert validate_required_input(
                "> ", validation_func=lambda s: s.startswith("g")
            ) == "good"

    def test_validation_func_retries_until_valid(self):
        fake, _ = _make_input(["bad", "worse", "good"])
        with patch.object(builtins, "input", fake):
            assert validate_required_input(
                "> ", validation_func=lambda s: s == "good"
            ) == "good"

    def test_validation_func_value_error_treated_as_invalid(self):
        def strict(s):
            if s == "bad":
                raise ValueError("explicitly bad")
            return s == "good"

        fake, _ = _make_input(["bad", "good"])
        with patch.object(builtins, "input", fake):
            assert validate_required_input(
                "> ", validation_func=strict, error_message="bad value"
            ) == "good"

    def test_eof_on_empty_raises(self):
        fake, _ = _make_input([], raises_after=[EOFError()])
        with patch.object(builtins, "input", fake):
            with pytest.raises(EOFError):
                validate_required_input("> ")

    def test_keyboard_interrupt_re_raises(self):
        fake, _ = _make_input([], raises_after=[KeyboardInterrupt()])
        with patch.object(builtins, "input", fake):
            with pytest.raises(KeyboardInterrupt):
                validate_required_input("> ")


# ---------------------------------------------------------------------------
# validate_file_path (re-export)
# ---------------------------------------------------------------------------


class TestValidateFilePathReexport:
    def test_delegates_to_file_validator(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        p = tmp_path / "data.csv"
        p.write_bytes(b"a,b\n1,2\n")
        result = validate_file_path(str(p))
        assert result == str(p)
