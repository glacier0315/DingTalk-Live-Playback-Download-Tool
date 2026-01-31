# 核心业务模块

## 模块概述

本模块是钉钉直播回放下载工具的核心业务逻辑层，负责协调Cookie获取、m3u8解析、视频下载等核心功能，是整个下载流程的协调者。采用分层架构和设计模式，提供高内聚、低耦合的业务逻辑实现。

## 模块架构

### 架构设计原则

- **单一职责原则**：每个类只负责一个明确的业务功能
- **开闭原则**：对扩展开放，对修改关闭
- **依赖倒置原则**：依赖抽象而非具体实现
- **接口隔离原则**：使用最小化接口
- **外观模式**：Downloader作为统一入口，简化子系统调用

### 类图结构

```text
┌─────────────────────────────────────────────────────────────┐
│                        Downloader                            │
│                    (外观类 - 统一入口)                        │
├─────────────────────────────────────────────────────────────┤
│ + download_single_video(url: str)                          │
│ + download_batch_videos(urls: Dict[int, str])               │
│ + close()                                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ 依赖
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  VideoDownloadManager                        │
│              (视频下载管理器 - 流程协调)                       │
├─────────────────────────────────────────────────────────────┤
│ + initialize_download(url: str) -> VideoDownloadContext     │
│ + repeat_get_context(url: str) -> VideoDownloadContext      │
│ + process_video(context: VideoDownloadContext) -> bool      │
│ + close()                                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ 依赖
                            ↓
        ┌───────────────────┴───────────────────┐
        │                                       │
        ↓                                       ↓
┌──────────────────────┐           ┌──────────────────────┐
│   CookieHandler      │           │  M3u8DownloadService │
│  (Cookie处理器)       │           │ (m3u8下载服务)       │
├──────────────────────┤           ├──────────────────────┤
│ + get_cookie()       │           │ + fetch_and_download │
│ + repeat_get_cookie()│           │   _m3u8()            │
│ + close()            │           └──────────────────────┘
└──────────────────────┘                      │
        │                                    │
        │ 依赖                               │ 依赖
        ↓                                    ↓
┌──────────────────────┐           ┌──────────────────────┐
│   M3u8Parser         │           │  M3u8FileManager     │
│  (m3u8解析器)         │           │ (m3u8文件管理器)      │
├──────────────────────┤           ├──────────────────────┤
│ + fetch_m3u8_link()  │           │ + get_temp_file_path │
│ + download_m3u8_file()│          │ + clean_temp_files   │
│ + extract_prefix()   │           └──────────────────────┘
└──────────────────────┘
```

## 功能描述

### Downloader - 下载器外观类

**职责**：作为统一入口，协调各个子模块完成视频下载

**功能**：

- 单个视频下载
- 批量视频下载
- 用户交互处理
- 资源生命周期管理

**设计模式**：外观模式（Facade Pattern）

**核心实现**：

```python
class Downloader:
    def __init__(
        self,
        browser_type: str,
        save_mode: str,
        user_controller: UserInteractionController,
        dependency_factory: Optional[DependencyFactory] = None,
    ):
        self.browser_type = browser_type
        self.save_mode = save_mode
        self.user_controller = user_controller

        self.dependency_factory = dependency_factory or DependencyFactory()

        cookie_handler = self.dependency_factory.get_cookie_handler(browser_type)
        path_selector = self.dependency_factory.get_path_selector(save_mode)
        n_m3u8dl_re = self.dependency_factory.get_n_m3u8dl_re()

        self.video_manager = VideoDownloadManager(
            browser_type,
            save_mode,
            cookie_handler=cookie_handler,
            path_selector=path_selector,
            n_m3u8dl_re=n_m3u8dl_re,
        )
```

### VideoDownloadManager - 视频下载管理器

**职责**：协调Cookie获取、m3u8解析、视频下载的整个流程

**功能**：

- 初始化下载环境
- 重复获取下载上下文
- 处理单个视频下载
- 管理下载资源
- 自动重试机制（最大20次）

**设计模式**：协调器模式（Coordinator Pattern）

**核心实现**：

