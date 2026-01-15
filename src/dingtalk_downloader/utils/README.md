# 工具模块

## 模块概述

本模块提供项目所需的通用工具函数，包括文件读取、路径处理和输入验证等功能，为其他模块提供基础支持。

## 功能描述

### FileReader - 文件读取工具类

**功能**：

- 从 CSV 文件中读取链接
- 从 Excel 文件中读取链接
- 自动处理不同编码（UTF-8、GBK）
- 提取以 "https://n.dingtalk.com" 开头的链接

### PathHelper - 路径处理工具函数

**功能**：

- 清理文件路径（去除引号和空格）
- 拼接多个路径片段
- 确保目录存在
- 获取文件扩展名

### Validator - 输入验证工具函数

**功能**：

- 验证用户输入
- 支持默认选项
- 捕获 EOFError 和 KeyboardInterrupt

## 核心实现原理

### FileReader 实现原理

#### CSV 文件读取

```python
def _read_csv(self, links: Dict[int, str]) -> None:
    try:
        df = pd.read_csv(self.file_path, encoding="utf-8")
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(self.file_path, encoding="gbk")
        except UnicodeDecodeError:
            logger.warning(f"文件 {self.file_path} 使用的编码无法识别")
            sys.exit(1)

    self._extract_links_from_dataframe(df, links)
```

#### Excel 文件读取

```python
def _read_excel(self, links: Dict[int, str]) -> None:
    xls = pd.ExcelFile(self.file_path)
    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)
        self._extract_links_from_dataframe(df, links)
```

#### 链接提取

```python
def _extract_links_from_dataframe(self, df: pd.DataFrame, links: Dict[int, str]) -> None:
    for col in df.columns:
        for i, value in df[col].dropna().items():
            if isinstance(value, str) and value.startswith("https://n.dingtalk.com"):
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

#### 扩展名获取

```python
def get_file_extension(file_path: str) -> str:
    return Path(file_path).suffix
```

### Validator 实现原理

#### 输入验证

```python
def validate_input(
    prompt: str, valid_options: List[str], default_option: Optional[str] = None
) -> str:
    while True:
        try:
            choice = input(prompt)
            if choice == "" and default_option is not None:
                return default_option
            if choice in valid_options:
                return choice
            print("无效的选择，请重新输入。")
        except EOFError:
            if default_option is not None:
                print(f"\n输入流结束，使用默认选项: {default_option}")
                return default_option
            raise
        except KeyboardInterrupt:
            print("\n用户中断输入")
            raise
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
    get_file_extension
)

# 清理文件路径
clean_path = clean_file_path('"C:\\Users\\Test\\file.csv"')
print(clean_path)  # 输出: C:\Users\Test\file.csv

# 拼接路径
full_path = join_paths("C:", "Users", "Test", "file.csv")
print(full_path)  # 输出: C:\Users\Test\file.csv

# 确保目录存在
ensure_dir_exists("C:\\Users\\Test\\Downloads")

# 获取文件扩展名
extension = get_file_extension("file.csv")
print(extension)  # 输出: .csv
```

### Validator 使用示例

```python
from dingtalk_downloader.utils.validator import validate_input

# 验证输入（带默认选项）
choice = validate_input(
    "请选择下载模式（1：单个，2：批量，直接回车默认选择1）: ",
    ["1", "2"],
    default_option="1"
)
print(f"您选择了: {choice}")

# 验证输入（无默认选项）
choice = validate_input(
    "请选择浏览器（1：Edge，2：Chrome，3：Firefox）: ",
    ["1", "2", "3"]
)
print(f"您选择了: {choice}")
```

## 接口参数说明

### FileReader 类

#### **init**(file_path: str)

**参数**：

- `file_path`：文件路径（CSV/Excel）

**异常**：

- `FileNotFoundError`：文件不存在时
- `ValueError`：文件格式不支持时

**功能**：初始化文件读取器

#### read_links() -> Dict[int, str]

**参数**：无

**返回值**：

- `Dict[int, str]`：链接字典 {index: url}

**异常**：

- `Exception`：读取失败时

**功能**：从文件中读取钉钉直播链接

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

#### get_file_extension(file_path: str) -> str

**参数**：

- `file_path`：文件路径

**返回值**：

- `str`：文件扩展名（包含点号）

**功能**：获取文件扩展名

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

### 被依赖的模块

1. `main` - 主程序入口
2. `core.downloader` - 下载器核心模块

## 数据流程

### 文件读取流程

```
创建文件读取器
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

```
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

```
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

## 注意事项

1. **文件编码**

   - CSV 文件支持 UTF-8 和 GBK 编码
   - 如果编码无法识别，程序会退出

2. **文件格式**

   - 只支持 CSV 和 Excel 文件
   - Excel 文件支持 .xlsx 和 .xls 格式

3. **链接提取**

   - 只提取以 "https://n.dingtalk.com" 开头的链接
   - 遍历所有工作表和单元格

4. **输入验证**

   - 支持默认选项（直接按 Enter）
   - 捕获 EOFError 和 KeyboardInterrupt

5. **路径处理**
   - 自动去除路径中的引号和空格
   - 使用 `os.makedirs()` 创建目录（`exist_ok=True`）

## 扩展方向

1. **支持更多文件格式**

   - 添加对 JSON、TXT 等格式的支持

2. **链接验证**

   - 添加链接有效性验证
   - 检查链接是否可访问

3. **编码检测**

   - 自动检测文件编码
   - 支持更多编码格式

4. **路径规范化**

   - 添加路径规范化功能
   - 处理相对路径和绝对路径转换

5. **输入增强**
   - 添加输入超时功能
   - 添加输入掩码功能

## 维护责任人

- **主要维护者**：项目团队
- **最后更新日期**：2025-01-15

## 相关文档

- [主程序入口模块](../README.md)
- [核心业务模块](../core/README.md)
