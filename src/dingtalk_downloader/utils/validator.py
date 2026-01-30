"""
钉钉直播回放下载工具 - 输入验证工具模块

本模块提供输入验证工具函数。

作者：项目团队
依赖：无
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2026-01-22: 新增URL验证函数
    - 2026-01-22: 完善用户输入校验机制
"""

import re
import os
from typing import List, Optional, Callable
from urllib.parse import urlparse, parse_qs
from .file_validator import FileValidator


def _handle_empty_input(
    default_option: Optional[str], error_message: Optional[str]
) -> Optional[str]:
    """
    处理空输入。

    Args:
        default_option: 默认选项
        error_message: 错误消息

    Returns:
        默认选项或None
    """
    if default_option is not None:
        print(f"已选择默认选项: {default_option}")
        return default_option
    print(error_message or "输入不能为空，请重新输入。")
    return None


def _validate_input(
    choice: str,
    validation_func: Optional[Callable[[str], bool]],
    error_message: Optional[str],
) -> bool:
    """
    验证输入。

    Args:
        choice: 用户输入
        validation_func: 验证函数
        error_message: 错误消息

    Returns:
        验证是否通过
    """
    if validation_func is not None and not validation_func(choice):
        print(error_message or "输入无效，请重新输入。")
        return False
    return True


def _handle_eof_error(
    default_option: Optional[str],
) -> Optional[str]:
    """
    处理EOF错误。

    Args:
        default_option: 默认选项

    Returns:
        默认选项或None

    Raises:
        EOFError: 没有默认选项时
    """
    if default_option is not None:
        print(f"\n输入流结束，使用默认选项: {default_option}")
        return default_option
    raise EOFError()


def _validate_choice(choice: str, valid_options: List[str]) -> bool:
    """
    验证选项是否有效。

    Args:
        choice: 用户输入
        valid_options: 有效选项列表

    Returns:
        选项是否有效
    """
    return choice in valid_options


def _process_user_choice(
    choice: str,
    valid_options: List[str],
    validation_func: Optional[Callable[[str], bool]],
    error_message: Optional[str],
) -> Optional[str]:
    """
    处理用户选择。

    Args:
        choice: 用户输入
        valid_options: 有效选项列表
        validation_func: 验证函数
        error_message: 错误消息

    Returns:
        有效选项或None
    """
    if not _validate_input(choice, validation_func, error_message):
        return None

    if _validate_choice(choice, valid_options):
        return choice

    print("无效的选择，请重新输入。")
    return None


def _handle_input_exception(
    exception: Exception,
    default_option: Optional[str],
) -> Optional[str]:
    """
    处理输入异常。

    Args:
        exception: 异常对象
        default_option: 默认选项

    Returns:
        默认选项或None

    Raises:
        Exception: 无法处理的异常
    """
    if isinstance(exception, EOFError):
        return _handle_eof_error(default_option)
    if isinstance(exception, KeyboardInterrupt):
        print("\n用户中断输入")
        raise
    return None


def _process_input(
    choice: str,
    valid_options: List[str],
    validation_func: Optional[Callable[[str], bool]],
    error_message: Optional[str],
    default_option: Optional[str],
) -> Optional[str]:
    """
    处理输入。

    Args:
        choice: 用户输入
        valid_options: 有效选项列表
        validation_func: 验证函数
        error_message: 错误消息
        default_option: 默认选项

    Returns:
        有效选项或None
    """
    if choice == "":
        return _handle_empty_input(default_option, error_message)

    return _process_user_choice(choice, valid_options, validation_func, error_message)


def validate_input(
    prompt: str,
    valid_options: List[str],
    default_option: Optional[str] = None,
    validation_func: Optional[Callable[[str], bool]] = None,
    error_message: Optional[str] = None,
) -> str:
    """
    验证用户输入。

    支持默认选项，如果用户直接按 Enter，则返回默认选项。
    增强异常处理，捕获 EOFError 和 KeyboardInterrupt。
    支持自定义验证函数和错误消息。

    Args:
        prompt: 提示信息
        valid_options: 有效选项列表
        default_option: 默认选项
        validation_func: 自定义验证函数，返回True表示验证通过
        error_message: 验证失败时的错误消息

    Returns:
        用户选择的选项

    Raises:
        ValueError: 输入无效时
        EOFError: 输入流结束时
        KeyboardInterrupt: 用户中断时
    """
    while True:
        try:
            choice = input(prompt)

            result = _process_input(
                choice, valid_options, validation_func, error_message, default_option
            )
            if result is not None:
                return result

        except (EOFError, KeyboardInterrupt) as e:
            result = _handle_input_exception(e, default_option)
            if result is not None:
                return result


