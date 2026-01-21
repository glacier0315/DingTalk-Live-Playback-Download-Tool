# CONSENSUS - 需求共识文档

## 共识确认

基于ALIGNMENT文档的分析，本任务的需求已明确，达成以下共识：

## 1. 需求确认

### 1.1 核心功能

为N_m3u8DL-RE下载工具添加临时文件目录和日志文件目录的配置支持：

- **临时文件目录**：`./temp`
- **日志文件目录**：`./logs`

### 1.2 实现方式

通过N_m3u8DL-RE的命令行参数：

```bash
--tmp-dir ./temp
--log-file-path ./logs/n_m3u8dl_re_{timestamp}.log
```

### 1.3 自动创建逻辑

在`NM3u8DLRE`类初始化时自动创建目录，使用现有的`path_helper.ensure_dir_exists()`方法。

## 2. 配置方案共识

### 2.1 配置项设计

在`yaml_config.py`的默认配置中添加：

```python
"n_m3u8dl_re": {
    "executable_path": "assets/bin/N_m3u8DL-RE.exe",
    "ui_language": "zh-CN",
    "temp_dir": "temp",           # 新增：临时文件目录
    "log_dir": "logs",            # 新增：日志文件目录
}
```

### 2.2 配置使用

- 使用相对路径（相对于项目根目录）
- 与现有配置风格保持一致
- 支持用户自定义配置

## 3. 代码修改方案共识

### 3.1 主要修改文件

1. **[n_m3u8dl_re.py](file:///d:\dev\works\git\github\DingTalk-Live-Playback-Download-Tool\src\dingtalk_downloader\binary\n_m3u8dl_re.py)**
   - 修改`__init__()`方法，添加目录创建逻辑
   - 修改`build_command()`方法，添加`--tmp-dir`和`--log-file-path`参数

2. **[yaml_config.py](file:///d:\dev\works\git\github\DingTalk-Live-Playback-Download-Tool\src\dingtalk_downloader\config\yaml_config.py)**
   - 在默认配置中添加`temp_dir`和`log_dir`配置项

3. **[config.yaml](file:///d:\dev\works\git\github\DingTalk-Live-Playback-Download-Tool\src\dingtalk_downloader\config.yaml)**
   - 添加`temp_dir`和`log_dir`配置项

4. **[config.yaml.example](file:///d:\dev\works\git\github\DingTalk-Live-Playback-Download-Tool\src\dingtalk_downloader\config\config.yaml.example)**
   - 添加`temp_dir`和`log_dir`配置项

### 3.2 日志文件命名方案

使用时间戳确保日志文件唯一性：

```python
log_file_name = f"n_m3u8dl_re_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
log_file_path = os.path.join(log_dir, log_file_name)
```

## 4. 技术方案共识

### 4.1 目录创建时机

在`NM3u8DLRE.__init__()`方法中创建目录：

```python
def __init__(self, executable_path: Optional[str] = None):
    if executable_path is None:
        self.executable_path = self.get_executable_name()
    else:
        self.executable_path = executable_path

    # 从配置读取目录路径
    config = YamlConfig()
    config.load()
    self.temp_dir = config.get("n_m3u8dl_re.temp_dir", "temp")
    self.log_dir = config.get("n_m3u8dl_re.log_dir", "logs")

    # 确保目录存在
    from ..utils.path_helper import ensure_dir_exists
    ensure_dir_exists(self.temp_dir)
    ensure_dir_exists(self.log_dir)
```

### 4.2 命令构建方案

在`build_command()`方法中添加参数：

```python
def build_command(self, ...):
    command = [
        self.executable_path,
        m3u8_file,
        "--ui-language", "zh-CN",
        "--save-name", save_name,
        "--save-dir", save_dir,
        "--base-url", prefix,
        "--tmp-dir", self.temp_dir,
        "--log-file-path", self._get_log_file_path(),
        # ... 其他参数
    ]
    return command
```

### 4.3 错误处理

- 目录创建失败时记录错误日志
- 使用默认值作为降级方案

## 5. 测试方案共识

### 5.1 单元测试

- 测试目录创建逻辑
- 测试命令构建逻辑
- 测试配置读取逻辑

### 5.2 集成测试

- 测试完整下载流程
- 验证临时文件和日志文件是否生成在指定目录

## 6. 兼容性共识

### 6.1 向后兼容

- 新增配置项使用默认值
- 不影响现有功能

### 6.2 跨平台兼容

- 使用`os.path.join()`处理路径拼接
- 支持Windows、Linux、macOS

## 7. 代码规范共识

### 7.1 命名规范

- 变量使用小驼峰命名
- 常量使用全大写+下划线
- 类名使用大驼峰

### 7.2 注释规范

- 添加中文注释说明关键逻辑
- 复杂逻辑添加详细说明

### 7.3 代码风格

- 4空格缩进
- 避免多层嵌套
- 提前返回优化

## 8. 验收标准共识

1. N_m3u8DL-RE命令行包含`--tmp-dir ./temp`参数
2. N_m3u8DL-RE命令行包含`--log-file-path ./logs/n_m3u8dl_re_xxx.log`参数
3. 临时目录`./temp`在下载前自动创建
4. 日志目录`./logs`在下载前自动创建
5. 配置文件包含`temp_dir`和`log_dir`配置项
6. 所有测试用例通过
7. 代码符合项目规范

## 9. 风险共识

### 9.1 已识别风险

- 日志文件路径的唯一性（已通过时间戳解决）
- 目录创建失败的处理（已添加错误处理）
- 跨平台路径兼容性（已使用`os.path.join()`）

### 9.2 风险缓解措施

- 使用现有工具函数确保目录创建
- 添加详细的日志记录
- 完善的错误处理

## 10. 下一步行动

共识已达成，进入**Architect（架构）**阶段，设计整体架构方案。
