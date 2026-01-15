# 日志系统集成 - 对齐文档

## 项目上下文分析

### 项目结构

- **项目名称**: DingTalk-Live-Playback-Download-Tool
- **项目类型**: 钉钉直播回放下载工具
- **技术栈**: Python 3.8+, Selenium, pandas, openpyxl
- **架构模式**: 分层架构（浏览器层、核心层、工具层、配置层）

### 核心模块分析

1. **主程序入口** ([main.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/main.py))

   - 负责用户交互和模式选择
   - 协调单视频下载和批量下载

2. **下载器核心** ([downloader.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/core/downloader.py))

   - 协调 Cookie 获取、m3u8 解析、视频下载
   - 管理下载流程和资源释放

3. **Cookie 处理器** ([cookie_handler.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/core/cookie_handler.py))

   - 通过浏览器自动化获取 Cookie
   - 获取请求头和直播名称

4. **m3u8 解析器** ([m3u8_parser.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/core/m3u8_parser.py))

   - 从浏览器网络日志提取 m3u8 链接
   - 下载 m3u8 文件并提取基础 URL

5. **浏览器驱动层**

   - [browser_factory.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/browser/browser_factory.py): 浏览器工厂
   - [edge_driver.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/browser/edge_driver.py): Edge 浏览器驱动
   - [chrome_driver.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/browser/chrome_driver.py): Chrome 浏览器驱动
   - [firefox_driver.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/browser/firefox_driver.py): Firefox 浏览器驱动

6. **工具层**

   - [file_reader.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/utils/file_reader.py): 文件读取
   - [validator.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/utils/validator.py): 输入验证
   - [path_helper.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/utils/path_helper.py): 路径处理

7. **配置层**

   - [constants.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/config/constants.py): 常量定义
   - [settings.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/config/settings.py): 配置管理

8. **二进制工具封装**
   - [n_m3u8dl_re.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/binary/n_m3u8dl_re.py): N_m3u8DL-RE 工具调用

### 现有代码模式

- 使用 try-except 进行异常捕获
- 使用 print() 进行信息输出
- 无结构化日志系统
- 无日志级别控制
- 无日志文件持久化

## 原始需求

对程序的实现逻辑进行系统性深度分析，包括但不限于核心算法流程、模块间交互机制、数据处理路径及异常处理策略。在完成逻辑梳理后，在以下关键位置添加结构化日志记录：

1. 程序入口与出口
2. 核心函数/方法的调用与返回
3. 条件分支关键节点
4. 循环执行状态
5. 数据转换/处理前后
6. 异常捕获与处理位置
7. 资源分配与释放操作

日志内容应包含时间戳、日志级别、模块标识、关键参数值、执行状态及结果信息，确保日志格式统一规范以便于后续调试分析。添加的日志需兼顾调试信息量与系统性能影响，避免过度冗余。

## 需求理解

### 任务边界确认

- **包含**: 在现有代码中添加结构化日志记录
- **不包含**: 修改核心业务逻辑、重构代码结构、添加新功能

### 核心算法流程分析

#### 单视频下载流程

1. 用户输入链接、保存模式、浏览器类型
2. 创建 Downloader 实例
3. 调用 download_single_video()
4. CookieHandler 获取 Cookie 和请求头
5. M3u8Parser 提取 m3u8 链接
6. 下载 m3u8 文件
7. 调用 N_m3u8DL-RE 下载视频
8. 循环支持继续输入新链接

#### 批量下载流程

1. 用户输入文件路径、保存模式、浏览器类型
2. FileReader 读取链接
3. 创建 Downloader 实例
4. 调用 download_batch_videos()
5. 对每个链接重复单视频下载流程
6. 支持继续输入新文件

#### 模块间交互机制

- **main.py** → **downloader.py**: 创建下载器实例
- **downloader.py** → **cookie_handler.py**: 获取 Cookie 和请求头
- **downloader.py** → **m3u8_parser.py**: 提取 m3u8 链接
- **downloader.py** → **n_m3u8dl_re.py**: 下载视频
- **cookie_handler.py** → **browser_factory.py**: 创建浏览器实例
- **browser_factory.py** → **edge/chrome/firefox_driver.py**: 创建具体浏览器驱动

#### 数据处理路径

1. **输入数据**: 用户输入的 URL、文件路径、选项
2. **Cookie 数据**: 从浏览器提取的 Cookie 字典
3. **请求头数据**: User-Agent、Referer 等请求头
4. **m3u8 数据**: 从网络日志提取的 m3u8 链接
5. **视频数据**: 通过 N_m3u8DL-RE 下载的视频文件

#### 异常处理策略

- **KeyboardInterrupt**: 用户中断，优雅退出
- **Exception**: 通用异常捕获，打印错误信息
- **sys.exit(0/1)**: 程序退出
- **资源释放**: close() 方法关闭浏览器

## 疑问澄清

### 已明确的问题

1. **日志库选择**: 使用 Python 标准库 `logging`，无需额外依赖
2. **日志级别**: DEBUG、INFO、WARNING、ERROR、CRITICAL
3. **日志格式**: 时间戳、日志级别、模块标识、消息
4. **日志输出**: 同时输出到控制台和文件
5. **日志文件位置**: 项目根目录下的 `logs` 目录

### 需要确认的问题

1. **日志文件命名**: 是否需要按日期分割日志文件？
2. **日志文件大小限制**: 是否需要限制单个日志文件大小？
3. **日志保留策略**: 是否需要自动清理旧日志？
4. **日志级别配置**: 是否需要支持通过配置文件动态调整日志级别？
5. **敏感信息过滤**: 是否需要过滤 Cookie 等敏感信息？

### 基于现有项目的决策

1. **日志文件命名**: 按日期分割，格式为 `dingtalk_downloader_YYYY-MM-DD.log`
2. **日志文件大小限制**: 单个文件最大 10MB，超过后自动创建新文件
3. **日志保留策略**: 保留最近 30 天的日志文件
4. **日志级别配置**: 默认 INFO 级别，支持通过环境变量 `LOG_LEVEL` 调整
5. **敏感信息过滤**: 过滤 Cookie 值，只记录 Cookie 名称和数量

## 项目特性规范

### 代码规范

- 遵循现有代码风格（100 字符行长度）
- 使用类型注解
- 添加中文注释说明关键逻辑

### 技术约束

- 使用 Python 标准库 `logging`
- 不引入新的第三方依赖
- 保持现有 API 接口不变
- 确保向后兼容

### 集成方案

- 创建统一的日志配置模块 `logger_config.py`
- 在各模块中导入并使用统一的 logger
- 在 `__init__.py` 中初始化日志系统
- 确保日志系统在程序启动时初始化

### 质量要求

- 日志信息简洁明了，避免冗余
- 关键节点必须有日志记录
- 异常处理位置必须记录错误详情
- 资源分配和释放必须记录
