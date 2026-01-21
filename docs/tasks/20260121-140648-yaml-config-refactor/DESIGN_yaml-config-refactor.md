# DESIGN_yaml-config-refactor

## 任务概述
- **任务名称**: yaml-config-refactor
- **创建时间**: 2026-01-21 14:07:06
- **时间戳**: 20260121-140706

## 系统架构设计

### 1. 整体架构

#### 1.1 架构层次

```
┌─────────────────────────────────────────────────────────┐
│                     应用层 (Application)                  │
│  main.py, downloader.py, m3u8_parser.py, cookie_handler  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   配置层 (Configuration)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Settings    │  │ YamlConfig    │  │LoggerConfig  │  │
│  │  (向后兼容)   │  │  (核心实现)   │  │  (日志配置)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   数据层 (Data)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ config.yaml  │  │  constants   │  │  .env文件    │  │
│  │ (用户配置)   │  │  (常量定义)   │  │ (环境变量)    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

#### 1.2 模块职责

**应用层**：
- 负责业务逻辑处理
- 通过配置层获取配置信息
- 不直接操作配置文件

**配置层**：
- Settings类：提供向后兼容的配置接口，内部委托给YamlConfig
- YamlConfig类：核心配置管理类，负责YAML文件的加载、解析、保存
- LoggerConfig类：日志配置管理，从YamlConfig读取配置
- constants.py：提供枚举常量和映射字典

**数据层**：
- config.yaml：用户配置文件，存储可配置的参数
- constants.py：代码常量定义
- .env文件：环境变量，存储敏感信息

### 2. 核心类设计

#### 2.1 YamlConfig类

**类图**：
```
┌─────────────────────────────────────────┐
│            YamlConfig                   │
├─────────────────────────────────────────┤
│ - config: dict                          │
│ - config_file: str                      │
│ - default_config: dict                  │
│ - _loaded: bool                         │
├─────────────────────────────────────────┤
│ + __init__(config_file: Optional[str]) │
│ + load() -> None                        │
│ + save() -> None                        │
│ + get(key: str, default: Any) -> Any   │
│ + set(key: str, value: Any) -> None    │
│ + get_nested(keys: List[str], ...)     │
│ + set_nested(keys: List[str], ...)      │
│ + reload() -> None                      │
│ + validate() -> bool                    │
│ - _load_default_config() -> dict        │
│ - _merge_configs(user, default) -> dict│
└─────────────────────────────────────────┘
```

**方法说明**：

1. **__init__(config_file: Optional[str])**
   - 功能：初始化YamlConfig实例
   - 参数：config_file - 配置文件路径，默认为~/.dingtalk_downloader/config.yaml
   - 实现：创建配置目录，加载默认配置，加载用户配置

2. **load() -> None**
   - 功能：加载配置文件
   - 实现：读取YAML文件，解析为字典，与默认配置合并

3. **save() -> None**
   - 功能：保存配置到文件
   - 实现：将config字典序列化为YAML格式，写入文件

4. **get(key: str, default: Any = None) -> Any**
   - 功能：获取配置项
   - 参数：key - 配置键，支持点号分隔的嵌套键（如"download.default_dir"）
   - 返回：配置值，不存在则返回默认值

5. **set(key: str, value: Any) -> None**
   - 功能：设置配置项
   - 参数：key - 配置键，value - 配置值
   - 实现：更新config字典，调用save()保存

6. **get_nested(keys: List[str], default: Any = None) -> Any**
   - 功能：获取嵌套配置项
   - 参数：keys - 键列表，default - 默认值
   - 返回：配置值

7. **set_nested(keys: List[str], value: Any) -> None**
   - 功能：设置嵌套配置项
   - 参数：keys - 键列表，value - 配置值

8. **reload() -> None**
   - 功能：重新加载配置文件
   - 实现：清空config，重新调用load()

9. **validate() -> bool**
   - 功能：验证配置有效性
   - 返回：验证结果
   - 实现：检查必需的配置项，验证配置值类型

#### 2.2 Settings类（重构）

**类图**：
```
┌─────────────────────────────────────────┐
│            Settings                      │
├─────────────────────────────────────────┤
│ - yaml_config: YamlConfig               │
├─────────────────────────────────────────┤
│ + __init__(config_file: Optional[str]) │
│ + load() -> None                        │
│ + save() -> None                        │
│ + get(key: str, default: Any) -> Any    │
│ + set(key: str, value: Any) -> None     │
│ + migrate_from_json(json_file: str)    │
└─────────────────────────────────────────┘
```

**设计说明**：
- 保持现有API不变，确保向后兼容
- 内部使用YamlConfig实现
- 提供从JSON到YAML的迁移功能

#### 2.3 LoggerConfig类（改造）

**改造点**：
1. 从YamlConfig读取日志配置
2. 支持动态更新日志级别
3. 保持现有日志格式和功能

**方法改造**：
```python
@staticmethod
def setup_logging(log_level: Optional[str] = None) -> None:
    # 改造前：从环境变量读取
    log_level_str = log_level or os.getenv("LOG_LEVEL", "INFO")
    
    # 改造后：从YamlConfig读取
    from .yaml_config import YamlConfig
    yaml_config = YamlConfig()
    log_level_str = log_level or yaml_config.get("logging.level", "INFO")
