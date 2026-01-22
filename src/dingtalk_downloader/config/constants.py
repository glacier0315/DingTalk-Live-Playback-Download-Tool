"""
钉钉直播回放下载工具 - 常量定义模块

本模块定义项目中的所有常量。

作者：项目团队
依赖：无
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2026-01-22: 新增直播名称选择器配置
"""

# 配置文件路径
CONFIG_FILE_PATH = "./config/app.yaml"

# 浏览器类型
BROWSER_TYPE_EDGE = "edge"
BROWSER_TYPE_CHROME = "chrome"
BROWSER_TYPE_FIREFOX = "firefox"

# 下载模式
DOWNLOAD_MODE_SINGLE = "1"
DOWNLOAD_MODE_BATCH = "2"

# 保存模式
SAVE_MODE_DEFAULT = "1"
SAVE_MODE_MANUAL = "2"

# 最大重试次数
MAX_RETRY_COUNT = 5

# 默认请求头
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://n.dingtalk.com/",
    "Accept": "application/vnd.apple.mpegurl, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

# 默认下载目录
DEFAULT_DOWNLOAD_DIR = "Downloads"

# 临时文件名
TEMP_M3U8_FILE = "output.m3u8"

# 浏览器选项映射
BROWSER_OPTION_MAP = {"1": BROWSER_TYPE_EDGE, "2": BROWSER_TYPE_CHROME, "3": BROWSER_TYPE_FIREFOX}

# 下载模式映射
DOWNLOAD_MODE_MAP = {"1": DOWNLOAD_MODE_SINGLE, "2": DOWNLOAD_MODE_BATCH}

# 保存模式映射
SAVE_MODE_MAP = {"1": SAVE_MODE_DEFAULT, "2": SAVE_MODE_MANUAL}

# 直播名称选择器配置
LIVE_NAME_SELECTORS = [
    ("xpath", '//*[@id="live-room"]/div[1]/div[1]/h3'),
    ("css", "vwi5-oG8"),
    ("xpath", '//h3[contains(@class, "live-title")]'),
    ("css", ".live-title"),
]
