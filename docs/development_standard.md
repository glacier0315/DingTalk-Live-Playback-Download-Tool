# 开发规范

本文档定义钉钉直播回放下载工具的开发规范,包括代码风格、命名约定、注释要求、提交信息格式及代码审查标准,确保团队协作的代码质量和一致性。

## 目录

- [一、代码风格规范](#一代码风格规范)
- [二、命名约定](#二命名约定)
- [三、注释要求](#三注释要求)
- [四、提交信息格式](#四提交信息格式)
- [五、代码审查标准](#五代码审查标准)
- [六、测试规范](#六测试规范)
- [七、文档规范](#七文档规范)

---

## 一、代码风格规范

### 1.1 基本原则

遵循以下基本原则:

1. **可读性优先**: 代码应该像散文一样易读
2. **一致性**: 整个项目保持一致的代码风格
3. **简洁性**: 避免不必要的复杂性
4. **明确性**: 代码意图应该清晰明了

### 1.2 格式规范

#### 1.2.1 行长度

- **默认规则**: 单行长度不超过79字符
- **例外情况**:
  - 长字符串(如SQL、多行文档字符串)
  - 不可拆分的导入路径
  - URL链接
- **换行方式**: 使用括号隐式换行,禁止使用反斜杠

**示例**:

```python
# 好的示例: 使用括号隐式换行
result = (
    some_function_with_long_name(
        arg1, arg2, arg3
    )
)

# 不好的示例: 使用反斜杠换行
result = some_function_with_long_name( \
    arg1, arg2, arg3)
```

#### 1.2.2 缩进

- **缩进方式**: 4个空格,禁止使用Tab键
- **缩进层级**: 每层缩进4个空格

**示例**:

```python
# 好的示例: 使用4个空格缩进
def some_function():
    if condition:
        do_something()
        if another_condition:
            do_another_thing()

# 不好的示例: 使用Tab缩进
def some_function():
	if condition:
		do_something()
```

#### 1.2.3 空行

- **顶级定义之间**: 空两行
- **类内方法定义之间**: 空一行
- **函数内逻辑段落之间**: 空一行

**示例**:

```python
# 好的示例: 适当的空行
class MyClass:
    def method1(self):
        pass

    def method2(self):
        pass


def function1():
    pass


def function2():
    pass
```

#### 1.2.4 空格

- **二元运算符前后**: 添加空格
- **逗号后**: 添加空格
- **冒号后**: 添加空格(字典、切片等)
- **函数参数**: 逗号后添加空格
- **括号内**: 不添加空格

**示例**:

```python
# 好的示例: 适当的空格
x = a + b
result = func(arg1, arg2)
my_dict = {"key": "value"}
my_list[1:3]

# 不好的示例: 不当的空格
x=a+b
result = func ( arg1 , arg2 )
my_dict = {"key" : "value"}
my_list[ 1 : 3 ]
```

### 1.3 导入规范

#### 1.3.1 导入顺序

按照以下顺序导入:

1. 标准库导入
2. 第三方库导入
3. 本地应用/库导入

**示例**:

```python
# 好的示例: 正确的导入顺序
import os
import sys
from typing import Optional, List

import requests
from selenium import webdriver

from dingtalk_downloader.utils.models import CookieData
from dingtalk_downloader.config.yaml_config import YamlConfig
```

#### 1.3.2 导入格式

- **每个顶级导入单独一行**
- **从同一模块导入多个成员**: 可使用括号隐式换行
- **禁止使用通配符导入**: `from module import *`

**示例**:

```python
# 好的示例: 单独一行导入
import os
import sys

# 好的示例: 使用括号合并导入
from os import (
    path,
    listdir,
    mkdir
)

# 不好的示例: 多个导入在一行
import os, sys

# 不好的示例: 通配符导入
from os import *
```

### 1.4 表达式和语句

#### 1.4.1 布尔判断

- **判断None值**: 使用 `is/is not`,避免使用 `==`
- **判断布尔值**: 避免使用 `== True/False`
- **判断容器**: 优先使用 `if not container`,而非 `if len(container) == 0`

**示例**:

```python
# 好的示例: 正确的布尔判断
if value is None:
    pass

if value:
    pass

if not my_list:
    pass

# 不好的示例: 错误的布尔判断
if value == None:
    pass

if value == True:
    pass

if len(my_list) == 0:
    pass
```

#### 1.4.2 条件表达式

- **简化逻辑**: 使用提前返回优化
- **复杂条件**: 拆分为布尔变量

**示例**:

```python
# 好的示例: 提前返回
def process_data(data):
    if not data:
        return None

    result = do_something(data)
    return result

# 好的示例: 拆分复杂条件
is_valid = condition1 and condition2
is_ready = condition3 or condition4

if is_valid and is_ready:
    do_something()

# 不好的示例: 深层嵌套
def process_data(data):
    if data:
        if condition1:
            if condition2:
                result = do_something(data)
                return result
```

#### 1.4.3 列表推导

- **简单场景**: 使用列表推导
- **复杂逻辑**: 使用for循环

**示例**:

```python
# 好的示例: 简单的列表推导
squares = [x ** 2 for x in range(10)]

# 好的示例: 复杂逻辑使用for循环
result = []
for item in items:
    if condition1(item):
        processed = process(item)
        if condition2(processed):
            result.append(processed)

# 不好的示例: 复杂的列表推导
result = [
    process(item)
    for item in items
    if condition1(item)
    if condition2(process(item))
]
```

### 1.5 异常处理

#### 1.5.1 异常捕获

- **捕获具体异常**: 避免捕获所有异常
- **提供错误信息**: 包含有用的错误信息
- **使用finally**: 确保资源释放

**示例**:

```python
# 好的示例: 捕获具体异常
try:
    result = some_function()
except ValueError as e:
    logger.error(f"值错误: {e}")
    return None
except ConnectionError as e:
    logger.error(f"连接错误: {e}")
    return None

# 不好的示例: 捕获所有异常
try:
    result = some_function()
except Exception as e:
    logger.error(f"错误: {e}")
    return None
```

#### 1.5.2 异常抛出

- **使用自定义异常**: 定义业务相关的异常
- **提供错误信息**: 包含有用的错误信息

**示例**:

```python
# 好的示例: 使用自定义异常
class CookieError(Exception):
    """Cookie相关异常"""
    pass


def get_cookie():
    if not cookie:
        raise CookieError("Cookie获取失败")
    return cookie

# 不好的示例: 使用通用异常
def get_cookie():
    if not cookie:
        raise Exception("Cookie获取失败")
    return cookie
```

---

## 二、命名约定

### 2.1 命名风格

| 类型     | 命名风格                      | 示例                  |
| -------- | ----------------------------- | --------------------- |
| 模块名   | 全小写,可包含下划线           | `cookie_handler.py`   |
| 包名     | 全小写,不包含下划线           | `dingtalk_downloader` |
| 类名     | 大驼峰命名法(PascalCase)      | `CookieHandler`       |
| 函数名   | 蛇形命名法(snake_case)        | `get_cookie`          |
| 变量名   | 蛇形命名法(snake_case)        | `cookie_data`         |
| 常量     | 全大写加下划线(CONSTANT_CASE) | `MAX_RETRY_COUNT`     |
| 私有成员 | 单下划线前缀                  | `_private_method`     |
| 魔术方法 | 双下划线前缀和后缀            | `__init__`            |

### 2.2 命名原则

#### 2.2.1 清晰性

- **使用有意义的名称**: 名称应该表达意图
- **避免缩写**: 除非是广泛接受的缩写
- **避免单字母**: 除了循环变量

**示例**:

```python
# 好的示例: 清晰的命名
def get_user_by_id(user_id: int) -> User:
    pass

cookie_data = CookieData(cookies)

# 不好的示例: 不清晰的命名
def get_u(uid: int) -> User:
    pass

cd = CookieData(cookies)
```

#### 2.2.2 一致性

- **保持命名风格一致**: 同类事物使用相同的命名风格
- **遵循Python惯例**: 使用Python社区接受的命名方式

**示例**:

```python
# 好的示例: 一致的命名
class CookieHandler:
    def get_cookie(self):
        pass

    def set_cookie(self):
        pass

# 不好的示例: 不一致的命名
class CookieHandler:
    def get_cookie(self):
        pass

    def SetCookie(self):
        pass
```

#### 2.2.3 避免保留字

- **避免使用Python保留字**: 如`class`、`def`、`return`等
- **避免使用内置函数名**: 如`list`、`dict`、`str`等

**示例**:

```python
# 好的示例: 避免保留字
class MyClass:
    pass

def my_function():
    pass

# 不好的示例: 使用保留字
class = MyClass
def = my_function
```

---

## 三、注释要求

### 3.1 注释原则

1. **解释为什么,而不是什么**: 代码应该自解释,注释解释原因
2. **保持注释更新**: 代码变更时同步更新注释
3. **避免冗余注释**: 不要重复代码已经表达的内容
4. **使用中文注释**: 便于团队理解

### 3.2 文档字符串

#### 3.2.1 模块文档字符串

每个模块都应该有文档字符串:

```python
"""
Cookie处理器模块

本模块负责通过浏览器自动化获取Cookie和请求头信息。
"""

from typing import Dict, List
```

#### 3.2.2 类文档字符串

每个类都应该有文档字符串:

```python
class CookieHandler:
    """Cookie处理器

    通过浏览器自动化获取Cookie和请求头信息。

    Attributes:
        browser_type: 浏览器类型
        driver: 浏览器驱动实例
    """

    def __init__(self, browser_type: str):
        pass
```

#### 3.2.3 函数文档字符串

每个公共函数都应该有文档字符串,遵循Google风格:

```python
def get_cookie(self, url: str) -> CookieData:
    """获取Cookie和请求头

    通过浏览器自动化获取指定URL的Cookie和请求头信息。

    Args:
        url: 目标URL

    Returns:
        CookieData: 包含Cookie和请求头的数据对象

    Raises:
        CookieError: Cookie获取失败时抛出

    Examples:
        >>> handler = CookieHandler("edge")
        >>> cookie_data = handler.get_cookie("https://example.com")
        >>> print(cookie_data.cookies)
    """
    pass
```

### 3.3 行内注释

#### 3.3.1 块注释

- **使用完整的句子**: 首字母大写
- **与代码对齐**: 缩进与代码相同
- **注释前空一行**: 与代码之间空一行

**示例**:

```python
# 好的示例: 块注释
def process_data(data):
    # 验证数据格式
    if not isinstance(data, dict):
        raise ValueError("数据必须是字典类型")

    # 处理数据
    result = transform(data)
    return result
```

#### 3.3.2 行内注释

- **与代码间隔两个空格**
- **解释复杂逻辑**
- **避免显而易见的注释**

**示例**:

```python
# 好的示例: 行内注释
result = x * y + z  # 计算加权平均值

# 不好的示例: 显而易见的注释
result = x + y  # 相加
```

### 3.4 TODO注释

使用TODO注释标记待办事项:

```python
# TODO: 添加重试机制
# FIXME: 修复内存泄漏问题
# XXX: 需要优化性能
# HACK: 临时解决方案,需要重构
```

---

## 四、提交信息格式

### 4.1 提交信息格式

遵循 `<type>(<scope>): <subject>` 格式:

```text
<type>(<scope>): <subject>

<body>

<footer>
```

### 4.2 Type类型

| Type     | 说明                      | 示例                               |
| -------- | ------------------------- | ---------------------------------- |
| feat     | 新功能                    | feat(downloader): 添加批量下载功能 |
| fix      | Bug修复                   | fix(cookie): 修复Cookie过期问题    |
| docs     | 文档更新                  | docs(readme): 更新使用说明         |
| style    | 代码格式调整(不影响功能)  | style(format): 统一代码格式        |
| refactor | 重构(不新增功能不修复bug) | refactor(parser): 重构M3U8解析器   |
| test     | 补充测试                  | test(models): 添加CookieData测试   |
| chore    | 构建/依赖调整             | chore(deps): 升级selenium版本      |

### 4.3 Scope范围

Scope填写模块名、功能名,简洁明了:

- `downloader`: 下载器
- `cookie`: Cookie处理
- `parser`: M3U8解析
- `browser`: 浏览器自动化
- `config`: 配置管理
- `utils`: 工具函数

### 4.4 Subject主题

- **首字母小写**
- **末尾无标点**
- **长度控制在50字符以内**
- **描述具体变更内容**

### 4.5 Body正文

- **详细说明变更内容**
- **使用列表说明**
- **每行不超过72字符**

### 4.6 Footer页脚

- **关联Issue**: `Closes #123`
- **破坏性变更**: `BREAKING CHANGE:`

### 4.7 提交信息示例

#### 示例1: 新功能

```text
feat(downloader): 添加批量下载功能

- 支持从CSV/Excel文件读取链接
- 支持批量下载多个视频
- 添加下载进度显示
- 优化错误处理机制

Closes #45
```

#### 示例2: Bug修复

```text
fix(cookie): 修复Cookie过期导致下载失败的问题

- 检测Cookie有效期
- 自动刷新过期Cookie
- 添加重试机制

Fixes #67
```

#### 示例3: 文档更新

```text
docs(readme): 更新安装说明

- 添加Windows安装步骤
- 更新依赖版本要求
- 补充常见问题解答
```

#### 示例4: 重构

```text
refactor(parser): 重构M3U8解析器

- 提取公共逻辑为独立方法
- 优化错误处理
- 提高代码可读性
```

---

## 五、代码审查标准

### 5.1 审查原则

1. **建设性**: 提供建设性的反馈
2. **及时性**: 及时响应审查请求
3. **全面性**: 全面审查代码变更
4. **礼貌性**: 保持礼貌和尊重

### 5.2 审查检查清单

#### 5.2.1 功能性

- [ ] 功能是否正确实现
- [ ] 是否满足需求
- [ ] 边界条件是否处理
- [ ] 异常情况是否处理

#### 5.2.2 代码质量

- [ ] 代码风格是否一致
- [ ] 命名是否清晰
- [ ] 注释是否充分
- [ ] 是否有重复代码
- [ ] 是否有代码坏味道

#### 5.2.3 测试

- [ ] 是否有单元测试
- [ ] 测试覆盖率是否达标
- [ ] 测试是否充分
- [ ] 是否有集成测试

#### 5.2.4 性能

- [ ] 是否有性能问题
- [ ] 是否有内存泄漏
- [ ] 是否有优化空间

#### 5.2.5 安全

- [ ] 是否有安全漏洞
- [ ] 是否有敏感信息泄露
- [ ] 输入是否验证

### 5.3 审查流程

#### 5.3.1 提交审查

1. 提交Pull Request
2. 填写PR描述
3. 指定审查者

#### 5.3.2 审查代码

1. 查看代码变更
2. 运行测试
3. 检查代码质量
4. 提供审查意见

#### 5.3.3 修改代码

1. 根据审查意见修改代码
2. 更新测试
3. 提交修改

#### 5.3.4 合并代码

1. 确认所有审查意见已解决
2. 确认测试通过
3. 合并到主分支

### 5.4 审查意见示例

#### 示例1: 建议改进

```text
建议:
- 函数名可以更清晰,建议改为`get_cookie_with_retry`
- 添加异常处理,避免程序崩溃
- 补充单元测试
```

#### 示例2: 必须修改

```text
必须修改:
- 存在安全漏洞,需要验证输入
- 测试覆盖率不足,需要补充测试
- 代码风格不一致,需要调整
```

#### 示例3: 赞扬

```text
做得好:
- 代码结构清晰,易于理解
- 测试覆盖充分
- 文档完善
```

---

## 六、测试规范

### 6.1 测试原则

1. **测试驱动开发**: 先写测试,再写代码
2. **独立测试**: 每个测试应该独立运行
3. **快速测试**: 测试应该快速执行
4. **可读性**: 测试代码应该易于理解

### 6.2 测试组织

#### 6.2.1 测试文件组织

- **测试文件**: 放在 `tests/unit/` 目录下
- **命名格式**: `test_<模块名>.py`
- **测试类**: `Test<类名>`
- **测试方法**: `test_<方法名>`

**示例**:

```python
# tests/unit/test_models.py
import pytest
from dingtalk_downloader.utils.models import CookieData


class TestCookieData:
    """测试CookieData类"""

    def test_create_cookie_data(self):
        """测试创建CookieData"""
        cookies = {"key1": "value1"}
        cookie_data = CookieData(cookies)
        assert cookie_data.cookies == cookies

    def test_to_dict(self):
        """测试to_dict方法"""
        cookies = {"key1": "value1"}
        cookie_data = CookieData(cookies)
        result = cookie_data.to_dict()
        assert result == cookies
```

#### 6.2.2 测试分类

- **单元测试**: 测试单个函数或类
- **集成测试**: 测试多个模块的集成
- **端到端测试**: 测试整个流程

### 6.3 测试编写

#### 6.3.1 测试结构

使用AAA模式(Arrange-Act-Assert):

```python
def test_function():
    # Arrange: 准备测试数据
    input_data = {"key": "value"}

    # Act: 执行被测试的代码
    result = process(input_data)

    # Assert: 验证结果
    assert result == expected
```

#### 6.3.2 测试覆盖

- **正常情况**: 测试正常输入
- **边界情况**: 测试边界值
- **异常情况**: 测试异常输入

**示例**:

```python
class TestCalculator:
    """测试计算器"""

    def test_add_normal(self):
        """测试正常加法"""
        result = add(1, 2)
        assert result == 3

    def test_add_zero(self):
        """测试加零"""
        result = add(5, 0)
        assert result == 5

    def test_add_negative(self):
        """测试负数加法"""
        result = add(-1, -2)
        assert result == -3

    def test_add_invalid_input(self):
        """测试无效输入"""
        with pytest.raises(TypeError):
            add("a", "b")
```

#### 6.3.3 使用Mock

隔离外部依赖:

```python
import pytest
from unittest.mock import Mock, patch


class TestCookieHandler:
    """测试CookieHandler"""

    @patch('dingtalk_downloader.core.cookie_handler.webdriver')
    def test_get_cookie_success(self, mock_webdriver):
        """测试成功获取Cookie"""
        mock_driver = Mock()
        mock_webdriver.Chrome.return_value = mock_driver
        mock_driver.get_cookies.return_value = [
            {"name": "key1", "value": "value1"}
        ]

        handler = CookieHandler("chrome")
        cookie_data = handler.get_cookie("https://example.com")

        assert cookie_data.cookies == {"key1": "value1"}
```

### 6.4 测试运行

#### 6.4.1 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/unit/test_models.py

# 运行特定测试函数
pytest tests/unit/test_models.py::TestCookieData::test_create_cookie_data

# 显示详细输出
pytest -v

# 显示覆盖率
pytest --cov=src/dingtalk_downloader
```

#### 6.4.2 测试覆盖率

- **目标覆盖率**: 90%以上
- **查看覆盖率报告**: `pytest --cov-report=html`
- **提高覆盖率**: 为未覆盖的代码编写测试

---

## 七、文档规范

### 7.1 文档原则

1. **及时更新**: 代码变更后同步更新文档
2. **准确无误**: 确保文档内容准确
3. **易于理解**: 使用清晰的语言
4. **结构清晰**: 文档结构清晰,易于导航

### 7.2 文档类型

#### 7.2.1 README.md

项目说明文档,包含:

- 项目简介
- 功能特性
- 安装步骤
- 使用方法
- 常见问题
- 贡献指南

#### 7.2.2 API文档

API接口文档,包含:

- 接口说明
- 参数说明
- 返回值说明
- 使用示例
- 异常说明

#### 7.2.3 架构文档

系统架构文档,包含:

- 系统架构图
- 模块划分
- 核心组件交互
- 技术栈选型

#### 7.2.4 开发指南

开发指南文档,包含:

- 环境搭建
- 开发流程
- 常用命令
- 调试技巧

### 7.3 文档编写

#### 7.3.1 使用Markdown

使用Markdown格式编写文档:

````markdown
# 标题

## 二级标题

### 三级标题

- 列表项1
- 列表项2

1. 有序列表项1
2. 有序列表项2

**粗体文本**
_斜体文本_

`代码`

```python
代码块
```
````

[链接文本](https://example.com)

````

#### 7.3.2 添加示例

为复杂功能添加使用示例:

```python
# 示例: 获取Cookie
from dingtalk_downloader.core.cookie_handler import CookieHandler

handler = CookieHandler("edge")
cookie_data = handler.get_cookie("https://example.com")
print(cookie_data.cookies)
````

#### 7.3.3 保持简洁

- **避免冗余**: 删除不必要的内容
- **突出重点**: 使用加粗、列表等方式突出重点
- **结构清晰**: 使用标题、列表等组织内容

---

## 总结

本文档定义了钉钉直播回放下载工具的开发规范,包括代码风格、命名约定、注释要求、提交信息格式及代码审查标准。遵循这些规范可以确保团队协作的代码质量和一致性。

关键要点:

1. **代码风格**: 遵循PEP 8规范,使用Black自动格式化
2. **命名约定**: 使用有意义的名称,保持一致性
3. **注释要求**: 解释为什么,而不是什么
4. **提交信息**: 遵循`<type>(<scope>): <subject>`格式
5. **代码审查**: 全面审查代码变更,提供建设性反馈
6. **测试规范**: 编写充分的测试,目标覆盖率90%以上
7. **文档规范**: 及时更新文档,保持准确和清晰

遵循这些规范,可以提高代码质量,促进团队协作,降低维护成本。
