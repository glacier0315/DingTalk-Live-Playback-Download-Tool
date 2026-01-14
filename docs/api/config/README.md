# Config 模块 API 文档

## 模块概述

Config 模块是 DingTalk 直播回放下载工具的配置管理模块，负责管理项目中的常量定义和配置项。该模块包含以下核心组件：

- **constants**: 常量定义模块，定义项目中的所有常量
- **Settings**: 配置类，负责管理配置项

## 常量文档

### constants 模块

常量定义模块，定义项目中的所有常量。

#### 浏览器类型常量

```python
BROWSER_TYPE_EDGE = "edge"
BROWSER_TYPE_CHROME = "chrome"
BROWSER_TYPE_FIREFOX = "firefox"
```

**说明**：定义支持的浏览器类型

**使用示例**：

```python
from dingtalk_downloader.config.constants import BROWSER_TYPE_EDGE, BROWSER_TYPE_CHROME, BROWSER_TYPE_FIREFOX

browser_type = BROWSER_TYPE_EDGE
print(f"浏览器类型: {browser_type}")
```

#### 下载模式常量

```python
DOWNLOAD_MODE_SINGLE = "1"
DOWNLOAD_MODE_BATCH = "2"
```

**说明**：定义下载模式

**使用示例**：

```python
from dingtalk_downloader.config.constants import DOWNLOAD_MODE_SINGLE, DOWNLOAD_MODE_BATCH

download_mode = DOWNLOAD_MODE_SINGLE
print(f"下载模式: {download_mode}")
```

#### 保存模式常量

```python
SAVE_MODE_DEFAULT = "1"
SAVE_MODE_MANUAL = "2"
```

**说明**：定义保存模式

**使用示例**：

```python
from dingtalk_downloader.config.constants import SAVE_MODE_DEFAULT, SAVE_MODE_MANUAL

save_mode = SAVE_MODE_DEFAULT
print(f"保存模式: {save_mode}")
```

#### 最大重试次数常量

```python
MAX_RETRY_COUNT = 5
```

**说明**：定义最大重试次数

**使用示例**：

```python
from dingtalk_downloader.config.constants import MAX_RETRY_COUNT

max_retries = MAX_RETRY_COUNT
print(f"最大重试次数: {max_retries}")
```

#### 默认请求头常量

```python
DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://n.dingtalk.com/",
    "Accept": "application/vnd.apple.mpegurl, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}
```

**说明**：定义默认的 HTTP 请求头

**使用示例**：

```python
from dingtalk_downloader.config.constants import DEFAULT_HEADERS

headers = DEFAULT_HEADERS
print(f"User-Agent: {headers['User-Agent']}")
print(f"Referer: {headers['Referer']}")
```

#### 默认下载目录常量

```python
DEFAULT_DOWNLOAD_DIR = "Downloads"
```

**说明**：定义默认下载目录

**使用示例**：

```python
from dingtalk_downloader.config.constants import DEFAULT_DOWNLOAD_DIR

download_dir = DEFAULT_DOWNLOAD_DIR
print(f"默认下载目录: {download_dir}")
```

#### 临时文件名常量

```python
TEMP_M3U8_FILE = "output.m3u8"
```

**说明**：定义临时 m3u8 文件名

**使用示例**：

```python
from dingtalk_downloader.config.constants import TEMP_M3U8_FILE

temp_file = TEMP_M3U8_FILE
print(f"临时文件名: {temp_file}")
```

#### 浏览器选项映射常量

```python
BROWSER_OPTION_MAP = {"1": BROWSER_TYPE_EDGE, "2": BROWSER_TYPE_CHROME, "3": BROWSER_TYPE_FIREFOX}
```

**说明**：定义浏览器选项映射

**使用示例**：

```python
from dingtalk_downloader.config.constants import BROWSER_OPTION_MAP

choice = "1"
browser_type = BROWSER_OPTION_MAP[choice]
print(f"浏览器类型: {browser_type}")
```

#### 下载模式映射常量

```python
DOWNLOAD_MODE_MAP = {"1": DOWNLOAD_MODE_SINGLE, "2": DOWNLOAD_MODE_BATCH}
```

**说明**：定义下载模式映射

**使用示例**：

```python
from dingtalk_downloader.config.constants import DOWNLOAD_MODE_MAP

choice = "1"
download_mode = DOWNLOAD_MODE_MAP[choice]
print(f"下载模式: {download_mode}")
```

#### 保存模式映射常量

