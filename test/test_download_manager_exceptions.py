#!/usr/bin/env python3
"""下载管理器异常处理测试"""
import sys
import os
import subprocess
import tempfile
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from dingtalk_download import download_manager


def test_execute_download_with_invalid_m3u8_file():
    """测试 M3U8 文件不存在的情况"""
    with pytest.raises(FileNotFoundError) as exc_info:
        download_manager.execute_download(
            m3u8_file="nonexistent.m3u8",
            save_name="test",
            prefix="https://example.com",
            cookies_data=None,
            headers=None,
            save_dir=tempfile.gettempdir()
        )
    
    assert "M3U8 文件不存在" in str(exc_info.value)


def test_execute_download_with_empty_m3u8_file():
    """测试 M3U8 文件路径为空的情况"""
    with pytest.raises(ValueError) as exc_info:
        download_manager.execute_download(
            m3u8_file="",
            save_name="test",
            prefix="https://example.com",
            cookies_data=None,
            headers=None,
            save_dir=tempfile.gettempdir()
        )
    
    assert "M3U8 文件路径不能为空" in str(exc_info.value)


def test_execute_download_with_empty_save_name():
    """测试保存文件名为空的情况"""
    with tempfile.NamedTemporaryFile(suffix=".m3u8", delete=False) as f:
        m3u8_file = f.name
    
    try:
        with pytest.raises(ValueError) as exc_info:
            download_manager.execute_download(
                m3u8_file=m3u8_file,
                save_name="",
                prefix="https://example.com",
                cookies_data=None,
                headers=None,
                save_dir=tempfile.gettempdir()
            )
        
        assert "保存文件名不能为空" in str(exc_info.value)
    finally:
        os.unlink(m3u8_file)


def test_execute_download_with_empty_save_dir():
    """测试保存目录为空的情况"""
    with tempfile.NamedTemporaryFile(suffix=".m3u8", delete=False) as f:
        m3u8_file = f.name
    
    try:
        with pytest.raises(ValueError) as exc_info:
            download_manager.execute_download(
                m3u8_file=m3u8_file,
                save_name="test",
                prefix="https://example.com",
                cookies_data=None,
                headers=None,
                save_dir=""
            )
        
        assert "保存目录不能为空" in str(exc_info.value)
    finally:
        os.unlink(m3u8_file)


def test_execute_download_with_nonexistent_save_dir():
    """测试保存目录不存在的情况"""
    with tempfile.NamedTemporaryFile(suffix=".m3u8", delete=False) as f:
        m3u8_file = f.name
    
    try:
        with pytest.raises(FileNotFoundError) as exc_info:
            download_manager.execute_download(
                m3u8_file=m3u8_file,
                save_name="test",
                prefix="https://example.com",
                cookies_data=None,
                headers=None,
                save_dir="/nonexistent/directory"
            )
        
        assert "保存目录不存在" in str(exc_info.value)
    finally:
        os.unlink(m3u8_file)


def test_execute_download_with_readonly_save_dir():
    """测试保存目录不可写的情况"""
    with tempfile.NamedTemporaryFile(suffix=".m3u8", delete=False) as f:
        m3u8_file = f.name
    
    try:
        # 创建一个只读目录
        readonly_dir = tempfile.mkdtemp()
        
        try:
            # 在 Windows 上，我们需要移除写入权限
            if os.name == 'nt':
                import stat
                os.chmod(readonly_dir, stat.S_IREAD)
            else:
                os.chmod(readonly_dir, 0o444)
            
            # 验证目录是否真的不可写
            try:
                test_file = os.path.join(readonly_dir, "test.txt")
                with open(test_file, 'w') as f:
                    f.write("test")
                # 如果能写入，说明权限设置失败，跳过这个测试
                os.unlink(test_file)
                pytest.skip("无法设置目录为只读模式")
            except (OSError, PermissionError):
                pass
            
            with pytest.raises(PermissionError) as exc_info:
                download_manager.execute_download(
                    m3u8_file=m3u8_file,
                    save_name="test",
                    prefix="https://example.com",
                    cookies_data=None,
                    headers=None,
                    save_dir=readonly_dir
                )
            
            assert "保存目录不可写" in str(exc_info.value)
        finally:
            # 恢复权限并删除目录
            if os.name == 'nt':
                import stat
                os.chmod(readonly_dir, stat.S_IWRITE | stat.S_IREAD)
            else:
                os.chmod(readonly_dir, 0o755)
            os.rmdir(readonly_dir)
    finally:
        os.unlink(m3u8_file)


def test_execute_download_subprocess_failure():
    """测试 subprocess 执行失败的情况"""
    with tempfile.NamedTemporaryFile(suffix=".m3u8", delete=False) as f:
        m3u8_file = f.name
    
    try:
        with patch('dingtalk_download.download_manager.subprocess.run') as mock_run:
            # 创建一个模拟的 CalledProcessError
            error = subprocess.CalledProcessError(
                returncode=1,
                cmd=['test']
            )
            # 手动设置 stdout 和 stderr 属性
            error.stdout = "stdout"
            error.stderr = "stderr"
            mock_run.side_effect = error
            
            with pytest.raises(RuntimeError) as exc_info:
                download_manager.execute_download(
                    m3u8_file=m3u8_file,
                    save_name="test",
                    prefix="https://example.com",
                    cookies_data=None,
                    headers=None,
                    save_dir=tempfile.gettempdir()
                )
            
            assert "下载失败" in str(exc_info.value)
            assert "退出码: 1" in str(exc_info.value)
    finally:
        os.unlink(m3u8_file)


def test_execute_download_executable_not_found():
    """测试可执行文件不存在的情况"""
    with tempfile.NamedTemporaryFile(suffix=".m3u8", delete=False) as f:
        m3u8_file = f.name
    
    try:
        with patch('dingtalk_download.download_manager.subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError("Executable not found")
            
            with pytest.raises(RuntimeError) as exc_info:
                download_manager.execute_download(
                    m3u8_file=m3u8_file,
                    save_name="test",
                    prefix="https://example.com",
                    cookies_data=None,
                    headers=None,
                    save_dir=tempfile.gettempdir()
                )
            
            assert "找不到可执行文件" in str(exc_info.value)
    finally:
        os.unlink(m3u8_file)


def test_execute_download_success():
    """测试成功下载的情况"""
    with tempfile.NamedTemporaryFile(suffix=".m3u8", delete=False) as f:
        m3u8_file = f.name
    
    try:
        with patch('dingtalk_download.download_manager.subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "success"
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            
            result = download_manager.execute_download(
                m3u8_file=m3u8_file,
                save_name="test",
                prefix="https://example.com",
                cookies_data=None,
                headers=None,
                save_dir=tempfile.gettempdir()
            )
            
            assert result == tempfile.gettempdir()
            mock_run.assert_called_once()
    finally:
        os.unlink(m3u8_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
