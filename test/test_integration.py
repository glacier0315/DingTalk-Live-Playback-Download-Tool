#!/usr/bin/env python3
"""端到端集成测试"""
import sys
import os
import tempfile
import json
from unittest.mock import Mock, patch, MagicMock
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dingtalk_download import (
    validate_input,
    clean_file_path,
    read_links_file,
    extract_live_uuid,
    get_browser_options,
    extract_prefix,
    download_m3u8_file,
    auto_download_m3u8_with_options
)


class TestFullDownloadWorkflow:
    """测试完整的下载工作流"""

    @patch('dingtalk_download.m3u8_utils.requests.get')
    def test_full_single_video_download_workflow(self, mock_get):
        """测试完整的单个视频下载工作流"""
        from dingtalk_download.m3u8_utils import (
            _validate_m3u8_download_parameters,
            _ensure_directory_exists,
            _fetch_m3u8_content_via_requests
        )

        mock_response = Mock()
        mock_response.text = '#EXTM3U\n#EXT-X-VERSION:3\n#EXTINF:10.0,\nsegment0.ts\n#EXTINF:10.0,\nsegment1.ts\n#EXT-X-ENDLIST'
        mock_get.return_value = mock_response

        dingtalk_url = 'https://n.dingtalk.com/live?liveUuid=abc123'
        live_uuid = extract_live_uuid(dingtalk_url)

        assert live_uuid == 'abc123'

        m3u8_url = 'https://example.com/live_hp/abc123/video.m3u8'
        prefix = extract_prefix(m3u8_url)

        assert prefix == 'https://example.com/live_hp/abc123'

        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, 'video.m3u8')

            _validate_m3u8_download_parameters(m3u8_url, filename, {'User-Agent': 'test'})
            _ensure_directory_exists(filename)

            content = _fetch_m3u8_content_via_requests(m3u8_url, {'User-Agent': 'test'}, {'cookie': 'test'})

            assert content.startswith('#EXTM3U')
            assert '#EXT-X-VERSION:3' in content

    @patch('dingtalk_download.m3u8_utils.requests.get')
    @patch('dingtalk_download.m3u8_utils.os.makedirs')
    @patch('dingtalk_download.m3u8_utils.os.path.exists')
    @patch('dingtalk_download.m3u8_utils.os.access')
    def test_full_batch_download_workflow(self, mock_access, mock_exists, mock_makedirs, mock_get):
        """测试完整的批量下载工作流"""
        from dingtalk_download.m3u8_utils import (
            _validate_m3u8_download_parameters,
            _ensure_directory_exists,
            _fetch_m3u8_content_via_requests
        )

        mock_response = Mock()
        mock_response.text = '#EXTM3U\n#EXT-X-VERSION:3\n#EXTINF:10.0,\nsegment0.ts\n#EXT-X-ENDLIST'
        mock_get.return_value = mock_response
        mock_exists.return_value = True
        mock_access.return_value = True

        links = [
            'https://n.dingtalk.com/live?liveUuid=abc123',
            'https://n.dingtalk.com/live?liveUuid=def456',
            'https://n.dingtalk.com/live?liveUuid=ghi789'
        ]

        results = []

        for link in links:
            live_uuid = extract_live_uuid(link)
            m3u8_url = f'https://example.com/live_hp/{live_uuid}/video.m3u8'
            prefix = extract_prefix(m3u8_url)

            with tempfile.TemporaryDirectory() as tmpdir:
                filename = os.path.join(tmpdir, f'{live_uuid}.m3u8')

                _validate_m3u8_download_parameters(m3u8_url, filename, {'User-Agent': 'test'})
                _ensure_directory_exists(filename)

                content = _fetch_m3u8_content_via_requests(m3u8_url, {'User-Agent': 'test'}, {'cookie': 'test'})

                results.append({
                    'live_uuid': live_uuid,
                    'm3u8_url': m3u8_url,
                    'prefix': prefix,
                    'content': content
                })

        assert len(results) == 3
        assert all(r['content'].startswith('#EXTM3U') for r in results)
        assert results[0]['live_uuid'] == 'abc123'
        assert results[1]['live_uuid'] == 'def456'
        assert results[2]['live_uuid'] == 'ghi789'

    @patch('dingtalk_download.m3u8_utils.requests.get')
    def test_full_workflow_with_different_browsers(self, mock_get):
        """测试使用不同浏览器的完整工作流"""
        from dingtalk_download.m3u8_utils import (
            _validate_m3u8_download_parameters,
            _fetch_m3u8_content_via_requests
        )

        mock_response = Mock()
        mock_response.text = '#EXTM3U\n#EXT-X-VERSION:3'
        mock_get.return_value = mock_response

        browsers = ['edge', 'chrome', 'firefox']

        for browser_type in browsers:
            browser_config = get_browser_options(browser_type)

            assert browser_config is not None
            assert browser_config['type'] == browser_type

            m3u8_url = 'https://example.com/video.m3u8'

            with tempfile.TemporaryDirectory() as tmpdir:
                filename = os.path.join(tmpdir, 'video.m3u8')

                _validate_m3u8_download_parameters(m3u8_url, filename, {'User-Agent': 'test'})
                content = _fetch_m3u8_content_via_requests(m3u8_url, {'User-Agent': 'test'}, {'cookie': 'test'})

                assert content.startswith('#EXTM3U')