```python
class VideoDownloadManager:
    def process_video(self, context: VideoDownloadContext) -> bool:
        max_retries = VIDEO_DOWNLOAD_MAX_RETRIES
        m3u8_link = None

        for attempt in range(1, max_retries + 1):
            try:
                m3u8_link = self._attempt_download(context, attempt, max_retries)
                download_success = self._download_video(m3u8_link, context)

                if download_success:
                    logger.info(f"视频下载成功: {context.live_name} (第 {attempt} 次尝试)")
                    return True

            except (DownloadError, BrowserError, NetworkError, M3u8ParseError) as e:
                self._handle_download_exception(context, e, attempt, max_retries)
                if attempt == max_retries:
                    return False
            finally:
                if m3u8_link and m3u8_link.local_file_path:
                    self.m3u8_download_service.cleanup_temp_file(m3u8_link.local_file_path)

        return False
```

### CookieHandler - Cookie处理模块

**职责**：获取和管理Cookie及请求头

**功能**：

- 通过Selenium自动化浏览器获取登录后的Cookie
- 获取请求头信息（User-Agent、Referer等）
- 获取直播视频名称
- 支持重复获取Cookie（复用浏览器实例）
- 提取并构建请求头

**核心算法**：

- 多选择器策略获取直播名称（XPath/CSS Selector）
- 请求头动态构建和合并

**核心实现**：

```python
class CookieHandler:
    def _get_live_name(self) -> str:
        for selector_type, selector_value in LIVE_NAME_SELECTORS:
            try:
                if selector_type == "xpath":
                    live_name = self.browser.get_element_by_xpath(selector_value).text
                elif selector_type == "css":
                    live_name = self.browser.get_element_by_class_name(selector_value).text
                return live_name
            except Exception:
                continue
        return "直播视频名称不可获取"
```

### M3u8Parser - m3u8解析模块

**职责**：从浏览器网络日志中提取m3u8链接

**功能**：

- 从浏览器性能日志中提取m3u8链接
- 下载m3u8文件
- 提取基础URL（prefix）
- 支持重试机制（最多MAX_RETRY_COUNT次）
- 支持Edge、Chrome、Firefox三种浏览器

**核心算法**：

- 日志解析算法：从性能日志中提取包含liveUuid的m3u8链接
- URL解析算法：使用urllib.parse提取liveUuid参数
- 重试机制：失败后自动刷新页面重试

**核心实现**：

```python
class M3u8Parser:
    def fetch_m3u8_link(self, url: str) -> str:
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        live_uuid = query_params.get("liveUuid", [None])[FIRST_ELEMENT_INDEX]

        if not live_uuid:
            logger.error("未能从 URL 提取 liveUuid")
            raise M3u8ParseError("未能从 URL 提取 liveUuid 参数")

        for attempt in range(self.max_retries):
            try:
                logger.info(f"第 {attempt + 1} 次尝试获取到 m3u8 链接")
                self._refresh_page()
                logs = self.browser.get_log(LOG_TYPE_PERFORMANCE)
                m3u8_links = self.browser.extract_m3u8_links_from_logs(logs, live_uuid)
                if not m3u8_links:
                    logger.warning(f"第 {attempt + 1} 次尝试未获取到 m3u8 链接")
                    continue

                if len(m3u8_links) >= 1:
                    logger.info(
                        f"提取到 {len(m3u8_links)} 个 m3u8 链接，预期仅 1 个, "
                        f"返回最后一个链接: {m3u8_links[-1]}"
                    )
                    return m3u8_links[-1]
            except Exception as e:
                logger.error(f"第 {attempt + 1} 次尝试获取 m3u8 链接时发生错误: {e}", exc_info=True)

        logger.warning(f"经过 {self.max_retries} 次重试后仍未获取到 m3u8 链接")
        raise M3u8ParseError(f"经过 {self.max_retries} 次重试后仍未获取到 m3u8 链接")
```

### M3u8DownloadService - m3u8下载服务

**职责**：封装m3u8文件下载逻辑

**功能**：

- 获取并下载m3u8文件
- 验证m3u8文件完整性
- 提取基础URL
- 生成临时文件路径
- 清理临时文件

**设计模式**：服务模式（Service Pattern）

**核心实现**：

