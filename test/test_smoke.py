#!/usr/bin/env python3
"""钉钉直播回放下载工具 - 单元测试"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest


def test_utils_module():
    """测试工具模块"""
    from dingtalk_download.utils import validate_input, clean_file_path, get_executable_name
    
    assert callable(validate_input)
    assert callable(clean_file_path)
    assert callable(get_executable_name)
    
    assert clean_file_path('  "test"  ') == 'test'
    print("[PASS] utils module imports correctly")


def test_link_handler_module():
    """测试链接处理模块"""
    from dingtalk_download.link_handler import read_links_file, extract_live_uuid
    
    assert callable(read_links_file)
    assert callable(extract_live_uuid)
    
    test_url = "https://n.dingtalk.com/live?liveUuid=abc123"
    assert extract_live_uuid(test_url) == "abc123"
    print("[PASS] link_handler module imports correctly")


def test_browser_module():
    """测试浏览器模块"""
    from dingtalk_download.browser import get_browser_options
    
    assert callable(get_browser_options)
    
    edge_config = get_browser_options('edge')
    assert edge_config is not None
    assert edge_config['type'] == 'edge'
    print("[PASS] browser module imports correctly")


def test_m3u8_utils_module():
    """测试M3U8工具模块"""
    from dingtalk_download.m3u8_utils import extract_prefix
    
    assert callable(extract_prefix)
    
    test_url = "https://example.com/live_hp/abc123-def456/chunklist.m3u8"
    result = extract_prefix(test_url)
    assert result == "https://example.com/live_hp/abc123-def456"
    print("[PASS] m3u8_utils module imports correctly")


def test_download_manager_module():
    """测试下载管理器模块"""
    from dingtalk_download.download_manager import (
        auto_download_m3u8_with_options,
        download_m3u8_with_options,
        download_m3u8_with_reused_path
    )
    
    assert callable(auto_download_m3u8_with_options)
    assert callable(download_m3u8_with_options)
    assert callable(download_m3u8_with_reused_path)
    print("[PASS] download_manager module imports correctly")


def test_main_module():
    """测试主程序模块"""
    from dingtalk_download.main import single_mode, batch_mode, main
    
    assert callable(single_mode)
    assert callable(batch_mode)
    assert callable(main)
    print("[PASS] main module imports correctly")


def test_package_exports():
    """测试包导出"""
    import dingtalk_download
    
    expected_exports = [
        'validate_input',
        'clean_file_path',
        'get_executable_name',
        'read_links_file',
        'extract_live_uuid',
        'get_browser_options',
        'get_browser_cookie',
        'extract_prefix',
        'fetch_m3u8_links',
        'download_m3u8_file',
        'single_mode',
        'batch_mode',
        'main'
    ]
    
    for export in expected_exports:
        assert hasattr(dingtalk_download, export), f"Missing export: {export}"
    
    print("[PASS] package exports are correct")


def run_all_tests():
    """运行所有基本功能测试"""
    print("Running functional smoke tests...")
    print("-" * 50)
    
    test_utils_module()
    test_link_handler_module()
    test_browser_module()
    test_m3u8_utils_module()
    test_download_manager_module()
    test_main_module()
    test_package_exports()
    
    print("-" * 50)
    print("All functional smoke tests passed!")


if __name__ == '__main__':
    run_all_tests()
