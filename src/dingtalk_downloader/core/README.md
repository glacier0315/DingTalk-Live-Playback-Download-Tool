# 核心业务模块

## 模块概述

本模块是钉钉直播回放下载工具的核心业务逻辑层，负责协调 Cookie 获取、m3u8 解析、视频下载等核心功能，是整个下载流程的协调者。

## 功能描述

### CookieHandler - Cookie 处理模块

**功能**：
- 通过 Selenium 自动化浏览器获取登录后的 Cookie
- 获取请求头信息（User-Agent、Referer 等）
- 获取直播视频名称
- 支持重复获取 Cookie（复用浏览器实例）

### M3u8Parser - m3u8 解析模块

**功能**：
- 从浏览器网络日志中提取 m3u8 链接
- 下载 m3u8 文件
- 提取基础 URL（prefix）
- 支持重试机制
- 支持 Edge、Chrome、Firefox 三种浏览器

### Downloader - 下载器核心模块

**功能**：
- 协调 Cookie 获取、m3u8 解析、视频下载
- 支持单个视频下载
- 支持批量视频下载
- 管理保存路径（默认/手动选择）
- 管理浏览器资源

## 核心实现原理

### CookieHandler 实现原理

#### Cookie 获取流程

```
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
获取直播名称
  ↓
获取 Cookie
  ↓
返回浏览器实例、Cookie、请求头、直播名称
```

#### 直播名称获取

```python
def _get_live_name(self) -> str:
    try:
        # 尝试通过 XPath 获取
        live_name = self.browser.get_element_by_xpath(
            '//*[@id="live-room"]/div[1]/div[1]/h3'
        ).text
        return live_name
    except Exception as e:
        try:
            # 尝试通过 CSS Selector 获取
            live_name = self.browser.get_element_by_class_name("vwi5-oG8").text
            return live_name
        except Exception as e:
            return "直播视频名称不可获取"
```

#### 请求头构建

```python
headers = {
    "User-Agent": user_agent,
    "Referer": referer,
    "Accept": "application/vnd.apple.mpegurl, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}
```

### M3u8Parser 实现原理

#### m3u8 链接提取流程

```
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
返回 m3u8 链接列表
```

#### m3u8 链接提取（Edge/Chrome）

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
            return m3u8_links
```

#### m3u8 链接提取（Firefox）

```python
pattern = r'https://[^,\'"]+\.m3u8\?[^\'"]+'
found_links = re.findall(pattern, log_message)

if found_links:
    cleaned_link = re.sub(r'[\]\s\\\'"]+$', "", found_links[0])
    m3u8_links.append(cleaned_link)
    return m3u8_links
```

#### m3u8 文件下载

```python
m3u8_content = self.browser.driver.execute_script(
    "return fetch(arguments[0], { method: 'GET' }).then(response => response.text())",
    url,
)

with open(filename, "w", encoding="utf-8") as f:
    f.write(m3u8_content)
```

#### 基础 URL 提取

```python
pattern = re.compile(r"(https?://[^/]+/live_hp/[0-9a-f-]+)")
match = pattern.search(url)
return match.group(1) if match else url
```

### Downloader 实现原理

#### 单个视频下载流程

```
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
调用 N_m3u8DL-RE 下载视频
  ↓
询问是否继续下载
```

#### 批量视频下载流程

```
获取第一个链接的 Cookie 和请求头
  ↓
创建 m3u8 解析器
  ↓
下载第一个视频
  ↓
遍历剩余链接
  ↓
重复获取 Cookie 和请求头
  ↓
下载视频
  ↓
询问是否继续下载
```

#### 保存路径选择

```python
if self.save_mode == SAVE_MODE_DEFAULT:
    save_dir = self._get_default_download_dir()
elif self.save_mode == SAVE_MODE_MANUAL:
    save_dir = self._get_manual_download_dir()
```

#### 默认下载目录

```python
def _get_default_download_dir(self) -> str:
    base_dir = os.getcwd()
    downloads_dir = os.path.join(base_dir, DEFAULT_DOWNLOAD_DIR)
    ensure_dir_exists(downloads_dir)
    return downloads_dir
```

#### 手动选择目录

```python
def _get_manual_download_dir(self) -> Optional[str]:
    root = tk.Tk()
    root.withdraw()
    save_dir = filedialog.askdirectory(title="选择保存视频的目录")
    root.destroy()
    return save_dir
```

## 使用方法

### CookieHandler 使用示例

```python
from dingtalk_downloader.core.cookie_handler import CookieHandler
from dingtalk_downloader.config.constants import BROWSER_TYPE_EDGE

# 创建 Cookie 处理器
cookie_handler = CookieHandler(BROWSER_TYPE_EDGE)

# 获取 Cookie 和请求头
browser, cookies, headers, live_name = cookie_handler.get_cookie(
    "https://n.dingtalk.com/xxx"
)

print(f"直播名称: {live_name}")
print(f"Cookie 数量: {len(cookies)}")