```python
class M3u8DownloadService:
    def fetch_and_download_m3u8(
        self,
        url: str,
        m3u8_headers: dict,
    ) -> M3u8Link:
        m3u8_link = self.m3u8_parser.fetch_m3u8_link(url)
        logger.info(f"获取到 m3u8 链接: {m3u8_link}")

        m3u8_file = self.m3u8_file_manager.get_temp_file_path()
        logger.debug(f"准备下载 m3u8 文件到: {m3u8_file}")

        try:
            m3u8_file = self.m3u8_parser.download_m3u8_file(m3u8_link, m3u8_file, m3u8_headers)

            if not m3u8_file or not os.path.exists(m3u8_file):
                raise DownloadError(f"m3u8 文件下载失败或文件不存在: {m3u8_file}")

            file_size = os.path.getsize(m3u8_file)
            logger.debug(f"m3u8 文件大小: {file_size} bytes")

        except Exception as e:
            logger.error(f"下载 m3u8 文件时发生错误: {e}", exc_info=True)
            raise DownloadError(f"下载 m3u8 文件失败: {e}") from e

        prefix = self.m3u8_parser.extract_prefix(m3u8_link)
        logger.info(f"提取到基础 URL: {prefix}")

        return M3u8Link(url=m3u8_link, prefix=prefix, local_file_path=m3u8_file)
```

### DependencyFactory - 依赖工厂

**职责**：创建和管理各种依赖实例，实现依赖注入和工厂模式

**功能**：

- 创建CookieHandler实例
- 创建M3u8Parser实例
- 创建PathSelector实例
- 创建NM3u8DLRE实例
- 创建M3u8DownloadService实例
- 实例缓存，避免重复创建

**设计模式**：工厂模式（Factory Pattern）、依赖注入（Dependency Injection）

**核心实现**：

```python
class DependencyFactory:
    def __init__(self):
        self._instances: Dict[str, object] = {}

    def get_cookie_handler(self, browser_type: str) -> CookieHandler:
        key = f"cookie_handler_{browser_type}"
        if key not in self._instances:
            self._instances[key] = CookieHandler(browser_type)
            logger.debug(f"创建Cookie处理器实例 - 浏览器类型: {browser_type}")
        return self._instances[key]

    def get_m3u8_parser(self, browser_driver) -> M3u8Parser:
        key = f"m3u8_parser_{id(browser_driver)}"
        if key not in self._instances:
            self._instances[key] = M3u8Parser(browser_driver)
            logger.debug(f"创建m3u8解析器实例 - 浏览器驱动ID: {id(browser_driver)}")
        return self._instances[key]
```

### UserInteractionController - 用户交互控制器

**职责**：处理用户交互逻辑

**功能**：

- 获取用户输入
- 验证用户输入
- 询问用户是否继续下载
- 询问用户文件路径

**核心实现**：

```python
class UserInteractionController:
    def get_user_input(
        self,
        prompt: str,
        validation_func: Optional[Callable[[str], bool]] = None,
        error_message: Optional[str] = None,
        input_name: str = "输入",
    ) -> str:
        while True:
            try:
                user_input = input(prompt)

                if validation_func:
                    if validation_func(user_input):
                        return user_input
                    else:
                        if error_message:
                            print(error_message)
                        continue

                return user_input

            except EOFError:
                raise
            except KeyboardInterrupt:
                print("\n用户中断输入")
                raise
```

## 核心实现原理

### Cookie获取流程

```text
创建浏览器实例 (BrowserFactory)
  ↓
导航到指定URL
  ↓
等待用户手动登录
  ↓
获取User-Agent和Referer (JavaScript执行)
  ↓
构建请求头 (HeaderManager)
  ↓
获取直播名称 (多选择器策略)
  ↓
获取Cookie (Selenium API)
  ↓
返回CookieData、HeadersData、直播名称
```

### 直播名称获取算法

采用多选择器策略，按优先级依次尝试：

```python
def _get_live_name(self) -> str:
    for selector_type, selector_value in LIVE_NAME_SELECTORS:
        try:
            if selector_type == "xpath":
                live_name = self.browser.get_element_by_xpath(selector_value).text
            elif selector_type == "css":
                live_name = self.browser.get_element_by_class_name(selector_value).text
            return live_name
        except Exception:
            continue
    return "直播视频名称不可获取"
```

### m3u8链接提取算法

#### URL解析

```python
parsed_url = urlparse(url)
query_params = parse_qs(parsed_url.query)
live_uuid = query_params.get("liveUuid", [None])[0]
```

#### 日志解析（Edge/Chrome）

