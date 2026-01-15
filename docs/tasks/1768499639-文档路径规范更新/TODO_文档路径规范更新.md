# 文档路径规范更新 - 待办事项清单

## 一、待办事项

### 1.1 实际文件系统更新

**待办事项**: 将实际项目文件结构更新为符合文档规范

**具体操作**:

1. 在项目根目录下创建`assets/bin`目录
2. 将`N_m3u8DL-RE.exe`移动到`assets/bin`目录
3. 将`N_m3u8DL-RE`(Linux/macOS)移动到`assets/bin`目录
4. 将`ffmpeg.exe`移动到`assets/bin`目录
5. 将`ffmpeg`(Linux/macOS)移动到`assets/bin`目录
6. 在项目根目录下创建`assets/template`目录
7. 将`批量下载模板.xlsx`移动到`assets/template`目录
8. 将`Source/ICO`目录移动到`assets/ICO`目录
9. 删除空的`Source`目录

**注意事项**:

- 移动文件前请备份重要文件
- 确保文件移动后权限正确
- 测试文件移动后程序是否正常运行

**优先级**: 高

### 1.2 代码中的路径引用更新

**待办事项**: 更新代码中所有涉及文件路径的引用

**具体操作**:

1. 搜索代码中所有涉及`N_m3u8DL-RE.exe`的路径引用
2. 搜索代码中所有涉及`ffmpeg.exe`的路径引用
3. 搜索代码中所有涉及`批量下载模板.xlsx`的路径引用
4. 搜索代码中所有涉及`Source/ICO`的路径引用
5. 将所有路径引用更新为新的标准路径

**注意事项**:

- 使用全局搜索功能,确保不遗漏任何路径引用
- 更新后进行充分测试
- 确保跨平台兼容性(Windows/Linux/macOS)

**优先级**: 高

### 1.3 其他文档更新

**待办事项**: 更新其他相关文档中的文件路径引用

**具体操作**:

1. 检查`README.md`中是否有文件路径引用需要更新
2. 检查`project_status.md`中是否有文件路径引用需要更新(作为历史记录保留,建议添加说明)
3. 检查其他 docs 目录下的文档中是否有文件路径引用需要更新
4. 更新所有相关的文件路径引用

**注意事项**:

- `project_status.md`作为历史记录保留,建议在文档开头添加说明,指出该文档记录的是项目现状,不代表当前规范
- 更新后进行交叉检查,确保所有文档一致

**优先级**: 中

### 1.4 测试验证

**待办事项**: 对更新后的文件结构和代码进行充分测试

**具体操作**:

1. 测试单个视频下载功能
2. 测试批量下载功能
3. 测试浏览器自动化功能
4. 测试跨平台兼容性(Windows/Linux/macOS)
5. 测试所有边界条件和异常情况

**注意事项**:

- 确保所有功能正常运行
- 确保没有引入新的 bug
- 记录测试结果和问题

**优先级**: 高

### 1.5 文档完善

**待办事项**: 完善相关文档,确保文档完整性和准确性

**具体操作**:

1. 在`README.md`中添加项目目录结构说明
2. 在`README.md`中添加文件路径规范说明
3. 在`project_status.md`开头添加说明,指出该文档记录的是项目现状,不代表当前规范
4. 检查并完善其他相关文档

**注意事项**:

- 保持文档风格一致
- 确保文档内容准确
- 使用统一的格式和术语

**优先级**: 中

## 二、缺少的配置

### 2.1 缺少的环境变量配置

**缺少的配置**: 外部二进制文件路径的环境变量

**建议配置**:

```bash
# 外部二进制文件路径
BINARY_DIR=assets/bin

# N_m3u8DL-RE工具路径
N_M3U8DL_RE_PATH=assets/bin/N_m3u8DL-RE.exe

# FFmpeg工具路径
FFMPEG_PATH=assets/bin/ffmpeg.exe

# 批量下载模板路径
TEMPLATE_PATH=assets/template/批量下载模板.xlsx

# ICO文件夹路径
ICO_DIR=assets/ICO
```

**操作指引**:

1. 在`.env.example`文件中添加上述环境变量配置
2. 在代码中添加环境变量加载逻辑
3. 在代码中使用环境变量替代硬编码的路径

**优先级**: 中

### 2.2 缺少的配置文件

**缺少的配置**: 文件路径配置文件

**建议配置**: 创建`config/paths.py`文件

```python
"""
文件路径配置模块

本模块定义项目中所有文件路径的配置,便于统一管理和修改。
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 外部二进制文件目录
BINARY_DIR = PROJECT_ROOT / "assets" / "bin"

# N_m3u8DL-RE工具路径
N_M3U8DL_RE_PATH = BINARY_DIR / "N_m3u8DL-RE.exe"

# FFmpeg工具路径
FFMPEG_PATH = BINARY_DIR / "ffmpeg.exe"

# 批量下载模板路径
TEMPLATE_PATH = PROJECT_ROOT / "assets" / "template" / "批量下载模板.xlsx"

# ICO文件夹路径
ICO_DIR = PROJECT_ROOT / "assets" / "ICO"

# 测试数据目录
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures"

# 下载目录
DOWNLOAD_DIR = PROJECT_ROOT / "Downloads"

# 日志目录
LOG_DIR = PROJECT_ROOT / "logs"
```

**操作指引**:

1. 创建`config/paths.py`文件
2. 在代码中导入并使用上述路径配置
3. 确保路径配置与文档规范一致

**优先级**: 中

## 三、操作指引

### 3.1 文件系统更新指引

#### 步骤 1: 创建目录结构

