"""通用工具函数模块"""
import platform
import os


def validate_input(prompt: str, valid_options: list, default_option: str = None) -> str:
    """
    验证用户输入
    
    Args:
        prompt: 提示信息
        valid_options: 有效选项列表
        default_option: 默认选项（当用户输入为空时返回）
    
    Returns:
        用户选择的选项
    
    Raises:
        ValueError: 如果参数无效
    """
    if not prompt:
        raise ValueError("提示信息不能为空")
    
    if not isinstance(prompt, str):
        raise ValueError(f"提示信息必须是字符串类型，实际类型: {type(prompt)}")
    
    if not isinstance(valid_options, list):
        raise ValueError(f"有效选项必须是列表类型，实际类型: {type(valid_options)}")
    
    if not valid_options:
        raise ValueError("有效选项列表不能为空")
    
    if default_option is not None and default_option not in valid_options:
        raise ValueError(f"默认选项 '{default_option}' 不在有效选项列表中")
    
    while True:
        choice = input(prompt)
        if choice == '' and default_option is not None:
            return default_option
        if choice in valid_options:
            return choice
        print("无效的选择，请重新输入。")


def get_executable_name() -> str:
    """
    获取可执行文件名
    
    Returns:
        可执行文件名
    
    Raises:
        RuntimeError: 如果操作系统不支持
    """
    system = platform.system()
    if system == 'Windows':
        return 'N_m3u8DL-RE.exe'
    elif system == 'Linux' or system == 'Darwin':
        return './N_m3u8DL-RE'
    else:
        raise RuntimeError(f"不支持的操作系统: {system}")


def clean_file_path(input_path):
    return input_path.strip().replace('"', '').replace("'", "")