```python
for log in logs:
    if "message" in log:
        log_message = log["message"]
    if ".m3u8" in log_message:
        start_idx = log_message.find('url":"') + len('url":"')
        end_idx = log_message.find('"', start_idx)
        m3u8_url = log_message[start_idx:end_idx]
        if live_uuid in m3u8_url:
            m3u8_links.append(m3u8_url)
```

#### 重试机制

```python
for attempt in range(self.max_retries):
    try:
        self._refresh_page()
        logs = self.browser.get_log("performance")
        m3u8_links = self.browser.extract_m3u8_links_from_logs(logs, live_uuid)
        if m3u8_links:
            return m3u8_links[-1]
    except Exception as e:
        logger.error(f"第 {attempt + 1} 次尝试失败: {e}")
raise M3u8ParseError("重试次数耗尽")
```

### 视频下载流程

```text
初始化下载环境 (VideoDownloadManager.initialize_download)
  ↓
获取Cookie和请求头 (CookieHandler.get_cookie)
  ↓
创建m3u8解析器 (M3u8Parser)
  ↓
获取并下载m3u8文件 (M3u8DownloadService.fetch_and_download_m3u8)
  ↓
提取基础URL (M3u8Parser.extract_prefix)
  ↓
选择保存路径 (PathSelector.get_save_dir)
  ↓
调用N_m3u8DL-RE下载视频 (NM3u8DLRE.download)
  ↓
验证下载结果
  ↓
清理临时文件
```

### 单个视频下载流程

```text
用户输入URL
  ↓
创建下载器 (Downloader)
  ↓
初始化下载环境 (VideoDownloadManager.initialize_download)
  ↓
处理视频 (VideoDownloadManager.process_video)
  ↓
询问是否继续下载
  ↓
重复或退出
```

### 批量视频下载流程

```text
用户输入文件路径
  ↓
读取链接列表 (FileReader)
  ↓
创建下载器 (Downloader)
  ↓
下载第一个视频
  ↓
遍历剩余链接下载
  ↓
询问是否继续下载新文件
  ↓
重复或退出
```

## 数据模型

### VideoDownloadContext - 视频下载上下文

**用途**：封装视频下载所需的所有上下文信息

**属性**：

- `url`: 钉钉直播回放分享链接
- `cookie_data`: Cookie数据值对象
- `headers_data`: 请求头数据值对象
- `live_name`: 直播视频名称
- `save_dir`: 保存目录
- `save_mode`: 保存模式

**设计模式**：数据传输对象（DTO）

### CookieData - Cookie数据值对象

**用途**：封装Cookie数据，提供类型安全和不可变性

**属性**：

- `cookies`: Cookie字典

**特性**：

- 不可变（frozen=True）
- 类型验证
- 提供便捷访问方法

**设计模式**：值对象（Value Object）

### HeadersData - 请求头数据值对象

**用途**：封装HTTP请求头数据

**属性**：

- `headers`: 请求头字典

**特性**：

- 不可变（frozen=True）
- 类型验证
- 提供便捷访问方法

**设计模式**：值对象（Value Object）

### M3u8Link - m3u8链接值对象

**用途**：封装m3u8链接和相关信息

**属性**：

- `url`: m3u8文件URL
- `prefix`: 基础URL
- `local_file_path`: 本地m3u8文件路径

**特性**：

- 不可变（frozen=True）
- URL格式验证

**设计模式**：值对象（Value Object）

## 使用方法

### Downloader使用示例

```python
from dingtalk_downloader.core.downloader import Downloader
from dingtalk_downloader.config.constants import (
    BROWSER_TYPE_EDGE,
    SAVE_MODE_DEFAULT
)

# 创建下载器
downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT, user_controller)

# 下载单个视频
downloader.download_single_video("https://n.dingtalk.com/xxx")

# 批量下载视频
urls = {
    0: "https://n.dingtalk.com/xxx",
    1: "https://n.dingtalk.com/yyy",
    2: "https://n.dingtalk.com/zzz"
}
downloader.download_batch_videos(urls)

# 关闭下载器
downloader.close()
```

### CookieHandler使用示例

