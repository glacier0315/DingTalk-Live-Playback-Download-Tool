"""
钉钉直播回放下载工具 - 输入验证工具模块

本模块提供输入验证工具函数。

作者：项目团队
依赖：无
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
"""

from typing import List, Optional


def validate_input(prompt: str, valid_options: List[str], default_option: Optional[str] = None) -> str:
    """
    验证用户输入。

    支持默认选项，如果用户直接按 Enter，则返回默认选项。

    Args:
        prompt: 提示信息
        valid_options: 有效选项列表
        default_option: 默认选项

    Returns:
        用户选择的选项

    Raises:
        ValueError: 输入无效时
    """
    while True:
        choice = input(prompt)
        if choice == '' and default_option is not None:
            return default_option
        if choice in valid_options:
            return choice
        print("无效的选择，请重新输入。")
