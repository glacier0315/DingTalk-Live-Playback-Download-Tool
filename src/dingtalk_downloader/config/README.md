# 配置管理模块

## 模块概述

本模块负责管理项目的配置项，包括常量定义、日志配置和用户配置管理，为整个项目提供统一的配置支持。

## 功能描述

### constants.py - 常量定义模块

**功能**：
- 定义项目中的所有常量
- 包括浏览器类型、下载模式、保存模式等
- 提供映射关系（选项映射）

### logger_config.py - 日志配置模块

**功能**：
- 配置和管理日志系统
- 支持控制台和文件日志输出
- 支持日志轮转和自动清理
- 自定义日志格式化器

### settings.py - 配置管理模块

**功能**：
- 管理用户配置项
- 支持配置文件的加载和保存
- 提供配置项的获取和设置接口

## 核心实现原理

### constants.py 实现原理

#### 常量定义

```python
# 浏览器类型
BROWSER_TYPE_EDGE = "edge"
BROWSER_TYPE_CHROME = "chrome"
BROWSER_TYPE_FIREFOX = "firefox"

# 下载模式
DOWNLOAD_MODE_SINGLE = "1"
DOWNLOAD_MODE_BATCH = "2"

# 保存模式
SAVE_MODE_DEFAULT = "1"
SAVE_MODE_MANUAL = "2"
```

#### 映射关系

```python
# 浏览器选项映射
BROWSER_OPTION_MAP = {
    "1": BROWSER_TYPE_EDGE,
    "2": BROWSER_TYPE_CHROME,
    "3": BROWSER_TYPE_FIREFOX
}

# 下载模式映射
DOWNLOAD_MODE_MAP = {
    "1": DOWNLOAD_MODE_SINGLE,
    "2": DOWNLOAD_MODE_BATCH
}

# 保存模式映射
SAVE_MODE_MAP = {
    "1": SAVE_MODE_DEFAULT,
    "2": SAVE_MODE_MANUAL
}
```

### logger_config.py 实现原理

#### 自定义格式化器

```python
class CustomFormatter(logging.Formatter):
    """自定义日志格式化器"""

    def format(self, record: logging.LogRecord) -> str:
        if hasattr(record, "module_name"):
            record.module_name = record.module_name
        else:
            record.module_name = record.name.split(".")[-1]

        return super().format(record)
```

#### 日志格式

```
[YYYY-MM-DD HH:MM:SS.mmm] [LEVEL     ] [MODULE_NAME          ] MESSAGE
```

#### 日志轮转

```python
class RotatingFileHandlerWithCleanup(logging.handlers.RotatingFileHandler):
    """带清理功能的文件处理器"""

    def __init__(self, filename: str, max_bytes: int = 10 * 1024 * 1024, backup_count: int = 5):
        super().__init__(filename, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
```

#### 日志初始化

```python
def setup_logging(log_level: Optional[str] = None) -> None:
    # 创建日志目录
    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)

    # 获取日志级别
    log_level_str = log_level or os.getenv("LOG_LEVEL", "INFO")
    numeric_level = getattr(logging, log_level_str.upper(), logging.INFO)

    # 配置根日志记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # 创建格式化器
    formatter = CustomFormatter(
        fmt="[%(asctime)s.%(msecs)03d] [%(levelname)-8s] [%(module_name)-20s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 添加文件处理器
    log_filename = os.path.join(log_dir, f"dingtalk_downloader_{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler = RotatingFileHandlerWithCleanup(log_filename)
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
```

#### 日志清理

```python
def clean_old_logs(days: int = 30) -> None:
    now = datetime.now()

    for filename in os.listdir(log_dir):
        if not filename.startswith("dingtalk_downloader_") or not filename.endswith(".log"):
            continue

        filepath = os.path.join(log_dir, filename)
        file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        file_age = (now - file_mtime).days

        if file_age > days:
            os.remove(filepath)
            logger.info(f"已删除过期日志文件: {filename}")
```

### settings.py 实现原理

#### 配置文件路径

```python
def __init__(self, config_file: Optional[str] = None):
    if config_file is None:
        config_dir = os.path.join(os.path.expanduser("~"), ".dingtalk_downloader")
        os.makedirs(config_dir, exist_ok=True)
        self.config_file = os.path.join(config_dir, "config.json")
    else:
        self.config_file = config_file
    self.load()
```

#### 配置加载

```python
def load(self) -> None:
    if os.path.exists(self.config_file):
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"加载配置文件失败: {e}", exc_info=True)
            self.config = {}
    else:
        self.config = {}
```

#### 配置保存

```python
def save(self) -> None:
    try:
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
    except IOError as e:
        logger.error(f"保存配置文件失败: {e}", exc_info=True)
```

## 使用方法

### constants.py 使用示例

```python
from dingtalk_downloader.config.constants import (
    BROWSER_TYPE_EDGE,
    BROWSER_TYPE_CHROME,
    DOWNLOAD_MODE_SINGLE,
    SAVE_MODE_DEFAULT,
    BROWSER_OPTION_MAP
)

# 使用常量
browser_type = BROWSER_TYPE_EDGE
download_mode = DOWNLOAD_MODE_SINGLE
save_mode = SAVE_MODE_DEFAULT

# 使用映射
browser_option = "1"
browser_type = BROWSER_OPTION_MAP[browser_option]
```

### logger_config.py 使用示例

