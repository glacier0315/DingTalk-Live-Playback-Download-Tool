"""M3U8 链接获取调试脚本。

该脚本用于测试和调试 M3U8 链接获取功能。
可以帮助诊断无法获取 M3U8 链接的问题。

Usage:
    python bin/debug_m3u8.py
"""

import logging
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from dingtalk_download import browser, m3u8_utils

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('Logs/debug_m3u8.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


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


def test_with_real_browser():
    """使用真实浏览器测试 M3U8 链接获取。"""
    print("\n" + "=" * 80)
    print("测试 4: 使用真实浏览器获取 M3U8 链接")
    print("=" * 80)

    dingtalk_url = input("\n请输入钉钉直播回放链接（或按 Enter 跳过）: ").strip()
    
    if not dingtalk_url:
        print("跳过真实浏览器测试")
        return

    browser_type = input("请选择浏览器类型（1: Edge, 2: Chrome, 3: Firefox，默认: 1）: ").strip() or "1"
    browser_type_map = {"1": "edge", "2": "chrome", "3": "firefox"}
    browser_type = browser_type_map.get(browser_type, "edge")

    print(f"\n正在启动 {browser_type} 浏览器...")

    try:
        br = browser.create_browser(browser_type)
        br.get(dingtalk_url)

        input("\n请在浏览器中登录钉钉账户后，按 Enter 键继续...")

        print("\n开始获取 M3U8 链接...")
        m3u8_links = m3u8_utils.fetch_m3u8_links(br, browser_type, dingtalk_url)

        if m3u8_links:
            print(f"\n✅ 成功获取到 {len(m3u8_links)} 个 M3U8 链接:")
            for idx, link in enumerate(m3u8_links, 1):
                print(f"  {idx}. {link}")
        else:
            print("\n❌ 未能获取到 M3U8 链接")
            print("请检查：")
            print("  1. 钉钉直播页面是否已完全加载")
            print("  2. 浏览器是否已登录钉钉账户")
            print("  3. 直播回放链接是否有效")
            print("  4. 网络连接是否正常")

        input("\n按 Enter 键关闭浏览器...")
        br.quit()

    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        logger.error("测试失败", exc_info=True)


def main():
    """主函数。"""
    print("\n" + "=" * 80)
    print("M3U8 链接获取调试工具")
    print("=" * 80)

    print("\n请选择测试项目：")
    print("1. 测试 liveUuid 提取")
    print("2. 测试 URL 前缀提取")
    print("3. 测试 Chrome/Edge 日志解析")
    print("4. 使用真实浏览器测试")
    print("5. 运行所有测试")
    print("0. 退出")

    choice = input("\n请输入选项（0-5）: ").strip()

    if choice == "1":
        test_extract_live_uuid()
    elif choice == "2":
        test_extract_prefix()
    elif choice == "3":
        test_parse_chrome_edge_log()
    elif choice == "4":
        test_with_real_browser()
    elif choice == "5":
        test_extract_live_uuid()
        test_extract_prefix()
        test_parse_chrome_edge_log()
        test_with_real_browser()
    elif choice == "0":
        print("退出调试工具")
        return
    else:
        print("无效的选项")

    print("\n" + "=" * 80)
    print("调试完成")
    print("=" * 80)
    print(f"\n详细日志已保存到: {Path.cwd() / 'Logs' / 'debug_m3u8.log'}")


if __name__ == "__main__":
    main()
