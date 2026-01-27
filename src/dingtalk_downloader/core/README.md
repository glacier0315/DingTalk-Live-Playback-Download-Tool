# 核心业务模块

## 模块概述

本模块是钉钉直播回放下载工具的核心业务逻辑层，负责协调 Cookie 获取、m3u8 解析、视频下载等核心功能，是整个下载流程的协调者。采用分层架构和设计模式，提供高内聚、低耦合的业务逻辑实现。

## 模块架构

### 架构设计原则

- **单一职责原则**：每个类只负责一个明确的业务功能
- **开闭原则**：对扩展开放，对修改关闭
- **依赖倒置原则**：依赖抽象而非具体实现
- **接口隔离原则**：使用最小化接口
- **外观模式**：Downloader 作为统一入口，简化子系统调用

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

### VideoDownloadManager - 视频下载管理器

**职责**：协调 Cookie 获取、m3u8 解析、视频下载的整个流程

**功能**：

- 初始化下载环境
- 重复获取下载上下文
- 处理单个视频下载
- 管理下载资源

**设计模式**：协调器模式（Coordinator Pattern）

### CookieHandler - Cookie 处理模块

**职责**：获取和管理 Cookie 及请求头

**功能**：

- 通过 Selenium 自动化浏览器获取登录后的 Cookie
- 获取请求头信息（User-Agent、Referer 等）
- 获取直播视频名称
- 支持重复获取 Cookie（复用浏览器实例）
- 提取并构建请求头

**核心算法**：

- 多选择器策略获取直播名称（XPath/CSS Selector）
- 请求头动态构建和合并

### M3u8Parser - m3u8 解析模块

**职责**：从浏览器网络日志中提取 m3u8 链接

**功能**：

- 从浏览器性能日志中提取 m3u8 链接
- 下载 m3u8 文件
- 提取基础 URL（prefix）
- 支持重试机制（最多 MAX_RETRY_COUNT 次）
- 支持 Edge、Chrome、Firefox 三种浏览器

**核心算法**：

- 日志解析算法：从性能日志中提取包含 liveUuid 的 m3u8 链接
- URL 解析算法：使用 urllib.parse 提取 liveUuid 参数
- 重试机制：失败后自动刷新页面重试

### M3u8DownloadService - m3u8 下载服务

**职责**：封装 m3u8 文件下载逻辑

**功能**：

- 获取并下载 m3u8 文件
- 验证 m3u8 文件完整性
- 提取基础 URL
- 生成临时文件路径

**设计模式**：服务模式（Service Pattern）

### PathSelector - 路径选择器

**职责**：根据保存模式选择下载路径

**功能**：

- 支持默认路径模式
- 支持手动选择路径模式
- 路径验证和创建

**设计模式**：策略模式（Strategy Pattern）

### HeaderManager - 请求头管理器

**职责**：统一管理请求头配置

**功能**：

- 从配置文件加载请求头
- 支持请求头动态覆盖
- 提供请求头缓存机制

**设计模式**：管理器模式（Manager Pattern）

## 核心实现原理

### Cookie 获取流程

```text
创建浏览器实例 (BrowserFactory)
  ↓
导航到指定 URL
  ↓
等待用户手动登录
  ↓
获取 User-Agent 和 Referer (JavaScript 执行)
  ↓
构建请求头 (HeaderManager)
  ↓
获取直播名称 (多选择器策略)
  ↓
获取 Cookie (Selenium API)
  ↓
返回浏览器实例、CookieData、HeadersData、直播名称
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

### m3u8 链接提取算法

#### URL 解析

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
获取 Cookie 和请求头 (CookieHandler.get_cookie)
  ↓
创建 m3u8 解析器 (M3u8Parser)
  ↓
获取并下载 m3u8 文件 (M3u8DownloadService.fetch_and_download_m3u8)
  ↓
提取基础 URL (M3u8Parser.extract_prefix)
  ↓
选择保存路径 (PathSelector.get_save_dir)
  ↓
调用 N_m3u8DL-RE 下载视频 (NM3u8DLRE.download)
  ↓
验证下载结果
  ↓
清理临时文件
```

