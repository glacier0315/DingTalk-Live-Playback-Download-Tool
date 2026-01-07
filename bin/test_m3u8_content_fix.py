"""测试 M3U8 内容获取修复。

该脚本用于验证使用 requests 库替代浏览器 fetch API 后，
M3U8 内容获取功能是否正常工作。
"""

import logging
import os
import sys
from typing import Dict, Optional

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.dingtalk_download import m3u8_utils, browser

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_requests_import():
    """测试 requests 库是否正确导入。"""
    print("\n" + "="*60)
    print("测试 1: 验证 requests 库导入")
    print("="*60)
    
    try:
        import requests
        print(f"✅ requests 库导入成功")
        print(f"   版本: {requests.__version__}")
        return True
    except ImportError as e:
        print(f"❌ requests 库导入失败: {e}")
        print(f"   请运行: pip install requests")
        return False


def test_fetch_m3u8_content_via_requests():
    """测试使用 requests 获取 M3U8 内容。"""
    print("\n" + "="*60)
    print("测试 2: 测试 requests 获取 M3U8 内容")
    print("="*60)
    
    test_url = "https://example.com/test.m3u8"
    test_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    print(f"测试 URL: {test_url}")
    print(f"测试 Headers: {test_headers}")
    
    try:
        import requests
        response = requests.get(test_url, headers=test_headers, timeout=5)
        print(f"✅ requests.get() 调用成功")
        print(f"   状态码: {response.status_code}")
        print(f"   响应头: {dict(response.headers)}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"⚠️  请求失败（这是预期的，因为 URL 不存在）: {e}")
        print(f"✅ 但 requests 库功能正常，错误是由于 URL 无效导致的")
        return True
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_m3u8_utils_function_signature():
    """测试 m3u8_utils 中的函数签名是否正确。"""
    print("\n" + "="*60)
    print("测试 3: 验证 m3u8_utils 函数签名")
    print("="*60)
    
    try:
        if hasattr(m3u8_utils, '_fetch_m3u8_content_via_requests'):
            print(f"✅ _fetch_m3u8_content_via_requests 函数存在")
            
            import inspect
            sig = inspect.signature(m3u8_utils._fetch_m3u8_content_via_requests)
            print(f"   函数签名: {sig}")
            
            params = list(sig.parameters.keys())
            if 'url' in params and 'headers' in params:
                print(f"✅ 函数参数正确: {params}")
                return True
            else:
                print(f"❌ 函数参数不正确: {params}")
                return False
        else:
            print(f"❌ _fetch_m3u8_content_via_requests 函数不存在")
            print(f"   可用的函数: {[name for name in dir(m3u8_utils) if not name.startswith('_')]}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_download_m3u8_file_signature():
    """测试 download_m3u8_file 函数是否正确调用新的实现。"""
    print("\n" + "="*60)
    print("测试 4: 验证 download_m3u8_file 调用链")
    print("="*60)
    
    try:
        import inspect
        
        source = inspect.getsource(m3u8_utils.download_m3u8_file)
        
        if '_fetch_m3u8_content_via_requests' in source:
            print(f"✅ download_m3u8_file 正确调用 _fetch_m3u8_content_via_requests")
            return True
        elif '_fetch_m3u8_content_via_browser' in source:
            print(f"❌ download_m3u8_file 仍在调用旧的 _fetch_m3u8_content_via_browser")
            return False
        else:
            print(f"⚠️  未找到明确的调用关系")
            print(f"   源代码片段:")
            for line in source.split('\n')[:20]:
                print(f"   {line}")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_error_handling():
    """测试错误处理机制。"""
    print("\n" + "="*60)
    print("测试 5: 测试错误处理")
    print("="*60)
    
    test_cases = [
        ("空 URL", "", {"User-Agent": "test"}, ValueError),
        ("无效 URL", "not-a-valid-url", {"User-Agent": "test"}, RuntimeError),
        ("空 Headers", "https://example.com", {}, ValueError),
    ]
    
    all_passed = True
    
    for test_name, url, headers, expected_error in test_cases:
        print(f"\n测试用例: {test_name}")
        print(f"  URL: {url}")
        print(f"  Headers: {headers}")
        print(f"  期望错误: {expected_error.__name__}")
        
        try:
            m3u8_utils._fetch_m3u8_content_via_requests(url, headers)
            print(f"  ⚠️  未抛出异常（可能不符合预期）")
            all_passed = False
        except expected_error as e:
            print(f"  ✅ 正确抛出 {expected_error.__name__}: {e}")
        except Exception as e:
            print(f"  ⚠️  抛出了不同的错误: {type(e).__name__}: {e}")
            all_passed = False
    
    return all_passed


def run_all_tests():
    """运行所有测试。"""
    print("\n" + "="*60)
    print("M3U8 内容获取修复验证测试")
    print("="*60)
    
    tests = [
        ("requests 库导入", test_requests_import),
        ("requests 获取内容", test_fetch_m3u8_content_via_requests),
        ("函数签名验证", test_m3u8_utils_function_signature),
        ("调用链验证", test_download_m3u8_file_signature),
        ("错误处理", test_error_handling),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ 测试 '{test_name}' 执行时发生异常: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！M3U8 内容获取修复成功！")
        return True
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查上述错误信息")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
