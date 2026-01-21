# TASK - 原子任务文档

## 任务拆分

基于DESIGN文档，将整体任务拆分为以下原子任务：

## 任务列表

### 任务1: 修改yaml_config.py默认配置

**任务ID**: TASK-001
**优先级**: 高
**依赖**: 无
**预计时间**: 5分钟

**任务描述**:
在`yaml_config.py`的`_load_default_config()`方法中添加`temp_dir`和`log_dir`配置项。

**输入**:
- 文件路径: `src/dingtalk_downloader/config/yaml_config.py`
- 默认值: `temp_dir: "temp"`, `log_dir: "logs"`

**输出**:
- 修改后的`_load_default_config()`方法

**验收标准**:
- 默认配置包含`n_m3u8dl_re.temp_dir`配置项
- 默认配置包含`n_m3u8dl_re.log_dir`配置项
- 配置值正确

---

### 任务2: 更新config.yaml配置文件

**任务ID**: TASK-002
**优先级**: 高
**依赖**: TASK-001
**预计时间**: 3分钟

**任务描述**:
在`config.yaml`文件中添加`temp_dir`和`log_dir`配置项。

**输入**:
- 文件路径: `src/dingtalk_downloader/config.yaml`
- 配置值: `temp_dir: "temp"`, `log_dir: "logs"`

**输出**:
- 更新后的`config.yaml`文件

**验收标准**:
- `n_m3u8dl_re`部分包含`temp_dir`配置项
- `n_m3u8dl_re`部分包含`log_dir`配置项
- 配置值正确

---

### 任务3: 更新config.yaml.example配置示例文件

**任务ID**: TASK-003
**优先级**: 高
**依赖**: TASK-002
**预计时间**: 3分钟

**任务描述**:
在`config.yaml.example`文件中添加`temp_dir`和`log_dir`配置项。

**输入**:
- 文件路径: `src/dingtalk_downloader/config/config.yaml.example`
- 配置值: `temp_dir: "temp"`, `log_dir: "logs"`

**输出**:
- 更新后的`config.yaml.example`文件

**验收标准**:
- `n_m3u8dl_re`部分包含`temp_dir`配置项
- `n_m3u8dl_re`部分包含`log_dir`配置项
- 配置值正确

---

### 任务4: 在NM3u8DLRE类中添加配置读取逻辑

**任务ID**: TASK-004
**优先级**: 高
**依赖**: TASK-001
**预计时间**: 10分钟

**任务描述**:
在`NM3u8DLRE`类的`__init__()`方法中添加配置读取逻辑，读取`temp_dir`和`log_dir`配置。

**输入**:
- 文件路径: `src/dingtalk_downloader/binary/n_m3u8dl_re.py`
- 配置项: `n_m3u8dl_re.temp_dir`, `n_m3u8dl_re.log_dir`

**输出**:
- 修改后的`__init__()`方法

**验收标准**:
- `__init__()`方法读取配置
- `self.temp_dir`属性正确设置
- `self.log_dir`属性正确设置
- 使用默认值作为降级方案

---

### 任务5: 在NM3u8DLRE类中添加目录创建方法

**任务ID**: TASK-005
**优先级**: 高
**依赖**: TASK-004
**预计时间**: 10分钟

**任务描述**:
在`NM3u8DLRE`类中添加`_ensure_directories_exist()`私有方法，确保临时目录和日志目录存在。

**输入**:
- 文件路径: `src/dingtalk_downloader/binary/n_m3u8dl_re.py`
- 工具函数: `path_helper.ensure_dir_exists()`

**输出**:
- `_ensure_directories_exist()`方法

**验收标准**:
- 方法检查并创建`temp_dir`目录
- 方法检查并创建`log_dir`目录
- 包含错误处理和日志记录

---

### 任务6: 在NM3u8DLRE类中添加日志文件路径生成方法

**任务ID**: TASK-006
**优先级**: 高
**依赖**: TASK-004
**预计时间**: 8分钟

**任务描述**:
在`NM3u8DLRE`类中添加`_get_log_file_path()`私有方法，生成唯一的日志文件路径。

**输入**:
- 文件路径: `src/dingtalk_downloader/binary/n_m3u8dl_re.py`
- 日志目录: `self.log_dir`

**输出**:
- `_get_log_file_path()`方法

**验收标准**:
- 方法生成包含时间戳的日志文件名
- 返回完整的日志文件路径
- 包含调试日志

---

### 任务7: 修改NM3u8DLRE类的build_command方法

**任务ID**: TASK-007
**优先级**: 高
**依赖**: TASK-005, TASK-006
**预计时间**: 5分钟

**任务描述**:
在`NM3u8DLRE`类的`build_command()`方法中添加`--tmp-dir`和`--log-file-path`参数。

**输入**:
- 文件路径: `src/dingtalk_downloader/binary/n_m3u8dl_re.py`
- 临时目录: `self.temp_dir`
- 日志文件路径: `self._get_log_file_path()`

**输出**:
- 修改后的`build_command()`方法

**验收标准**:
- 命令列表包含`--tmp-dir`参数
- 命令列表包含`--log-file-path`参数
- 参数值正确

---

### 任务8: 更新NM3u8DLRE类的文档字符串

**任务ID**: TASK-008
**优先级**: 中
**依赖**: TASK-004, TASK-005, TASK-006, TASK-007
**预计时间**: 5分钟

**任务描述**:
更新`NM3u8DLRE`类的文档字符串，添加新增属性和方法的说明。

