# 工具模块

## 模块概述

本模块提供项目所需的通用工具函数和数据模型，包括文件读取、路径处理、输入验证、路径选择、m3u8文件管理等功能，为其他模块提供基础支持。采用函数式编程和面向对象编程相结合的方式，提供高内聚、低耦合的工具组件。

## 模块架构

### 架构设计原则

- **单一职责原则**：每个函数/类只负责一个明确的功能
- **开闭原则**：对扩展开放，对修改关闭
- **依赖倒置原则**：依赖抽象而非具体实现
- **值对象模式**：使用不可变数据类封装复杂数据
- **函数式编程**：纯函数，无副作用

### 模块结构

```tree
utils/
├── file_reader.py          # 文件读取工具类
├── path_helper.py          # 路径处理工具函数
├── path_selector.py        # 路径选择器
├── validator.py            # 输入验证工具函数
├── m3u8_file_manager.py    # m3u8文件管理器
├── models.py               # 数据模型
└── __init__.py
```

## 功能描述

### FileReader - 文件读取工具类

**职责**：从 CSV/Excel 文件中读取钉钉直播链接

**功能**：

- 从 CSV 文件中读取链接
- 从 Excel 文件中读取链接
- 自动处理不同编码（UTF-8、GBK、GB18030）
- 提取以 "https://n.dingtalk.com" 开头的链接
- 文件路径验证（扩展名、存在性、可读性、大小）
- 支持多工作表读取

**核心算法**：

- 多编码尝试策略
- DataFrame 遍历提取链接
- 文件验证链

**设计模式**：策略模式（编码选择）

### PathHelper - 路径处理工具函数

**职责**：提供路径处理通用函数

**功能**：

- 清理文件路径（去除引号和空格）
- 拼接多个路径片段
- 确保目录存在
- 跨平台路径处理

**设计模式**：工具函数模式（Utility Functions）

### PathSelector - 路径选择器

**职责**：根据保存模式选择下载路径

**功能**：

- 支持默认路径模式（从配置文件读取）
- 支持手动选择路径模式（使用文件对话框）
- 路径验证和创建
- 路径缓存

**设计模式**：策略模式（Strategy Pattern）

### Validator - 输入验证工具函数

**职责**：验证用户输入

**功能**：

- 验证用户输入（支持默认选项）
- 验证必填输入
- 验证钉钉直播链接格式
- 验证文件路径
- 捕获 EOFError 和 KeyboardInterrupt
- 支持自定义验证函数

**核心算法**：

- URL 解析和验证
- 文件路径验证链
- 输入循环验证

**设计模式**：验证器模式（Validator Pattern）

### M3u8FileManager - m3u8 文件管理器

**职责**：管理 m3u8 临时文件

**功能**：

- 生成临时文件路径
- 清理临时文件
- 文件路径验证

**设计模式**：管理器模式（Manager Pattern）

### Models - 数据模型

**职责**：定义值对象和数据类

**功能**：

- CookieData：Cookie 数据值对象
- HeadersData：请求头数据值对象
- M3u8Link：m3u8 链接值对象
- VideoDownloadContext：视频下载上下文数据类

**设计模式**：值对象模式（Value Object Pattern）、数据传输对象（DTO）

## 核心实现原理

### FileReader 实现原理

#### 文件验证链

```python
def _validate_file_path(self) -> None:
    self._check_file_extension()      # 1. 检查扩展名
    self._check_file_exists()          # 2. 检查文件存在
    self._check_is_file()              # 3. 检查是否为文件
    self._check_file_readable()        # 4. 检查可读性
    self._check_file_size()            # 5. 检查文件大小
```

#### CSV 文件读取（多编码策略）

```python
def _read_csv(self, links: Dict[int, str]) -> None:
    encodings = ["utf-8", "gbk", "gb18030"]
    last_error = None

    for encoding in encodings:
        try:
            df = pd.read_csv(self.file_path, encoding=encoding)
            self._extract_links_from_dataframe(df, links)
            return
        except UnicodeDecodeError as e:
            last_error = e
            continue

    raise FileReaderError(f"文件编码无法识别: {last_error}")
```