```python
from dingtalk_downloader.config.logger_config import LoggerConfig
import logging

# 初始化日志系统
LoggerConfig.setup_logging()

# 获取 logger 实例
logger = LoggerConfig.get_logger(__name__)

# 记录日志
logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")

# 清理过期日志
LoggerConfig.clean_old_logs(days=30)
```

### settings.py 使用示例

```python
from dingtalk_downloader.config.settings import Settings

# 创建配置管理器
settings = Settings()

# 获取配置项
browser_type = settings.get("browser_type", "edge")
download_mode = settings.get("download_mode", "1")

# 设置配置项
settings.set("browser_type", "chrome")
settings.set("download_mode", "2")

# 使用自定义配置文件
settings = Settings(config_file="/path/to/config.json")
```

## 接口参数说明

### constants.py 常量

#### 浏览器类型常量

- `BROWSER_TYPE_EDGE`：Edge 浏览器
- `BROWSER_TYPE_CHROME`：Chrome 浏览器
- `BROWSER_TYPE_FIREFOX`：Firefox 浏览器

#### 下载模式常量

- `DOWNLOAD_MODE_SINGLE`：单个下载模式（"1"）
- `DOWNLOAD_MODE_BATCH`：批量下载模式（"2"）

#### 保存模式常量

- `SAVE_MODE_DEFAULT`：默认保存模式（"1"）
- `SAVE_MODE_MANUAL`：手动保存模式（"2"）

#### 其他常量

- `MAX_RETRY_COUNT`：最大重试次数（5）
- `DEFAULT_DOWNLOAD_DIR`：默认下载目录（"Downloads"）
- `TEMP_M3U8_FILE`：临时 m3u8 文件名（"output.m3u8"）

### LoggerConfig 类

#### setup_logging(log_level: Optional[str] = None) -> None

**参数**：
- `log_level`：日志级别，默认从环境变量 LOG_LEVEL 读取

**功能**：初始化日志系统

#### get_logger(name: str) -> logging.Logger

**参数**：
- `name`：logger 名称，通常使用 `__name__`

**返回值**：
- `logging.Logger`：logger 实例

**功能**：获取 logger 实例

#### clean_old_logs(days: int = 30) -> None

**参数**：
- `days`：保留天数，默认 30 天

**功能**：清理过期日志文件

### Settings 类

#### __init__(config_file: Optional[str] = None)

**参数**：
- `config_file`：配置文件路径，默认为 None（使用默认路径）

**功能**：初始化配置管理器

#### load() -> None

**参数**：无

**返回值**：无

**功能**：从配置文件加载配置

#### save() -> None

**参数**：无

**返回值**：无

**功能**：保存配置到文件

#### get(key: str, default: Any = None) -> Any

**参数**：
- `key`：配置项键
- `default`：默认值

**返回值**：
- `Any`：配置项值，如果不存在则返回默认值

**功能**：获取配置项

#### set(key: str, value: Any) -> None

**参数**：
- `key`：配置项键
- `value`：配置项值

**返回值**：无

**功能**：设置配置项

## 依赖关系

### 依赖的 Python 模块

1. `logging` - 日志系统
2. `logging.handlers` - 日志处理器
3. `os` - 操作系统接口
4. `json` - JSON 处理
5. `datetime` - 日期时间处理
6. `typing` - 类型提示

### 被依赖的模块

1. `main` - 主程序入口
2. `core.downloader` - 下载器核心模块
3. `core.cookie_handler` - Cookie 处理模块
4. `core.m3u8_parser` - m3u8 解析模块
5. `browser.browser_factory` - 浏览器工厂
6. `browser.*_driver` - 浏览器驱动

## 数据流程

### 日志系统流程

```
初始化日志系统
  ↓
创建日志目录
  ↓
配置根日志记录器
  ↓
创建格式化器
  ↓
添加控制台处理器
  ↓
添加文件处理器
  ↓
记录日志
```

### 配置管理流程

```
创建配置管理器
  ↓
加载配置文件
  ↓
获取/设置配置项
  ↓
保存配置文件
```

## 注意事项

1. **常量使用**
   - 所有常量都应该通过 `constants.py` 导入使用
   - 不要在代码中硬编码常量值

2. **日志级别**
   - 支持通过环境变量 `LOG_LEVEL` 设置
   - 默认级别为 INFO
   - 支持的级别：DEBUG、INFO、WARNING、ERROR、CRITICAL

3. **日志文件**
   - 日志文件按日期命名
   - 单个文件最大 10MB
   - 最多保留 5 个备份文件

4. **配置文件**
   - 默认路径为 `~/.dingtalk_downloader/config.json`
   - 支持 JSON 格式
   - 自动创建目录

5. **异常处理**
   - 配置文件加载失败时使用空配置
   - 日志系统初始化失败时使用基本配置

## 扩展方向

1. **配置验证**
   - 添加配置项验证逻辑
   - 支持配置项类型检查

2. **配置模板**
   - 提供配置文件模板
   - 支持配置项默认值

3. **日志增强**
   - 支持日志压缩
   - 支持日志上传到远程服务器
   - 支持日志过滤

4. **多环境配置**
   - 支持开发、测试、生产环境配置
   - 支持配置文件切换

5. **配置热更新**
   - 支持配置文件监听
   - 支持配置热更新

## 相关文档

- [主程序入口模块](../README.md)
- [核心业务模块](../core/README.md)
- [浏览器驱动模块](../browser/README.md)
