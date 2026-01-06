"""钉钉直播回放下载工具包"""
from .utils import validate_input, clean_file_path, get_executable_name
from .link_handler import read_links_file, extract_live_uuid
from .browser import get_browser_options, get_browser_cookie, repeat_get_browser_cookie
from .m3u8_utils import extract_prefix, fetch_m3u8_links, download_m3u8_file, refresh_page_by_click
from .download_manager import (
    auto_download_m3u8_with_options,
    download_m3u8_with_options,
    download_m3u8_with_reused_path
)
from .main import single_mode, batch_mode, main

__version__ = "1.3.0"
__all__ = [
    'validate_input',
    'clean_file_path', 
    'get_executable_name',
    'read_links_file',
    'extract_live_uuid',
    'get_browser_options',
    'get_browser_cookie',
    'repeat_get_browser_cookie',
    'extract_prefix',
    'fetch_m3u8_links',
    'download_m3u8_file',
    'refresh_page_by_click',
    'auto_download_m3u8_with_options',
    'download_m3u8_with_options',
    'download_m3u8_with_reused_path',
    'single_mode',
    'batch_mode',
    'main'
]
