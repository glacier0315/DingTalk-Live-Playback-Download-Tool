"""测试修复后的 M3U8 提取功能。"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from dingtalk_download import browser, m3u8_utils


def main():
    """主函数。"""
    print("\n" + "=" * 80)
    print("测试修复后的 M3U8 提取功能")
    print("=" * 80)
    
    # 测试 URL
    test_url = "https://n.dingtalk.com/live?liveUuid=6b145224-17b9-486b-904f-5e2b79e90bec"
    
    print(f"\n📋 测试 URL: {test_url}")
    
    # 提取 liveUuid
    live_uuid = m3u8_utils.extract_live_uuid(test_url)
    print(f"✓ liveUuid: {live_uuid}")
    
    # 创建浏览器
    print(f"\n🌐 创建 Edge 浏览器实例...")
    try:
        br = browser.create_browser('edge')
        print(f"✓ 浏览器创建成功")
        
        # 导航到测试页面
        print(f"\n📺 导航到测试页面...")
        br.get(test_url)
        print(f"✓ 页面加载完成")
        
        # 等待用户登录
        print(f"\n⏳ 请在浏览器中登录钉钉账户，然后按 Enter 继续...")
        input()
        
        # 测试 M3U8 链接提取
        print(f"\n🎯 开始测试 M3U8 链接提取...")
        m3u8_links = m3u8_utils.fetch_m3u8_links(br, 'edge', test_url)
        
        if m3u8_links:
            print(f"\n✅ 测试成功！找到 {len(m3u8_links)} 个 M3U8 链接:")
            for idx, link in enumerate(m3u8_links, 1):
                print(f"   {idx}. {link}")
        else:
            print(f"\n❌ 测试失败：未能找到 M3U8 链接")
            print(f"\n💡 可能的原因：")
            print(f"   1. 视频播放器未触发播放")
            print(f"   2. 需要手动点击播放按钮")
            print(f"   3. 视频元素未正确加载")
            print(f"   4. 等待时间不足")
        
        # 关闭浏览器
        input(f"\n按 Enter 键关闭浏览器...")
        br.quit()
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
