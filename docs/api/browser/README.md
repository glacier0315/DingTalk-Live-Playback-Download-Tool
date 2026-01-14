# Browser 模块 API 文档

## 模块概述

Browser 模块是 DingTalk 直播回放下载工具的浏览器驱动模块，负责管理和操作浏览器实例。该模块包含以下核心组件：

- **BrowserFactory**: 浏览器工厂类，负责创建不同类型的浏览器实例
- **EdgeDriver**: Edge 浏览器驱动类，负责 Edge 浏览器的创建、配置和操作
- **ChromeDriver**: Chrome 浏览器驱动类，负责 Chrome 浏览器的创建、配置和操作
- **FirefoxDriver**: Firefox 浏览器驱动类，负责 Firefox 浏览器的创建、配置和操作

## 类文档

### BrowserFactory

浏览器工厂类，负责创建不同类型的浏览器实例。该类封装了 Edge、Chrome、Firefox 三种浏览器的创建逻辑，提供统一的接口供上层模块使用。

#### create_browser

创建浏览器实例，根据浏览器类型创建对应的浏览器实例。

```python
@staticmethod
def create_browser(browser_type: str) -> Union[EdgeDriver, ChromeDriver, FirefoxDriver]
```

**参数说明**：
- `browser_type` (str): 浏览器类型，可选值为 "edge"、"chrome"、"firefox"

**返回值**：
- `browser` (Union[EdgeDriver, ChromeDriver, FirefoxDriver]): 浏览器实例

**异常**：
- `ValueError`: 浏览器类型不支持时

**使用示例**：
```python
from dingtalk_downloader.browser.browser_factory import BrowserFactory

# 创建 Edge 浏览器
edge_browser = BrowserFactory.create_browser("edge")

# 创建 Chrome 浏览器
chrome_browser = BrowserFactory.create_browser("chrome")

# 创建 Firefox 浏览器
firefox_browser = BrowserFactory.create_browser("firefox")

# 不支持的浏览器类型
try:
    browser = BrowserFactory.create_browser("safari")
except ValueError as e:
    print(f"错误: {e}")
```

---

### EdgeDriver

Edge 浏览器驱动类，负责 Edge 浏览器的创建、配置和操作。

#### 初始化方法

```python
def __init__(self)
```

**参数说明**：无

**返回值**：无

**异常**：无

**使用示例**：
```python
from dingtalk_downloader.browser.edge_driver import EdgeDriver

edge_driver = EdgeDriver()
```

#### create_driver

创建 Edge 浏览器实例，配置 Edge 浏览器选项，包括禁用 USB 设备事件日志、忽略证书错误、禁用日志等。

```python
def create_driver(self) -> webdriver.Edge
```

**参数说明**：无

**返回值**：
- `driver` (webdriver.Edge): Edge 浏览器实例

**异常**：无

**使用示例**：
```python
from dingtalk_downloader.browser.edge_driver import EdgeDriver

edge_driver = EdgeDriver()
driver = edge_driver.create_driver()
driver.get("https://www.example.com")
edge_driver.close()
```

#### get_log

获取浏览器日志，获取指定类型的浏览器日志。

```python
def get_log(self, log_type: str) -> List[dict]
```

**参数说明**：
- `log_type` (str): 日志类型（如 "performance"）

**返回值**：
- `logs` (List[dict]): 日志列表

**异常**：无

**使用示例**：
```python
from dingtalk_downloader.browser.edge_driver import EdgeDriver

edge_driver = EdgeDriver()
driver = edge_driver.create_driver()
driver.get("https://www.example.com")

logs = edge_driver.get_log("performance")
for log in logs:
    print(log)

edge_driver.close()
```

#### get_element_by_xpath

通过 XPath 获取元素。

```python
def get_element_by_xpath(self, xpath: str)
```

**参数说明**：
- `xpath` (str): XPath 表达式

**返回值**：
- `element`: 元素对象

**异常**：无

**使用示例**：
```python
from dingtalk_downloader.browser.edge_driver import EdgeDriver

edge_driver = EdgeDriver()
driver = edge_driver.create_driver()
driver.get("https://www.example.com")

element = edge_driver.get_element_by_xpath("//h1")
print(element.text)

edge_driver.close()
```

#### get_element_by_class_name

通过类名获取元素。

```python
def get_element_by_class_name(self, class_name: str)
```

**参数说明**：
- `class_name` (str): 类名

**返回值**：
- `element`: 元素对象

**异常**：无

**使用示例**：
```python
from dingtalk_downloader.browser.edge_driver import EdgeDriver

edge_driver = EdgeDriver()
driver = edge_driver.create_driver()
driver.get("https://www.example.com")

element = edge_driver.get_element_by_class_name("title")
print(element.text)

edge_driver.close()
```

#### get_user_agent

