"""
钉钉直播回放下载工具 - M3U8文件管理集成测试

本模块测试M3U8文件管理在实际下载流程中的集成效果。

作者：项目团队
依赖：pytest, tempfile, os
创建日期：2026-01-22
"""

import pytest
import os
import tempfile
from dingtalk_downloader.utils.m3u8_file_manager import M3u8FileManager


class TestM3u8FileManagerIntegration:
    """测试M3U8文件管理器集成场景"""

    def test_config_change_affects_temp_dir(self):
        """测试配置文件修改影响临时目录"""
        with tempfile.TemporaryDirectory() as temp_dir1:
            temp_dir1_normalized = temp_dir1.replace("\\", "/")
            config_content1 = f"""
download:
  temp_dir: "{temp_dir1_normalized}"
"""
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                config_path = f.name
                f.write(config_content1)
            
            try:
                manager1 = M3u8FileManager(config_path)
                original_temp_dir = manager1.get_temp_dir()
                
                # 修改配置文件
                with tempfile.TemporaryDirectory() as temp_dir2:
                    temp_dir2_normalized = temp_dir2.replace("\\", "/")
                    config_content2 = f"""
download:
  temp_dir: "{temp_dir2_normalized}"
"""
                    with open(config_path, 'w') as f:
                        f.write(config_content2)
                    
                    # 重新加载配置
                    manager1.reload_config()
                    new_temp_dir = manager1.get_temp_dir()
                    
                    # 验证临时目录已更改
                    assert new_temp_dir != original_temp_dir
                    assert os.path.normpath(temp_dir2) in os.path.normpath(new_temp_dir)
            finally:
                os.unlink(config_path)

    def test_dynamic_filename_in_download_flow(self):
        """测试动态文件名在下载流程中的唯一性"""
        manager = M3u8FileManager()
        
        # 模拟多次下载场景
        filenames = []
        for i in range(10):
            filename = manager.generate_filename(prefix=f"download_{i}")
            filenames.append(filename)
        
        # 验证所有文件名都是唯一的
        assert len(filenames) == len(set(filenames))
        
        # 验证所有文件名都包含前缀
        for filename in filenames:
            assert filename.startswith("download_")
            assert filename.endswith(".m3u8")

    def test_temp_dir_auto_creation(self):
        """测试临时目录自动创建"""
        with tempfile.TemporaryDirectory() as base_dir:
            new_temp_dir = os.path.join(base_dir, "new_temp", "nested", "dir")
            config_content = f"""
download:
  temp_dir: "{new_temp_dir.replace(chr(92), '/')}"
"""
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                config_path = f.name
                f.write(config_content)
            
            try:
                manager = M3u8FileManager(config_path)
                
                # 验证目录已自动创建
                assert os.path.exists(manager.temp_dir)
                assert os.path.isdir(manager.temp_dir)
                
                # 验证路径正确
                assert os.path.normpath(new_temp_dir) == os.path.normpath(manager.temp_dir)
            finally:
                os.unlink(config_path)

    def test_file_cleanup_after_download(self):
        """测试下载后文件清理"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_normalized = temp_dir.replace("\\", "/")
            config_content = f"""
download:
  temp_dir: "{temp_dir_normalized}"
"""
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                config_path = f.name
                f.write(config_content)
            
            try:
                manager = M3u8FileManager(config_path)
                
                # 创建一些临时文件
                for i in range(5):
                    file_path = manager.get_temp_file_path()
                    with open(file_path, 'w') as f:
                        f.write("#EXTM3U")
                
                # 验证文件已创建
                files_before = os.listdir(manager.temp_dir)
                assert len(files_before) == 5
                
                # 清理文件
                cleaned_count = manager.clean_temp_files()
                
                # 验证文件已清理
                files_after = os.listdir(manager.temp_dir)
                assert len(files_after) == 0
                assert cleaned_count == 5
            finally:
                os.unlink(config_path)

    def test_path_validation_in_real_scenario(self):
        """测试路径验证在实际场景中的效果"""
        manager = M3u8FileManager()
        
        # 测试有效路径
        valid_path = manager.get_temp_file_path()
        assert manager.validate_path(valid_path) is True
        
        # 测试无效路径
        invalid_path = "/nonexistent/directory/file.m3u8"
        assert manager.validate_path(invalid_path) is False

    def test_relative_vs_absolute_path(self):
        """测试相对路径和绝对路径的处理"""
        # 测试相对路径
        config_relative = """
download:
  temp_dir: "temp_relative"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
            f.write(config_relative)
        
        try:
            manager_relative = M3u8FileManager(config_path)
            temp_dir_relative = manager_relative.get_temp_dir()
            
            # 验证相对路径被转换为绝对路径
            assert os.path.isabs(temp_dir_relative)
            assert "temp_relative" in temp_dir_relative
        finally:
            os.unlink(config_path)
        
        # 测试绝对路径
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_normalized = temp_dir.replace("\\", "/")
            config_absolute = f"""
download:
  temp_dir: "{temp_dir_normalized}"
"""
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                config_path = f.name
                f.write(config_absolute)
            
            try:
                manager_absolute = M3u8FileManager(config_path)
                temp_dir_absolute = manager_absolute.get_temp_dir()
                
                # 验证绝对路径保持不变
                assert os.path.normpath(temp_dir) == os.path.normpath(temp_dir_absolute)
            finally:
                os.unlink(config_path)

    def test_multiple_managers_with_different_configs(self):
        """测试多个管理器使用不同配置"""
        with tempfile.TemporaryDirectory() as temp_dir1:
            with tempfile.TemporaryDirectory() as temp_dir2:
                config1_content = f"""
download:
  temp_dir: "{temp_dir1.replace(chr(92), '/')}"
"""
                config2_content = f"""
download:
  temp_dir: "{temp_dir2.replace(chr(92), '/')}"
"""
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                    config_path1 = f.name
                    f.write(config1_content)
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                    config_path2 = f.name
                    f.write(config2_content)
                
                try:
                    manager1 = M3u8FileManager(config_path1)
                    manager2 = M3u8FileManager(config_path2)
                    
                    # 验证两个管理器使用不同的临时目录
                    assert os.path.normpath(manager1.get_temp_dir()) != os.path.normpath(manager2.get_temp_dir())
                    
                    # 验证各自的文件名生成
                    filename1 = manager1.generate_filename(prefix="manager1")
                    filename2 = manager2.generate_filename(prefix="manager2")
                    
                    assert filename1 != filename2
                    assert filename1.startswith("manager1_")
                    assert filename2.startswith("manager2_")
                finally:
                    os.unlink(config_path1)
                    os.unlink(config_path2)

    def test_file_info_in_download_context(self):
        """测试文件信息在下载上下文中的使用"""
        manager = M3u8FileManager()
        
        # 创建一个测试文件
        file_path = manager.get_temp_file_path()
        with open(file_path, 'w') as f:
            f.write("#EXTM3U\n#EXT-X-VERSION:3\n")
        
        try:
            # 获取文件信息
            info = manager.get_file_info(file_path)
            
            # 验证文件信息
            assert info["exists"] is True
            assert info["is_file"] is True
            assert info["is_dir"] is False
            assert info["size"] > 0
            
            # 验证路径正确
            assert info["path"] == file_path
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)