```python
SAVE_MODE_MAP = {"1": SAVE_MODE_DEFAULT, "2": SAVE_MODE_MANUAL}
```

**说明**：定义保存模式映射

**使用示例**：

```python
from dingtalk_downloader.config.constants import SAVE_MODE_MAP

choice = "1"
save_mode = SAVE_MODE_MAP[choice]
print(f"保存模式: {save_mode}")
```

---

## 类文档

### Settings

配置类，负责管理配置项。该类提供配置项的加载、保存、获取和设置功能。

#### 初始化方法

```python
def __init__(self, config_file: Optional[str] = None)
```

**参数说明**：

- `config_file` (Optional[str]): 配置文件路径，默认为 None（使用默认路径）

**返回值**：无

**异常**：无

**使用示例**：

```python
from dingtalk_downloader.config.settings import Settings

# 使用默认路径
settings = Settings()

# 使用自定义路径
settings = Settings(config_file="C:/config/my_config.json")
```

**默认路径说明**：

- Windows: `C:/Users/<用户名>/.dingtalk_downloader/config.json`
- Linux/macOS: `/home/<用户名>/.dingtalk_downloader/config.json`

#### load

加载配置，从配置文件中加载配置项，如果配置文件不存在，则使用默认配置。

```python
def load(self) -> None
```

**参数说明**：无

**返回值**：无

**异常**：

- `json.JSONDecodeError`: 配置文件格式错误时
- `IOError`: 配置文件读取失败时

**使用示例**：

```python
from dingtalk_downloader.config.settings import Settings

settings = Settings()
settings.load()
print("配置已加载")
```

#### save

保存配置，将配置项保存到配置文件。

```python
def save(self) -> None
```

**参数说明**：无

**返回值**：无

**异常**：

- `IOError`: 配置文件保存失败时

**使用示例**：

```python
from dingtalk_downloader.config.settings import Settings

settings = Settings()
settings.set("browser_type", "edge")
settings.save()
print("配置已保存")
```

#### get

获取配置项，获取指定键的配置值，如果不存在则返回默认值。

```python
def get(self, key: str, default: Any = None) -> Any
```

**参数说明**：

- `key` (str): 配置项键
- `default` (Any): 默认值

**返回值**：

- `value` (Any): 配置项值，如果不存在则返回默认值

**异常**：无

**使用示例**：

```python
from dingtalk_downloader.config.settings import Settings

settings = Settings()

# 获取配置项
browser_type = settings.get("browser_type", "edge")
print(f"浏览器类型: {browser_type}")

# 获取不存在的配置项
unknown = settings.get("unknown_key", "default_value")
print(f"未知配置项: {unknown}")
```

#### set

设置配置项，设置指定键的配置值，并自动保存到配置文件。

```python
def set(self, key: str, value: Any) -> None
```

**参数说明**：

- `key` (str): 配置项键
- `value` (Any): 配置项值

**返回值**：无

**异常**：无

**使用示例**：

```python
from dingtalk_downloader.config.settings import Settings

settings = Settings()

# 设置配置项
settings.set("browser_type", "edge")
settings.set("download_mode", "single")
settings.set("save_mode", "default")

print("配置已设置并保存")
```

## 使用流程

### 使用常量

```python
from dingtalk_downloader.config.constants import (
    BROWSER_TYPE_EDGE,
    BROWSER_TYPE_CHROME,
    BROWSER_TYPE_FIREFOX,
    DOWNLOAD_MODE_SINGLE,
    DOWNLOAD_MODE_BATCH,
    SAVE_MODE_DEFAULT,
    SAVE_MODE_MANUAL,
    MAX_RETRY_COUNT,
    DEFAULT_HEADERS,
    DEFAULT_DOWNLOAD_DIR,
    TEMP_M3U8_FILE,
    BROWSER_OPTION_MAP,
    DOWNLOAD_MODE_MAP,
    SAVE_MODE_MAP
)

# 使用浏览器类型
browser_type = BROWSER_TYPE_EDGE
print(f"浏览器类型: {browser_type}")

# 使用下载模式
download_mode = DOWNLOAD_MODE_SINGLE
print(f"下载模式: {download_mode}")

# 使用保存模式
save_mode = SAVE_MODE_DEFAULT
print(f"保存模式: {save_mode}")

# 使用最大重试次数
max_retries = MAX_RETRY_COUNT
print(f"最大重试次数: {max_retries}")

# 使用默认请求头
headers = DEFAULT_HEADERS
print(f"User-Agent: {headers['User-Agent']}")

# 使用默认下载目录
download_dir = DEFAULT_DOWNLOAD_DIR
print(f"默认下载目录: {download_dir}")

# 使用临时文件名
temp_file = TEMP_M3U8_FILE
print(f"临时文件名: {temp_file}")

# 使用映射
choice = "1"
browser_type = BROWSER_OPTION_MAP[choice]
print(f"浏览器类型: {browser_type}")
```

