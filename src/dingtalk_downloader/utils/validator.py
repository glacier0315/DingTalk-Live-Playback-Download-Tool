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

            # 处理空输入
            if choice == "":
                if default_option is not None:
                    print(f"已选择默认选项: {default_option}")
                    return default_option
                else:
                    print(error_message or "输入不能为空，请重新输入。")
                    continue

            # 验证输入
            if validation_func is not None and not validation_func(choice):
                print(error_message or "输入无效，请重新输入。")
                continue

            # 验证选项
            if choice in valid_options:
                return choice

            print("无效的选择，请重新输入。")

        except EOFError:
            if default_option is not None:
                print(f"\n输入流结束，使用默认选项: {default_option}")
                return default_option
            raise
        except KeyboardInterrupt:
            print("\n用户中断输入")
            raise


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
            if validation_func is not None:
                try:
                    if not validation_func(user_input):
                        print(error_message or f"{input_name}格式不正确，请重新输入。")
                        continue
                except ValueError as e:
                    print(error_message or str(e))
                    continue

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
    try:
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

        query_params = parse_qs(parsed.query)

        if "liveUuid" not in query_params:
            raise ValueError("链接缺少 liveUuid 参数")

        live_uuid = query_params.get("liveUuid", [None])[0]

        if not live_uuid:
            raise ValueError("liveUuid 参数为空")

        if not re.match(r"^[a-f0-9\-]{36}$", live_uuid):
            raise ValueError("liveUuid 格式无效")

        return url

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"无效的钉钉直播链接: {e}") from e


def validate_file_path(file_path: str) -> str:
    """
    验证文件路径。

    检查文件路径格式、文件是否存在、文件是否可读、文件大小是否合理。

    Args:
        file_path: 文件路径

    Returns:
        验证通过的文件路径

    Raises:
        FileNotFoundError: 文件不存在时
        PermissionError: 文件不可读时
        ValueError: 文件格式不支持或文件过大时
    """
    file_path = file_path.strip()

    # 检查空路径
    if not file_path:
        raise ValueError("文件路径不能为空")

    # 检查文件扩展名
    valid_extensions = [".csv", ".xlsx", ".xls"]
    if not file_path.lower().endswith(tuple(valid_extensions)):
        raise ValueError(
            f"文件格式不支持: {file_path}. 请使用CSV或Excel文件（.csv, .xlsx, .xls）。"
        )

    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    # 检查是否为文件
    if not os.path.isfile(file_path):
        raise ValueError(f"路径不是文件: {file_path}")

    # 检查文件可读性
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"文件不可读: {file_path}")

    # 检查文件大小
    file_size = os.path.getsize(file_path)
    max_size = 100 * 1024 * 1024  # 100MB

    if file_size > max_size:
        raise ValueError(
            f"文件过大: {file_path} ({file_size} bytes, 最大允许 {max_size} bytes)"
        )

    if file_size == 0:
        raise ValueError(f"文件为空: {file_path}")

    return file_path
