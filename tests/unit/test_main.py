"""
钉钉直播回放下载工具 - main 单元测试

本模块测试主程序入口。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
"""

import sys
import os
import pytest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from dingtalk_downloader.config.yaml_config import ConfigLoadError, ConfigValidationError
from dingtalk_downloader.config.constants import (
    BROWSER_TYPE_EDGE,
    BROWSER_TYPE_CHROME,
    BROWSER_TYPE_FIREFOX,
    SAVE_MODE_DEFAULT,
    SAVE_MODE_MANUAL,
)
from dingtalk_downloader.main import main, single_mode, batch_mode


def test_single_mode_with_default_options():
    """测试单个视频下载模式 - 使用默认选项"""
    mock_user_controller = Mock()
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.Downloader"
    ) as mock_downloader_class:

        mock_user_controller.get_user_input.return_value = (
            "https://n.dingtalk.com/test?liveUuid=12345678-1234-1234-1234-1234567890ab"
        )
        mock_input.side_effect = ["", ""]

        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        single_mode(mock_user_controller)

        mock_downloader.download_single_video.assert_called_once_with(
            "https://n.dingtalk.com/test?liveUuid=12345678-1234-1234-1234-1234567890ab"
        )
        assert mock_downloader_class.call_count == 1


def test_single_mode_with_manual_options():
    """测试单个视频下载模式 - 手动选择选项"""
    mock_user_controller = Mock()
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.Downloader"
    ) as mock_downloader_class:

        mock_user_controller.get_user_input.return_value = (
            "https://n.dingtalk.com/test?liveUuid=12345678-1234-1234-1234-1234567890ab"
        )
        mock_input.side_effect = ["2", "3"]

        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        single_mode(mock_user_controller)

        mock_downloader.download_single_video.assert_called_once_with(
            "https://n.dingtalk.com/test?liveUuid=12345678-1234-1234-1234-1234567890ab"
        )
        assert mock_downloader_class.call_count == 1


def test_single_mode_keyboard_interrupt():
    """测试单个视频下载模式 - 用户中断"""
    mock_user_controller = Mock()
    with patch("builtins.input") as mock_input:
        mock_input.side_effect = KeyboardInterrupt()

        with pytest.raises(SystemExit) as exc_info:
            single_mode(mock_user_controller)

        assert exc_info.value.code == 0


def test_single_mode_exception():
    """测试单个视频下载模式 - 异常处理"""
    mock_user_controller = Mock()
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.Downloader"
    ) as mock_downloader_class:

        mock_input.side_effect = [
            "https://n.dingtalk.com/test?liveUuid=12345678-1234-1234-1234-1234567890ab",
            "",
            "",
        ]
        mock_downloader_class.side_effect = Exception("下载失败")

        with pytest.raises(SystemExit) as exc_info:
            single_mode(mock_user_controller)

        assert exc_info.value.code == 1


def test_batch_mode_with_default_options():
    """测试批量下载模式 - 使用默认选项"""
    import tempfile
    import os

    # 创建临时CSV文件
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as temp_file:
        temp_file.write("link\n")
        temp_file_path = temp_file.name

    try:
        mock_user_controller = Mock()
        with patch("builtins.input") as mock_input, patch(
            "dingtalk_downloader.main.FileReader"
        ) as mock_file_reader_class, patch(
            "dingtalk_downloader.main.Downloader"
        ) as mock_downloader_class:

            mock_user_controller.get_user_input.return_value = temp_file_path
            mock_input.side_effect = ["", ""]

            mock_file_reader = Mock()
            mock_file_reader.read_links.return_value = {
                0: "https://n.dingtalk.com/test1?liveUuid=12345678-1234-1234-1234-1234567890ab",
                1: "https://n.dingtalk.com/test2?liveUuid=12345678-1234-1234-1234-1234567890ab",
            }
            mock_file_reader_class.return_value = mock_file_reader

            mock_downloader = Mock()
            mock_downloader_class.return_value = mock_downloader

            batch_mode(mock_user_controller)

            mock_downloader.download_batch_videos.assert_called_once()
            assert mock_downloader_class.call_count == 1
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


