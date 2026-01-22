"""
钉钉直播回放下载工具 - 输入验证工具模块

本模块提供输入验证工具函数。

作者：项目团队
依赖：无
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2026-01-22: 新增URL验证函数
"""

import re
from typing import List, Optional
from urllib.parse import urlparse, parse_qs


def validate_input(
    prompt: str, valid_options: List[str], default_option: Optional[str] = None
) -> str:
    """
    验证用户输入。

    支持默认选项，如果用户直接按 Enter，则返回默认选项。
    增强异常处理，捕获 EOFError 和 KeyboardInterrupt。

    Args:
        prompt: 提示信息
        valid_options: 有效选项列表
        default_option: 默认选项

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
            if choice == "" and default_option is not None:
                return default_option
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

        if not re.match(r"^[a-f0-9-]{36}$", live_uuid):
            raise ValueError("liveUuid 格式无效")

        return url

    except ValueError:
        raise
    except Exception as e:
        raise ValueError(f"无效的钉钉直播链接: {e}") from e
