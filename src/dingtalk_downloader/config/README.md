# 配置管理模块

## 模块概述

本模块负责管理项目的配置项，包括常量定义、日志配置、YAML配置管理和请求头管理，为整个项目提供统一的配置支持。采用单例模式、管理器模式和策略模式，提供高内聚、低耦合的配置管理方案。

## 模块架构

### 架构设计原则

- **单一职责原则**：每个类只负责一个明确的配置功能
- **开闭原则**：对扩展开放，对修改关闭
- **依赖倒置原则**：依赖抽象而非具体实现
- **单例模式**：确保配置文件在应用生命周期内只被加载一次
- **配置验证**：确保配置值的有效性和完整性

### 模块结构

```markdown
config/
├── constants.py # 常量定义模块
├── logger_config.py # 日志配置模块
├── yaml_config.py # YAML配置管理模块
├── header_manager.py # 请求头管理模块
└── **init**.py
```

## 功能描述

### Constants - 常量定义模块

**职责**：定义项目中的所有常量

**功能**：

- 定义浏览器类型常量
- 定义下载模式常量
- 定义保存模式常量
- 定义最大重试次数
- 提供浏览器选项映射
- 提供直播名称选择器配置

**设计模式**：常量模式（Constants Pattern）

### LoggerConfig - 日志配置模块

**职责**：配置和管理日志系统

**功能**：

- 配置日志级别和格式
- 支持控制台和文件日志输出
- 支持日志轮转和自动清理
- 自定义日志格式化器
- 支持日志文件按日期命名

**设计模式**：管理器模式（Manager Pattern）

### YamlConfig - YAML配置管理模块

**职责**：管理YAML格式的配置文件

**功能**：

- 采用单例模式确保配置文件只加载一次
- 支持配置验证，确保配置值的有效性和完整性
- 支持线程安全的并发访问
- 提供类型安全的配置访问接口（get_str、get_int、get_bool等）
- 支持配置热重载
- 支持嵌套配置访问

**核心算法**：

- 单例模式实现（双重检查锁定）
- 配置Schema验证
- 类型安全访问

**设计模式**：单例模式（Singleton Pattern）

### HeaderManager - 请求头管理模块

**职责**：统一管理请求头配置

**功能**：

- 从配置文件加载请求头
- 支持请求头动态覆盖
- 提供请求头缓存机制
- 支持请求头合并

**设计模式**：管理器模式（Manager Pattern）

## 核心实现原理

### Constants 实现原理

#### 常量定义

```python
# 配置文件路径
CONFIG_FILE_PATH = "./config/app.yaml"

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

# 最大重试次数
MAX_RETRY_COUNT = 5

# 浏览器选项映射
BROWSER_OPTION_MAP = {
    "1": BROWSER_TYPE_EDGE,
    "2": BROWSER_TYPE_CHROME,
    "3": BROWSER_TYPE_FIREFOX
}

# 直播名称选择器配置
LIVE_NAME_SELECTORS = [
    ("xpath", '//*[@id="live-room"]/div[1]/div[1]/h3'),
    ("css", "vwi5-oG8"),
    ("xpath", '//h3[contains(@class, "live-title")]'),
    ("css", ".live-title"),
]
```