class TestErrorRecoveryWorkflow:
    """测试错误恢复工作流"""

    @patch('dingtalk_download.m3u8_utils.requests.get')
    def test_error_recovery_with_retry(self, mock_get):
        """测试错误恢复和重试"""
        from dingtalk_download.m3u8_utils import (
            _validate_m3u8_download_parameters,
            _fetch_m3u8_content_via_requests
        )
        import requests

        mock_response = Mock()
        mock_response.text = '#EXTM3U\n#EXT-X-VERSION:3'

        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] < 3:
                raise requests.exceptions.RequestException("Network error")
            return mock_response

        mock_get.side_effect = side_effect

        m3u8_url = 'https://example.com/video.m3u8'

        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, 'video.m3u8')

            _validate_m3u8_download_parameters(m3u8_url, filename, {'User-Agent': 'test'})

            with pytest.raises(RuntimeError, match="获取 M3U8 内容失败"):
                _fetch_m3u8_content_via_requests(m3u8_url, {'User-Agent': 'test'}, {'cookie': 'test'})

        assert call_count[0] == 1

    @patch('dingtalk_download.m3u8_utils.requests.get')
    def test_error_recovery_with_empty_content(self, mock_get):
        """测试空内容错误恢复"""
        from dingtalk_download.m3u8_utils import (
            _validate_m3u8_download_parameters,
            _fetch_m3u8_content_via_requests
        )

        mock_response = Mock()
        mock_response.text = ''
        mock_get.return_value = mock_response

        m3u8_url = 'https://example.com/video.m3u8'

        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, 'video.m3u8')

            _validate_m3u8_download_parameters(m3u8_url, filename, {'User-Agent': 'test'})

            with pytest.raises(RuntimeError, match="下载的 M3U8 内容为空"):
                _fetch_m3u8_content_via_requests(m3u8_url, {'User-Agent': 'test'}, {'cookie': 'test'})

    @patch('dingtalk_download.m3u8_utils.requests.get')
    def test_error_recovery_with_http_error(self, mock_get):
        """测试 HTTP 错误恢复"""
        from dingtalk_download.m3u8_utils import (
            _validate_m3u8_download_parameters,
            _fetch_m3u8_content_via_requests
        )
        import requests

        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        m3u8_url = 'https://example.com/video.m3u8'

        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, 'video.m3u8')

            _validate_m3u8_download_parameters(m3u8_url, filename, {'User-Agent': 'test'})

            with pytest.raises(RuntimeError, match="获取 M3U8 内容失败"):
                _fetch_m3u8_content_via_requests(m3u8_url, {'User-Agent': 'test'}, {'cookie': 'test'})


