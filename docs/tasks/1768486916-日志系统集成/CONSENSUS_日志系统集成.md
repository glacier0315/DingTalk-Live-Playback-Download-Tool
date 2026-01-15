# 日志系统集成 - 共识文档

## 明确的需求描述

### 需求概述
在钉钉直播回放下载工具中集成结构化日志系统，在关键位置添加日志记录，提升程序的可调试性和可维护性。

### 验收标准
1. 创建统一的日志配置模块 `logger_config.py`
2. 在所有关键位置添加结构化日志记录
3. 日志格式统一，包含时间戳、日志级别、模块标识、关键参数值、执行状态及结果信息
4. 日志同时输出到控制台和文件
5. 日志文件按日期分割，自动管理
6. 不影响现有功能和性能
7. 所有测试通过

## 技术实现方案

### 日志系统架构
```
src/dingtalk_downloader/
├── config/
│   ├── __init__.py
│   ├── constants.py
│   ├── settings.py
│   └── logger_config.py  # 新增：日志配置模块
```

### 日志配置模块设计
- 使用 Python 标准库 `logging`
- 支持多级别日志（DEBUG、INFO、WARNING、ERROR、CRITICAL）
- 同时输出到控制台和文件
- 按日期分割日志文件
- 自动清理过期日志文件
- 支持环境变量 `LOG_LEVEL` 动态调整日志级别

### 日志格式规范
```
[时间戳] [日志级别] [模块名] 消息内容
示例: [2025-01-15 10:30:45,123] [INFO] [main] 程序启动
```

### 关键日志位置清单

#### 1. 程序入口与出口
- [main.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/main.py)
  - `main()` 函数入口
  - `main()` 函数出口
  - `single_mode()` 函数入口和出口
  - `batch_mode()` 函数入口和出口

#### 2. 核心函数/方法的调用与返回
- [downloader.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/core/downloader.py)
  - `Downloader.__init__()`: 初始化参数
  - `Downloader.download_single_video()`: 调用和返回
  - `Downloader.download_batch_videos()`: 调用和返回
  - `Downloader._download_video()`: 调用和返回
  - `Downloader.close()`: 资源释放

- [cookie_handler.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/core/cookie_handler.py)
  - `CookieHandler.get_cookie()`: 调用和返回
  - `CookieHandler.repeat_get_cookie()`: 调用和返回
  - `CookieHandler.close()`: 资源释放

- [m3u8_parser.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/core/m3u8_parser.py)
  - `M3u8Parser.fetch_m3u8_links()`: 调用和返回
  - `M3u8Parser.download_m3u8_file()`: 调用和返回
  - `M3u8Parser.extract_prefix()`: 调用和返回

- [n_m3u8dl_re.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/binary/n_m3u8dl_re.py)
  - `NM3u8DLRE.download()`: 调用和返回

#### 3. 条件分支关键节点
- [main.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/main.py)
  - 下载模式选择
  - 保存模式选择
  - 浏览器类型选择

- [downloader.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/core/downloader.py)
  - m3u8 链接获取成功/失败
  - 保存模式判断
  - 用户取消下载

- [cookie_handler.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/core/cookie_handler.py)
  - 直播名称获取成功/失败（XPath/CSS 选择器）

#### 4. 循环执行状态
- [downloader.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/core/downloader.py)
  - 单视频下载循环（继续输入新链接）
  - 批量下载循环（遍历链接列表）
  - 继续下载循环（继续输入新文件）

- [m3u8_parser.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/core/m3u8_parser.py)
  - m3u8 链接提取重试循环

#### 5. 数据转换/处理前后
- [cookie_handler.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/core/cookie_handler.py)
  - Cookie 列表转换为字典
  - 请求头构建

- [m3u8_parser.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/core/m3u8_parser.py)
  - URL 解析提取 liveUuid
  - m3u8 链接提取和清理
  - 基础 URL 提取

- [n_m3u8dl_re.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/binary/n_m3u8dl_re.py)
  - Cookie 字典转换为字符串
  - 下载命令构建

- [file_reader.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/utils/file_reader.py)
  - 文件路径清理
  - DataFrame 链接提取