```python
from dingtalk_downloader.core.cookie_handler import CookieHandler
from dingtalk_downloader.config.constants import BROWSER_TYPE_EDGE

# 创建Cookie处理器
cookie_handler = CookieHandler(BROWSER_TYPE_EDGE)

# 获取Cookie和请求头
cookie_data, headers_data, live_name = cookie_handler.get_cookie(
    "https://n.dingtalk.com/xxx"
)

print(f"直播名称: {live_name}")
print(f"Cookie数量: {len(cookie_data)}")

# 重复获取Cookie（复用浏览器实例）
cookie_data, headers_data, live_name = cookie_handler.repeat_get_cookie(
    "https://n.dingtalk.com/yyy"
)

# 关闭浏览器
cookie_handler.close()
```

### M3u8Parser使用示例

```python
from dingtalk_downloader.core.m3u8_parser import M3u8Parser
from dingtalk_downloader.config.constants import BROWSER_TYPE_EDGE

# 创建m3u8解析器
parser = M3u8Parser(browser)

# 获取m3u8链接
m3u8_link = parser.fetch_m3u8_link("https://n.dingtalk.com/xxx")

if m3u8_link:
    print(f"获取到m3u8链接: {m3u8_link}")

    # 下载m3u8文件
    m3u8_file = parser.download_m3u8_file(
        m3u8_link,
        "output.m3u8",
        headers
    )

    # 提取基础URL
    prefix = parser.extract_prefix(m3u8_link)
    print(f"基础URL: {prefix}")
```

### VideoDownloadManager使用示例

```python
from dingtalk_downloader.core.video_download_manager import VideoDownloadManager
from dingtalk_downloader.config.constants import BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT

# 创建视频下载管理器
manager = VideoDownloadManager(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)

# 初始化下载环境
context = manager.initialize_download("https://n.dingtalk.com/xxx")

# 处理视频下载
success = manager.process_video(context)

# 重复获取上下文（复用浏览器）
context2 = manager.repeat_get_context("https://n.dingtalk.com/yyy")
success2 = manager.process_video(context2)

# 关闭管理器
manager.close()
```

### DependencyFactory使用示例

```python
from dingtalk_downloader.core.dependency_factory import DependencyFactory

# 创建依赖工厂
factory = DependencyFactory()

# 获取Cookie处理器
cookie_handler = factory.get_cookie_handler("edge")

# 获取路径选择器
path_selector = factory.get_path_selector("1")

# 获取N_m3u8DL-RE实例
n_m3u8dl_re = factory.get_n_m3u8dl_re()

# 清除所有缓存的实例
factory.clear_instances()
```

## 接口参数说明

### Downloader类

#### **init**(browser_type: str, save_mode: str, user_controller: UserInteractionController, dependency_factory: Optional[DependencyFactory] = None)

**参数**：

- `browser_type`：浏览器类型（edge/chrome/firefox）
- `save_mode`：保存模式（1：默认路径，2：手动选择）
- `user_controller`：用户交互控制器
- `dependency_factory`：依赖工厂（可选，用于依赖注入）

**功能**：初始化下载器

#### download_single_video(url: str) -> None

**参数**：

- `url`：钉钉直播回放分享链接

**功能**：下载单个视频

**异常**：

- `DownloadError`：下载失败时

#### download_batch_videos(urls: Dict[int, str]) -> None

**参数**：

- `urls`：链接字典 {index: url}

**功能**：批量下载视频

**异常**：

- `DownloadError`：下载失败时

#### close() -> None

**功能**：关闭浏览器，释放资源

### VideoDownloadManager类

#### **init**(browser_type: str, save_mode: str, cookie_handler: Optional[CookieHandler] = None, m3u8_parser: Optional[M3u8Parser] = None, m3u8_download_service: Optional[M3u8DownloadService] = None, path_selector: Optional[PathSelector] = None, n_m3u8dl_re: Optional[NM3u8DLRE] = None)

**参数**：

- `browser_type`：浏览器类型（edge/chrome/firefox）
- `save_mode`：保存模式（1：默认路径，2：手动选择）
- `cookie_handler`：Cookie处理器（可选，用于依赖注入）
- `m3u8_parser`：m3u8解析器（可选，用于依赖注入）
- `m3u8_download_service`：m3u8下载服务（可选，用于依赖注入）
- `path_selector`：路径选择器（可选，用于依赖注入）
- `n_m3u8dl_re`：NM3u8DLRE实例（可选，用于依赖注入）

**功能**：初始化视频下载管理器

#### initialize_download(url: str) -> VideoDownloadContext

**参数**：

- `url`：钉钉直播回放分享链接

**返回值**：

- `VideoDownloadContext`：视频下载上下文

