# 浏览器驱动模块

## 模块概述

本模块负责封装 Selenium 浏览器驱动，提供统一的浏览器操作接口，支持 Edge、Chrome、Firefox 三种主流浏览器，用于自动化操作浏览器以获取 Cookie、请求头和页面元素。

## 功能描述

### BrowserFactory - 浏览器工厂类

**功能**：
- 统一浏览器创建逻辑
- 根据浏览器类型创建对应的浏览器实例
- 提供工厂方法模式

### EdgeDriver - Edge 浏览器驱动类

**功能**：
- 创建和配置 Edge 浏览器实例
- 提供浏览器操作方法（导航、获取元素、获取 Cookie 等）
- 获取浏览器性能日志

### ChromeDriver - Chrome 浏览器驱动类

**功能**：
- 创建和配置 Chrome 浏览器实例
- 提供浏览器操作方法（导航、获取元素、获取 Cookie 等）
- 获取浏览器性能日志

### FirefoxDriver - Firefox 浏览器驱动类

**功能**：
- 创建和配置 Firefox 浏览器实例
- 提供浏览器操作方法（导航、获取元素、获取 Cookie 等）
- 获取浏览器性能日志

## 核心实现原理

### 浏览器配置

#### Edge 浏览器配置

```python
edge_options = EdgeOptions()
edge_options.add_argument("--disable-usb-device-event-log")
edge_options.add_argument("--ignore-certificate-errors")
edge_options.add_argument("--disable-logging")
edge_options.add_argument("--disable_ssl_verification")
edge_options.add_argument("--log-level=3")
edge_options.add_experimental_option("excludeSwitches", ["enable-logging"])
edge_options.set_capability("ms:loggingPrefs", {"performance": "ALL"})
```

#### Chrome 浏览器配置

```python
chrome_options = ChromeOptions()
chrome_options.add_argument("--disable-usb-device-event-log")
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--disable-logging")
chrome_options.add_argument("--log-level=3")
chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
```

#### Firefox 浏览器配置

```python
firefox_options = FirefoxOptions()
firefox_options.add_argument("--disable-usb-device-event-log")
firefox_options.add_argument("--ignore-certificate-errors")
firefox_options.add_argument("--disable-logging")
firefox_options.add_argument("--log-level=3")
firefox_options.set_capability(
    "moz:firefoxOptions",
    {
        "log": {
            "level": "ALL",
            "browser": "ALL",
        }
    },
)
```

### 性能日志获取

#### Edge/Chrome 日志获取

```python
logs = self.driver.get_log("performance")
```

#### Firefox 日志获取

```python
logs = self.driver.execute_script(
    """
    var performance = window.performance || window.mozPerformance || window.msPerformance || window.webkitPerformance || {};
    var network = performance.getEntries() || {};
    return network;
    """
)
```

### 元素获取

#### 通过 XPath 获取元素

```python
element = self.driver.find_element(By.XPATH, xpath)
```

#### 通过类名获取元素

```python
element = self.driver.find_element(By.CLASS_NAME, class_name)
```

### JavaScript 执行

#### 获取 User-Agent

```python
user_agent = self.driver.execute_script("return navigator.userAgent")
```

#### 获取 Referer

```python
referer = self.driver.execute_script("return document.referrer")
```

### 等待视频加载

```python
WebDriverWait(self.driver, timeout).until(
    lambda driver: driver.execute_script(
        "return isNaN(document.querySelector('video')?.duration)"
    )
    == False
)
```

## 使用方法

### BrowserFactory 使用示例

```python
from dingtalk_downloader.browser.browser_factory import BrowserFactory
from dingtalk_downloader.config.constants import BROWSER_TYPE_EDGE

# 创建 Edge 浏览器实例
browser = BrowserFactory.create_browser(BROWSER_TYPE_EDGE)

# 创建浏览器驱动
driver = browser.create_driver()

# 导航到指定 URL
browser.navigate("https://n.dingtalk.com/")

# 获取 Cookie
cookies = browser.get_cookies()

# 关闭浏览器
browser.close()
```

### EdgeDriver 使用示例

```python
from dingtalk_downloader.browser.edge_driver import EdgeDriver

# 创建 Edge 浏览器驱动
edge_driver = EdgeDriver()

# 创建浏览器实例
driver = edge_driver.create_driver()

# 导航到指定 URL
edge_driver.navigate("https://n.dingtalk.com/")

# 获取 User-Agent
user_agent = edge_driver.get_user_agent()

# 获取 Referer
referer = edge_driver.get_referer()

# 获取 Cookie
cookies = edge_driver.get_cookies()

# 通过 XPath 获取元素
element = edge_driver.get_element_by_xpath('//*[@id="live-room"]/div[1]/div[1]/h3')

# 通过类名获取元素
element = edge_driver.get_element_by_class_name("vwi5-oG8")

# 等待视频加载
edge_driver.wait_for_video(timeout=20)

# 获取性能日志
logs = edge_driver.get_log("performance")

# 关闭浏览器
edge_driver.close()
```

### ChromeDriver 使用示例

