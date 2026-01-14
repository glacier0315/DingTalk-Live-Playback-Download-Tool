# Utils 模块 API 文档

## 模块概述

Utils 模块是 DingTalk 直播回放下载工具的工具模块，提供文件读取、路径处理、输入验证等通用功能。该模块包含以下核心组件：

- **FileReader**: 文件读取类，负责从 CSV/Excel 文件中读取链接
- **path_helper**: 路径处理工具函数模块
- **validator**: 输入验证工具函数模块

## 类和函数文档

### FileReader

文件读取类，负责从 CSV/Excel 文件中读取链接。该类支持 CSV 和 Excel 文件，自动处理不同编码。

#### 初始化方法

```python
def __init__(self, file_path: str)
```

**参数说明**：
- `file_path` (str): 文件路径（CSV/Excel）

**返回值**：无

**异常**：
- `FileNotFoundError`: 文件不存在时
- `ValueError`: 文件格式不支持时

**使用示例**：
```python
from dingtalk_downloader.utils.file_reader import FileReader

file_reader = FileReader("links.csv")
```

#### read_links

从文件中读取钉钉直播链接。遍历文件中的所有单元格，提取以 "https://n.dingtalk.com" 开头的链接。

```python
def read_links(self) -> Dict[int, str]
```

**参数说明**：无

**返回值**：
- `links` (Dict[int, str]): 链接字典，格式为 `{index: url}`

**异常**：
- `Exception`: 读取失败时

**使用示例**：
```python
from dingtalk_downloader.utils.file_reader import FileReader

file_reader = FileReader("links.csv")
links = file_reader.read_links()
print(f"找到 {len(links)} 个链接")
for index, url in links.items():
    print(f"{index}: {url}")
```

---

### path_helper 模块

路径处理工具函数模块，提供路径清理、拼接、目录创建等功能。

#### clean_file_path

清理文件路径，去除路径中的多余引号和空格。

```python
def clean_file_path(file_path: str) -> str
```

**参数说明**：
- `file_path` (str): 文件路径

**返回值**：
- `cleaned_path` (str): 清理后的文件路径

**异常**：无

**使用示例**：
```python
from dingtalk_downloader.utils.path_helper import clean_file_path

path = '  "C:/Users/test/file.txt"  '
cleaned_path = clean_file_path(path)
print(cleaned_path)  # 输出: C:/Users/test/file.txt
```

#### join_paths

拼接路径，使用 os.path.join 拼接多个路径片段。

```python
def join_paths(*paths: str) -> str
```

**参数说明**：
- `*paths` (str): 路径片段

**返回值**：
- `joined_path` (str): 拼接后的路径

**异常**：无

**使用示例**：
```python
from dingtalk_downloader.utils.path_helper import join_paths

path = join_paths("C:/Users", "test", "file.txt")
print(path)  # 输出: C:/Users/test/file.txt
```

#### ensure_dir_exists

确保目录存在，如果目录不存在，则创建目录。

```python
def ensure_dir_exists(dir_path: str) -> None
```

**参数说明**：
- `dir_path` (str): 目录路径

**返回值**：无

**异常**：无

**使用示例**：
```python
from dingtalk_downloader.utils.path_helper import ensure_dir_exists

ensure_dir_exists("C:/Users/test/new_dir")
```

#### get_file_extension

获取文件扩展名。

```python
def get_file_extension(file_path: str) -> str
```

**参数说明**：
- `file_path` (str): 文件路径

**返回值**：
- `extension` (str): 文件扩展名（包含点号）

**异常**：无

**使用示例**：
```python
from dingtalk_downloader.utils.path_helper import get_file_extension

extension = get_file_extension("C:/Users/test/file.txt")
print(extension)  # 输出: .txt
```

---

### validator 模块

输入验证工具函数模块，提供用户输入验证功能。

#### validate_input

验证用户输入，支持默认选项，如果用户直接按 Enter，则返回默认选项。

```python
def validate_input(prompt: str, valid_options: List[str], default_option: Optional[str] = None) -> str
```

**参数说明**：
- `prompt` (str): 提示信息
- `valid_options` (List[str]): 有效选项列表
- `default_option` (Optional[str]): 默认选项

**返回值**：
- `choice` (str): 用户选择的选项

