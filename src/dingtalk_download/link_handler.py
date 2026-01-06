"""链接处理模块

该模块提供文件读取和链接提取功能，支持从CSV和Excel文件中
提取钉钉直播回放链接。
"""

import logging
import sys
from typing import Dict, Optional
import pandas as pd
from urllib.parse import urlparse, parse_qs

from .utils import clean_file_path

# 配置日志
logger = logging.getLogger(__name__)

# 支持的文件扩展名
SUPPORTED_CSV_EXTENSIONS = ['.csv']
SUPPORTED_EXCEL_EXTENSIONS = ['.xlsx', '.xls']
SUPPORTED_EXTENSIONS = SUPPORTED_CSV_EXTENSIONS + SUPPORTED_EXCEL_EXTENSIONS

# 钉钉直播链接前缀
DINGTALK_LIVE_URL_PREFIX = "https://n.dingtalk.com"


def read_links_file(file_path: str) -> Dict[int, str]:
    """从文件中读取钉钉直播回放链接。

    支持从CSV和Excel文件中提取钉钉直播回放链接。
    会尝试多种编码格式读取CSV文件（UTF-8、GBK）。

    Args:
        file_path: 文件路径，支持CSV或Excel格式。

    Returns:
        包含链接索引和URL的字典。键为索引，值为钉钉直播链接URL。

    Raises:
        ValueError: 如果文件格式不支持或未找到有效链接。
        FileNotFoundError: 如果文件不存在。
        RuntimeError: 如果文件读取失败。

    Examples:
        >>> links = read_links_file("links.csv")
        >>> print(len(links))
        5
        >>> print(links[0])
        'https://n.dingtalk.com/...'
    """
    logger.info(f"开始读取链接文件: {file_path}")

    try:
        # 清理文件路径
        cleaned_path = clean_file_path(file_path)
        logger.debug(f"清理后的文件路径: {cleaned_path}")

        # 验证文件扩展名
        file_extension = _get_file_extension(cleaned_path)
        if file_extension not in SUPPORTED_EXTENSIONS:
            error_msg = f"文件格式不支持: {cleaned_path}. 支持的格式: {', '.join(SUPPORTED_EXTENSIONS)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 根据文件类型读取链接
        if file_extension in SUPPORTED_CSV_EXTENSIONS:
            links = _read_csv_links(cleaned_path)
        elif file_extension in SUPPORTED_EXCEL_EXTENSIONS:
            links = _read_excel_links(cleaned_path)
        else:
            error_msg = f"不支持的文件扩展名: {file_extension}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 验证是否找到有效链接
        if not links:
            error_msg = "未找到有效的钉钉直播链接"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info(f"成功读取 {len(links)} 个钉钉直播链接")
        return links

    except (ValueError, FileNotFoundError) as e:
        logger.error(f"读取文件时发生错误: {e}")
        raise
    except Exception as e:
        error_msg = f"读取文件时发生未知错误: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def _get_file_extension(file_path: str) -> str:
    """获取文件扩展名。

    Args:
        file_path: 文件路径。

    Returns:
        文件扩展名（包含点号，如 '.csv'）。
    """
    import os
    _, extension = os.path.splitext(file_path)
    return extension.lower()


def _read_csv_links(file_path: str) -> Dict[int, str]:
    """从CSV文件中读取钉钉直播链接。

    尝试使用多种编码格式读取CSV文件，包括UTF-8和GBK。

    Args:
        file_path: CSV文件路径。

    Returns:
        包含链接索引和URL的字典。

    Raises:
        RuntimeError: 如果所有编码格式都失败。
    """
    logger.debug(f"尝试读取CSV文件: {file_path}")

    # 尝试的编码列表
    encodings = ['utf-8', 'gbk', 'utf-8-sig']

    for encoding in encodings:
        try:
            logger.debug(f"尝试使用编码: {encoding}")
            dataframe = pd.read_csv(file_path, encoding=encoding)
            logger.info(f"成功使用 {encoding} 编码读取CSV文件")
            return _extract_links_from_dataframe(dataframe)
        except UnicodeDecodeError:
            logger.warning(f"编码 {encoding} 失败，尝试下一个编码")
            continue
        except Exception as e:
            logger.error(f"使用编码 {encoding} 读取文件时发生错误: {e}")
            continue

    error_msg = f"文件 {file_path} 使用的编码无法识别，请尝试其他编码格式"
    logger.error(error_msg)
    raise RuntimeError(error_msg)


def _read_excel_links(file_path: str) -> Dict[int, str]:
    """从Excel文件中读取钉钉直播链接。

    支持读取Excel文件的所有工作表。

    Args:
        file_path: Excel文件路径。

    Returns:
        包含链接索引和URL的字典。
    """
    logger.debug(f"尝试读取Excel文件: {file_path}")

    links = {}

    try:
        excel_file = pd.ExcelFile(file_path)
        logger.info(f"发现 {len(excel_file.sheet_names)} 个工作表")

        for sheet_name in excel_file.sheet_names:
            logger.debug(f"读取工作表: {sheet_name}")
            dataframe = pd.read_excel(excel_file, sheet_name=sheet_name)
            sheet_links = _extract_links_from_dataframe(dataframe)
            links.update(sheet_links)

        logger.info(f"从Excel文件中提取了 {len(links)} 个链接")
        return links

    except Exception as e:
        error_msg = f"读取Excel文件时发生错误: {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e


def _extract_links_from_dataframe(dataframe: pd.DataFrame) -> Dict[int, str]:
    """从DataFrame中提取钉钉直播链接。

    遍历DataFrame的所有列和行，提取以钉钉直播链接前缀开头的URL。

    Args:
        dataframe: pandas DataFrame对象。

    Returns:
        包含链接索引和URL的字典。
    """
    links = {}

    for column_name in dataframe.columns:
        for index, value in dataframe[column_name].dropna().items():
            if isinstance(value, str) and value.startswith(DINGTALK_LIVE_URL_PREFIX):
                links[index] = value
                logger.debug(f"找到链接 (索引 {index}, 列 {column_name}): {value}")

    return links


def extract_live_uuid(dingtalk_url: str) -> Optional[str]:
    """从钉钉直播URL中提取liveUuid参数。

    解析URL查询参数，提取liveUuid参数的值。

    Args:
        dingtalk_url: 钉钉直播URL。

    Returns:
        liveUuid参数值，如果不存在则返回None。

    Examples:
        >>> url = "https://n.dingtalk.com/live?liveUuid=abc123"
        >>> extract_live_uuid(url)
        'abc123'
        >>> url = "https://n.dingtalk.com/live"
        >>> extract_live_uuid(url)
        None
    """
    logger.debug(f"从URL提取liveUuid: {dingtalk_url}")

    try:
        parsed_url = urlparse(dingtalk_url)
        query_params = parse_qs(parsed_url.query)
        live_uuid = query_params.get('liveUuid', [None])[0]

        if live_uuid:
            logger.debug(f"成功提取liveUuid: {live_uuid}")
        else:
            logger.warning(f"URL中未找到liveUuid参数: {dingtalk_url}")

        return live_uuid

    except Exception as e:
        logger.error(f"提取liveUuid时发生错误: {e}")
        return None
