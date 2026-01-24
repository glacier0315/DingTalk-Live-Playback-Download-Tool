# DESIGN - 浏览器驱动代码重构

## 文档信息

- **任务名称**: browser-driver-refactoring
- **创建时间**: 2026-01-24
- **阶段**: Architect（架构）
- **目标**: 设计重构架构，定义核心组件和接口

---

## 一、架构设计原则

### 1.1 设计原则

本次重构严格遵循以下设计原则：

1. **单一职责原则（SRP）**: 每个类只负责一项职责
2. **开闭原则（OCP）**: 对扩展开放，对修改关闭
3. **里氏替换原则（LSP）**: 子类可以替换父类
4. **接口隔离原则（ISP）**: 接口应该小而专一
5. **依赖倒置原则（DIP）**: 依赖抽象而非具体实现

### 1.2 设计模式

本次重构使用以下设计模式：

1. **模板方法模式**: BrowserDriver提供默认实现，子类可选择重写
2. **工厂模式**: BrowserFactory负责创建浏览器实例
3. **策略模式**: 不同浏览器子类实现不同的日志解析策略

---

## 二、核心架构设计

### 2.1 类图

```
┌─────────────────────────────────────────────────────────────────┐
│                        BrowserDriver (ABC)                    │
├─────────────────────────────────────────────────────────────────┤
│ + driver: Optional[WebDriver]                                │
├─────────────────────────────────────────────────────────────────┤
│ + create_driver(): WebDriver (抽象)                           │
│ + get_log(log_type: str): List[dict] (抽象)                  │
│ + get_element_by_xpath(xpath: str): Optional[WebDriver]        │
│ + get_element_by_class_name(class_name: str): Optional[WebDriver]│
│ + get_cookies(): List[dict]                                   │
│ + navigate(url: str): None                                    │
│ + wait_for_video(timeout: int): None                          │
│ + close(): None                                              │
│ + is_driver_initialized(): bool                                │
│ + get_driver(): Optional[WebDriver]                            │
│ + extract_m3u8_links_from_logs(logs: List[dict]): List[str]  │
└─────────────────────────────────────────────────────────────────┘
                              △
                              │ 继承
              ┌───────────────┼───────────────┐
              │               │               │
┌─────────────┴─────┐ ┌─────┴──────┐ ┌────┴──────────┐
│   ChromeDriver      │ │FirefoxDriver│ │  EdgeDriver   │
├────────────────────┤ ├────────────┤ ├───────────────┤
│ + create_driver()  │ │+create_    │ │+create_       │
│ + get_log()       │ │ driver()    │ │ driver()      │
│                  │ │+get_log()   │ │+get_log()     │
│ (继承父类方法)    │ │            │ │               │
│                  │ │+extract_   │ │ (继承父类方法) │
│                  │ │ m3u8_links_│ │               │
│                  │ │ from_logs() │ │               │
└──────────────────┘ └────────────┘ └───────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      M3u8Parser                             │
├─────────────────────────────────────────────────────────────────┤
│ - browser: BrowserDriver                                      │
│ - max_retries: int                                          │
├─────────────────────────────────────────────────────────────────┤
│ + __init__(browser: BrowserDriver, max_retries: int)         │
│ + fetch_m3u8_links(url: str): Optional[List[str]]           │
│ + download_m3u8_file(url: str, filename: str, headers: dict): str│
│ + extract_prefix(url: str): str                              │
│ - _refresh_page(): None                                      │
└─────────────────────────────────────────────────────────────────┘
                              │ 使用
                              ▽
┌─────────────────────────────────────────────────────────────────┐
│                    BrowserFactory                             │
├─────────────────────────────────────────────────────────────────┤
│ + create_browser(browser_type: str): BrowserDriver             │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 模块依赖关系

```
┌─────────────────────────────────────────────────────────────────┐
│                      main.py                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▽
┌─────────────────────────────────────────────────────────────────┐
│                    Downloader                                │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▽               ▽               ▽
┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
│  CookieHandler   │ │ M3u8Parser   │ │NM3u8DLRE     │
└──────────────────┘ └──────────────┘ └──────────────┘
                              │
                              ▽
