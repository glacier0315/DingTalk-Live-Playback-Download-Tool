# TASK_yaml-config-refactor

## 任务概述
- **任务名称**: yaml-config-refactor
- **创建时间**: 2026-01-21 14:07:06
- **时间戳**: 20260121-140706

## 任务拆分

### 任务1: 添加PyYAML依赖
**优先级**: 高  
**预计耗时**: 5分钟  
**依赖**: 无  

**任务描述**:
在requirements.txt中添加PyYAML依赖

**输入**:
- requirements.txt文件

**输出**:
- 更新后的requirements.txt文件

**验收标准**:
- requirements.txt中包含`PyYAML>=6.0`
- 依赖版本符合项目要求

**执行步骤**:
1. 打开requirements.txt文件
2. 添加`PyYAML>=6.0`到依赖列表
3. 保存文件

---

### 任务2: 创建YamlConfig类
**优先级**: 高  
**预计耗时**: 30分钟  
**依赖**: 任务1  

**任务描述**:
创建src/dingtalk_downloader/config/yaml_config.py文件，实现YamlConfig类

**输入**:
- DESIGN文档中的YamlConfig类设计

**输出**:
- src/dingtalk_downloader/config/yaml_config.py文件

**验收标准**:
- YamlConfig类实现完整
- 包含所有公共方法
- 代码符合PEP 8规范
- 代码通过flake8检查
- 代码通过black格式化
- 代码通过mypy类型检查

**执行步骤**:
1. 创建yaml_config.py文件
2. 实现YamlConfig类
3. 实现__init__方法
4. 实现load方法
5. 实现save方法
6. 实现get方法
7. 实现set方法
8. 实现get_nested方法
9. 实现set_nested方法
10. 实现reload方法
11. 实现validate方法
12. 实现私有方法_load_default_config
13. 实现私有方法_merge_configs
14. 添加类型提示
15. 添加中文注释

---

### 任务3: 创建默认配置文件
**优先级**: 高  
**预计耗时**: 15分钟  
**依赖**: 任务2  

**任务描述**:
创建src/dingtalk_downloader/config/config.yaml.example文件，包含所有配置项和详细注释

**输入**:
- DESIGN文档中的配置文件结构

**输出**:
- src/dingtalk_downloader/config/config.yaml.example文件

**验收标准**:
- 配置文件结构完整
- 包含所有配置项
- 包含详细的中文注释
- YAML格式正确

**执行步骤**:
1. 创建config.yaml.example文件
2. 添加应用配置
3. 添加下载配置
4. 添加浏览器配置
5. 添加日志配置
6. 添加请求头配置
7. 添加N_m3u8DL-RE配置
8. 添加FFmpeg配置
9. 为每个配置项添加中文注释

---

### 任务4: 重构Settings类
**优先级**: 高  
**预计耗时**: 20分钟  
**依赖**: 任务2, 任务3  

**任务描述**:
重构src/dingtalk_downloader/config/settings.py文件，使其内部使用YamlConfig实现

**输入**:
- 现有的settings.py文件
- DESIGN文档中的Settings类设计

**输出**:
- 重构后的settings.py文件

**验收标准**:
- 保持现有API不变
- 内部使用YamlConfig实现
- 代码符合PEP 8规范
- 代码通过flake8检查
- 代码通过black格式化
- 代码通过mypy类型检查

**执行步骤**:
1. 读取现有settings.py文件
2. 修改__init__方法，创建YamlConfig实例
3. 修改load方法，委托给YamlConfig.load
4. 修改save方法，委托给YamlConfig.save
5. 修改get方法，委托给YamlConfig.get
6. 修改set方法，委托给YamlConfig.set
7. 添加migrate_from_json方法
8. 保持向后兼容性
9. 添加类型提示
10. 添加中文注释

---

### 任务5: 改造LoggerConfig类
**优先级**: 高  
**预计耗时**: 15分钟  
**依赖**: 任务2, 任务3  

**任务描述**:
改造src/dingtalk_downloader/config/logger_config.py文件，使其从YamlConfig读取配置

**输入**:
- 现有的logger_config.py文件
- DESIGN文档中的LoggerConfig改造方案

**输出**:
- 改造后的logger_config.py文件

**验收标准**:
- 从YamlConfig读取日志配置
- 保持现有日志格式和功能
- 代码符合PEP 8规范
- 代码通过flake8检查
- 代码通过black格式化
- 代码通过mypy类型检查