```bash
# Windows PowerShell
New-Item -ItemType Directory -Path "assets\bin" -Force
New-Item -ItemType Directory -Path "assets\template" -Force
New-Item -ItemType Directory -Path "assets\ICO" -Force

# Linux/macOS
mkdir -p assets/bin
mkdir -p assets/template
mkdir -p assets/ICO
```

#### 步骤 2: 移动文件

```bash
# Windows PowerShell
Move-Item -Path "N_m3u8DL-RE.exe" -Destination "assets\bin\" -Force
Move-Item -Path "ffmpeg.exe" -Destination "assets\bin\" -Force
Move-Item -Path "批量下载模板.xlsx" -Destination "assets\template\" -Force
Move-Item -Path "Source\ICO" -Destination "assets\ICO" -Force

# Linux/macOS
mv N_m3u8DL-RE assets/bin/
mv ffmpeg assets/bin/
mv 批量下载模板.xlsx assets/template/
mv Source/ICO assets/ICO
```

#### 步骤 3: 删除空目录

```bash
# Windows PowerShell
Remove-Item -Path "Source" -Recurse -Force

# Linux/macOS
rmdir Source
```

### 3.2 代码路径引用更新指引

#### 步骤 1: 搜索路径引用

```bash
# 搜索N_m3u8DL-RE.exe
grep -r "N_m3u8DL-RE.exe" --include="*.py" .

# 搜索ffmpeg.exe
grep -r "ffmpeg.exe" --include="*.py" .

# 搜索批量下载模板.xlsx
grep -r "批量下载模板.xlsx" --include="*.py" .

# 搜索Source/ICO
grep -r "Source/ICO" --include="*.py" .
```

#### 步骤 2: 更新路径引用

将所有路径引用更新为新的标准路径:

- `N_m3u8DL-RE.exe` → `assets/bin/N_m3u8DL-RE.exe`
- `ffmpeg.exe` → `assets/bin/ffmpeg.exe`
- `批量下载模板.xlsx` → `assets/template/批量下载模板.xlsx`
- `Source/ICO` → `assets/ICO`

#### 步骤 3: 测试验证

运行所有测试,确保更新后代码正常运行:

```bash
pytest
```

### 3.3 环境变量配置指引

#### 步骤 1: 更新.env.example 文件

在`.env.example`文件中添加环境变量配置:

```bash
# 外部二进制文件路径
BINARY_DIR=assets/bin

# N_m3u8DL-RE工具路径
N_M3U8DL_RE_PATH=assets/bin/N_m3u8DL-RE.exe

# FFmpeg工具路径
FFMPEG_PATH=assets/bin/ffmpeg.exe

# 批量下载模板路径
TEMPLATE_PATH=assets/template/批量下载模板.xlsx

# ICO文件夹路径
ICO_DIR=assets/ICO
```

#### 步骤 2: 创建.env 文件

复制`.env.example`文件为`.env`文件:

```bash
# Windows PowerShell
Copy-Item -Path ".env.example" -Destination ".env"

# Linux/macOS
cp .env.example .env
```

#### 步骤 3: 更新代码以使用环境变量

在代码中添加环境变量加载逻辑:

```python
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 获取环境变量
binary_dir = os.getenv('BINARY_DIR', 'assets/bin')
n_m3u8dl_re_path = os.getenv('N_M3U8DL_RE_PATH', 'assets/bin/N_m3u8DL-RE.exe')
ffmpeg_path = os.getenv('FFMPEG_PATH', 'assets/bin/ffmpeg.exe')
template_path = os.getenv('TEMPLATE_PATH', 'assets/template/批量下载模板.xlsx')
ico_dir = os.getenv('ICO_DIR', 'assets/ICO')
```

## 四、注意事项

### 4.1 文件移动注意事项

1. **备份重要文件**: 在移动文件前,请备份重要文件
2. **检查文件权限**: 确保文件移动后权限正确
3. **测试程序运行**: 测试文件移动后程序是否正常运行
4. **跨平台兼容性**: 确保跨平台兼容性(Windows/Linux/macOS)

### 4.2 代码更新注意事项

1. **全局搜索**: 使用全局搜索功能,确保不遗漏任何路径引用
2. **充分测试**: 更新后进行充分测试
3. **版本控制**: 使用版本控制系统,便于回滚
4. **代码审查**: 进行代码审查,确保更新正确

### 4.3 文档更新注意事项

1. **保持一致**: 确保所有文档一致
2. **历史记录**: `project_status.md`作为历史记录保留,建议添加说明
3. **文档风格**: 保持文档风格一致
4. **格式统一**: 使用统一的格式和术语

## 五、优先级说明

### 5.1 高优先级

- 实际文件系统更新
- 代码中的路径引用更新
- 测试验证

### 5.2 中优先级

- 其他文档更新
- 文档完善
- 缺少的环境变量配置
- 缺少的配置文件

### 5.3 低优先级

- 其他优化和改进

## 六、总结

本 TODO 文档列出了文档路径规范更新后的待办事项和缺少的配置,包括:

1. **实际文件系统更新**: 将实际项目文件结构更新为符合文档规范
2. **代码中的路径引用更新**: 更新代码中所有涉及文件路径的引用
3. **其他文档更新**: 更新其他相关文档中的文件路径引用
4. **测试验证**: 对更新后的文件结构和代码进行充分测试
5. **文档完善**: 完善相关文档,确保文档完整性和准确性
6. **缺少的环境变量配置**: 添加外部二进制文件路径的环境变量配置
7. **缺少的配置文件**: 创建文件路径配置文件

所有待办事项都提供了具体的操作指引和注意事项,便于快速执行。