┌─────────────────────────────────────────────────────────────────┐
│                    BrowserDriver (ABC)                        │
└─────────────────────────────────────────────────────────────────┘
                              △
              ┌───────────────┼───────────────┐
              │               │               │
              ▽               ▽               ▽
┌──────────────────┐ ┌──────────────┐ ┌──────────────┐
│   ChromeDriver   │ │FirefoxDriver │ │  EdgeDriver  │
└──────────────────┘ └──────────────┘ └──────────────┘
```

---

## 三、详细设计

### 3.1 BrowserDriver扩展设计

#### 3.1.1 新增方法：extract_m3u8_links_from_logs

**方法签名**:
```python
def extract_m3u8_links_from_logs(self, logs: List[dict]) -> List[str]:
    """
    从浏览器日志中提取m3u8链接。

    提供默认实现，处理Edge和Chrome的日志格式。
    子类可以重写此方法以处理特定浏览器的日志格式。

    Args:
        logs: 浏览器日志列表

    Returns:
        m3u8链接列表
    """
```

**默认实现逻辑**:
1. 遍历日志列表
2. 检查日志中是否包含"message"字段
3. 如果包含，提取message内容
4. 在message中查找".m3u8"关键字
5. 提取URL（格式：'url":"..."）
6. 返回找到的m3u8链接列表

**代码实现**:
```python
def extract_m3u8_links_from_logs(self, logs: List[dict]) -> List[str]:
    m3u8_links = []
    for log in logs:
        try:
            if "message" in log:
                log_message = log["message"]
            else:
                log_message = str(log)

            if ".m3u8" in log_message:
                start_idx = log_message.find('url":"') + len('url":"')
                end_idx = log_message.find('"', start_idx)
                m3u8_url = log_message[start_idx:end_idx]
                m3u8_links.append(m3u8_url)
        except Exception as e:
            logger.error(f"提取m3u8链接时发生错误: {e}", exc_info=True)
    return m3u8_links
```

#### 3.1.2 FirefoxDriver重写方法

**重写逻辑**:
1. 遍历日志列表
2. 将日志转换为字符串
3. 使用正则表达式匹配m3u8链接
4. 清理链接中的特殊字符
5. 返回找到的m3u8链接列表

**代码实现**:
```python
def extract_m3u8_links_from_logs(self, logs: List[dict]) -> List[str]:
    m3u8_links = []
    pattern = r'https://[^,\'"]+\.m3u8\?[^\'"]+'
    
    for log in logs:
        try:
            log_message = str(log)
            found_links = re.findall(pattern, log_message)
            
            if found_links:
                cleaned_link = re.sub(r'[\]\s\\\'"]+$', "", found_links[0])
                m3u8_links.append(cleaned_link)
        except Exception as e:
            logger.error(f"提取m3u8链接时发生错误: {e}", exc_info=True)
    
    return m3u8_links
```

### 3.2 M3u8Parser重构设计

#### 3.2.1 构造函数修改

**修改前**:
```python
def __init__(
    self,
    browser: Union[EdgeDriver, ChromeDriver, FirefoxDriver],
    browser_type: str,
    max_retries: int = MAX_RETRY_COUNT,
):
    self.browser = browser
    self.browser_type = browser_type
    self.max_retries = max_retries
```

**修改后**:
```python
def __init__(
    self,
    browser: BrowserDriver,
    max_retries: int = MAX_RETRY_COUNT,
):
    self.browser = browser
    self.max_retries = max_retries
