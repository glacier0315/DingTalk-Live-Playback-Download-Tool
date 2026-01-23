"""
钉钉直播回放下载工具 - 二进制程序调用模块

本模块包含 N_m3u8DL-RE 工具的调用封装。

作者：项目团队
依赖：subprocess, platform
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
"""

from .n_m3u8dl_re import NM3u8DLRE

__all__ = ["NM3u8DLRE"]