#### Excel 文件读取（多工作表）

```python
def _read_excel(self, links: Dict[int, str]) -> None:
    xls = pd.ExcelFile(self.file_path)
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        self._extract_links_from_dataframe(df, links)
```

#### 链接提取算法

```python
def _extract_links_from_dataframe(
    self, df: pd.DataFrame, links: Dict[int, str]
) -> None:
    for col in df.columns:
        for i, value in df[col].dropna().items():
            if (
                isinstance(value, str)
                and value.startswith("https://n.dingtalk.com")
            ):
                links[i] = value
```

### PathHelper 实现原理

#### 路径清理

```python
def clean_file_path(file_path: str) -> str:
    return file_path.strip().replace('"', "").replace("'", "")
```

#### 路径拼接

```python
def join_paths(*paths: str) -> str:
    return os.path.join(*paths)
```

#### 目录创建

```python
def ensure_dir_exists(dir_path: str) -> None:
    os.makedirs(dir_path, exist_ok=True)
```

### PathSelector 实现原理

#### 默认路径选择

```python
def _get_default_download_dir(self) -> str:
    config = YamlConfig.get_instance()
    default_dir = config.get_str("download.default_dir", "Downloads")

    if os.path.isabs(default_dir):
        downloads_dir = default_dir
    else:
        base_dir = os.getcwd()
        downloads_dir = os.path.join(base_dir, default_dir)

    ensure_dir_exists(downloads_dir)
    return downloads_dir
```

#### 手动路径选择

```python
def _get_manual_download_dir(self) -> Optional[str]:
    root = tk.Tk()
    root.withdraw()
    save_dir = filedialog.askdirectory(title="选择保存视频的目录")
    root.destroy()
    return save_dir
```

### Validator 实现原理

#### URL 验证算法

```python
def validate_dingtalk_url(url: str) -> str:
    parsed = urlparse(url)

    # 1. 验证协议
    if parsed.scheme not in ["http", "https"]:
        raise ValueError("仅支持 http 和 https 协议")

    # 2. 验证域名
    if parsed.netloc != "n.dingtalk.com":
        raise ValueError("仅支持钉钉直播链接 (n.dingtalk.com)")

    # 3. 验证 liveUuid 参数
    _validate_live_uuid(parsed)

    return url
```

#### liveUuid 验证

```python
def _validate_live_uuid(parsed) -> None:
    query_params = parse_qs(parsed.query)
    live_uuid = query_params.get("liveUuid", [None])[0]

    if not live_uuid:
        raise ValueError("liveUuid 参数为空")

    if not re.match(r"^[a-f0-9\-]{36}$", live_uuid):
        raise ValueError("liveUuid 格式无效")
```

#### 输入验证循环

```python
def validate_input(
    prompt: str,
    valid_options: List[str],
    default_option: Optional[str] = None,
) -> str:
    while True:
        try:
            choice = input(prompt)

            # 空输入处理
            if choice == "" and default_option is not None:
                return default_option

            # 选项验证
            if choice in valid_options:
                return choice

            print("无效的选择，请重新输入。")

        except EOFError:
            if default_option is not None:
                return default_option
            raise
        except KeyboardInterrupt:
            print("\n用户中断输入")
            raise
```

### M3u8FileManager 实现原理

#### 临时文件路径生成

```python
def get_temp_file_path(self) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"m3u8_{timestamp}.m3u8"
    file_path = os.path.join(self.temp_dir, filename)
    return file_path
```

### Models 实现原理

#### 值对象模式

```python
@dataclass(frozen=True)
class CookieData:
    """Cookie数据值对象"""

    cookies: Dict[str, str]

    def __post_init__(self):
        """验证Cookie数据"""
        if not isinstance(self.cookies, dict):
            raise ValueError("cookies必须是字典类型")

        for key, value in self.cookies.items():
            if not isinstance(key, str):
                raise ValueError("Cookie键必须是字符串类型")
            if not isinstance(value, str):
                raise ValueError("Cookie值必须是字符串类型")
```

