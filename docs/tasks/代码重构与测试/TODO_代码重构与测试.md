# TODO_代码重构与测试

## 一、待办事项

### 1.1 测试修复

#### 1.1.1 修复 Mock 装饰器使用方式

**问题描述**：
- `@patch` 装饰器的参数传递方式不正确
- 导致测试用例无法正常运行

**修复方法**：
1. 修正 `test_validator.py` 中的 Mock 装饰器使用方式
2. 修正 `test_cookie_handler.py` 中的 Mock 装饰器使用方式
3. 修正 `test_downloader.py` 中的 Mock 装饰器使用方式
4. 修正 `test_download_flow.py` 中的 Mock 装饰器使用方式

**示例**：
```python
# 错误示例
@patch('builtins.input', side_effect=['1'])
def test_validate_input_valid_option():
    pass

# 正确示例
@patch('builtins.input')
def test_validate_input_valid_option(mock_input):
    mock_input.return_value = '1'
    pass
```

**优先级**：高

**预计时间**：2 小时

#### 1.1.2 补充缺失的导入

**问题描述**：
- `test_file_reader.py` 缺少 `tempfile` 导入
- 导致测试用例无法正常运行

**修复方法**：
1. 在 `test_file_reader.py` 中添加 `import tempfile`
2. 验证所有测试文件的导入是否完整

**示例**：
```python
# 添加导入
import tempfile
```

**优先级**：高

**预计时间**：0.5 小时

#### 1.1.3 优化模块间的相对导入

**问题描述**：
- 模块间的相对导入需要进一步优化
- 部分导入路径不够清晰

**修复方法**：
1. 检查所有模块的导入语句
2. 优化相对导入路径
3. 确保导入路径清晰一致

**优先级**：中

**预计时间**：1 小时

#### 1.1.4 完善测试用例的 Mock 设置

**问题描述**：
- 部分测试用例的 Mock 设置不完善
- 导致测试用例无法正常运行

**修复方法**：
1. 完善 `test_cookie_handler.py` 的 Mock 设置
2. 完善 `test_m3u8_parser.py` 的 Mock 设置
3. 完善 `test_downloader.py` 的 Mock 设置
4. 完善 `test_download_flow.py` 的 Mock 设置

**优先级**：高

**预计时间**：3 小时

### 1.2 提高测试覆盖率

#### 1.2.1 提高核心模块覆盖率

**问题描述**：
- `core/downloader.py` 覆盖率：35%
- `core/cookie_handler.py` 覆盖率：66%
- `core/m3u8_parser.py` 覆盖率：65%

**改进方法**：
1. 为 `core/downloader.py` 添加更多测试用例
2. 为 `core/cookie_handler.py` 添加更多测试用例
3. 为 `core/m3u8_parser.py` 添加更多测试用例
4. 覆盖更多边界条件和异常情况

**优先级**：高

**预计时间**：4 小时

#### 1.2.2 提高工具模块覆盖率

**问题描述**：
- `utils/file_reader.py` 覆盖率：36%
- `utils/validator.py` 覆盖率：22%

**改进方法**：
1. 为 `utils/file_reader.py` 添加更多测试用例
2. 为 `utils/validator.py` 添加更多测试用例
3. 覆盖更多边界条件和异常情况

**优先级**：中

**预计时间**：2 小时

#### 1.2.3 提高浏览器模块覆盖率

**问题描述**：
- `browser/chrome_driver.py` 覆盖率：34%
- `browser/firefox_driver.py` 覆盖率：33%

**改进方法**：
1. 为 `browser/chrome_driver.py` 添加更多测试用例
2. 为 `browser/firefox_driver.py` 添加更多测试用例
3. 覆盖更多边界条件和异常情况

**优先级**：中

**预计时间**：2 小时

#### 1.2.4 提高二进制模块覆盖率

**问题描述**：
- `binary/n_m3u8dl_re.py` 覆盖率：22%
- `binary/ffmpeg_wrapper.py` 覆盖率：27%

**改进方法**：
1. 为 `binary/n_m3u8dl_re.py` 添加更多测试用例
2. 为 `binary/ffmpeg_wrapper.py` 添加更多测试用例
3. 覆盖更多边界条件和异常情况

**优先级**：中

**预计时间**：2 小时

### 1.3 代码质量验证

#### 1.3.1 运行 black 格式化检查

**问题描述**：
- 未运行 black 格式化检查
- 代码格式可能不符合规范

**执行方法**：
```bash
black src/ tests/
```

**优先级**：中

**预计时间**：0.5 小时

#### 1.3.2 运行 flake8 代码检查

**问题描述**：
- 未运行 flake8 代码检查
- 代码可能存在 PEP 8 规范问题

**执行方法**：
```bash
flake8 src/ tests/
```

**优先级**：中

**预计时间**：0.5 小时

#### 1.3.3 运行 mypy 类型检查

**问题描述**：
- 未运行 mypy 类型检查
- 代码可能存在类型问题

**执行方法**：
```bash
mypy src/
```

**优先级**：中

**预计时间**：0.5 小时