def test_batch_mode_with_manual_options():
    """测试批量下载模式 - 手动选择选项"""
    import tempfile
    import os

    # 创建临时Excel文件
    with tempfile.NamedTemporaryFile(mode="w", suffix=".xlsx", delete=False) as temp_file:
        temp_file.write("link\n")
        temp_file_path = temp_file.name

    try:
        mock_user_controller = Mock()
        with patch("builtins.input") as mock_input, patch(
            "dingtalk_downloader.main.FileReader"
        ) as mock_file_reader_class, patch(
            "dingtalk_downloader.main.Downloader"
        ) as mock_downloader_class:

            mock_user_controller.get_user_input.return_value = temp_file_path
            mock_input.side_effect = ["2", "2"]

            mock_file_reader = Mock()
            mock_file_reader.read_links.return_value = {
                0: "https://n.dingtalk.com/test1?liveUuid=12345678-1234-1234-1234-1234567890ab"
            }
            mock_file_reader_class.return_value = mock_file_reader

            mock_downloader = Mock()
            mock_downloader_class.return_value = mock_downloader

            batch_mode(mock_user_controller)

            mock_downloader.download_batch_videos.assert_called_once()
            assert mock_downloader_class.call_count == 1
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


def test_batch_mode_keyboard_interrupt():
    """测试批量下载模式 - 用户中断"""
    mock_user_controller = Mock()
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.FileReader"
    ) as mock_file_reader_class:
        mock_input.side_effect = KeyboardInterrupt()

        with pytest.raises(SystemExit) as exc_info:
            batch_mode(mock_user_controller)

        assert exc_info.value.code == 0


def test_batch_mode_exception():
    """测试批量下载模式 - 异常处理"""
    import tempfile
    import os

    # 创建临时CSV文件
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as temp_file:
        temp_file.write("link\n")
        temp_file_path = temp_file.name

    try:
        mock_user_controller = Mock()
        with patch("builtins.input") as mock_input, patch(
            "dingtalk_downloader.main.FileReader"
        ) as mock_file_reader_class:

            mock_user_controller.get_user_input.return_value = temp_file_path
            mock_input.side_effect = ["", ""]
            mock_file_reader_class.side_effect = Exception("文件读取失败")

            with pytest.raises(SystemExit) as exc_info:
                batch_mode(mock_user_controller)

            assert exc_info.value.code == 1
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)


def test_main_single_mode():
    """测试主程序入口 - 单个视频下载模式"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.YamlConfig"
    ) as mock_yaml_config_class, patch("dingtalk_downloader.main.single_mode") as mock_single_mode:

        mock_input.side_effect = ["1"]

        mock_config = Mock()
        mock_config.get_str.side_effect = ["test", "1.0.0", "2026-01-01"]
        mock_yaml_config_class.get_instance.return_value = mock_config

        main()

        mock_single_mode.assert_called_once()


def test_main_batch_mode():
    """测试主程序入口 - 批量下载模式"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.YamlConfig"
    ) as mock_yaml_config_class, patch("dingtalk_downloader.main.batch_mode") as mock_batch_mode:

        mock_input.side_effect = ["2"]

        mock_config = Mock()
        mock_config.get_str.side_effect = ["test", "1.0.0", "2026-01-01"]
        mock_yaml_config_class.get_instance.return_value = mock_config

        main()

        mock_batch_mode.assert_called_once()


def test_main_keyboard_interrupt():
    """测试主程序入口 - 用户中断"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.YamlConfig"
    ) as mock_yaml_config_class:

        mock_input.side_effect = KeyboardInterrupt()

        mock_config = Mock()
        mock_config.get_str.side_effect = ["test", "1.0.0", "2026-01-01"]
        mock_yaml_config_class.get_instance.return_value = mock_config

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0


def test_main_exception():
    """测试主程序入口 - 异常处理"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.YamlConfig"
    ) as mock_yaml_config_class:

        mock_input.side_effect = Exception("输入错误")

        mock_config = Mock()
        mock_config.get_str.side_effect = ["test", "1.0.0", "2026-01-01"]
        mock_yaml_config_class.get_instance.return_value = mock_config

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1


