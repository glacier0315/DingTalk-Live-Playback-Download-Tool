# Black 集成待办事项清单

## 概述

本文档列出了 Black 集成项目完成后的待办事项、缺少的配置和需要改进的地方，方便后续跟进和处理。

## 待办事项

### 高优先级

#### 1. 修复现有测试失败

**问题描述**：项目中有 6 个测试失败和 1 个错误，与 Black 格式化无关，是项目原有的测试问题。

**失败测试**：

- tests/integration/test_download_flow.py::test_single_download_flow
- tests/integration/test_download_flow.py::test_batch_download_flow
- tests/unit/test_cookie_handler.py::test_cookie_handler_get_cookie
- tests/unit/test_cookie_handler.py::test_cookie_handler_close
- tests/unit/test_downloader.py::test_downloader_close
- tests/unit/test_file_reader.py::test_file_reader_csv

**错误测试**：

- tests/unit/test_file_reader.py::test_file_reader_excel

**操作指引**：

1. 运行测试：`python -m pytest -v`
2. 查看详细的错误信息
3. 根据错误信息修复测试代码
4. 确保所有测试通过

**相关文件**：

- [tests/integration/test_download_flow.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/tests/integration/test_download_flow.py)
- [tests/unit/test_cookie_handler.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/tests/unit/test_cookie_handler.py)
- [tests/unit/test_downloader.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/tests/unit/test_downloader.py)
- [tests/unit/test_file_reader.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/tests/unit/test_file_reader.py)

#### 2. 提高测试覆盖率

**问题描述**：当前测试覆盖率为 49%，需要提高到 80% 以上。

**当前覆盖率**：

- 总覆盖率：49%
- 最低覆盖率模块：
  - src/dingtalk_downloader/main.py：17%
  - src/dingtalk_downloader/binary/n_m3u8dl_re.py：22%
  - src/dingtalk_downloader/binary/ffmpeg_wrapper.py：27%
  - src/dingtalk_downloader/config/settings.py：28%

**操作指引**：

1. 运行覆盖率测试：`python -m pytest --cov=src/dingtalk_downloader --cov-report=html`
2. 查看覆盖率报告：打开 `htmlcov/index.html`
3. 为覆盖率低的模块添加单元测试
4. 目标覆盖率：80% 以上

**相关文件**：

- [src/dingtalk_downloader/main.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/main.py)
- [src/dingtalk_downloader/binary/n_m3u8dl_re.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/binary/n_m3u8dl_re.py)
- [src/dingtalk_downloader/binary/ffmpeg_wrapper.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/binary/ffmpeg_wrapper.py)
- [src/dingtalk_downloader/config/settings.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/config/settings.py)

### 中优先级

#### 3. 配置 IDE 自动格式化

**问题描述**：为了提高开发效率，建议配置 IDE 自动格式化功能。

**操作指引**：

**VS Code**：

1. 安装 "Black Formatter" 扩展
2. 在 settings.json 中添加以下配置：
   ```json
   {
     "editor.formatOnSave": true,
     "editor.defaultFormatter": "ms-python.black-formatter",
     "python.formatting.provider": "none"
   }
   ```

**PyCharm**：

1. 打开 Settings > Tools > External Tools
2. 添加 Black 工具：
   - Name: Black
   - Program: python
   - Arguments: -m black $FilePath$
3. 配置自动格式化：Settings > Tools > Actions on Save > Reformat code

**Vim/Neovim**：

1. 安装 black 插件：`Plug 'psf/black', { 'branch': 'stable' }`
2. 在 .vimrc 中添加：
   ```vim
   autocmd BufWritePre *.py execute ':Black'
   ```

#### 4. 添加 Git 提交前检查脚本

**问题描述**：虽然不配置 pre-commit 钩子，但可以提供一个提交前检查脚本供开发者使用。

**操作指引**：

1. 创建 `scripts/pre-commit-check.sh` 脚本：

   ```bash
   #!/bin/bash
   echo "运行 Black 格式化检查..."
   python -m black --check .
   if [ $? -ne 0 ]; then
       echo "❌ 代码格式检查失败，请运行 'python -m black .' 格式化代码"
       exit 1
   fi

   echo "运行测试..."
   python -m pytest
   if [ $? -ne 0 ]; then
       echo "❌ 测试失败，请修复测试后再提交"
       exit 1
   fi

   echo "✅ 所有检查通过，可以提交代码"
   exit 0
   ```