**输入**:
- 文件路径: `src/dingtalk_downloader/binary/n_m3u8dl_re.py`
- 新增属性: `temp_dir`, `log_dir`
- 新增方法: `_ensure_directories_exist()`, `_get_log_file_path()`

**输出**:
- 更新后的文档字符串

**验收标准**:
- 类文档字符串包含`temp_dir`属性说明
- 类文档字符串包含`log_dir`属性说明
- 新增方法有完整的文档字符串

---

### 任务9: 编写目录创建单元测试

**任务ID**: TASK-009
**优先级**: 中
**依赖**: TASK-005
**预计时间**: 10分钟

**任务描述**:
编写单元测试，验证目录创建逻辑。

**输入**:
- 测试文件: `tests/unit/test_n_m3u8dl_re.py`
- 测试方法: `test_ensure_directories_exist()`

**输出**:
- 新增测试用例

**验收标准**:
- 测试验证临时目录创建
- 测试验证日志目录创建
- 测试通过

---

### 任务10: 编写命令构建单元测试

**任务ID**: TASK-010
**优先级**: 中
**依赖**: TASK-007
**预计时间**: 10分钟

**任务描述**:
编写单元测试，验证命令构建包含目录参数。

**输入**:
- 测试文件: `tests/unit/test_n_m3u8dl_re.py`
- 测试方法: `test_build_command_with_dirs()`

**输出**:
- 新增测试用例

**验收标准**:
- 测试验证`--tmp-dir`参数存在
- 测试验证`--log-file-path`参数存在
- 测试通过

---

### 任务11: 编写日志文件路径生成单元测试

**任务ID**: TASK-011
**优先级**: 中
**依赖**: TASK-006
**预计时间**: 10分钟

**任务描述**:
编写单元测试，验证日志文件路径生成逻辑。

**输入**:
- 测试文件: `tests/unit/test_n_m3u8dl_re.py`
- 测试方法: `test_get_log_file_path()`

**输出**:
- 新增测试用例

**验收标准**:
- 测试验证日志文件路径格式
- 测试验证时间戳存在
- 测试通过

---

### 任务12: 运行所有测试并修复问题

**任务ID**: TASK-012
**优先级**: 高
**依赖**: TASK-009, TASK-010, TASK-011
**预计时间**: 10分钟

**任务描述**:
运行所有测试用例，确保所有测试通过。

**输入**:
- 测试命令: `pytest`

**输出**:
- 测试结果

**验收标准**:
- 所有测试用例通过
- 无测试失败或错误

---

## 任务依赖关系

```
TASK-001 (修改yaml_config.py)
    ├─→ TASK-002 (更新config.yaml)
    │       └─→ TASK-003 (更新config.yaml.example)
    │
    └─→ TASK-004 (添加配置读取逻辑)
            ├─→ TASK-005 (添加目录创建方法)
            │       └─→ TASK-007 (修改build_command方法)
            │               └─→ TASK-008 (更新文档字符串)
            │                       └─→ TASK-010 (编写命令构建测试)
            │
            └─→ TASK-006 (添加日志文件路径生成方法)
                    └─→ TASK-007 (修改build_command方法)
                            └─→ TASK-008 (更新文档字符串)
                                    └─→ TASK-011 (编写日志文件路径测试)

TASK-005 (添加目录创建方法)
    └─→ TASK-009 (编写目录创建测试)

TASK-009, TASK-010, TASK-011
    └─→ TASK-012 (运行所有测试)
```

## 任务执行顺序

### 第一批：配置文件修改（TASK-001, TASK-002, TASK-003）

1. TASK-001: 修改yaml_config.py默认配置
2. TASK-002: 更新config.yaml配置文件
3. TASK-003: 更新config.yaml.example配置示例文件

### 第二批：核心功能实现（TASK-004, TASK-005, TASK-006, TASK-007）

4. TASK-004: 在NM3u8DLRE类中添加配置读取逻辑
5. TASK-005: 在NM3u8DLRE类中添加目录创建方法
6. TASK-006: 在NM3u8DLRE类中添加日志文件路径生成方法
7. TASK-007: 修改NM3u8DLRE类的build_command方法

### 第三批：文档更新（TASK-008）

8. TASK-008: 更新NM3u8DLRE类的文档字符串

### 第四批：测试编写（TASK-009, TASK-010, TASK-011）

9. TASK-009: 编写目录创建单元测试
10. TASK-010: 编写命令构建单元测试
11. TASK-011: 编写日志文件路径生成单元测试

### 第五批：测试验证（TASK-012）

12. TASK-012: 运行所有测试并修复问题

## 预计总时间

- 配置文件修改: 11分钟
- 核心功能实现: 33分钟
- 文档更新: 5分钟
- 测试编写: 30分钟
- 测试验证: 10分钟
- **总计**: 约89分钟

## 风险与缓解措施

### 风险1: 配置读取失败

**缓解措施**:
- 使用默认值作为降级方案
- 添加异常处理和日志记录

### 风险2: 目录创建失败

**缓解措施**:
- 使用`os.makedirs(exist_ok=True)`
- 添加详细的错误日志
- 抛出明确的异常

### 风险3: 测试失败

**缓解措施**:
- 使用Mock对象隔离外部依赖
- 编写清晰的测试用例
- 逐步修复问题

## 下一步行动

进入**Approve（审批）**阶段，执行完整性、一致性、可行性检查。