**功能**：初始化下载环境

#### process_video(context: VideoDownloadContext) -> bool

**参数**：

- `context`：视频下载上下文

**返回值**：

- `bool`：下载成功返回True，下载失败返回False

**功能**：处理单个视频下载

**异常**：

- `DownloadError`：处理失败时

#### close() -> None

**功能**：关闭浏览器，释放资源

### CookieHandler类

#### **init**(browser_type: str)

**参数**：

- `browser_type`：浏览器类型（edge/chrome/firefox）

**功能**：初始化Cookie处理器

#### get_cookie(url: str) -> Tuple[CookieData, HeadersData, str]

**参数**：

- `url`：钉钉直播回放分享链接

**返回值**：

- `Tuple`：包含三个元素的元组
  - `cookie_data`：Cookie数据值对象
  - `headers_data`：请求头数据值对象
  - `live_name`：直播视频名称

**功能**：获取Cookie和请求头信息

**异常**：

- `CookieError`：获取失败时

#### close() -> None

**功能**：关闭浏览器，释放资源

### M3u8Parser类

#### **init**(browser: BrowserDriver, max_retries: int = MAX_RETRY_COUNT)

**参数**：

- `browser`：浏览器实例
- `max_retries`：最大重试次数，默认为5

**功能**：初始化m3u8解析器

#### fetch_m3u8_link(url: str) -> str

**参数**：

- `url`：钉钉直播回放分享链接

**返回值**：

- `str`：m3u8链接

**功能**：从浏览器网络日志中提取m3u8链接

**异常**：

- `M3u8ParseError`：提取失败时

#### download_m3u8_file(url: str, filename: str, headers: dict) -> str

**参数**：

- `url`：m3u8文件URL
- `filename`：保存的文件名
- `headers`：请求头字典

**返回值**：

- `str`：m3u8文件路径

**功能**：下载m3u8文件

**异常**：

- `M3u8ParseError`：下载失败时

#### extract_prefix(url: str) -> str

**参数**：

- `url`：m3u8文件URL

**返回值**：

- `str`：基础URL

**功能**：提取基础URL

## 依赖关系

### 依赖的模块

1. `browser.browser_factory` - 浏览器工厂
2. `browser.*_driver` - 浏览器驱动
3. `binary.n_m3u8dl_re` - N_m3u8DL-RE调用封装
4. `utils.path_helper` - 路径处理工具
5. `utils.path_selector` - 路径选择器
6. `utils.models` - 数据模型
7. `config.constants` - 常量定义
8. `config.yaml_config` - YAML配置管理
9. `config.header_manager` - 请求头管理

### 被依赖的模块

1. `main` - 主程序入口

## 数据流程

### Cookie获取流程

```text
创建浏览器实例
  ↓
导航到指定URL
  ↓
等待用户登录
  ↓
获取User-Agent和Referer
  ↓
构建请求头
  ↓
获取直播名称（多选择器策略）
  ↓
获取Cookie
  ↓
返回CookieData、HeadersData、直播名称
```

### m3u8解析流程

```text
解析URL获取liveUuid
  ↓
获取浏览器性能日志
  ↓
遍历日志查找包含liveUuid的m3u8链接
  ↓
如果未找到，刷新页面重试
  ↓
最多重试MAX_RETRY_COUNT次
  ↓
返回m3u8链接
```

### 视频下载流程

```text
获取Cookie和请求头
  ↓
创建m3u8解析器
  ↓
获取m3u8链接
  ↓
下载m3u8文件
  ↓
提取基础URL
  ↓
选择保存路径
  ↓
调用N_m3u8DL-RE下载视频
  ↓
验证下载结果
  ↓
清理临时文件
```

## 设计模式应用

### 1. 外观模式（Facade Pattern）

**应用类**：Downloader

**说明**：Downloader作为统一入口，隐藏了VideoDownloadManager、CookieHandler、M3u8Parser等子系统的复杂性，为客户端提供简单的接口。

### 2. 工厂模式（Factory Pattern）

**应用类**：BrowserFactory（在browser模块中）、DependencyFactory

**说明**：根据浏览器类型创建对应的浏览器实例；根据依赖类型创建对应的依赖实例。

### 3. 单例模式（Singleton Pattern）

**应用类**：YamlConfig（在config模块中）

**说明**：确保配置文件在应用生命周期内只被加载一次。

