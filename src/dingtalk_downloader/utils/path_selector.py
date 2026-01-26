"""
钉钉直播回放下载工具 - 路径选择器模块

本模块负责根据保存模式选择下载路径。

作者：项目团队
依赖：tkinter, os, logging
创建日期：2026-01-26
修改历史：
    - 2026-01-26: 初始版本，从Downloader类中提取路径选择逻辑
"""

import os
import tkinter as tk
from tkinter import filedialog
from typing import Optional
import logging
from ..config.yaml_config import YamlConfig
from ..utils.path_helper import ensure_dir_exists
from ..config.constants import SAVE_MODE_DEFAULT, SAVE_MODE_MANUAL

logger = logging.getLogger(__name__)


class PathSelector:
    """
    路径选择器类。

    根据保存模式选择下载路径，支持默认路径和手动选择路径。

    Attributes:
        save_mode: 保存模式（1：默认路径，2：手动选择）
        saved_path: 已选择的保存路径
    """

    def __init__(self, save_mode: str):
        """
        初始化路径选择器。

        Args:
            save_mode: 保存模式（1：默认路径，2：手动选择）
        """
        self.save_mode = save_mode
        self.saved_path = None
        logger.debug(f"路径选择器初始化 - 保存模式: {save_mode}")

    def get_save_dir(self) -> Optional[str]:
        """
        获取保存目录。

        根据保存模式选择保存目录。

        Returns:
            保存目录路径，如果用户取消则返回None
        """
        if self.save_mode == SAVE_MODE_DEFAULT:
            save_dir = self._get_default_download_dir()
            logger.debug(f"使用默认保存目录: {save_dir}")
        elif self.save_mode == SAVE_MODE_MANUAL:
            save_dir = self._get_manual_download_dir()
            logger.debug(f"使用手动选择目录: {save_dir}")
        else:
            logger.error(f"无效的保存模式: {self.save_mode}")
            return None

        if not save_dir:
            logger.warning("用户取消了目录选择")
            print("用户取消了选择。视频下载已中止。")
            return None

        self.saved_path = save_dir
        return save_dir

    def _get_default_download_dir(self) -> str:
        """
        获取默认下载目录。

        从配置文件中读取default_dir配置项作为下载目录。
        如果配置文件不存在或配置项缺失，则使用默认值"Downloads"。

        Returns:
            默认下载目录路径
        """
        try:
            config = YamlConfig.get_instance()
            default_dir = config.get_str("download.default_dir", "Downloads")

            if os.path.isabs(default_dir):
                downloads_dir = default_dir
            else:
                base_dir = os.getcwd()
                downloads_dir = os.path.join(base_dir, default_dir)

            ensure_dir_exists(downloads_dir)
            logger.debug(f"默认下载目录: {downloads_dir}")
            return downloads_dir

        except Exception as e:
            logger.warning(f"从配置文件读取默认下载目录失败，使用默认值: {e}")
            base_dir = os.getcwd()
            downloads_dir = os.path.join(base_dir, "Downloads")
            ensure_dir_exists(downloads_dir)
            logger.debug(f"默认下载目录: {downloads_dir}")
            return downloads_dir

    def _get_manual_download_dir(self) -> Optional[str]:
        """
        获取手动选择的下载目录。

        弹出文件选择对话框，让用户选择保存目录。

        Returns:
            用户选择的目录路径，如果用户取消则返回None
        """
        root = tk.Tk()
        root.withdraw()
        save_dir = filedialog.askdirectory(title="选择保存视频的目录")
        root.destroy()
        logger.debug(f"用户选择的目录: {save_dir}")
        return save_dir

    def get_saved_path(self) -> Optional[str]:
        """
        获取已保存的路径。

        Returns:
            已保存的路径，如果未保存则返回None
        """
        return self.saved_path
