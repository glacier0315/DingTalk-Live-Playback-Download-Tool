"""
钉钉直播回放下载工具 - 用户交互控制器模块

本模块提供用户交互控制器类，专门负责处理用户输入和交互逻辑。

作者：项目团队
依赖：无
创建日期：2026-01-28
修改历史：
    - 2026-01-28: 初始版本
"""

import logging
from typing import Callable, Optional
from ..utils.validator import (
    validate_required_input,
    validate_dingtalk_url,
    validate_file_path,
)

logger = logging.getLogger(__name__)


class UserInteractionController:
    """
    用户交互控制器类。

    专门负责处理用户输入和交互逻辑。

    Attributes:
        logger: 日志记录器
    """

    def __init__(self):
        """
        初始化用户交互控制器。
        """
        self.logger = logging.getLogger(__name__)

    def get_user_input(
        self,
        prompt: str,
        validation_func: Callable[[str], bool],
        error_message: str,
        input_name: str,
    ) -> str:
        """
        获取用户输入。

        Args:
            prompt: 提示信息
            validation_func: 验证函数，返回True表示验证通过
            error_message: 错误消息
            input_name: 输入项名称

        Returns:
            用户输入

        Raises:
            ValueError: 输入无效时
            EOFError: 输入流结束时
            KeyboardInterrupt: 用户中断时
        """
        return validate_required_input(
            prompt,
            validation_func=validation_func,
            error_message=error_message,
            input_name=input_name,
        )

    def ask_continue_download(self) -> bool:
        """
        询问用户是否继续下载。

        Returns:
            True表示继续，False表示退出

        Raises:
            EOFError: 输入流结束时
            KeyboardInterrupt: 用户中断时
        """
        continue_option = input(
            "是否继续输入钉钉直播回放链接表格路径进行下载？(按Enter继续，按q退出程序): "
        )
        return continue_option.lower() != "q"

    def ask_file_path(self) -> Optional[str]:
        """
        询问用户输入文件路径。

        Returns:
            文件路径，如果用户选择退出则返回None

        Raises:
            ValueError: 文件路径无效时
            FileNotFoundError: 文件不存在时
            EOFError: 输入流结束时
            KeyboardInterrupt: 用户中断时
        """
        file_path = input(
            "请输入新的钉钉直播回放链接表格路径（支持CSV或Excel格式，可直接将文件拖放进窗口）: "
        )
        return file_path if file_path.strip() else None
