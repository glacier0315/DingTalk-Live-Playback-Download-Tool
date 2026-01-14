# 开发指南

本文档为钉钉直播回放下载工具项目的开发指南，旨在帮助开发者快速上手项目开发，了解开发流程、工具使用和代码质量要求。

## 目录

- [一、环境搭建](#一环境搭建)
- [二、开发流程](#二开发流程)
- [三、代码质量工具](#三代码质量工具)
- [四、测试指南](#四测试指南)
- [五、常见问题](#五常见问题)

## 一、环境搭建

### 1.1 系统要求

- **操作系统**：Windows 10/11、macOS 10.14+、Linux (Ubuntu 18.04+)
- **Python 版本**：Python 3.8 或更高版本
- **浏览器**：Edge、Chrome 或 Firefox（用于获取 Cookie）

### 1.2 克隆项目

```bash
git clone https://github.com/your-username/DingTalk-Live-Playback-Download-Tool.git
cd DingTalk-Live-Playback-Download-Tool
```

### 1.3 安装依赖

#### 安装 Python 依赖

```bash
# 安装项目依赖
pip install -r requirements.txt

# 安装开发依赖（包含 Black、pytest 等工具）
pip install -r requirements-dev.txt
```

#### 安装浏览器驱动

项目使用 Selenium 自动化浏览器，需要安装对应的浏览器驱动：

- **Edge**: 自动下载（使用 EdgeDriverManager）
- **Chrome**: 自动下载（使用 ChromeDriverManager）
- **Firefox**: 自动下载（使用 GeckoDriverManager）

### 1.4 配置环境变量

创建 `.env` 文件（参考 `.env.example`）：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置必要的环境变量（如有需要）。

### 1.5 验证安装

```bash
# 运行测试验证安装
pytest

# 检查 Black 配置
python -m black --check .
```

## 二、开发流程

### 2.1 开发前准备

1. **拉取最新代码**

```bash
git pull origin main
```

2. **创建功能分支**

```bash
git checkout -b feature/your-feature-name
```

3. **运行代码格式化检查**

```bash
python -m black --check .
```

4. **运行测试**

```bash
pytest
```

### 2.2 开发过程

1. **编写代码**

   - 遵循项目开发规范（见 [development_standard.md](development_standard.md)）
   - 使用有意义的变量和函数名
   - 添加必要的注释和文档字符串

2. **定期格式化代码**

```bash
python -m black .
```

3. **定期运行测试**

```bash
pytest
```

4. **提交代码**

```bash
git add .
git commit -m "feat: 添加新功能"
```

### 2.3 提交前检查清单

在提交代码前，请确保完成以下检查：

- [ ] 代码已通过 Black 格式化检查：`python -m black --check .`
- [ ] 所有测试通过：`pytest`
- [ ] 代码符合项目开发规范
- [ ] 添加了必要的注释和文档字符串
- [ ] 提交信息符合 Git 提交信息规范

### 2.4 提交代码

```bash
# 添加所有修改
git add .

# 提交代码（使用规范的提交信息）
git commit -m "feat: 添加新功能"

# 推送到远程仓库
git push origin feature/your-feature-name
```

### 2.5 代码审查

1. **创建 Pull Request**

   - 在 GitHub 上创建 Pull Request
   - 填写 PR 模板，说明修改内容
   - 关联相关的 Issue

2. **等待审查**

   - 等待项目维护者审查代码
   - 根据反馈修改代码

3. **合并代码**

   - 审查通过后，合并代码到主分支
   - 删除功能分支

## 三、代码质量工具

### 3.1 Black 代码格式化工具

#### 3.1.1 工具介绍

Black 是 Python 社区广泛使用的代码格式化工具，具有以下特点：

- **一致性**：自动统一代码风格，消除代码风格争议
- **确定性**：相同的代码总是产生相同的格式化结果
- **自动化**：一键格式化，无需手动调整
- **标准性**：遵循 PEP 8 规范，是 Python 社区的标准工具

#### 3.1.2 安装和配置

Black 已集成到项目的开发依赖中，通过以下命令安装：

```bash
pip install -r requirements-dev.txt
```

配置文件位于项目根目录的 `pyproject.toml`，包含以下关键配置：

```toml
[tool.black]
line-length = 100                    # 行长度设置为 100 字符
target-version = ['py38']            # 目标 Python 版本为 3.8+
include = '\.pyi?$'                  # 包含 .py 和 .pyi 文件
exclude = '''                         # 排除目录和文件
/(
    \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''
```

#### 3.1.3 使用方法

##### 格式化当前文件

```bash
python -m black 文件名.py
```

##### 格式化整个项目

```bash
python -m black .
```

##### 检查代码格式（不修改文件）

```bash
python -m black --check .
```

##### 查看格式化差异（不修改文件）

```bash
python -m black --diff .
```

##### 格式化指定目录

```bash
python -m black src/
python -m black tests/
```

#### 3.1.4 开发流程集成

##### 代码提交前检查

在提交代码前，必须运行以下命令确保代码格式正确：

```bash
# 检查代码格式
python -m black --check .

# 如果检查通过，可以提交代码
git add .
git commit -m "feat: 添加新功能"
```

##### 代码格式化后提交

如果检查失败，运行以下命令格式化代码：

```bash
# 格式化代码
python -m black .

# 再次检查
python -m black --check .

# 提交代码
git add .
git commit -m "style: 格式化代码"
```

#### 3.1.5 代码格式化要求

**强制要求**：

1. **提交前必须格式化**：所有代码在提交前必须通过 Black 格式化检查
2. **不得手动调整**：格式化后的代码不得手动调整，除非有充分的理由
3. **CI/CD 检查**：代码合并前必须通过格式化检查（如果配置了 CI/CD）

**推荐实践**：

1. **定期格式化**：开发过程中定期运行格式化命令，保持代码风格一致
2. **IDE 集成**：配置 IDE 自动格式化，保存时自动运行 Black
3. **团队协作**：团队成员统一使用 Black，避免代码风格冲突

#### 3.1.6 常见问题

##### Q1: Black 格式化后的代码不符合我的习惯？

**A**: Black 的设计理念是"统一优于个人偏好"。团队统一使用 Black 可以避免代码风格争议，提高代码可读性。建议接受 Black 的格式化结果。

##### Q2: 某些代码不想被格式化怎么办？

**A**: 可以在代码中使用 `# fmt: off` 和 `# fmt: on` 注释来跳过格式化：

```python
# fmt: off
complex_dict = {
    'key1': 'value1',
    'key2': 'value2',
    # ...
}
# fmt: on
```

**注意**：这种用法应该谨慎使用，仅在必要时使用。

##### Q3: Black 改变了代码逻辑怎么办？

**A**: Black 只改变代码格式，不会改变代码逻辑。如果发现逻辑变化，请检查代码本身是否有问题。

##### Q4: 如何在 IDE 中集成 Black？

**A**: 主流 IDE 都支持 Black 集成：

- **VS Code**: 安装 "Black Formatter" 扩展，配置为默认格式化工具
- **PyCharm**: 安装 Black 插件，配置为代码格式化工具
- **Vim/Neovim**: 使用 `black` 插件或配置自动格式化

#### 3.1.7 格式化示例

##### 格式化前

```python
def calculate_total(items):
    total=0
    for item in items:
        total+=item['price']*item['quantity']
    return total
```

##### 格式化后

```python
def calculate_total(items):
    total = 0
    for item in items:
        total += item["price"] * item["quantity"]
    return total
```

主要变化：

- 运算符周围添加空格
- 单引号改为双引号
- 代码缩进和间距统一

### 3.2 Pytest 测试框架

#### 3.2.1 运行测试

```bash
# 运行所有测试
pytest

# 运行指定测试文件
pytest tests/unit/test_downloader.py

# 运行指定测试函数
pytest tests/unit/test_downloader.py::test_download_single_video

# 显示详细输出
pytest -v

# 显示测试覆盖率
pytest --cov=src/dingtalk_downloader
```

#### 3.2.2 编写测试

测试文件应放在 `tests/` 目录下，文件名以 `test_` 开头：

```python
import pytest
from dingtalk_downloader.core.downloader import Downloader

def test_download_single_video():
    """测试单个视频下载"""
    downloader = Downloader()
    result = downloader.download("https://example.com/video.m3u8")
    assert result is True
```

### 3.3 其他工具

#### 3.3.1 MyPy 类型检查

```bash
# 运行类型检查
mypy src/dingtalk_downloader
```

#### 3.3.2 Pylint 代码检查

```bash
# 运行代码检查
pylint src/dingtalk_downloader
```

## 四、测试指南

### 4.1 测试结构

```
tests/
├── unit/           # 单元测试
│   ├── test_downloader.py
│   ├── test_cookie_handler.py
│   └── test_file_reader.py
├── integration/    # 集成测试
│   └── test_download_flow.py
└── fixtures/       # 测试数据
    ├── sample_links.csv
    └── sample_links.xlsx
```

### 4.2 单元测试

单元测试用于测试单个函数或类的功能：

```python
import pytest
from dingtalk_downloader.utils.file_reader import FileReader

def test_read_csv_file():
    """测试读取 CSV 文件"""
    reader = FileReader()
    links = reader.read_csv_file("tests/fixtures/sample_links.csv")
    assert len(links) > 0
    assert isinstance(links[0], str)
```

### 4.3 集成测试

集成测试用于测试多个模块协同工作的功能：

```python
import pytest
from dingtalk_downloader.core.downloader import Downloader
from dingtalk_downloader.utils.file_reader import FileReader

def test_batch_download_flow():
    """测试批量下载流程"""
    reader = FileReader()
    links = reader.read_csv_file("tests/fixtures/sample_links.csv")
    
    downloader = Downloader()
    results = downloader.batch_download(links)
    
    assert all(results)
```

### 4.4 Mock 测试

使用 pytest-mock 进行 Mock 测试：

```python
import pytest
from unittest.mock import Mock, patch
from dingtalk_downloader.core.downloader import Downloader

def test_download_with_mock():
    """使用 Mock 测试下载功能"""
    downloader = Downloader()
    
    with patch.object(downloader, '_download_video') as mock_download:
        mock_download.return_value = True
        result = downloader.download("https://example.com/video.m3u8")
        
        assert result is True
        mock_download.assert_called_once()
```

### 4.5 测试覆盖率

运行测试并生成覆盖率报告：

```bash
# 生成覆盖率报告
pytest --cov=src/dingtalk_downloader --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

## 五、常见问题

### 5.1 Black 相关问题

#### Q1: Black 命令找不到？

**A**: 确保已安装 Black 并使用 `python -m black` 命令：

```bash
pip install -r requirements-dev.txt
python -m black --check .
```

#### Q2: Black 格式化后代码无法运行？

**A**: Black 只改变代码格式，不会改变代码逻辑。如果代码无法运行，请检查代码本身是否有问题。

#### Q3: 如何跳过某些文件的格式化？

**A**: 在 `pyproject.toml` 的 `exclude` 配置中添加要排除的文件或目录。

### 5.2 测试相关问题

#### Q1: 测试运行失败怎么办？

**A**: 按照以下步骤排查：

1. 查看错误信息，确定失败原因
2. 检查测试代码是否正确
3. 检查被测试的代码是否有问题
4. 使用 `-v` 参数查看详细输出

#### Q2: 如何调试测试？

**A**: 使用 `pdb` 或 `ipdb` 进行调试：

```python
import pytest

def test_example():
    import pdb; pdb.set_trace()
    # 测试代码
```

或者使用 pytest 的调试功能：

```bash
pytest --pdb
```

### 5.3 环境相关问题

#### Q1: 依赖安装失败怎么办？

**A**: 尝试以下解决方案：

1. 升级 pip：`pip install --upgrade pip`
2. 使用国内镜像源：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
3. 创建虚拟环境：`python -m venv venv`

#### Q2: 浏览器驱动下载失败怎么办？

**A**: 手动下载浏览器驱动：

- Edge: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/
- Chrome: https://chromedriver.chromium.org/downloads
- Firefox: https://github.com/mozilla/geckodriver/releases

### 5.4 其他问题

#### Q1: 如何贡献代码？

**A**: 按照以下步骤贡献代码：

1. Fork 项目仓库
2. 创建功能分支
3. 编写代码和测试
4. 运行 Black 格式化检查
5. 运行测试确保通过
6. 提交 Pull Request

#### Q2: 如何报告 Bug？

**A**: 在 GitHub Issues 中创建新的 Issue，包含以下信息：

- Bug 描述
- 复现步骤
- 期望行为
- 实际行为
- 环境信息（操作系统、Python 版本等）

#### Q3: 如何提出新功能建议？

**A**: 在 GitHub Issues 中创建新的 Issue，描述你的功能建议和使用场景。

## 六、资源链接

- [项目开发规范](development_standard.md)
- [Black 官方文档](https://black.readthedocs.io/)
- [Pytest 官方文档](https://docs.pytest.org/)
- [PEP 8 编码规范](https://www.python.org/dev/peps/pep-0008/)
- [Git 提交信息规范](https://www.conventionalcommits.org/)

## 七、联系方式

如有疑问或建议，请联系项目维护者或在 Issue 中讨论。
