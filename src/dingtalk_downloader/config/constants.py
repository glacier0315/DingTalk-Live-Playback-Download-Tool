"""
钉钉直播回放下载工具 - 常量定义模块

本模块定义项目中的所有常量。

作者：项目团队
依赖：os
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2026-01-22: 新增直播名称选择器配置
    - 2026-01-27: 支持从环境变量读取配置文件路径
"""

import os

# 配置文件路径
# 优先级：环境变量 > 默认值
CONFIG_FILE_PATH = os.getenv("DINGTALK_DOWNLOADER_CONFIG_PATH", "./config/app.yaml")

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

# 浏览器选项映射
BROWSER_OPTION_MAP = {"1": BROWSER_TYPE_EDGE, "2": BROWSER_TYPE_CHROME, "3": BROWSER_TYPE_FIREFOX}

# 直播名称选择器配置
LIVE_NAME_SELECTORS = [
    ("xpath", '//*[@id="live-room"]/div[1]/div[1]/h3'),
    ("css", "vwi5-oG8"),
    ("xpath", '//h3[contains(@class, "live-title")]'),
    ("css", ".live-title"),
]
