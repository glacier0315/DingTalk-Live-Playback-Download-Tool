"""链接处理模块"""
import sys
import pandas as pd
from urllib.parse import urlparse, parse_qs


def read_links_file(file_path):
    try:
        file_path = clean_file_path(file_path)
        links = {}

        if file_path.endswith('.csv'):
            try:
                df = pd.read_csv(file_path, encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(file_path, encoding='gbk')
                except UnicodeDecodeError:
                    print(f"文件 {file_path} 使用的编码无法识别，请尝试其他编码格式。")
                    sys.exit(1)

            for col in df.columns:
                for i, value in df[col].dropna().items():
                    if isinstance(value, str) and value.startswith("https://n.dingtalk.com"):
                        links[i] = value

        elif file_path.endswith(('.xlsx', '.xls')):
            xls = pd.ExcelFile(file_path)
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                for col in df.columns:
                    for i, value in df[col].dropna().items():
                        if isinstance(value, str) and value.startswith("https://n.dingtalk.com"):
                            links[i] = value

        else:
            raise ValueError(f"文件格式不支持: {file_path}. 请使用CSV或Excel文件。")

        if not links:
            raise ValueError("未找到有效的钉钉直播链接。")

        return links

    except Exception as e:
        print(f"读取文件时发生错误: {e}")
        sys.exit(1)


def extract_live_uuid(dingtalk_url):
    parsed_url = urlparse(dingtalk_url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get('liveUuid', [None])[0]


def clean_file_path(input_path: str) -> str:
    """
    清理文件路径，移除周围的空白和引号
    
    Args:
        input_path: 输入的文件路径
    
    Returns:
        清理后的文件路径
    
    Raises:
        ValueError: 如果输入路径为空或无效
    """
    if not input_path:
        raise ValueError("文件路径不能为空")
    
    if not isinstance(input_path, str):
        raise ValueError(f"文件路径必须是字符串类型，实际类型: {type(input_path)}")
    
    cleaned = input_path.strip().replace('"', '').replace("'", "")
    
    if not cleaned:
        raise ValueError("清理后的文件路径为空")
    
    return cleaned
