"""
钉钉直播回放下载工具 - 重试装饰器模块

本模块提供统一的重试装饰器，消除重复的重试逻辑。

作者：项目团队
依赖：functools, logging, time, random
创建日期：2026-01-30
修改历史：
    - 2026-01-30: 初始版本，统一重试逻辑
"""

import functools
import logging
import time
import random
from typing import Callable, Optional, Type, Tuple, List
from ..config.constants import (
    VIDEO_DOWNLOAD_RETRY_WAIT_MIN,
    VIDEO_DOWNLOAD_RETRY_WAIT_MAX,
)

logger = logging.getLogger(__name__)


def retry_decorator(
    max_retries: int = 3,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    wait_min: float = VIDEO_DOWNLOAD_RETRY_WAIT_MIN,
    wait_max: float = VIDEO_DOWNLOAD_RETRY_WAIT_MAX,
    on_retry: Optional[Callable] = None,
):
    """
    重试装饰器。

    在函数执行失败时自动重试，支持自定义重试次数、异常类型、等待时间。

    Args:
        max_retries: 最大重试次数，默认为3
        exceptions: 需要重试的异常类型元组，默认为所有异常
        wait_min: 重试等待最小时间（秒），默认为3
        wait_max: 重试等待最大时间（秒），默认为10
        on_retry: 每次重试前的回调函数，接收参数：(exception, attempt, max_retries)

    Returns:
        装饰器函数

    Example:
        @retry_decorator(max_retries=5, exceptions=(ValueError, IOError))
        def fetch_data():
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"函数 {func.__name__} 执行失败 (第 {attempt} 次尝试), "
                        f"错误: {e}"
                    )

                    if attempt < max_retries:
                        if on_retry:
                            on_retry(e, attempt, max_retries)

                        wait_time = random.uniform(wait_min, wait_max)
                        logger.info(f"等待 {wait_time:.2f} 秒后重试...")
                        time.sleep(wait_time)
                    else:
                        logger.error(
                            f"函数 {func.__name__} 已达到最大重试次数 {max_retries}"
                        )

            if last_exception:
                raise last_exception

        return wrapper

    return decorator


def retry_with_backoff(
    max_retries: int = 3,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
):
    """
    指数退避重试装饰器。

    使用指数退避算法进行重试，避免在服务不可用时过度请求。

    Args:
        max_retries: 最大重试次数，默认为3
        exceptions: 需要重试的异常类型元组，默认为所有异常
        base_delay: 基础延迟时间（秒），默认为1.0
        max_delay: 最大延迟时间（秒），默认为60.0
        exponential_base: 指数退避基数，默认为2.0

    Returns:
        装饰器函数

    Example:
        @retry_with_backoff(max_retries=5, base_delay=2.0)
        def api_call():
            pass
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"函数 {func.__name__} 执行失败 (第 {attempt} 次尝试), "
                        f"错误: {e}"
                    )

                    if attempt < max_retries:
                        delay = min(
                            base_delay * (exponential_base ** (attempt - 1)),
                            max_delay,
                        )
                        logger.info(f"等待 {delay:.2f} 秒后重试...")
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"函数 {func.__name__} 已达到最大重试次数 {max_retries}"
                        )

            if last_exception:
                raise last_exception

        return wrapper

    return decorator