**执行步骤**:
1. 读取现有logger_config.py文件
2. 修改setup_logging方法
3. 从YamlConfig读取日志级别
4. 从YamlConfig读取日志目录
5. 从YamlConfig读取日志文件大小
6. 从YamlConfig读取日志备份数量
7. 从YamlConfig读取日志保留天数
8. 保持现有日志格式
9. 添加类型提示
10. 添加中文注释

---

### 任务6: 编写YamlConfig单元测试
**优先级**: 高  
**预计耗时**: 30分钟  
**依赖**: 任务2, 任务3  

**任务描述**:
创建tests/unit/test_yaml_config.py文件，编写YamlConfig类的单元测试

**输入**:
- yaml_config.py文件
- config.yaml.example文件

**输出**:
- tests/unit/test_yaml_config.py文件

**验收标准**:
- 测试覆盖所有公共方法
- 测试覆盖正常场景
- 测试覆盖边界条件
- 测试覆盖异常情况
- 测试覆盖率≥80%
- 所有测试通过

**执行步骤**:
1. 创建test_yaml_config.py文件
2. 编写test_yaml_config_init测试
3. 编写test_yaml_config_load测试
4. 编写test_yaml_config_save测试
5. 编写test_yaml_config_get测试
6. 编写test_yaml_config_set测试
7. 编写test_yaml_config_get_nested测试
8. 编写test_yaml_config_set_nested测试
9. 编写test_yaml_config_reload测试
10. 编写test_yaml_config_validate测试
11. 编写test_yaml_config_load_nonexistent_file测试
12. 编写test_yaml_config_load_invalid_yaml测试
13. 编写test_yaml_config_save_io_error测试
14. 运行测试确保通过

---

### 任务7: 更新Settings单元测试
**优先级**: 中  
**预计耗时**: 15分钟  
**依赖**: 任务4, 任务6  

**任务描述**:
更新tests/unit/test_settings.py文件，确保测试覆盖重构后的Settings类

**输入**:
- 现有的test_settings.py文件
- 重构后的settings.py文件

**输出**:
- 更新后的test_settings.py文件

**验收标准**:
- 测试覆盖所有公共方法
- 测试覆盖向后兼容性
- 测试覆盖JSON到YAML迁移
- 测试覆盖率≥80%
- 所有测试通过

**执行步骤**:
1. 读取现有test_settings.py文件
2. 更新test_settings_init测试
3. 更新test_settings_load测试
4. 更新test_settings_save测试
5. 更新test_settings_get测试
6. 更新test_settings_set测试
7. 添加test_settings_migrate_from_json测试
8. 运行测试确保通过

---

### 任务8: 编写LoggerConfig单元测试
**优先级**: 中  
**预计耗时**: 20分钟  
**依赖**: 任务5, 任务6  

**任务描述**:
创建tests/unit/test_logger_config_yaml.py文件，编写LoggerConfig从YAML读取配置的单元测试

**输入**:
- logger_config.py文件
- yaml_config.py文件

**输出**:
- tests/unit/test_logger_config_yaml.py文件

**验收标准**:
- 测试覆盖从YAML读取配置
- 测试覆盖日志级别更新
- 测试覆盖率≥80%
- 所有测试通过

**执行步骤**:
1. 创建test_logger_config_yaml.py文件
2. 编写test_setup_logging_from_yaml测试
3. 编写test_log_level_from_yaml测试
4. 编写test_log_dir_from_yaml测试
5. 编写test_log_max_bytes_from_yaml测试
6. 编写test_log_backup_count_from_yaml测试
7. 运行测试确保通过

---

### 任务9: 运行所有测试并修复问题
**优先级**: 高  
**预计耗时**: 15分钟  
**依赖**: 任务6, 任务7, 任务8  

**任务描述**:
运行所有单元测试，修复发现的问题

**输入**:
- 所有测试文件

**输出**:
- 所有测试通过的测试报告

**验收标准**:
- 所有单元测试通过
- 测试覆盖率≥80%
- 无测试失败

**执行步骤**:
1. 运行pytest命令
2. 检查测试结果
3. 修复失败的测试
4. 检查测试覆盖率
5. 确保覆盖率≥80%
6. 重新运行测试确保通过

---

