# Binary 模块 API 文档

## 模块概述

Binary 模块是 DingTalk 直播回放下载工具的二进制工具调用模块，负责调用外部二进制工具（如 N_m3u8DL-RE、FFmpeg）进行视频下载和音视频处理。该模块包含以下核心组件：

- **NM3u8DLRE**: N_m3u8DL-RE 调用类，负责调用 N_m3u8DL-RE 工具下载 m3u8 视频流
- **FFmpegWrapper**: FFmpeg 调用类，负责调用 FFmpeg 工具进行音视频处理

## 类文档

### NM3u8DLRE

N_m3u8DL-RE 调用类，负责调用 N_m3u8DL-RE 工具。该类封装了 N_m3u8DL-RE 工具的调用逻辑，提供统一的接口供上层模块使用。

#### 初始化方法

```python
def __init__(self, executable_path: Optional[str] = None)
```

**参数说明**：

- `executable_path` (Optional[str]): 可执行文件路径，默认为 None（自动查找）

**返回值**：无

**异常**：无

**使用示例**：

```python
from dingtalk_downloader.binary.n_m3u8dl_re import NM3u8DLRE

# 使用默认路径
downloader = NM3u8DLRE()

# 使用自定义路径
downloader = NM3u8DLRE(executable_path="C:/tools/N_m3u8DL-RE.exe")
```

#### download

下载 m3u8 视频，构建下载命令并调用 N_m3u8DL-RE 工具。

```python
def download(
    self,
    m3u8_file: str,
    save_name: str,
    save_dir: str,
    prefix: str,
    cookies_data: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None
) -> bool
```

**参数说明**：

- `m3u8_file` (str): m3u8 文件路径
- `save_name` (str): 保存文件名
- `save_dir` (str): 保存目录
- `prefix` (str): 基础 URL
- `cookies_data` (Optional[Dict[str, str]]): Cookie 字典，默认为 None
- `headers` (Optional[Dict[str, str]]): 请求头字典，默认为 None

**返回值**：

- `success` (bool): 下载是否成功

**异常**：

- `Exception`: 下载失败时

**使用示例**：

```python
from dingtalk_downloader.binary.n_m3u8dl_re import NM3u8DLRE

downloader = NM3u8DLRE()

cookies = {
    "session_id": "abc123",
    "user_token": "xyz789"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://n.dingtalk.com/"
}

success = downloader.download(
    m3u8_file="output.m3u8",
    save_name="video",
    save_dir="Downloads",
    prefix="https://example.com/path/",
    cookies_data=cookies,
    headers=headers
)

if success:
    print("下载成功")
else:
    print("下载失败")
```

#### build_command

构建下载命令，构建 N_m3u8DL-RE 下载命令，包括文件名、保存目录、基础 URL、Cookie 和请求头。

```python
def build_command(
    self,
    m3u8_file: str,
    save_name: str,
    save_dir: str,
    prefix: str,
    cookies_data: Optional[Dict[str, str]] = None,
    headers: Optional[Dict[str, str]] = None
) -> List[str]
```

**参数说明**：

- `m3u8_file` (str): m3u8 文件路径
- `save_name` (str): 保存文件名
- `save_dir` (str): 保存目录
- `prefix` (str): 基础 URL
- `cookies_data` (Optional[Dict[str, str]]): Cookie 字典，默认为 None
- `headers` (Optional[Dict[str, str]]): 请求头字典，默认为 None

**返回值**：

- `command` (List[str]): 命令列表

**异常**：无

**使用示例**：

```python
from dingtalk_downloader.binary.n_m3u8dl_re import NM3u8DLRE

downloader = NM3u8DLRE()

command = downloader.build_command(
    m3u8_file="output.m3u8",
    save_name="video",
    save_dir="Downloads",
    prefix="https://example.com/path/",
    cookies_data={"session_id": "abc123"},
    headers={"User-Agent": "Mozilla/5.0"}
)

print("命令:", " ".join(command))
```

#### get_executable_name

获取可执行文件名，根据操作系统返回对应的可执行文件名。

```python
@staticmethod
def get_executable_name() -> str
```

**参数说明**：无

**返回值**：

- `executable_name` (str): 可执行文件名

**异常**：

- `Exception`: 不支持的操作系统时

**使用示例**：

