# ALIGNMENT - 需求对齐文档

## 任务概述

为N_m3u8DL-RE下载工具添加临时文件目录和日志文件目录的配置支持。

## 需求分析

### 1. 核心需求

在调用N_m3u8DL-RE二进制程序执行视频下载操作时，必须明确指定以下参数：

- **临时文件目录**：通过命令行参数`--tmp-dir`设置为`"./temp"`
- **日志文件目录**：通过命令行参数`--log-file-path`设置为`"./logs"`

### 2. 约束条件

- 确保这两个目录在程序执行前已存在
- 如目录不存在，需添加自动创建目录的逻辑
- 配置需在整个项目中保持一致性

### 3. 技术背景

根据N_m3u8DL-RE官方文档，该工具支持以下相关命令行参数：

```bash
--tmp-dir <tmp-dir>         设置临时文件存储目录
--log-file-path <log-file-path>  设置日志文件路径, 例如 C:\Logs\log.txt
```

### 4. 当前状态分析

#### 4.1 代码现状

**[n_m3u8dl_re.py](file:///d:\dev\works\git\github\DingTalk-Live-Playback-Download-Tool\src\dingtalk_downloader\binary\n_m3u8dl_re.py)**

- `build_command()`方法（第105-189行）当前未使用`--tmp-dir`和`--log-file-path`参数
- 命令构建逻辑仅包含基本参数：`--ui-language`, `--save-name`, `--save-dir`, `--base-url`, `-H`

#### 4.2 配置现状

**[yaml_config.py](file:///d:\dev\works\git\github\DingTalk-Live-Playback-Download-Tool\src\dingtalk_downloader\config\yaml_config.py)**

- 默认配置（第209-256行）中`n_m3u8dl_re`部分仅包含：
  - `executable_path`: 可执行文件路径
  - `ui_language`: UI语言
- **缺少临时目录和日志目录的配置项**

#### 4.3 目录创建逻辑

- 项目中已存在`path_helper.py`工具模块，包含`ensure_dir_exists()`方法
- 可复用现有工具函数实现目录自动创建

## 任务边界

### 包含范围

1. 修改`n_m3u8dl_re.py`的`build_command()`方法，添加`--tmp-dir`和`--log-file-path`参数
2. 在`yaml_config.py`的默认配置中添加`temp_dir`和`log_dir`配置项
3. 在`NM3u8DLRE`类初始化时自动创建临时目录和日志目录
4. 更新`config.yaml`和`config.yaml.example`配置文件
5. 更新相关测试用例

### 不包含范围

1. 不修改FFmpeg相关的配置
2. 不修改日志系统的其他部分（仅N_m3u8DL-RE的日志）
3. 不修改下载流程的其他逻辑

## 不确定性分析

### 1. 日志文件路径格式

**问题**：N_m3u8DL-RE的`--log-file-path`参数需要完整的文件路径，而需求中指定的是目录路径`"./logs"`

**解决方案**：
- 配置中设置日志目录为`"./logs"`
- 在构建命令时，自动生成日志文件路径，例如：`"./logs/n_m3u8dl_re_{timestamp}.log"`

### 2. 目录创建时机

**问题**：应该在何时创建临时目录和日志目录？

**解决方案**：
- 在`NM3u8DLRE`类的`__init__()`方法中创建
- 使用`path_helper.ensure_dir_exists()`方法确保目录存在

### 3. 配置项命名

**问题**：配置项应该如何命名？

**解决方案**：
- 临时目录：`temp_dir`
- 日志目录：`log_dir`

### 4. 相对路径与绝对路径

**问题**：使用相对路径还是绝对路径？

**解决方案**：
- 使用相对路径（相对于项目根目录）
- 与现有配置保持一致（如`download.default_dir: "Downloads"`）

## 验收标准

1. N_m3u8DL-RE命令行包含`--tmp-dir ./temp`参数
2. N_m3u8DL-RE命令行包含`--log-file-path ./logs/n_m3u8dl_re_xxx.log`参数
3. 临时目录`./temp`在下载前自动创建
4. 日志目录`./logs`在下载前自动创建
5. 配置文件包含`temp_dir`和`log_dir`配置项
6. 所有测试用例通过
7. 代码符合项目规范（4空格缩进、中文注释等）

## 风险评估

### 低风险

- 添加新参数不会影响现有功能
- 使用相对路径与现有配置风格一致

### 需要注意

- 确保日志文件路径的唯一性（使用时间戳或UUID）
- 目录创建失败时的错误处理
- Windows和Linux/macOS的路径兼容性

## 依赖关系

- 依赖`path_helper.py`的`ensure_dir_exists()`方法
- 依赖`yaml_config.py`的配置管理
- 需要更新相关测试用例

## 下一步行动

进入**Architect（架构）**阶段，设计整体架构方案。
