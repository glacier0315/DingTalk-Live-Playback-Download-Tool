# 开发规范

本文档定义钉钉直播回放下载工具的开发规范,包括代码风格、命名约定、注释要求、提交信息格式及代码审查标准,确保代码质量和团队协作效率。

## 目录

- [一、通用规范](#一通用规范)
- [二、Python语言规范](#二python语言规范)
- [三、命名约定](#三命名约定)
- [四、代码风格](#四代码风格)
- [五、注释规范](#五注释规范)
- [六、测试规范](#六测试规范)
- [七、提交规范](#七提交规范)
- [八、代码审查标准](#八代码审查标准)
- [九、安全规范](#九安全规范)
- [十、文档规范](#十文档规范)

---

## 一、通用规范

### 1.1 编码规范

1. **编码格式**: 使用UTF-8编码
2. **缩进**: 使用4个空格,禁止使用Tab键
3. **行长度**: 单行长度不超过79字符
4. **换行**: 使用括号隐式换行,禁止使用反斜杠
5. **空格**: 运算符两侧加空格,逗号后加空格
6. **空行**: 顶级定义之间空两行,类内方法定义之间空一行

### 1.2 通用原则

1. **单一职责**: 函数/接口仅做一件事,相关代码聚合存放,禁止"万能函数"
2. **消除冗余**: 相同逻辑抽离为函数/工具类,避免重复代码与重复计算
3. **简化逻辑**: 避免多层嵌套,采用提前返回优化;复杂条件拆分为布尔变量,提升可读性
4. **资源管理**: 及时释放无用资源,防范内存泄漏
5. **错误处理**: 完善的异常处理,提供友好的错误提示

### 1.3 代码质量原则

1. **可读性**: 代码应该像散文一样易读
2. **可维护性**: 代码应该易于修改和扩展
3. **可测试性**: 代码应该易于编写测试
4. **性能**: 在保证正确性的前提下优化性能
5. **安全性**: 遵循安全最佳实践

---

## 二、Python语言规范

### 2.1 基本规范

#### 2.1.1 导入规范

1. **导入顺序**: 标准库 → 第三方库 → 本地应用/库
2. **每个顶级导入单独一行**
3. **禁止使用通配符导入**: `from module import *`
4. **使用绝对导入**: 避免相对导入

**示例**:

```python
# 标准库
import os
import sys
from typing import Optional, List, Dict

# 第三方库
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

# 本地应用/库
from dingtalk_downloader.utils.models import CookieData
from dingtalk_downloader.core.cookie_handler import CookieHandler
```

#### 2.1.2 模块组织

1. **模块文档字符串**: 每个模块都应该有文档字符串
2. **导入语句**: 放在模块文档字符串之后
3. **全局变量**: 放在导入语句之后
4. **类和函数**: 按照逻辑顺序排列

**示例**:

```python
"""
模块描述

这个模块实现了XXX功能
"""

import os
from typing import Optional, List, Dict

# 全局常量
MAX_RETRY_COUNT = 5
DEFAULT_TIMEOUT = 30

# 类定义
class ClassName:
    """类描述"""

    def __init__(self):
        pass

# 函数定义
def function_name():
    pass
```

### 2.2 类型提示

#### 2.2.1 基本类型提示

为所有函数添加类型提示:

```python
def add_numbers(a: int, b: int) -> int:
    """计算两个数的和

    Args:
        a: 第一个数
        b: 第二个数

    Returns:
        两个数的和
    """
    return a + b
```

#### 2.2.2 复杂类型提示

使用typing模块定义复杂类型:

```python
from typing import Optional, List, Dict, Union, Tuple

def process_data(
    data: List[Dict[str, Union[str, int]]],
    config: Optional[Dict[str, str]] = None
) -> Tuple[List[str], int]:
    """处理数据

    Args:
        data: 数据列表
        config: 配置字典

    Returns:
        处理结果和数量
    """
    pass
```

#### 2.2.3 类型别名

为复杂类型定义别名:

```python
from typing import Dict, List, Optional

CookieDict = Dict[str, str]
HeadersDict = Dict[str, str]
ConfigDict = Optional[Dict[str, str]]

def process_cookies(cookies: CookieDict) -> HeadersDict:
    """处理Cookie"""
    pass
```

### 2.3 异常处理

#### 2.3.1 异常捕获

捕获特定的异常,避免使用裸except:

```python
# 好的做法
try:
    result = some_function()
except ValueError as e:
    logger.error(f"值错误: {e}")
    raise
except Exception as e:
    logger.error(f"未知错误: {e}")
    raise

# 不好的做法
try:
    result = some_function()
except:
    pass
```

#### 2.3.2 自定义异常

定义自定义异常类:

```python
class DingTalkDownloadError(Exception):
    """钉钉下载异常基类"""

    pass


class CookieNotFoundError(DingTalkDownloadError):
    """Cookie未找到异常"""

    pass


class M3u8LinkNotFoundError(DingTalkDownloadError):
    """M3U8链接未找到异常"""

    pass
```

#### 2.3.3 异常处理最佳实践

1. **尽早抛出异常**: 在问题发生时立即抛出异常
2. **提供有用的错误信息**: 错误信息应该清晰、具体
3. **记录异常**: 使用日志记录异常
4. **清理资源**: 在finally块中清理资源

```python
def process_video(url: str) -> None:
    """处理视频

    Args:
        url: 视频URL

    Raises:
        CookieNotFoundError: Cookie未找到
        M3u8LinkNotFoundError: M3U8链接未找到
    """
    try:
        cookie = get_cookie()
        if not cookie:
            raise CookieNotFoundError("Cookie未找到")

        m3u8_link = get_m3u8_link(url)
        if not m3u8_link:
            raise M3u8LinkNotFoundError("M3U8链接未找到")

        download_video(m3u8_link)

    except Exception as e:
        logger.error(f"处理视频失败: {e}")
        raise
    finally:
        cleanup_resources()
```

### 2.4 日志规范

#### 2.4.1 日志级别

使用合适的日志级别:

- **DEBUG**: 调试信息,用于开发阶段
- **INFO**: 一般信息,记录程序运行状态
- **WARNING**: 警告信息,不影响程序运行
- **ERROR**: 错误信息,影响程序运行
- **CRITICAL**: 严重错误,可能导致程序崩溃

#### 2.4.2 日志使用

```python
import logging

logger = logging.getLogger(__name__)

def some_function():
    """某个函数"""

    logger.debug("调试信息")
    logger.info("开始处理")
    logger.warning("警告信息")
    logger.error("错误信息")
    logger.critical("严重错误")
```

#### 2.4.3 日志格式

日志应该包含足够的信息:

```python
# 好的做法
logger.info(f"开始下载视频: {url}, 保存路径: {save_dir}")

# 不好的做法
logger.info("开始下载")
```

### 2.5 资源管理

#### 2.5.1 使用上下文管理器

使用with语句管理资源:

```python
# 好的做法
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()

# 不好的做法
f = open("file.txt", "r", encoding="utf-8")
content = f.read()
f.close()
```

#### 2.5.2 及时释放资源

在不需要时及时释放资源:

```python
def process_browser():
    """处理浏览器"""

    driver = create_driver()
    try:
        result = do_something(driver)
        return result
    finally:
        driver.close()
        driver.quit()
```

---

## 三、命名约定

### 3.1 基本规则

1. **使用有意义的名称**: 名称应该清晰表达意图
2. **避免缩写**: 除非是广泛使用的缩写
3. **避免单字母变量**: 除了循环变量
4. **避免使用保留字**: 不要使用Python保留字

### 3.2 模块命名

- **规则**: 使用全小写,可包含下划线
- **示例**: `cookie_handler.py`, `m3u8_parser.py`

```python
# 好的做法
# cookie_handler.py
# m3u8_parser.py

# 不好的做法
# CookieHandler.py
# m3u8parser.py
```

### 3.3 类命名

- **规则**: 使用大驼峰命名法(PascalCase)
- **示例**: `CookieHandler`, `M3u8Parser`

```python
# 好的做法
class CookieHandler:
    """Cookie处理器"""

    pass

class M3u8Parser:
    """M3U8解析器"""

    pass

# 不好的做法
class cookie_handler:
    pass

class m3u8_parser:
    pass
```

### 3.4 函数命名

- **规则**: 使用蛇形命名法(snake_case)
- **示例**: `get_cookie`, `parse_m3u8`

```python
# 好的做法
def get_cookie():
    """获取Cookie"""
    pass

def parse_m3u8(url: str) -> Dict:
    """解析M3U8"""
    pass

# 不好的做法
def GetCookie():
    pass

def ParseM3U8(url: str) -> Dict:
    pass
```

### 3.5 变量命名

- **规则**: 使用蛇形命名法(snake_case)
- **示例**: `cookie_data`, `m3u8_url`

```python
# 好的做法
cookie_data = {}
m3u8_url = "https://example.com/video.m3u8"
max_retry_count = 5

# 不好的做法
cookieData = {}
m3u8Url = "https://example.com/video.m3u8"
MaxRetryCount = 5
```

### 3.6 常量命名

- **规则**: 使用全大写加下划线(CONSTANT_CASE)
- **示例**: `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT`

```python
# 好的做法
MAX_RETRY_COUNT = 5
DEFAULT_TIMEOUT = 30
BROWSER_TYPE_EDGE = "edge"

# 不好的做法
max_retry_count = 5
default_timeout = 30
browser_type_edge = "edge"
```

### 3.7 私有成员命名

- **规则**: 使用单下划线前缀
- **示例**: `_private_method`, `_private_var`

```python
class ClassName:
    """类描述"""

    def __init__(self):
        self._private_var = None

    def _private_method(self):
        """私有方法"""
        pass

    def public_method(self):
        """公共方法"""
        pass
```

### 3.8 特殊方法命名

- **规则**: 使用双下划线前缀和后缀
- **示例**: `__init__`, `__str__`, `__repr__`

```python
class ClassName:
    """类描述"""

    def __init__(self):
        """初始化方法"""
        pass

    def __str__(self):
        """字符串表示"""
        return "ClassName"

    def __repr__(self):
        """开发者表示"""
        return f"ClassName()"
```

---

## 四、代码风格

### 4.1 代码格式化

#### 4.1.1 使用Black

项目使用Black进行代码格式化:

```bash
# 格式化所有Python文件
black src/ tests/

# 格式化特定文件
black src/dingtalk_downloader/main.py

# 检查格式(不修改文件)
black --check src/ tests/
```

#### 4.1.2 Black配置

在 `pyproject.toml` 中配置Black:

```toml
[tool.black]
line-length = 79
target-version = ['py38']
include = '\.pyi?$'
```

### 4.2 代码检查

#### 4.2.1 使用Flake8

项目使用Flake8进行代码检查:

```bash
# 检查所有Python文件
flake8 src/ tests/

# 检查特定文件
flake8 src/dingtalk_downloader/main.py

# 显示错误代码
flake8 src/ tests/ --show-source
```

#### 4.2.2 Flake8配置

在 `pyproject.toml` 中配置Flake8:

```toml
[tool.flake8]
max-line-length = 79
exclude = [
    '.git',
    '__pycache__',
    '.pytest_cache',
    'venv',
    'env',
]
ignore = ['E203', 'W503']
```

### 4.3 代码组织

#### 4.3.1 文件组织

每个文件应该只包含一个主要类或一组相关函数:

```python
# 好的做法
# cookie_handler.py - 只包含CookieHandler类
class CookieHandler:
    """Cookie处理器"""

    pass

# 不好的做法
# utils.py - 包含太多不相关的类和函数
class CookieHandler:
    pass

class M3u8Parser:
    pass

def get_cookie():
    pass

def parse_m3u8():
    pass
```

#### 4.3.2 类组织

类的方法按照以下顺序排列:

1. `__init__` 方法
2. 公共方法
3. 私有方法
4. 特殊方法(`__str__`, `__repr__`等)

```python
class CookieHandler:
    """Cookie处理器"""

    def __init__(self, browser_type: str):
        """初始化方法"""
        pass

    def get_cookie(self) -> CookieData:
        """获取Cookie(公共方法)"""
        pass

    def _collect_browser_data(self) -> Dict:
        """收集浏览器数据(私有方法)"""
        pass

    def __str__(self) -> str:
        """字符串表示(特殊方法)"""
        return "CookieHandler"
```

#### 4.3.3 函数组织

函数内部按照以下顺序排列:

1. 输入验证
2. 核心逻辑
3. 返回结果

```python
def process_video(url: str, save_dir: str) -> bool:
    """处理视频

    Args:
        url: 视频URL
        save_dir: 保存目录

    Returns:
        处理是否成功
    """
    # 输入验证
    if not url:
        raise ValueError("URL不能为空")

    if not save_dir:
        raise ValueError("保存目录不能为空")

    # 核心逻辑
    cookie = get_cookie()
    m3u8_link = get_m3u8_link(url)
    download_video(m3u8_link, save_dir)

    # 返回结果
    return True
```

### 4.4 代码复杂度

#### 4.4.1 函数长度

单个函数不超过50行:

```python
# 好的做法
def get_cookie() -> CookieData:
    """获取Cookie"""
    cookies = {}
    headers = {}
    return CookieData(cookies, headers)

# 不好的做法
def get_cookie_and_headers_and_parse_and_validate_and_download():
    """函数太长,应该拆分"""
    # 100多行代码
    pass
```

#### 4.4.2 嵌套层次

嵌套层次不超过3层:

```python
# 好的做法
def process_data(data: List[Dict]) -> List[Dict]:
    """处理数据"""
    result = []
    for item in data:
        if item["valid"]:
            result.append(item)
    return result

# 不好的做法
def process_data(data: List[Dict]) -> List[Dict]:
    """嵌套太深"""
    result = []
    for item in data:
        if item["valid"]:
            for sub_item in item["sub_items"]:
                if sub_item["active"]:
                    for detail in sub_item["details"]:
                        if detail["checked"]:
                            result.append(detail)
    return result
```

#### 4.4.3 提前返回

使用提前返回减少嵌套:

```python
# 好的做法
def process_data(data: Optional[Dict]) -> Optional[Dict]:
    """处理数据"""
    if not data:
        return None

    if not data.get("valid"):
        return None

    return data

# 不好的做法
def process_data(data: Optional[Dict]) -> Optional[Dict]:
    """处理数据"""
    if data:
        if data.get("valid"):
            return data
    return None
```

---

## 五、注释规范

### 5.1 文档字符串

#### 5.1.1 模块文档字符串

每个模块都应该有文档字符串:

```python
"""
Cookie处理器模块

这个模块负责从浏览器中获取Cookie和请求头信息。
"""

import logging
from typing import Dict, Optional
```

#### 5.1.2 类文档字符串

每个类都应该有文档字符串:

```python
class CookieHandler:
    """Cookie处理器

    负责从浏览器中获取Cookie和请求头信息。

    Attributes:
        browser_type: 浏览器类型
        driver: 浏览器驱动实例
    """

    def __init__(self, browser_type: str):
        """初始化Cookie处理器

        Args:
            browser_type: 浏览器类型(edge、chrome、firefox)
        """
        self.browser_type = browser_type
        self.driver = None
```

#### 5.1.3 函数文档字符串

每个函数都应该有文档字符串,遵循Google风格:

```python
def get_cookie(self) -> CookieData:
    """获取Cookie和请求头

    从浏览器中获取Cookie和请求头信息。

    Returns:
        CookieData: 包含Cookie和请求头的值对象

    Raises:
        CookieNotFoundError: Cookie未找到
        BrowserNotInitializedError: 浏览器未初始化

    Examples:
        >>> handler = CookieHandler("edge")
        >>> cookie_data = handler.get_cookie()
        >>> print(cookie_data.cookies)
        {'key': 'value'}
    """
    pass
```

### 5.2 行内注释

#### 5.2.1 注释位置

注释应该放在代码上方,与代码间隔两个空格:

```python
# 好的做法
# 提取liveUuid
parsed_url = urlparse(url)
query_params = parse_qs(parsed_url.query)
live_uuid = query_params.get("liveUuid", [None])[0]

# 不好的做法
parsed_url = urlparse(url)  # 提取URL
query_params = parse_qs(parsed_url.query)  # 解析查询参数
live_uuid = query_params.get("liveUuid", [None])[0]  # 获取liveUuid
```

#### 5.2.2 注释内容

注释应该解释"为什么"而不是"是什么":

```python
# 好的做法
# 使用正则表达式提取基础URL,因为URL格式可能变化
pattern = re.compile(r"(https?://[^/]+/live_hp/[0-9a-f-]+)")
match = pattern.search(url)

# 不好的做法
# 创建正则表达式
pattern = re.compile(r"(https?://[^/]+/live_hp/[0-9a-f-]+)")
# 搜索URL
match = pattern.search(url)
```

### 5.3 注释原则

1. **注释应该解释为什么**: 而不是解释代码做了什么
2. **注释应该保持最新**: 代码变更时同步更新注释
3. **避免无用的注释**: 删除无意义的注释
4. **使用中文注释**: 便于团队成员理解

---

## 六、测试规范

### 6.1 测试文件组织

#### 6.1.1 测试目录结构

```tree
tests/
├── unit/                        # 单元测试
│   ├── test_models.py
│   ├── test_validator.py
│   └── ...
├── integration/                 # 集成测试
│   ├── test_download_flow.py
│   └── ...
├── functional/                  # 功能测试
│   ├── test_user_interaction_controller.py
│   └── ...
├── fixtures/                    # 测试数据
│   ├── browser_fixtures.py
│   ├── cookie_fixtures.py
│   └── ...
├── mocks/                       # Mock对象
│   ├── mock_binary.py
│   ├── mock_browser.py
│   └── ...
└── conftest.py                  # pytest配置
```

#### 6.1.2 测试文件命名

测试文件命名格式为 `test_<模块名>.py`:

```python
# 测试文件
# test_cookie_handler.py
# test_m3u8_parser.py
# test_downloader.py
```

### 6.2 单元测试

#### 6.2.1 测试类命名

测试类命名格式为 `Test<类名>`:

```python
class TestCookieHandler:
    """测试CookieHandler类"""

    pass

class TestM3u8Parser:
    """测试M3u8Parser类"""

    pass
```

#### 6.2.2 测试方法命名

测试方法命名格式为 `test_<被测试方法>_<测试场景>`:

```python
class TestCookieHandler:
    """测试CookieHandler类"""

    def test_get_cookie_success(self):
        """测试成功获取Cookie"""
        pass

    def test_get_cookie_not_found(self):
        """测试Cookie未找到"""
        pass

    def test_get_cookie_browser_not_initialized(self):
        """测试浏览器未初始化"""
        pass
```

#### 6.2.3 测试示例

```python
import pytest
from dingtalk_downloader.utils.models import CookieData
from dingtalk_downloader.core.cookie_handler import CookieHandler

class TestCookieData:
    """测试CookieData类"""

    def test_create_cookie_data(self):
        """测试创建CookieData"""
        cookies = {"key1": "value1", "key2": "value2"}
        cookie_data = CookieData(cookies)

        assert cookie_data.cookies == cookies

    def test_to_dict(self):
        """测试to_dict方法"""
        cookies = {"key1": "value1"}
        cookie_data = CookieData(cookies)

        result = cookie_data.to_dict()

        assert result == cookies
        assert result is not cookies  # 确保返回的是副本

    def test_frozen(self):
        """测试不可变性"""
        cookies = {"key1": "value1"}
        cookie_data = CookieData(cookies)

        with pytest.raises(Exception):
            cookie_data.cookies["key2"] = "value2"
```

### 6.3 测试覆盖率

#### 6.3.1 覆盖率目标

- **单元测试覆盖率**: 目标90%以上
- **集成测试覆盖率**: 目标80%以上
- **总体覆盖率**: 目标85%以上

#### 6.3.2 生成覆盖率报告

```bash
# 生成HTML覆盖率报告
pytest --cov=src/dingtalk_downloader --cov-report=html

# 查看报告
# 打开 htmlcov/index.html
```

### 6.4 测试最佳实践

1. **测试应该独立**: 每个测试应该独立运行
2. **测试应该快速**: 单元测试应该在几秒内完成
3. **测试应该可重复**: 多次运行应该得到相同结果
4. **使用Mock**: 隔离外部依赖
5. **测试边界条件**: 测试正常情况和异常情况

---

## 七、提交规范

### 7.1 提交信息格式

遵循 `<type>(<scope>): <subject>` 格式:

#### 7.1.1 Type(类型)

- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式调整(不影响功能)
- `refactor`: 重构(不新增功能不修复bug)
- `test`: 补充测试
- `chore`: 构建/依赖调整

#### 7.1.2 Scope(范围)

填写模块名、功能名,简洁明了:

- `main`: 主程序
- `downloader`: 下载器
- `cookie`: Cookie处理
- `m3u8`: M3U8处理
- `browser`: 浏览器
- `config`: 配置
- `utils`: 工具

#### 7.1.3 Subject(主题)

首字母小写,末尾无标点,长度控制在50字符以内:

```text
feat(downloader): 添加批量下载功能
fix(cookie): 修复Cookie过期问题
docs(readme): 更新安装说明
style(code): 统一代码格式
refactor(parser): 重构M3U8解析器
test(handler): 添加CookieHandler测试
chore(deps): 升级Selenium版本
```

### 7.2 提交信息示例

#### 7.2.1 简单提交

```text
feat(downloader): 添加批量下载功能
```

#### 7.2.2 详细提交

```text
feat(downloader): 添加批量下载功能

- 支持从CSV/Excel文件读取链接
- 支持批量下载多个视频
- 添加下载进度显示
- 优化错误处理

Closes #123
```

### 7.3 提交最佳实践

1. **频繁提交**: 小步快跑,频繁提交代码
2. **清晰的提交信息**: 遵循提交信息规范
3. **每次只提交一个功能**: 避免一次提交多个不相关的变更
4. **提交前运行测试**: 确保所有测试通过
5. **提交前格式化代码**: 使用Black格式化代码

---

## 八、代码审查标准

### 8.1 代码审查清单

#### 8.1.1 功能性

- [ ] 代码是否实现了预期的功能
- [ ] 是否有未处理的边界情况
- [ ] 错误处理是否完善
- [ ] 是否有潜在的Bug

#### 8.1.2 代码质量

- [ ] 代码是否符合项目规范
- [ ] 是否有重复代码
- [ ] 是否有复杂的逻辑可以简化
- [ ] 变量和函数命名是否清晰

#### 8.1.3 性能

- [ ] 是否有性能问题
- [ ] 是否有不必要的计算
- [ ] 是否有内存泄漏风险
- [ ] 是否可以使用更高效的算法

#### 8.1.4 安全性

- [ ] 是否有安全漏洞
- [ ] 是否有SQL注入风险
- [ ] 是否有XSS风险
- [ ] 敏感信息是否泄露

#### 8.1.5 测试

- [ ] 是否有足够的测试
- [ ] 测试覆盖率是否达标
- [ ] 测试是否通过
- [ ] 是否有集成测试

#### 8.1.6 文档

- [ ] 是否有文档字符串
- [ ] 文档是否准确
- [ ] 是否有使用示例
- [ ] 注释是否清晰

### 8.2 审查流程

1. **创建Pull Request**
2. **自动检查**: CI/CD自动运行测试和代码检查
3. **人工审查**: 至少一名团队成员审查代码
4. **修改反馈**: 根据审查意见修改代码
5. **批准合并**: 审查通过后合并代码

### 8.3 审查反馈

#### 8.3.1 反馈格式

使用清晰的反馈格式:

```text
**问题**: 描述问题
**建议**: 提出改进建议
**示例**: 提供代码示例
```

#### 8.3.2 反馈示例

```text
**问题**: CookieHandler.get_cookie()方法缺少错误处理

**建议**: 添加try-except块捕获异常,并提供友好的错误提示

**示例**:
```python
def get_cookie(self) -> CookieData:
    try:
        cookies = self.driver.get_cookies()
        if not cookies:
            raise CookieNotFoundError("Cookie未找到")
        return CookieData(cookies)
    except Exception as e:
        logger.error(f"获取Cookie失败: {e}")
        raise
```
```

---

## 九、安全规范

### 9.1 敏感信息管理

#### 9.1.1 禁止硬编码敏感信息

```python
# 好的做法
import os

api_key = os.getenv("API_KEY")
password = os.getenv("PASSWORD")

# 不好的做法
api_key = "1234567890"
password = "password123"
```

#### 9.1.2 使用环境变量

创建 `.env` 文件:

```env
API_KEY=your_api_key
PASSWORD=your_password
```

在代码中使用:

```python
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")
password = os.getenv("PASSWORD")
```

#### 9.1.3 使用配置文件

使用YAML配置文件管理敏感信息:

```yaml
# config/app.yaml
api:
  key: ${API_KEY}
  secret: ${API_SECRET}
```

### 9.2 输入验证

#### 9.2.1 验证用户输入

```python
def validate_url(url: str) -> bool:
    """验证URL格式

    Args:
        url: 待验证的URL

    Returns:
        URL是否有效
    """
    if not url:
        return False

    if not url.startswith("http"):
        return False

    return True
```

#### 9.2.2 使用pydantic验证

```python
from pydantic import BaseModel, validator

class VideoDownloadRequest(BaseModel):
    """视频下载请求"""

    url: str
    save_dir: str

    @validator("url")
    def validate_url(cls, v):
        if not v.startswith("http"):
            raise ValueError("URL必须以http开头")
        return v
```

### 9.3 安全最佳实践

1. **使用HTTPS**: 使用安全的通信协议
2. **验证输入**: 对所有输入进行验证
3. **最小权限原则**: 只给程序必要的权限
4. **定期更新依赖**: 及时更新第三方库
5. **使用安全的加密算法**: 使用业界认可的加密算法

---

## 十、文档规范

### 10.1 文档类型

#### 10.1.1 代码文档

- **模块文档字符串**: 描述模块的功能
- **类文档字符串**: 描述类的功能和使用方法
- **函数文档字符串**: 描述函数的功能、参数、返回值和异常

#### 10.1.2 项目文档

- **README.md**: 项目说明文档
- **architecture.md**: 架构文档
- **development_guide.md**: 开发指南
- **development_standard.md**: 开发规范

#### 10.1.3 API文档

- **API文档**: 描述API接口
- **使用示例**: 提供使用示例
- **变更日志**: 记录版本变更

### 10.2 文档编写

#### 10.2.1 使用Markdown

使用Markdown格式编写文档:

```markdown
# 标题

## 二级标题

### 三级标题

- 列表项1
- 列表项2

1. 有序列表项1
2. 有序列表项2

**粗体**
*斜体*

`代码`

```python
代码块
```

[链接](https://example.com)
```

#### 10.2.2 添加示例

为复杂功能添加使用示例:

```python
def get_cookie() -> CookieData:
    """获取Cookie和请求头

    从浏览器中获取Cookie和请求头信息。

    Returns:
        CookieData: 包含Cookie和请求头的值对象

    Examples:
        >>> handler = CookieHandler("edge")
        >>> cookie_data = handler.get_cookie()
        >>> print(cookie_data.cookies)
        {'key': 'value'}
    """
    pass
```

### 10.3 文档维护

1. **及时更新文档**: 代码变更后同步更新文档
2. **保持文档简洁**: 避免冗余内容
3. **定期审查文档**: 定期检查文档的准确性
4. **使用版本控制**: 文档也应该使用版本控制

---

## 总结

本文档定义了钉钉直播回放下载工具的开发规范,包括代码风格、命名约定、注释要求、提交信息格式及代码审查标准。

关键要点:

1. **遵循PEP 8规范**: 使用Black自动格式化代码
2. **使用有意义的命名**: 名称应该清晰表达意图
3. **编写完善的文档字符串**: 为函数和类添加docstring
4. **编写单元测试**: 为每个函数编写测试
5. **遵循提交信息规范**: 使用清晰的提交信息
6. **进行代码审查**: 提交前进行代码审查
7. **遵循安全最佳实践**: 保护敏感信息,验证输入

遵循本文档的规范,可以提高代码质量,促进团队协作,降低维护成本。