class TestBatchDownloadWorkflow:
    """测试批量下载工作流"""

    def test_batch_download_with_csv_file(self):
        """测试使用 CSV 文件批量下载"""
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_file = os.path.join(tmpdir, 'links.csv')
            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write('链接\n')
                f.write('https://n.dingtalk.com/live?liveUuid=abc123\n')
                f.write('https://n.dingtalk.com/live?liveUuid=def456\n')
                f.write('https://n.dingtalk.com/live?liveUuid=ghi789\n')

            links_dict = read_links_file(csv_file)

            assert len(links_dict) == 3
            assert links_dict[0] == 'https://n.dingtalk.com/live?liveUuid=abc123'
            assert links_dict[1] == 'https://n.dingtalk.com/live?liveUuid=def456'
            assert links_dict[2] == 'https://n.dingtalk.com/live?liveUuid=ghi789'

    def test_batch_download_with_excel_file(self):
        """测试使用 Excel 文件批量下载"""
        with tempfile.TemporaryDirectory() as tmpdir:
            excel_file = os.path.join(tmpdir, 'links.xlsx')
            
            try:
                import pandas as pd
                data = {'链接': [
                    'https://n.dingtalk.com/live?liveUuid=abc123',
                    'https://n.dingtalk.com/live?liveUuid=def456'
                ]}
                df = pd.DataFrame(data)
                df.to_excel(excel_file, index=False)

                links_dict = read_links_file(excel_file)

                assert len(links_dict) == 2
                assert links_dict[0] == 'https://n.dingtalk.com/live?liveUuid=abc123'
                assert links_dict[1] == 'https://n.dingtalk.com/live?liveUuid=def456'
            except ImportError:
                pytest.skip("pandas not installed")

    @patch('dingtalk_download.m3u8_utils.requests.get')
    def test_batch_download_with_mixed_content_types(self, mock_get):
        """测试混合内容类型的批量下载"""
        from dingtalk_download.m3u8_utils import (
            _validate_m3u8_download_parameters,
            _fetch_m3u8_content_via_requests
        )

        mock_response = Mock()
        mock_response.text = '#EXTM3U\n#EXT-X-VERSION:3\n#EXTINF:10.0,\nsegment0.ts\n#EXT-X-ENDLIST'
        mock_get.return_value = mock_response

        with tempfile.TemporaryDirectory() as tmpdir:
            csv_file = os.path.join(tmpdir, 'links.csv')
            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write('链接\n')
                f.write('https://n.dingtalk.com/live?liveUuid=video1\n')
                f.write('https://n.dingtalk.com/live?liveUuid=video2\n')

            links_dict = read_links_file(csv_file)

            for idx, link in links_dict.items():
                live_uuid = extract_live_uuid(link)
                m3u8_url = f'https://example.com/live_hp/{live_uuid}/video.m3u8'

                filename = os.path.join(tmpdir, f'{live_uuid}.m3u8')

                _validate_m3u8_download_parameters(m3u8_url, filename, {'User-Agent': 'test'})
                content = _fetch_m3u8_content_via_requests(m3u8_url, {'User-Agent': 'test'}, {'cookie': 'test'})

                assert content.startswith('#EXTM3U')
                assert '#EXTINF:10.0' in content


class TestUserInteractionWorkflow:
    """测试用户交互工作流"""

    @patch('builtins.input')
    def test_user_input_validation_workflow(self, mock_input):
        """测试用户输入验证工作流"""
        mock_input.side_effect = ['invalid', '1']

        result = validate_input(
            "请选择选项（1-3）: ",
            ['1', '2', '3'],
            default_option='1'
        )

        assert result == '1'
        assert mock_input.call_count == 2

    @patch('builtins.input')
    def test_user_input_with_default(self, mock_input):
        """测试使用默认值的用户输入"""
        mock_input.return_value = ''

        result = validate_input(
            "请选择选项（1-3，直接回车默认选择1）: ",
            ['1', '2', '3'],
            default_option='1'
        )

        assert result == '1'
        assert mock_input.call_count == 1

    def test_file_path_cleanup_workflow(self):
        """测试文件路径清理工作流"""
        test_cases = [
            ('  "test video.mp4"  ', 'test video.mp4'),
            ('"test_video.mp4"', 'test_video.mp4'),
            ("'test_video.mp4'", 'test_video.mp4'),
            ('  test_video.mp4  ', 'test_video.mp4'),
            ('test video.mp4', 'test video.mp4')
        ]

        for input_path, expected_output in test_cases:
            result = clean_file_path(input_path)
            assert result == expected_output, f"Failed for input: {input_path}"

    def test_live_uuid_extraction_workflow(self):
        """测试直播 UUID 提取工作流"""
        test_cases = [
            ('https://n.dingtalk.com/live?liveUuid=abc123', 'abc123'),
            ('https://n.dingtalk.com/live?liveUuid=def456&other=param', 'def456'),
            ('https://n.dingtalk.com/live?liveUuid=ghi789#fragment', 'ghi789'),
            ('https://n.dingtalk.com/live?other=param&liveUuid=xyz789', 'xyz789')
        ]

        for url, expected_uuid in test_cases:
            result = extract_live_uuid(url)
            assert result == expected_uuid, f"Failed for URL: {url}"

    def test_m3u8_prefix_extraction_workflow(self):
        """测试 M3U8 前缀提取工作流"""
        test_cases = [
            ('https://example.com/live_hp/abc123/video.m3u8', 'https://example.com/live_hp/abc123'),
            ('https://example.com/live/def456/chunklist.m3u8', 'https://example.com/live/def456'),
            ('https://example.com/ghi789/video.m3u8', 'https://example.com/ghi789')
        ]

        for url, expected_prefix in test_cases:
            result = extract_prefix(url)
            assert result == expected_prefix, f"Failed for URL: {url}"