```

**变更说明**:
- 移除`browser_type`参数
- 将`browser`参数类型从具体类改为抽象类`BrowserDriver`
- 符合依赖倒置原则

#### 3.2.2 fetch_m3u8_links方法重构

**修改前**:
```python
def fetch_m3u8_links(self, url: str) -> Optional[List[str]]:
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    live_uuid = query_params.get("liveUuid", [None])[FIRST_ELEMENT_INDEX]

    if not live_uuid:
        logger.error("未能从 URL 提取 liveUuid，程序将退出")
        return None

    m3u8_links = []

    for attempt in range(self.max_retries):
        try:
            if self.browser_type in [BROWSER_TYPE_EDGE, BROWSER_TYPE_CHROME]:
                logs = self.browser.get_log(LOG_TYPE_PERFORMANCE)
            elif self.browser_type == BROWSER_TYPE_FIREFOX:
                logs = self.browser.get_log(LOG_TYPE_PERFORMANCE)

            for log in logs:
                try:
                    if self.browser_type == BROWSER_TYPE_FIREFOX:
                        log_message = str(log)
                        pattern = r'https://[^,\'"]+\.m3u8\?[^\'"]+'
                        found_links = re.findall(pattern, log_message)

                        if found_links:
                            cleaned_link = re.sub(r'[\]\s\\\'"]+$', "", found_links[0])
                            m3u8_links.append(cleaned_link)
                            logger.debug(f"获取到m3u8链接: {cleaned_link}")
                            return m3u8_links
                    else:
                        if "message" in log:
                            log_message = log["message"]
                        else:
                            log_message = str(log)

                        if ".m3u8" in log_message:
                            start_idx = log_message.find('url":"') + len('url":"')
                            end_idx = log_message.find('"', start_idx)
                            m3u8_url = log_message[start_idx:end_idx]

                            if live_uuid in m3u8_url:
                                logger.debug(f"获取到m3u8链接: {m3u8_url}")
                                m3u8_links.append(m3u8_url)
                                return m3u8_links
                except Exception as e:
                    logger.error(f"处理日志时发生错误: {e}", exc_info=True)

            logger.debug(f"第 {attempt + 1} 次尝试未获取到 m3u8 链接，重试中")
            self._refresh_page()

        except Exception as e:
            logger.error(f"获取 m3u8 链接时发生错误: {e}", exc_info=True)

    if not m3u8_links:
        logger.warning(f"经过 {self.max_retries} 次重试后仍未获取到 m3u8 链接")
    return None
```

**修改后**:
```python
def fetch_m3u8_links(self, url: str) -> Optional[List[str]]:
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    live_uuid = query_params.get("liveUuid", [None])[FIRST_ELEMENT_INDEX]

    if not live_uuid:
        logger.error("未能从 URL 提取 liveUuid，程序将退出")
        return None

    for attempt in range(self.max_retries):
        try:
            logs = self.browser.get_log(LOG_TYPE_PERFORMANCE)
            m3u8_links = self.browser.extract_m3u8_links_from_logs(logs)

            for m3u8_url in m3u8_links:
                if live_uuid in m3u8_url:
                    logger.debug(f"获取到m3u8链接: {m3u8_url}")
                    return [m3u8_url]

            logger.debug(f"第 {attempt + 1} 次尝试未获取到 m3u8 链接，重试中")
            self._refresh_page()

        except Exception as e:
            logger.error(f"获取 m3u8 链接时发生错误: {e}", exc_info=True)

    logger.warning(f"经过 {self.max_retries} 次重试后仍未获取到 m3u8 链接")
    return None
