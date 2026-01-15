# 日志优化任务 - 待办事项

## 已完成事项

- [x] 修复所有日志截断问题（14处）
- [x] 替换所有非用户交互print语句为日志输出（38处）
- [x] 运行现有测试套件并验证通过
- [x] 验证日志输出完整性
- [x] 验证日志格式规范性
- [x] 验证用户交互流程正常

## 可选优化事项

### 测试覆盖率提升
当前测试覆盖率为26.52%，低于pytest.ini中设置的80%要求。建议：

1. 为新增的日志代码添加单元测试
   - 测试日志输出格式
   - 测试日志级别设置
   - 测试异常处理和堆栈信息记录

2. 为日志优化涉及的模块添加集成测试
   - downloader.py的日志输出测试
   - n_m3u8dl_re.py的日志输出测试
   - cookie_handler.py的日志输出测试
   - m3u8_parser.py的日志输出测试

### 日志配置优化
当前日志配置在logger_config.py中，可以考虑：

1. 添加日志轮转配置
   - 按文件大小轮转（如单个日志文件最大10MB）
   - 按日期轮转（如每天一个日志文件）
   - 保留最近N天的日志文件

2. 添加日志过滤配置
   - 支持按模块过滤日志
   - 支持按日志级别过滤日志
   - 支持按关键词过滤日志

3. 添加日志输出目标配置
   - 支持同时输出到控制台和文件
   - 支持输出到远程日志服务器
   - 支持输出到数据库

### 日志格式优化
当前日志格式为：`[时间戳] [日志级别] [模块名] 日志消息`

可以考虑：

1. 添加更多上下文信息
   - 线程ID
   - 进程ID
   - 函数名
   - 行号

2. 支持结构化日志
   - JSON格式日志
   - 支持日志聚合工具（如ELK、Splunk）

3. 支持日志着色
   - 不同日志级别使用不同颜色
   - 提高日志可读性

### 性能优化
当前日志系统可以考虑：

1. 异步日志输出
   - 使用异步日志处理器
   - 减少日志对主程序性能的影响

2. 日志缓存
   - 缓存日志消息，批量写入
   - 减少I/O操作次数

3. 日志采样
   - 对高频日志进行采样
   - 减少日志量

## 缺少配置

### 环境变量配置
建议添加以下环境变量配置：

1. 日志级别配置
   - `LOG_LEVEL`: 控制日志输出级别（DEBUG、INFO、WARNING、ERROR）
   - 默认值：INFO

2. 日志目录配置
   - `LOG_DIR`: 控制日志文件保存目录
   - 默认值：项目根目录下的logs文件夹

3. 日志文件名配置
   - `LOG_FILE`: 控制日志文件名
   - 默认值：dingtalk_downloader_YYYY-MM-DD.log

### 配置文件配置
建议在settings.py中添加以下配置：

1. 日志轮转配置
   - 日志文件最大大小
   - 保留的日志文件数量

2. 日志过滤配置
   - 需要过滤的模块列表
   - 需要过滤的日志级别列表

3. 日志输出目标配置
   - 是否输出到控制台
   - 是否输出到文件
   - 是否输出到远程服务器

## 操作指引

### 如何调整日志级别

**方法1：通过环境变量**
```powershell
$env:LOG_LEVEL = "DEBUG"
python -m dingtalk_downloader.main
```

**方法2：修改logger_config.py**
```python
# 在logger_config.py中修改
logger.setLevel(logging.DEBUG)  # 改为DEBUG级别
```

### 如何查看日志文件

**方法1：直接打开日志文件**
```powershell
# 日志文件位置
Get-Content "D:\dev\works\git\github\DingTalk-Live-Playback-Download-Tool\logs\dingtalk_downloader_2026-01-15.log"
```

**方法2：实时查看日志**
```powershell
# 使用PowerShell实时查看日志
Get-Content "D:\dev\works\git\github\DingTalk-Live-Playback-Download-Tool\logs\dingtalk_downloader_2026-01-15.log" -Wait -Tail 50
```

### 如何清理日志文件

**方法1：删除所有日志文件**
```powershell
Remove-Item "D:\dev\works\git\github\DingTalk-Live-Playback-Download-Tool\logs\*.log"
```

**方法2：删除N天前的日志文件**
```powershell
$days = 7
$cutoffDate = (Get-Date).AddDays(-$days)
Get-ChildItem "D:\dev\works\git\github\DingTalk-Live-Playback-Download-Tool\logs\*.log" | Where-Object { $_.LastWriteTime -lt $cutoffDate } | Remove-Item
```

### 如何添加新的日志输出

**步骤1：导入logging模块**
```python
import logging

# 获取logger实例
logger = logging.getLogger(__name__)
```

**步骤2：选择合适的日志级别**
```python
logger.debug("调试信息")      # 调试信息
logger.info("一般信息")       # 一般信息
logger.warning("警告信息")    # 警告信息
logger.error("错误信息")      # 错误信息
logger.critical("严重错误")   # 严重错误
```

**步骤3：添加必要的上下文信息**
```python
logger.info(f"开始下载视频: {url}")
logger.error(f"下载失败: {e}", exc_info=True)  # 添加堆栈信息
```

### 如何验证日志输出

**方法1：运行测试**
```powershell
pytest tests/unit/test_settings.py -v
```

**方法2：运行程序并查看日志**
```powershell
python -m dingtalk_downloader.main
# 程序运行后，查看日志文件
Get-Content "D:\dev\works\git\github\DingTalk-Live-Playback-Download-Tool\logs\dingtalk_downloader_*.log"
```

**方法3：创建测试脚本**
```python
import logging
from dingtalk_downloader.config.logger_config import LoggerConfig

LoggerConfig.setup_logging()
logger = logging.getLogger(__name__)

logger.info("测试日志输出")
```

## 注意事项

1. **不要在日志中记录敏感信息**
   - 密码
   - Token
   - Cookie值
   - 个人身份信息

2. **合理使用日志级别**
   - DEBUG: 调试信息，仅在开发时使用
   - INFO: 一般信息，记录程序正常运行状态
   - WARNING: 警告信息，记录潜在问题
   - ERROR: 错误信息，记录程序错误
   - CRITICAL: 严重错误，记录可能导致程序崩溃的错误

3. **日志消息要清晰明确**
   - 使用简洁的语言
   - 包含必要的上下文信息
   - 避免使用模糊的描述

4. **定期清理日志文件**
   - 日志文件会占用磁盘空间
   - 建议定期清理旧日志文件
   - 可以设置日志轮转策略

5. **日志文件权限**
   - 确保日志文件有正确的读写权限
   - 避免日志文件被其他程序占用