#### 1.3.4 修复所有代码质量问题

**问题描述**：
- 可能存在代码质量问题
- 需要修复

**修复方法**：
1. 根据 black 检查结果修复格式问题
2. 根据 flake8 检查结果修复规范问题
3. 根据 mypy 检查结果修复类型问题

**优先级**：高

**预计时间**：2 小时

### 1.4 文档更新

#### 1.4.1 验证并更新开发规范文档

**问题描述**：
- 未验证重构后的代码是否符合开发规范
- 需要更新规范示例

**更新方法**：
1. 验证重构后的代码是否符合开发规范
2. 更新命名规范示例
3. 更新注释规范示例
4. 更新项目结构规范

**优先级**：中

**预计时间**：1 小时

#### 1.4.2 编写 API 文档

**问题描述**：
- 未编写 API 文档
- 需要编写

**编写方法**：
1. 创建 `docs/api/api_reference.md`
2. 文档包含所有公共接口
3. 文档包含模块说明
4. 文档包含类说明
5. 文档包含函数说明
6. 文档包含参数说明
7. 文档包含返回值说明
8. 文档包含异常说明
9. 文档格式统一

**优先级**：中

**预计时间**：3 小时

#### 1.4.3 编写开发者指南

**问题描述**：
- 未编写开发者指南
- 需要编写

**编写方法**：
1. 创建 `docs/developer_guide.md`
2. 指南包含项目结构说明
3. 指南包含开发环境搭建
4. 指南包含开发流程
5. 指南包含测试流程
6. 指南包含代码规范
7. 指南包含提交规范
8. 指南易于理解

**优先级**：中

**预计时间**：2 小时

#### 1.4.4 更新 README.md

**问题描述**：
- 未更新 README.md
- 需要更新

**更新方法**：
1. 更新项目简介
2. 更新功能特性
3. 更新安装说明
4. 更新使用指南
5. 更新项目结构
6. 更新开发指南
7. 更新常见问题
8. 反映重构后的结构

**优先级**：中

**预计时间**：1 小时

### 1.5 持续集成

#### 1.5.1 配置 CI/CD 流程

**问题描述**：
- 未配置 CI/CD 流程
- 需要配置

**配置方法**：
1. 创建 `.github/workflows/test.yml`
2. 配置自动运行测试
3. 配置自动生成覆盖率报告
4. 配置自动检查代码质量

**优先级**：低

**预计时间**：2 小时

#### 1.5.2 配置自动化测试

**问题描述**：
- 未配置自动化测试
- 需要配置

**配置方法**：
1. 配置 GitHub Actions
2. 配置测试触发条件
3. 配置测试报告生成
4. 配置覆盖率报告生成

**优先级**：低

**预计时间**：1 小时

## 二、缺少的配置

### 2.1 测试配置

#### 2.1.1 pytest 配置文件

**问题描述**：
- 缺少 `pytest.ini` 或 `pyproject.toml` 中的 pytest 配置
- 需要添加

**添加方法**：
1. 创建 `pytest.ini` 文件
2. 配置 pytest 参数
3. 配置 pytest 插件
4. 配置 pytest 覆盖率

**示例**：
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --cov=src/dingtalk_downloader --cov-report=html --cov-report=term
```

**优先级**：中

**预计时间**：0.5 小时

#### 2.1.2 测试夹具（fixtures）

**问题描述**：
- 缺少测试夹具（fixtures）
- 需要添加

**添加方法**：
1. 创建 `tests/conftest.py`
2. 添加公共测试夹具
3. 添加 Mock 浏览器夹具
4. 添加 Mock 配置夹具

**示例**：
```python
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_browser():
    browser = Mock()
    browser.get_cookies.return_value = [{'name': 'test', 'value': 'value'}]
    browser.get_user_agent.return_value = 'Mozilla/5.0'
    browser.get_referer.return_value = 'https://n.dingtalk.com/'
    return browser