获取 User-Agent，通过 JavaScript 获取 User-Agent。

```python
def get_user_agent(self) -> str
```

**参数说明**：无

**返回值**：
- `user_agent` (str): User-Agent 字符串

**异常**：无

**使用示例**：
```python
from dingtalk_downloader.browser.edge_driver import EdgeDriver

edge_driver = EdgeDriver()
driver = edge_driver.create_driver()
driver.get("https://www.example.com")

user_agent = edge_driver.get_user_agent()
print(f"User-Agent: {user_agent}")

edge_driver.close()
```

#### get_referer

获取 Referer，通过 JavaScript 获取 Referer。

```python
def get_referer(self) -> str
```

**参数说明**：无

**返回值**：
- `referer` (str): Referer 字符串

**异常**：无

**使用示例**：
```python
from dingtalk_downloader.browser.edge_driver import EdgeDriver

edge_driver = EdgeDriver()
driver = edge_driver.create_driver()
driver.get("https://www.example.com")

referer = edge_driver.get_referer()
print(f"Referer: {referer}")

edge_driver.close()
```

#### get_cookies

获取 Cookie，获取浏览器的所有 Cookie。

```python
def get_cookies(self) -> List[dict]
```

**参数说明**：无

**返回值**：
- `cookies` (List[dict]): Cookie 列表

**异常**：无

**使用示例**：
```python
from dingtalk_downloader.browser.edge_driver import EdgeDriver

edge_driver = EdgeDriver()
driver = edge_driver.create_driver()
driver.get("https://www.example.com")

cookies = edge_driver.get_cookies()
for cookie in cookies:
    print(f"{cookie['name']}: {cookie['value']}")

edge_driver.close()
```

#### navigate

导航到指定 URL。

```python
def navigate(self, url: str) -> None
```

**参数说明**：
- `url` (str): 目标 URL

**返回值**：无

**异常**：无

**使用示例**：
```python
from dingtalk_downloader.browser.edge_driver import EdgeDriver

edge_driver = EdgeDriver()
driver = edge_driver.create_driver()

edge_driver.navigate("https://www.example.com")
edge_driver.navigate("https://www.google.com")

edge_driver.close()
```

#### wait_for_video

等待视频加载，等待视频元素加载完成。

```python
def wait_for_video(self, timeout: int = 20) -> None
```

**参数说明**：
- `timeout` (int): 超时时间（秒），默认为 20

**返回值**：无

**异常**：无

**使用示例**：
```python
from dingtalk_downloader.browser.edge_driver import EdgeDriver

edge_driver = EdgeDriver()
driver = edge_driver.create_driver()
driver.get("https://www.example.com/video")

edge_driver.wait_for_video(timeout=30)
print("视频加载完成")

edge_driver.close()
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
from dingtalk_downloader.browser.edge_driver import EdgeDriver

edge_driver = EdgeDriver()
driver = edge_driver.create_driver()
driver.get("https://www.example.com")

edge_driver.close()
```

---

### ChromeDriver

Chrome 浏览器驱动类，负责 Chrome 浏览器的创建、配置和操作。

ChromeDriver 的所有方法与 EdgeDriver 相同，包括：
- `create_driver()`: 创建 Chrome 浏览器实例
- `get_log(log_type: str)`: 获取浏览器日志
- `get_element_by_xpath(xpath: str)`: 通过 XPath 获取元素
- `get_element_by_class_name(class_name: str)`: 通过类名获取元素
- `get_user_agent()`: 获取 User-Agent
- `get_referer()`: 获取 Referer
- `get_cookies()`: 获取 Cookie
- `navigate(url: str)`: 导航到指定 URL
- `wait_for_video(timeout: int = 20)`: 等待视频加载
- `close()`: 关闭浏览器

**使用示例**：
```python
from dingtalk_downloader.browser.chrome_driver import ChromeDriver

chrome_driver = ChromeDriver()
driver = chrome_driver.create_driver()
driver.get("https://www.example.com")

user_agent = chrome_driver.get_user_agent()
cookies = chrome_driver.get_cookies()

chrome_driver.close()
```

---

### FirefoxDriver

Firefox 浏览器驱动类，负责 Firefox 浏览器的创建、配置和操作。

FirefoxDriver 的所有方法与 EdgeDriver 相同，包括：
- `create_driver()`: 创建 Firefox 浏览器实例
- `get_log(log_type: str)`: 获取浏览器日志
- `get_element_by_xpath(xpath: str)`: 通过 XPath 获取元素
- `get_element_by_class_name(class_name: str)`: 通过类名获取元素
- `get_user_agent()`: 获取 User-Agent
- `get_referer()`: 获取 Referer
- `get_cookies()`: 获取 Cookie
- `navigate(url: str)`: 导航到指定 URL
- `wait_for_video(timeout: int = 20)`: 等待视频加载
- `close()`: 关闭浏览器

