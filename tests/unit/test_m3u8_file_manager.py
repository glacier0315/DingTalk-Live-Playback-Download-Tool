"""
钉钉直播回放下载工具 - M3u8FileManager单元测试

本模块测试M3u8FileManager的各项功能。

作者：项目团队
依赖：pytest, unittest.mock, tempfile, os
创建日期：2026-01-22
"""

import pytest
import os
import tempfile
import uuid
from unittest.mock import patch, MagicMock
from dingtalk_downloader.utils.m3u8_file_manager import M3u8FileManager


class TestM3u8FileManagerInit:
    """测试M3u8FileManager初始化"""

    def test_init_default_path(self):
        """测试使用默认配置文件路径初始化"""
        manager = M3u8FileManager()
        assert manager.config is not None
        assert manager.temp_dir is not None
        assert os.path.isabs(manager.temp_dir)

    def test_init_custom_path(self):
        """测试使用自定义配置文件路径初始化"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
            f.write("""
download:
  temp_dir: "custom_temp"
""")
        
        try:
            manager = M3u8FileManager(config_path)
            assert manager.config.config_file == config_path
            assert "custom_temp" in manager.temp_dir
        finally:
            os.unlink(config_path)

    def test_init_creates_temp_dir(self):
        """测试初始化时自动创建临时目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_content = f"""
download:
  temp_dir: "{temp_dir}"
"""
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                config_path = f.name
                f.write(config_content)
            
            try:
                manager = M3u8FileManager(config_path)
                assert os.path.exists(manager.temp_dir)
                assert os.path.isdir(manager.temp_dir)
            finally:
                os.unlink(config_path)


