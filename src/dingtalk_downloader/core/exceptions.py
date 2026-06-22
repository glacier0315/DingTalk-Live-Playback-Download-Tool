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


class M3u8ParseError(DownloadError):
    """m3u8解析异常"""

    pass


class FileReaderError(Exception):
    """文件读取异常"""

    pass


class BrowserError(Exception):
    """浏览器操作异常"""

    pass


class NetworkError(DownloadError):
    """网络请求异常"""

    pass


class ValidationError(Exception):
    """输入验证异常"""

    pass


# --- New: retry pipeline exception hierarchy (2026-06-20 spec) ---


class RecoverableDownloadError(DownloadError):
    """可重试的下载错误基类。"""

    pass


class AuthKeyExpiredError(RecoverableDownloadError):
    """m3u8 auth_key 过期（403/Forbidden/401）。"""

    pass


class NetworkTransientError(RecoverableDownloadError):
    """瞬时网络问题（连接重置、DNS、5xx）。"""

    pass


class ProcessSpawnError(RecoverableDownloadError):
    """N_m3u8DL-RE 启动失败（资源占用、路径错）。"""

    pass


class M3u8RefreshError(RecoverableDownloadError):
    """拉取新 m3u8 失败（页面未加载、liveUuid 提取失败）。"""

    pass


class DownloadFatalError(DownloadError):
    """不可恢复：磁盘满、权限拒绝、保存路径无效。"""

    pass
