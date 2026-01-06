"""分析浏览器日志格式的调试脚本。

该脚本用于分析浏览器日志的实际格式，帮助诊断 M3U8 链接提取问题。

Usage:
    python bin/analyze_browser_logs.py
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from dingtalk_download import browser

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('Logs/analyze_logs.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


def save_logs_to_file(logs: List[Dict], filename: str) -> None:
    """保存日志到 JSON 文件。"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
        print(f"✅ 日志已保存到: {filename}")
        logger.info(f"日志已保存到: {filename}")
    except Exception as e:
        print(f"❌ 保存日志时发生错误: {e}")
        logger.error(f"保存日志时发生错误: {e}")


def analyze_log_structure(log: Any, depth: int = 0) -> None:
    """分析日志条目的结构。"""
    indent = "  " * depth
    
    if isinstance(log, dict):
        print(f"{indent}📋 字典类型，包含 {len(log)} 个键:")
        for key, value in log.items():
            print(f"{indent}  - {key}: {type(value).__name__}")
            if depth < 2 and isinstance(value, (dict, list)):
                analyze_log_structure(value, depth + 1)
    elif isinstance(log, list):
        print(f"{indent}📋 列表类型，包含 {len(log)} 个元素:")
        if depth < 2 and len(log) > 0:
            print(f"{indent}  第一个元素:")
            analyze_log_structure(log[0], depth + 1)
    elif isinstance(log, str):
        print(f"{indent}📋 字符串类型，长度: {len(log)}")
        if len(log) > 200:
            print(f"{indent}  前 200 字符: {log[:200]}...")
            print(f"{indent}  后 200 字符: ...{log[-200:]}")
        else:
            print(f"{indent}  内容: {log}")
    else:
        print(f"{indent}📋 {type(log).__name__} 类型: {log}")


def search_m3u8_in_logs(logs: List[Any]) -> List[Dict]:
    """在日志中搜索包含 M3U8 的条目。"""
    m3u8_logs = []
    
    for idx, log in enumerate(logs):
        log_str = str(log)
        if '.m3u8' in log_str.lower():
            m3u8_logs.append({
                'index': idx,
                'log': log,
                'snippet': log_str[:500] if len(log_str) > 500 else log_str
            })
    
    return m3u8_logs


def analyze_browser_logs(browser_type: str, url: str) -> None:
    """分析浏览器日志。"""
    print("\n" + "=" * 80)
    print(f"分析 {browser_type} 浏览器日志")
    print("=" * 80)
    
    try:
        # 创建浏览器实例
        print(f"\n正在创建 {browser_type} 浏览器...")
        br = browser.create_browser(browser_type)
        
        # 导航到 URL
        print(f"正在导航到: {url}")
        br.get(url)
        
        # 等待用户登录
        input("\n请在浏览器中登录钉钉账户后，按 Enter 键继续...")
        
        # 获取日志
        print(f"\n正在获取 {browser_type} 浏览器日志...")
        
        if browser_type in ['chrome', 'edge']:
            logs = br.get_log("performance")
            print(f"✅ 获取到 {len(logs)} 条性能日志")
        elif browser_type == 'firefox':
            logs = br.execute_script("""
                var performance = window.performance || window.mozPerformance || 
                                  window.msPerformance || window.webkitPerformance || {};
                var network = performance.getEntries() || {};
                return network;
            """)
            print(f"✅ 获取到 {len(logs)} 条网络日志")
        
        # 保存原始日志
        timestamp = logging.Formatter('%Y%m%d_%H%M%S').format(logging.LogRecord(
            '', 0, '', 0, '', (), None
        ))
        log_filename = f"Logs/browser_logs_{browser_type}_{timestamp}.json"
        save_logs_to_file(logs, log_filename)
        
        # 分析日志结构
        print("\n" + "-" * 80)
        print("分析日志结构")
        print("-" * 80)
        
        if len(logs) > 0:
            print(f"\n第一个日志条目的结构:")
            analyze_log_structure(logs[0])
            
            if len(logs) > 1:
                print(f"\n第二个日志条目的结构:")
                analyze_log_structure(logs[1])
        else:
            print("\n⚠️  没有获取到日志")
        
        # 搜索 M3U8 相关日志
        print("\n" + "-" * 80)
        print("搜索 M3U8 相关日志")
        print("-" * 80)
        
        m3u8_logs = search_m3u8_in_logs(logs)
        print(f"\n找到 {len(m3u8_logs)} 条包含 M3U8 的日志")
        
        if m3u8_logs:
            for i, m3u8_log in enumerate(m3u8_logs[:5], 1):  # 只显示前 5 条
                print(f"\n📌 M3U8 日志 #{i} (索引: {m3u8_log['index']}):")
                print(f"   类型: {type(m3u8_log['log']).__name__}")
                print(f"   内容片段: {m3u8_log['snippet'][:300]}...")
                
                # 如果是字典，显示键
                if isinstance(m3u8_log['log'], dict):
                    print(f"   字典键: {list(m3u8_log['log'].keys())}")
        else:
            print("\n⚠️  未找到包含 M3U8 的日志")
            print("💡 可能的原因：")
            print("   1. 页面还没有加载视频")
            print("   2. 浏览器日志配置不正确")
            print("   3. 视频播放器使用了不同的加载方式")
        
        # 关闭浏览器
        input("\n按 Enter 键关闭浏览器...")
        br.quit()
        
    except Exception as e:
        print(f"\n❌ 分析过程中发生错误: {e}")
        logger.error("分析失败", exc_info=True)
        if 'br' in locals():
            br.quit()


def main():
    """主函数。"""
    print("\n" + "=" * 80)
    print("浏览器日志分析工具")
    print("=" * 80)
    
    url = input("\n请输入钉钉直播回放链接: ").strip()
    
    if not url:
        print("❌ URL 不能为空")
        return
    
    print("\n请选择浏览器类型：")
    print("1. Edge")
    print("2. Chrome")
    print("3. Firefox")
    
    choice = input("\n请输入选项（1-3）: ").strip()
    browser_type_map = {"1": "edge", "2": "chrome", "3": "firefox"}
    browser_type = browser_type_map.get(choice, "edge")
    
    analyze_browser_logs(browser_type, url)
    
    print("\n" + "=" * 80)
    print("分析完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