```python
from dingtalk_downloader.browser.chrome_driver import ChromeDriver

# 创建 Chrome 浏览器驱动
chrome_driver = ChromeDriver()

# 创建浏览器实例
driver = chrome_driver.create_driver()

# 使用方法与 EdgeDriver 相同
```

### FirefoxDriver 使用示例

```python
from dingtalk_downloader.browser.firefox_driver import FirefoxDriver

# 创建 Firefox 浏览器驱动
firefox_driver = FirefoxDriver()

# 创建浏览器实例
driver = firefox_driver.create_driver()

# 使用方法与 EdgeDriver 相同
```

## 接口参数说明

### BrowserFactory 类

#### create_browser(browser_type: str) -> Union[EdgeDriver, ChromeDriver, FirefoxDriver]

**参数**：
- `browser_type`：浏览器类型（edge/chrome/firefox）

**返回值**：
- `Union[EdgeDriver, ChromeDriver, FirefoxDriver]`：浏览器实例

**功能**：创建浏览器实例

**异常**：
- `ValueError`：浏览器类型不支持时

### EdgeDriver/ChromeDriver/FirefoxDriver 类

#### __init__()

**参数**：无

**功能**：初始化浏览器驱动

#### create_driver() -> webdriver.Edge/Chrome/Firefox

**参数**：无

**返回值**：
- `webdriver.Edge/Chrome/Firefox`：浏览器实例

**功能**：创建浏览器实例

#### get_log(log_type: str) -> List[dict]

**参数**：
- `log_type`：日志类型（如 "performance"）

**返回值**：
- `List[dict]`：日志列表

**功能**：获取浏览器日志

#### get_element_by_xpath(xpath: str)

**参数**：
- `xpath`：XPath 表达式

**返回值**：
- 元素对象

**功能**：通过 XPath 获取元素

#### get_element_by_class_name(class_name: str)

**参数**：
- `class_name`：类名

**返回值**：
- 元素对象

**功能**：通过类名获取元素

#### get_user_agent() -> str

**参数**：无

**返回值**：
- `str`：User-Agent 字符串

**功能**：获取 User-Agent

#### get_referer() -> str

**参数**：无

**返回值**：
- `str`：Referer 字符串

**功能**：获取 Referer

#### get_cookies() -> List[dict]

**参数**：无

**返回值**：
- `List[dict]`：Cookie 列表

**功能**：获取 Cookie

#### navigate(url: str) -> None

**参数**：
- `url`：目标 URL

**返回值**：无

**功能**：导航到指定 URL

#### wait_for_video(timeout: int = 20) -> None

**参数**：
- `timeout`：超时时间（秒），默认为 20

**返回值**：无

**功能**：等待视频加载

#### close() -> None

**参数**：无

**返回值**：无

**功能**：关闭浏览器，释放资源

## 依赖关系

### 依赖的外部库

1. **selenium**
   - 浏览器自动化框架
   - 用于控制浏览器

### 依赖的 Python 模块

1. `selenium.webdriver` - WebDriver 驱动
2. `selenium.webdriver.common.by` - 元素定位
3. `selenium.webdriver.support.ui` - 等待机制
4. `selenium.webdriver.support.expected_conditions` - 预期条件
5. `logging` - 日志记录
6. `typing` - 类型提示

### 被依赖的模块

1. `core.cookie_handler` - Cookie 处理模块
2. `core.m3u8_parser` - m3u8 解析模块

## 数据流程

### 浏览器操作流程

```
创建浏览器驱动
  ↓
创建浏览器实例
  ↓
导航到指定 URL
  ↓
等待页面加载
  ↓
获取 Cookie/请求头/元素
  ↓
关闭浏览器
```

### 性能日志获取流程

```
获取性能日志
  ↓
解析日志内容
  ↓
提取 m3u8 链接
  ↓
返回链接列表
```

## 注意事项

1. **浏览器配置**
   - 禁用 USB 设备事件日志
   - 忽略证书错误
   - 禁用日志输出
   - 启用性能日志

2. **资源释放**
   - 使用完毕后必须调用 `close()` 方法
   - 避免浏览器进程残留

3. **异常处理**
   - 捕获浏览器操作异常
   - 记录详细错误信息

4. **日志记录**
   - 记录浏览器创建、操作、关闭等关键步骤
   - 记录异常信息

5. **浏览器兼容性**
   - Edge 和 Chrome 使用相同的日志获取方式
   - Firefox 使用不同的日志获取方式

## 扩展方向

1. **支持更多浏览器**
   - 添加对 Safari、Opera 等浏览器的支持

2. **无头模式**
   - 添加无头浏览器模式支持

3. **代理支持**
   - 添加代理服务器配置

4. **用户数据目录**
   - 支持自定义用户数据目录

5. **性能优化**
   - 优化浏览器启动速度
   - 减少内存占用

## 相关文档

- [核心业务模块 - CookieHandler](../core/README.md)
- [核心业务模块 - M3u8Parser](../core/README.md)
- [配置模块 - Constants](../config/README.md)
