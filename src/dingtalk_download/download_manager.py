"""下载管理器模块。

该模块提供了 M3U8 视频文件的下载功能，支持自定义请求头、Cookie 和保存路径。
主要功能包括：
- 自动选择下载目录
- 自定义下载路径
- 配置请求头和 Cookie
- 执行下载任务

Example:
    >>> from dingtalk_download.download_manager import auto_download_m3u8_with_options
    >>> cookies = {'session_id': 'xxx', 'token': 'yyy'}
    >>> headers = {'User-Agent': 'Mozilla/5.0...', 'Referer': 'https://...'}
    >>> result = auto_download_m3u8_with_options(
    ...     'video.m3u8',
    ...     'my_video',
    ...     'https://example.com/',
    ...     cookies,
    ...     headers
    ... )
"""
import subprocess
import logging
import tkinter as tk
from tkinter import filedialog
import os
from typing import Optional, Dict, Any


logger = logging.getLogger(__name__)

# 默认下载目录名称
DEFAULT_DOWNLOAD_DIR = 'Downloads'

# 默认请求头配置
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
DEFAULT_REFERER = 'https://n.dingtalk.com/'
DEFAULT_ACCEPT = 'application/vnd.apple.mpegurl, text/plain, */*'

# 支持的请求头类型
SUPPORTED_HEADERS = ['User-Agent', 'Referer', 'Accept', 'Accept-Language', 'Accept-Encoding']