# 重复获取 Cookie（复用浏览器实例）
cookies, headers, live_name = cookie_handler.repeat_get_cookie(
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
parser = M3u8Parser(browser, BROWSER_TYPE_EDGE)

# 获取 m3u8 链接
m3u8_links = parser.fetch_m3u8_links("https://n.dingtalk.com/xxx")

if m3u8_links:
    print(f"获取到 {len(m3u8_links)} 个 m3u8 链接")

    # 下载 m3u8 文件
    m3u8_file = parser.download_m3u8_file(
        m3u8_links[0],
        "output.m3u8",
        headers
    )

    # 提取基础 URL
    prefix = parser.extract_prefix(m3u8_links[0])
    print(f"基础 URL: {prefix}")
```

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

## 接口参数说明

### CookieHandler 类

#### __init__(browser_type: str)

**参数**：
- `browser_type`：浏览器类型（edge/chrome/firefox）

**功能**：初始化 Cookie 处理器

#### get_cookie(url: str) -> Tuple[Union[EdgeDriver, ChromeDriver, FirefoxDriver], Dict[str, str], Dict[str, str], str]

**参数**：
- `url`：钉钉直播回放分享链接

**返回值**：
- `Tuple`：包含四个元素的元组
  - `browser`：浏览器实例
  - `cookie_dict`：Cookie 字典
  - `headers`：请求头字典
  - `live_name`：直播视频名称

**功能**：获取 Cookie 和请求头信息

#### repeat_get_cookie(url: str) -> Tuple[Dict[str, str], Dict[str, str], str]

**参数**：
- `url`：钉钉直播回放分享链接

**返回值**：
- `Tuple`：包含三个元素的元组
  - `cookie_dict`：Cookie 字典
  - `headers`：请求头字典
  - `live_name`：直播视频名称

**功能**：重复获取 Cookie 和请求头信息

#### close() -> None

**参数**：无

**返回值**：无

**功能**：关闭浏览器，释放资源

### M3u8Parser 类

#### __init__(browser: Union[EdgeDriver, ChromeDriver, FirefoxDriver], browser_type: str, max_retries: int = MAX_RETRY_COUNT)

**参数**：
- `browser`：浏览器实例
- `browser_type`：浏览器类型（edge/chrome/firefox）
- `max_retries`：最大重试次数，默认为 5

**功能**：初始化 m3u8 解析器

#### fetch_m3u8_links(url: str) -> Optional[List[str]]

**参数**：
- `url`：钉钉直播回放分享链接

**返回值**：
- `Optional[List[str]]`：m3u8 链接列表，如果提取失败则返回 None

**功能**：从浏览器网络日志中提取 m3u8 链接

#### download_m3u8_file(url: str, filename: str, headers: dict) -> str

**参数**：
- `url`：m3u8 文件 URL
- `filename`：保存的文件名
- `headers`：请求头字典

**返回值**：
- `str`：m3u8 文件路径

**功能**：下载 m3u8 文件

#### extract_prefix(url: str) -> str

**参数**：
- `url`：m3u8 文件 URL

**返回值**：
- `str`：基础 URL

**功能**：提取基础 URL

### Downloader 类

#### __init__(browser_type: str, save_mode: str)

**参数**：
- `browser_type`：浏览器类型（edge/chrome/firefox）
- `save_mode`：保存模式（1：默认路径，2：手动选择）

**功能**：初始化下载器

#### download_single_video(url: str) -> None

**参数**：
- `url`：钉钉直播回放分享链接

**返回值**：无

**功能**：下载单个视频

#### download_batch_videos(urls: Dict[int, str]) -> None

**参数**：
- `urls`：链接字典 {index: url}

**返回值**：无

**功能**：批量下载视频

#### close() -> None

**参数**：无

**返回值**：无

**功能**：关闭浏览器，释放资源

## 依赖关系

### 依赖的模块

1. `browser.browser_factory` - 浏览器工厂
2. `browser.*_driver` - 浏览器驱动
3. `binary.n_m3u8dl_re` - N_m3u8DL-RE 调用封装
4. `utils.path_helper` - 路径处理工具
5. `config.constants` - 常量定义

### 被依赖的模块

1. `main` - 主程序入口

## 数据流程

### Cookie 获取流程

```
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
获取直播名称
  ↓
获取 Cookie
  ↓
返回浏览器实例、Cookie、请求头、直播名称
```

### m3u8 解析流程

```
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
返回 m3u8 链接列表
```

### 视频下载流程

```
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
调用 N_m3u8DL-RE 下载视频
  ↓
询问是否继续下载
```

## 注意事项

1. **浏览器资源管理**
   - 使用完毕后必须调用 `close()` 方法
   - 避免浏览器进程残留

2. **重试机制**
   - m3u8 链接提取失败时会自动重试
   - 最多重试 `MAX_RETRY_COUNT` 次

3. **异常处理**
   - 捕获所有异常并记录日志
   - 异常时自动关闭浏览器

4. **用户交互**
   - Cookie 获取时需要用户手动登录
   - 支持继续下载新链接

5. **日志记录**
   - 在关键步骤记录日志
   - 异常时记录完整堆栈信息

## 扩展方向

1. **断点续传**
   - 支持下载中断后继续下载

2. **下载队列管理**
   - 添加下载队列，支持暂停、恢复、取消等操作

3. **进度显示**
   - 添加下载进度条和实时速度显示

4. **多线程下载**
   - 支持多线程下载提高速度

5. **下载历史记录**
   - 记录下载历史，支持重新下载

## 相关文档

- [主程序入口模块](../README.md)
- [浏览器驱动模块](../browser/README.md)
- [二进制工具封装模块](../binary/README.md)
- [工具模块](../utils/README.md)
