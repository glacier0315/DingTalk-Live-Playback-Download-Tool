# 日志系统集成 - 待办事项

## 待办事项

### 日志配置优化
1. **日志级别动态调整**
   - 当前支持：通过环境变量 `LOG_LEVEL` 调整
   - 建议：添加配置文件支持，允许用户在配置文件中设置日志级别
   - 操作指引：在 `src/dingtalk_downloader/config/settings.py` 中添加 `log_level` 配置项

2. **日志文件路径自定义**
   - 当前：固定为 `logs` 目录
   - 建议：支持自定义日志文件路径
   - 操作指引：在 `src/dingtalk_downloader/config/settings.py` 中添加 `log_dir` 配置项

3. **日志文件大小限制调整**
   - 当前：固定为 10MB
   - 建议：支持自定义日志文件大小限制
   - 操作指引：在 `src/dingtalk_downloader/config/settings.py` 中添加 `log_max_size` 配置项

4. **日志保留天数调整**
   - 当前：固定为 30 天
   - 建议：支持自定义日志保留天数
   - 操作指引：在 `src/dingtalk_downloader/config/settings.py` 中添加 `log_retention_days` 配置项

### 日志功能增强
1. **日志文件压缩**
   - 当前：不压缩日志文件
   - 建议：对超过一定天数的日志文件进行压缩（如 gzip）
   - 操作指引：在 `src/dingtalk_downloader/config/logger_config.py` 中添加日志压缩逻辑

2. **日志文件上传**
   - 当前：日志文件仅保存在本地
   - 建议：支持将日志文件上传到远程服务器（如 S3、OSS）
   - 操作指引：在 `src/dingtalk_downloader/config/logger_config.py` 中添加日志上传逻辑

3. **日志告警**
   - 当前：无告警功能
   - 建议：对 ERROR 和 CRITICAL 级别的日志发送告警（如邮件、钉钉通知）
   - 操作指引：在 `src/dingtalk_downloader/config/logger_config.py` 中添加日志告警逻辑

4. **日志分析工具**
   - 当前：无日志分析工具
   - 建议：创建日志分析工具，统计错误频率、性能指标等
   - 操作指引：创建 `src/dingtalk_downloader/utils/log_analyzer.py` 模块

### 日志测试完善
1. **日志功能测试**
   - 当前：日志功能测试不完整
   - 建议：添加日志功能的单元测试
   - 操作指引：在 `tests/unit/test_logger_config.py` 中添加测试用例

2. **日志格式测试**
   - 当前：日志格式测试不完整
   - 建议：添加日志格式的单元测试
   - 操作指引：在 `tests/unit/test_logger_config.py` 中添加测试用例

3. **日志性能测试**
   - 当前：日志性能测试不完整
   - 建议：添加日志性能的单元测试
   - 操作指引：在 `tests/unit/test_logger_config.py` 中添加测试用例

### 文档完善
1. **日志使用文档**
   - 当前：无日志使用文档
   - 建议：创建日志使用文档，说明如何查看日志、如何调整日志级别等
   - 操作指引：创建 `docs/logging_guide.md` 文档

2. **日志配置文档**
   - 当前：无日志配置文档
   - 建议：创建日志配置文档，说明所有日志配置项的含义和用法
   - 操作指引：创建 `docs/logging_config.md` 文档

3. **日志故障排查文档**
   - 当前：无日志故障排查文档
   - 建议：创建日志故障排查文档，说明常见问题和解决方法
   - 操作指引：创建 `docs/logging_troubleshooting.md` 文档

## 缺少的配置

### 环境变量
1. **LOG_LEVEL**
   - 描述：日志级别配置
   - 默认值：`INFO`
   - 可选值：`DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL`
   - 设置方法：在命令行中设置 `set LOG_LEVEL=DEBUG`
   - 示例：`set LOG_LEVEL=DEBUG && python -m dingtalk_downloader.main`

### 配置文件
1. **log_level**
   - 描述：日志级别配置
   - 默认值：`INFO`
   - 可选值：`DEBUG`、`INFO`、`WARNING`、`ERROR`、`CRITICAL`
   - 设置方法：在配置文件中设置
   - 示例：
     ```json
     {
       "log_level": "DEBUG"
     }
     ```

2. **log_dir**
   - 描述：日志文件目录配置
   - 默认值：`logs`
   - 设置方法：在配置文件中设置
   - 示例：
     ```json
     {
       "log_dir": "logs"
     }
     ```

3. **log_max_size**
   - 描述：日志文件最大大小配置（MB）
   - 默认值：`10`
   - 设置方法：在配置文件中设置
   - 示例：
     ```json
     {
       "log_max_size": 10
     }
     ```

4. **log_retention_days**
   - 描述：日志文件保留天数配置
   - 默认值：`30`
   - 设置方法：在配置文件中设置
   - 示例：
     ```json
     {
       "log_retention_days": 30
     }
     ```

## 操作指引

### 如何查看日志
1. **查看控制台日志**
   - 程序运行时，日志会同时输出到控制台
   - 可以直接在控制台中查看日志

2. **查看日志文件**
   - 日志文件保存在 `logs` 目录下
   - 文件名格式：`dingtalk_downloader_YYYY-MM-DD.log`
   - 可以使用文本编辑器或日志查看工具打开日志文件

3. **实时查看日志**
   - 使用 `tail` 命令实时查看日志文件
   - 示例：`tail -f logs/dingtalk_downloader_2025-01-15.log`

### 如何调整日志级别
1. **通过环境变量调整**
   - 在命令行中设置 `LOG_LEVEL` 环境变量
   - 示例：`set LOG_LEVEL=DEBUG && python -m dingtalk_downloader.main`

2. **通过配置文件调整**
   - 在配置文件中设置 `log_level` 配置项
   - 示例：
     ```json
     {
       "log_level": "DEBUG"
     }
     ```

### 如何清理日志
1. **自动清理**
   - 程序启动时会自动清理超过 30 天的日志文件
   - 无需手动清理

2. **手动清理**
   - 可以手动删除 `logs` 目录下的日志文件
   - 示例：`del logs\*.log`

### 如何分析日志
1. **使用日志查看工具**
   - 推荐使用 `less`、`more`、`grep` 等工具查看日志
   - 示例：`grep "ERROR" logs/dingtalk_downloader_2025-01-15.log`

2. **使用日志分析工具**
   - 可以使用 ELK、Splunk 等日志分析工具
   - 需要配置日志收集和分析系统

3. **使用 Python 脚本分析**
   - 可以编写 Python 脚本分析日志文件
   - 示例：统计错误数量、分析性能指标等

## 注意事项

1. **日志文件大小**
   - 单个日志文件最大为 10MB
   - 超过大小后会自动创建新文件
   - 最多保留 5 个备份文件

2. **日志保留天数**
   - 默认保留最近 30 天的日志文件
   - 超过保留天数的日志文件会被自动删除

3. **日志级别选择**
   - DEBUG：详细的调试信息，适合开发和调试
   - INFO：一般信息，适合日常使用
   - WARNING：警告信息，适合生产环境
   - ERROR：错误信息，适合生产环境
   - CRITICAL：严重错误，适合生产环境

4. **性能影响**
   - 日志记录会对程序性能产生一定影响
   - 建议在生产环境中使用 INFO 或更高级别
   - 避免在循环中频繁记录 DEBUG 级别的日志

## 联系支持

如果在使用日志系统时遇到问题，请联系项目团队获取支持。