def auto_download_m3u8_with_options(
    m3u8_file: str,
    save_name: str,
    prefix: str,
    cookies_data: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Optional[str]:
    """自动下载 M3U8 文件到默认 Downloads 目录。
    
    该函数自动将 M3U8 文件下载到当前工作目录下的 Downloads 文件夹中。
    如果 Downloads 文件夹不存在，会自动创建。
    
    Args:
        m3u8_file: M3U8 文件路径。
        save_name: 保存的文件名（不含扩展名）。
        prefix: 基础 URL 前缀，用于解析 M3U8 文件中的相对路径。
        cookies_data: Cookie 数据字典，可选。
        headers: 请求头字典，可选。
    
    Returns:
        保存目录路径，如果用户取消选择则返回 None。
    
    Examples:
        >>> result = auto_download_m3u8_with_options(
        ...     'video.m3u8',
        ...     'my_video',
        ...     'https://example.com/'
        ... )
        >>> print(result)
        'd:\\path\\to\\Downloads'
    """
    logger.info(f"自动下载 M3U8 文件: {m3u8_file}")
    
    base_dir = os.getcwd()
    downloads_dir = os.path.join(base_dir, DEFAULT_DOWNLOAD_DIR)
    
    logger.debug(f"默认下载目录: {downloads_dir}")
    return download_m3u8_with_options(
        m3u8_file,
        save_name,
        prefix,
        cookies_data,
        headers,
        downloads_dir
    )


def download_m3u8_with_options(
    m3u8_file: str,
    save_name: str,
    prefix: str,
    cookies_data: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None,
    save_dir: Optional[str] = None
) -> Optional[str]:
    """下载 M3U8 文件到指定目录。
    
    如果未指定保存目录，则弹出文件选择对话框让用户选择。
    如果用户取消选择，则返回 None。
    
    Args:
        m3u8_file: M3U8 文件路径。
        save_name: 保存的文件名（不含扩展名）。
        prefix: 基础 URL 前缀，用于解析 M3U8 文件中的相对路径。
        cookies_data: Cookie 数据字典，可选。
        headers: 请求头字典，可选。
        save_dir: 保存目录路径，可选。如果为 None，则弹出选择对话框。
    
    Returns:
        保存目录路径，如果用户取消选择则返回 None。
    
    Examples:
        >>> result = download_m3u8_with_options(
        ...     'video.m3u8',
        ...     'my_video',
        ...     'https://example.com/',
        ...     save_dir='d:\\videos'
        ... )
        >>> print(result)
        'd:\\videos'
    """
    logger.info(f"下载 M3U8 文件到指定目录: {m3u8_file}")
    
    root = tk.Tk()
    root.withdraw()
    
    if save_dir is None:
        save_dir = filedialog.askdirectory(title="选择保存视频的目录")
        logger.info(f"用户选择的保存目录: {save_dir}")

    if not save_dir:
        logger.info("用户取消了选择。视频下载已中止。")
        print("用户取消了选择。视频下载已中止。")
        return None
    
    return execute_download(
        m3u8_file,
        save_name,
        prefix,
        cookies_data,
        headers,
        save_dir
    )


def download_m3u8_with_reused_path(
    m3u8_file: str,
    save_name: str,
    prefix: str,
    reused_path: Optional[str],
    cookies_data: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None
) -> Optional[str]:
    """下载 M3U8 文件到复用的路径或新选择的路径。
    
    如果提供了复用路径，则直接使用该路径。
    如果未提供复用路径，则弹出文件选择对话框让用户选择。
    
    Args:
        m3u8_file: M3U8 文件路径。
        save_name: 保存的文件名（不含扩展名）。
        prefix: 基础 URL 前缀，用于解析 M3U8 文件中的相对路径。
        reused_path: 复用的保存目录路径，可选。
        cookies_data: Cookie 数据字典，可选。
        headers: 请求头字典，可选。
    
    Returns:
        保存目录路径，如果用户取消选择则返回 None。
    
    Examples:
        >>> result = download_m3u8_with_reused_path(
        ...     'video.m3u8',
        ...     'my_video',
        ...     'https://example.com/',
        ...     'd:\\videos'
        ... )
        >>> print(result)
        'd:\\videos'
    """
    logger.info(f"下载 M3U8 文件到复用路径: {m3u8_file}")
    
    if reused_path:
        logger.debug(f"使用复用路径: {reused_path}")
        return execute_download(
            m3u8_file,
            save_name,
            prefix,
            cookies_data,
            headers,
            reused_path
        )
    
    root = tk.Tk()
    root.withdraw()
    save_dir = filedialog.askdirectory(title="选择保存视频的目录")
    logger.info(f"用户选择的保存目录: {save_dir}")

    if not save_dir:
        logger.info("用户取消了选择。视频下载已中止。")
        print("用户取消了选择。视频下载已中止。")
        return None
    
    return execute_download(
        m3u8_file,
        save_name,
        prefix,
        cookies_data,
        headers,
        save_dir
    )


def _validate_download_parameters(
    m3u8_file: str,
    save_name: str,
    save_dir: str
) -> None:
    """验证下载参数的有效性。
    
    检查 M3U8 文件是否存在、保存目录是否存在且可写等。
    
    Args:
        m3u8_file: M3U8 文件路径。
        save_name: 保存的文件名。
        save_dir: 保存目录路径。
    
    Raises:
        ValueError: 如果参数无效。
        FileNotFoundError: 如果文件或目录不存在。
        PermissionError: 如果目录不可写。
    
    Examples:
        >>> _validate_download_parameters('video.m3u8', 'my_video', 'd:\\videos')
    """
    logger.debug("验证下载参数")
    
    if not m3u8_file:
        error_msg = "M3U8 文件路径不能为空"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    if not os.path.exists(m3u8_file):
        error_msg = f"M3U8 文件不存在: {m3u8_file}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    if not save_name:
        error_msg = "保存文件名不能为空"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    if not save_dir:
        error_msg = "保存目录不能为空"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    if not os.path.exists(save_dir):
        error_msg = f"保存目录不存在: {save_dir}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    if not os.access(save_dir, os.W_OK):
        error_msg = f"保存目录不可写: {save_dir}"
        logger.error(error_msg)
        raise PermissionError(error_msg)
    
    logger.debug("下载参数验证通过")


def _build_cookie_header(cookies_data: Dict[str, str]) -> str:
    """构建 Cookie 请求头字符串。
    
    将 Cookie 字典转换为请求头格式。
    
    Args:
        cookies_data: Cookie 数据字典。
    
    Returns:
        Cookie 请求头字符串。
    
    Examples:
        >>> cookies = {'session_id': 'xxx', 'token': 'yyy'}
        >>> header = _build_cookie_header(cookies)
        >>> 'session_id=xxx' in header
        True
    """
    logger.debug("构建 Cookie 请求头")
    cookie_string = "; ".join([f"{name}={value}" for name, value in cookies_data.items()])
    logger.debug(f"Cookie 请求头: {cookie_string[:50]}...")
    return cookie_string


def _build_download_command(
    m3u8_file: str,
    save_name: str,
    save_dir: str,
    prefix: str,
    cookies_data: Optional[Dict[str, str]],
    headers: Optional[Dict[str, str]]
) -> list:
    """构建下载命令。
    
    根据参数构建 N_m3u8DL-RE 下载命令。
    
    Args:
        m3u8_file: M3U8 文件路径。
        save_name: 保存的文件名。
        save_dir: 保存目录路径。
        prefix: 基础 URL 前缀。
        cookies_data: Cookie 数据字典，可选。
        headers: 请求头字典，可选。
    
    Returns:
        下载命令列表。
    
    Examples:
        >>> command = _build_download_command(
        ...     'video.m3u8',
        ...     'my_video',
        ...     'd:\\videos',
        ...     'https://example.com/',
        ...     None,
        ...     None
        ... )
        >>> isinstance(command, list)
        True
    """
    from .utils import get_executable_name
    
    logger.debug("构建下载命令")
    
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
        cookie_string = _build_cookie_header(cookies_data)
        command.extend(["-H", f"Cookie: {cookie_string}"])
        headers_added.append("Cookie")
        logger.info("已添加 Cookie 请求头")
    
    if headers:
        if 'User-Agent' in headers:
            command.extend(["-H", f"User-Agent: {headers['User-Agent']}"])
            headers_added.append("User-Agent")
            logger.info("已添加 User-Agent 请求头")
        else:
            logger.warning("headers 中没有 User-Agent")
        
        if 'Referer' in headers:
            command.extend(["-H", f"Referer: {headers['Referer']}"])
            headers_added.append("Referer")
            logger.info("已添加 Referer 请求头")
        else:
            command.extend(["-H", f"Referer: {DEFAULT_REFERER}"])
            headers_added.append("Referer (默认)")
            logger.info("已添加默认 Referer 请求头")
        
        if 'Accept' in headers:
            command.extend(["-H", f"Accept: {headers['Accept']}"])
            headers_added.append("Accept")
            logger.info("已添加 Accept 请求头")
        
        if 'Accept-Language' in headers:
            command.extend(["-H", f"Accept-Language: {headers['Accept-Language']}"])
            headers_added.append("Accept-Language")
            logger.info("已添加 Accept-Language 请求头")
        
        if 'Accept-Encoding' in headers:
            command.extend(["-H", f"Accept-Encoding: {headers['Accept-Encoding']}"])
            headers_added.append("Accept-Encoding")
            logger.info("已添加 Accept-Encoding 请求头")
    else:
        command.extend(["-H", f"User-Agent: {DEFAULT_USER_AGENT}"])
        command.extend(["-H", f"Referer: {DEFAULT_REFERER}"])
        command.extend(["-H", f"Accept: {DEFAULT_ACCEPT}"])
        headers_added.extend(["User-Agent (默认)", "Referer (默认)", "Accept (默认)"])
        logger.info("已添加默认请求头")
    
    logger.info(f"总共添加了 {len(headers_added)} 个请求头: {', '.join(headers_added)}")
    return command


def execute_download(
    m3u8_file: str,
    save_name: str,
    prefix: str,
    cookies_data: Optional[Dict[str, str]],
    headers: Optional[Dict[str, str]],
    save_dir: str
) -> str:
    """执行下载任务。
    
    验证参数、构建下载命令并执行下载任务。
    
    Args:
        m3u8_file: M3U8 文件路径。
        save_name: 保存的文件名。
        prefix: 基础 URL 前缀。
        cookies_data: Cookie 数据字典，可选。
        headers: 请求头字典，可选。
        save_dir: 保存目录路径。
    
    Returns:
        保存目录路径。
    
    Raises:
        FileNotFoundError: 如果 M3U8 文件不存在。
        ValueError: 如果参数无效。
        RuntimeError: 如果下载失败。
    
    Examples:
        >>> result = execute_download(
        ...     'video.m3u8',
        ...     'my_video',
        ...     'https://example.com/',
        ...     None,
        ...     None,
        ...     'd:\\videos'
        ... )
        >>> print(result)
        'd:\\videos'
    """
    logger.info(f"开始执行下载任务: {m3u8_file}")
    
    _validate_download_parameters(m3u8_file, save_name, save_dir)
    command = _build_download_command(
        m3u8_file,
        save_name,
        save_dir,
        prefix,
        cookies_data,
        headers
    )
    
    logger.debug(f"下载命令: {' '.join(command[:5])}...")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        logger.info(f"视频下载成功完成。文件保存路径: {save_dir}")
        print(f"视频下载成功完成。文件保存路径: {save_dir}")
        return save_dir
    
    except subprocess.CalledProcessError as e:
        from .utils import get_executable_name
        error_msg = f"下载失败，退出码: {e.returncode}\n"
        error_msg += f"标准输出: {e.stdout}\n"
        error_msg += f"标准错误: {e.stderr}"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    
    except FileNotFoundError as e:
        from .utils import get_executable_name
        error_msg = f"找不到可执行文件: {get_executable_name()}。请确保已安装 N_m3u8DL-RE 或 ffmpeg。"
        logger.error(error_msg)
        raise RuntimeError(error_msg) from e
    
    except Exception as e:
        error_msg = f"下载过程中发生未知错误: {e}"
        logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e
