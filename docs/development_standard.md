# 项目开发规范

本文档定义了钉钉直播回放下载工具项目的完整开发规范，所有开发人员必须严格遵循，以确保代码质量和项目可维护性。

## 一、命名规范（遵循 PEP 8）

### 1. 文件名/目录名

- **规范**：小写字母+下划线
- **示例**：
  - `binary_handler.py` ✅
  - `core_module/` ✅
  - `download_manager.py` ✅
  - `BinaryHandler.py` ❌
  - `downloadManager.py` ❌

### 2. 变量/函数名

- **规范**：小写字母+下划线（蛇形命名）
- **示例**：
  - `binary_file_path` ✅
  - `execute_binary_task()` ✅
  - `get_browser_cookie()` ✅
  - `binaryFilePath` ❌
  - `executeBinaryTask()` ❌

### 3. 类名

- **规范**：大驼峰命名（PascalCase）
- **示例**：
  - `BinaryProcessor` ✅
  - `DownloadManager` ✅
  - `CookieHandler` ✅
  - `binary_processor` ❌
  - `binaryProcessor` ❌

### 4. 常量

- **规范**：全大写+下划线
- **示例**：
  - `BINARY_FILE_NAME = "xxx.bin"` ✅
  - `MAX_RETRY_COUNT = 5` ✅
  - `DEFAULT_BROWSER_TYPE = "edge"` ✅
  - `binary_file_name = "xxx.bin"` ❌
  - `MaxRetryCount = 5` ❌

### 5. 私有成员

- **规范**：前缀单下划线表示受保护成员，前缀双下划线表示私有成员
- **示例**：
  - `_internal_method()` ✅（受保护）
  - `__private_method()` ✅（私有）
  - `public_method()` ✅（公开）

### 6. 避免无意义命名

- **禁止使用**：`a`、`b`、`func1`、`temp`、`data`等无语义命名
- **推荐使用**：具有描述性的名称
  - `user_input` ✅
  - `download_url` ✅
  - `cookie_dict` ✅
  - `a` ❌
  - `func1` ❌
  - `temp` ❌

### 7. 特殊命名约定

- **布尔变量**：使用`is_`、`has_`、`can_`等前缀
  - `is_valid` ✅
  - `has_cookie` ✅
  - `can_download` ✅
- **集合变量**：使用复数形式
  - `links` ✅
  - `cookies` ✅
  - `headers` ✅
- **迭代变量**：在循环中使用有意义的名称
  - `for idx, link in enumerate(links):` ✅
  - `for i in range(len(links)):` ❌（除非索引确实需要）

## 二、注释规范

### 1. 模块注释

每个`.py`文件顶部必须添加模块说明，包含以下信息：

- **功能描述**：简要说明模块的功能
- **作者**：原作者或维护者
- **依赖**：主要依赖的外部库
- **创建日期**：文件创建日期
- **修改历史**：重要修改记录

**示例**：

```python
"""
钉钉直播回放下载工具 - 浏览器Cookie处理模块

本模块负责通过Selenium自动化浏览器获取钉钉直播回放的Cookie和请求头信息，
支持Edge、Chrome、Firefox三种浏览器。

作者：项目团队
依赖：selenium>=4.6.0
创建日期：2024-12-18
修改历史：
    - 2024-12-18: 初始版本
    - 2025-01-14: 添加Firefox浏览器支持
"""
```

### 2. 类注释

使用 Google 风格文档字符串，包含以下信息：

- **类描述**：类的功能和用途
- **属性**：重要属性的说明
- **方法**：主要方法的简要说明

**示例**：