```

**优先级**：中

**预计时间**：1 小时

### 2.2 代码质量配置

#### 2.2.1 black 配置文件

**问题描述**：
- 缺少 `pyproject.toml` 中的 black 配置
- 需要添加

**添加方法**：
1. 在 `pyproject.toml` 中添加 black 配置
2. 配置 black 参数
3. 配置 black 目标版本

**示例**：
```toml
[tool.black]
line-length = 100
target-version = ['py38']
include = '\.pyi?$'
exclude = '''
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

**优先级**：中

**预计时间**：0.5 小时

#### 2.2.2 flake8 配置文件

**问题描述**：
- 缺少 `.flake8` 或 `pyproject.toml` 中的 flake8 配置
- 需要添加

**添加方法**：
1. 创建 `.flake8` 文件
2. 配置 flake8 参数
3. 配置 flake8 忽略规则

**示例**：
```ini
[flake8]
max-line-length = 100
exclude = .git,__pycache__,docs,old,build,dist
ignore = E203, E266, E501, W503
```

**优先级**：中

**预计时间**：0.5 小时

#### 2.2.3 mypy 配置文件

**问题描述**：
- 缺少 `mypy.ini` 或 `pyproject.toml` 中的 mypy 配置
- 需要添加

**添加方法**：
1. 在 `pyproject.toml` 中添加 mypy 配置
2. 配置 mypy 参数
3. 配置 mypy 忽略规则

**示例**：
```toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
ignore_missing_imports = true
```

**优先级**：中

**预计时间**：0.5 小时

### 2.3 文档配置

#### 2.3.1 Sphinx 配置

**问题描述**：
- 缺少 Sphinx 配置
- 需要添加（可选）

**添加方法**：
1. 创建 `docs/conf.py`
2. 配置 Sphinx 参数
3. 配置 Sphinx 扩展

**优先级**：低

**预计时间**：2 小时

## 三、有用的操作指引

### 3.1 运行测试

#### 3.1.1 运行所有测试

**命令**：
```bash
python -m pytest tests/ -v
```

**说明**：
- 运行所有测试
- 显示详细输出

#### 3.1.2 运行单个测试文件

**命令**：
```bash
python -m pytest tests/unit/test_path_helper.py -v
```

**说明**：
- 运行单个测试文件
- 显示详细输出

#### 3.1.3 运行单个测试用例

**命令**：
```bash
python -m pytest tests/unit/test_path_helper.py::test_clean_file_path_normal -v
```

**说明**：
- 运行单个测试用例
- 显示详细输出

#### 3.1.4 运行测试并生成覆盖率报告

**命令**：
```bash
python -m pytest tests/ --cov=src/dingtalk_downloader --cov-report=html --cov-report=term
```

**说明**：
- 运行所有测试
- 生成 HTML 格式的覆盖率报告
- 生成终端格式的覆盖率报告

### 3.2 代码质量检查

#### 3.2.1 运行 black 格式化

**命令**：
```bash
black src/ tests/
```

**说明**：
- 格式化代码
- 自动修复格式问题

#### 3.2.2 检查 black 格式

**命令**：
```bash
black --check src/ tests/
```

**说明**：
- 检查代码格式
- 不修改代码

#### 3.2.3 运行 flake8 检查

**命令**：
```bash
flake8 src/ tests/
```

**说明**：
- 检查代码规范
- 显示规范问题

#### 3.2.4 运行 mypy 类型检查

**命令**：
```bash
mypy src/
```

**说明**：
- 检查类型
- 显示类型问题

### 3.3 运行程序

#### 3.3.1 运行主程序

**命令**：
```bash
python -m dingtalk_downloader
```

**说明**：
- 运行主程序
- 交互式输入

#### 3.3.2 运行主程序（开发模式）

**命令**：
```bash
python src/dingtalk_downloader/main.py
```

**说明**：
- 运行主程序
- 交互式输入

### 3.4 安装依赖

#### 3.4.1 安装生产依赖

**命令**：
```bash
pip install -r requirements.txt
```

**说明**：
- 安装生产环境依赖

#### 3.4.2 安装开发依赖

**命令**：
```bash
pip install -r requirements-dev.txt
```

**说明**：
- 安装开发环境依赖

### 3.5 查看覆盖率报告

#### 3.5.1 在浏览器中查看

**方法**：
1. 打开 `htmlcov/index.html` 文件
2. 在浏览器中查看覆盖率报告

**说明**：
- 可视化覆盖率报告
- 查看每个模块的覆盖率

#### 3.5.2 在终端中查看

**命令**：
```bash
python -m pytest tests/ --cov=src/dingtalk_downloader --cov-report=term
```

**说明**：
- 在终端中查看覆盖率统计
- 查看每个模块的覆盖率

## 四、总结

### 4.1 优先级排序

**高优先级**：
1. 修复 Mock 装饰器使用方式
2. 补充缺失的导入
3. 完善测试用例的 Mock 设置
4. 提高核心模块覆盖率
5. 修复所有代码质量问题

**中优先级**：
1. 优化模块间的相对导入
2. 提高工具模块覆盖率
3. 提高浏览器模块覆盖率
4. 提高二进制模块覆盖率
5. 运行 black 格式化检查
6. 运行 flake8 代码检查
7. 运行 mypy 类型检查
8. 验证并更新开发规范文档
9. 编写 API 文档
10. 编写开发者指南
11. 更新 README.md
12. 配置 pytest 配置文件
13. 配置测试夹具
14. 配置 black 配置文件
15. 配置 flake8 配置文件
16. 配置 mypy 配置文件

**低优先级**：
1. 配置 CI/CD 流程
2. 配置自动化测试
3. 配置 Sphinx 配置

### 4.2 预计总时间

**高优先级**：13 小时
**中优先级**：16 小时
**低优先级**：4 小时
**总计**：33 小时

### 4.3 后续建议

1. **优先完成高优先级任务**：
   - 修复测试用例
   - 提高测试覆盖率
   - 修复代码质量问题

2. **逐步完成中优先级任务**：
   - 完善文档
   - 配置工具
   - 优化代码

3. **考虑完成低优先级任务**：
   - 配置 CI/CD
   - 自动化测试
   - 生成 API 文档