#### 数据传输对象

```python
@dataclass
class VideoDownloadContext:
    """视频下载上下文数据类"""

    url: str
    cookie_data: CookieData
    headers_data: HeadersData
    live_name: str
    save_dir: Optional[str] = None
    save_mode: str = "1"

    def get_cookies_dict(self) -> Dict[str, str]:
        """获取Cookie字典"""
        return self.cookie_data.to_dict()

    def get_headers_dict(self) -> Dict[str, str]:
        """获取请求头字典"""
        return self.headers_data.to_dict()
```

## 使用方法

### FileReader 使用示例

```python
from dingtalk_downloader.utils.file_reader import FileReader

# 创建文件读取器
file_reader = FileReader("links.csv")

# 读取链接
links = file_reader.read_links()

# 输出链接
for index, url in links.items():
    print(f"{index}: {url}")

# 读取 Excel 文件
file_reader = FileReader("links.xlsx")
links = file_reader.read_links()
```

### PathHelper 使用示例

```python
from dingtalk_downloader.utils.path_helper import (
    clean_file_path,
    join_paths,
    ensure_dir_exists,
)

# 清理文件路径
clean_path = clean_file_path('"C:\\Users\\Test\\file.csv"')
print(clean_path)  # 输出: C:\Users\Test\file.csv

# 拼接路径
full_path = join_paths("C:", "Users", "Test", "file.csv")
print(full_path)  # 输出: C:\Users\Test\file.csv

# 确保目录存在
ensure_dir_exists("C:\\Users\\Test\\Downloads")
```

### PathSelector 使用示例

```python
from dingtalk_downloader.utils.path_selector import PathSelector
from dingtalk_downloader.config.constants import SAVE_MODE_DEFAULT

# 创建路径选择器（默认模式）
path_selector = PathSelector(SAVE_MODE_DEFAULT)

# 获取保存目录
save_dir = path_selector.get_save_dir()
print(f"保存目录: {save_dir}")

# 获取已保存的路径
saved_path = path_selector.get_saved_path()
print(f"已保存路径: {saved_path}")
```

### Validator 使用示例

```python
from dingtalk_downloader.utils.validator import (
    validate_input,
    validate_required_input,
    validate_dingtalk_url,
    validate_file_path,
)

# 验证输入（带默认选项）
choice = validate_input(
    "请选择下载模式（1：单个，2：批量，直接回车默认选择1）: ",
    ["1", "2"],
    default_option="1"
)
print(f"您选择了: {choice}")

# 验证必填输入
url = validate_required_input(
    "请输入钉钉直播链接: ",
    validation_func=validate_dingtalk_url,
    error_message="链接格式不正确",
    input_name="钉钉直播链接"
)
print(f"链接: {url}")

# 验证文件路径
file_path = validate_required_input(
    "请输入文件路径: ",
    validation_func=validate_file_path,
    error_message="文件路径不正确",
    input_name="文件路径"
)
print(f"文件路径: {file_path}")
```

### Models 使用示例

```python
from dingtalk_downloader.utils.models import (
    CookieData,
    HeadersData,
    M3u8Link,
    VideoDownloadContext,
)

# 创建 Cookie 数据
cookie_data = CookieData({"session": "abc123", "token": "xyz789"})
print(f"Cookie 数量: {len(cookie_data)}")
print(f"Session: {cookie_data.get('session')}")

# 创建请求头数据
headers_data = HeadersData({
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://n.dingtalk.com"
})
print(f"请求头数量: {len(headers_data)}")

# 创建 m3u8 链接
m3u8_link = M3u8Link(
    url="https://example.com/live/video.m3u8",
    prefix="https://example.com/live/",
    local_file_path="/path/to/local/video.m3u8"
)
print(f"m3u8 链接: {m3u8_link}")

# 创建视频下载上下文
context = VideoDownloadContext(
    url="https://n.dingtalk.com/xxx",
    cookie_data=cookie_data,
    headers_data=headers_data,
    live_name="直播视频",
    save_mode="1"
)
print(f"直播名称: {context.live_name}")
print(f"Cookie 字典: {context.get_cookies_dict()}")
```

