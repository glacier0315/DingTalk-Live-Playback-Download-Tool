"""
钉钉直播回放下载工具 - 文件读取工具模块

本模块提供文件读取工具类，支持 CSV 和 Excel 文件。

作者：项目团队
依赖：pandas, openpyxl, xlrd
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2025-01-15: 添加日志记录
    - 2026-01-22: 重构-移除sys.exit调用,改为抛出FileReaderError,增强输入验证
"""

import os
import logging
import pandas as pd
from typing import Dict
from .path_helper import clean_file_path

logger = logging.getLogger(__name__)


class FileReaderError(Exception):
    """文件读取异常"""
    pass


class FileReader:
    """
    文件读取类，负责从 CSV/Excel 文件中读取链接。

    该类支持 CSV 和 Excel 文件，自动处理不同编码。

    Attributes:
        file_path (str): 文件路径
    """

    def __init__(self, file_path: str):
        """
        初始化文件读取器。

        Args:
            file_path: 文件路径（CSV/Excel）

        Raises:
            FileNotFoundError: 文件不存在时
            PermissionError: 文件不可读时
            ValueError: 文件格式不支持或文件过大时
            FileReaderError: 其他错误时
        """
        self.file_path = clean_file_path(file_path)
        logger.debug(f"文件读取器初始化 - 文件路径: {self.file_path}")

        self._validate_file_path()

    def _validate_file_path(self) -> None:
        """
        验证文件路径。

        检查文件扩展名、文件是否存在、文件是否可读、文件大小是否合理。

        Raises:
            FileNotFoundError: 文件不存在时
            PermissionError: 文件不可读时
            ValueError: 文件格式不支持或文件过大时
        """
        valid_extensions = [".csv", ".xlsx", ".xls"]

        if not self.file_path.lower().endswith(tuple(valid_extensions)):
            raise ValueError(
                f"文件格式不支持: {self.file_path}. 请使用CSV或Excel文件。"
            )

        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"文件不存在: {self.file_path}")

        if not os.path.isfile(self.file_path):
            raise ValueError(f"路径不是文件: {self.file_path}")

        if not os.access(self.file_path, os.R_OK):
            raise PermissionError(f"文件不可读: {self.file_path}")

        file_size = os.path.getsize(self.file_path)
        max_size = 100 * 1024 * 1024

        if file_size > max_size:
            raise ValueError(
                f"文件过大: {self.file_path} ({file_size} bytes, 最大允许 {max_size} bytes)"
            )

        if file_size == 0:
            raise ValueError(f"文件为空: {self.file_path}")

        logger.debug(f"文件验证通过: {self.file_path}, 大小: {file_size} bytes")

    def read_links(self) -> Dict[int, str]:
        """
        从文件中读取钉钉直播链接。

        遍历文件中的所有单元格，提取以 "https://n.dingtalk.com" 开头的链接。

        Returns:
            链接字典 {index: url}

        Raises:
            FileReaderError: 读取失败时
        """
        logger.info(f"开始读取文件链接: {self.file_path}")

        try:
            links = {}

            if self.file_path.lower().endswith(".csv"):
                self._read_csv(links)
            elif self.file_path.lower().endswith((".xlsx", ".xls")):
                self._read_excel(links)

            if not links:
                logger.error("未找到有效的钉钉直播链接")
                raise FileReaderError("未找到有效的钉钉直播链接。")

            logger.info(f"从文件中读取到 {len(links)} 个链接")
            return links

        except FileReaderError:
            raise
        except Exception as e:
            logger.error(f"读取文件时发生错误: {e}", exc_info=True)
            raise FileReaderError(f"读取文件失败: {e}") from e

    def _read_csv(self, links: Dict[int, str]) -> None:
        """
        读取 CSV 文件。

        Args:
            links: 链接字典（用于存储提取的链接）

        Raises:
            FileReaderError: 读取失败时
        """
        encodings = ["utf-8", "gbk", "gb18030"]
        last_error = None

        for encoding in encodings:
            try:
                df = pd.read_csv(self.file_path, encoding=encoding)
                self._extract_links_from_dataframe(df, links)
                logger.info(f"CSV 文件读取成功，编码: {encoding}")
                return
            except UnicodeDecodeError as e:
                last_error = e
                continue
            except Exception as e:
                logger.error(f"读取 CSV 文件时发生错误: {e}", exc_info=True)
                raise FileReaderError(f"读取CSV文件失败: {e}") from e

        logger.error(f"文件 {self.file_path} 使用的编码无法识别，请尝试其他编码格式")
        raise FileReaderError(f"文件编码无法识别: {last_error}") from last_error

    def _read_excel(self, links: Dict[int, str]) -> None:
        """
        读取 Excel 文件。

        Args:
            links: 链接字典（用于存储提取的链接）
        """
        xls = pd.ExcelFile(self.file_path)
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            self._extract_links_from_dataframe(df, links)

    def _extract_links_from_dataframe(self, df: pd.DataFrame, links: Dict[int, str]) -> None:
        """
        从 DataFrame 中提取链接。

        Args:
            df: Pandas DataFrame
            links: 链接字典（用于存储提取的链接）
        """
        for col in df.columns:
            for i, value in df[col].dropna().items():
                if isinstance(value, str) and value.startswith("https://n.dingtalk.com"):
                    links[i] = value

    @staticmethod
    def clean_file_path(file_path: str) -> str:
        """
        清理文件路径。

        去除路径中的多余引号和空格。

        Args:
            file_path: 文件路径

        Returns:
            清理后的文件路径
        """
        return clean_file_path(file_path)
