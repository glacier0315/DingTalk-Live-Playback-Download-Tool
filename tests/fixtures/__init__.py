"""测试Fixture模块

提供各种测试fixture，包括：
- browser_fixtures: 浏览器相关fixture
- cookie_fixtures: Cookie相关fixture
- file_fixtures: 文件相关fixture
- mock_fixtures: Mock工具fixture
"""

from .browser_fixtures import *
from .cookie_fixtures import *
from .file_fixtures import *
from .mock_fixtures import *

__all__ = [
    # Browser fixtures
    "mock_edge_driver",
    "mock_chrome_driver",
    "mock_firefox_driver",
    "mock_browser_factory",
    "mock_selenium_options",
    "mock_webdriver",
    "sample_cookies",
    "sample_live_url",
    "sample_live_page_content",
    # Cookie fixtures
    "sample_cookie_data",
    "sample_cookie_list",
    "sample_cookie_string",
    "sample_cookie_file",
    "sample_cookie_json_file",
    "mock_cookie_handler",
    "cookie_with_live_name",
    "cookie_with_special_chars",
    "cookie_with_unicode",
    "empty_cookie_data",
    "invalid_cookie_data",
    "cookie_with_expiry",
    # File fixtures
    "sample_links",
    "sample_link_data",
    "sample_csv_file",
    "sample_csv_with_headers",
    "sample_csv_no_headers",
    "sample_csv_empty",
    "sample_csv_single_line",
    "sample_csv_with_special_chars",
    "sample_csv_with_unicode",
    "sample_excel_file",
    "sample_txt_file",
    "sample_txt_empty",
    "sample_txt_single_line",
    "sample_txt_with_spaces",
    "sample_output_dir",
    "sample_output_file",
    "sample_config_file",
    "sample_log_file",
    "sample_m3u8_file",
    "sample_nested_m3u8_file",
    "sample_binary_file",
    "sample_large_file",
    "sample_file_with_bom",
    "sample_file_with_different_encoding",
    # Mock fixtures
    "mock_response",
    "mock_response_error",
    "mock_response_timeout",
    "mock_requests",
    "mock_subprocess",
    "mock_os",
    "mock_pathlib",
    "mock_logger",
    "mock_config",
    "mock_file_reader",
    "mock_downloader",
    "mock_m3u8_parser",
    "mock_ffmpeg_wrapper",
    "mock_n_m3u8dl_re",
    "mock_settings",
    "mock_validator",
    "mock_path_helper",
    "mock_exception",
    "mock_network_error",
    "mock_file_error",
    "mock_timeout_error",
    "mock_retry_decorator",
    "mock_progress_callback",
    "mock_event_emitter",
    "mock_async_executor",
    "mock_thread_pool",
    "mock_process_pool",
    "mock_queue",
    "mock_lock",
    "mock_semaphore",
    "mock_event",
    "mock_condition",
    "mock_timer",
    "mock_thread",
    "mock_process",
]
