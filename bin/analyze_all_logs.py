#!/usr/bin/env python3
"""分析所有日志文件中的 M3U8 请求"""
import json
import sys
import glob
from pathlib import Path
from collections import defaultdict

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

def analyze_all_logs():
    """分析所有日志文件"""
    
    log_files = glob.glob("Logs/browser_logs_*.json")
    print(f"📂 找到 {len(log_files)} 个日志文件\n")
    
    all_stats = defaultdict(lambda: {
        'total_logs': 0,
        'm3u8_found': 0,
        'm3u8_links': [],
        'video_requests': 0
    })
    
    for log_file in sorted(log_files):
        print(f"📂 分析: {log_file}")
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            logs = log_data['logs']
            browser_type = log_data.get('browser_type', 'unknown')
            attempt = log_data.get('attempt', 0)
            live_uuid = log_data.get('live_uuid', 'unknown')
            
            key = f"{browser_type}_attempt{attempt}"
            all_stats[key]['total_logs'] = len(logs)
            
            m3u8_count = 0
            video_count = 0
            m3u8_links = []
            
            for idx, log_entry in enumerate(logs):
                log_message = log_entry.get('message', '')
                
                try:
                    log_json = json.loads(log_message)
                    message = log_json.get('message', {})
                    method = message.get('method', '')
                    params = message.get('params', {})
                    
                    if 'request' in params:
                        url = params['request'].get('url', '')
                        
                        if '.m3u8' in url.lower():
                            m3u8_count += 1
                            m3u8_links.append(url)
                            print(f"   ✅ 发现 M3U8 请求: {url}")
                        
                        if any(kw in url.lower() for kw in ['video', 'stream', 'media']):
                            video_count += 1
                
                except Exception:
                    continue
            
            all_stats[key]['m3u8_found'] = m3u8_count
            all_stats[key]['m3u8_links'] = m3u8_links
            all_stats[key]['video_requests'] = video_count
            
            print(f"   📊 总日志: {len(logs)}")
            print(f"   🎬 视频相关请求: {video_count}")
            print(f"   📺 M3U8 请求: {m3u8_count}")
            print()
            
        except Exception as e:
            print(f"   ❌ 错误: {e}\n")
    
    print("=" * 60)
    print("📈 总体统计:")
    print("=" * 60)
    
    total_m3u8 = 0
    for key, stats in sorted(all_stats.items()):
        print(f"\n{key}:")
        print(f"  总日志数: {stats['total_logs']}")
        print(f"  视频请求: {stats['video_requests']}")
        print(f"  M3U8 请求: {stats['m3u8_found']}")
        if stats['m3u8_links']:
            print(f"  M3U8 链接:")
            for link in stats['m3u8_links']:
                print(f"    - {link}")
        total_m3u8 += stats['m3u8_found']
    
    print(f"\n" + "=" * 60)
    print(f"总计 M3U8 请求: {total_m3u8}")
    
    if total_m3u8 == 0:
        print(f"\n⚠️  所有日志中均未发现 M3U8 请求")
        print(f"💡 可能的原因:")
        print(f"   1. 视频播放触发机制未生效")
        print(f"   2. 等待时间不足，视频未开始加载")
        print(f"   3. 需要用户手动点击播放按钮")
        print(f"   4. 页面需要额外的交互才能触发视频加载")

if __name__ == '__main__':
    analyze_all_logs()