#### 6. 异常捕获与处理位置
- [main.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/main.py)
  - `single_mode()` 异常捕获
  - `batch_mode()` 异常捕获
  - `main()` 异常捕获

- [downloader.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/core/downloader.py)
  - `download_single_video()` 异常捕获
  - `download_batch_videos()` 异常捕获

- [cookie_handler.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/core/cookie_handler.py)
  - `get_cookie()` 异常捕获
  - `repeat_get_cookie()` 异常捕获
  - `_get_live_name()` 异常捕获

- [m3u8_parser.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/core/m3u8_parser.py)
  - `fetch_m3u8_links()` 异常捕获
  - `download_m3u8_file()` 异常捕获

- [file_reader.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/utils/file_reader.py)
  - `read_links()` 异常捕获
  - `_read_csv()` 异常捕获

#### 7. 资源分配与释放操作
- [browser_factory.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/browser/browser_factory.py)
  - 浏览器实例创建

- [edge_driver.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/browser/edge_driver.py)
  - `create_driver()`: 浏览器驱动创建
  - `close()`: 浏览器驱动关闭

- [chrome_driver.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/browser/chrome_driver.py)
  - `create_driver()`: 浏览器驱动创建
  - `close()`: 浏览器驱动关闭

- [firefox_driver.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/browser/firefox_driver.py)
  - `create_driver()`: 浏览器驱动创建
  - `close()`: 浏览器驱动关闭

- [downloader.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/core/downloader.py)
  - `close()`: 浏览器资源释放

- [cookie_handler.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/core/cookie_handler.py)
  - `close()`: 浏览器资源释放

## 技术约束

### 依赖约束
- 使用 Python 标准库 `logging`
- 不引入新的第三方依赖
- 保持现有依赖不变

### 兼容性约束
- 保持现有 API 接口不变
- 确保向后兼容
- 不影响现有功能

### 性能约束
- 日志记录不应影响程序性能
- 避免过度冗余的日志
- 使用异步日志写入（可选）

## 集成方案

### 模块集成
1. 在 `config` 目录下创建 `logger_config.py`
2. 在 `config/__init__.py` 中导出日志配置
3. 在各模块中导入并使用统一的 logger
4. 在 `main.py` 中初始化日志系统

### 日志初始化
```python
# 在 main.py 顶部
from dingtalk_downloader.config.logger_config import setup_logging
setup_logging()
```

### 日志使用
```python
# 在各模块中
import logging
logger = logging.getLogger(__name__)

logger.info("程序启动")
logger.error(f"发生错误: {e}")
```

## 任务边界限制

### 包含范围
- 创建日志配置模块
- 在关键位置添加日志记录
- 日志文件管理
- 日志级别控制

### 不包含范围
- 修改核心业务逻辑
- 重构代码结构
- 添加新功能
- 创建日志分析工具

## 验收标准

### 功能验收
1. 日志系统正常工作
2. 所有关键位置都有日志记录
3. 日志格式统一规范
4. 日志文件正常生成和管理
5. 程序功能正常

### 质量验收
1. 代码符合项目规范
2. 日志信息简洁明了
3. 无过度冗余的日志
4. 敏感信息已过滤
5. 所有测试通过

### 性能验收
1. 日志记录不影响程序性能
2. 日志文件大小可控
3. 日志写入不影响主流程

## 确认所有不确定性已解决

### 已确认事项
1. ✅ 使用 Python 标准库 `logging`
2. ✅ 日志级别：DEBUG、INFO、WARNING、ERROR、CRITICAL
3. ✅ 日志格式：时间戳、日志级别、模块标识、消息
4. ✅ 日志输出：控制台和文件
5. ✅ 日志文件位置：`logs` 目录
6. ✅ 日志文件命名：按日期分割
7. ✅ 日志文件大小限制：10MB
8. ✅ 日志保留策略：30 天
9. ✅ 日志级别配置：环境变量 `LOG_LEVEL`
10. ✅ 敏感信息过滤：Cookie 值过滤

### 无遗留问题
所有关键决策点已确认，可以进入架构设计阶段。