### LoggerConfig 实现原理

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
    file_handler = logging.handlers.RotatingFileHandler(
        log_filename,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setLevel(numeric_level)
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
```

### YamlConfig 实现原理

#### 单例模式实现

```python
class YamlConfig:
    """YAML配置管理类，负责管理YAML格式的配置文件。"""

    _instance: Optional["YamlConfig"] = None
    _lock: threading.RLock = threading.RLock()

    def __new__(cls, config_file: Optional[str] = None) -> "YamlConfig":
        """单例模式实现，确保全局只有一个YamlConfig实例。"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._initialize(config_file)
                    cls._instance = instance
                    logger.debug("YamlConfig单例实例创建成功")
        return cls._instance
```

#### 配置Schema定义

```python
CONFIG_SCHEMA = {
    "app": {
        "required": True,
        "type": dict,
        "fields": {
            "name": {"required": True, "type": str},
            "version": {"required": True, "type": str},
            "build_date": {"required": True, "type": str},
        },
    },
    "download": {
        "required": True,
        "type": dict,
        "fields": {
            "default_dir": {"required": True, "type": str},
            "temp_dir": {"required": True, "type": str},
            "max_retry_count": {"required": True, "type": int, "min": 1, "max": 100},
        },
    },
    # ... 其他配置项
}
```

#### 配置验证

```python
def _validate_config(
    self, config: Dict[str, Any], schema: Dict[str, Any], path: str = ""
) -> None:
    """验证配置是否符合schema定义。"""
    for key, field_schema in schema.items():
        current_path = f"{path}.{key}" if path else key

        if field_schema.get("required", False) and key not in config:
            raise ConfigValidationError(f"缺少必填配置项: {current_path}")

        if key not in config:
            continue

        value = config[key]

        expected_type = field_schema.get("type")
        if expected_type and not isinstance(value, expected_type):
            raise ConfigValueError(
                f"配置项类型错误: {current_path}, 期望类型: "
                f"{expected_type.__name__}, 实际类型: {type(value).__name__}",
                current_path,
            )

        if "min" in field_schema and value < field_schema["min"]:
            raise ConfigValueError(
                f"配置值过小: {current_path}, 最小值: {field_schema['min']}, 实际值: {value}",
                current_path,
            )

        if "max" in field_schema and value > field_schema["max"]:
            raise ConfigValueError(
                f"配置值过大: {current_path}, 最大值: {field_schema['max']}, 实际值: {value}",
                current_path,
            )

        if "choices" in field_schema and value not in field_schema["choices"]:
            raise ConfigValueError(
                f"配置值无效: {current_path}, 可选值: {field_schema['choices']}, 实际值: {value}",
                current_path,
            )

        if "fields" in field_schema and isinstance(value, dict):
            self._validate_config(value, field_schema["fields"], current_path)
```

#### 类型安全访问

```python
def get_str(self, key: str, default: str = "") -> str:
    """获取字符串类型配置项。"""
    value = self.get(key, default)
    if value is None:
        return default
    if not isinstance(value, str):
        raise ConfigValueError(f"配置值类型错误，期望str，实际{type(value).__name__}", key)
    return value

def get_int(self, key: str, default: int = 0) -> int:
    """获取整数类型配置项。"""
    value = self.get(key, default)
    if value is None:
        return default
    if isinstance(value, bool):
        raise ConfigValueError(
            f"配置值类型错误，bool不能转换为int: {key}", key
        )
    try:
        return int(value)
    except (ValueError, TypeError) as e:
        raise ConfigValueError(f"配置值无法转换为int: {value}", key) from e

def get_bool(self, key: str, default: bool = False) -> bool:
    """获取布尔类型配置项。"""
    value = self.get(key, default)
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        if value.lower() in ("true", "1", "yes", "on"):
            return True
        if value.lower() in ("false", "0", "no", "off"):
            return False
    raise ConfigValueError(f"配置值无法转换为bool: {value}", key)
```

### HeaderManager 实现原理

#### 请求头加载

```python
def _load_headers(self) -> None:
    """从配置文件加载请求头到缓存。"""
    header_mapping = {
        "user_agent": "User-Agent",
        "referer": "Referer",
        "accept": "Accept",
        "accept_language": "Accept-Language",
        "accept_encoding": "Accept-Encoding",
        "connection": "Connection",
        "sec_fetch_dest": "Sec-Fetch-Dest",
        "sec_fetch_mode": "Sec-Fetch-Mode",
        "sec_fetch_site": "Sec-Fetch-Site",
        "sec_fetch_user": "Sec-Fetch-User",
        "upgrade_insecure_requests": "Upgrade-Insecure-Requests",
    }

    headers_config = self.config.get("headers", {})
    self._headers_cache.clear()

    for config_key, header_name in header_mapping.items():
        if config_key in headers_config:
            self._headers_cache[header_name] = headers_config[config_key]
            logger.debug(f"加载请求头: {header_name}")
```

#### 请求头获取

```python
def get_headers(self, include_overrides: bool = True) -> Dict[str, str]:
    """获取请求头字典。"""
    headers = self._headers_cache.copy()

    if include_overrides:
        # 应用覆盖的请求头（优先级更高）
        headers.update(self._override_headers)

    logger.debug(f"获取请求头字典，共 {len(headers)} 个请求头")
    return headers
```

## 使用方法

### Constants 使用示例

```python
from dingtalk_downloader.config.constants import (
    BROWSER_TYPE_EDGE,
    BROWSER_TYPE_CHROME,
    DOWNLOAD_MODE_SINGLE,
    SAVE_MODE_DEFAULT,
    BROWSER_OPTION_MAP,
    LIVE_NAME_SELECTORS
)

# 使用常量
browser_type = BROWSER_TYPE_EDGE
download_mode = DOWNLOAD_MODE_SINGLE
save_mode = SAVE_MODE_DEFAULT

# 使用映射
browser_option = "1"
browser_type = BROWSER_OPTION_MAP[browser_option]

# 使用直播名称选择器
for selector_type, selector_value in LIVE_NAME_SELECTORS:
    print(f"{selector_type}: {selector_value}")
```

### LoggerConfig 使用示例

```python
from dingtalk_downloader.config.logger_config import LoggerConfig
import logging

# 初始化日志系统
LoggerConfig.setup_logging()

# 获取 logger 实例
logger = logging.getLogger(__name__)

# 记录日志
logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

### YamlConfig 使用示例

```python
from dingtalk_downloader.config.yaml_config import YamlConfig

# 获取单例实例
config = YamlConfig.get_instance()

# 加载配置文件
config.load()

# 获取配置项
app_name = config.get_str("app.name")
app_version = config.get_str("app.version")
max_retry_count = config.get_int("download.max_retry_count")

# 获取嵌套配置项
default_dir = config.get_str("download.default_dir")

# 使用默认值
non_existent = config.get_str("non.existent.key", "default_value")

# 重新加载配置
config.reload()

# 验证配置
config.validate()
```

### HeaderManager 使用示例

```python
from dingtalk_downloader.config.header_manager import HeaderManager

# 创建请求头管理器
header_manager = HeaderManager()

# 获取所有请求头
headers = header_manager.get_headers()
print(f"请求头数量: {len(headers)}")

# 获取单个请求头
user_agent = header_manager.get_header("User-Agent")
print(f"User-Agent: {user_agent}")

# 重新加载配置
header_manager.reload_config()
```

## 接口参数说明

### Constants 常量

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
- `CONFIG_FILE_PATH`：配置文件路径（"./config/app.yaml"）
- `BROWSER_OPTION_MAP`：浏览器选项映射
- `LIVE_NAME_SELECTORS`：直播名称选择器配置

### LoggerConfig 类

#### setup_logging(log_level: Optional[str] = None) -> None

**参数**：

- `log_level`：日志级别，默认从环境变量 LOG_LEVEL 读取

**功能**：初始化日志系统

### YamlConfig 类

#### **new**(config_file: Optional[str] = None) -> YamlConfig

**参数**：

- `config_file`：配置文件路径，仅首次创建时有效

**返回值**：

- `YamlConfig`：单例实例

**功能**：获取单例实例

#### load() -> None

**参数**：无

**返回值**：无

**功能**：加载配置文件

**异常**：

- `ConfigLoadError`：配置文件加载失败时
- `ConfigValidationError`：配置文件验证失败时

#### get(key: str, default: Any = None) -> Any

**参数**：

- `key`：配置项键，支持点号分隔的嵌套键（如"download.default_dir"）
- `default`：默认值

**返回值**：

- `Any`：配置项值，如果不存在则返回默认值

**功能**：获取配置项

#### get_str(key: str, default: str = "") -> str

**参数**：

- `key`：配置项键
- `default`：默认值

**返回值**：

- `str`：字符串类型的配置项值

**异常**：

- `ConfigValueError`：配置值不是字符串类型时

**功能**：获取字符串类型配置项

#### get_int(key: str, default: int = 0) -> int

**参数**：

- `key`：配置项键
- `default`：默认值

**返回值**：

- `int`：整数类型的配置项值

**异常**：

- `ConfigValueError`：配置值不是整数类型时

**功能**：获取整数类型配置项

#### get_float(key: str, default: float = 0.0) -> float

**参数**：

- `key`：配置项键
- `default`：默认值

**返回值**：

- `float`：浮点数类型的配置项值

**异常**：

- `ConfigValueError`：配置值不是浮点数类型时

**功能**：获取浮点数类型配置项

#### get_bool(key: str, default: bool = False) -> bool

**参数**：

- `key`：配置项键
- `default`：默认值

**返回值**：

- `bool`：布尔类型的配置项值

**异常**：

- `ConfigValueError`：配置值不是布尔类型时

**功能**：获取布尔类型配置项

#### get_list(key: str, default: Optional[List[Any]] = None) -> List[Any]

**参数**：

- `key`：配置项键
- `default`：默认值

**返回值**：

- `List[Any]`：列表类型的配置项值

**异常**：

- `ConfigValueError`：配置值不是列表类型时

**功能**：获取列表类型配置项

#### get_dict(key: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]

**参数**：

- `key`：配置项键
- `default`：默认值

**返回值**：

- `Dict[str, Any]`：字典类型的配置项值

**异常**：

- `ConfigValueError`：配置值不是字典类型时

**功能**：获取字典类型配置项

#### reload() -> None

**参数**：无

**返回值**：无

**功能**：重新加载配置文件

#### validate() -> bool

**参数**：无

**返回值**：

- `bool`：验证结果，True表示配置有效

**异常**：

- `ConfigValidationError`：配置验证失败时

**功能**：验证配置有效性

#### get_instance(cls, config_file: Optional[str] = None) -> YamlConfig

**参数**：

- `config_file`：配置文件路径，仅首次创建时有效

**返回值**：

- `YamlConfig`：单例实例

**功能**：获取单例实例（类方法）

#### reset_instance(cls) -> None

**参数**：无

**返回值**：无

**功能**：重置单例实例（类方法，主要用于测试）

### HeaderManager 类

#### **init**()

**参数**：无

**功能**：初始化请求头管理器

#### get_headers(include_overrides: bool = True) -> Dict[str, str]

**参数**：

- `include_overrides`：是否包含覆盖的请求头，默认为True

**返回值**：

- `Dict[str, str]`：请求头字典

**功能**：获取请求头字典

#### get_header(name: str, default: Optional[str] = None, include_overrides: bool = True) -> Optional[str]

**参数**：

- `name`：请求头名称
- `default`：默认值
- `include_overrides`：是否包含覆盖的请求头，默认为True

**返回值**：

- `Optional[str]`：请求头值，如果不存在则返回默认值

**功能**：获取单个请求头

#### reload_config() -> None

**参数**：无

**返回值**：无

**功能**：重新加载配置文件

## 依赖关系

### 依赖的 Python 模块

1. `logging` - 日志系统
2. `logging.handlers` - 日志处理器
3. `os` - 操作系统接口
4. `yaml` - YAML 处理
5. `threading` - 线程支持
6. `typing` - 类型提示
7. `datetime` - 日期时间处理

### 被依赖的模块

1. `main` - 主程序入口
2. `core.downloader` - 下载器核心模块
3. `core.cookie_handler` - Cookie 处理模块
4. `core.m3u8_parser` - m3u8 解析模块
5. `browser.browser_factory` - 浏览器工厂
6. `browser.*_driver` - 浏览器驱动
7. `binary.n_m3u8dl_re` - N_m3u8DL-RE 调用封装
8. `utils.path_selector` - 路径选择器

## 数据流程

### 日志系统流程

```text
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

### YAML配置管理流程

```text
获取单例实例
  ↓
加载配置文件
  ↓
验证配置有效性
  ↓
获取/设置配置项
  ↓
重新加载配置（可选）
```

### 请求头管理流程

```text
创建请求头管理器
  ↓
从配置文件加载请求头
  ↓
缓存请求头
  ↓
获取请求头
  ↓
应用覆盖请求头（可选）
```

## 设计模式应用

### 1. 单例模式（Singleton Pattern）

**应用类**：YamlConfig

**说明**：确保配置文件在应用生命周期内只被加载一次，使用双重检查锁定实现线程安全。

### 2. 管理器模式（Manager Pattern）

**应用类**：LoggerConfig、HeaderManager

**说明**：统一管理日志和请求头的生命周期。

### 3. 常量模式（Constants Pattern）

**应用类**：Constants

**说明**：集中管理项目中的所有常量，避免魔法数字和字符串。

### 4. 策略模式（Strategy Pattern）

**应用类**：LIVE_NAME_SELECTORS

**说明**：提供多种直播名称获取策略，按优先级依次尝试。

## 异常处理

### 异常层次结构

```tree
Exception
  └── ConfigError (配置异常基类)
        ├── ConfigLoadError (配置加载异常)
        ├── ConfigValueError (配置值异常)
        └── ConfigValidationError (配置验证异常)
```

### 异常处理策略

1. **配置加载**：配置文件不存在或格式错误时抛出 ConfigLoadError
2. **配置验证**：配置值不符合 Schema 时抛出 ConfigValidationError 或 ConfigValueError
3. **类型安全**：类型转换失败时抛出 ConfigValueError
4. **日志记录**：记录详细的错误信息和堆栈跟踪

## 注意事项

### 1. 常量使用

- 所有常量都应该通过 `constants.py` 导入使用
- 不要在代码中硬编码常量值
- 使用映射关系而不是硬编码选项

### 2. 日志级别

- 支持通过环境变量 `LOG_LEVEL` 设置
- 默认级别为 INFO
- 支持的级别：DEBUG、INFO、WARNING、ERROR、CRITICAL

### 3. 日志文件

- 日志文件按日期命名
- 单个文件最大 10MB
- 最多保留 5 个备份文件

### 4. YAML配置

- 配置文件路径为 `./config/app.yaml`
- 支持嵌套配置访问
- 支持类型安全的配置访问
- 支持配置验证

### 5. 单例模式

- YamlConfig 使用单例模式
- 线程安全，使用双重检查锁定
- 支持重置单例实例（主要用于测试）

### 6. 请求头管理

- 请求头从配置文件加载
- 支持请求头动态覆盖
- 提供请求头缓存机制

## 性能优化

### 1. 单例模式

- 配置文件只加载一次，避免重复加载
- 使用缓存提高访问速度

### 2. 线程安全

- 使用 RLock 确保线程安全
- 避免竞态条件

### 3. 日志轮转

- 自动轮转日志文件，避免单个文件过大
- 自动清理过期日志

## 扩展方向

### 1. 配置验证

- 添加更多配置验证规则
- 支持自定义验证函数
- 支持配置依赖验证

### 2. 配置模板

- 提供配置文件模板
- 支持配置项默认值
- 支持配置文件生成

### 3. 日志增强

- 支持日志压缩
- 支持日志上传到远程服务器
- 支持日志过滤
- 支持结构化日志（JSON格式）

### 4. 多环境配置

- 支持开发、测试、生产环境配置
- 支持配置文件切换
- 支持环境变量覆盖

### 5. 配置热更新

- 支持配置文件监听
- 支持配置热更新
- 支持配置变更通知

### 6. 请求头增强

- 支持请求头模板
- 支持请求头动态生成
- 支持请求头加密

## 测试建议

### 1. 单元测试

- 测试各个类的独立功能
- 测试配置加载和验证
- 测试日志配置
- 测试请求头管理

### 2. 集成测试

- 测试配置管理流程
- 测试日志系统
- 测试请求头管理

### 3. 异常测试

- 测试各种异常情况
- 验证异常处理逻辑
- 测试边界条件

### 4. 线程安全测试

- 测试单例模式的线程安全性
- 测试并发访问配置

## 维护责任人

- **主要维护者**：项目团队
- **最后更新日期**：2026-01-27

## 相关文档

- [主程序入口模块](../README.md)
- [核心业务模块](../core/README.md)
- [浏览器驱动模块](../browser/README.md)
- [工具模块](../utils/README.md)
