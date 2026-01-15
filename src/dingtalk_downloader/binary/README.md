# 二进制工具封装模块

## 模块概述

本模块负责封装和调用外部二进制工具（FFmpeg 和 N_m3u8DL-RE），提供统一的接口供上层模块使用，实现音视频处理和 m3u8 视频流下载功能。

## 功能描述

### FFmpegWrapper - FFmpeg 调用封装

**功能**：
- 封装 FFmpeg 工具的调用逻辑
- 提供音视频文件转换功能
- 自动检测操作系统并使用对应的可执行文件

### NM3u8DLRE - N_m3u8DL-RE 调用封装

**功能**：
- 封装 N_m3u8DL-RE 工具的调用逻辑
- 提供从 m3u8 文件下载视频流的功能
- 支持自定义 Cookie 和请求头
- 自动构建下载命令

## 核心实现原理

### FFmpegWrapper 实现原理

#### 可执行文件路径检测

```python
if system == "Windows":
    self.executable_path = os.path.join("assets", "bin", "ffmpeg.exe")
elif system == "Linux" or system == "Darwin":
    self.executable_path = os.path.join("assets", "bin", "ffmpeg")
else:
    self.executable_path = "ffmpeg"
```

#### 命令构建

```python
command = [self.executable_path, "-i", input_file]

if options:
    command.extend(options)

command.append(output_file)
```

#### 子进程调用

使用 `subprocess.run()` 执行 FFmpeg 命令，实现音视频转换。

### NM3u8DLRE 实现原理

#### 可执行文件路径检测

```python
if system == "Windows":
    return os.path.join("assets", "bin", "N_m3u8DL-RE.exe")
elif system == "Linux" or system == "Darwin":
    return os.path.join("assets", "bin", "N_m3u8DL-RE")
```

#### 下载命令构建

```python
command = [
    self.executable_path,
    m3u8_file,
    "--ui-language", "zh-CN",
    "--save-name", save_name,
    "--save-dir", save_dir,
    "--base-url", prefix,
]

# 添加 Cookie
if cookies_data:
    cookie_string = "; ".join([f"{name}={value}" for name, value in cookies_data.items()])
    command.extend(["-H", f"Cookie: {cookie_string}"])

# 添加请求头
if headers:
    if "User-Agent" in headers:
        command.extend(["-H", f"User-Agent: {headers['User-Agent']}"])
    if "Referer" in headers:
        command.extend(["-H", f"Referer: {headers['Referer']}"])
    # ... 其他请求头
```

#### 下载结果验证

```python
if result.returncode != 0:
    logger.error(f"视频下载失败 - 子进程退出码: {result.returncode}")
    return False

output = result.stdout + result.stderr

if "ERROR:" in output or "Failed" in output:
    # 提取错误信息
    error_lines = []
    for line in output.split('\n'):
        if 'ERROR:' in line or 'Failed' in line:
            error_lines.append(line.strip())
    error_info = '\n'.join(error_lines)
    logger.error(f"视频下载失败")
    if error_info:
        logger.error(f"错误信息:\n{error_info}")
    return False
```

## 使用方法

### FFmpegWrapper 使用示例

```python
from dingtalk_downloader.binary.ffmpeg_wrapper import FFmpegWrapper

# 创建 FFmpeg 调用器
ffmpeg = FFmpegWrapper()

# 转换音视频文件
success = ffmpeg.convert(
    input_file="input.mp4",
    output_file="output.mkv",
    options=["-c:v", "libx264", "-c:a", "aac"]
)

if success:
    print("转换成功")
else:
    print("转换失败")
```

### NM3u8DLRE 使用示例

```python
from dingtalk_downloader.binary.n_m3u8dl_re import NM3u8DLRE

# 创建 N_m3u8DL-RE 调用器
downloader = NM3u8DLRE()

# 下载 m3u8 视频
success = downloader.download(
    m3u8_file="output.m3u8",
    save_name="直播视频",
    save_dir="Downloads",
    prefix="https://example.com/live_hp/abc-123",
    cookies_data={"session_id": "xxx", "token": "yyy"},
    headers={
        "User-Agent": "Mozilla/5.0 ...",
        "Referer": "https://n.dingtalk.com/"
    }
)

if success:
    print("下载成功")
else:
    print("下载失败")
```

## 接口参数说明

### FFmpegWrapper 类

