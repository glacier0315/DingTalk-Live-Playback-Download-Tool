"""
钉钉直播回放下载工具 - 功能测试

本模块测试修复后的 m3u8 下载功能。

作者：项目团队
依赖：pytest, unittest.mock
创建日期：2025-01-15
修改历史：
    - 2025-01-15: 初始版本，验证 m3u8 下载修复
    - 2026-01-22: 更新测试以适配新的异常处理机制
"""

import sys
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.core.m3u8_parser import M3u8Parser, M3u8ParseError
from dingtalk_downloader.config.constants import BROWSER_TYPE_EDGE


def test_m3u8_download_without_headers():
    """
    功能测试：验证 m3u8 下载不使用 headers 参数

    测试场景：
    1. 模拟浏览器执行 fetch 请求
    2. 验证只传递 URL，不传递 headers
    3. 验证使用浏览器默认请求头（包括 Cookie）
    """
    mock_browser = Mock()
    mock_browser.driver = Mock()

    # 模拟浏览器返回 m3u8 内容
    m3u8_content = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXTINF:10.0,
segment1.ts
#EXTINF:10.0,
segment2.ts
#EXT-X-ENDLIST
"""
    mock_browser.driver.execute_script.return_value = m3u8_content

    parser = M3u8Parser(mock_browser, BROWSER_TYPE_EDGE)

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".m3u8") as temp_file:
        temp_path = temp_file.name

    try:
        # 调用下载方法，传入空的 headers 字典
        headers = {}
        result = parser.download_m3u8_file(
            "https://dtliving-sz.dingtalk.com/live/test.m3u8", temp_path, headers
        )

        # 验证文件已创建
        assert result == temp_path
        assert os.path.exists(temp_path)

        # 验证文件内容正确
        with open(temp_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert content == m3u8_content
            assert "#EXTM3U" in content
            assert "segment1.ts" in content

        # 验证 execute_script 只被调用一次，且只传递了 URL 参数
        assert mock_browser.driver.execute_script.call_count == 1
        call_args = mock_browser.driver.execute_script.call_args

        # 验证 JavaScript 代码不包含 headers 参数
        js_code = call_args[0][0]
        assert "headers: arguments[1]" not in js_code
        assert "method: 'GET'" in js_code

        # 验证只传递了两个参数（script 和 url）
        assert len(call_args[0]) == 2
        assert call_args[0][1] == "https://dtliving-sz.dingtalk.com/live/test.m3u8"

        print("✓ 功能测试通过：m3u8 下载不使用 headers 参数")

    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_m3u8_download_with_headers_parameter():
    """
    功能测试：验证即使传入 headers 参数也不会被使用

    测试场景：
    1. 传入完整的 headers 字典
    2. 验证 headers 参数被忽略
    3. 验证使用浏览器默认请求头
    """
    mock_browser = Mock()
    mock_browser.driver = Mock()

    m3u8_content = "#EXTM3U\n#EXT-X-VERSION:3\n"
    mock_browser.driver.execute_script.return_value = m3u8_content

    parser = M3u8Parser(mock_browser, BROWSER_TYPE_EDGE)

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".m3u8") as temp_file:
        temp_path = temp_file.name

    try:
        # 传入完整的 headers 字典
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://n.dingtalk.com/",
            "Accept": "application/vnd.apple.mpegurl, text/plain, */*",
            "Cookie": "test=value",
        }

        result = parser.download_m3u8_file(
            "https://dtliving-sz.dingtalk.com/live/test.m3u8", temp_path, headers
        )

        # 验证文件已创建
        assert result == temp_path
        assert os.path.exists(temp_path)

        # 验证 execute_script 只传递了 URL，没有传递 headers
        call_args = mock_browser.driver.execute_script.call_args
        assert len(call_args[0]) == 2  # 只有 script 和 url

        # 验证 headers 字典没有被传递给 JavaScript
        assert len(call_args[0]) == 2
        assert call_args[0][1] == "https://dtliving-sz.dingtalk.com/live/test.m3u8"

        print("✓ 功能测试通过：headers 参数被正确忽略")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_m3u8_download_error_handling():
    """
    功能测试：验证错误处理机制

    测试场景：
    1. 模拟 fetch 请求失败
    2. 验证 M3u8ParseError 异常被正确抛出
    """
    mock_browser = Mock()
    mock_browser.driver = Mock()

    # 模拟 fetch 请求失败
    mock_browser.driver.execute_script.side_effect = Exception("Failed to fetch")

    parser = M3u8Parser(mock_browser, BROWSER_TYPE_EDGE)

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".m3u8") as temp_file:
        temp_path = temp_file.name

    try:
        # 验证异常被正确抛出
        from dingtalk_downloader.core.m3u8_parser import M3u8ParseError

        try:
            parser.download_m3u8_file(
                "https://dtliving-sz.dingtalk.com/live/test.m3u8", temp_path, {}
            )
            assert False, "应该抛出 M3u8ParseError 异常"
        except M3u8ParseError as e:
            assert "下载m3u8文件失败" in str(e)
            assert "Failed to fetch" in str(e)

        print("✓ 功能测试通过：错误处理机制正常")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_m3u8_download_real_scenario():
    """
    功能测试：模拟真实场景

    测试场景：
    1. 模拟真实的钉钉 m3u8 URL
    2. 模拟浏览器已登录状态（通过 Cookie）
    3. 验证下载流程完整
    """
    mock_browser = Mock()
    mock_browser.driver = Mock()

    # 模拟真实的 m3u8 内容（注意：segment URL 使用 live_hp 路径）
    m3u8_content = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:6
#EXT-X-MEDIA-SEQUENCE:0
#EXTINF:6.0,
https://dtliving-sz.dingtalk.com/live_hp/9f3171a7-3b52-47ca-917a-bcc2f02e33f5/segment_0.ts
#EXTINF:6.0,
https://dtliving-sz.dingtalk.com/live_hp/9f3171a7-3b52-47ca-917a-bcc2f02e33f5/segment_1.ts
#EXT-X-ENDLIST
"""
    mock_browser.driver.execute_script.return_value = m3u8_content

    parser = M3u8Parser(mock_browser, BROWSER_TYPE_EDGE)

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".m3u8") as temp_file:
        temp_path = temp_file.name

    try:
        # 使用真实的钉钉 URL 格式（注意：m3u8 文件 URL 使用 live 路径）
        real_url = "https://dtliving-sz.dingtalk.com/live/9f3171a7-3b52-47ca-917a-bcc2f02e33f5_normal.m3u8?auth_key=test"

        result = parser.download_m3u8_file(real_url, temp_path, {})

        # 验证下载成功
        assert result == temp_path
        assert os.path.exists(temp_path)

        # 验证文件内容
        with open(temp_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "segment_0.ts" in content
            assert "segment_1.ts" in content

        # 验证 extract_prefix 方法能正确从 m3u8 内容中提取基础 URL
        # 注意：extract_prefix 应该从 m3u8 内容中的 segment URL 提取前缀
        segment_url = "https://dtliving-sz.dingtalk.com/live_hp/9f3171a7-3b52-47ca-917a-bcc2f02e33f5/segment_0.ts"
        prefix = parser.extract_prefix(segment_url)
        assert "live_hp/9f3171a7-3b52-47ca-917a-bcc2f02e33f5" in prefix

        print("✓ 功能测试通过：真实场景模拟成功")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("开始执行功能测试...")
    print("=" * 60 + "\n")

    test_m3u8_download_without_headers()
    test_m3u8_download_with_headers_parameter()
    test_m3u8_download_error_handling()
    test_m3u8_download_real_scenario()

    print("\n" + "=" * 60)
    print("所有功能测试通过！✓")
    print("=" * 60 + "\n")