## 接口参数说明

### FileReader 类

#### **init**(file_path: str)

**参数**：

- `file_path`：文件路径（CSV/Excel）

**功能**：初始化文件读取器

**异常**：

- `FileNotFoundError`：文件不存在时
- `PermissionError`：文件不可读时
- `ValueError`：文件格式不支持或文件过大时
- `FileReaderError`：其他错误时

#### read_links() -> Dict[int, str]

**参数**：无

**返回值**：

- `Dict[int, str]`：链接字典 {index: url}

**功能**：从文件中读取钉钉直播链接

**异常**：

- `FileReaderError`：读取失败时

### PathHelper 函数

#### clean_file_path(file_path: str) -> str

**参数**：

- `file_path`：文件路径

**返回值**：

- `str`：清理后的文件路径

**功能**：清理文件路径（去除引号和空格）

#### join_paths(\*paths: str) -> str

**参数**：

- `*paths`：路径片段

**返回值**：

- `str`：拼接后的路径

**功能**：拼接多个路径片段

#### ensure_dir_exists(dir_path: str) -> None

**参数**：

- `dir_path`：目录路径

**返回值**：无

**功能**：确保目录存在（不存在则创建）

### PathSelector 类

#### **init**(save_mode: str)

**参数**：

- `save_mode`：保存模式（1：默认路径，2：手动选择）

**功能**：初始化路径选择器

#### get_save_dir() -> Optional[str]

**参数**：无

**返回值**：

- `Optional[str]`：保存目录路径，如果用户取消则返回 None

**功能**：获取保存目录

#### get_saved_path() -> Optional[str]

**参数**：无

**返回值**：

- `Optional[str]`：已保存的路径，如果未保存则返回 None

**功能**：获取已保存的路径

### Validator 函数

#### validate_input(prompt: str, valid_options: List[str], default_option: Optional[str] = None) -> str

**参数**：

- `prompt`：提示信息
- `valid_options`：有效选项列表
- `default_option`：默认选项

**返回值**：

- `str`：用户选择的选项

**异常**：

- `ValueError`：输入无效时
- `EOFError`：输入流结束时
- `KeyboardInterrupt`：用户中断时

**功能**：验证用户输入

#### validate_required_input(prompt: str, validation_func: Optional[Callable[[str], bool]] = None, error_message: Optional[str] = None, input_name: str = "输入") -> str

**参数**：

- `prompt`：提示信息
- `validation_func`：自定义验证函数
- `error_message`：验证失败时的错误消息
- `input_name`：输入项的名称

**返回值**：

- `str`：用户输入的有效值

**异常**：

- `ValueError`：输入无效时
- `EOFError`：输入流结束时
- `KeyboardInterrupt`：用户中断时

**功能**：验证必填的用户输入

#### validate_dingtalk_url(url: str) -> str

**参数**：

- `url`：钉钉直播回放分享链接

**返回值**：

- `str`：验证通过的 URL

**异常**：

- `ValueError`：URL 无效时

**功能**：验证钉钉直播链接

#### validate_file_path(file_path: str) -> str

**参数**：

- `file_path`：文件路径

**返回值**：

- `str`：验证通过的文件路径

**异常**：

- `FileNotFoundError`：文件不存在时
- `PermissionError`：文件不可读时
- `ValueError`：文件格式不支持或文件过大时

**功能**：验证文件路径

### Models 类

#### CookieData

**属性**：

- `cookies`：Cookie 字典

**方法**：

- `to_dict()` -> Dict[str, str]：转换为字典
- `get(name: str, default: Optional[str] = None) -> Optional[str]`：获取指定 Cookie 值
- `__len__()` -> int：返回 Cookie 数量
- `__contains__(key: str) -> bool`：检查是否包含指定的 Cookie