#### __init__(executable_path: Optional[str] = None)

**参数**：
- `executable_path`：可执行文件路径，默认为 None（自动检测）

**功能**：初始化 FFmpeg 调用器

#### convert(input_file: str, output_file: str, options: Optional[List[str]] = None) -> bool

**参数**：
- `input_file`：输入文件路径
- `output_file`：输出文件路径
- `options`：FFmpeg 选项列表，默认为 None

**返回值**：
- `bool`：转换是否成功

**功能**：转换音视频文件

#### build_command(input_file: str, output_file: str, options: Optional[List[str]] = None) -> List[str]

**参数**：
- `input_file`：输入文件路径
- `output_file`：输出文件路径
- `options`：FFmpeg 选项列表，默认为 None

**返回值**：
- `List[str]`：命令列表

**功能**：构建 FFmpeg 转换命令

### NM3u8DLRE 类

#### __init__(executable_path: Optional[str] = None)

**参数**：
- `executable_path`：可执行文件路径，默认为 None（自动检测）

**功能**：初始化 N_m3u8DL-RE 调用器

#### download(m3u8_file: str, save_name: str, save_dir: str, prefix: str, cookies_data: Optional[Dict[str, str]] = None, headers: Optional[Dict[str, str]] = None) -> bool

**参数**：
- `m3u8_file`：m3u8 文件路径
- `save_name`：保存文件名
- `save_dir`：保存目录
- `prefix`：基础 URL
- `cookies_data`：Cookie 字典，默认为 None
- `headers`：请求头字典，默认为 None

**返回值**：
- `bool`：下载是否成功

**功能**：下载 m3u8 视频

#### build_command(m3u8_file: str, save_name: str, save_dir: str, prefix: str, cookies_data: Optional[Dict[str, str]] = None, headers: Optional[Dict[str, str]] = None) -> List[str]

**参数**：
- `m3u8_file`：m3u8 文件路径
- `save_name`：保存文件名
- `save_dir`：保存目录
- `prefix`：基础 URL
- `cookies_data`：Cookie 字典，默认为 None
- `headers`：请求头字典，默认为 None

**返回值**：
- `List[str]`：命令列表

**功能**：构建 N_m3u8DL-RE 下载命令

#### get_executable_name() -> str

**参数**：无

**返回值**：
- `str`：可执行文件名

**功能**：获取可执行文件名（静态方法）

## 依赖关系

### 依赖的外部工具

1. **FFmpeg**
   - 音视频处理工具
   - 用于音视频格式转换

2. **N_m3u8DL-RE**
   - m3u8 视频流下载工具
   - 用于下载钉钉直播回放视频

### 依赖的 Python 模块

1. `subprocess` - 子进程调用
2. `platform` - 操作系统检测
3. `logging` - 日志记录
4. `typing` - 类型提示

### 被依赖的模块

1. `core.downloader` - 下载器核心模块

## 数据流程

### FFmpeg 转换流程

```
输入文件路径
  ↓
构建 FFmpeg 命令
  ↓
执行 subprocess.run()
  ↓
检查返回码
  ↓
返回转换结果
```

### N_m3u8DL-RE 下载流程

```
m3u8 文件路径
  ↓
构建下载命令
  ↓
执行 subprocess.run()
  ↓
检查返回码
  ↓
检查输出中的错误信息
  ↓
返回下载结果
```

## 注意事项

1. **可执行文件路径**
   - 默认路径为 `assets/bin/` 目录
   - 支持自定义路径
   - 自动检测操作系统

2. **错误处理**
   - 捕获子进程异常
   - 检查返回码和输出
   - 记录详细错误信息

3. **日志记录**
   - 记录命令执行过程
   - 记录成功/失败信息
   - 记录错误详情

4. **请求头处理**
   - Cookie 格式化为 `name=value; name2=value2`
   - 支持默认请求头
   - 自动添加必要的请求头

## 扩展方向

1. **支持更多工具**
   - 添加对其他音视频处理工具的支持

2. **进度回调**
   - 添加下载/转换进度回调函数

3. **并发下载**
   - 支持多线程/多进程下载

4. **断点续传**
   - 支持下载中断后继续下载

5. **更多格式支持**
   - 扩展支持更多音视频格式

## 相关文档

- [核心业务模块 - Downloader](../core/README.md)
- [配置模块 - Constants](../config/README.md)
