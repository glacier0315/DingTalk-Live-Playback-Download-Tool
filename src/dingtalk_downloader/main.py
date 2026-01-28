"""
钉钉直播回放下载工具 - 主程序入口

本模块是程序的入口，负责协调各模块。

作者：项目团队
依赖：无
创建日期：2025-01-14
修改历史：
    - 2025-01-14: 初始版本
    - 2025-01-15: 添加日志记录
    - 2026-01-22: 重构-完善异常处理,捕获FileReaderError和M3u8ParseError
    - 2026-01-22: 完善用户输入校验机制
"""

import sys
import logging
from .config.logger_config import LoggerConfig
from .config.yaml_config import (
    YamlConfig,
    ConfigLoadError,
    ConfigValidationError,
)
from .core.downloader import Downloader
from .core.user_interaction_controller import UserInteractionController
from .core.exceptions import CookieError, M3u8ParseError, FileReaderError
from .utils.validator import (
    validate_input,
    validate_required_input,
    validate_dingtalk_url,
    validate_file_path,
)
from .utils.file_reader import FileReader
from .config.constants import (
    BROWSER_OPTION_MAP,
    DOWNLOAD_MODE_SINGLE,
    DOWNLOAD_MODE_BATCH,
)

logger = logging.getLogger(__name__)


def _handle_download_error(error: Exception) -> None:
    """
    处理下载错误。

    Args:
        error: 异常对象
    """
    logger.error(f"发生错误: {error}", exc_info=True)
    print(f"发生错误: {error}")
    sys.exit(1)


def _handle_interrupt() -> None:
    """
    处理用户中断。
    """
    logger.warning("用户中断程序")
    print("\n程序已被用户终止。")
    sys.exit(0)


def _get_user_inputs(
    user_controller: UserInteractionController,
) -> tuple[str, str, str]:
    """
    获取用户输入。

    获取链接、保存模式和浏览器类型。

    Args:
        user_controller: 用户交互控制器

    Returns:
        tuple: (dingtalk_url, save_mode, browser_option)
    """
    dingtalk_url = user_controller.get_user_input(
        "请输入钉钉直播回放分享链接: ",
        validation_func=validate_dingtalk_url,
        error_message=(
            "链接格式不正确。请确保链接以 https://n.dingtalk.com "
            "开头，并包含 liveUuid 参数。"
        ),
        input_name="钉钉直播链接",
    )
    logger.debug(f"用户输入链接: {dingtalk_url}")

    save_mode = validate_input(
        "请选择保存模式（输入1：保存到程序默认路径，"
        "输入2：手动选择保存路径模式，直接回车默认选择1）: ",
        ["1", "2"],
        default_option="1",
    )
    logger.debug(f"用户选择保存模式: {save_mode}")

    browser_option = validate_input(
        "请选择您使用的浏览器（输入1：Edge，输入2：Chrome，"
        "输入3：Firefox，直接回车默认选择1）: ",
        ["1", "2", "3"],
        default_option="1",
    )
    logger.debug(f"浏览器选项: {browser_option}")

    return dingtalk_url, save_mode, browser_option


def _create_downloader(
    browser_option: str,
    save_mode: str,
    user_controller: UserInteractionController,
) -> Downloader:
    """
    创建下载器实例。

    Args:
        browser_option: 浏览器选项
        save_mode: 保存模式
        user_controller: 用户交互控制器

    Returns:
        Downloader实例
    """
    browser_type = BROWSER_OPTION_MAP[browser_option]
    downloader = Downloader(browser_type, save_mode, user_controller)
    logger.debug(f"下载器创建成功 - 浏览器: {browser_type}, " f"保存模式: {save_mode}")
    return downloader


def single_mode(user_controller: UserInteractionController) -> None:
    """
    单个视频下载模式。

    功能：
        - 获取用户输入（链接、保存模式、浏览器类型）
        - 调用下载器下载视频
        - 支持继续输入新链接

    输入：
        - 钉钉直播回放分享链接
        - 保存模式（1：默认路径，2：手动选择）
        - 浏览器类型（1：Edge，2：Chrome，3：Firefox）

    输出：
        - 下载的视频文件

    异常：
        - KeyboardInterrupt：用户中断
        - Exception：其他异常
    """
    logger.info("进入单个视频下载模式")

    try:
        dingtalk_url, save_mode, browser_option = _get_user_inputs(user_controller)
        downloader = _create_downloader(browser_option, save_mode, user_controller)
        downloader.download_single_video(dingtalk_url)

    except KeyboardInterrupt:
        _handle_interrupt()
    except (CookieError, M3u8ParseError, FileReaderError) as e:
        _handle_download_error(e)
    except Exception as e:
        _handle_download_error(e)


