"""详细分析浏览器日志文件。"""

import json
import glob
from pathlib import Path
from collections import defaultdict


def analyze_log_file(log_file):
    """分析单个日志文件。"""
    print(f"\n{'=' * 80}")
    print(f"分析文件: {log_file}")
    print('=' * 80)
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logs = data.get('logs', [])
        live_uuid = data.get('live_uuid', 'unknown')
        
        print(f"\n📊 基本信息:")
        print(f"  - 浏览器类型: {data.get('browser_type', 'unknown')}")
        print(f"  - 尝试次数: {data.get('attempt', 0)}")
        print(f"  - liveUuid: {live_uuid}")
        print(f"  - 总日志数: {len(logs)}")
        
        # 分析网络请求
        network_requests = []
        video_requests = []
        m3u8_requests = []
        
        for log_entry in logs:
            message = log_entry.get('message', '')
            
            try:
                log_json = json.loads(message)
                msg_content = log_json.get('message', {})
                method = msg_content.get('method', '')
                params = msg_content.get('params', {})
                
                # 检查是否是网络请求
                if 'Network' in method and 'request' in params:
                    request = params.get('request', {})
                    url = request.get('url', '')
                    
                    if url:
                        network_requests.append({
                            'method': method,
                            'url': url,
                            'type': params.get('type', 'unknown')
                        })
                        
                        # 检查是否是视频相关
                        if any(kw in url.lower() for kw in ['video', 'stream', 'media', 'm3u8', 'mp4']):
                            video_requests.append(url)
                        
                        # 检查是否是 M3U8
                        if '.m3u8' in url.lower():
                            m3u8_requests.append(url)
                
            except json.JSONDecodeError:
                continue
        
        print(f"\n📡 网络请求统计:")
        print(f"  - 总网络请求数: {len(network_requests)}")
        print(f"  - 视频相关请求: {len(video_requests)}")
        print(f"  - M3U8 请求: {len(m3u8_requests)}")
        
        # 显示前 10 个网络请求
        if network_requests:
            print(f"\n📋 前 10 个网络请求:")
            for idx, req in enumerate(network_requests[:10], 1):
                print(f"  {idx}. [{req['method']}] {req['type']}")
                print(f"     {req['url'][:100]}...")
        
        # 显示视频相关请求
        if video_requests:
            print(f"\n🎬 视频相关请求 ({len(video_requests)} 个):")
            for idx, url in enumerate(video_requests, 1):
                print(f"  {idx}. {url}")
        
        # 显示 M3U8 请求
        if m3u8_requests:
            print(f"\n📺 M3U8 请求 ({len(m3u8_requests)} 个):")
            for idx, url in enumerate(m3u8_requests, 1):
                print(f"  {idx}. {url}")
        else:
            print(f"\n⚠️  未找到 M3U8 请求")
        
        # 分析日志方法分布
        method_counts = defaultdict(int)
        for log_entry in logs:
            message = log_entry.get('message', '')
            try:
                log_json = json.loads(message)
                msg_content = log_json.get('message', {})
                method = msg_content.get('method', '')
                if method:
                    method_counts[method] += 1
            except json.JSONDecodeError:
                continue
        
        print(f"\n📊 日志方法分布 (前 10 个):")
        for method, count in sorted(method_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {method}: {count}")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")


def main():
    """主函数。"""
    print("\n" + "=" * 80)
    print("浏览器日志详细分析工具")
    print("=" * 80)
    
    log_files = glob.glob("Logs/browser_logs_*.json")
    print(f"\n📂 找到 {len(log_files)} 个日志文件")
    
    if not log_files:
        print("⚠️  没有找到日志文件")
        return
    
    for log_file in sorted(log_files):
        analyze_log_file(log_file)
    
    print("\n" + "=" * 80)
    print("分析完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