```python
class BinaryProcessor:
    """
    二进制程序处理器，负责调用和管理外部二进制工具。

    该类封装了N_m3u8DL-RE和FFmpeg等二进制程序的调用逻辑，
    提供统一的接口供上层模块使用。

    Attributes:
        binary_path (str): 二进制程序的路径
        binary_name (str): 二进制程序的名称
        max_retries (int): 最大重试次数
    """

    def __init__(self, binary_path: str, max_retries: int = 3):
        """
        初始化二进制程序处理器。

        Args:
            binary_path: 二进制程序的绝对路径
            max_retries: 最大重试次数，默认为3

        Raises:
            FileNotFoundError: 当二进制程序文件不存在时
        """
        pass
```

### 3. 函数注释

使用 Google 风格文档字符串，包含以下信息：

- **功能描述**：函数的功能和用途
- **参数（Args）**：每个参数的名称、类型和说明
- **返回值（Returns）**：返回值的类型和说明
- **异常（Raises）**：可能抛出的异常及条件
- **示例（Examples）**：使用示例（可选）

**示例**：

```python
def get_browser_cookie(url: str, browser_type: str = 'edge') -> tuple:
    """
    获取浏览器Cookie和请求头信息。

    通过Selenium自动化浏览器访问指定URL，获取登录后的Cookie和请求头信息，
    用于后续的m3u8视频流下载。

    Args:
        url: 钉钉直播回放分享链接
        browser_type: 浏览器类型，可选值为'edge'、'chrome'、'firefox'，默认为'edge'

    Returns:
        tuple: 包含四个元素的元组
            - browser: Selenium浏览器实例
            - cookie_dict: Cookie字典，格式为{cookie_name: cookie_value}
            - headers: 请求头字典，包含User-Agent、Referer等
            - live_name: 直播视频名称

    Raises:
        Exception: 当浏览器启动失败或获取Cookie失败时
        TimeoutException: 当页面加载超时时

    Examples:
        >>> browser, cookies, headers, name = get_browser_cookie(
        ...     "https://n.dingtalk.com/xxx",
        ...     browser_type='edge'
        ... )
        >>> print(cookies)
        {'session_id': 'xxx', 'user_token': 'yyy'}
    """
    pass
```

### 4. 行内注释

- **原则**：仅为复杂逻辑添加注释，避免冗余注释
- **禁止**：注释显而易见的代码（如`a = 1 # 赋值1`）
- **推荐**：解释"为什么"而不是"是什么"

**示例**：

```python
# ❌ 错误示例：冗余注释
count = 0  # 初始化计数器为0
for link in links:  # 遍历所有链接
    count += 1  # 计数加1

# ✅ 正确示例：解释复杂逻辑
# 使用正则表达式从m3u8链接中提取基础URL
# 用于后续下载时构建完整的资源路径
pattern = re.compile(r'(https?://[^/]+/live_hp/[0-9a-f-]+)')
match = pattern.search(m3u8_url)
base_url = match.group(1) if match else m3u8_url
```

### 5. 注释语言

- **规范**：使用中文编写注释
- **例外**：技术术语、API 名称、变量名等保持英文
- **示例**：

  ```python
  # 获取浏览器Cookie  ✅
  # Get browser cookies  ❌（除非是国际化项目）
  ```

### 6. 注释工具

- **推荐**：借助 Trae IDE GLM-4.7 生成注释
- **要求**：保证格式统一，风格一致
- **流程**：
  1. 编写函数/类的基本逻辑
  2. 使用 Trae IDE 的 AI 功能生成注释
  3. 审查并调整注释，确保准确性和完整性
  4. 保持与现有注释风格一致

### 7. TODO 注释

- **格式**：`# TODO: [描述]`
- **用途**：标记待完成的功能或需要改进的代码
- **示例**：

  ```python
  # TODO: 添加对Safari浏览器的支持
  # TODO: 优化批量下载性能，考虑使用多线程
  ```

### 8. FIXME 注释

- **格式**：`# FIXME: [描述]`
- **用途**：标记需要修复的问题或已知的 bug
- **示例**：

  ```python
  # FIXME: 当前重试机制可能导致无限循环，需要添加最大重试次数限制
  ```