```python
from dingtalk_downloader.binary.n_m3u8dl_re import NM3u8DLRE

executable_name = NM3u8DLRE.get_executable_name()
print(f"可执行文件名: {executable_name}")
# Windows: N_m3u8DL-RE.exe
# Linux/macOS: ./N_m3u8DL-RE
```

---

### FFmpegWrapper

FFmpeg 调用类，负责调用 FFmpeg 工具。该类封装了 FFmpeg 工具的调用逻辑，提供统一的接口供上层模块使用。

#### 初始化方法

```python
def __init__(self, executable_path: Optional[str] = None)
```

**参数说明**：

- `executable_path` (Optional[str]): 可执行文件路径，默认为 None（使用默认路径）

**返回值**：无

**异常**：无

**使用示例**：

```python
from dingtalk_downloader.binary.ffmpeg_wrapper import FFmpegWrapper

# 使用默认路径
ffmpeg = FFmpegWrapper()

# 使用自定义路径
ffmpeg = FFmpegWrapper(executable_path="C:/tools/ffmpeg.exe")
```

#### convert

转换音视频文件，构建转换命令并调用 FFmpeg 工具。

```python
def convert(
    self,
    input_file: str,
    output_file: str,
    options: Optional[List[str]] = None
) -> bool
```

**参数说明**：

- `input_file` (str): 输入文件路径
- `output_file` (str): 输出文件路径
- `options` (Optional[List[str]]): FFmpeg 选项列表，默认为 None

**返回值**：

- `success` (bool): 转换是否成功

**异常**：

- `Exception`: 转换失败时

**使用示例**：

```python
from dingtalk_downloader.binary.ffmpeg_wrapper import FFmpegWrapper

ffmpeg = FFmpegWrapper()

# 基本转换
success = ffmpeg.convert(
    input_file="input.mp4",
    output_file="output.mkv"
)

# 带选项的转换
options = [
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "23",
    "-c:a", "aac",
    "-b:a", "128k"
]

success = ffmpeg.convert(
    input_file="input.mp4",
    output_file="output.mkv",
    options=options
)

if success:
    print("转换成功")
else:
    print("转换失败")
```

#### build_command

构建转换命令，构建 FFmpeg 转换命令。

```python
def build_command(
    self,
    input_file: str,
    output_file: str,
    options: Optional[List[str]] = None
) -> List[str]
```

**参数说明**：

- `input_file` (str): 输入文件路径
- `output_file` (str): 输出文件路径
- `options` (Optional[List[str]]): FFmpeg 选项列表，默认为 None

**返回值**：

- `command` (List[str]): 命令列表

**异常**：无

**使用示例**：

```python
from dingtalk_downloader.binary.ffmpeg_wrapper import FFmpegWrapper

ffmpeg = FFmpegWrapper()

# 基本命令
command = ffmpeg.build_command(
    input_file="input.mp4",
    output_file="output.mkv"
)

# 带选项的命令
options = ["-c:v", "libx264", "-preset", "medium", "-crf", "23"]
command = ffmpeg.build_command(
    input_file="input.mp4",
    output_file="output.mkv",
    options=options
)

print("命令:", " ".join(command))
```

## 使用流程

### 使用 N_m3u8DL-RE 下载视频流程

```python
from dingtalk_downloader.binary.n_m3u8dl_re import NM3u8DLRE

# 创建下载器实例
downloader = NM3u8DLRE()

# 准备下载参数
m3u8_file = "output.m3u8"
save_name = "video"
save_dir = "Downloads"
prefix = "https://example.com/path/"

# 准备 Cookie 和请求头
cookies = {
    "session_id": "abc123",
    "user_token": "xyz789"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://n.dingtalk.com/",
    "Accept": "application/vnd.apple.mpegurl, text/plain, */*"
}

# 下载视频
try:
    success = downloader.download(
        m3u8_file=m3u8_file,
        save_name=save_name,
        save_dir=save_dir,
        prefix=prefix,
        cookies_data=cookies,
        headers=headers
    )

    if success:
        print("视频下载成功")
    else:
        print("视频下载失败")

except Exception as e:
    print(f"下载过程中发生错误: {e}")
```

### 使用 FFmpeg 转换视频流程

