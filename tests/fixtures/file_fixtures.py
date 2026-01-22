"""文件测试Fixture模块

提供文件相关的测试fixture，包括示例文件、CSV文件、Excel文件等。
"""

import pytest
import csv
from pathlib import Path
from typing import List, Dict


@pytest.fixture
def sample_links():
    """示例直播链接列表"""
    return [
        "https://live.dingtalk.com/123456789",
        "https://live.dingtalk.com/987654321",
        "https://live.dingtalk.com/111222333",
    ]


@pytest.fixture
def sample_link_data():
    """示例链接数据（包含额外信息）"""
    return [
        {
            "url": "https://live.dingtalk.com/123456789",
            "name": "测试直播1",
            "cookie": "session_id=abc123",
        },
        {
            "url": "https://live.dingtalk.com/987654321",
            "name": "测试直播2",
            "cookie": "session_id=def456",
        },
        {
            "url": "https://live.dingtalk.com/111222333",
            "name": "测试直播3",
            "cookie": "session_id=ghi789",
        },
    ]


@pytest.fixture
def sample_csv_file(tmp_path):
    """示例CSV文件"""
    csv_file = tmp_path / "links.csv"
    csv_content = """url,name,cookie
https://live.dingtalk.com/123456789,测试直播1,session_id=abc123
https://live.dingtalk.com/987654321,测试直播2,session_id=def456
https://live.dingtalk.com/111222333,测试直播3,session_id=ghi789
"""
    csv_file.write_text(csv_content, encoding="utf-8")
    return csv_file


@pytest.fixture
def sample_csv_with_headers(tmp_path):
    """带表头的CSV文件"""
    csv_file = tmp_path / "links_with_headers.csv"
    csv_content = """直播链接,直播名称,Cookie
https://live.dingtalk.com/123456789,测试直播1,session_id=abc123
https://live.dingtalk.com/987654321,测试直播2,session_id=def456
"""
    csv_file.write_text(csv_content, encoding="utf-8")
    return csv_file


@pytest.fixture
def sample_csv_no_headers(tmp_path):
    """不带表头的CSV文件"""
    csv_file = tmp_path / "links_no_headers.csv"
    csv_content = """https://live.dingtalk.com/123456789,测试直播1,session_id=abc123
https://live.dingtalk.com/987654321,测试直播2,session_id=def456
https://live.dingtalk.com/111222333,测试直播3,session_id=ghi789
"""
    csv_file.write_text(csv_content, encoding="utf-8")
    return csv_file


@pytest.fixture
def sample_csv_empty(tmp_path):
    """空CSV文件"""
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("", encoding="utf-8")
    return csv_file


@pytest.fixture
def sample_csv_single_line(tmp_path):
    """单行CSV文件"""
    csv_file = tmp_path / "single.csv"
    csv_content = "https://live.dingtalk.com/123456789,测试直播1,session_id=abc123\n"
    csv_file.write_text(csv_content, encoding="utf-8")
    return csv_file


@pytest.fixture
def sample_csv_with_special_chars(tmp_path):
    """包含特殊字符的CSV文件"""
    csv_file = tmp_path / "special_chars.csv"
    csv_content = """url,name,cookie
https://live.dingtalk.com/123456789,"测试,直播1",session_id=abc123
https://live.dingtalk.com/987654321,"测试\"直播2\"",session_id=def456
"""
    csv_file.write_text(csv_content, encoding="utf-8")
    return csv_file


@pytest.fixture
def sample_csv_with_unicode(tmp_path):
    """包含Unicode字符的CSV文件"""
    csv_file = tmp_path / "unicode.csv"
    csv_content = """url,name,cookie
https://live.dingtalk.com/123456789,测试直播🎥,session_id=abc123
https://live.dingtalk.com/987654321,テストライブ,session_id=def456
"""
    csv_file.write_text(csv_content, encoding="utf-8")
    return csv_file


@pytest.fixture
def sample_excel_file(tmp_path):
    """示例Excel文件（模拟）"""
    excel_file = tmp_path / "links.xlsx"
    # 注意：实际创建Excel文件需要openpyxl或xlrd库
    # 这里创建一个模拟的Excel文件
    excel_file.write_text("MOCK_EXCEL_FILE", encoding="utf-8")
    return excel_file


