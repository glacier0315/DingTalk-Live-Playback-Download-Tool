# Core 模块 API 文档

## 模块概述

Core 模块是 DingTalk 直播回放下载工具的核心功能模块，负责协调和管理视频下载的主要流程。该模块包含以下核心组件：

- **Downloader**: 下载器类，负责协调 Cookie 获取、m3u8 解析、视频下载
- **CookieHandler**: Cookie 处理类，负责获取和管理 Cookie
- **M3u8Parser**: m3u8 解析类，负责提取 m3u8 链接和基础 URL

## 类文档

### Downloader

下载器类，负责协调 Cookie 获取、m3u8 解析、视频下载。该类封装了单个视频下载和批量下载的逻辑。

#### 初始化方法

```python
def __init__(self, browser_type: str, save_mode: str)
```

**参数说明**：
- `browser_type` (str): 浏览器类型，可选值为 "edge"、"chrome"、"firefox"
- `save_mode` (str): 保存模式，可选值为 "1"（默认路径）或 "2"（手动选择）

**返回值**：无

**异常**：无

**使用示例**：
```python
downloader = Downloader(browser_type="edge", save_mode="1")
```

#### download_single_video

下载单个视频，协调 Cookie 获取、m3u8 解析、视频下载。

```python
def download_single_video(self, url: str) -> None
```

**参数说明**：
- `url` (str): 钉钉直播回放分享链接

**返回值**：无

**异常**：
- `Exception`: 下载失败时抛出异常

**使用示例**：
```python
downloader = Downloader(browser_type="edge", save_mode="1")
downloader.download_single_video("https://live.dingtalk.com/xxx")
```

#### download_videos

批量下载视频，从文件中读取 URL 列表并逐个下载。

```python
def download_videos(self, file_path: str) -> None
```

**参数说明**：
- `file_path` (str): 包含 URL 列表的文件路径

**返回值**：无

**异常**：
- `Exception`: 下载失败时抛出异常

**使用示例**：
```python
downloader = Downloader(browser_type="edge", save_mode="1")
downloader.download_videos("urls.txt")
```

#### close

关闭浏览器，释放资源。

```python
def close(self) -> None
```

**参数说明**：无

**返回值**：无

**异常**：无

**使用示例**：
```python
downloader.close()
```

---

### CookieHandler

Cookie 处理类，负责获取和管理 Cookie。该类封装了 Cookie 获取、请求头获取、直播名称获取的逻辑。

#### 初始化方法

```python
def __init__(self, browser_type: str)
```

**参数说明**：
- `browser_type` (str): 浏览器类型，可选值为 "edge"、"chrome"、"firefox"

**返回值**：无

**异常**：无

**使用示例**：
```python
cookie_handler = CookieHandler(browser_type="edge")
```

#### get_cookie

获取 Cookie 和请求头信息。通过 Selenium 自动化浏览器访问指定 URL，获取登录后的 Cookie 和请求头信息。

```python
def get_cookie(self, url: str) -> Tuple[Union[EdgeDriver, ChromeDriver, FirefoxDriver], Dict[str, str], Dict[str, str], str]
```

**参数说明**：
- `url` (str): 钉钉直播回放分享链接

**返回值**：
返回一个包含四个元素的元组：
- `browser`: 浏览器实例（EdgeDriver、ChromeDriver 或 FirefoxDriver）
- `cookie_dict`: Cookie 字典，格式为 `{cookie_name: cookie_value}`
- `headers`: 请求头字典，包含 User-Agent、Referer 等
- `live_name`: 直播视频名称

**异常**：
- `Exception`: 获取失败时抛出异常

**使用示例**：
```python
cookie_handler = CookieHandler(browser_type="edge")
browser, cookies, headers, live_name = cookie_handler.get_cookie("https://live.dingtalk.com/xxx")
```

#### get_headers

获取请求头信息。

```python
def get_headers(self) -> Dict[str, str]
```

**参数说明**：无

**返回值**：
- `headers` (Dict[str, str]): 请求头字典，包含 User-Agent、Referer 等

**异常**：无

**使用示例**：
```python
headers = cookie_handler.get_headers()
```

#### get_live_name

获取直播视频名称。

```python
def get_live_name(self) -> str
```

**参数说明**：无

**返回值**：
- `live_name` (str): 直播视频名称

**异常**：无

**使用示例**：
```python
live_name = cookie_handler.get_live_name()
```

#### close

关闭浏览器，释放资源。

```python
def close(self) -> None
```

**参数说明**：无

**返回值**：无

**异常**：无

**使用示例**：
```python
cookie_handler.close()
```

---

### M3u8Parser

m3u8 解析类，负责提取 m3u8 链接和基础 URL。该类封装了从浏览器网络日志中提取 m3u8 链接的逻辑，支持 Edge、Chrome、Firefox 三种浏览器。

#### 初始化方法

```python
def __init__(self, browser: Union[EdgeDriver, ChromeDriver, FirefoxDriver], browser_type: str, max_retries: int = MAX_RETRY_COUNT)
```

**参数说明**：
- `browser` (Union[EdgeDriver, ChromeDriver, FirefoxDriver]): 浏览器实例
- `browser_type` (str): 浏览器类型，可选值为 "edge"、"chrome"、"firefox"
- `max_retries` (int): 最大重试次数，默认为 5