### 单个视频下载流程

```text
用户输入 URL
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
- `cookie_data`: Cookie 数据值对象
- `headers_data`: 请求头数据值对象
- `live_name`: 直播视频名称
- `save_dir`: 保存目录
- `save_mode`: 保存模式

**设计模式**：数据传输对象（DTO）

### CookieData - Cookie 数据值对象

**用途**：封装 Cookie 数据，提供类型安全和不可变性

**属性**：

- `cookies`: Cookie 字典

**特性**：

- 不可变（frozen=True）
- 类型验证
- 提供便捷访问方法

**设计模式**：值对象（Value Object）

### HeadersData - 请求头数据值对象

**用途**：封装 HTTP 请求头数据

**属性**：

- `headers`: 请求头字典

**特性**：

- 不可变（frozen=True）
- 类型验证
- 提供便捷访问方法

**设计模式**：值对象（Value Object）

### M3u8Link - m3u8 链接值对象

**用途**：封装 m3u8 链接和相关信息

**属性**：

- `url`: m3u8 文件 URL
- `prefix`: 基础 URL
- `local_file_path`: 本地 m3u8 文件路径

**特性**：

- 不可变（frozen=True）
- URL 格式验证

**设计模式**：值对象（Value Object）

## 使用方法

### Downloader 使用示例

```python
from dingtalk_downloader.core.downloader import Downloader
from dingtalk_downloader.config.constants import (
    BROWSER_TYPE_EDGE,
    SAVE_MODE_DEFAULT
)

# 创建下载器
downloader = Downloader(BROWSER_TYPE_EDGE, SAVE_MODE_DEFAULT)

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

### CookieHandler 使用示例

```python
from dingtalk_downloader.core.cookie_handler import CookieHandler
from dingtalk_downloader.config.constants import BROWSER_TYPE_EDGE

# 创建 Cookie 处理器
cookie_handler = CookieHandler(BROWSER_TYPE_EDGE)

# 获取 Cookie 和请求头
browser, cookie_data, headers_data, live_name = cookie_handler.get_cookie(
    "https://n.dingtalk.com/xxx"
)

print(f"直播名称: {live_name}")
print(f"Cookie 数量: {len(cookie_data)}")

# 重复获取 Cookie（复用浏览器实例）
cookie_data, headers_data, live_name = cookie_handler.repeat_get_cookie(
    "https://n.dingtalk.com/yyy"
)

# 关闭浏览器
cookie_handler.close()
```

### M3u8Parser 使用示例

```python
from dingtalk_downloader.core.m3u8_parser import M3u8Parser
from dingtalk_downloader.config.constants import BROWSER_TYPE_EDGE

# 创建 m3u8 解析器
parser = M3u8Parser(browser)

# 获取 m3u8 链接
m3u8_link = parser.fetch_m3u8_link("https://n.dingtalk.com/xxx")

if m3u8_link:
    print(f"获取到 m3u8 链接: {m3u8_link}")

    # 下载 m3u8 文件
    m3u8_file = parser.download_m3u8_file(
        m3u8_link,
        "output.m3u8",
        headers
    )

    # 提取基础 URL
    prefix = parser.extract_prefix(m3u8_link)
    print(f"基础 URL: {prefix}")
```

### VideoDownloadManager 使用示例

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

## 接口参数说明

### Downloader 类

#### **init**(browser_type: str, save_mode: str)

**参数**：

- `browser_type`：浏览器类型（edge/chrome/firefox）
- `save_mode`：保存模式（1：默认路径，2：手动选择）

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

### CookieHandler 类

#### **init**(browser_type: str)

**参数**：

- `browser_type`：浏览器类型（edge/chrome/firefox）

**功能**：初始化 Cookie 处理器

#### get_cookie(url: str) -> Tuple[Any, CookieData, HeadersData, str]

**参数**：

- `url`：钉钉直播回放分享链接

**返回值**：