### 使用配置管理

```python
from dingtalk_downloader.config.settings import Settings

# 创建配置实例（使用默认路径）
settings = Settings()

# 加载配置
settings.load()

# 获取配置项
browser_type = settings.get("browser_type", "edge")
download_mode = settings.get("download_mode", "single")
save_mode = settings.get("save_mode", "default")

print(f"浏览器类型: {browser_type}")
print(f"下载模式: {download_mode}")
print(f"保存模式: {save_mode}")

# 设置配置项
settings.set("browser_type", "chrome")
settings.set("download_mode", "batch")
settings.set("save_mode", "manual")

# 保存配置
settings.save()

print("配置已保存")
```

### 使用自定义配置文件

```python
from dingtalk_downloader.config.settings import Settings

# 创建配置实例（使用自定义路径）
settings = Settings(config_file="C:/config/my_config.json")

# 加载配置
settings.load()

# 获取配置项
custom_setting = settings.get("custom_key", "default_value")
print(f"自定义配置: {custom_setting}")

# 设置配置项
settings.set("custom_key", "custom_value")

# 保存配置
settings.save()

print("自定义配置已保存")
```

### 使用映射常量

```python
from dingtalk_downloader.config.constants import BROWSER_OPTION_MAP, DOWNLOAD_MODE_MAP, SAVE_MODE_MAP

# 用户输入
browser_choice = input("请选择浏览器 (1-Edge, 2-Chrome, 3-Firefox): ")
download_choice = input("请选择下载模式 (1-单个, 2-批量): ")
save_choice = input("请选择保存模式 (1-默认路径, 2-手动选择): ")

# 使用映射获取实际值
browser_type = BROWSER_OPTION_MAP.get(browser_choice, "edge")
download_mode = DOWNLOAD_MODE_MAP.get(download_choice, "single")
save_mode = SAVE_MODE_MAP.get(save_choice, "default")

print(f"浏览器类型: {browser_type}")
print(f"下载模式: {download_mode}")
print(f"保存模式: {save_mode}")
```

## 异常处理

### 常见异常

1. **配置文件格式错误**

   - 原因：配置文件不是有效的 JSON 格式
   - 解决：检查配置文件格式，确保是有效的 JSON

2. **配置文件读取失败**

   - 原因：配置文件路径不存在或无读取权限
   - 解决：检查配置文件路径和权限

3. **配置文件保存失败**

   - 原因：配置文件路径不存在或无写入权限
   - 解决：检查配置文件路径和权限

4. **映射键不存在**
   - 原因：映射中不存在指定的键
   - 解决：使用 `get()` 方法并提供默认值

### 异常处理示例

```python
from dingtalk_downloader.config.settings import Settings

settings = Settings()

try:
    # 加载配置
    settings.load()

    # 获取配置项
    browser_type = settings.get("browser_type", "edge")
    print(f"浏览器类型: {browser_type}")

    # 设置配置项
    settings.set("browser_type", "chrome")

    # 保存配置
    settings.save()

except Exception as e:
    if "JSONDecodeError" in str(type(e)):
        print("配置文件格式错误，请检查 JSON 格式")
    elif "IOError" in str(type(e)):
        print("配置文件读写失败，请检查路径和权限")
    else:
        print(f"发生错误: {e}")
```

## 注意事项

1. **配置文件路径**：默认配置文件路径为 `~/.dingtalk_downloader/config.json`
2. **配置文件格式**：配置文件使用 JSON 格式，确保格式正确
3. **配置自动保存**：调用 `set()` 方法会自动保存配置到文件
4. **默认值**：使用 `get()` 方法时，建议提供默认值以避免 KeyError
5. **映射使用**：使用映射常量时，建议使用 `get()` 方法并提供默认值
6. **常量不可修改**：constants 模块中的常量不应被修改
7. **配置文件权限**：确保配置文件目录有读写权限
8. **跨平台支持**：配置文件路径会根据操作系统自动调整
