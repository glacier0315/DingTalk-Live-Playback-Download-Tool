"""浏览器配置测试模块"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dingtalk_download.browser import get_browser_options


class TestGetBrowserOptions:
    """测试get_browser_options函数"""
    
    def test_edge_options_configured(self):
        """测试Edge浏览器选项配置"""
        result = get_browser_options('edge')
        assert result is not None
        assert isinstance(result, dict)
    
    def test_chrome_options_configured(self):
        """测试Chrome浏览器选项配置"""
        result = get_browser_options('chrome')
        assert result is not None
        assert isinstance(result, dict)
    
    def test_firefox_options_configured(self):
        """测试Firefox浏览器选项配置"""
        result = get_browser_options('firefox')
        assert result is not None
        assert isinstance(result, dict)
    
    def test_invalid_browser_raises_error(self):
        """测试无效浏览器类型抛出错误"""
        with pytest.raises(ValueError):
            get_browser_options('invalid_browser')