- `Tuple`：包含四个元素的元组
  - `browser`：浏览器实例
  - `cookie_data`：Cookie 数据值对象
  - `headers_data`：请求头数据值对象
  - `live_name`：直播视频名称

**功能**：获取 Cookie 和请求头信息

**异常**：

- `CookieError`：获取失败时

#### repeat_get_cookie(url: str) -> Tuple[CookieData, HeadersData, str]

**参数**：

- `url`：钉钉直播回放分享链接

**返回值**：

- `Tuple`：包含三个元素的元组
  - `cookie_data`：Cookie 数据值对象
  - `headers_data`：请求头数据值对象
  - `live_name`：直播视频名称

**功能**：重复获取 Cookie 和请求头信息

**异常**：

- `CookieError`：获取失败时

#### close() -> None

**功能**：关闭浏览器，释放资源

### M3u8Parser 类

#### **init**(browser: BrowserDriver, max_retries: int = MAX_RETRY_COUNT)

**参数**：

- `browser`：浏览器实例
- `max_retries`：最大重试次数，默认为 5

**功能**：初始化 m3u8 解析器

#### fetch_m3u8_link(url: str) -> str

**参数**：

- `url`：钉钉直播回放分享链接

**返回值**：

- `str`：m3u8 链接

**功能**：从浏览器网络日志中提取 m3u8 链接

**异常**：

- `M3u8ParseError`：提取失败时

#### download_m3u8_file(url: str, filename: str, headers: dict) -> str

**参数**：

- `url`：m3u8 文件 URL
- `filename`：保存的文件名
- `headers`：请求头字典

**返回值**：

- `str`：m3u8 文件路径

**功能**：下载 m3u8 文件

**异常**：

- `M3u8ParseError`：下载失败时

#### extract_prefix(url: str) -> str

**参数**：

- `url`：m3u8 文件 URL

**返回值**：

- `str`：基础 URL

**功能**：提取基础 URL

### VideoDownloadManager 类

#### **init**(browser_type: str, save_mode: str)

**参数**：

- `browser_type`：浏览器类型（edge/chrome/firefox）
- `save_mode`：保存模式（1：默认路径，2：手动选择）

**功能**：初始化视频下载管理器

#### initialize_download(url: str) -> VideoDownloadContext

**参数**：

- `url`：钉钉直播回放分享链接

**返回值**：

- `VideoDownloadContext`：视频下载上下文

**功能**：初始化下载环境

#### repeat_get_context(url: str) -> VideoDownloadContext

**参数**：

- `url`：钉钉直播回放分享链接

**返回值**：

- `VideoDownloadContext`：视频下载上下文

**功能**：重复获取下载上下文

#### process_video(context: VideoDownloadContext) -> bool

**参数**：

- `context`：视频下载上下文

**返回值**：

- `bool`：下载成功返回 True，下载失败返回 False

**功能**：处理单个视频下载

**异常**：

- `DownloadError`：处理失败时

#### close() -> None

**功能**：关闭浏览器，释放资源

## 依赖关系

### 依赖的模块

1. `browser.browser_factory` - 浏览器工厂
2. `browser.*_driver` - 浏览器驱动
3. `binary.n_m3u8dl_re` - N_m3u8DL-RE 调用封装
4. `utils.path_helper` - 路径处理工具
5. `utils.path_selector` - 路径选择器
6. `utils.models` - 数据模型
7. `config.constants` - 常量定义
8. `config.yaml_config` - YAML 配置管理
9. `config.header_manager` - 请求头管理

### 被依赖的模块

1. `main` - 主程序入口

## 数据流程

### Cookie 获取流程

```text
创建浏览器实例
  ↓
导航到指定 URL
  ↓
等待用户登录
  ↓
获取 User-Agent 和 Referer
  ↓
构建请求头
  ↓
获取直播名称（多选择器策略）
  ↓
获取 Cookie
  ↓
返回浏览器实例、Cookie、请求头、直播名称
```

### m3u8 解析流程