#### HeadersData

**属性**：

- `headers`：请求头字典

**方法**：

- `to_dict()` -> Dict[str, str]：转换为字典
- `get(name: str, default: Optional[str] = None) -> Optional[str]`：获取指定请求头值
- `__len__()` -> int：返回请求头数量
- `__contains__(key: str) -> bool`：检查是否包含指定的请求头

#### M3u8Link

**属性**：

- `url`：m3u8 文件 URL
- `prefix`：基础 URL
- `local_file_path`：本地 m3u8 文件路径

#### VideoDownloadContext

**属性**：

- `url`：钉钉直播回放分享链接
- `cookie_data`：Cookie 数据
- `headers_data`：请求头数据
- `live_name`：直播视频名称
- `save_dir`：保存目录
- `save_mode`：保存模式

**方法**：

- `get_cookies_dict()` -> Dict[str, str]：获取 Cookie 字典
- `get_headers_dict()` -> Dict[str, str]：获取请求头字典
- `is_save_dir_set()` -> bool：检查保存目录是否已设置

## 依赖关系

### 依赖的外部库

1. **pandas**
   - 数据处理库
   - 用于读取 CSV 和 Excel 文件

2. **openpyxl**
   - Excel 文件处理库
   - 用于读取 .xlsx 文件

3. **xlrd**
   - Excel 文件处理库
   - 用于读取 .xls 文件

### 依赖的 Python 模块

1. `os` - 操作系统接口
2. `pathlib` - 路径处理
3. `sys` - 系统相关
4. `logging` - 日志记录
5. `typing` - 类型提示
6. `re` - 正则表达式
7. `urllib.parse` - URL 解析
8. `dataclasses` - 数据类
9. `tkinter` - GUI 界面（用于文件对话框）

### 依赖的内部模块

1. `config.yaml_config` - YAML 配置管理
2. `config.constants` - 常量定义
3. `core.exceptions` - 异常定义

### 被依赖的模块

1. `main` - 主程序入口
2. `core.downloader` - 下载器核心模块
3. `core.video_download_manager` - 视频下载管理器
4. `core.m3u8_download_service` - m3u8 下载服务

## 数据流程

### 文件读取流程

```text
创建文件读取器
  ↓
验证文件路径（扩展名、存在性、可读性、大小）
  ↓
判断文件类型（CSV/Excel）
  ↓
读取文件内容
  ↓
遍历所有单元格
  ↓
提取以 "https://n.dingtalk.com" 开头的链接
  ↓
返回链接字典
```

### 路径处理流程

```text
输入路径
  ↓
清理路径（去除引号和空格）
  ↓
拼接路径片段
  ↓
确保目录存在
  ↓
返回处理后的路径
```

### 输入验证流程

```text
显示提示信息
  ↓
获取用户输入
  ↓
检查是否为空（使用默认选项）
  ↓
检查是否在有效选项列表中
  ↓
返回有效选项或提示重新输入
```

### URL 验证流程

```text
解析 URL
  ↓
验证协议（http/https）
  ↓
验证域名（n.dingtalk.com）
  ↓
验证路径
  ↓
验证 liveUuid 参数
  ↓
验证 liveUuid 格式
  ↓
返回验证通过的 URL
```

## 设计模式应用

### 1. 策略模式（Strategy Pattern）

**应用类**：FileReader（编码选择）、PathSelector（路径选择）

**说明**：根据不同情况采用不同的策略（编码、路径选择）。

### 2. 值对象模式（Value Object Pattern）

**应用类**：CookieData、HeadersData、M3u8Link

**说明**：封装数据，提供类型安全和不可变性。

### 3. 数据传输对象（DTO）

**应用类**：VideoDownloadContext

**说明**：封装视频下载所需的所有上下文信息，在模块间传递。

### 4. 验证器模式（Validator Pattern）

**应用类**：Validator 模块