```

**变更说明**:
- 移除浏览器类型判断逻辑
- 直接调用`browser.get_log()`获取日志
- 调用`browser.extract_m3u8_links_from_logs()`提取m3u8链接
- 简化代码逻辑，提高可读性

#### 3.2.3 import语句修改

**修改前**:
```python
from ..browser.edge_driver import EdgeDriver
from ..browser.chrome_driver import ChromeDriver
from ..browser.firefox_driver import FirefoxDriver
from ..config.constants import (
    BROWSER_TYPE_EDGE,
    BROWSER_TYPE_CHROME,
    BROWSER_TYPE_FIREFOX,
    MAX_RETRY_COUNT,
)
```

**修改后**:
```python
from ..browser.browser_driver import BrowserDriver
from ..config.constants import MAX_RETRY_COUNT
```

**变更说明**:
- 移除具体浏览器驱动类的导入
- 只导入BrowserDriver抽象类
- 移除浏览器类型常量的导入

### 3.3 测试用例设计

#### 3.3.1 BrowserDriver测试

**测试文件**: `tests/unit/test_browser_driver.py`

**新增测试用例**:
```python
def test_extract_m3u8_links_from_logs_default():
    """测试默认实现提取m3u8链接"""
    mock_browser = Mock(spec=BrowserDriver)
    
    logs = [
        {"message": '{"message":{"params":{"request":{"url":"https://example.com/video.m3u8?token=abc"}}}'},
        {"message": '{"message":{"params":{"request":{"url":"https://example.com/other.m3u8?token=xyz"}}}'}
    ]
    
    result = BrowserDriver.extract_m3u8_links_from_logs(mock_browser, logs)
    
    assert len(result) == 2
    assert "https://example.com/video.m3u8?token=abc" in result
    assert "https://example.com/other.m3u8?token=xyz" in result
```

#### 3.3.2 FirefoxDriver测试

**测试文件**: `tests/unit/test_firefox_driver.py`

**新增测试用例**:
```python
def test_extract_m3u8_links_from_logs_firefox():
    """测试FirefoxDriver重写方法提取m3u8链接"""
    firefox_driver = FirefoxDriver()
    
    logs = [
        "{'name': 'Network.request', 'url': 'https://example.com/video.m3u8?token=abc'}",
        "{'name': 'Network.request', 'url': 'https://example.com/other.m3u8?token=xyz'}"
    ]
    
    result = firefox_driver.extract_m3u8_links_from_logs(logs)
    
    assert len(result) == 2
    assert "https://example.com/video.m3u8?token=abc" in result
    assert "https://example.com/other.m3u8?token=xyz" in result
```

#### 3.3.3 M3u8Parser测试

**测试文件**: `tests/unit/test_m3u8_parser.py`

**修改测试用例**:
```python
def test_fetch_m3u8_links_edge():
    """测试Edge浏览器获取m3u8链接"""
    mock_browser = Mock(spec=BrowserDriver)
    mock_browser.get_log.return_value = [
        {"message": '{"message":{"params":{"request":{"url":"https://example.com/video.m3u8?liveUuid=abc123"}}}'}
    ]
    mock_browser.extract_m3u8_links_from_logs.return_value = [
        "https://example.com/video.m3u8?liveUuid=abc123"
    ]
    
    parser = M3u8Parser(mock_browser)
    url = "https://n.dingtalk.com/live?liveUuid=abc123"
    
    result = parser.fetch_m3u8_links(url)
    
    assert result is not None
    assert len(result) == 1
    assert result[0] == "https://example.com/video.m3u8?liveUuid=abc123"

def test_fetch_m3u8_links_firefox():
    """测试Firefox浏览器获取m3u8链接"""
    mock_browser = Mock(spec=BrowserDriver)
    mock_browser.get_log.return_value = [
        "{'name': 'Network.request', 'url': 'https://example.com/video.m3u8?liveUuid=abc123'}"
    ]
    mock_browser.extract_m3u8_links_from_logs.return_value = [
        "https://example.com/video.m3u8?liveUuid=abc123"
    ]
    
    parser = M3u8Parser(mock_browser)
    url = "https://n.dingtalk.com/live?liveUuid=abc123"
    
    result = parser.fetch_m3u8_links(url)
    
    assert result is not None
    assert len(result) == 1
    assert result[0] == "https://example.com/video.m3u8?liveUuid=abc123"
```

---

## 四、数据流设计

### 4.1 获取m3u8链接的数据流

```
┌─────────────────────────────────────────────────────────────────┐
│                      M3u8Parser                             │
│  fetch_m3u8_links(url)                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 1. 解析URL获取liveUuid
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  urlparse + parse_qs                          │
│              提取liveUuid参数                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 2. 获取浏览器日志
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              browser.get_log("performance")                     │
│              (ChromeDriver/EdgeDriver/FirefoxDriver)          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 3. 提取m3u8链接
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│     browser.extract_m3u8_links_from_logs(logs)              │
│     (默认实现或FirefoxDriver重写实现)                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 4. 过滤匹配liveUuid的链接
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              检查m3u8_url中是否包含liveUuid                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ 5. 返回结果
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              返回m3u8链接列表                                │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 日志处理流程