def test_main_default_mode():
    """测试主程序入口 - 默认模式"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.YamlConfig"
    ) as mock_yaml_config_class, patch("dingtalk_downloader.main.single_mode") as mock_single_mode:

        mock_input.side_effect = [""]

        mock_config = Mock()
        mock_config.get_str.side_effect = ["test", "1.0.0", "2026-01-01"]
        mock_yaml_config_class.get_instance.return_value = mock_config

        main()

        mock_single_mode.assert_called_once()


def test_single_mode_edge_browser():
    """测试单个视频下载模式 - Edge浏览器"""
    mock_user_controller = Mock()
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.Downloader"
    ) as mock_downloader_class:

        mock_user_controller.get_user_input.return_value = (
            "https://n.dingtalk.com/test?liveUuid=12345678-1234-1234-1234-1234567890ab"
        )
        mock_input.side_effect = ["", "1"]

        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        single_mode(mock_user_controller)

        call_args = mock_downloader_class.call_args
        assert call_args[0][0] == BROWSER_TYPE_EDGE


def test_single_mode_chrome_browser():
    """测试单个视频下载模式 - Chrome浏览器"""
    mock_user_controller = Mock()
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.Downloader"
    ) as mock_downloader_class:

        mock_user_controller.get_user_input.return_value = (
            "https://n.dingtalk.com/test?liveUuid=12345678-1234-1234-1234-1234567890ab"
        )
        mock_input.side_effect = ["", "2"]

        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        single_mode(mock_user_controller)

        call_args = mock_downloader_class.call_args
        assert call_args[0][0] == BROWSER_TYPE_CHROME


def test_single_mode_firefox_browser():
    """测试单个视频下载模式 - Firefox浏览器"""
    mock_user_controller = Mock()
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.Downloader"
    ) as mock_downloader_class:

        mock_user_controller.get_user_input.return_value = (
            "https://n.dingtalk.com/test?liveUuid=12345678-1234-1234-1234-1234567890ab"
        )
        mock_input.side_effect = ["", "3"]

        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        single_mode(mock_user_controller)

        call_args = mock_downloader_class.call_args
        assert call_args[0][0] == BROWSER_TYPE_FIREFOX


def test_single_mode_default_save_mode():
    """测试单个视频下载模式 - 默认保存模式"""
    mock_user_controller = Mock()
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.Downloader"
    ) as mock_downloader_class:

        mock_user_controller.get_user_input.return_value = (
            "https://n.dingtalk.com/test?liveUuid=12345678-1234-1234-1234-1234567890ab"
        )
        mock_input.side_effect = ["", ""]

        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        single_mode(mock_user_controller)

        call_args = mock_downloader_class.call_args
        assert call_args[0][1] == SAVE_MODE_DEFAULT


def test_single_mode_manual_save_mode():
    """测试单个视频下载模式 - 手动保存模式"""
    mock_user_controller = Mock()
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.Downloader"
    ) as mock_downloader_class:

        mock_user_controller.get_user_input.return_value = (
            "https://n.dingtalk.com/test?liveUuid=12345678-1234-1234-1234-1234567890ab"
        )
        mock_input.side_effect = ["2", ""]

        mock_downloader = Mock()
        mock_downloader_class.return_value = mock_downloader

        single_mode(mock_user_controller)

        call_args = mock_downloader_class.call_args
        assert call_args[0][1] == SAVE_MODE_MANUAL


def test_main_config_loading():
    """测试主程序入口 - 配置加载"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.YamlConfig"
    ) as mock_yaml_config_class, patch("builtins.print") as mock_print, patch(
        "dingtalk_downloader.main.single_mode"
    ):

        mock_input.side_effect = [""]

        mock_config = Mock()
        mock_config.get_str.side_effect = [
            "钉钉直播回放下载工具",
            "1.5.0",
            "2026年01月26日",
        ]
        mock_yaml_config_class.get_instance.return_value = mock_config

        main()

        mock_yaml_config_class.get_instance.assert_called_once()
        mock_config.load.assert_called_once()

        mock_config.get_str.assert_any_call("app.name")
        mock_config.get_str.assert_any_call("app.version")
        mock_config.get_str.assert_any_call("app.build_date")

        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("钉钉直播回放下载工具" in call for call in print_calls)
        assert any("1.5.0" in call for call in print_calls)
        assert any("2026年01月26日" in call for call in print_calls)


def test_main_config_load_error():
    """测试主程序入口 - 配置加载失败"""
    with patch("dingtalk_downloader.main.YamlConfig") as mock_yaml_config_class:

        mock_yaml_config_class.get_instance.side_effect = ConfigLoadError(
            "配置文件不存在: config/app.yaml"
        )

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1


def test_main_config_validation_error():
    """测试主程序入口 - 配置验证失败"""
    with patch("dingtalk_downloader.main.YamlConfig") as mock_yaml_config_class:

        mock_config = Mock()
        mock_config.load.side_effect = ConfigValidationError("缺少必填配置项: app.build_date")
        mock_yaml_config_class.get_instance.return_value = mock_config

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1