### 9. HACK 注释

- **格式**：`# HACK: [描述]`
- **用途**：标记临时解决方案或不够优雅的实现
- **示例**：

  ```python
  # HACK: 由于钉钉页面结构变化，暂时使用XPath获取直播名称
  # 后续需要寻找更稳定的方法
  live_name = browser.find_element(By.XPATH, '//*[@id="live-room"]/div[1]/div[1]/h3').text
  ```

### 10. 注释位置

- **模块注释**：文件顶部，在 import 语句之前
- **类注释**：类定义下方，缩进一级
- **函数注释**：函数定义下方，缩进一级
- **行内注释**：注释所在行的末尾或上一行，与代码对齐

**示例**：

```python
"""
模块注释
"""

import os
import sys


class MyClass:
    """类注释"""

    def my_method(self):
        """方法注释"""
        # 行内注释
        pass
```

## 三、项目结构规范（后续重构目标结构）

### 1. 根目录结构

```markdown
DingTalk-Live-Playback-Download-Tool/
├── src/ # 源代码目录（所有业务代码放入此处）
│ └── dingtalk_downloader/ # 项目包名（与项目名称一致，包含**init**.py）
│ ├── **init**.py # 包初始化文件，简化导入
│ ├── main.py # 程序入口文件
│ ├── core/ # 核心业务逻辑模块
│ │ ├── **init**.py
│ │ ├── downloader.py # 下载器核心逻辑
│ │ ├── cookie_handler.py # Cookie 处理逻辑
│ │ └── m3u8_parser.py # m3u8 解析逻辑
│ ├── utils/ # 工具函数模块
│ │ ├── **init**.py
│ │ ├── file_reader.py # 文件读取工具
│ │ ├── validator.py # 输入验证工具
│ │ └── path_helper.py # 路径处理工具
│ ├── binary/ # 二进制程序调用模块
│ │ ├── **init**.py
│ │ ├── n_m3u8dl_re.py # N_m3u8DL-RE 调用封装
│ │ └── ffmpeg_wrapper.py # FFmpeg 调用封装
│ ├── browser/ # 浏览器自动化模块
│ │ ├── **init**.py
│ │ ├── browser_factory.py # 浏览器工厂
│ │ ├── edge_driver.py # Edge 浏览器驱动
│ │ ├── chrome_driver.py # Chrome 浏览器驱动
│ │ └── firefox_driver.py # Firefox 浏览器驱动
│ └── config/ # 配置管理模块
│ ├── **init**.py
│ ├── settings.py # 配置项定义
│ └── constants.py # 常量定义
├── tests/ # 测试代码目录（与 src 目录结构对应）
│ ├── **init**.py
│ ├── unit/ # 单元测试
│ │ ├── **init**.py
│ │ ├── test_downloader.py
│ │ ├── test_cookie_handler.py
│ │ ├── test_file_reader.py
│ │ └── test_binary_handler.py
│ ├── integration/ # 集成测试
│ │ ├── **init**.py
│ │ └── test_download_flow.py
│ └── fixtures/ # 测试数据
│ ├── sample_links.csv
│ └── sample_links.xlsx
├── assets/ # 静态资源目录（存放外部二进制程序）
│ ├── N_m3u8DL-RE.exe # N_m3u8DL-RE 可执行文件
│ ├── N_m3u8DL-RE # N_m3u8DL-RE 可执行文件（Linux/macOS）
│ ├── ffmpeg.exe # FFmpeg 可执行文件
│ └── ffmpeg # FFmpeg 可执行文件（Linux/macOS）
├── scripts/ # 辅助脚本目录（验证、部署等）
│ ├── setup.py # 安装脚本
│ ├── validate_dependencies.py # 依赖验证脚本
│ └── build_exe.py # 打包为 exe 的脚本
├── docs/ # 文档目录
│ ├── project_status.md # 项目现状记录
│ ├── development_standard.md # 开发规范（本文件）
│ ├── api/ # API 文档
│ │ └── api_reference.md
│ ├── user_guide/ # 用户指南
│ │ └── usage_guide.md
│ └── foundation/ # 基础文档
│ ├── N_m3u8DL-RE.md
│ ├── ffmpeg.md
│ └── 钉钉视频下载记录.md
├── requirements.txt # 依赖清单
├── requirements-dev.txt # 开发依赖清单
├── .gitignore # Git 忽略文件
├── .env.example # 环境变量示例文件
├── README.md # 项目说明
├── LICENSE # 许可证
├── pyproject.toml # 项目配置文件（Python 3.6+）
└── setup.cfg # 安装配置文件
```

