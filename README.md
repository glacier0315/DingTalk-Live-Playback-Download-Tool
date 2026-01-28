# DingTalk-Live-Playback-Download-Tool

<div align="center">

钉钉直播回放下载工具 - 一键下载钉钉直播回放视频

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Black](https://img.shields.io/badge/Code%20Style-Black-black.svg)](https://github.com/psf/black)

</div>

## 项目概述

DingTalk-Live-Playback-Download-Tool 是一个功能强大的钉钉直播回放下载工具，专为需要保存钉钉直播回放内容的用户设计。该工具通过自动化浏览器操作，实现了钉钉直播回放视频的批量下载功能，支持多种浏览器和下载模式，极大提升了工作效率。

### 核心特性

- **一键下载**：通过钉钉分享链接，一键下载直播回放视频
- **批量处理**：支持批量下载多个直播回放，通过 CSV/Excel 文件导入链接
- **多浏览器支持**：兼容 Edge、Chrome、Firefox 等主流浏览器
- **自动化操作**：自动处理浏览器登录、Cookie 获取、视频解析等复杂流程
- **智能下载**：自动识别 M3U8 视频流，使用专业工具进行下载和合并
- **跨平台支持**：支持 Windows、macOS、Linux 等主流操作系统
- **模块化设计**：采用清晰的模块化架构，易于维护和扩展

### 技术架构

项目采用模块化设计，主要包含以下核心模块：

- **Core 模块**：核心业务逻辑，包括下载器、Cookie 处理器、M3U8 解析器
- **Browser 模块**：浏览器自动化，支持多种浏览器的驱动管理和操作
- **Utils 模块**：工具函数库，提供文件操作、路径处理、字符串处理等通用功能
- **Binary 模块**：二进制工具封装，集成 N_m3u8DL-RE 和 FFmpeg 等专业工具
- **Config 模块**：配置管理，统一管理项目配置和常量定义

## 项目目录结构

```plaintext
DingTalk-Live-Playback-Download-Tool/
├── src/                                    # 源代码目录
│   └── dingtalk_downloader/                # 项目包名
│       ├── __init__.py
│       ├── main.py                         # 程序入口文件
│       ├── core/                           # 核心业务逻辑模块
│       ├── utils/                          # 工具函数模块
│       ├── binary/                         # 二进制程序调用模块
│       ├── browser/                        # 浏览器自动化模块
│       └── config/                         # 配置管理模块
├── tests/                                  # 测试代码目录
│   ├── unit/                               # 单元测试
│   ├── integration/                        # 集成测试
│   └── fixtures/                           # 测试数据
│       ├── sample_links.csv
│       └── sample_links.xlsx
├── assets/                                 # 静态资源目录
│   ├── bin/                                # 外部二进制程序目录
│   │   ├── N_m3u8DL-RE.exe                 # N_m3u8DL-RE可执行文件(Windows)
│   │   ├── N_m3u8DL-RE                     # N_m3u8DL-RE可执行文件(Linux/macOS)
│   │   ├── ffmpeg.exe                      # FFmpeg可执行文件(Windows)
│   │   └── ffmpeg                          # FFmpeg可执行文件(Linux/macOS)
│   ├── template/                           # 模板文件目录
│   │   └── 批量下载模板.xlsx                # 批量下载模板文件
│   └── ICO/                                # 图标资源目录
│       ├── icon-512x512.png
│       ├── icon.ico
│       └── icon.png
├── docs/                                   # 文档目录
│   ├── development_standard.md             # 开发规范文档
│   ├── development_guide.md                # 开发指南文档
│   └── project_status.md                   # 项目现状记录
├── requirements.txt                        # Python依赖包列表
├── requirements-dev.txt                    # 开发依赖包列表
├── .gitignore                              # Git忽略文件配置
├── .trae/                                  # Trae IDE配置目录
│   └── rules/
│       └── project_rules.md                # 项目规则文档
└── README.md                               # 项目说明文档
```

### 目录说明

- **src/**: 源代码目录，包含所有 Python 代码
- **tests/**: 测试代码目录，包含单元测试、集成测试和测试数据
- **assets/**: 静态资源目录，包含外部二进制程序、模板文件和图标资源
- **docs/**: 文档目录，包含开发规范、开发指南和项目记录
- **requirements.txt**: 项目运行所需的 Python 依赖包
- **requirements-dev.txt**: 开发所需的额外依赖包（测试、代码格式化等）

## 快速开始

### 环境要求

- **操作系统**：Windows 10/11、macOS 10.14+、Linux（Ubuntu 18.04+）
- **Python 版本**：Python 3.8 或更高版本
- **浏览器**：Edge、Chrome 或 Firefox（需安装对应浏览器）
- **网络**：稳定的网络连接，用于访问钉钉平台

### 安装步骤

#### 方式一：使用可执行文件（推荐）

1. 从 [Releases](https://github.com/glacier0315/DingTalk-Live-Playback-Download-Tool/releases) 页面下载最新版本的可执行文件
2. 解压下载的压缩包
3. 双击运行 `DingTalk-Live-Playback-Download-Tool.exe`
4. 按照界面提示进行操作

#### 方式二：从源码安装

```bash
# 克隆项目
git clone https://github.com/glacier0315/DingTalk-Live-Playback-Download-Tool.git
cd DingTalk-Live-Playback-Download-Tool

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖（可选）
pip install -r requirements-dev.txt

# 运行程序
python -m src.dingtalk_downloader.main
```

### 基本使用

#### 单个视频下载

1. 运行程序后，选择"单个下载"模式
2. 输入钉钉直播分享链接
3. 选择保存路径和浏览器类型
4. 等待浏览器自动打开
5. 在浏览器中登录钉钉账号
6. 等待页面加载完毕后，按回车键开始下载

#### 批量视频下载

1. 准备 CSV 或 Excel 文件，将钉钉直播分享链接放入单元格（不要放在首行）
2. 运行程序后，选择"批量下载"模式
3. 输入或拖拽包含链接的文件
4. 选择保存路径和浏览器类型
5. 等待浏览器自动打开
6. 在浏览器中登录钉钉账号
7. 等待页面加载完毕后，按回车键开始批量下载

## 依赖工具

本项目使用了以下第三方工具：

- [N_m3u8DL-RE](https://github.com/nilaoda/N_m3u8DL-RE)：一个跨平台的 DASH/HLS/MSS 下载工具，支持点播和直播（DASH/HLS）视频下载。
- [FFmpeg](https://ffmpeg.org/)：一个开源的音视频处理工具，支持多种格式的转换、录制和流媒体处理。

## 开发工具

本项目使用以下开发工具来确保代码质量和一致性：

### Black 代码格式化

[Black](https://black.readthedocs.io/) 是 Python 社区广泛使用的代码格式化工具。

```bash
# 安装
pip install -r requirements-dev.txt

# 格式化代码
python -m black src tests

# 检查格式
python -m black --check .
```

### Pytest 测试框架

[Pytest](https://docs.pytest.org/) 是 Python 的测试框架。

```bash
# 运行测试
pytest

# 查看覆盖率
pytest --cov=src/dingtalk_downloader
```

## 项目文档

- [开发规范](docs/development_standard.md)：项目的完整开发规范，包括命名规范、注释规范、项目结构规范等
- [开发指南](docs/development_guide.md)：开发流程、工具使用和代码质量要求的详细说明

## 贡献指南

我们欢迎任何形式的贡献！无论是代码、文档、问题报告还是功能建议，都非常感谢您的参与。

### 如何贡献

#### 报告问题

如果您发现了 bug 或有功能建议，请：

1. 在 [Issues](https://github.com/glacier0315/DingTalk-Live-Playback-Download-Tool/issues) 中搜索是否已有类似问题
2. 如果没有，创建新的 Issue，详细描述问题或建议
3. 提供复现步骤、错误信息和相关环境信息

#### 提交代码

1. **Fork 项目**：点击项目页面右上角的 Fork 按钮
2. **克隆到本地**：

   ```bash
   git clone https://github.com/glacier0315/DingTalk-Live-Playback-Download-Tool.git
   cd DingTalk-Live-Playback-Download-Tool
   ```

3. **创建功能分支**：

   ```bash
   git checkout -b feature/your-feature-name
   # 或修复分支
   git checkout -b fix/your-bug-fix
   ```

4. **进行开发**：
   - 遵循项目代码规范
   - 编写清晰的注释
   - 添加必要的测试
   - 确保所有测试通过
5. **提交代码**：

   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   # 或
   git commit -m "fix: 修复问题描述"
   ```

6. **推送到远程**：

   ```bash
   git push origin feature/your-feature-name
   ```

7. **创建 Pull Request**：在 GitHub 上创建 PR，详细描述您的改动

### 提交规范

我们遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式调整（不影响功能）
- `refactor:` 重构代码
- `test:` 测试相关
- `chore:` 构建/工具链相关

示例：

```bash
git commit -m "feat: 添加批量下载功能"
git commit -m "fix: 修复浏览器驱动加载失败问题"
git commit -m "docs: 更新 README 使用说明"
```

### 代码审查

提交 PR 后，请：

1. 等待维护者进行代码审查
2. 根据反馈意见进行修改
3. 确保所有 CI 检查通过
4. 保持耐心和友好的沟通态度

### 开发要求

在提交代码前，请确保：

- ✅ 代码已通过 Black 格式化检查：`python -m black --check .`
- ✅ 所有测试通过：`pytest`
- ✅ 代码符合项目开发规范
- ✅ 添加了必要的测试用例
- ✅ 更新了相关文档

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。
