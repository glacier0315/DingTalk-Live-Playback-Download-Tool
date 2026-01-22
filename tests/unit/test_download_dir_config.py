"""
钉钉直播回放下载工具 - 下载目录配置单元测试

本模块测试下载目录配置的各项功能。

作者：项目团队
依赖：pytest, tempfile, os
创建日期：2026-01-22
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from dingtalk_downloader.core.downloader import Downloader


class TestDownloadDirConfiguration:
    """测试下载目录配置功能"""

    def test_read_default_dir_from_config(self):
        """测试从配置文件读取default_dir配置项"""
        with patch('dingtalk_downloader.config.yaml_config.YamlConfig') as mock_yaml_config:
            mock_config_instance = MagicMock()
            mock_config_instance.get.return_value = "custom_downloads"
            mock_yaml_config.return_value = mock_config_instance
            
            downloader = Downloader(browser_type="edge", save_mode="1")
            default_dir = downloader._get_default_download_dir()
            
            assert "custom_downloads" in default_dir
            assert os.path.isabs(default_dir)

    def test_default_dir_missing_in_config(self):
        """测试配置文件缺失default_dir配置时使用默认值"""
        with patch('dingtalk_downloader.config.yaml_config.YamlConfig') as mock_yaml_config:
            mock_config_instance = MagicMock()
            mock_config_instance.get.return_value = "Downloads"
            mock_yaml_config.return_value = mock_config_instance
            
            downloader = Downloader(browser_type="edge", save_mode="1")
            default_dir = downloader._get_default_download_dir()
            
            assert "Downloads" in default_dir
            assert os.path.isabs(default_dir)

    def test_default_dir_absolute_path(self):
        """测试配置文件中使用绝对路径"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('dingtalk_downloader.config.yaml_config.YamlConfig') as mock_yaml_config:
                mock_config_instance = MagicMock()
                mock_config_instance.get.return_value = temp_dir
                mock_yaml_config.return_value = mock_config_instance
                
                downloader = Downloader(browser_type="edge", save_mode="1")
                default_dir = downloader._get_default_download_dir()
                
                assert os.path.normpath(temp_dir) == os.path.normpath(default_dir)

    def test_default_dir_relative_path(self):
        """测试配置文件中使用相对路径"""
        with patch('dingtalk_downloader.config.yaml_config.YamlConfig') as mock_yaml_config:
            mock_config_instance = MagicMock()
            mock_config_instance.get.return_value = "custom_downloads"
            mock_yaml_config.return_value = mock_config_instance
            
            downloader = Downloader(browser_type="edge", save_mode="1")
            default_dir = downloader._get_default_download_dir()
            
            assert os.path.isabs(default_dir)
            assert "custom_downloads" in default_dir

    def test_malformed_yaml_config(self):
        """测试配置文件格式错误时的异常处理"""
        with patch('dingtalk_downloader.config.yaml_config.YamlConfig') as mock_yaml_config:
            mock_config_instance = MagicMock()
            mock_config_instance.get.side_effect = Exception("YAML parse error")
            mock_yaml_config.return_value = mock_config_instance
            
            downloader = Downloader(browser_type="edge", save_mode="1")
            default_dir = downloader._get_default_download_dir()
            
            assert default_dir is not None
            assert "Downloads" in default_dir

    def test_empty_default_dir_config(self):
        """测试配置文件中default_dir为空字符串"""
        with patch('dingtalk_downloader.config.yaml_config.YamlConfig') as mock_yaml_config:
            mock_config_instance = MagicMock()
            mock_config_instance.get.return_value = ""
            mock_yaml_config.return_value = mock_config_instance
            
            downloader = Downloader(browser_type="edge", save_mode="1")
            default_dir = downloader._get_default_download_dir()
            
            assert default_dir is not None

    def test_nonexistent_config_file(self):
        """测试配置文件不存在时的处理"""
        with patch('dingtalk_downloader.config.yaml_config.YamlConfig') as mock_yaml_config:
            mock_config_instance = MagicMock()
            mock_config_instance.get.side_effect = FileNotFoundError("Config file not found")
            mock_yaml_config.return_value = mock_config_instance
            
            downloader = Downloader(browser_type="edge", save_mode="1")
            default_dir = downloader._get_default_download_dir()
            
            assert default_dir is not None
            assert "Downloads" in default_dir

    def test_default_dir_auto_creation(self):
        """测试默认下载目录自动创建"""
        with tempfile.TemporaryDirectory() as base_dir:
            new_dir = os.path.join(base_dir, "new_downloads")
            
            with patch('dingtalk_downloader.config.yaml_config.YamlConfig') as mock_yaml_config:
                mock_config_instance = MagicMock()
                mock_config_instance.get.return_value = new_dir
                mock_yaml_config.return_value = mock_config_instance
                
                downloader = Downloader(browser_type="edge", save_mode="1")
                default_dir = downloader._get_default_download_dir()
                
                assert os.path.exists(default_dir)
                assert os.path.isdir(default_dir)

    def test_default_dir_with_special_characters(self):
        """测试默认下载目录包含特殊字符"""
        with tempfile.TemporaryDirectory() as base_dir:
            special_dir = os.path.join(base_dir, "downloads with spaces & special!@#")
            os.makedirs(special_dir)
            
            with patch('dingtalk_downloader.config.yaml_config.YamlConfig') as mock_yaml_config:
                mock_config_instance = MagicMock()
                mock_config_instance.get.return_value = special_dir
                mock_yaml_config.return_value = mock_config_instance
                
                downloader = Downloader(browser_type="edge", save_mode="1")
                default_dir = downloader._get_default_download_dir()
                
                assert os.path.normpath(special_dir) == os.path.normpath(default_dir)

    def test_default_dir_with_unicode(self):
        """测试默认下载目录包含Unicode字符"""
        with tempfile.TemporaryDirectory() as base_dir:
            unicode_dir = os.path.join(base_dir, "下载_测试_中文")
            os.makedirs(unicode_dir)
            
            with patch('dingtalk_downloader.config.yaml_config.YamlConfig') as mock_yaml_config:
                mock_config_instance = MagicMock()
                mock_config_instance.get.return_value = unicode_dir
                mock_yaml_config.return_value = mock_config_instance
                
                downloader = Downloader(browser_type="edge", save_mode="1")
                default_dir = downloader._get_default_download_dir()
                
                assert os.path.normpath(unicode_dir) == os.path.normpath(default_dir)

    def test_default_dir_nested_path(self):
        """测试默认下载目录为嵌套路径"""
        with tempfile.TemporaryDirectory() as base_dir:
            nested_dir = os.path.join(base_dir, "level1", "level2", "level3", "downloads")
            
            with patch('dingtalk_downloader.config.yaml_config.YamlConfig') as mock_yaml_config:
                mock_config_instance = MagicMock()
                mock_config_instance.get.return_value = nested_dir
                mock_yaml_config.return_value = mock_config_instance
                
                downloader = Downloader(browser_type="edge", save_mode="1")
                default_dir = downloader._get_default_download_dir()
                
                assert os.path.normpath(nested_dir) == os.path.normpath(default_dir)
                assert os.path.exists(default_dir)

    def test_default_dir_cross_platform(self):
        """测试跨平台路径兼容性"""
        with patch('dingtalk_downloader.config.yaml_config.YamlConfig') as mock_yaml_config:
            mock_config_instance = MagicMock()
            mock_config_instance.get.return_value = "Downloads"
            mock_yaml_config.return_value = mock_config_instance
            
            downloader = Downloader(browser_type="edge", save_mode="1")
            default_dir = downloader._get_default_download_dir()
            
            assert os.path.isabs(default_dir)
            assert "Downloads" in default_dir