```

### 3. 配置文件设计

#### 3.1 YAML配置文件结构

```yaml
# ========================================
# 钉钉直播回放下载工具 - 配置文件
# ========================================
# 说明：
#   1. 本文件用于配置钉钉直播回放下载工具的各项参数
#   2. 配置文件位置：~/.dingtalk_downloader/config.yaml
#   3. 修改配置后重启程序生效
#   4. 注释以#开头
# ========================================

# ========================================
# 应用配置
# ========================================
app:
  # 应用名称
  name: "钉钉直播回放下载工具"
  # 应用版本
  version: "1.5.0"

# ========================================
# 下载配置
# ========================================
download:
  # 默认下载目录（相对于项目根目录）
  # 说明：当保存模式为默认时，视频将保存到此目录
  default_dir: "Downloads"
  
  # 临时m3u8文件名
  # 说明：下载过程中使用的临时文件名
  temp_m3u8_file: "output.m3u8"
  
  # 最大重试次数
  # 说明：获取m3u8链接失败时的最大重试次数
  max_retry_count: 5

# ========================================
# 浏览器配置
# ========================================
browser:
  # 默认浏览器类型
  # 可选值：edge, chrome, firefox
  default_type: "edge"
  
  # 是否使用无头模式
  # 说明：无头模式下浏览器不显示界面
  headless: false
  
  # 页面加载超时时间（秒）
  # 说明：等待页面加载完成的最大时间
  timeout: 30

# ========================================
# 日志配置
# ========================================
logging:
  # 日志级别
  # 可选值：DEBUG, INFO, WARNING, ERROR, CRITICAL
  # 说明：DEBUG显示所有日志，CRITICAL只显示严重错误
  level: "INFO"
  
  # 日志目录
  # 说明：日志文件保存目录
  dir: "logs"
  
  # 单个日志文件最大大小（字节）
  # 说明：超过此大小会自动创建新文件
  # 10485760 = 10MB
  max_bytes: 10485760
  
  # 保留的日志文件数量
  # 说明：超过此数量的旧日志文件会被删除
  backup_count: 5
  
  # 日志保留天数
  # 说明：超过此天数的日志文件会被清理
  retention_days: 30

# ========================================
# 请求头配置
# ========================================
headers:
  # User-Agent
  # 说明：标识客户端类型和版本
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
  
  # Referer
  # 说明：表示请求的来源页面
  referer: "https://n.dingtalk.com/"
  
  # Accept
  # 说明：指定客户端能够接收的内容类型
  accept: "application/vnd.apple.mpegurl, text/plain, */*"
  
  # Accept-Language
  # 说明：指定客户端偏好的语言
  accept_language: "zh-CN,zh;q=0.9,en;q=0.8"
  
  # Accept-Encoding
  # 说明：指定客户端支持的压缩算法
  accept_encoding: "gzip, deflate, br"

