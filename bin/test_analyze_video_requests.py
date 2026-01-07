#!/usr/bin/env python3
"""分析日志中的视频相关请求"""
import json
import sys
from pathlib import Path
from collections import defaultdict

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

def analyze_video_requests():
    """分析日志中的视频相关请求"""
    
    log_file = "Logs/browser_logs_edge_attempt1_20260106_235603.json"
    
    print(f"📂 读取日志文件: {log_file}")
    
    with open(log_file, 'r', encoding='utf-8') as f:
        log_data = json.load(f)
    
    logs = log_data['logs']
    print(f"📊 共 {len(logs)} 条日志")
    
    video_keywords = ['video', 'media', 'stream', 'play', 'm3u8', 'mp4', 'flv', 'ts', 'segment']
    url_types = defaultdict(int)
    methods = defaultdict(int)
    
    for idx, log_entry in enumerate(logs):
        log_message = log_entry.get('message', '')
        
        try:
            log_json = json.loads(log_message)
            message = log_json.get('message', {})
            method = message.get('method', '')
            params = message.get('params', {})
            
            if 'request' in params:
                url = params['request'].get('url', '')
                
                for keyword in video_keywords:
                    if keyword in url.lower():
                        url_types[keyword] += 1
                        print(f"\n🔍 发现 {keyword} 相关请求 #{idx + 1}")
                        print(f"   方法: {method}")
                        print(f"   URL: {url}")
                        break
            
            methods[method] += 1
            
        except Exception as e:
            continue
    
    print(f"\n📈 统计结果:")
    print(f"   总日志条数: {len(logs)}")
    print(f"\n   视频相关请求类型:")
    for keyword, count in sorted(url_types.items()):
        print(f"   - {keyword}: {count}")
    
    print(f"\n   网络方法统计:")
    for method, count in sorted(methods.items(), key=lambda x: -x[1])[:10]:
        print(f"   - {method}: {count}")
    
    if not url_types:
        print(f"\n⚠️  未发现任何视频相关请求")
        print(f"💡 这可能意味着:")
        print(f"   1. 视频尚未播放，相关请求未触发")
        print(f"   2. 视频播放触发机制需要改进")
        print(f"   3. 需要更长的等待时间让视频加载")

if __name__ == '__main__':
    analyze_video_requests()