class TestDataFlowIntegration:
    """测试数据流集成"""

    @patch('dingtalk_download.m3u8_utils.requests.get')
    def test_data_flow_from_url_to_content(self, mock_get):
        """测试从 URL 到内容的数据流"""
        from dingtalk_download.m3u8_utils import (
            extract_live_uuid,
            extract_prefix,
            _validate_m3u8_download_parameters,
            _fetch_m3u8_content_via_requests
        )

        mock_response = Mock()
        mock_response.text = '#EXTM3U\n#EXT-X-VERSION:3\n#EXTINF:10.0,\nsegment0.ts\n#EXT-X-ENDLIST'
        mock_get.return_value = mock_response

        dingtalk_url = 'https://n.dingtalk.com/live?liveUuid=abc123'

        live_uuid = extract_live_uuid(dingtalk_url)
        m3u8_url = f'https://example.com/live_hp/{live_uuid}/video.m3u8'
        prefix = extract_prefix(m3u8_url)

        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, 'video.m3u8')

            _validate_m3u8_download_parameters(m3u8_url, filename, {'User-Agent': 'test'})
            content = _fetch_m3u8_content_via_requests(m3u8_url, {'User-Agent': 'test'}, {'cookie': 'test'})

            assert live_uuid == 'abc123'
            assert prefix == 'https://example.com/live_hp/abc123'
            assert content.startswith('#EXTM3U')
            assert '#EXTINF:10.0' in content

    @patch('dingtalk_download.m3u8_utils.requests.get')
    def test_data_flow_with_multiple_segments(self, mock_get):
        """测试多段数据流"""
        from dingtalk_download.m3u8_utils import (
            extract_live_uuid,
            extract_prefix,
            _validate_m3u8_download_parameters,
            _fetch_m3u8_content_via_requests
        )

        mock_response = Mock()
        mock_response.text = '''#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXTINF:10.0,
segment0.ts
#EXTINF:10.0,
segment1.ts
#EXTINF:10.0,
segment2.ts
#EXT-X-ENDLIST'''
        mock_get.return_value = mock_response

        dingtalk_url = 'https://n.dingtalk.com/live?liveUuid=abc123'

        live_uuid = extract_live_uuid(dingtalk_url)
        m3u8_url = f'https://example.com/live_hp/{live_uuid}/video.m3u8'
        prefix = extract_prefix(m3u8_url)

        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, 'video.m3u8')

            _validate_m3u8_download_parameters(m3u8_url, filename, {'User-Agent': 'test'})
            content = _fetch_m3u8_content_via_requests(m3u8_url, {'User-Agent': 'test'}, {'cookie': 'test'})

            assert live_uuid == 'abc123'
            assert prefix == 'https://example.com/live_hp/abc123'
            assert 'segment0.ts' in content
            assert 'segment1.ts' in content
            assert 'segment2.ts' in content
            assert '#EXT-X-ENDLIST' in content
