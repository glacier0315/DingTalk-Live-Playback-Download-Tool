"""
钉钉直播回放下载工具 - N_m3u8DL-RE 调用封装模块

本模块负责调用 N_m3u8DL-RE 工具下载 m3u8 视频流。

作者：项目团队
依赖：subprocess, platform
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
"""

import subprocess
import platform
from typing import Dict, Optional, List


class NM3u8DLRE:
    """
    N_m3u8DL-RE 调用类，负责调用 N_m3u8DL-RE 工具。

    该类封装了 N_m3u8DL-RE 工具的调用逻辑，提供统一的接口供上层模块使用。

    Attributes:
        executable_path (str): 可执行文件路径
    """

    def __init__(self, executable_path: Optional[str] = None):
        """
        初始化 N_m3u8DL-RE 调用器。

        Args:
            executable_path: 可执行文件路径，默认为 None（自动查找）
        """
        if executable_path is None:
            self.executable_path = self.get_executable_name()
        else:
            self.executable_path = executable_path

    def download(
        self,
        m3u8_file: str,
        save_name: str,
        save_dir: str,
        prefix: str,
        cookies_data: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        下载 m3u8 视频。

        构建下载命令并调用 N_m3u8DL-RE 工具。

        Args:
            m3u8_file: m3u8 文件路径
            save_name: 保存文件名
            save_dir: 保存目录
            prefix: 基础 URL
            cookies_data: Cookie 字典
            headers: 请求头字典

        Returns:
            下载是否成功

        Raises:
            Exception: 下载失败时
        """
        try:
            command = self.build_command(
                m3u8_file, save_name, save_dir, prefix, cookies_data, headers
            )
            subprocess.run(command)
            print(f"视频下载成功完成。文件保存路径: {save_dir}")
            return True
        except Exception as e:
            print(f"下载视频时发生错误: {e}")
            return False

    def build_command(
        self,
        m3u8_file: str,
        save_name: str,
        save_dir: str,
        prefix: str,
        cookies_data: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        """
        构建下载命令。

        构建 N_m3u8DL-RE 下载命令，包括文件名、保存目录、基础 URL、Cookie 和请求头。

        Args:
            m3u8_file: m3u8 文件路径
            save_name: 保存文件名
            save_dir: 保存目录
            prefix: 基础 URL
            cookies_data: Cookie 字典
            headers: 请求头字典

        Returns:
            命令列表
        """
        command = [
            self.executable_path,
            m3u8_file,
            "--ui-language",
            "zh-CN",
            "--save-name",
            save_name,
            "--save-dir",
            save_dir,
            "--base-url",
            prefix,
        ]

        headers_added = []

        if cookies_data:
            cookie_string = "; ".join([f"{name}={value}" for name, value in cookies_data.items()])
            command.extend(["-H", f"Cookie: {cookie_string}"])
            headers_added.append("Cookie")
            print(f"已添加 Cookie 请求头")

        if headers:
            if "User-Agent" in headers:
                command.extend(["-H", f"User-Agent: {headers['User-Agent']}"])
                headers_added.append("User-Agent")
                print(f"已添加 User-Agent 请求头")
            else:
                print("警告: headers 中没有 User-Agent")

            if "Referer" in headers:
                command.extend(["-H", f"Referer: {headers['Referer']}"])
                headers_added.append("Referer")
                print(f"已添加 Referer 请求头")
            else:
                command.extend(["-H", "Referer: https://n.dingtalk.com/"])
                headers_added.append("Referer (默认)")
                print(f"已添加默认 Referer 请求头")

            if "Accept" in headers:
                command.extend(["-H", f"Accept: {headers['Accept']}"])
                headers_added.append("Accept")
                print(f"已添加 Accept 请求头")

            if "Accept-Language" in headers:
                command.extend(["-H", f"Accept-Language: {headers['Accept-Language']}"])
                headers_added.append("Accept-Language")
                print(f"已添加 Accept-Language 请求头")

            if "Accept-Encoding" in headers:
                command.extend(["-H", f"Accept-Encoding: {headers['Accept-Encoding']}"])
                headers_added.append("Accept-Encoding")
                print(f"已添加 Accept-Encoding 请求头")
        else:
            command.extend(
                [
                    "-H",
                    "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                ]
            )
            command.extend(["-H", "Referer: https://n.dingtalk.com/"])
            command.extend(["-H", "Accept: application/vnd.apple.mpegurl, text/plain, */*"])
            headers_added.extend(["User-Agent (默认)", "Referer (默认)", "Accept (默认)"])
            print("已添加默认请求头")

        print(f"总共添加了 {len(headers_added)} 个请求头: {', '.join(headers_added)}")

        return command

    @staticmethod
    def get_executable_name() -> str:
        """
        获取可执行文件名。

        根据操作系统返回对应的可执行文件名。

        Returns:
            可执行文件名
        """
        system = platform.system()
        if system == "Windows":
            return "N_m3u8DL-RE.exe"
        elif system == "Linux" or system == "Darwin":
            return "./N_m3u8DL-RE"
        else:
            raise Exception(f"不支持的操作系统: {system}")
