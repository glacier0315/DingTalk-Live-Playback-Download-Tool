#!/usr/bin/env python3
"""浏览器模块异常处理测试"""
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from dingtalk_download import browser


def test_create_browser_with_unsupported_type():
    """测试创建不支持的浏览器类型"""
    with pytest.raises(RuntimeError) as exc_info:
        browser.create_browser('unsupported')
    
    assert "创建浏览器失败" in str(exc_info.value)
    assert "不支持的浏览器类型" in str(exc_info.value)


def test_create_browser_with_none_config():
    """测试当 get_browser_options 返回 None 时的情况"""
    with patch('dingtalk_download.browser.get_browser_options') as mock_get_options:
        mock_get_options.return_value = None
        
        with pytest.raises(RuntimeError) as exc_info:
            browser.create_browser('edge')
        
        assert "创建浏览器失败" in str(exc_info.value)
        assert "无法获取浏览器配置" in str(exc_info.value)


def test_create_browser_exception_handling():
    """测试创建浏览器时的异常处理"""
    with patch('dingtalk_download.browser.get_browser_options') as mock_get_options:
        mock_get_options.side_effect = Exception("模拟的异常")
        
        with pytest.raises(RuntimeError) as exc_info:
            browser.create_browser('edge')
        
        assert "创建浏览器失败" in str(exc_info.value)
        assert "模拟的异常" in str(exc_info.value)


def test_create_browser_valid_types():
    """测试创建支持的浏览器类型（不实际启动浏览器）"""
    valid_types = ['edge', 'chrome', 'firefox']
    
    for browser_type in valid_types:
        with patch('dingtalk_download.browser.webdriver') as mock_webdriver:
            mock_browser = MagicMock()
            
            if browser_type == 'edge':
                mock_webdriver.Edge.return_value = mock_browser
            elif browser_type == 'chrome':
                mock_webdriver.Chrome.return_value = mock_browser
            elif browser_type == 'firefox':
                mock_webdriver.Firefox.return_value = mock_browser
            
            result = browser.create_browser(browser_type)
            assert result is not None
            assert result == mock_browser
            
            browser.close_browser()


def test_browser_manager_class():
    """测试 BrowserManager 类的功能"""
    manager = browser.BrowserManager()
    
    assert manager.get_browser() is None
    
    with patch('dingtalk_download.browser.webdriver') as mock_webdriver:
        mock_browser = MagicMock()
        mock_webdriver.Edge.return_value = mock_browser
        
        result = manager.create_browser('edge')
        assert result == mock_browser
        assert manager.get_browser() == mock_browser
        
        manager.close_browser()
        assert manager.get_browser() is None


def test_browser_manager_exception_handling():
    """测试 BrowserManager 类的异常处理"""
    manager = browser.BrowserManager()
    
    with patch('dingtalk_download.browser.get_browser_options') as mock_get_options:
        mock_get_options.side_effect = Exception("模拟的异常")
        
        with pytest.raises(RuntimeError) as exc_info:
            manager.create_browser('edge')
        
        assert "创建浏览器失败" in str(exc_info.value)
        assert "模拟的异常" in str(exc_info.value)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