**返回值**：无

**异常**：无

**使用示例**：
```python
from selenium.webdriver.edge import EdgeDriver
browser = EdgeDriver()
parser = M3u8Parser(browser, browser_type="edge", max_retries=5)
```

#### fetch_m3u8_links

从浏览器网络日志中提取 m3u8 链接。从用户输入的 URL 中提取 liveUuid，然后从浏览器网络日志中提取包含 liveUuid 的 m3u8 链接。

```python
def fetch_m3u8_links(self, url: str) -> Optional[List[str]]
```

**参数说明**：
- `url` (str): 钉钉直播回放分享链接

**返回值**：
- `m3u8_links` (Optional[List[str]]): m3u8 链接列表，如果提取失败则返回 None

**异常**：
- `Exception`: 提取失败时抛出异常

**使用示例**：
```python
from selenium.webdriver.edge import EdgeDriver
browser = EdgeDriver()
parser = M3u8Parser(browser, browser_type="edge")
m3u8_links = parser.fetch_m3u8_links("https://live.dingtalk.com/xxx")
if m3u8_links:
    print(f"找到 {len(m3u8_links)} 个 m3u8 链接")
```

#### get_base_url

从 m3u8 链接中提取基础 URL。

```python
def get_base_url(self, m3u8_url: str) -> str
```

**参数说明**：
- `m3u8_url` (str): m3u8 链接

**返回值**：
- `base_url` (str): 基础 URL

**异常**：无

**使用示例**：
```python
base_url = parser.get_base_url("https://example.com/path/to/video.m3u8")
print(base_url)  # 输出: https://example.com/path/to/
```

## 使用流程

### 单个视频下载流程

```python
from dingtalk_downloader.core.downloader import Downloader

# 创建下载器实例
downloader = Downloader(browser_type="edge", save_mode="1")

# 下载单个视频
try:
    downloader.download_single_video("https://live.dingtalk.com/xxx")
    print("下载成功")
except Exception as e:
    print(f"下载失败: {e}")
finally:
    downloader.close()
```

### 批量视频下载流程

```python
from dingtalk_downloader.core.downloader import Downloader

# 创建下载器实例
downloader = Downloader(browser_type="edge", save_mode="1")

# 批量下载视频
try:
    downloader.download_videos("urls.txt")
    print("批量下载完成")
except Exception as e:
    print(f"批量下载失败: {e}")
finally:
    downloader.close()
```

### 自定义 Cookie 获取流程

```python
from dingtalk_downloader.core.cookie_handler import CookieHandler
from dingtalk_downloader.core.m3u8_parser import M3u8Parser

# 创建 Cookie 处理器
cookie_handler = CookieHandler(browser_type="edge")

# 获取 Cookie 和请求头
try:
    browser, cookies, headers, live_name = cookie_handler.get_cookie("https://live.dingtalk.com/xxx")
    print(f"直播名称: {live_name}")
    print(f"Cookie 数量: {len(cookies)}")
    print(f"请求头: {headers}")
    
    # 创建 m3u8 解析器
    parser = M3u8Parser(browser, browser_type="edge")
    m3u8_links = parser.fetch_m3u8_links("https://live.dingtalk.com/xxx")
    if m3u8_links:
        print(f"找到 {len(m3u8_links)} 个 m3u8 链接")
except Exception as e:
    print(f"获取失败: {e}")
finally:
    cookie_handler.close()
```

## 异常处理

### 常见异常

1. **浏览器启动失败**
   - 原因：浏览器驱动未安装或版本不匹配
   - 解决：安装对应版本的浏览器驱动

2. **Cookie 获取失败**
   - 原因：用户未登录或网络问题
   - 解决：确保用户已登录钉钉，检查网络连接

3. **m3u8 链接提取失败**
   - 原因：网络日志中未找到 m3u8 链接
   - 解决：检查 URL 是否正确，等待页面加载完成

4. **视频下载失败**
   - 原因：N_m3u8DL-RE 工具未安装或配置错误
   - 解决：安装 N_m3u8DL-RE 工具，检查配置

### 异常处理示例

```python
from dingtalk_downloader.core.downloader import Downloader

downloader = Downloader(browser_type="edge", save_mode="1")

try:
    downloader.download_single_video("https://live.dingtalk.com/xxx")
except Exception as e:
    if "浏览器" in str(e):
        print("浏览器启动失败，请检查浏览器驱动")
    elif "Cookie" in str(e):
        print("Cookie 获取失败，请确保已登录钉钉")
    elif "m3u8" in str(e):
        print("m3u8 链接提取失败，请检查 URL 是否正确")
    else:
        print(f"下载失败: {e}")
finally:
    downloader.close()
```

## 注意事项

1. **浏览器驱动**：确保已安装对应版本的浏览器驱动（EdgeDriver、ChromeDriver、GeckoDriver）
2. **登录状态**：使用前请确保已在浏览器中登录钉钉账号
3. **网络连接**：确保网络连接正常，能够访问钉钉直播回放页面
4. **N_m3u8DL-RE 工具**：确保已安装 N_m3u8DL-RE 工具并配置到系统 PATH
5. **资源释放**：使用完毕后务必调用 `close()` 方法释放浏览器资源
6. **重试机制**：m3u8 链接提取支持重试机制，默认最大重试次数为 5 次