# ========================================
# N_m3u8DL-RE配置
# ========================================
n_m3u8dl_re:
  # 可执行文件路径
  # 说明：N_m3u8DL-RE工具的完整路径
  executable_path: "assets/bin/N_m3u8DL-RE.exe"
  
  # UI语言
  # 说明：N_m3u8DL-RE工具的界面语言
  ui_language: "zh-CN"

# ========================================
# FFmpeg配置
# ========================================
ffmpeg:
  # 可执行文件路径
  # 说明：FFmpeg工具的完整路径
  executable_path: "assets/bin/ffmpeg.exe"
```

#### 3.2 配置文件位置

**优先级顺序**（从高到低）：
1. 用户配置文件：`~/.dingtalk_downloader/config.yaml`
2. 项目配置文件：`config.yaml`（项目根目录，可选）
3. 默认配置：代码中定义的默认值

**配置加载流程**：
```
1. 加载默认配置（代码中定义）
   ↓
2. 加载项目配置文件（如果存在）
   ↓
3. 加载用户配置文件（如果存在）
   ↓
4. 合并配置（用户配置覆盖项目配置，项目配置覆盖默认配置）
```

### 4. 数据流设计

#### 4.1 配置读取流程

```
应用代码调用Settings.get(key)
        ↓
Settings委托给YamlConfig.get(key)
        ↓
YamlConfig检查是否已加载
        ↓
未加载 → 调用load()
        ↓
load()执行：
  1. 加载默认配置
  2. 加载项目配置（可选）
  3. 加载用户配置
  4. 合并配置
        ↓
从config字典中查找key
        ↓
返回配置值或默认值
```

#### 4.2 配置写入流程

```
应用代码调用Settings.set(key, value)
        ↓
Settings委托给YamlConfig.set(key, value)
        ↓
YamlConfig更新config字典
        ↓
调用save()
        ↓
save()执行：
  1. 将config字典序列化为YAML
  2. 写入配置文件
        ↓
保存完成
```

### 5. 接口设计

#### 5.1 YamlConfig公共接口

```python
class YamlConfig:
    """YAML配置管理类"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化YamlConfig实例
        
        Args:
            config_file: 配置文件路径，默认为None（使用默认路径）
        """
        pass
    
    def load(self) -> None:
        """
        加载配置文件
        
        从配置文件中加载配置项，如果配置文件不存在，则使用默认配置。
        """
        pass
    
    def save(self) -> None:
        """
        保存配置
        
        将配置项保存到配置文件。
        """
        pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置项键，支持点号分隔的嵌套键（如"download.default_dir"）
            default: 默认值
        
        Returns:
            配置项值，如果不存在则返回默认值
        """
        pass
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置项
        
        Args:
            key: 配置项键，支持点号分隔的嵌套键
            value: 配置项值
        """
        pass
    
    def get_nested(self, keys: List[str], default: Any = None) -> Any:
        """
        获取嵌套配置项
        
        Args:
            keys: 键列表
            default: 默认值
        
        Returns:
            配置项值，如果不存在则返回默认值
        """
        pass
    
    def set_nested(self, keys: List[str], value: Any) -> None:
        """
        设置嵌套配置项
        
        Args:
            keys: 键列表
            value: 配置项值
        """
        pass
    
    def reload(self) -> None:
        """
        重新加载配置文件
        
        清空当前配置，重新从文件加载。
        """
        pass
    
    def validate(self) -> bool:
        """
        验证配置有效性
        
        Returns:
            验证结果，True表示配置有效，False表示配置无效
        """
        pass