```
┌─────────────────────────────────────────────────────────────────┐
│              浏览器日志 (logs)                              │
│  [                                                         │
│    {"message": "..."},  (Chrome/Edge)                       │
│    "...",                    (Firefox)                       │
│  ]                                                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│      extract_m3u8_links_from_logs(logs)                     │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
┌──────────────────────┐        ┌──────────────────────┐
│  Chrome/EdgeDriver   │        │   FirefoxDriver      │
│  (默认实现)          │        │   (重写实现)         │
├──────────────────────┤        ├──────────────────────┤
│ 1. 提取message字段  │        │ 1. 转换为字符串     │
│ 2. 查找".m3u8"     │        │ 2. 正则匹配         │
│ 3. 提取URL          │        │ 3. 清理特殊字符     │
└──────────────────────┘        └──────────────────────┘
              │                               │
              └───────────────┬───────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              m3u8链接列表                                    │
│  [                                                         │
│    "https://example.com/video.m3u8?token=abc",              │
│    "https://example.com/other.m3u8?token=xyz",              │
│  ]                                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 五、接口设计

### 5.1 BrowserDriver接口

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from selenium.webdriver.remote.webdriver import WebDriver

class BrowserDriver(ABC):
    """
    浏览器驱动抽象基类。
    
    定义所有浏览器驱动必须实现的接口。
    """
    
    def __init__(self):
        self.driver: Optional[WebDriver] = None
    
    @abstractmethod
    def create_driver(self) -> WebDriver:
        """创建浏览器实例"""
        pass
    
    @abstractmethod
    def get_log(self, log_type: str) -> List[dict]:
        """获取浏览器日志"""
        pass
    
    def extract_m3u8_links_from_logs(self, logs: List[dict]) -> List[str]:
        """
        从浏览器日志中提取m3u8链接。
        
        提供默认实现，处理Edge和Chrome的日志格式。
        子类可以重写此方法以处理特定浏览器的日志格式。
        """
        pass
    
    def get_element_by_xpath(self, xpath: str) -> Optional[WebDriver]:
        """通过XPath获取元素"""
        pass
    
    def get_element_by_class_name(self, class_name: str) -> Optional[WebDriver]:
        """通过类名获取元素"""
        pass
    
    def get_cookies(self) -> List[dict]:
        """获取Cookie"""
        pass
    
    def navigate(self, url: str) -> None:
        """导航到指定URL"""
        pass
    
    def wait_for_video(self, timeout: int = 20) -> None:
        """等待视频加载"""
        pass
    
    def close(self) -> None:
        """关闭浏览器"""
        pass
    
    def is_driver_initialized(self) -> bool:
        """检查浏览器驱动是否已初始化"""
        pass
    
    def get_driver(self) -> Optional[WebDriver]:
        """获取浏览器驱动实例"""
        pass
```

### 5.2 M3u8Parser接口

```python
from typing import Optional, List
from urllib.parse import urlparse, parse_qs
from ..browser.browser_driver import BrowserDriver

class M3u8Parser:
    """
    m3u8解析类，负责提取m3u8链接和基础URL。
    """
    
    def __init__(self, browser: BrowserDriver, max_retries: int = 5):
        """
        初始化m3u8解析器。
        
        Args:
            browser: 浏览器驱动实例
            max_retries: 最大重试次数
        """
        self.browser = browser
        self.max_retries = max_retries
    
    def fetch_m3u8_links(self, url: str) -> Optional[List[str]]:
        """
        从浏览器网络日志中提取m3u8链接。
        
        Args:
            url: 钉钉直播回放分享链接
        
        Returns:
            m3u8链接列表，如果提取失败则返回None
        """
        pass
    
    def download_m3u8_file(self, url: str, filename: str, headers: dict) -> str:
        """
        下载m3u8文件。
        
        Args:
            url: m3u8文件URL
            filename: 保存的文件名
            headers: 请求头字典
        
        Returns:
            m3u8文件路径
        """
        pass
    
    def extract_prefix(self, url: str) -> str:
        """
        提取基础URL。
        
        Args:
            url: m3u8文件URL
        
        Returns:
            基础URL
        """
        pass
```

