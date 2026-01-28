"""
钉钉直播回放下载工具 - 异常模块

本模块定义项目中使用的所有自定义异常。

作者：项目团队
依赖：无
创建日期：2026-01-26
修改历史：
    - 2026-01-26: 初始版本，统一异常定义
    - 2026-01-28: 添加更具体的异常类型
"""


class DownloadError(Exception):
    """下载异常"""

    pass


class CookieError(Exception):
    """Cookie处理异常"""

    pass


class M3u8ParseError(Exception):
    """m3u8解析异常"""

    pass


class FileReaderError(Exception):
    """文件读取异常"""

    pass


class ConfigLoadError(Exception):
    """配置文件加载异常"""

    pass


class ConfigValidationError(Exception):
    """配置文件验证异常"""

    pass


class BrowserError(Exception):
    """浏览器操作异常"""

    pass


class NetworkError(Exception):
    """网络请求异常"""

    pass


class ValidationError(Exception):
    """输入验证异常"""

    pass