def _validate_required_input(
    user_input: str,
    validation_func: Optional[Callable[[str], bool]],
    error_message: Optional[str],
    input_name: str,
) -> bool:
    """
    验证必填输入。

    Args:
        user_input: 用户输入
        validation_func: 验证函数
        error_message: 错误消息
        input_name: 输入项名称

    Returns:
        验证是否通过
    """
    if validation_func is None:
        return True

    try:
        if not validation_func(user_input):
            print(error_message or f"{input_name}格式不正确，请重新输入。")
            return False
        return True
    except ValueError as e:
        print(error_message or str(e))
        return False


def validate_required_input(
    prompt: str,
    validation_func: Optional[Callable[[str], bool]] = None,
    error_message: Optional[str] = None,
    input_name: str = "输入",
) -> str:
    """
    验证必填的用户输入。

    持续提示用户输入，直至获取到有效的非空输入值。
    提供清晰的错误提示信息，帮助用户提供正确的输入内容。

    Args:
        prompt: 提示信息
        validation_func: 自定义验证函数，返回True表示验证通过
        error_message: 验证失败时的错误消息
        input_name: 输入项的名称，用于错误提示

    Returns:
        用户输入的有效值

    Raises:
        ValueError: 输入无效时
        EOFError: 输入流结束时
        KeyboardInterrupt: 用户中断时
    """
    while True:
        try:
            user_input = input(prompt).strip()

            # 检查空输入
            if not user_input:
                print(f"{input_name}不能为空，请重新输入。")
                continue

            # 自定义验证
            if _validate_required_input(user_input, validation_func, error_message, input_name):
                return user_input

        except EOFError:
            print(f"\n输入流结束，{input_name}不能为空。")
            raise
        except KeyboardInterrupt:
            print("\n用户中断输入")
            raise


def validate_dingtalk_url(url: str) -> str:
    """
    验证钉钉直播链接。

    检查URL格式、协议、域名、必需的查询参数。

    Args:
        url: 钉钉直播回放分享链接

    Returns:
        验证通过的URL

    Raises:
        ValueError: URL无效时
    """
    parsed = urlparse(url)

    if not parsed.scheme:
        raise ValueError("URL缺少协议")

    if parsed.scheme not in ["http", "https"]:
        raise ValueError("仅支持 http 和 https 协议")

    if not parsed.netloc:
        raise ValueError("URL缺少域名")

    if parsed.netloc != "n.dingtalk.com":
        raise ValueError("仅支持钉钉直播链接 (n.dingtalk.com)")

    if not parsed.path:
        raise ValueError("URL缺少路径")

    _validate_live_uuid(parsed)

    return url


def _validate_live_uuid(parsed) -> None:
    """
    验证liveUuid参数。

    Args:
        parsed: 解析后的URL对象

    Raises:
        ValueError: liveUuid无效时
    """
    query_params = parse_qs(parsed.query)

    if "liveUuid" not in query_params:
        raise ValueError("链接缺少 liveUuid 参数")

    live_uuid = query_params.get("liveUuid", [None])[0]

    if not live_uuid:
        raise ValueError("liveUuid 参数为空")

    if not re.match(r"^[a-f0-9\-]{36}$", live_uuid):
        raise ValueError("liveUuid 格式无效")


def validate_file_path(file_path: str) -> str:
    """
    验证文件路径。

    使用统一的FileValidator进行文件路径验证。

    Args:
        file_path: 文件路径

    Returns:
        验证通过的文件路径

    Raises:
        FileNotFoundError: 文件不存在时
        PermissionError: 文件不可读时
        ValueError: 文件格式不支持或文件过大时
    """
    return FileValidator.validate_file_path(file_path)