**异常**：
- `ValueError`: 输入无效时

**使用示例**：
```python
from dingtalk_downloader.utils.validator import validate_input

# 不带默认选项
choice = validate_input("请选择浏览器 (1-Edge, 2-Chrome, 3-Firefox): ", ["1", "2", "3"])
print(f"你选择了: {choice}")

# 带默认选项
choice = validate_input("请选择浏览器 (1-Edge, 2-Chrome, 3-Firefox) [默认: 1]: ", ["1", "2", "3"], "1")
print(f"你选择了: {choice}")
```

## 使用流程

### 从文件读取链接流程

```python
from dingtalk_downloader.utils.file_reader import FileReader

try:
    # 创建文件读取器
    file_reader = FileReader("links.csv")
    
    # 读取链接
    links = file_reader.read_links()
    
    # 处理链接
    print(f"找到 {len(links)} 个链接")
    for index, url in links.items():
        print(f"{index}: {url}")
        
except FileNotFoundError:
    print("文件不存在")
except ValueError as e:
    print(f"错误: {e}")
except Exception as e:
    print(f"读取失败: {e}")
```

### 路径处理流程

```python
from dingtalk_downloader.utils.path_helper import clean_file_path, join_paths, ensure_dir_exists, get_file_extension

# 清理路径
path = '  "C:/Users/test/file.txt"  '
cleaned_path = clean_file_path(path)

# 拼接路径
full_path = join_paths("C:/Users", "test", "file.txt")

# 确保目录存在
ensure_dir_exists("C:/Users/test/new_dir")

# 获取文件扩展名
extension = get_file_extension("C:/Users/test/file.txt")
```

### 用户输入验证流程

```python
from dingtalk_downloader.utils.validator import validate_input

# 验证浏览器选择
browser_choice = validate_input(
    "请选择浏览器 (1-Edge, 2-Chrome, 3-Firefox): ",
    ["1", "2", "3"]
)

# 验证下载模式（带默认选项）
download_mode = validate_input(
    "请选择下载模式 (1-单个, 2-批量) [默认: 1]: ",
    ["1", "2"],
    "1"
)

# 验证保存模式（带默认选项）
save_mode = validate_input(
    "请选择保存模式 (1-默认路径, 2-手动选择) [默认: 1]: ",
    ["1", "2"],
    "1"
)
```

## 异常处理

### 常见异常

1. **文件不存在**
   - 原因：指定的文件路径不存在
   - 解决：检查文件路径是否正确

2. **文件格式不支持**
   - 原因：文件格式不是 CSV 或 Excel
   - 解决：使用 CSV 或 Excel 文件

3. **文件编码无法识别**
   - 原因：CSV 文件使用的编码无法识别
   - 解决：尝试使用其他编码格式（如 UTF-8、GBK）

4. **未找到有效的钉钉直播链接**
   - 原因：文件中没有以 "https://n.dingtalk.com" 开头的链接
   - 解决：检查文件内容，确保包含有效的钉钉直播链接

5. **输入无效**
   - 原因：用户输入的选项不在有效选项列表中
   - 解决：重新输入有效的选项

### 异常处理示例

```python
from dingtalk_downloader.utils.file_reader import FileReader

try:
    file_reader = FileReader("links.csv")
    links = file_reader.read_links()
    print(f"找到 {len(links)} 个链接")
except FileNotFoundError:
    print("文件不存在，请检查文件路径")
except ValueError as e:
    print(f"文件格式错误: {e}")
except Exception as e:
    print(f"读取文件时发生错误: {e}")
```

## 注意事项

1. **文件格式**：FileReader 只支持 CSV 和 Excel 文件（.csv、.xlsx、.xls）
2. **链接格式**：只提取以 "https://n.dingtalk.com" 开头的链接
3. **文件编码**：CSV 文件支持 UTF-8 和 GBK 编码，如果其他编码无法识别，会提示错误
4. **路径处理**：path_helper 模块的函数都是跨平台的，可以在 Windows、Linux、macOS 上使用
5. **输入验证**：validator 模块的 validate_input 函数会一直循环直到用户输入有效的选项
6. **默认选项**：validate_input 函数支持默认选项，如果用户直接按 Enter，则返回默认选项