### 2. 目录职责说明

#### src/ 源代码目录

- **职责**：存放所有业务代码
- **原则**：所有可执行代码必须在 src 目录下
- **命名**：包名使用小写字母+下划线

#### tests/ 测试代码目录

- **职责**：存放所有测试代码
- **原则**：测试目录结构与 src 目录对应
- **命名**：测试文件以`test_`开头

#### assets/ 静态资源目录

- **职责**：存放外部二进制程序和静态资源
- **原则**：所有外部依赖的可执行文件统一管理
- **命名**：保持原始文件名

#### scripts/ 辅助脚本目录

- **职责**：存放辅助脚本（安装、部署、验证等）
- **原则**：脚本命名清晰，功能单一
- **命名**：使用动词开头，如`setup.py`、`validate.py`

#### docs/ 文档目录

- **职责**：存放所有项目文档
- **原则**：文档分类清晰，易于查找
- **命名**：使用小写字母+下划线

### 3. 模块组织原则

#### 单一职责原则

- 每个模块只负责一个功能领域
- 模块内部函数和类职责明确
- 避免模块间过度耦合

#### 依赖倒置原则

- 高层模块不依赖低层模块，都依赖抽象
- 通过接口定义模块间交互
- 便于单元测试和模块替换

#### 开闭原则

- 对扩展开放，对修改关闭
- 通过继承和接口扩展功能
- 避免修改已有代码

### 4. 导入规范

#### 导入顺序

1. 标准库导入
2. 第三方库导入
3. 本地应用/库导入

#### 导入分组

- 每组导入之间用空行分隔
- 同组导入按字母顺序排列

#### 示例

```python
# 标准库导入
import os
import sys
from pathlib import Path

# 第三方库导入
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

# 本地应用导入
from dingtalk_downloader.core.downloader import Downloader
from dingtalk_downloader.utils.file_reader import FileReader
```

#### 避免使用通配符导入

```python
# ❌ 错误示例
from module import *

# ✅ 正确示例
from module import function1, function2
```

#### 避免循环导入

- 通过重构模块结构解决循环导入
- 使用延迟导入（在函数内部导入）

### 5. 文件组织原则

#### 文件大小限制

- 单个 Python 文件不超过 500 行
- 超过 500 行考虑拆分为多个模块
- 保持文件职责单一

#### 类和函数组织

- 类定义按字母顺序排列
- 公共方法在前，私有方法在后
- 函数按逻辑分组，使用注释分隔

**示例**：

```python
class MyClass:
    """类文档字符串"""

    def __init__(self):
        """初始化方法"""
        pass

    # 公共方法
    def public_method1(self):
        """公共方法1"""
        pass

    def public_method2(self):
        """公共方法2"""
        pass

    # 私有方法
    def _private_method1(self):
        """私有方法1"""
        pass

    def _private_method2(self):
        """私有方法2"""
        pass
```

## 四、Git 提交信息规范（遵循 Conventional Commits）

### 1. 格式规范

