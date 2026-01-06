"""下载管理器模块"""
import subprocess
import tkinter as tk
from tkinter import filedialog
import os
from typing import Optional, Dict, Any


def auto_download_m3u8_with_options(m3u8_file, save_name, prefix, cookies_data=None, headers=None):
     # 获取当前工作目录
    base_dir = os.getcwd()
    
    # 确定 Downloads 文件夹的路径
    downloads_dir = os.path.join(base_dir, 'Downloads')
    return download_m3u8_with_options(m3u8_file, save_name, prefix, cookies_data, headers, downloads_dir)


def download_m3u8_with_options(m3u8_file, save_name, prefix, cookies_data=None, headers=None, save_dir=None):
    root = tk.Tk()
    root.withdraw()
    
    if save_dir is None:
        save_dir = filedialog.askdirectory(title="选择保存视频的目录")

    if not save_dir:
        print("用户取消了选择。视频下载已中止。")
        return
    
    return execute_download(m3u8_file, save_name, prefix, cookies_data, headers, save_dir)


def download_m3u8_with_reused_path(m3u8_file, save_name, prefix, reused_path, cookies_data=None, headers=None):
    if reused_path:
        return execute_download(m3u8_file, save_name, prefix, cookies_data, headers, reused_path)
    
    root = tk.Tk()
    root.withdraw()
    save_dir = filedialog.askdirectory(title="选择保存视频的目录")

    if not save_dir:
        print("用户取消了选择。视频下载已中止。")
        return
    
    return execute_download(m3u8_file, save_name, prefix, cookies_data, headers, save_dir)


def execute_download(m3u8_file: str, save_name: str, prefix: str, 
                     cookies_data: Optional[Dict[str, str]], 
                     headers: Optional[Dict[str, str]], 
                     save_dir: str) -> str:
    """
    执行下载任务
    
    Args:
        m3u8_file: M3U8 文件路径
        save_name: 保存的文件名
        prefix: 基础 URL 前缀
        cookies_data: Cookie 数据字典
        headers: 请求头字典
        save_dir: 保存目录
    
    Returns:
        保存目录路径
    
    Raises:
        FileNotFoundError: 如果 M3U8 文件不存在
        ValueError: 如果参数无效
        RuntimeError: 如果下载失败
    """
    from .utils import get_executable_name
    
    # 参数验证
    if not m3u8_file:
        raise ValueError("M3U8 文件路径不能为空")
    
    if not os.path.exists(m3u8_file):
        raise FileNotFoundError(f"M3U8 文件不存在: {m3u8_file}")
    
    if not save_name:
        raise ValueError("保存文件名不能为空")
    
    if not save_dir:
        raise ValueError("保存目录不能为空")
    
    if not os.path.exists(save_dir):
        raise FileNotFoundError(f"保存目录不存在: {save_dir}")
    
    if not os.access(save_dir, os.W_OK):
        raise PermissionError(f"保存目录不可写: {save_dir}")
    
    command = [
        get_executable_name(),
        m3u8_file,
        "--ui-language", "zh-CN",
        "--save-name", save_name,
        "--save-dir", save_dir,
        "--base-url", prefix,
    ]
    
    headers_added = []
    
    if cookies_data:
        cookie_string = "; ".join([f"{name}={value}" for name, value in cookies_data.items()])
        command.extend(["-H", f"Cookie: {cookie_string}"])
        headers_added.append("Cookie")
        print(f"已添加 Cookie 请求头")
    
    if headers:
        if 'User-Agent' in headers:
            command.extend(["-H", f"User-Agent: {headers['User-Agent']}"])
            headers_added.append("User-Agent")
            print(f"已添加 User-Agent 请求头")
        else:
            print("警告: headers 中没有 User-Agent")
        
        if 'Referer' in headers:
            command.extend(["-H", f"Referer: {headers['Referer']}"])
            headers_added.append("Referer")
            print(f"已添加 Referer 请求头")
        else:
            command.extend(["-H", "Referer: https://n.dingtalk.com/"])
            headers_added.append("Referer (默认)")
            print(f"已添加默认 Referer 请求头")
        
        if 'Accept' in headers:
            command.extend(["-H", f"Accept: {headers['Accept']}"])
            headers_added.append("Accept")
            print(f"已添加 Accept 请求头")
        
        if 'Accept-Language' in headers:
            command.extend(["-H", f"Accept-Language: {headers['Accept-Language']}"])
            headers_added.append("Accept-Language")
            print(f"已添加 Accept-Language 请求头")
        
        if 'Accept-Encoding' in headers:
            command.extend(["-H", f"Accept-Encoding: {headers['Accept-Encoding']}"])
            headers_added.append("Accept-Encoding")
            print(f"已添加 Accept-Encoding 请求头")
    
    else:
        command.extend(["-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"])
        command.extend(["-H", "Referer: https://n.dingtalk.com/"])
        command.extend(["-H", "Accept: application/vnd.apple.mpegurl, text/plain, */*"])
        headers_added.extend(["User-Agent (默认)", "Referer (默认)", "Accept (默认)"])
        print("已添加默认请求头")
    
    print(f"总共添加了 {len(headers_added)} 个请求头: {', '.join(headers_added)}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"视频下载成功完成。文件保存路径: {save_dir}")
        return save_dir
    except subprocess.CalledProcessError as e:
        error_msg = f"下载失败，退出码: {e.returncode}\n"
        error_msg += f"标准输出: {e.stdout}\n"
        error_msg += f"标准错误: {e.stderr}"
        raise RuntimeError(error_msg) from e
    except FileNotFoundError as e:
        raise RuntimeError(f"找不到可执行文件: {get_executable_name()}。请确保已安装 N_m3u8DL-RE 或 ffmpeg。") from e
    except Exception as e:
        raise RuntimeError(f"下载过程中发生未知错误: {e}") from e