2. 在提交代码前运行：`bash scripts/pre-commit-check.sh`

**相关文件**：

- 创建新文件：[scripts/pre-commit-check.sh](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/scripts/pre-commit-check.sh)

### 低优先级

#### 5. 添加代码质量检查工具

**问题描述**：除了 Black，还可以集成其他代码质量检查工具，如 MyPy、Pylint 等。

**操作指引**：

**MyPy（类型检查）**：

1. 安装：`pip install mypy`
2. 运行：`mypy src/dingtalk_downloader`
3. 在 pyproject.toml 中添加配置：
   ```toml
   [tool.mypy]
   python_version = "3.8"
   warn_return_any = true
   warn_unused_configs = true
   disallow_untyped_defs = true
   ```

**Pylint（代码检查）**：

1. 安装：`pip install pylint`
2. 运行：`pylint src/dingtalk_downloader`
3. 创建 .pylintrc 配置文件

**相关文件**：

- [pyproject.toml](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/pyproject.toml)

#### 6. 添加更多使用示例

**问题描述**：在文档中添加更多的 Black 使用示例和最佳实践。

**操作指引**：

1. 在 [docs/development_guide.md](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/docs/development_guide.md) 中添加：
   - Black 高级用法示例
   - 常见问题和解决方案
   - 最佳实践和技巧
2. 添加实际项目的格式化前后对比示例

## 缺少的配置

### 1. CI/CD 配置

**状态**：根据用户要求，不配置 CI/CD 流程。

**说明**：如果将来需要配置 CI/CD，可以参考以下配置：

**GitHub Actions 示例**：

```yaml
name: Code Quality Check

on: [push, pull_request]

jobs:
  black-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: "3.8"
      - run: pip install black
      - run: black --check .
```

**相关文件**：

- 创建新文件：`.github/workflows/black-check.yml`

### 2. Pre-commit 钩子配置

**状态**：根据用户要求，不配置 Pre-commit 钩子。

**说明**：如果将来需要配置 Pre-commit 钩子，可以参考以下配置：

**.pre-commit-config.yaml 示例**：

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.8
```

**安装命令**：

```bash
pip install pre-commit
pre-commit install
```

**相关文件**：

- 创建新文件：`.pre-commit-config.yaml`

## 需要改进的地方

### 1. 文档改进

**改进点**：

1. 添加更多的代码示例和实际使用场景
2. 添加视频教程或截图说明
3. 添加 FAQ（常见问题解答）
4. 添加故障排除指南

**相关文件**：

- [docs/development_guide.md](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/docs/development_guide.md)
- [README.md](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/README.md)

### 2. 代码改进

**改进点**：

1. 为所有模块添加完整的文档字符串
2. 为所有公共函数添加类型注解
3. 改进错误处理和日志记录
4. 添加更多的单元测试

**相关文件**：

- [src/dingtalk_downloader/](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_downloader/)

### 3. 开发流程改进

**改进点**：

1. 建立代码审查流程
2. 建立发布流程
3. 建立版本管理规范
4. 建立问题跟踪流程

## 操作指引总结

### 日常开发流程

1. **拉取最新代码**：

   ```bash
   git pull origin main
   ```

2. **创建功能分支**：

   ```bash
   git checkout -b feature/your-feature
   ```

3. **开发代码**：

   - 编写代码
   - 定期格式化：`python -m black .`
   - 定期测试：`python -m pytest`

4. **提交代码**：

   ```bash
   git add .
   git commit -m "feat: 添加新功能"
   ```

5. **提交前检查**：

   ```bash
   python -m black --check .
   python -m pytest
   ```

6. **推送代码**：
   ```bash
   git push origin feature/your-feature
   ```

### 常用命令

**格式化相关**：

- 格式化整个项目：`python -m black .`
- 检查代码格式：`python -m black --check .`
- 查看格式化差异：`python -m black --diff .`

**测试相关**：

- 运行所有测试：`python -m pytest`
- 运行指定测试文件：`python -m pytest tests/unit/test_downloader.py`
- 显示测试覆盖率：`python -m pytest --cov=src/dingtalk_downloader`

**其他工具**：

- 类型检查：`mypy src/dingtalk_downloader`
- 代码检查：`pylint src/dingtalk_downloader`

## 联系方式

如有疑问或建议，请联系项目维护者或在 Issue 中讨论。

---

**文档版本**：1.0

**最后更新**：2025-01-14

**维护者**：项目团队