```markdown
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### 2. Type（类型）可选值

#### refactor：重构

- **定义**：结构/代码优化，无功能变化
- **示例**：
  - `refactor(core): 拆分下载器模块，提高代码可维护性`
  - `refactor(utils): 提取文件读取逻辑到独立模块`
  - `refactor(binary): 统一二进制程序调用接口`

#### docs：文档修改

- **定义**：文档的添加、修改或删除
- **示例**：
  - `docs: 添加项目开发规范文档`
  - `docs(readme): 更新安装说明和使用指南`
  - `docs(api): 完善API文档`

#### chore：杂项操作

- **定义**：依赖、配置等不改变代码逻辑的操作
- **示例**：
  - `chore: 更新requirements.txt依赖版本`
  - `chore: 添加.gitignore规则`
  - `chore: 配置代码格式化工具`

#### test：添加/修改测试代码

- **定义**：测试代码的添加、修改或删除
- **示例**：
  - `test: 添加下载器单元测试`
  - `test(core): 修复Cookie处理测试用例`
  - `test(integration): 添加批量下载集成测试`

#### fix：修复 bug

- **定义**：修复代码中的 bug 或错误
- **示例**：
  - `fix(core): 修复m3u8链接提取失败问题`
  - `fix(browser): 解决Firefox浏览器兼容性问题`
  - `fix(utils): 修复Excel文件编码解析错误`

#### feat：新功能

- **定义**：添加新功能或特性
- **示例**：
  - `feat: 添加Firefox浏览器支持`
  - `feat(core): 实现断点续传功能`
  - `feat(utils): 支持从剪贴板读取链接`

#### style：代码风格修改

- **定义**：不影响代码逻辑的格式修改
- **示例**：
  - `style: 统一代码缩进和空格`
  - `style: 调整导入顺序`
  - `style: 优化注释格式`

#### perf：性能优化

- **定义**：提高代码性能的修改
- **示例**：
  - `perf: 优化批量下载速度`
  - `perf(core): 减少不必要的网络请求`
  - `perf(browser): 优化浏览器启动时间`

#### revert：回滚提交

- **定义**：回滚之前的提交
- **示例**：
  - `revert: 回滚feat: 添加Firefox浏览器支持`

### 3. Scope（范围）

- **定义**：提交影响的模块或功能区域
- **可选值**：
  - `core`：核心业务逻辑
  - `utils`：工具函数
  - `binary`：二进制程序调用
  - `browser`：浏览器自动化
  - `config`：配置管理
  - `test`：测试代码
  - `docs`：文档
  - `scripts`：辅助脚本

### 4. Description（描述）

- **语言**：使用中文
- **长度**：不超过 50 字
- **原则**：简洁明了，描述做了什么
- **示例**：
  - `refactor(core): 拆分下载器模块，提高代码可维护性` ✅
  - `fix(browser): 修复Edge浏览器Cookie获取失败问题` ✅
  - `docs: 添加API文档` ✅
  - `refactor(core): 修改了代码结构` ❌（太笼统）
  - `fix: 修复bug` ❌（太笼统）

### 5. Body（正文）

- **用途**：详细描述提交内容
- **格式**：每行不超过 72 个字符
- **内容**：
  - 修改原因
  - 修改内容
  - 影响范围
  - 注意事项

**示例**：

```markdown
refactor(core): 拆分下载器模块，提高代码可维护性

将原有的单文件下载器拆分为多个子模块：

- downloader.py: 核心下载逻辑
- cookie_handler.py: Cookie 处理逻辑
- m3u8_parser.py: m3u8 解析逻辑

主要改进：

1. 降低模块耦合度
2. 提高代码可测试性
3. 便于后续功能扩展

影响范围：

- 所有导入下载器的代码需要更新导入路径
- 单元测试需要相应调整
```

### 6. Footer（脚注）

- **用途**：关联 Issue、Breaking Change 等
- **格式**：
  - 关联 Issue：`Closes #123` 或 `Refs #123`
  - 破坏性变更：`BREAKING CHANGE: 详细描述`

**示例**：

```markdown
feat(core): 实现断点续传功能

添加断点续传支持，允许从中断处继续下载。

Closes #45
```