---

## 六、错误处理设计

### 6.1 异常处理策略

1. **BrowserDriver层**: 捕获并记录日志，向上抛出异常
2. **M3u8Parser层**: 捕获异常，记录日志，返回None或重试
3. **应用层**: 处理异常，向用户显示友好的错误信息

### 6.2 日志记录策略

1. **DEBUG级别**: 详细的调试信息（如获取到的m3u8链接）
2. **INFO级别**: 重要的操作信息（如开始获取m3u8链接）
3. **WARNING级别**: 警告信息（如重试未成功）
4. **ERROR级别**: 错误信息（如获取m3u8链接失败）

---

## 七、性能考虑

### 7.1 性能优化点

1. **减少重复计算**: 缓存解析结果
2. **提前返回**: 找到第一个匹配的m3u8链接后立即返回
3. **减少日志量**: 只记录必要的日志信息

### 7.2 性能监控

1. 记录获取m3u8链接的耗时
2. 记录重试次数
3. 记录成功率

---

## 八、安全性考虑

### 8.1 输入验证

1. 验证URL格式
2. 验证liveUuid参数
3. 验证m3u8链接格式

### 8.2 数据安全

1. 不记录敏感信息（如Cookie）
2. 使用HTTPS协议
3. 验证证书

---

## 九、可扩展性设计

### 9.1 添加新浏览器类型

添加新浏览器类型（如Safari）的步骤：

1. 创建SafariDriver类，继承BrowserDriver
2. 实现create_driver和get_log方法
3. 根据需要重写extract_m3u8_links_from_logs方法
4. 在BrowserFactory中添加Safari的创建逻辑
5. 更新常量定义（BROWSER_TYPE_SAFARI）
6. 更新用户界面（如果需要）

**无需修改M3u8Parser代码**，符合开闭原则。

### 9.2 添加新功能

添加新功能（如支持其他视频格式）的步骤：

1. 在BrowserDriver中添加新的抽象方法
2. 在各个浏览器子类中实现该方法
3. 在M3u8Parser中调用新方法

---

## 十、测试策略

### 10.1 单元测试

1. **BrowserDriver测试**: 测试抽象方法的接口定义
2. **ChromeDriver测试**: 测试Chrome特定的实现
3. **FirefoxDriver测试**: 测试Firefox特定的实现
4. **EdgeDriver测试**: 测试Edge特定的实现
5. **M3u8Parser测试**: 测试m3u8解析逻辑

### 10.2 集成测试

1. 测试M3u8Parser与BrowserDriver的集成
2. 测试不同浏览器类型的完整流程

### 10.3 功能测试

1. 测试Edge浏览器获取m3u8链接
2. 测试Chrome浏览器获取m3u8链接
3. 测试Firefox浏览器获取m3u8链接

---

## 十一、部署计划

### 11.1 部署步骤

1. 代码审查
2. 合并到主分支
3. 运行所有测试
4. 部署到生产环境

### 11.2 回滚计划

如果出现问题，可以快速回滚到之前的版本。

---

## 十二、下一步行动

1. ✅ 分析现有浏览器操作代码
2. ✅ 识别代码中重复的浏览器类型判断逻辑
3. ✅ 生成ALIGNMENT文档
4. ✅ 生成CONSENSUS文档
5. ✅ 设计重构架构（当前）
6. ⏳ 拆分原子任务（Atomize阶段）
7. ⏳ 执行质量检查（Approve阶段）
8. ⏳ 实现代码重构（Automate阶段）
9. ⏳ 质量评估与交付确认（Assess阶段）
