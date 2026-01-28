"""
钉钉直播回放下载工具 - 项目包

本模块是项目的根包，提供统一的导入接口。

作者：项目团队
依赖：无
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
"""

from .main import main
from .core.downloader import Downloader
from .core.user_interaction_controller import UserInteractionController
from .core.cookie_handler import CookieHandler
from .core.m3u8_parser import M3u8Parser
from .utils.file_reader import FileReader
from .utils.validator import validate_input
from .utils.path_helper import clean_file_path, join_paths
from .binary.n_m3u8dl_re import NM3u8DLRE
from .browser.browser_factory import BrowserFactory
from .browser.edge_driver import EdgeDriver
from .browser.chrome_driver import ChromeDriver
from .browser.firefox_driver import FirefoxDriver
from .config.yaml_config import YamlConfig

__all__ = [
    "main",
    "Downloader",
    "UserInteractionController",
    "CookieHandler",
    "M3u8Parser",
    "FileReader",
    "validate_input",
    "clean_file_path",
    "join_paths",
    "NM3u8DLRE",
    "BrowserFactory",
    "EdgeDriver",
    "ChromeDriver",
    "FirefoxDriver",
    "YamlConfig",
]
__version__ = "1.3.0"