```markdown
refactor(api): 重构下载器接口

BREAKING CHANGE: 下载器接口参数顺序已调整，所有调用代码需要更新。
```

### 7. 完整示例

#### 示例 1：重构提交

```markdown
refactor(core): 拆分下载器模块，提高代码可维护性

将原有的单文件下载器拆分为多个子模块：

- downloader.py: 核心下载逻辑
- cookie_handler.py: Cookie 处理逻辑
- m3u8_parser.py: m3u8 解析逻辑

主要改进：

1. 降低模块耦合度
2. 提高代码可测试性
3. 便于后续功能扩展

影响范围：

- 所有导入下载器的代码需要更新导入路径
- 单元测试需要相应调整
```

#### 示例 2：修复提交

```markdown
fix(browser): 修复 Firefox 浏览器 Cookie 获取失败问题

问题原因：

- Firefox 浏览器的日志获取方式与 Chrome/Edge 不同
- 原有代码未正确处理 Firefox 的日志格式

解决方案：

- 使用 execute_script 获取 performance entries
- 通过正则表达式提取 m3u8 链接

测试验证：

- 在 Firefox 浏览器上测试通过
- Chrome 和 Edge 浏览器功能正常

Closes #78
```

#### 示例 3：功能提交

```markdown
feat(core): 实现断点续传功能

新增功能：

1. 支持从中断处继续下载
2. 自动检测已下载的分片
3. 跳过已完成的分片

实现方式：

- 在下载目录创建临时文件记录进度
- 每次下载前检查临时文件
- 根据进度恢复下载

用户体验：

- 减少重复下载时间
- 提高下载成功率
- 支持网络中断后继续

Closes #45
```

#### 示例 4：文档提交

```markdown
docs: 添加项目开发规范文档

新增文档：

- development_standard.md: 完整的开发规范
- 包含命名规范、注释规范、项目结构规范等

目的：

- 统一团队开发标准
- 提高代码质量
- 便于新成员快速上手
```

#### 示例 5：测试提交

```markdown
test(core): 添加下载器单元测试

新增测试用例：

1. test_download_single_video: 测试单个视频下载
2. test_download_batch_videos: 测试批量下载
3. test_resume_download: 测试断点续传

测试覆盖率：

- 下载器核心逻辑：85%
- Cookie 处理：90%
- m3u8 解析：80%

使用工具：

- pytest
- pytest-cov
- pytest-mock
```

### 8. 提交频率

- **原则**：小步提交，频繁提交
- **粒度**：每次提交只做一件事
- **时机**：
  - 完成一个功能点
  - 修复一个 bug
  - 完成一次重构
  - 添加/修改测试

### 9. 提交检查清单

提交前请确认：

- [ ] 提交信息符合格式规范
- [ ] 提交信息描述清晰准确
- [ ] 代码通过所有测试
- [ ] 代码符合开发规范
- [ ] 无敏感信息（如 API 密钥、密码等）
- [ ] 无调试代码和注释掉的代码
- [ ] 无不必要的文件（如临时文件、日志文件）

### 10. 分支管理规范

#### 分支命名

- `main`：主分支，用于生产环境
- `dev`：开发分支，用于集成开发
- `feature/<feature-name>`：功能分支
- `fix/<bug-name>`：修复分支
- `refactor/<refactor-name>`：重构分支

#### 分支策略

- 从`dev`分支创建功能分支
- 功能开发完成后合并回`dev`
- 定期将`dev`合并到`main`
- 使用 Pull Request 进行代码审查

**示例**：

```markdown
feature/add-firefox-support
fix/cookie-getting-failure
refactor/module-structure-optimization
```

## 五、代码质量规范

### 1. 代码格式化

- **工具**：使用`black`进行代码格式化
- **配置**：遵循默认配置
- **命令**：`black src/ tests/`

### 2. 代码检查

