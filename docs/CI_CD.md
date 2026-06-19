# GitHub Actions CI/CD 配置

本项目已配置完整的 CI/CD 流程，使用 GitHub Actions 实现自动化测试、代码质量检查和发布。

## 📋 目录

- [工作流程概览](#工作流程概览)
- [触发条件](#触发条件)
- [质量门禁](#质量门禁)
- [本地开发](#本地开发)
- [配置说明](#配置说明)
- [故障排除](#故障排除)

---

## 工作流程概览

### 1. CI 工作流 (`.github/workflows/ci.yml`)

**主要功能：**

- ✅ 跨平台测试（Ubuntu、Windows、macOS）
- ✅ 多版本 Python 测试（3.8、3.9、3.10、3.11）
- ✅ 测试覆盖率检查（≥80%）
- ✅ 代码格式检查（Black）
- ✅ 代码质量检查（Flake8、MyPy）
- ✅ 安全漏洞扫描（Safety、Bandit）
- ✅ 自动构建包

**执行顺序：**

```markdown
Push/PR → Test → Lint → Security → Build → Quality Gate
```

### 2. 代码质量工作流 (`.github/workflows/code-quality.yml`)

**主要功能：**

- ✅ 代码复杂度分析（Cyclomatic Complexity）
- ✅ 可维护性指数（Maintainability Index）
- ✅ 代码度量（LOC、LLOC、SLOC）
- ✅ 文档完整性检查
- ✅ 依赖项检查

**触发条件：**

- Push 到主分支
- Pull Request
- 每天定时运行（UTC 2:00 AM）

### 3. 发布工作流 (`.github/workflows/release.yml`)

**主要功能：**

- ✅ 自动构建发布包
- ✅ 自动发布到 PyPI
- ✅ 创建 GitHub Release 资产

**触发条件：**

- 创建 GitHub Release 时自动触发

---

## 触发条件

### 自动触发

| 事件              | 分支                  | 工作流               |
| ----------------- | --------------------- | -------------------- |
| Push              | main, master, develop | CI, Code Quality     |
| Pull Request      | main, master, develop | CI, Code Quality     |
| Release (created) | -                     | Release              |
| Schedule          | -                     | Code Quality (daily) |

### 手动触发

在 GitHub 仓库页面：

1. 点击 **Actions** 标签
2. 选择对应的工作流
3. 点击 **Run workflow**

---

## 质量门禁

### 必须通过的检查

所有 Pull Request 必须通过以下检查才能合并：

1. **测试检查** ✅
   - 所有测试用例通过
   - 测试覆盖率 ≥ 80%

2. **代码风格检查** ✅
   - Black 格式检查通过
   - Flake8 无语法错误

3. **安全检查** ✅
   - 无已知安全漏洞
   - 无敏感信息泄露

### 覆盖率要求

- **最低要求：** 80%
- **当前覆盖率：** 92.48%
- **覆盖率报告：**
  - HTML 报告：`htmlcov/index.html`
  - XML 报告：`coverage.xml`

---

## 本地开发

### 快速开始

```bash
# 安装开发依赖
make install-dev

# 运行测试
make test

# 运行代码检查
make lint

# 格式化代码
make format

# 运行安全检查
make security

# 清理生成文件
make clean
```

### 完整检查流程

```bash
# 模拟 CI 流程
make ci

# 或者分步执行
make lint      # 代码风格检查
make test      # 运行测试
make security  # 安全检查
```

---

## 配置说明

### 1. 代码风格配置

#### Black (`.black` 配置在 `pyproject.toml`)

- 行长度：100 字符
- 目标版本：Python 3.8+

#### Flake8 (`.flake8`)

- 行长度：100 字符
- 最大复杂度：10
- 忽略规则：E203, W503, W504, D100-D104

#### MyPy (`mypy.ini`)

- 目标版本：Python 3.8
- 忽略第三方库缺失导入

### 2. 测试配置

#### Pytest (`pytest.ini`)

- 测试目录：`tests/`
- 最小覆盖率：80%
- 输出格式：详细报告

---

## 故障排除

### 常见问题

#### 1. 测试覆盖率不足

**问题：** 覆盖率低于 80%，CI 失败

**解决方案：**

```bash
# 查看覆盖率报告
pytest tests/ --cov=src/dingtalk_downloader --cov-report=html

# 打开 HTML 报告
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux

# 添加缺失的测试
```

#### 2. Black 格式检查失败

**问题：** Black 检查失败

**解决方案：**

```bash
# 自动格式化代码
black src/ tests/

# 或者使用 Makefile
make format
```

#### 3. Flake8 报错

**问题：** Flake8 发现代码质量问题

**解决方案：**

```bash
# 查看 Flake8 错误
flake8 src/ tests/ --count --statistics

# 常见错误修复：
# E501: 行太长 - 拆分长行
# F401: 导入未使用 - 删除未使用的导入
# F841: 变量未使用 - 删除或使用该变量
```

#### 4. MyPy 类型检查失败

**问题：** MyPy 发现类型错误

**解决方案：**

```bash
# 查看类型错误
mypy src/ --ignore-missing-imports

# 添加类型注解
# 或在特定行添加 # type: ignore
```

#### 5. 安全漏洞警告

**问题：** Safety 或 Bandit 发现安全问题

**解决方案：**

```bash
# 查看详细报告
safety check --full-report
bandit -r src/ -ll

# 更新依赖版本
pip install --upgrade <package>

# 或在 requirements.txt 中指定安全版本
```

### CI 调试

#### 本地模拟 CI 环境

```bash
# 使用 Makefile
make ci

# 或手动执行步骤
pip install -r requirements.txt -r requirements-dev.txt
black --check src/ tests/
flake8 src/ tests/
pytest tests/ --cov=src/dingtalk_downloader --cov-fail-under=80
```

#### 查看 CI 日志

1. 在 GitHub 仓库页面点击 **Actions** 标签
2. 选择失败的 workflow run
3. 展开各个步骤查看详细日志
4. 下载 artifacts（如覆盖率报告）

---

## 徽章

在 README.md 中添加 CI 徽章：

```markdown
[![CI](https://github.com/yourusername/DingTalk-Live-Playback-Download-Tool/workflows/CI/badge.svg)](https://github.com/yourusername/DingTalk-Live-Playback-Download-Tool/actions)
[![Coverage](https://codecov.io/gh/yourusername/DingTalk-Live-Playback-Download-Tool/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/DingTalk-Live-Playback-Download-Tool)
[![Code Quality](https://img.shields.io/badge/code%20quality-A-brightgreen.svg)](https://github.com/yourusername/DingTalk-Live-Playback-Download-Tool/actions)
```

---

## 最佳实践

### 1. 提交前检查清单

- [ ] 运行 `make lint` 确保代码风格正确
- [ ] 运行 `make test` 确保所有测试通过
- [ ] 运行 `make security` 确保无安全漏洞
- [ ] 更新文档和 CHANGELOG
- [ ] 添加必要的测试用例

### 2. Pull Request 流程

1. 创建功能分支
2. 进行开发
3. 运行本地 CI 检查
4. 提交 Pull Request
5. 等待 CI 通过
6. 代码审查
7. 合并到主分支

### 3. 保持 CI 高效

- 使用缓存加速依赖安装
- 并行运行测试
- 使用 matrix 策略测试多平台
- 合理设置超时时间

---

## 相关链接

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Pytest 文档](https://docs.pytest.org/)
- [Black 文档](https://black.readthedocs.io/)
- [Flake8 文档](https://flake8.pycqa.org/)
- [MyPy 文档](https://mypy.readthedocs.io/)

---

## 支持

如有问题，请：

1. 查看本文档的故障排除部分
2. 查看项目的 Issues
3. 创建新的 Issue 描述问题

**维护者：** 项目团队
**最后更新：** 2026-02-18