```text
解析 URL 获取 liveUuid
  ↓
获取浏览器性能日志
  ↓
遍历日志查找包含 liveUuid 的 m3u8 链接
  ↓
如果未找到，刷新页面重试
  ↓
最多重试 MAX_RETRY_COUNT 次
  ↓
返回 m3u8 链接
```

### 视频下载流程

```text
获取 Cookie 和请求头
  ↓
创建 m3u8 解析器
  ↓
获取 m3u8 链接
  ↓
下载 m3u8 文件
  ↓
提取基础 URL
  ↓
选择保存路径
  ↓
调用 N_m3u8DL-RE 下载视频
  ↓
验证下载结果
  ↓
清理临时文件
```

## 设计模式应用

### 1. 外观模式（Facade Pattern）

**应用类**：Downloader

**说明**：Downloader 作为统一入口，隐藏了 VideoDownloadManager、CookieHandler、M3u8Parser 等子系统的复杂性，为客户端提供简单的接口。

### 2. 工厂模式（Factory Pattern）

**应用类**：BrowserFactory（在 browser 模块中）

**说明**：根据浏览器类型创建对应的浏览器实例。

### 3. 单例模式（Singleton Pattern）

**应用类**：YamlConfig（在 config 模块中）

**说明**：确保配置文件在应用生命周期内只被加载一次。

### 4. 策略模式（Strategy Pattern）

**应用类**：PathSelector

**说明**：根据不同的保存模式（默认路径/手动选择）采用不同的路径选择策略。

### 5. 值对象模式（Value Object Pattern）

**应用类**：CookieData、HeadersData、M3u8Link

**说明**：封装数据，提供类型安全和不可变性。

### 6. 数据传输对象（DTO）

**应用类**：VideoDownloadContext

**说明**：封装视频下载所需的所有上下文信息，在模块间传递。

## 异常处理

### 异常层次结构

```tree
Exception
  └── DownloadError (下载异常)
        ├── CookieError (Cookie 处理异常)
        ├── M3u8ParseError (m3u8 解析异常)
        └── FileReaderError (文件读取异常)
```

### 异常处理策略

1. **捕获并转换**：在底层捕获具体异常，转换为业务异常
2. **记录日志**：记录详细的错误信息和堆栈跟踪
3. **资源清理**：异常时自动关闭浏览器，释放资源
4. **用户友好**：向用户显示友好的错误信息

## 注意事项

### 1. 浏览器资源管理

- 使用完毕后必须调用 `close()` 方法
- 避免浏览器进程残留
- 使用上下文管理器（with 语句）自动管理资源

### 2. 重试机制

- m3u8 链接提取失败时会自动重试
- 最多重试 `MAX_RETRY_COUNT` 次
- 每次重试前会刷新页面

### 3. 异常处理

- 捕获所有异常并记录日志
- 异常时自动关闭浏览器
- 向用户显示友好的错误信息

### 4. 用户交互

- Cookie 获取时需要用户手动登录
- 支持继续下载新链接
- 支持批量下载

### 5. 日志记录

- 在关键步骤记录日志
- 异常时记录完整堆栈信息
- 使用不同日志级别（DEBUG、INFO、WARNING、ERROR）

### 6. 配置管理

- 使用 YamlConfig 单例模式
- 支持配置热重载
- 配置验证确保数据有效性

## 性能优化

### 1. 浏览器复用

- 批量下载时复用浏览器实例
- 减少浏览器启动开销

### 2. 请求头缓存

- HeaderManager 缓存请求头
- 避免重复构建

### 3. 临时文件管理

- 使用临时目录存储 m3u8 文件
- 下载完成后自动清理

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
- Mock 浏览器和网络请求

### 2. 集成测试

- 测试完整的下载流程
- 测试批量下载

### 3. 异常测试

- 测试各种异常情况
- 验证异常处理逻辑

## 维护责任人

- **主要维护者**：项目团队
- **最后更新日期**：2026-01-27

## 相关文档

- [主程序入口模块](../README.md)
- [浏览器驱动模块](../browser/README.md)
- [二进制工具封装模块](../binary/README.md)
- [工具模块](../utils/README.md)
- [配置模块](../config/README.md)