- **工具**：使用`flake8`进行代码检查
- **配置**：遵循 PEP 8 规范
- **命令**：`flake8 src/ tests/`

### 3. 类型检查

- **工具**：使用`mypy`进行类型检查
- **配置**：启用严格模式
- **命令**：`mypy src/`

### 4. 代码复杂度

- **工具**：使用`radon`检查代码复杂度
- **标准**：
  - 圈复杂度 <= 10
  - 认知复杂度 <= 15
- **命令**：`radon cc src/ -a`

### 5. 测试覆盖率

- **工具**：使用`pytest-cov`检查测试覆盖率
- **标准**：核心模块覆盖率 >= 80%
- **命令**：`pytest --cov=src --cov-report=html`

## 六、版本管理规范

### 1. 版本号格式

遵循语义化版本规范（Semantic Versioning）：

```markdown
MAJOR.MINOR.PATCH
```

- **MAJOR**：不兼容的 API 修改
- **MINOR**：向后兼容的功能性新增
- **PATCH**：向后兼容的问题修正

### 2. 版本发布流程

1. 更新版本号
2. 更新 CHANGELOG.md
3. 创建 Git 标签
4. 推送标签到远程仓库
5. 发布新版本

### 3. 示例

```markdown
1.0.0 -> 1.1.0 (新增功能)
1.1.0 -> 1.1.1 (修复 bug)
1.1.1 -> 2.0.0 (不兼容的 API 修改)
```

## 七、安全规范

### 1. 敏感信息管理

- **禁止**：将 API 密钥、密码等敏感信息提交到 Git
- **使用**：`.env`文件管理环境变量
- **示例**：`.env.example`提供模板

### 2. 依赖安全

- **定期**：检查依赖漏洞
- **工具**：使用`pip-audit`或`safety`
- **命令**：`pip-audit` 或 `safety check`

### 3. 输入验证

- **原则**：所有用户输入必须验证
- **内容**：
  - 文件路径验证
  - URL 格式验证
  - 参数范围验证
- **示例**：

  ```python
  def validate_url(url: str) -> bool:
      """验证URL格式"""
      if not url.startswith("https://n.dingtalk.com"):
          raise ValueError("无效的钉钉直播链接")
      return True
  ```

## 八、总结

本开发规范旨在：

1. **统一代码风格**：提高代码可读性和可维护性
2. **规范开发流程**：降低协作成本，提高开发效率
3. **保证代码质量**：通过规范和工具确保代码质量
4. **便于团队协作**：新成员快速上手，减少沟通成本

**重要提醒**：

- 所有开发人员必须严格遵循本规范
- 定期审查代码，确保规范执行
- 持续改进规范，适应项目发展
- 使用工具辅助规范执行（如 black、flake8 等）

**联系方式**：
## 五、代码格式化规范

### 1. Black 代码格式化工具

#### 1.1 工具介绍

Black 是 Python 社区广泛使用的代码格式化工具，具有以下特点：

- **一致性**：自动统一代码风格，消除代码风格争议
- **确定性**：相同的代码总是产生相同的格式化结果
- **自动化**：一键格式化，无需手动调整
- **标准性**：遵循 PEP 8 规范，是 Python 社区的标准工具

#### 1.2 安装和配置

Black 已集成到项目的开发依赖中，通过以下命令安装：

```bash
pip install -r requirements-dev.txt
```

配置文件位于项目根目录的 `pyproject.toml`，包含以下关键配置：

```toml
[tool.black]
line-length = 100                    # 行长度设置为 100 字符
target-version = ['py38']            # 目标 Python 版本为 3.8+
include = '\.pyi?$'                  # 包含 .py 和 .pyi 文件
exclude = '''                         # 排除目录和文件
/(
    \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''
```

#### 1.3 使用方法

##### 格式化当前文件

```bash
python -m black 文件名.py
```

##### 格式化整个项目

```bash
python -m black .
```