**使用示例**：
```python
from dingtalk_downloader.browser.firefox_driver import FirefoxDriver

firefox_driver = FirefoxDriver()
driver = firefox_driver.create_driver()
driver.get("https://www.example.com")

user_agent = firefox_driver.get_user_agent()
cookies = firefox_driver.get_cookies()

firefox_driver.close()
```

## 使用流程

### 使用浏览器工厂创建浏览器

```python
from dingtalk_downloader.browser.browser_factory import BrowserFactory

# 创建 Edge 浏览器
edge_browser = BrowserFactory.create_browser("edge")
driver = edge_browser.create_driver()
driver.get("https://www.example.com")
edge_browser.close()

# 创建 Chrome 浏览器
chrome_browser = BrowserFactory.create_browser("chrome")
driver = chrome_browser.create_driver()
driver.get("https://www.example.com")
chrome_browser.close()

# 创建 Firefox 浏览器
firefox_browser = BrowserFactory.create_browser("firefox")
driver = firefox_browser.create_driver()
driver.get("https://www.example.com")
firefox_browser.close()
```

### 使用浏览器驱动获取信息

```python
from dingtalk_downloader.browser.edge_driver import EdgeDriver

edge_driver = EdgeDriver()
driver = edge_driver.create_driver()
driver.get("https://www.example.com")

# 获取 User-Agent
user_agent = edge_driver.get_user_agent()
print(f"User-Agent: {user_agent}")

# 获取 Referer
referer = edge_driver.get_referer()
print(f"Referer: {referer}")

# 获取 Cookie
cookies = edge_driver.get_cookies()
for cookie in cookies:
    print(f"{cookie['name']}: {cookie['value']}")

# 获取页面元素
element = edge_driver.get_element_by_xpath("//h1")
print(f"标题: {element.text}")

edge_driver.close()
```

### 使用浏览器驱动等待视频加载

```python
from dingtalk_downloader.browser.chrome_driver import ChromeDriver

chrome_driver = ChromeDriver()
driver = chrome_driver.create_driver()
driver.get("https://www.example.com/video")

# 等待视频加载
chrome_driver.wait_for_video(timeout=30)
print("视频加载完成")

chrome_driver.close()
```

### 使用浏览器驱动获取网络日志

```python
from dingtalk_downloader.browser.firefox_driver import FirefoxDriver

firefox_driver = FirefoxDriver()
driver = firefox_driver.create_driver()
driver.get("https://www.example.com")

# 获取网络日志
logs = firefox_driver.get_log("performance")
for log in logs:
    print(log)

firefox_driver.close()
```

## 异常处理

### 常见异常

1. **浏览器驱动未找到**
   - 原因：浏览器驱动未安装或版本不匹配
   - 解决：安装对应版本的浏览器驱动

2. **浏览器未启动**
   - 原因：浏览器实例未创建或已关闭
   - 解决：确保已调用 create_driver() 方法

3. **元素未找到**
   - 原因：XPath 或类名错误，或元素未加载
   - 解决：检查 XPath 或类名，确保元素已加载

4. **视频加载超时**
   - 原因：视频加载时间超过超时时间
   - 解决：增加超时时间或检查网络连接

5. **不支持的浏览器类型**
   - 原因：浏览器类型不在支持列表中
   - 解决：使用支持的浏览器类型（edge、chrome、firefox）

### 异常处理示例

```python
from dingtalk_downloader.browser.edge_driver import EdgeDriver

edge_driver = EdgeDriver()

try:
    driver = edge_driver.create_driver()
    driver.get("https://www.example.com")
    
    # 获取元素
    element = edge_driver.get_element_by_xpath("//h1")
    print(element.text)
    
except Exception as e:
    if "驱动" in str(e):
        print("浏览器驱动未找到，请安装 EdgeDriver")
    elif "元素" in str(e):
        print("元素未找到，请检查 XPath")
    else:
        print(f"发生错误: {e}")
finally:
    edge_driver.close()
```

## 注意事项

1. **浏览器驱动**：确保已安装对应版本的浏览器驱动（EdgeDriver、ChromeDriver、GeckoDriver）
2. **资源释放**：使用完毕后务必调用 `close()` 方法释放浏览器资源
3. **元素定位**：使用 XPath 或类名定位元素时，确保元素已加载
4. **视频等待**：等待视频加载时，根据实际情况调整超时时间
5. **网络日志**：Firefox 的网络日志获取方式与 Edge 和 Chrome 不同
6. **浏览器选项**：所有浏览器驱动都配置了相同的选项，包括禁用日志、忽略证书错误等
7. **跨平台支持**：模块支持 Windows、Linux、macOS 操作系统
8. **浏览器版本**：建议使用最新版本的浏览器和浏览器驱动
