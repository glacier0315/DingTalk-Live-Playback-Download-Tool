# 日志优化任务 - 共识文档

## 需求描述

对钉钉直播回放下载工具的日志系统进行全面优化，包括：

1. **日志截断问题修复**

   - 全面检查并优化日志输出逻辑
   - 彻底去除任何可能导致字符串被截断的代码实现
   - 具体包括：
     - 审查日志格式化函数
     - 检查日志长度限制配置
     - 验证字符串拼接操作
     - 确保长文本、特殊字符和结构化数据都能完整记录

2. **print 语句替换**
   - 将代码中所有非用户交互场景的 print 输出语句统一修改为标准日志输出
   - 保留引导用户输入的 print 语句
   - 转换时需根据信息重要性合理设置日志级别（如 DEBUG、INFO、WARNING、ERROR）
   - 确保日志包含时间戳、模块信息和必要上下文

## 技术实现方案

### 1. 日志截断修复方案

#### 修复策略

- 去除所有字符串切片操作（如`[:50]`, `[:80]`）
- 确保 URL、链接、基础 URL 等长文本完整记录
- 不设置日志行长度限制

#### 修复位置

- **downloader.py**: 8 处截断

  - Line 78: `url[:50]` → `url`
  - Line 94: `link[:80]` → `link`
  - Line 101: `prefix[:80]` → `prefix`
  - Line 117: `url[:50]` → `url`
  - Line 168: `link[:80]` → `link`
  - Line 175: `prefix[:80]` → `prefix`
  - Line 197: `link[:80]` → `link`
  - Line 204: `prefix[:80]` → `prefix`

- **n_m3u8dl_re.py**: 1 处截断

  - Line 79: `command[:5]` → `command`

- **cookie_handler.py**: 4 处截断

  - Line 74: `url[:50]` → `url`
  - Line 90: `user_agent[:50]` → `user_agent`
  - Line 141: `url[:50]` → `url`
  - Line 160: `user_agent[:50]` → `user_agent`

- **main.py**: 1 处截断
  - Line 60: `dingtalk_url[:50]` → `dingtalk_url`

### 2. print 语句替换方案

#### 替换策略

- 识别所有非用户交互的 print 语句
- 根据信息重要性设置合适的日志级别
- 确保日志包含时间戳、模块信息和必要上下文
- 删除无用的分隔符 print 语句

#### 日志级别映射

| 信息类型 | 日志级别 | 示例                                    |
| -------- | -------- | --------------------------------------- |
| 调试信息 | DEBUG    | 获取到 m3u8 链接、处理日志、页面刷新    |
| 一般信息 | INFO     | 开始下载、下载完成、视频数量            |
| 警告信息 | WARNING  | headers 中没有 User-Agent、编码无法识别 |
| 错误信息 | ERROR    | 下载失败、读取失败、转换失败            |

#### 保留的 print 语句（用户交互）

- 欢迎信息
- 用户提示信息（如"请在浏览器中登录钉钉账户后，按 Enter 键继续..."）
- 程序终止信息（如"程序已退出。"）
- 错误提示信息（如"发生错误: {e}"）

#### 替换位置

- **main.py**: 2 处

  - Line 85: `print(f"发生错误: {e}")` → `logger.error(f"发生错误: {e}", exc_info=True)`
  - Line 121: `print(f"发生错误: {e}")` → `logger.error(f"发生错误: {e}", exc_info=True)`

- **downloader.py**: 8 处

  - Line 114: `print("=" * 100)` → 删除
  - Line 134: `print(f"共提取到 {total_links} 个钉钉直播回放分享链接。")` → `logger.info(f"共提取到 {total_links} 个钉钉直播回放分享链接")`
  - Line 143: `print(f"正在下载第 1 个视频，共 {total_links} 个视频。")` → `logger.info(f"正在下载第 1 个视频，共 {total_links} 个视频")`
  - Line 161: `print("=" * 100)` → 删除
  - Line 166: `print(f"正在下载第 {idx + 1} 个视频，共 {total_links} 个视频。")` → `logger.info(f"正在下载第 {idx + 1} 个视频，共 {total_links} 个视频")`
  - Line 184: `print("=" * 100)` → 删除
  - Line 195: `print(f"发生错误: {e}")` → `logger.error(f"发生错误: {e}", exc_info=True)`
  - Line 247: `print("无效的保存模式")` → `logger.error("无效的保存模式")`

