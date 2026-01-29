"""
用户交互控制器单元测试
"""

import pytest
from unittest.mock import patch, MagicMock
from dingtalk_downloader.core.user_interaction_controller import UserInteractionController


class TestUserInteractionController:
    """用户交互控制器测试类"""

    def test_init(self):
        """测试初始化"""
        controller = UserInteractionController()
        assert controller is not None
        assert controller.logger is not None

    @patch("builtins.input", return_value="https://n.dingtalk.com/dingding/live/?liveUuid=xxx")
    def test_get_user_input_valid(self, mock_input):
        """测试获取有效用户输入"""
        controller = UserInteractionController()
        result = controller.get_user_input(
            "请输入钉钉直播回放分享链接: ",
            validation_func=lambda x: x.startswith("https://"),
            error_message="链接格式不正确",
            input_name="钉钉直播链接",
        )
        assert result == "https://n.dingtalk.com/dingding/live/?liveUuid=xxx"
        mock_input.assert_called_once()

    @patch("builtins.input", side_effect=["invalid", "https://n.dingtalk.com/dingding/live/?liveUuid=xxx"])
    def test_get_user_input_invalid_then_valid(self, mock_input):
        """测试获取无效后有效的用户输入"""
        controller = UserInteractionController()
        result = controller.get_user_input(
            "请输入钉钉直播回放分享链接: ",
            validation_func=lambda x: x.startswith("https://"),
            error_message="链接格式不正确",
            input_name="钉钉直播链接",
        )
        assert result == "https://n.dingtalk.com/dingding/live/?liveUuid=xxx"
        assert mock_input.call_count == 2

    @patch("builtins.input", side_effect=["", "", "https://n.dingtalk.com/dingding/live/?liveUuid=xxx"])
    def test_get_user_input_empty(self, mock_input):
        """测试获取空用户输入"""
        from dingtalk_downloader.utils.validator import validate_required_input

        controller = UserInteractionController()
        with patch(
            "dingtalk_downloader.core.user_interaction_controller.validate_required_input",
            side_effect=validate_required_input,
        ):
            result = controller.get_user_input(
                "请输入钉钉直播回放分享链接: ",
                validation_func=lambda x: x.startswith("https://"),
                error_message="链接格式不正确",
                input_name="钉钉直播链接",
            )
            assert result == "https://n.dingtalk.com/dingding/live/?liveUuid=xxx"
            assert mock_input.call_count == 3

    @patch("builtins.input", return_value="")
    def test_ask_continue_download_continue(self, mock_input):
        """测试询问继续下载-继续"""
        controller = UserInteractionController()
        result = controller.ask_continue_download()
        assert result is True
        mock_input.assert_called_once()

    @patch("builtins.input", return_value="q")
    def test_ask_continue_download_quit(self, mock_input):
        """测试询问继续下载-退出"""
        controller = UserInteractionController()
        result = controller.ask_continue_download()
        assert result is False
        mock_input.assert_called_once()

    @patch("builtins.input", return_value="Q")
    def test_ask_continue_download_quit_uppercase(self, mock_input):
        """测试询问继续下载-退出（大写）"""
        controller = UserInteractionController()
        result = controller.ask_continue_download()
        assert result is False
        mock_input.assert_called_once()

    @patch("builtins.input", return_value="/path/to/file.csv")
    def test_ask_file_path_valid(self, mock_input):
        """测试询问文件路径-有效"""
        controller = UserInteractionController()
        result = controller.ask_file_path()
        assert result == "/path/to/file.csv"
        mock_input.assert_called_once()

    @patch("builtins.input", return_value="")
    def test_ask_file_path_empty(self, mock_input):
        """测试询问文件路径-空"""
        controller = UserInteractionController()
        result = controller.ask_file_path()
        assert result is None
        mock_input.assert_called_once()

    @patch("builtins.input", return_value="   ")
    def test_ask_file_path_whitespace(self, mock_input):
        """测试询问文件路径-空白"""
        controller = UserInteractionController()
        result = controller.ask_file_path()
        assert result is None
        mock_input.assert_called_once()

    @patch("builtins.input", side_effect=EOFError())
    def test_get_user_input_eof_error(self, mock_input):
        """测试获取用户输入-EOF错误"""
        controller = UserInteractionController()
        with pytest.raises(EOFError):
            controller.get_user_input(
                "请输入钉钉直播回放分享链接: ",
                validation_func=lambda x: x.startswith("https://"),
                error_message="链接格式不正确",
                input_name="钉钉直播链接",
            )

    @patch("builtins.input", side_effect=KeyboardInterrupt())
    def test_get_user_input_keyboard_interrupt(self, mock_input):
        """测试获取用户输入-键盘中断"""
        controller = UserInteractionController()
        with pytest.raises(KeyboardInterrupt):
            controller.get_user_input(
                "请输入钉钉直播回放分享链接: ",
                validation_func=lambda x: x.startswith("https://"),
                error_message="链接格式不正确",
                input_name="钉钉直播链接",
            )

    @patch("builtins.input", side_effect=EOFError())
    def test_ask_continue_download_eof_error(self, mock_input):
        """测试询问继续下载-EOF错误"""
        controller = UserInteractionController()
        with pytest.raises(EOFError):
            controller.ask_continue_download()

    @patch("builtins.input", side_effect=KeyboardInterrupt())
    def test_ask_continue_download_keyboard_interrupt(self, mock_input):
        """测试询问继续下载-键盘中断"""
        controller = UserInteractionController()
        with pytest.raises(KeyboardInterrupt):
            controller.ask_continue_download()

    @patch("builtins.input", side_effect=EOFError())
    def test_ask_file_path_eof_error(self, mock_input):
        """测试询问文件路径-EOF错误"""
        controller = UserInteractionController()
        with pytest.raises(EOFError):
            controller.ask_file_path()

    @patch("builtins.input", side_effect=KeyboardInterrupt())
    def test_ask_file_path_keyboard_interrupt(self, mock_input):
        """测试询问文件路径-键盘中断"""
        controller = UserInteractionController()
        with pytest.raises(KeyboardInterrupt):
            controller.ask_file_path()