### 4. 策略模式（Strategy Pattern）

**应用类**：PathSelector（在utils模块中）

**说明**：根据不同的保存模式（默认路径/手动选择）采用不同的路径选择策略。

### 5. 值对象模式（Value Object Pattern）

**应用类**：CookieData、HeadersData、M3u8Link

**说明**：封装数据，提供类型安全和不可变性。

### 6. 数据传输对象（DTO）

**应用类**：VideoDownloadContext

**说明**：封装视频下载所需的所有上下文信息，在模块间传递。

### 7. 依赖注入（Dependency Injection）

**应用类**：DependencyFactory

**说明**：通过依赖工厂管理依赖实例的创建和生命周期，降低模块间耦合度。

### 8. 协调器模式（Coordinator Pattern）

**应用类**：VideoDownloadManager

**说明**：协调Cookie获取、m3u8解析、视频下载的整个流程。

## 异常处理

### 异常层次结构

```tree
Exception
  └── DownloadError (下载异常)
        ├── CookieError (Cookie处理异常)
        ├── M3u8ParseError (m3u8解析异常)
        ├── FileReaderError (文件读取异常)
        ├── BrowserError (浏览器操作异常)
        ├── NetworkError (网络请求异常)
        └── ValidationError (输入验证异常)
```

### 异常处理策略

1. **捕获并转换**：在底层捕获具体异常，转换为业务异常
2. **记录日志**：记录详细的错误信息和堆栈跟踪
3. **资源清理**：异常时自动关闭浏览器，释放资源
4. **用户友好**：向用户显示友好的错误信息
5. **重试机制**：支持自动重试，提高成功率

## 注意事项

### 1. 浏览器资源管理

- 使用完毕后必须调用`close()`方法
- 避免浏览器进程残留
- 使用上下文管理器（with语句）自动管理资源

### 2. 重试机制

- m3u8链接提取失败时会自动重试
- 视频下载失败时会自动重试（最多20次）
- 每次重试前会刷新页面
- 每次重试前会等待3-10秒

### 3. 异常处理

- 捕获所有异常并记录日志
- 异常时自动关闭浏览器
- 向用户显示友好的错误信息

### 4. 用户交互

- Cookie获取时需要用户手动登录
- 支持继续下载新链接
- 支持批量下载

### 5. 日志记录

- 在关键步骤记录日志
- 异常时记录完整堆栈信息
- 使用不同日志级别（DEBUG、INFO、WARNING、ERROR）

### 6. 配置管理

- 使用YamlConfig单例模式
- 支持配置热重载
- 配置验证确保数据有效性

### 7. 依赖注入

- 使用DependencyFactory管理依赖实例
- 避免重复创建相同实例
- 支持自定义依赖注入

## 性能优化

### 1. 浏览器复用

- 批量下载时复用浏览器实例
- 减少浏览器启动开销

### 2. 请求头缓存

- HeaderManager缓存请求头
- 避免重复构建

### 3. 临时文件管理

- 使用临时目录存储m3u8文件
- 下载完成后自动清理

### 4. 依赖注入

- 使用DependencyFactory管理依赖实例
- 避免重复创建相同实例

## 扩展方向

### 1. 断点续传

- 支持下载中断后继续下载
- 记录下载进度

### 2. 下载队列管理

- 添加下载队列
- 支持暂停、恢复、取消等操作

### 3. 进度显示

- 添加下载进度条
- 实时速度显示

### 4. 多线程下载

- 支持多线程下载提高速度
- 并发下载多个视频

### 5. 下载历史记录

- 记录下载历史
- 支持重新下载

### 6. 下载限速

- 支持下载速度限制
- 避免占用过多带宽

## 测试建议

### 1. 单元测试

- 测试各个类的独立功能
- Mock浏览器和网络请求
- 测试重试机制

### 2. 集成测试

- 测试完整的下载流程
- 测试批量下载
- 测试异常处理

### 3. 异常测试

- 测试各种异常情况
- 验证异常处理逻辑
- 测试边界条件

## 维护责任人

- **主要维护者**：项目团队
- **最后更新日期**：2026-01-31

## 相关文档

- [主程序入口模块](../README.md)
- [浏览器驱动模块](../browser/README.md)
- [二进制工具封装模块](../binary/README.md)
- [工具模块](../utils/README.md)
- [配置模块](../config/README.md)