- **n_m3u8dl_re.py**: 13 处

  - Line 98: `print(f"已添加 Cookie 请求头")` → `logger.debug("已添加 Cookie 请求头")`
  - Line 101: `print(f"已添加 User-Agent 请求头")` → `logger.debug("已添加 User-Agent 请求头")`
  - Line 102: `print("警告: headers 中没有 User-Agent")` → `logger.warning("headers 中没有 User-Agent")`
  - Line 105: `print(f"已添加 Referer 请求头")` → `logger.debug("已添加 Referer 请求头")`
  - Line 107: `print(f"已添加默认 Referer 请求头")` → `logger.debug("已添加默认 Referer 请求头")`
  - Line 110: `print(f"已添加 Accept 请求头")` → `logger.debug("已添加 Accept 请求头")`
  - Line 113: `print(f"已添加 Accept-Language 请求头")` → `logger.debug("已添加 Accept-Language 请求头")`
  - Line 116: `print(f"已添加 Accept-Encoding 请求头")` → `logger.debug("已添加 Accept-Encoding 请求头")`
  - Line 119: `print("已添加默认请求头")` → `logger.debug("已添加默认请求头")`
  - Line 121: `print(f"总共添加了 {len(headers_added)} 个请求头: {', '.join(headers_added)}")` → `logger.debug(f"总共添加了 {len(headers_added)} 个请求头: {', '.join(headers_added)}")`
  - Line 137: `print(f"下载视频时发生错误: {e}")` → `logger.error(f"下载视频时发生错误: {e}", exc_info=True)`

- **m3u8_parser.py**: 8 处

  - Line 76: `print("未能从 URL 提取 liveUuid，程序将退出。")` → `logger.error("未能从 URL 提取 liveUuid，程序将退出")`
  - Line 95: `print(f"获取到m3u8链接: {cleaned_link}")` → `logger.debug(f"获取到m3u8链接: {cleaned_link}")`
  - Line 104: `print(f"获取到m3u8链接: {m3u8_url}")` → `logger.debug(f"获取到m3u8链接: {m3u8_url}")`
  - Line 109: `print(f"处理日志时发生错误: {e}")` → `logger.error(f"处理日志时发生错误: {e}", exc_info=True)`
  - Line 113: `print(f"第 {attempt + 1} 次尝试未获取到 m3u8 链接，重试中...")` → `logger.warning(f"第 {attempt + 1} 次尝试未获取到 m3u8 链接，重试中")`
  - Line 116: `print(f"获取 m3u8 链接时发生错误: {e}")` → `logger.error(f"获取 m3u8 链接时发生错误: {e}", exc_info=True)`
  - Line 147: `print(f"下载 m3u8 文件时发生错误: {e}")` → `logger.error(f"下载 m3u8 文件时发生错误: {e}", exc_info=True)`
  - Line 156: `print("页面已刷新")` → `logger.debug("页面已刷新")`
  - Line 160: `print(f"刷新页面时发生错误: {e}")` → `logger.error(f"刷新页面时发生错误: {e}", exc_info=True)`

- **file_reader.py**: 2 处

  - Line 70: `print(f"文件 {self.file_path} 使用的编码无法识别，请尝试其他编码格式。")` → `logger.warning(f"文件 {self.file_path} 使用的编码无法识别，请尝试其他编码格式")`
  - Line 87: `print(f"读取文件时发生错误: {e}")` → `logger.error(f"读取文件时发生错误: {e}", exc_info=True)`

- **ffmpeg_wrapper.py**: 2 处

  - Line 52: `print(f"音视频转换成功完成。输出文件: {output_file}")` → `logger.info(f"音视频转换成功完成。输出文件: {output_file}")`
  - Line 56: `print(f"转换音视频时发生错误: {e}")` → `logger.error(f"转换音视频时发生错误: {e}", exc_info=True)`

- **logger_config.py**: 1 处

  - Line 83: `print(f"日志系统初始化失败: {e}")` → `logger.error(f"日志系统初始化失败: {e}", exc_info=True)`

- **settings.py**: 2 处
  - Line 44: `print(f"加载配置文件失败: {e}")` → `logger.error(f"加载配置文件失败: {e}", exc_info=True)`
  - Line 53: `print(f"保存配置文件失败: {e}")` → `logger.error(f"保存配置文件失败: {e}", exc_info=True)`

## 技术约束

### 1. 日志系统约束

- 使用标准库 logging 模块
- 保持现有日志架构不变
- 使用 CustomFormatter 格式化日志
- 使用 RotatingFileHandlerWithCleanup 处理文件

### 2. 代码规范约束

- 遵循项目现有代码规范
- 保持代码风格一致
- 添加必要的注释
- 不引入新的依赖库

### 3. 向后兼容约束

- 不破坏现有 API 接口
- 保持用户交互体验不变
- 确保现有测试通过

## 集成方案

### 1. 与现有系统集成

- 复用现有 LoggerConfig 类
- 复用现有 CustomFormatter 类
- 复用现有 RotatingFileHandlerWithCleanup 类

### 2. 日志格式统一