### 任务10: 代码质量检查
**优先级**: 高  
**预计耗时**: 10分钟  
**依赖**: 任务9  

**任务描述**:
运行代码质量检查工具，确保代码符合规范

**输入**:
- 所有源代码文件

**输出**:
- 代码质量检查报告

**验收标准**:
- 代码通过flake8检查
- 代码通过black格式化
- 代码通过mypy类型检查
- 无严重代码质量问题

**执行步骤**:
1. 运行flake8检查
2. 修复flake8发现的问题
3. 运行black格式化
4. 运行mypy类型检查
5. 修复mypy发现的问题
6. 重新运行检查确保通过

---

### 任务11: 更新config模块README
**优先级**: 中  
**预计耗时**: 15分钟  
**依赖**: 任务4, 任务5  

**任务描述**:
更新src/dingtalk_downloader/config/README.md文件，说明新的YAML配置系统

**输入**:
- 现有的README.md文件
- DESIGN文档

**输出**:
- 更新后的README.md文件

**验收标准**:
- 说明YAML配置系统的使用方法
- 说明配置文件的结构
- 说明配置项的含义
- 包含使用示例

**执行步骤**:
1. 读取现有README.md文件
2. 添加YAML配置系统说明
3. 添加配置文件结构说明
4. 添加配置项说明
5. 添加使用示例
6. 更新相关章节

---

### 任务12: 更新项目README
**优先级**: 中  
**预计耗时**: 10分钟  
**依赖**: 任务11  

**任务描述**:
更新项目根目录的README.md文件，说明新的YAML配置系统

**输入**:
- 现有的README.md文件
- config模块的README.md

**输出**:
- 更新后的README.md文件

**验收标准**:
- 说明YAML配置系统的变更
- 提供配置文件位置
- 提供配置文件示例

**执行步骤**:
1. 读取现有README.md文件
2. 添加YAML配置系统说明
3. 提供配置文件位置
4. 提供配置文件示例链接

---

### 任务13: 集成测试
**优先级**: 高  
**预计耗时**: 20分钟  
**依赖**: 任务10  

**任务描述**:
运行集成测试，验证配置系统与现有模块的兼容性

**输入**:
- 所有源代码文件
- 所有测试文件

**输出**:
- 集成测试报告

**验收标准**:
- 所有集成测试通过
- 配置系统与现有模块兼容
- 无功能回归

**执行步骤**:
1. 运行单个视频下载测试
2. 运行批量下载测试
3. 验证配置系统正常工作
4. 检查日志输出
5. 修复发现的问题

---

## 任务依赖关系图

```
任务1: 添加PyYAML依赖
    ↓
任务2: 创建YamlConfig类 ──────→ 任务3: 创建默认配置文件
    ↓                           ↓
任务4: 重构Settings类          ↓
    ↓                           ↓
任务5: 改造LoggerConfig类 ←─────┘
    ↓
任务6: 编写YamlConfig单元测试
    ↓
任务7: 更新Settings单元测试 ←─── 任务8: 编写LoggerConfig单元测试
    ↓                           ↓
任务9: 运行所有测试并修复问题 ←─┘
    ↓
任务10: 代码质量检查
    ↓
任务11: 更新config模块README ─→ 任务12: 更新项目README
    ↓
任务13: 集成测试
```

## 任务执行顺序

1. 任务1: 添加PyYAML依赖
2. 任务2: 创建YamlConfig类
3. 任务3: 创建默认配置文件
4. 任务4: 重构Settings类
5. 任务5: 改造LoggerConfig类
6. 任务6: 编写YamlConfig单元测试
7. 任务7: 更新Settings单元测试
8. 任务8: 编写LoggerConfig单元测试
9. 任务9: 运行所有测试并修复问题
10. 任务10: 代码质量检查
11. 任务11: 更新config模块README
12. 任务12: 更新项目README
13. 任务13: 集成测试

## 总体时间估算

- 任务1: 5分钟
- 任务2: 30分钟
- 任务3: 15分钟
- 任务4: 20分钟
- 任务5: 15分钟
- 任务6: 30分钟
- 任务7: 15分钟
- 任务8: 20分钟
- 任务9: 15分钟
- 任务10: 10分钟
- 任务11: 15分钟
- 任务12: 10分钟
- 任务13: 20分钟

**总计**: 约2小时15分钟
