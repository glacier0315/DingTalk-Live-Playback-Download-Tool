"""非交互式测试 M3U8 功能模块。"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from dingtalk_download import m3u8_utils


def test_extract_live_uuid():
    """测试 liveUuid 提取功能。"""
    print("\n" + "=" * 80)
    print("测试 1: 提取 liveUuid")
    print("=" * 80)

    test_urls = [
        "https://n.dingtalk.com/live?liveUuid=6b145224-17b9-486b-904f-5e2b79e90bec",
        "https://n.dingtalk.com/live?roomId=ijOBB2PlE4&liveUuid=abc123",
        "https://n.dingtalk.com/live",
        ""
    ]

    for url in test_urls:
        try:
            uuid = m3u8_utils.extract_live_uuid(url)
            print(f"✓ URL: {url}")
            print(f"  提取结果: {uuid}")
        except Exception as e:
            print(f"✗ URL: {url}")
            print(f"  错误: {e}")


def test_extract_prefix():
    """测试 URL 前缀提取功能。"""
    print("\n" + "=" * 80)
    print("测试 2: 提取 URL 前缀")
    print("=" * 80)

    test_urls = [
        "https://n.dingtalk.com/live_hp/6b145224-17b9-486b-904f-5e2b79e90bec/video.m3u8",
        "https://example.com/video.m3u8",
        ""
    ]

    for url in test_urls:
        try:
            prefix = m3u8_utils.extract_prefix(url)
            print(f"✓ URL: {url}")
            print(f"  提取结果: {prefix}")
        except Exception as e:
            print(f"✗ URL: {url}")
            print(f"  错误: {e}")


def test_parse_chrome_edge_log():
    """测试 Chrome/Edge 日志解析功能。"""
    print("\n" + "=" * 80)
    print("测试 3: 解析 Chrome/Edge 日志")
    print("=" * 80)

    test_logs = [
        {
            'message': '{"message":{"method":"Network.requestWillBeSent","params":{"request":{"url":"https://n.dingtalk.com/live_hp/6b145224-17b9-486b-904f-5e2b79e90bec/video.m3u8?token=abc123"}}}}',
            'live_uuid': '6b145224-17b9-486b-904f-5e2b79e90bec'
        },
        {
            'message': '{"message":{"method":"Network.requestWillBeSent","params":{"request":{"url":"https://example.com/video.m3u8"}}}}',
            'live_uuid': '6b145224-17b9-486b-904f-5e2b79e90bec'
        },
        {
            'message': '{"message":{"method":"Network.requestWillBeSent","params":{"request":{"url":"https://n.dingtalk.com/live_hp/abc123/video.m3u8"}}}}',
            'live_uuid': '6b145224-17b9-486b-904f-5e2b79e90bec'
        }
    ]

    for test_case in test_logs:
        log_message = test_case['message']
        live_uuid = test_case['live_uuid']
        
        try:
            result = m3u8_utils._parse_chrome_edge_log(log_message, live_uuid)
            print(f"✓ 日志: {log_message[:100]}...")
            print(f"  liveUuid: {live_uuid}")
            print(f"  解析结果: {result}")
        except Exception as e:
            print(f"✗ 日志: {log_message[:100]}...")
            print(f"  错误: {e}")


def main():
    """主函数。"""
    print("\n" + "=" * 80)
    print("M3U8 功能模块单元测试")
    print("=" * 80)

    test_extract_live_uuid()
    test_extract_prefix()
    test_parse_chrome_edge_log()

    print("\n" + "=" * 80)
    print("所有测试完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
