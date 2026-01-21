# DESIGN - 架构设计文档

## 1. 系统架构概述

### 1.1 架构目标

为N_m3u8DL-RE下载工具添加临时文件目录和日志文件目录的配置支持，确保：

- 配置集中管理
- 目录自动创建
- 跨平台兼容
- 向后兼容

### 1.2 架构原则

- **单一职责**：每个模块只负责一个功能
- **开闭原则**：对扩展开放，对修改关闭
- **依赖倒置**：依赖抽象而非具体实现
- **配置驱动**：通过配置文件控制行为

## 2. 模块设计

### 2.1 配置模块（Config Module）

#### 2.1.1 YamlConfig类扩展

**文件**：[yaml_config.py](file:///d:\dev\works\git\github\DingTalk-Live-Playback-Download-Tool\src\dingtalk_downloader\config\yaml_config.py)

**修改内容**：

```python
def _load_default_config(self) -> Dict[str, Any]:
    return {
        # ... 其他配置
        "n_m3u8dl_re": {
            "executable_path": "assets/bin/N_m3u8DL-RE.exe",
            "ui_language": "zh-CN",
            "temp_dir": "temp",           # 新增
            "log_dir": "logs",            # 新增
        },
    }
```

**设计要点**：

- 使用相对路径（相对于项目根目录）
- 提供默认值确保向后兼容
- 支持用户自定义配置

#### 2.1.2 配置文件更新

**文件**：
- [config.yaml](file:///d:\dev\works\git\github\DingTalk-Live-Playback-Download-Tool\src\dingtalk_downloader\config.yaml)
- [config.yaml.example](file:///d:\dev\works\git\github\DingTalk-Live-Playback-Download-Tool\src\dingtalk_downloader\config\config.yaml.example)

**新增配置项**：

```yaml
n_m3u8dl_re:
  executable_path: "assets/bin/N_m3u8DL-RE.exe"
  ui_language: "zh-CN"
  temp_dir: "temp"          # 新增：临时文件目录
  log_dir: "logs"           # 新增：日志文件目录
```

### 2.2 二进制工具模块（Binary Module）

#### 2.2.1 NM3u8DLRE类扩展

**文件**：[n_m3u8dl_re.py](file:///d:\dev\works\git\github\DingTalk-Live-Playback-Download-Tool\src\dingtalk_downloader\binary\n_m3u8dl_re.py)

**类结构**：

```python
class NM3u8DLRE:
    """
    N_m3u8DL-RE 调用类，负责调用 N_m3u8DL-RE 工具。

    Attributes:
        executable_path (str): 可执行文件路径
        temp_dir (str): 临时文件目录
        log_dir (str): 日志文件目录
    """

    def __init__(self, executable_path: Optional[str] = None):
        """
        初始化 N_m3u8DL-RE 调用器。

        Args:
            executable_path: 可执行文件路径，默认为 None（自动查找）
        """
        # 设置可执行文件路径
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
        self._ensure_directories_exist()

        logger.debug(f"N_m3u8DL-RE 调用器初始化完成")
        logger.debug(f"可执行文件: {self.executable_path}")
        logger.debug(f"临时目录: {self.temp_dir}")
        logger.debug(f"日志目录: {self.log_dir}")

    def _ensure_directories_exist(self) -> None:
        """
        确保临时目录和日志目录存在。

        如果目录不存在，则自动创建。
        """
        from ..utils.path_helper import ensure_dir_exists

        try:
            ensure_dir_exists(self.temp_dir)
            logger.debug(f"临时目录已就绪: {self.temp_dir}")
        except Exception as e:
            logger.error(f"创建临时目录失败: {e}")
            raise

        try:
            ensure_dir_exists(self.log_dir)
            logger.debug(f"日志目录已就绪: {self.log_dir}")
        except Exception as e:
            logger.error(f"创建日志目录失败: {e}")
            raise

    def _get_log_file_path(self) -> str:
        """
        获取日志文件路径。

        使用时间戳确保日志文件唯一性。

        Returns:
            日志文件完整路径
        """
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file_name = f"n_m3u8dl_re_{timestamp}.log"
        log_file_path = os.path.join(self.log_dir, log_file_name)
        logger.debug(f"日志文件路径: {log_file_path}")
        return log_file_path

    def build_command(
        self,
        m3u8_file: str,
        save_name: str,
        save_dir: str,
        prefix: str,
        cookies_data: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> List[str]:
        """
        构建下载命令。

        构建 N_m3u8DL-RE 下载命令，包括文件名、保存目录、基础 URL、Cookie、请求头、临时目录和日志文件路径。

        Args:
            m3u8_file: m3u8 文件路径
            save_name: 保存文件名
            save_dir: 保存目录
            prefix: 基础 URL
            cookies_data: Cookie 字典
            headers: 请求头字典

        Returns:
            命令列表
        """
        command = [
            self.executable_path,
            m3u8_file,
            "--ui-language", "zh-CN",
            "--save-name", save_name,
            "--save-dir", save_dir,
            "--base-url", prefix,
            "--tmp-dir", self.temp_dir,
            "--log-file-path", self._get_log_file_path(),
        ]

        # ... 其他请求头处理逻辑保持不变

        return command
```

**设计要点**：

1. **初始化时创建目录**：在`__init__()`方法中调用`_ensure_directories_exist()`
2. **配置读取**：使用`YamlConfig`读取配置，支持默认值
3. **日志文件命名**：使用时间戳确保唯一性
4. **错误处理**：目录创建失败时记录错误并抛出异常
5. **日志记录**：添加详细的调试日志

#### 2.2.2 方法职责划分

| 方法名 | 职责 | 输入 | 输出 |
|--------|------|------|------|
| `__init__()` | 初始化调用器，创建目录 | executable_path | None |
| `_ensure_directories_exist()` | 确保目录存在 | None | None |
| `_get_log_file_path()` | 生成日志文件路径 | None | str |
| `build_command()` | 构建下载命令 | 多个参数 | List[str] |
| `download()` | 执行下载 | 多个参数 | bool |

## 3. 数据流设计

### 3.1 初始化流程

```
用户创建 NM3u8DLRE 实例
    ↓
读取配置文件 (YamlConfig)
    ↓
获取 temp_dir 和 log_dir 配置
    ↓
调用 _ensure_directories_exist()
    ↓
检查并创建 temp 目录
    ↓
检查并创建 log 目录
    ↓
初始化完成
```

### 3.2 下载流程

```
用户调用 download() 方法
    ↓
调用 build_command() 构建命令
    ↓
生成日志文件路径 (_get_log_file_path)
    ↓
构建完整命令列表（包含 --tmp-dir 和 --log-file-path）
    ↓
执行 subprocess.run()
    ↓
N_m3u8DL-RE 使用指定的临时目录和日志文件
    ↓
返回下载结果
```

## 4. 接口设计

### 4.1 配置接口

```python
# 获取临时目录配置
temp_dir = config.get("n_m3u8dl_re.temp_dir", "temp")

# 获取日志目录配置
log_dir = config.get("n_m3u8dl_re.log_dir", "logs")

# 设置临时目录配置
config.set("n_m3u8dl_re.temp_dir", "./temp")

# 设置日志目录配置
config.set("n_m3u8dl_re.log_dir", "./logs")
```

### 4.2 NM3u8DLRE接口

```python
# 创建实例（自动创建目录）
downloader = NM3u8DLRE()

# 创建实例（自定义可执行文件路径）
downloader = NM3u8DLRE(executable_path="custom/path/N_m3u8DL-RE.exe")

# 下载视频（自动使用配置的目录）
success = downloader.download(
    m3u8_file="output.m3u8",
    save_name="video",
    save_dir="Downloads",
    prefix="https://example.com/",
    cookies_data={"session": "xxx"},
    headers={"User-Agent": "..."}
)
```

## 5. 错误处理设计

### 5.1 目录创建失败

```python
try:
    ensure_dir_exists(self.temp_dir)
except Exception as e:
    logger.error(f"创建临时目录失败: {e}")
    raise RuntimeError(f"无法创建临时目录 {self.temp_dir}: {e}")
```

### 5.2 配置读取失败

```python
try:
    config = YamlConfig()
    config.load()
    self.temp_dir = config.get("n_m3u8dl_re.temp_dir", "temp")
    self.log_dir = config.get("n_m3u8dl_re.log_dir", "logs")
except Exception as e:
    logger.warning(f"读取配置失败，使用默认值: {e}")
    self.temp_dir = "temp"
    self.log_dir = "logs"
```

### 5.3 日志文件路径生成失败

```python
try:
    log_file_path = self._get_log_file_path()
except Exception as e:
    logger.error(f"生成日志文件路径失败: {e}")
    raise
```

## 6. 测试策略

### 6.1 单元测试

#### 6.1.1 目录创建测试

```python
def test_ensure_directories_exist(self):
    """测试目录创建逻辑"""
    dl = NM3u8DLRE()
    assert os.path.exists(dl.temp_dir)
    assert os.path.exists(dl.log_dir)
```

#### 6.1.2 命令构建测试

```python
def test_build_command_with_dirs(self):
    """测试命令构建包含目录参数"""
    dl = NM3u8DLRE()
    command = dl.build_command("test.m3u8", "video", "Downloads", "https://example.com/")
    assert "--tmp-dir" in command
    assert "--log-file-path" in command
```

#### 6.1.3 日志文件路径测试

```python
def test_get_log_file_path(self):
    """测试日志文件路径生成"""
    dl = NM3u8DLRE()
    log_path = dl._get_log_file_path()
    assert log_path.startswith(dl.log_dir)
    assert "n_m3u8dl_re_" in log_path
    assert ".log" in log_path
```

### 6.2 集成测试

```python
def test_download_with_custom_dirs(self):
    """测试使用自定义目录下载"""
    dl = NM3u8DLRE()
    success = dl.download(...)
    assert success is True
    # 验证临时文件和日志文件在指定目录
```

## 7. 性能考虑

### 7.1 目录创建

- 只在初始化时创建一次
- 使用`os.makedirs(exist_ok=True)`避免重复创建

### 7.2 日志文件路径生成

- 使用时间戳，性能开销极小
- 每次下载生成新的日志文件

## 8. 安全考虑

### 8.1 路径安全

- 使用`os.path.join()`拼接路径，避免路径注入
- 不接受用户输入的路径参数

### 8.2 权限检查

- 确保程序有权限创建目录
- 目录创建失败时抛出异常

## 9. 兼容性设计

### 9.1 向后兼容

- 新增配置项使用默认值
- 不修改现有接口

### 9.2 跨平台兼容

- 使用`os.path.join()`处理路径
- 支持Windows、Linux、macOS

## 10. 扩展性设计

### 10.1 配置扩展

- 未来可添加更多N_m3u8DL-RE参数
- 配置结构清晰，易于扩展

### 10.2 功能扩展

- 可添加日志文件清理功能
- 可添加临时文件清理功能

## 11. 架构图

```
┌─────────────────────────────────────────────────────────┐
│                     用户代码                              │
│                  (downloader.py)                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              NM3u8DLRE 类                                 │
│  ┌───────────────────────────────────────────────────┐  │
│  │ __init__()                                       │  │
│  │   - 读取配置                                      │  │
│  │   - 创建目录                                      │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │ build_command()                                  │  │
│  │   - 构建命令（包含目录参数）                       │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │ download()                                       │  │
│  │   - 执行下载                                      │  │
│  └───────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│  YamlConfig      │    │  PathHelper      │
│  配置管理        │    │  路径工具        │
└──────────────────┘    └──────────────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
         ┌───────────────────────┐
         │  N_m3u8DL-RE.exe      │
         │  下载工具              │
         └───────────────────────┘
```

## 12. 总结

本架构设计遵循以下原则：

1. **配置驱动**：通过配置文件控制行为
2. **单一职责**：每个方法职责明确
3. **错误处理**：完善的异常处理机制
4. **日志记录**：详细的调试日志
5. **向后兼容**：不影响现有功能
6. **跨平台**：支持多操作系统

下一步进入**Atomize（原子化）**阶段，将架构拆分为原子任务。
