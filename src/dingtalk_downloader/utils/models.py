"""
钉钉直播回放下载工具 - 数据模型模块

本模块定义值对象和数据类，用于封装复杂概念。

作者：项目团队
依赖：dataclasses, typing
创建日期：2026-01-26
修改历史：
    - 2026-01-26: 初始版本，创建值对象和数据类
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class CookieData:
    """
    Cookie数据值对象。

    封装Cookie数据，提供类型安全和不可变性。

    Attributes:
        cookies: Cookie字典，格式为{cookie_name: cookie_value}

    Example:
        >>> cookie_data = CookieData({"session": "abc123"})
        >>> cookie_data.cookies
        {'session': 'abc123'}
    """

    cookies: Dict[str, str]

    def __post_init__(self):
        """验证Cookie数据。"""
        if not isinstance(self.cookies, dict):
            raise ValueError("cookies必须是字典类型")

        for key, value in self.cookies.items():
            if not isinstance(key, str):
                raise ValueError("Cookie键必须是字符串类型")
            if not isinstance(value, str):
                raise ValueError("Cookie值必须是字符串类型")

    def to_dict(self) -> Dict[str, str]:
        """
        转换为字典。

        Returns:
            Cookie字典
        """
        return self.cookies.copy()

    def get(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        获取指定Cookie值。

        Args:
            name: Cookie名称
            default: 默认值

        Returns:
            Cookie值，如果不存在则返回默认值
        """
        return self.cookies.get(name, default)

    def __len__(self) -> int:
        """返回Cookie数量。"""
        return len(self.cookies)

    def __contains__(self, key: str) -> bool:
        """
        检查是否包含指定的Cookie。

        Args:
            key: Cookie名称

        Returns:
            如果包含则返回True
        """
        return key in self.cookies


@dataclass(frozen=True)
class HeadersData:
    """
    请求头数据值对象。

    封装HTTP请求头数据，提供类型安全和不可变性。

    Attributes:
        headers: 请求头字典，包含User-Agent、Referer等

    Example:
        >>> headers_data = HeadersData({"User-Agent": "Mozilla/5.0"})
        >>> headers_data.headers
        {'User-Agent': 'Mozilla/5.0'}
    """

    headers: Dict[str, str]

    def __post_init__(self):
        """验证请求头数据。"""
        if not isinstance(self.headers, dict):
            raise ValueError("headers必须是字典类型")

        for key, value in self.headers.items():
            if not isinstance(key, str):
                raise ValueError("请求头键必须是字符串类型")
            if not isinstance(value, str):
                raise ValueError("请求头值必须是字符串类型")

    def to_dict(self) -> Dict[str, str]:
        """
        转换为字典。

        Returns:
            请求头字典
        """
        return self.headers.copy()

    def get(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        获取指定请求头值。

        Args:
            name: 请求头名称
            default: 默认值

        Returns:
            请求头值，如果不存在则返回默认值
        """
        return self.headers.get(name, default)

    def __len__(self) -> int:
        """返回请求头数量。"""
        return len(self.headers)

    def __contains__(self, key: str) -> bool:
        """
        检查是否包含指定的请求头。

        Args:
            key: 请求头名称

        Returns:
            如果包含则返回True
        """
        return key in self.headers


@dataclass(frozen=True)
class M3u8Link:
    """
    m3u8链接值对象。

    封装m3u8链接和相关信息，提供类型安全和不可变性。

    Attributes:
        url: m3u8文件URL
        prefix: 基础URL
        local_file_path: 本地m3u8文件路径

    Example:
        >>> m3u8_link = M3u8Link(
        ...     "https://example.com/live/video.m3u8",
        ...     "https://example.com/live/",
        ...     "/path/to/local/video.m3u8"
        ... )
        >>> m3u8_link.url
        'https://example.com/live/video.m3u8'
    """

    url: str
    prefix: str
    local_file_path: Optional[str] = None

    def __post_init__(self):
        """验证m3u8链接数据。"""
        if not isinstance(self.url, str):
            raise ValueError("url必须是字符串类型")
        if not isinstance(self.prefix, str):
            raise ValueError("prefix必须是字符串类型")

        if not self.url:
            raise ValueError("url不能为空")
        if not self.prefix:
            raise ValueError("prefix不能为空")

        if not self.url.startswith(("http://", "https://")):
            raise ValueError("url必须是有效的HTTP/HTTPS URL")

        if not self.prefix.startswith(("http://", "https://")):
            raise ValueError("prefix必须是有效的HTTP/HTTPS URL")

        if self.local_file_path is not None and not isinstance(self.local_file_path, str):
            raise ValueError("local_file_path必须是字符串类型或None")

    def __str__(self) -> str:
        """返回字符串表示。"""
        return f"M3u8Link(url={self.url}, prefix={self.prefix}, local_file_path={self.local_file_path})"


@dataclass
class VideoDownloadContext:
    """
    视频下载上下文数据类。

    封装视频下载所需的所有上下文信息。

    Attributes:
        url: 钉钉直播回放分享链接
        cookie_data: Cookie数据
        headers_data: 请求头数据
        live_name: 直播视频名称
        save_dir: 保存目录
        save_mode: 保存模式

    Example:
        >>> context = VideoDownloadContext(
        ...     url="https://n.dingtalk.com/...",
        ...     cookie_data=CookieData({"session": "abc"}),
        ...     headers_data=HeadersData({"User-Agent": "Mozilla"}),
        ...     live_name="直播视频",
        ...     save_dir="Downloads",
        ...     save_mode="1"
        ... )
    """

    url: str
    cookie_data: CookieData
    headers_data: HeadersData
    live_name: str
    save_dir: Optional[str] = None
    save_mode: str = "1"

    def __post_init__(self):
        """验证视频下载上下文数据。"""
        if not isinstance(self.url, str):
            raise ValueError("url必须是字符串类型")
        if not isinstance(self.live_name, str):
            raise ValueError("live_name必须是字符串类型")
        if not isinstance(self.save_mode, str):
            raise ValueError("save_mode必须是字符串类型")

        if not self.url:
            raise ValueError("url不能为空")
        if not self.live_name:
            raise ValueError("live_name不能为空")

        if self.save_dir is not None and not isinstance(self.save_dir, str):
            raise ValueError("save_dir必须是字符串类型或None")

    def get_cookies_dict(self) -> Dict[str, str]:
        """
        获取Cookie字典。

        Returns:
            Cookie字典
        """
        return self.cookie_data.to_dict()

    def get_headers_dict(self) -> Dict[str, str]:
        """
        获取请求头字典。

        Returns:
            请求头字典
        """
        return self.headers_data.to_dict()

    def is_save_dir_set(self) -> bool:
        """
        检查保存目录是否已设置。

        Returns:
            如果保存目录已设置则返回True
        """
        return self.save_dir is not None
