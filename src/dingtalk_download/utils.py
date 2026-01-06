"""通用工具函数模块

该模块提供项目中使用的通用工具函数，包括输入验证、
文件路径处理和可执行文件名获取等功能。
"""

import logging
import platform
from typing import Optional, List

# 配置日志
logger = logging.getLogger(__name__)


def validate_input(
    prompt: str,
    valid_options: List[str],
    default_option: Optional[str] = None
) -> str:
    """验证用户输入并返回有效选项。

    该函数持续提示用户输入，直到用户提供有效的选项。
    如果用户输入为空且提供了默认选项，则返回默认选项。

    Args:
        prompt: 显示给用户的提示信息。
        valid_options: 有效选项列表。
        default_option: 当用户输入为空时返回的默认选项。默认为None。

    Returns:
        用户选择的选项字符串。

    Raises:
        ValueError: 如果参数无效（提示信息为空、选项列表为空、
                   默认选项不在有效选项列表中等）。
        TypeError: 如果参数类型不正确。

    Examples:
        >>> validate_input("请选择: ", ['1', '2', '3'], '1')
        '1'  # 用户直接按回车，返回默认值
        >>> validate_input("请选择: ", ['a', 'b', 'c'])
        'a'  # 用户输入 'a'
    """
    logger.debug(f"validate_input called with prompt='{prompt}', options={valid_options}")

    # 参数验证
    if not prompt:
        error_msg = "提示信息不能为空"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if not isinstance(prompt, str):
        error_msg = f"提示信息必须是字符串类型，实际类型: {type(prompt)}"
        logger.error(error_msg)
        raise TypeError(error_msg)

    if not isinstance(valid_options, list):
        error_msg = f"有效选项必须是列表类型，实际类型: {type(valid_options)}"
        logger.error(error_msg)
        raise TypeError(error_msg)

    if not valid_options:
        error_msg = "有效选项列表不能为空"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if default_option is not None and default_option not in valid_options:
        error_msg = f"默认选项 '{default_option}' 不在有效选项列表中"
        logger.error(error_msg)
        raise ValueError(error_msg)

    # 持续提示用户输入，直到获得有效选项
    while True:
        try:
            choice = input(prompt)
            logger.debug(f"User input: '{choice}'")

            # 处理空输入
            if choice == '' and default_option is not None:
                logger.info(f"使用默认选项: {default_option}")
                return default_option

            # 验证输入是否有效
            if choice in valid_options:
                logger.info(f"用户选择了有效选项: {choice}")
                return choice

            logger.warning(f"无效的选择: '{choice}'")
            print("无效的选择，请重新输入。")

        except EOFError:
            logger.error("用户输入被中断（EOF）")
            raise
        except KeyboardInterrupt:
            logger.warning("用户中断了输入")
            raise


def get_executable_name() -> str:
    """获取当前操作系统对应的可执行文件名。

    根据运行程序的操作系统返回相应的可执行文件名。
    支持的操作系统包括Windows、Linux和macOS。

    Returns:
        可执行文件名字符串。Windows返回'N_m3u8DL-RE.exe'，
        Linux和macOS返回'./N_m3u8DL-RE'。

    Raises:
        RuntimeError: 如果操作系统不被支持。

    Examples:
        >>> # 在Windows上
        >>> get_executable_name()
        'N_m3u8DL-RE.exe'
        >>> # 在Linux或macOS上
        >>> get_executable_name()
        './N_m3u8DL-RE'
    """
    logger.debug("Getting executable name for current OS")

    system = platform.system()
    logger.debug(f"Detected operating system: {system}")

    if system == 'Windows':
        executable_name = 'N_m3u8DL-RE.exe'
        logger.info(f"Windows detected, using executable: {executable_name}")
        return executable_name
    elif system == 'Linux' or system == 'Darwin':
        executable_name = './N_m3u8DL-RE'
        logger.info(f"Unix-like system detected ({system}), using executable: {executable_name}")
        return executable_name
    else:
        error_msg = f"不支持的操作系统: {system}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def clean_file_path(input_path: str) -> str:
    """清理文件路径，移除周围的空白和引号。

    该函数用于处理用户输入的文件路径，移除可能存在的
    前后空白字符以及单引号或双引号。

    Args:
        input_path: 需要清理的原始文件路径字符串。

    Returns:
        清理后的文件路径字符串。

    Raises:
        ValueError: 如果输入路径为空或清理后为空。
        TypeError: 如果输入路径不是字符串类型。

    Examples:
        >>> clean_file_path('  "C:\\path\\to\\file.txt"  ')
        'C:\\path\\to\\file.txt'
        >>> clean_file_path(\"'/home/user/file.txt'\")
        '/home/user/file.txt'
    """
    logger.debug(f"Cleaning file path: '{input_path}'")

    # 参数验证
    if not input_path:
        error_msg = "文件路径不能为空"
        logger.error(error_msg)
        raise ValueError(error_msg)

    if not isinstance(input_path, str):
        error_msg = f"文件路径必须是字符串类型，实际类型: {type(input_path)}"
        logger.error(error_msg)
        raise TypeError(error_msg)

    # 移除空白和引号
    cleaned = input_path.strip().replace('"', '').replace("'", "")

    # 验证清理结果
    if not cleaned:
        error_msg = "清理后的文件路径为空"
        logger.error(error_msg)
        raise ValueError(error_msg)

    logger.debug(f"Cleaned file path: '{cleaned}'")
    return cleaned
