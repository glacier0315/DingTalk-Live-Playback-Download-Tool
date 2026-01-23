"""
钉钉直播回放下载工具 - 路径处理工具模块

本模块提供路径处理工具函数。

作者：项目团队
依赖：os, pathlib
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
"""

import os


def clean_file_path(file_path: str) -> str:
    """
    清理文件路径。

    去除路径中的多余引号和空格。

    Args:
        file_path: 文件路径

    Returns:
        清理后的文件路径
    """
    return file_path.strip().replace('"', "").replace("'", "")


def join_paths(*paths: str) -> str:
    """
    拼接路径。

    使用 os.path.join 拼接多个路径片段。

    Args:
        *paths: 路径片段

    Returns:
        拼接后的路径
    """
    return os.path.join(*paths)


def ensure_dir_exists(dir_path: str) -> None:
    """
    确保目录存在。

    如果目录不存在，则创建目录。

    Args:
        dir_path: 目录路径
    """
    os.makedirs(dir_path, exist_ok=True)
