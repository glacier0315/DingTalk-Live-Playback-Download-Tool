#!/usr/bin/env python3
"""测试修复后的 M3U8 提取功能"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from dingtalk_download import m3u8_utils, browser

def test_m3u8_extraction():
    """测试 M3U8 提取功能"""
    
    print("=" * 60)
    print("🧪 测试修复后的 M3U8 提取功能")
    print("=" * 60)
    
    test_url = "https://n.dingtalk.com/live?liveUuid=6b145224-17b9-486b-904f-5e2b79e90bec"
    
    print(f"\n📋 测试 URL: {test_url}")
    print(f"🔍 提取 liveUuid...")
    
    live_uuid = m3u8_utils.extract_live_uuid(test_url)
    print(f"✓ liveUuid: {live_uuid}")
    
    print(f"\n🌐 创建浏览器实例...")
    try:
        br = browser.create_browser('edge')
        print(f"✓ 浏览器创建成功")
        
        print(f"\n📺 导航到测试页面...")
        br.get(test_url)
        print(f"✓ 页面加载完成")
        
        print(f"\n⏳ 请在浏览器中登录钉钉账户，然后按 Enter 继续...")
        input()
        
        print(f"\n🎯 开始测试 M3U8 链接提取...")
        m3u8_links = m3u8_utils.fetch_m3u8_links(br, 'edge', test_url)
        
        if m3u8_links:
            print(f"\n✅ 测试成功！找到 {len(m3u8_links)} 个 M3U8 链接:")
            for idx, link in enumerate(m3u8_links, 1):
                print(f"   {idx}. {link}")
        else:
            print(f"\n❌ 测试失败：未能找到 M3U8 链接")
            print(f"💡 请检查:")
            print(f"   1. 是否已登录钉钉账户")
            print(f"   2. 直播回放链接是否有效")
            print(f"   3. 视频是否能够正常播放")
            print(f"   4. 网络连接是否正常")
        
        print(f"\n🧹 清理资源...")
        browser.close_browser()
        print(f"✓ 浏览器已关闭")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        try:
            browser.close_browser()
        except:
            pass
    
    print(f"\n" + "=" * 60)
    print("🏁 测试完成")
    print("=" * 60)

if __name__ == '__main__':
    test_m3u8_extraction()
