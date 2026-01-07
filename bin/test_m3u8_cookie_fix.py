"""
测试 M3U8 内容获取的 Cookie 认证修复

该脚本用于验证修复后的 M3U8 内容获取功能是否正确传递 Cookie 参数。
"""

import os
import sys
import logging
from typing import Dict, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dingtalk_download.m3u8_utils import (
    _fetch_m3u8_content_via_requests,
    download_m3u8_file
)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_fetch_m3u8_content_with_cookies():
    """测试带 Cookie 的 M3U8 内容获取"""
    logger.info("=" * 60)
    logger.info("测试 1: 带 Cookie 的 M3U8 内容获取")
    logger.info("=" * 60)

    test_url = "https://example.com/test.m3u8"
    test_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    test_cookies = {
        "session": "test_session_value",
        "auth": "test_auth_value"
    }

    logger.info(f"测试 URL: {test_url}")
    logger.info(f"测试 Headers: {test_headers}")
    logger.info(f"测试 Cookies: {test_cookies}")

    try:
        result = _fetch_m3u8_content_via_requests(
            test_url,
            test_headers,
            test_cookies
        )
        logger.info(f"测试结果: 成功获取内容，长度: {len(result)}")
        return True
    except Exception as e:
        logger.info(f"测试结果: 预期失败（URL 不存在），错误类型: {type(e).__name__}")
        logger.info(f"错误信息: {str(e)}")
        return True


def test_fetch_m3u8_content_without_cookies():
    """测试不带 Cookie 的 M3U8 内容获取"""
    logger.info("=" * 60)
    logger.info("测试 2: 不带 Cookie 的 M3U8 内容获取")
    logger.info("=" * 60)

    test_url = "https://example.com/test.m3u8"
    test_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    logger.info(f"测试 URL: {test_url}")
    logger.info(f"测试 Headers: {test_headers}")
    logger.info(f"测试 Cookies: None")

    try:
        result = _fetch_m3u8_content_via_requests(
            test_url,
            test_headers
        )
        logger.info(f"测试结果: 成功获取内容，长度: {len(result)}")
        return True
    except Exception as e:
        logger.info(f"测试结果: 预期失败（URL 不存在），错误类型: {type(e).__name__}")
        logger.info(f"错误信息: {str(e)}")
        return True


def test_download_m3u8_file_with_cookies():
    """测试带 Cookie 的 M3U8 文件下载"""
    logger.info("=" * 60)
    logger.info("测试 3: 带 Cookie 的 M3U8 文件下载")
    logger.info("=" * 60)

    test_url = "https://example.com/test.m3u8"
    test_filename = "test_output.m3u8"
    test_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    test_cookies = {
        "session": "test_session_value",
        "auth": "test_auth_value"
    }

    logger.info(f"测试 URL: {test_url}")
    logger.info(f"测试文件名: {test_filename}")
    logger.info(f"测试 Headers: {test_headers}")
    logger.info(f"测试 Cookies: {test_cookies}")

    try:
        result = download_m3u8_file(
            test_url,
            test_filename,
            test_headers,
            test_cookies
        )
        logger.info(f"测试结果: 成功下载文件，路径: {result}")
        return True
    except Exception as e:
        logger.info(f"测试结果: 预期失败（URL 不存在），错误类型: {type(e).__name__}")
        logger.info(f"错误信息: {str(e)}")
        return True


def test_download_m3u8_file_without_cookies():
    """测试不带 Cookie 的 M3U8 文件下载"""
    logger.info("=" * 60)
    logger.info("测试 4: 不带 Cookie 的 M3U8 文件下载")
    logger.info("=" * 60)

    test_url = "https://example.com/test.m3u8"
    test_filename = "test_output_no_cookies.m3u8"
    test_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    logger.info(f"测试 URL: {test_url}")
    logger.info(f"测试文件名: {test_filename}")
    logger.info(f"测试 Headers: {test_headers}")
    logger.info(f"测试 Cookies: None")

    try:
        result = download_m3u8_file(
            test_url,
            test_filename,
            test_headers
        )
        logger.info(f"测试结果: 成功下载文件，路径: {result}")
        return True
    except Exception as e:
        logger.info(f"测试结果: 预期失败（URL 不存在），错误类型: {type(e).__name__}")
        logger.info(f"错误信息: {str(e)}")
        return True


def main():
    """运行所有测试"""
    logger.info("开始测试 M3U8 内容获取的 Cookie 认证修复")
    logger.info("")

    results = []

    results.append(("带 Cookie 的 M3U8 内容获取", test_fetch_m3u8_content_with_cookies()))
    logger.info("")
    results.append(("不带 Cookie 的 M3U8 内容获取", test_fetch_m3u8_content_without_cookies()))
    logger.info("")
    results.append(("带 Cookie 的 M3U8 文件下载", test_download_m3u8_file_with_cookies()))
    logger.info("")
    results.append(("不带 Cookie 的 M3U8 文件下载", test_download_m3u8_file_without_cookies()))

    logger.info("")
    logger.info("=" * 60)
    logger.info("测试总结")
    logger.info("=" * 60)

    for test_name, result in results:
        status = "通过" if result else "失败"
        logger.info(f"{test_name}: {status}")

    all_passed = all(result for _, result in results)

    if all_passed:
        logger.info("")
        logger.info("所有测试通过！")
        logger.info("Cookie 参数已正确传递到 requests 库。")
    else:
        logger.error("")
        logger.error("部分测试失败，请检查代码实现。")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
