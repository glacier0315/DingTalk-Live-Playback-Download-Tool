"""
钉钉直播回放下载工具 - 文件验证工具模块

本模块提供统一的文件验证工具类，消除重复的验证逻辑。

作者：项目团队
依赖：os, pathlib
创建日期：2026-01-30
修改历史：
    - 2026-01-30: 初始版本，统一文件验证逻辑
"""

import os
import logging
from pathlib import Path
from ..config.constants import MAX_FILE_SIZE

logger = logging.getLogger(__name__)


class FileValidator:
    """
    文件验证工具类。

    提供统一的文件验证方法，包括路径验证、扩展名验证、
    文件存在性验证、文件大小验证等。
    """

    VALID_EXTENSIONS = [".csv", ".xlsx", ".xls"]

    @staticmethod
    def validate_file_path(file_path: str) -> str:
        """
        验证文件路径。

        执行完整的文件路径验证，包括路径遍历检查、扩展名检查、
        文件存在性检查、文件大小检查等。

        Args:
            file_path: 文件路径

        Returns:
            验证通过的文件路径

        Raises:
            ValueError: 文件路径无效时
            FileNotFoundError: 文件不存在时
            PermissionError: 文件不可读时
        """
        file_path = file_path.strip()

        FileValidator._check_path_not_empty(file_path)
        FileValidator._check_path_traversal(file_path)
        FileValidator._check_file_extension(file_path)
        FileValidator._check_file_exists(file_path)
        FileValidator._check_is_file(file_path)
        FileValidator._check_file_readable(file_path)
        FileValidator._check_file_size(file_path)

        logger.debug(
            f"文件验证通过: {file_path}, 大小: {os.path.getsize(file_path)} bytes"
        )
        return file_path

    @staticmethod
    def _check_path_not_empty(file_path: str) -> None:
        """
        检查文件路径是否为空。

        Args:
            file_path: 文件路径

        Raises:
            ValueError: 文件路径为空时
        """
        if not file_path:
            raise ValueError("文件路径不能为空")

    @staticmethod
    def _check_file_extension(file_path: str) -> None:
        """
        检查文件扩展名。

        Args:
            file_path: 文件路径

        Raises:
            ValueError: 文件扩展名不支持时
        """
        if not file_path.lower().endswith(tuple(FileValidator.VALID_EXTENSIONS)):
            raise ValueError(
                f"文件格式不支持: {file_path}. "
                f"请使用CSV或Excel文件（{', '.join(FileValidator.VALID_EXTENSIONS)}）。"
            )

    @staticmethod
    def _check_path_traversal(file_path: str) -> None:
        """
        检查路径遍历攻击。

        确保文件路径在预期的工作目录内，防止路径遍历攻击。

        Args:
            file_path: 文件路径

        Raises:
            ValueError: 检测到路径遍历攻击时
        """
        try:
            file_path_obj = Path(file_path)
            current_dir = Path.cwd()

            real_path = file_path_obj.resolve(strict=False)
            abs_path = file_path_obj.absolute()

            if real_path != abs_path:
                logger.warning(f"检测到符号链接: {file_path} -> {real_path}")

            if not str(abs_path).startswith(str(current_dir)):
                logger.error(f"检测到路径遍历攻击: {file_path}")
                logger.error(f"当前工作目录: {current_dir}")
                logger.error(f"文件绝对路径: {abs_path}")
                raise ValueError(
                    f"路径遍历攻击检测: 文件路径必须在当前工作目录内。"
                    f"当前工作目录: {current_dir}"
                )

            if ".." in str(abs_path.relative_to(current_dir)):
                logger.error(f"检测到路径遍历尝试: {file_path}")
                logger.error(
                    f"相对路径包含父目录引用: {abs_path.relative_to(current_dir)}"
                )
                raise ValueError("路径遍历攻击检测: 路径包含父目录引用。")

        except (OSError, ValueError) as e:
            logger.error(f"路径验证失败: {e}")
            raise ValueError(f"路径验证失败: {e}") from e

    @staticmethod
    def _check_file_exists(file_path: str) -> None:
        """
        检查文件是否存在。

        Args:
            file_path: 文件路径

        Raises:
            FileNotFoundError: 文件不存在时
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

    @staticmethod
    def _check_is_file(file_path: str) -> None:
        """
        检查是否为文件。

        Args:
            file_path: 文件路径

        Raises:
            ValueError: 路径不是文件时
        """
        if not os.path.isfile(file_path):
            raise ValueError(f"路径不是文件: {file_path}")

    @staticmethod
    def _check_file_readable(file_path: str) -> None:
        """
        检查文件是否可读。

        Args:
            file_path: 文件路径

        Raises:
            PermissionError: 文件不可读时
        """
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"文件不可读: {file_path}")

    @staticmethod
    def _check_file_size(file_path: str) -> None:
        """
        检查文件大小是否合理。

        Args:
            file_path: 文件路径

        Raises:
            ValueError: 文件过大或为空时
        """
        file_size = os.path.getsize(file_path)

        if file_size > MAX_FILE_SIZE:
            raise ValueError(
                f"文件过大: {file_path} ({file_size} bytes, "
                f"最大允许 {MAX_FILE_SIZE} bytes)"
            )

        if file_size == 0:
            raise ValueError(f"文件为空: {file_path}")
