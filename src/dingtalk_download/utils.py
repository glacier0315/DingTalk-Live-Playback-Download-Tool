"""通用工具函数模块"""
import platform
import os


def validate_input(prompt, valid_options, default_option=None):
    while True:
        choice = input(prompt)
        if choice == '' and default_option is not None:
            return default_option
        if choice in valid_options:
            return choice
        print("无效的选择，请重新输入。")


def get_executable_name():
    system = platform.system()
    if system == 'Windows':
        return 'N_m3u8DL-RE.exe'
    elif system == 'Linux' or system == 'Darwin':
        return './N_m3u8DL-RE'
    else:
        raise Exception(f"不支持的操作系统: {system}")


def clean_file_path(input_path):
    return input_path.strip().replace('"', '').replace("'", "")