def _get_batch_inputs(
    user_controller: UserInteractionController,
) -> tuple[str, dict, str, str]:
    """
    获取批量下载模式的用户输入。

    Args:
        user_controller: 用户交互控制器

    Returns:
        tuple: (file_path, links_dict, save_mode, browser_option)
    """
    file_path = user_controller.get_user_input(
        "请输入钉钉直播回放链接表格路径（支持CSV或Excel格式，" "可直接将文件拖放进窗口）: ",
        validation_func=validate_file_path,
        error_message="文件路径不正确。",
        input_name="文件路径",
    )
    logger.debug("用户已输入文件路径")

    links_dict = FileReader(file_path).read_links()
    logger.info(f"从文件中读取到 {len(links_dict)} 个链接")

    save_mode = validate_input(
        "请选择保存模式（输入1：保存到程序默认路径，"
        "输入2：手动选择保存路径模式，直接回车默认选择1）: ",
        ["1", "2"],
        default_option="1",
    )
    logger.debug(f"用户选择保存模式: {save_mode}")

    browser_option = validate_input(
        "请选择您使用的浏览器（输入1：Edge，输入2：Chrome，"
        "输入3：Firefox，直接回车默认选择1）: ",
        ["1", "2", "3"],
        default_option="1",
    )
    logger.info(f"用户选择浏览器选项: {browser_option}")

    return file_path, links_dict, save_mode, browser_option


def batch_mode(user_controller: UserInteractionController) -> None:
    """
    批量下载模式。

    功能：
        - 获取用户输入（文件路径、保存模式、浏览器类型）
        - 读取文件中的链接
        - 调用下载器批量下载视频
        - 支持继续输入新文件

    输入：
        - 文件路径（CSV/Excel）
        - 保存模式（1：默认路径，2：手动选择）
        - 浏览器类型（1：Edge，2：Chrome，3：Firefox）

    输出：
        - 下载的视频文件

    异常：
        - KeyboardInterrupt：用户中断
        - Exception：其他异常
    """
    logger.info("进入批量下载模式")

    try:
        file_path, links_dict, save_mode, browser_option = _get_batch_inputs(user_controller)
        downloader = _create_downloader(browser_option, save_mode, user_controller)
        downloader.download_batch_videos(links_dict)

    except KeyboardInterrupt:
        _handle_interrupt()
    except (CookieError, M3u8ParseError, FileReaderError) as e:
        _handle_download_error(e)
    except Exception as e:
        _handle_download_error(e)


def _display_welcome_info(config) -> None:
    """
    显示欢迎信息。

    Args:
        config: 配置对象
    """
    app_name = config.get_str("app.name")
    app_version = config.get_str("app.version")
    build_date = config.get_str("app.build_date")

    print("=" * 47)
    print(f"     欢迎使用{app_name} v{app_version}")
    print(f"         构建日期:{build_date}")
    print("=" * 47)
    logger.info("程序启动")


def _handle_config_error(error: Exception, error_type: str) -> None:
    """
    处理配置错误。

    Args:
        error: 异常对象
        error_type: 错误类型
    """
    logger.error(f"配置{error_type}失败: {error}")
    print(f"错误: 配置文件{error_type}失败 - {error}")
    sys.exit(1)


def main() -> None:
    """
    主程序入口。

    显示欢迎信息,获取用户输入的下载模式,调用相应的下载函数。

    Raises:
        ConfigLoadError: 配置文件加载失败
        ConfigValidationError: 配置文件验证失败
    """
    LoggerConfig.setup_logging()

    try:
        config = YamlConfig.get_instance()
        config.load()
        _display_welcome_info(config)

    except ConfigLoadError as e:
        _handle_config_error(e, "加载")
    except ConfigValidationError as e:
        _handle_config_error(e, "验证")

    user_controller = UserInteractionController()

    try:
        download_mode = validate_input(
            "请选择下载模式(输入1:单个视频下载模式,输入2:批量下载模式," "直接回车默认选择1）: ",
            ["1", "2"],
            default_option="1",
        )
        logger.debug(f"用户选择下载模式: {download_mode}")

        if download_mode == DOWNLOAD_MODE_SINGLE:
            single_mode(user_controller)
        elif download_mode == DOWNLOAD_MODE_BATCH:
            batch_mode(user_controller)

    except KeyboardInterrupt:
        _handle_interrupt()
    except (CookieError, M3u8ParseError, FileReaderError) as e:
        _handle_download_error(e)
    except Exception as e:
        _handle_download_error(e)

    logger.info("程序退出")


if __name__ == "__main__":
    main()