```python
from dingtalk_downloader.binary.ffmpeg_wrapper import FFmpegWrapper

# 创建 FFmpeg 实例
ffmpeg = FFmpegWrapper()

# 准备转换参数
input_file = "input.mp4"
output_file = "output.mkv"

# 准备转换选项
options = [
    "-c:v", "libx264",
    "-preset", "medium",
    "-crf", "23",
    "-c:a", "aac",
    "-b:a", "128k",
    "-movflags", "+faststart"
]

# 转换视频
try:
    success = ffmpeg.convert(
        input_file=input_file,
        output_file=output_file,
        options=options
    )

    if success:
        print("视频转换成功")
    else:
        print("视频转换失败")

except Exception as e:
    print(f"转换过程中发生错误: {e}")
```

### 构建自定义命令流程

```python
from dingtalk_downloader.binary.n_m3u8dl_re import NM3u8DLRE
from dingtalk_downloader.binary.ffmpeg_wrapper import FFmpegWrapper

# 构建 N_m3u8DL-RE 命令
downloader = NM3u8DLRE()
command = downloader.build_command(
    m3u8_file="output.m3u8",
    save_name="video",
    save_dir="Downloads",
    prefix="https://example.com/path/",
    cookies_data={"session_id": "abc123"},
    headers={"User-Agent": "Mozilla/5.0"}
)

print("N_m3u8DL-RE 命令:", " ".join(command))

# 构建 FFmpeg 命令
ffmpeg = FFmpegWrapper()
command = ffmpeg.build_command(
    input_file="input.mp4",
    output_file="output.mkv",
    options=["-c:v", "libx264", "-preset", "medium"]
)

print("FFmpeg 命令:", " ".join(command))
```

## 异常处理

### 常见异常

1. **可执行文件未找到**

   - 原因：N_m3u8DL-RE 或 FFmpeg 未安装或未配置到系统 PATH
   - 解决：安装对应的工具并配置到系统 PATH，或指定可执行文件路径

2. **下载失败**

   - 原因：m3u8 文件无效、网络问题、Cookie 或请求头错误
   - 解决：检查 m3u8 文件、网络连接、Cookie 和请求头

3. **转换失败**

   - 原因：输入文件无效、输出路径不可写、选项错误
   - 解决：检查输入文件、输出路径权限、FFmpeg 选项

4. **不支持的操作系统**
   - 原因：操作系统不在支持列表中
   - 解决：使用支持的操作系统（Windows、Linux、macOS）

### 异常处理示例

```python
from dingtalk_downloader.binary.n_m3u8dl_re import NM3u8DLRE
from dingtalk_downloader.binary.ffmpeg_wrapper import FFmpegWrapper

# N_m3u8DL-RE 下载异常处理
downloader = NM3u8DLRE()

try:
    success = downloader.download(
        m3u8_file="output.m3u8",
        save_name="video",
        save_dir="Downloads",
        prefix="https://example.com/path/"
    )
except FileNotFoundError:
    print("N_m3u8DL-RE 未找到，请安装并配置到系统 PATH")
except Exception as e:
    if "可执行文件" in str(e):
        print("可执行文件错误，请检查路径")
    elif "网络" in str(e):
        print("网络错误，请检查网络连接")
    else:
        print(f"下载失败: {e}")

# FFmpeg 转换异常处理
ffmpeg = FFmpegWrapper()

try:
    success = ffmpeg.convert(
        input_file="input.mp4",
        output_file="output.mkv"
    )
except FileNotFoundError:
    print("FFmpeg 未找到，请安装并配置到系统 PATH")
except Exception as e:
    if "输入文件" in str(e):
        print("输入文件错误，请检查文件路径")
    elif "输出路径" in str(e):
        print("输出路径错误，请检查路径权限")
    else:
        print(f"转换失败: {e}")
```

## 注意事项

1. **工具安装**：使用前请确保已安装 N_m3u8DL-RE 和 FFmpeg 工具
2. **系统 PATH**：建议将工具添加到系统 PATH 中，或指定可执行文件路径
3. **Cookie 和请求头**：下载时需要提供正确的 Cookie 和请求头，否则可能下载失败
4. **文件路径**：确保输入文件路径正确，输出路径有写入权限
5. **网络连接**：下载时需要稳定的网络连接
6. **FFmpeg 选项**：使用 FFmpeg 选项时，请确保选项格式正确
7. **跨平台支持**：模块支持 Windows、Linux、macOS 操作系统
8. **命令构建**：build_command 方法只构建命令，不执行命令，需要手动执行或使用 download/convert 方法