class TestM3u8FileManagerResolveTempDir:
    """测试临时目录路径解析"""

    def test_resolve_temp_dir_absolute_path(self):
        """测试解析绝对路径"""
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
                assert os.path.normpath(manager.temp_dir) == os.path.normpath(temp_dir)
            finally:
                os.unlink(config_path)

    def test_resolve_temp_dir_relative_path(self):
        """测试解析相对路径"""
        config_content = """
download:
  temp_dir: "temp"
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
            f.write(config_content)
        
        try:
            manager = M3u8FileManager(config_path)
            expected_path = os.path.join(os.getcwd(), "temp")
            assert manager.temp_dir == expected_path
        finally:
            os.unlink(config_path)


class TestM3u8FileManagerGenerateFilename:
    """测试动态文件名生成"""

    def test_generate_filename_without_prefix(self):
        """测试生成不带前缀的文件名"""
        manager = M3u8FileManager()
        filename = manager.generate_filename()
        
        assert filename.endswith(".m3u8")
        assert len(filename) == 41  # UUID格式: 36字符 + .m3u8 = 41字符

    def test_generate_filename_with_prefix(self):
        """测试生成带前缀的文件名"""
        manager = M3u8FileManager()
        filename = manager.generate_filename(prefix="test")
        
        assert filename.startswith("test_")
        assert filename.endswith(".m3u8")
        assert len(filename) == 46  # "test_" + UUID + ".m3u8" = 5 + 36 + 5 = 46字符

    def test_generate_filename_uniqueness(self):
        """测试生成文件名的唯一性"""
        manager = M3u8FileManager()
        filenames = [manager.generate_filename() for _ in range(100)]
        
        assert len(filenames) == len(set(filenames))

    def test_generate_filename_valid_uuid(self):
        """测试生成的文件名包含有效的UUID"""
        manager = M3u8FileManager()
        filename = manager.generate_filename()
        
        uuid_str = filename.replace(".m3u8", "")
        try:
            uuid.UUID(uuid_str)
        except ValueError:
            pytest.fail("生成的文件名不包含有效的UUID")


class TestM3u8FileManagerGetTempFilePath:
    """测试获取临时文件路径"""

    def test_get_temp_file_path_with_filename(self):
        """测试使用指定文件名获取路径"""
        manager = M3u8FileManager()
        filename = "test.m3u8"
        file_path = manager.get_temp_file_path(filename)
        
        assert file_path.endswith(filename)
        assert manager.temp_dir in file_path

    def test_get_temp_file_path_without_filename(self):
        """测试自动生成文件名获取路径"""
        manager = M3u8FileManager()
        file_path = manager.get_temp_file_path()
        
        assert file_path.endswith(".m3u8")
        assert manager.temp_dir in file_path
        assert len(file_path) > len(manager.temp_dir)

    def test_get_temp_file_path_consistency(self):
        """测试多次调用生成的文件名不同"""
        manager = M3u8FileManager()
        path1 = manager.get_temp_file_path()
        path2 = manager.get_temp_file_path()
        
        assert path1 != path2


class TestM3u8FileManagerValidatePath:
    """测试路径验证"""

    def test_validate_path_valid(self):
        """测试验证有效路径"""
        manager = M3u8FileManager()
        with tempfile.NamedTemporaryFile(delete=False) as f:
            valid_path = f.name
        
        try:
            result = manager.validate_path(valid_path)
            assert result is True
        finally:
            os.unlink(valid_path)

    def test_validate_path_invalid_none(self):
        """测试验证None路径"""
        manager = M3u8FileManager()
        result = manager.validate_path(None)
        assert result is False

    def test_validate_path_invalid_empty(self):
        """测试验证空字符串路径"""
        manager = M3u8FileManager()
        result = manager.validate_path("")
        assert result is False

    def test_validate_path_invalid_type(self):
        """测试验证非字符串路径"""
        manager = M3u8FileManager()
        result = manager.validate_path(123)
        assert result is False

    def test_validate_path_nonexistent_parent(self):
        """测试验证不存在的父目录路径"""
        manager = M3u8FileManager()
        invalid_path = "/nonexistent/directory/file.m3u8"
        result = manager.validate_path(invalid_path)
        assert result is False


class TestM3u8FileManagerEnsurePathExists:
    """测试确保路径存在"""

    def test_ensure_path_exists_existing_dir(self):
        """测试确保已存在的目录"""
        manager = M3u8FileManager()
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test.m3u8")
            result = manager.ensure_path_exists(file_path)
            assert result is True

    def test_ensure_path_exists_create_dir(self):
        """测试创建不存在的目录"""
        manager = M3u8FileManager()
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = os.path.join(temp_dir, "new_dir")
            file_path = os.path.join(new_dir, "test.m3u8")
            
            result = manager.ensure_path_exists(file_path)
            assert result is True
            assert os.path.exists(new_dir)
            assert os.path.isdir(new_dir)


class TestM3u8FileManagerCleanTempFiles:
    """测试清理临时文件"""

    def test_clean_temp_files_all(self):
        """测试清理所有.m3u8文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = temp_dir.replace("\\", "/")
            config_content = f"""
download:
  temp_dir: "{temp_dir}"
"""
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                config_path = f.name
                f.write(config_content)
            
            try:
                manager = M3u8FileManager(config_path)
                
                # 创建测试文件
                for i in range(5):
                    file_path = os.path.join(manager.temp_dir, f"test_{i}.m3u8")
                    with open(file_path, 'w') as f:
                        f.write("#EXTM3U")
                
                # 创建非.m3u8文件
                other_file = os.path.join(manager.temp_dir, "other.txt")
                with open(other_file, 'w') as f:
                    f.write("test")
                
                cleaned_count = manager.clean_temp_files()
                
                assert cleaned_count == 5
                assert not os.path.exists(os.path.join(manager.temp_dir, "test_0.m3u8"))
                assert os.path.exists(other_file)
            finally:
                os.unlink(config_path)

    def test_clean_temp_files_with_pattern(self):
        """测试使用模式清理文件"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = temp_dir.replace("\\", "/")
            config_content = f"""
download:
  temp_dir: "{temp_dir}"