@pytest.fixture
def sample_txt_file(tmp_path):
    """示例文本文件"""
    txt_file = tmp_path / "links.txt"
    txt_content = """https://live.dingtalk.com/123456789
https://live.dingtalk.com/987654321
https://live.dingtalk.com/111222333
"""
    txt_file.write_text(txt_content, encoding="utf-8")
    return txt_file


@pytest.fixture
def sample_txt_empty(tmp_path):
    """空文本文件"""
    txt_file = tmp_path / "empty.txt"
    txt_file.write_text("", encoding="utf-8")
    return txt_file


@pytest.fixture
def sample_txt_single_line(tmp_path):
    """单行文本文件"""
    txt_file = tmp_path / "single.txt"
    txt_content = "https://live.dingtalk.com/123456789\n"
    txt_file.write_text(txt_content, encoding="utf-8")
    return txt_file


@pytest.fixture
def sample_txt_with_spaces(tmp_path):
    """包含空格的文本文件"""
    txt_file = tmp_path / "spaces.txt"
    txt_content = """
https://live.dingtalk.com/123456789

https://live.dingtalk.com/987654321

"""
    txt_file.write_text(txt_content, encoding="utf-8")
    return txt_file


@pytest.fixture
def sample_output_dir(tmp_path):
    """示例输出目录"""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_output_file(tmp_path):
    """示例输出文件"""
    output_file = tmp_path / "output" / "test.mp4"
    output_file.parent.mkdir(exist_ok=True)
    output_file.write_text("MOCK_VIDEO_CONTENT", encoding="utf-8")
    return output_file


@pytest.fixture
def sample_config_file(tmp_path):
    """示例配置文件"""
    config_file = tmp_path / "config.json"
    config_content = """{
    "output_dir": "output",
    "browser": "edge",
    "timeout": 30,
    "retry": 3
}"""
    config_file.write_text(config_content, encoding="utf-8")
    return config_file


@pytest.fixture
def sample_log_file(tmp_path):
    """示例日志文件"""
    log_file = tmp_path / "test.log"
    log_content = """[INFO] Starting download...
[INFO] Downloading: https://live.dingtalk.com/123456789
[ERROR] Failed to download: Network error
[INFO] Retry 1/3...
"""
    log_file.write_text(log_content, encoding="utf-8")
    return log_file


@pytest.fixture
def sample_m3u8_file(tmp_path):
    """示例M3U8文件"""
    m3u8_file = tmp_path / "playlist.m3u8"
    m3u8_content = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXTINF:10.0,
segment1.ts
#EXTINF:10.0,
segment2.ts
#EXTINF:10.0,
segment3.ts
#EXT-X-ENDLIST
"""
    m3u8_file.write_text(m3u8_content, encoding="utf-8")
    return m3u8_file


@pytest.fixture
def sample_nested_m3u8_file(tmp_path):
    """嵌套M3U8文件"""
    m3u8_file = tmp_path / "master.m3u8"
    m3u8_content = """#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=1000000,RESOLUTION=1280x720
720p.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=2000000,RESOLUTION=1920x1080
1080p.m3u8
"""
    m3u8_file.write_text(m3u8_content, encoding="utf-8")
    return m3u8_file


@pytest.fixture
def sample_binary_file(tmp_path):
    """示例二进制文件"""
    binary_file = tmp_path / "test.bin"
    binary_content = b"\x00\x01\x02\x03\x04\x05"
    binary_file.write_bytes(binary_content)
    return binary_file


@pytest.fixture
def sample_large_file(tmp_path):
    """大文件（模拟）"""
    large_file = tmp_path / "large.txt"
    large_content = "x" * 10000
    large_file.write_text(large_content, encoding="utf-8")
    return large_file


@pytest.fixture
def sample_file_with_bom(tmp_path):
    """带BOM的UTF-8文件"""
    file_with_bom = tmp_path / "with_bom.txt"
    content = "\ufeffhttps://live.dingtalk.com/123456789\n"
    file_with_bom.write_text(content, encoding="utf-8-sig")
    return file_with_bom


@pytest.fixture
def sample_file_with_different_encoding(tmp_path):
    """不同编码的文件"""
    file_gbk = tmp_path / "gbk.txt"
    content = "https://live.dingtalk.com/123456789\n"
    file_gbk.write_text(content, encoding="gbk")
    return file_gbk