```

#### 5.2 Settings公共接口（保持不变）

```python
class Settings:
    """配置类，负责管理配置项（向后兼容）"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置
        
        Args:
            config_file: 配置文件路径，默认为None（使用默认路径）
        """
        pass
    
    def load(self) -> None:
        """
        加载配置
        
        从配置文件中加载配置项，如果配置文件不存在，则使用默认配置。
        """
        pass
    
    def save(self) -> None:
        """
        保存配置
        
        将配置项保存到配置文件。
        """
        pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        Args:
            key: 配置项键
            default: 默认值
        
        Returns:
            配置项值，如果不存在则返回默认值
        """
        pass
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置项
        
        Args:
            key: 配置项键
            value: 配置项值
        """
        pass
    
    def migrate_from_json(self, json_file: str) -> None:
        """
        从JSON配置文件迁移到YAML
        
        Args:
            json_file: JSON配置文件路径
        """
        pass
```

### 6. 错误处理设计

#### 6.1 错误类型

1. **配置文件不存在**
   - 处理：使用默认配置，记录警告日志

2. **配置文件格式错误**
   - 处理：捕获YAML解析异常，记录错误日志，使用默认配置

3. **配置项不存在**
   - 处理：返回默认值，记录调试日志

4. **配置项类型错误**
   - 处理：记录错误日志，使用默认值

5. **配置文件权限错误**
   - 处理：捕获IOError，记录错误日志，提示用户检查权限

#### 6.2 错误处理策略

```python
try:
    # 尝试加载配置文件
    with open(self.config_file, "r", encoding="utf-8") as f:
        user_config = yaml.safe_load(f)
except FileNotFoundError:
    # 配置文件不存在，使用默认配置
    logger.warning(f"配置文件不存在: {self.config_file}，使用默认配置")
    user_config = {}
except yaml.YAMLError as e:
    # YAML格式错误，使用默认配置
    logger.error(f"配置文件格式错误: {e}，使用默认配置")
    user_config = {}
except IOError as e:
    # IO错误，使用默认配置
    logger.error(f"读取配置文件失败: {e}，使用默认配置")
    user_config = {}
```

### 7. 性能优化设计

#### 7.1 配置缓存

- **策略**：首次加载后缓存配置，避免重复读取文件
- **实现**：使用_loaded标志位，记录配置是否已加载

#### 7.2 延迟加载

- **策略**：只有在首次访问配置时才加载配置文件
- **实现**：在get()方法中检查_loaded标志

#### 7.3 配置合并优化

- **策略**：使用字典合并算法，避免递归调用
- **实现**：使用dict.update()或自定义合并函数

### 8. 测试策略

#### 8.1 单元测试

1. **YamlConfig测试**
   - 测试配置加载
   - 测试配置保存
   - 测试配置获取
   - 测试配置设置
   - 测试嵌套配置
   - 测试配置验证
   - 测试错误处理

2. **Settings测试**
   - 测试向后兼容性
   - 测试JSON到YAML迁移

3. **LoggerConfig测试**
   - 测试从YAML读取日志配置
   - 测试日志级别动态更新

#### 8.2 集成测试

1. 测试配置系统与现有模块的兼容性
2. 测试配置文件热加载
3. 测试配置迁移功能

### 9. 部署策略

#### 9.1 依赖管理

在requirements.txt中添加：
```
PyYAML>=6.0
```

#### 9.2 配置文件分发

1. 将config.yaml.example打包到项目中
2. 首次运行时自动创建用户配置文件
3. 提供配置迁移脚本

#### 9.3 向后兼容

1. 保留Settings类的现有API
2. 提供JSON到YAML的自动迁移
3. 在文档中说明配置变更

### 10. 扩展性设计

#### 10.1 配置验证

- 支持配置项类型验证
- 支持配置项范围验证
- 支持自定义验证规则

#### 10.2 配置热更新

- 支持监听配置文件变化
- 支持自动重新加载配置
- 支持配置变更通知

#### 10.3 多环境配置

- 支持开发、测试、生产环境配置
- 支持环境变量覆盖
- 支持配置文件继承