##### 检查代码格式（不修改文件）

```bash
python -m black --check .
```

##### 查看格式化差异（不修改文件）

```bash
python -m black --diff .
```

##### 格式化指定目录

```bash
python -m black src/
python -m black tests/
```

#### 1.4 开发流程集成

##### 代码提交前检查

在提交代码前，必须运行以下命令确保代码格式正确：

```bash
# 检查代码格式
python -m black --check .

# 如果检查通过，可以提交代码
git add .
git commit -m "feat: 添加新功能"
```

##### 代码格式化后提交

如果检查失败，运行以下命令格式化代码：

```bash
# 格式化代码
python -m black .

# 再次检查
python -m black --check .

# 提交代码
git add .
git commit -m "style: 格式化代码"
```

#### 1.5 代码格式化要求

**强制要求**：

1. **提交前必须格式化**：所有代码在提交前必须通过 Black 格式化检查
2. **不得手动调整**：格式化后的代码不得手动调整，除非有充分的理由
3. **CI/CD 检查**：代码合并前必须通过格式化检查（如果配置了 CI/CD）

**推荐实践**：

1. **定期格式化**：开发过程中定期运行格式化命令，保持代码风格一致
2. **IDE 集成**：配置 IDE 自动格式化，保存时自动运行 Black
3. **团队协作**：团队成员统一使用 Black，避免代码风格冲突

#### 1.6 常见问题

##### Q1: Black 格式化后的代码不符合我的习惯？

**A**: Black 的设计理念是"统一优于个人偏好"。团队统一使用 Black 可以避免代码风格争议，提高代码可读性。建议接受 Black 的格式化结果。

##### Q2: 某些代码不想被格式化怎么办？

**A**: 可以在代码中使用 `# fmt: off` 和 `# fmt: on` 注释来跳过格式化：

```python
# fmt: off
complex_dict = {
    'key1': 'value1',
    'key2': 'value2',
    # ...
}
# fmt: on
```

**注意**：这种用法应该谨慎使用，仅在必要时使用。

##### Q3: Black 改变了代码逻辑怎么办？

**A**: Black 只改变代码格式，不会改变代码逻辑。如果发现逻辑变化，请检查代码本身是否有问题。

##### Q4: 如何在 IDE 中集成 Black？

**A**: 主流 IDE 都支持 Black 集成：

- **VS Code**: 安装 "Black Formatter" 扩展，配置为默认格式化工具
- **PyCharm**: 安装 Black 插件，配置为代码格式化工具
- **Vim/Neovim**: 使用 `black` 插件或配置自动格式化

#### 1.7 格式化示例

##### 格式化前

```python
def calculate_total(items):
    total=0
    for item in items:
        total+=item['price']*item['quantity']
    return total
```

##### 格式化后

```python
def calculate_total(items):
    total = 0
    for item in items:
        total += item["price"] * item["quantity"]
    return total
```

主要变化：

- 运算符周围添加空格
- 单引号改为双引号
- 代码缩进和间距统一

### 2. 代码质量检查流程

#### 2.1 开发前检查

在开始开发新功能或修复 bug 前：

1. 拉取最新代码：`git pull`
2. 运行格式化检查：`python -m black --check .`
3. 运行测试：`pytest`

#### 2.2 开发中检查

在开发过程中：

1. 定期运行格式化：`python -m black .`
2. 定期运行测试：`pytest`
3. 确保代码符合项目规范

#### 2.3 提交前检查

在提交代码前：

1. 运行格式化：`python -m black .`
2. 运行格式化检查：`python -m black --check .`
3. 运行测试：`pytest`
4. 确保所有检查通过

#### 2.4 提交信息规范

提交信息应遵循 Git 提交信息规范（见第四部分），格式化相关的提交使用 `style` 类型：

```bash
git commit -m "style: 格式化代码"
```

如有疑问或建议，请联系项目维护者或在 Issue 中讨论。