- 保持现有日志格式：`[YYYY-MM-DD HH:MM:SS.mmm] [LEVEL    ] [MODULE_NAME          ] MESSAGE`
- 包含时间戳、日志级别、模块名称、消息内容

### 3. 日志级别统一

- DEBUG: 详细调试信息
- INFO: 一般信息
- WARNING: 警告信息
- ERROR: 错误信息
- CRITICAL: 严重错误

## 任务边界限制

### 包含

1. 修复所有日志输出中的字符串截断问题
2. 将非用户交互的 print 语句替换为日志输出
3. 确保日志格式统一规范
4. 保持用户交互体验不变

### 不包含

1. 修改日志系统架构（保持现有架构）
2. 添加新的日志功能（如日志分析、告警等）
3. 修改用户交互逻辑
4. 引入新的依赖库

## 验收标准

### 1. 日志截断修复验收

- [ ] 所有日志输出完整显示，无截断
- [ ] URL、链接、基础 URL 等长文本完整记录
- [ ] 命令行参数完整记录
- [ ] User-Agent 等请求头完整记录

### 2. print 替换验收

- [ ] 所有非用户交互的 print 语句已替换为日志输出
- [ ] 日志级别设置合理（DEBUG、INFO、WARNING、ERROR）
- [ ] 日志包含时间戳、模块信息和必要上下文
- [ ] 用户交互 print 语句保留

### 3. 代码质量验收

- [ ] 代码遵循项目现有代码规范
- [ ] 代码风格保持一致
- [ ] 添加必要的注释
- [ ] 无语法错误

### 4. 功能验收

- [ ] 用户交互体验保持不变
- [ ] 程序功能正常运行
- [ ] 日志输出正确
- [ ] 日志格式规范

### 5. 测试验收

- [ ] 现有测试通过
- [ ] 日志输出验证通过
- [ ] 日志格式验证通过
- [ ] 用户交互测试通过

## 关键假设确认

### 1. 敏感信息处理

- **假设**: URL、Cookie 等敏感信息不需要脱敏处理
- **确认**: 保持原样，不进行脱敏处理，因为这些信息对调试很重要

### 2. 日志长度限制

- **假设**: 不设置日志行长度限制
- **确认**: 不设置长度限制，确保完整显示

### 3. 分隔符处理

- **假设**: `print("=" * 100)`等分隔符对调试没有帮助
- **确认**: 删除这些分隔符

### 4. 日志级别设置

- **假设**: 根据信息重要性合理设置日志级别
- **确认**: 调试信息用 DEBUG，一般信息用 INFO，警告信息用 WARNING，错误信息用 ERROR

### 5. 异常处理

- **假设**: 异常信息需要包含堆栈信息
- **确认**: 使用`exc_info=True`包含堆栈信息

## 不确定性解决

所有不确定性已在 ALIGNMENT 文档中明确并解决：

- 敏感信息处理：保持原样
- 日志长度限制：不设置限制
- 分隔符处理：删除
- 日志级别设置：根据重要性设置
- 异常处理：包含堆栈信息

## 最终确认

### 明确的实现需求

1. 修复 14 处日志截断问题
2. 替换 38 处 print 语句为日志输出
3. 删除 3 处无用的分隔符 print 语句
4. 确保日志格式统一规范
5. 保持用户交互体验不变

### 明确的子任务定义

1. 修复 downloader.py 中的日志截断和 print 语句
2. 修复 n_m3u8dl_re.py 中的日志截断和 print 语句
3. 修复 cookie_handler.py 中的日志截断
4. 修复 main.py 中的日志截断和 print 语句
5. 修复 m3u8_parser.py 中的 print 语句
6. 修复 file_reader.py 中的 print 语句
7. 修复 ffmpeg_wrapper.py 中的 print 语句
8. 修复 logger_config.py 中的 print 语句
9. 修复 settings.py 中的 print 语句
10. 验证所有修改并运行测试

### 明确的边界和限制

1. 不修改日志系统架构
2. 不添加新的日志功能
3. 不修改用户交互逻辑
4. 不引入新的依赖库

### 明确的验收标准

1. 所有日志输出完整显示，无截断
2. 所有非用户交互的 print 语句已替换为日志输出
3. 日志级别设置合理
4. 日志包含时间戳、模块信息和必要上下文
5. 用户交互体验保持不变
6. 代码通过现有测试

### 代码质量标准

1. 遵循项目现有代码规范
2. 保持代码风格一致
3. 添加必要的注释
4. 无语法错误

### 测试质量标准

1. 现有测试通过
2. 日志输出验证通过
3. 日志格式验证通过
4. 用户交互测试通过

### 文档质量标准

1. 完整记录所有修改
2. 清晰说明修改原因
3. 提供修改前后对比
4. 包含验收结果
