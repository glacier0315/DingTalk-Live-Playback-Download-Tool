#!/usr/bin/env python3
"""测试修复后的 M3U8 解析逻辑"""
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from dingtalk_download.m3u8_utils import _parse_chrome_edge_log

def test_log_parsing():
    """测试日志解析功能"""
    
    log_file = "Logs/browser_logs_edge_attempt1_20260106_235603.json"
    live_uuid = "6b145224-17b9-486b-904f-5e2b79e90bec"
    
    print(f"📂 读取日志文件: {log_file}")
    
    with open(log_file, 'r', encoding='utf-8') as f:
        log_data = json.load(f)
    
    logs = log_data['logs']
    print(f"📊 共 {len(logs)} 条日志")
    
    m3u8_count = 0
    m3u8_links = []
    
    for idx, log_entry in enumerate(logs):
        log_message = log_entry.get('message', '')
        
        if '.m3u8' in log_message.lower():
            print(f"\n🔍 发现包含 .m3u8 的日志条目 #{idx + 1}")
            print(f"   日志长度: {len(log_message)}")
            
            m3u8_url = _parse_chrome_edge_log(log_message, live_uuid)
            
            if m3u8_url:
                m3u8_count += 1
                m3u8_links.append(m3u8_url)
                print(f"   ✅ 成功提取 M3U8 链接: {m3u8_url}")
            else:
                print(f"   ❌ 未能提取 M3U8 链接")
    
    print(f"\n📈 统计结果:")
    print(f"   总日志条数: {len(logs)}")
    print(f"   包含 .m3u8 的日志: {sum(1 for log in logs if '.m3u8' in log.get('message', '').lower())}")
    print(f"   成功提取的 M3U8 链接: {m3u8_count}")
    
    if m3u8_links:
        print(f"\n🎉 找到的 M3U8 链接:")
        for link in m3u8_links:
            print(f"   - {link}")
    else:
        print(f"\n⚠️  未能找到任何 M3U8 链接")
        print(f"💡 这可能意味着:")
        print(f"   1. 视频尚未播放，M3U8 请求未触发")
        print(f"   2. M3U8 链接不包含 liveUuid: {live_uuid}")
        print(f"   3. 日志中确实没有 M3U8 请求")

if __name__ == '__main__':
    test_log_parsing()
