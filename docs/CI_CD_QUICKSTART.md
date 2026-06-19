# CI/CD 快速设置指南

本文档帮助你快速设置和使用项目的 CI/CD 流程。

## 🚀 快速开始（5分钟）

### 1. 安装依赖

```bash
# 安装项目依赖和开发工具
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. 本地测试

```bash
# Windows 用户
scripts\run_ci_local.bat

# Linux/macOS 用户
./scripts/run_ci_local.sh

# 或使用 Makefile
make ci
```

### 3. 提交代码

```bash
git add .
git commit -m "feat: your feature"
```

---

## 📦 已配置的 CI/CD 功能

### ✅ 自动化测试

- **多平台测试：** Ubuntu, Windows, macOS
- **多版本测试：** Python 3.8, 3.9, 3.10, 3.11
- **覆盖率检查：** ≥ 80%
- **测试报告：** HTML + XML

### ✅ 代码质量检查

- **Black：** 代码格式化
- **Flake8：** 代码质量
- **MyPy：** 类型检查
- **isort：** 导入排序

### ✅ 安全检查

- **Safety：** 依赖漏洞扫描
- **Bandit：** 代码安全检查

### ✅ 代码度量

- **Radon：** 复杂度分析
- **可维护性指数**
- **代码行数统计**

---

## 🛠️ 本地开发命令

### 常用命令

```bash
# 运行所有测试
make test

# 运行特定类型测试
make test-unit
make test-integration
make test-functional

# 代码检查
make lint

# 格式化代码
make format

# 安全检查
make security

# 代码质量分析
make quality

# 清理生成文件
make clean

# 完整 CI 流程
make ci
```

### 查看所有命令

```bash
make help
```

---

## ⚙️ 配置文件说明

### 测试配置

| 文件          | 说明        |
| ------------- | ----------- |
| `pytest.ini`  | Pytest 配置 |
| `.coveragerc` | 覆盖率配置  |

### 代码质量配置

| 文件       | 说明        |
| ---------- | ----------- |
| `.flake8`  | Flake8 配置 |
| `mypy.ini` | MyPy 配置   |

### CI/CD 配置

| 文件                                 | 说明           |
| ------------------------------------ | -------------- |
| `.github/workflows/ci.yml`           | 主 CI 工作流   |
| `.github/workflows/code-quality.yml` | 代码质量工作流 |
| `.github/workflows/release.yml`      | 发布工作流     |

---

## 🎯 质量门禁要求

Pull Request 必须满足：

1. ✅ 所有测试通过
2. ✅ 覆盖率 ≥ 80%
3. ✅ Black 检查通过
4. ✅ Flake8 无语法错误
5. ✅ 无严重安全漏洞

---

## 💡 故障排除

### 测试覆盖率不足

```bash
# 查看覆盖率报告
pytest tests/ --cov=src/dingtalk_downloader --cov-report=html

# 打开报告
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
```

### Black 格式问题

```bash
# 自动修复
black src/ tests/

# 或使用 Makefile
make format
```

### Flake8 错误

```bash
# 查看详细错误
flake8 src/ tests/ --count --statistics
```

---

## 📚 更多信息

详细文档请查看：

- [完整 CI/CD 文档](./CI_CD.md)
- [开发规范](./development_standard.md)
- [开发指南](./development_guide.md)

---

**需要帮助？** 查看项目的 Issues 或创建新 Issue。