**说明**：提供统一的验证接口和验证逻辑。

### 5. 工具函数模式（Utility Functions）

**应用类**：PathHelper

**说明**：提供纯函数，无副作用，易于测试和复用。

### 6. 管理器模式（Manager Pattern）

**应用类**：M3u8FileManager

**说明**：管理 m3u8 文件的生命周期。

## 异常处理

### 异常层次结构

```text
Exception
  └── FileReaderError (文件读取异常)
```

### 异常处理策略

1. **文件验证**：在读取前验证文件路径、扩展名、大小等
2. **编码处理**：多编码尝试，捕获 UnicodeDecodeError
3. **输入验证**：验证用户输入，提供友好的错误提示
4. **URL 验证**：验证 URL 格式、协议、域名、参数等
5. **异常转换**：将底层异常转换为业务异常

## 注意事项

### 1. 文件编码

- CSV 文件支持 UTF-8、GBK、GB18030 编码
- 如果编码无法识别，程序会抛出 FileReaderError
- 建议使用 UTF-8 编码保存 CSV 文件

### 2. 文件格式

- 只支持 CSV 和 Excel 文件
- Excel 文件支持 .xlsx 和 .xls 格式
- 文件大小限制为 100MB

### 3. 链接提取

- 只提取以 `https://n.dingtalk.com` 开头的链接
- 遍历所有工作表和单元格
- 忽略空值和非字符串值

### 4. 输入验证

- 支持默认选项（直接按 Enter）
- 捕获 EOFError 和 KeyboardInterrupt
- 提供友好的错误提示

### 5. 路径处理

- 自动去除路径中的引号和空格
- 使用 `os.makedirs()` 创建目录（`exist_ok=True`）
- 支持跨平台路径处理

### 6. 值对象

- 使用 `@dataclass(frozen=True)` 确保不可变性
- 在 `__post_init__` 中进行数据验证
- 提供便捷的访问方法

## 性能优化

### 1. 文件读取优化

- 使用 pandas 高效读取 CSV/Excel 文件
- 遍历 DataFrame 时使用 `dropna()` 跳过空值
- 提前验证文件，避免无效读取

### 2. 路径处理优化

- 使用 `os.path.join` 确保跨平台兼容性
- 使用 `os.makedirs(exist_ok=True)` 避免重复检查

### 3. 输入验证优化

- 使用正则表达式快速验证 URL 格式
- 提前验证文件路径，避免无效操作

## 扩展方向

### 1. 支持更多文件格式

- 添加对 JSON、TXT 等格式的支持
- 支持从数据库读取链接

### 2. 链接验证

- 添加链接有效性验证
- 检查链接是否可访问
- 验证链接是否过期

### 3. 编码检测

- 自动检测文件编码
- 支持更多编码格式
- 使用 chardet 库进行编码检测

### 4. 路径规范化

- 添加路径规范化功能
- 处理相对路径和绝对路径转换
- 支持路径别名和环境变量

### 5. 输入增强

- 添加输入超时功能
- 添加输入掩码功能
- 支持多行输入

### 6. 数据模型扩展

- 添加更多值对象
- 支持数据序列化和反序列化
- 添加数据验证规则

## 测试建议

### 1. 单元测试

- 测试各个函数的独立功能
- 测试文件读取的各种情况
- 测试输入验证的各种情况

### 2. 集成测试

- 测试文件读取和链接提取
- 测试路径选择和验证
- 测试输入验证和用户交互

### 3. 异常测试

- 测试各种异常情况
- 验证异常处理逻辑
- 测试边界条件

### 4. 性能测试

- 测试大文件读取性能
- 测试大量链接提取性能
- 测试输入验证性能

## 维护责任人

- **主要维护者**：项目团队
- **最后更新日期**：2026-01-27

## 相关文档

- [主程序入口模块](../README.md)
- [核心业务模块](../core/README.md)
- [配置模块](../config/README.md)
- [浏览器驱动模块](../browser/README.md)