"""
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                config_path = f.name
                f.write(config_content)
            
            try:
                manager = M3u8FileManager(config_path)
                
                # 创建测试文件
                for i in range(3):
                    file_path = os.path.join(manager.temp_dir, f"test_{i}.m3u8")
                    with open(file_path, 'w') as f:
                        f.write("#EXTM3U")
                
                for i in range(2):
                    file_path = os.path.join(manager.temp_dir, f"other_{i}.m3u8")
                    with open(file_path, 'w') as f:
                        f.write("#EXTM3U")
                
                cleaned_count = manager.clean_temp_files(pattern="test")
                
                assert cleaned_count == 3
                assert not os.path.exists(os.path.join(manager.temp_dir, "test_0.m3u8"))
                assert os.path.exists(os.path.join(manager.temp_dir, "other_0.m3u8"))
            finally:
                os.unlink(config_path)

    def test_clean_temp_files_nonexistent_dir(self):
        """测试清理不存在的目录"""
        manager = M3u8FileManager()
        manager.temp_dir = "/nonexistent/directory"
        cleaned_count = manager.clean_temp_files()
        assert cleaned_count == 0


class TestM3u8FileManagerGetTempDir:
    """测试获取临时目录"""

    def test_get_temp_dir(self):
        """测试获取临时目录路径"""
        manager = M3u8FileManager()
        temp_dir = manager.get_temp_dir()
        
        assert temp_dir is not None
        assert isinstance(temp_dir, str)
        assert os.path.isabs(temp_dir)


class TestM3u8FileManagerSetTempDir:
    """测试设置临时目录"""

    def test_set_temp_dir_absolute(self):
        """测试设置绝对路径"""
        manager = M3u8FileManager()
        with tempfile.TemporaryDirectory() as temp_dir:
            manager.set_temp_dir(temp_dir)
            assert manager.temp_dir == temp_dir

    def test_set_temp_dir_relative(self):
        """测试设置相对路径"""
        manager = M3u8FileManager()
        manager.set_temp_dir("new_temp")
        
        expected_path = os.path.join(os.getcwd(), "new_temp")
        assert manager.temp_dir == expected_path


class TestM3u8FileManagerGetFileInfo:
    """测试获取文件信息"""

    def test_get_file_info_existing_file(self):
        """测试获取已存在文件的信息"""
        manager = M3u8FileManager()
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content")
            file_path = f.name
        
        try:
            info = manager.get_file_info(file_path)
            
            assert info["path"] == file_path
            assert info["exists"] is True
            assert info["size"] > 0
            assert info["is_file"] is True
            assert info["is_dir"] is False
        finally:
            os.unlink(file_path)

    def test_get_file_info_nonexistent_file(self):
        """测试获取不存在文件的信息"""
        manager = M3u8FileManager()
        info = manager.get_file_info("/nonexistent/file.m3u8")
        
        assert info["path"] == "/nonexistent/file.m3u8"
        assert info["exists"] is False
        assert info["size"] == 0
        assert info["is_file"] is False
        assert info["is_dir"] is False

    def test_get_file_info_directory(self):
        """测试获取目录的信息"""
        manager = M3u8FileManager()
        with tempfile.TemporaryDirectory() as temp_dir:
            info = manager.get_file_info(temp_dir)
            
            assert info["path"] == temp_dir
            assert info["exists"] is True
            assert info["is_file"] is False
            assert info["is_dir"] is True


class TestM3u8FileManagerReloadConfig:
    """测试重新加载配置"""

    def test_reload_config(self):
        """测试重新加载配置"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
            f.write("""
download:
  temp_dir: "temp"
""")
        
        try:
            manager = M3u8FileManager(config_path)
            original_temp_dir = manager.temp_dir
            
            # 修改配置文件
            with open(config_path, 'w') as f:
                f.write("""
download:
  temp_dir: "new_temp"
""")
            
            manager.reload_config()
            
            assert manager.temp_dir != original_temp_dir
            assert "new_temp" in manager.temp_dir
        finally:
            os.unlink(config_path)


class TestM3u8FileManagerEdgeCases:
    """测试边界情况"""

    def test_generate_filename_special_prefix(self):
        """测试使用特殊字符前缀生成文件名"""
        manager = M3u8FileManager()
        filename = manager.generate_filename(prefix="测试_123")
        
        assert filename.startswith("测试_123_")
        assert filename.endswith(".m3u8")

    def test_validate_path_with_spaces(self):
        """测试验证包含空格的路径"""
        manager = M3u8FileManager()
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "file with spaces.m3u8")
            with open(file_path, 'w') as f:
                f.write("#EXTM3U")
            
            result = manager.validate_path(file_path)
            assert result is True

    def test_ensure_path_exists_nested_dirs(self):
        """测试创建嵌套目录"""
        manager = M3u8FileManager()
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = os.path.join(temp_dir, "level1", "level2", "level3", "file.m3u8")
            
            result = manager.ensure_path_exists(nested_path)
            assert result is True
            assert os.path.exists(os.path.join(temp_dir, "level1", "level2", "level3"))