# TODO_输入验证错误修复

## 待办事项

### 1. 测试覆盖率提升

**优先级**：中

**描述**：虽然 validator.py 达到了 100% 覆盖率，但整体项目覆盖率仍需提升。

**当前状态**：
- validator.py: 100%
- main.py: 100%
- constants.py: 100%
- 其他模块: 平均 25%

**建议操作**：
1. 为其他模块编写更多测试用例
2. 重点关注核心模块（如 downloader.py、cookie_handler.py）
3. 目标：整体覆盖率提升至 80% 以上

**相关文档**：
- [测试覆盖率提升任务](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/docs/tasks/测试覆盖率提升/)

---

### 2. 异常处理增强

**优先级**：低

**描述**：考虑在其他模块中也增强异常处理。

**建议操作**：
1. 审查其他模块的异常处理逻辑
2. 为关键模块添加异常处理
3. 确保异常信息友好且有用

**相关模块**：
- downloader.py
- cookie_handler.py
- file_reader.py

---

### 3. 日志记录优化

**优先级**：低

**描述**：在异常处理中添加更详细的日志记录。

**建议操作**：
1. 在 validate_input 的异常处理中添加日志记录
2. 记录异常类型、异常信息、上下文信息
3. 便于问题排查和调试

**示例**：
```python
except EOFError:
    logger.warning("输入流结束，使用默认选项: %s", default_option)
    print(f"\n输入流结束，使用默认选项: {default_option}")
    return default_option
```

---

### 4. 用户输入验证增强

**优先级**：低

**描述**：考虑增强用户输入验证功能。

**建议操作**：
1. 支持输入去除前后空格
2. 支持大小写不敏感的选项
3. 支持选项别名（如 "y"/"yes"）

**示例**：
```python
choice = input(prompt).strip().lower()
```

---

## 缺少的配置

### 1. 环境变量配置

**优先级**：低

**描述**：项目没有使用 .env 文件管理配置。

**当前状态**：
- 项目中没有 .env 文件
- 没有使用环境变量管理敏感信息

**建议操作**：
1. 创建 .env.example 文件作为模板
2. 使用 python-dotenv 库加载环境变量
3. 将敏感信息（如 API Key）移至 .env 文件
4. 将 .env 添加到 .gitignore

**示例**：
```bash
# .env.example
LOG_LEVEL=INFO
DOWNLOAD_DIR=./downloads
```

---

### 2. 日志配置

**优先级**：低

**描述**：日志配置可以更加灵活。

**当前状态**：
- 日志配置硬编码在 logger_config.py 中
- 不支持通过环境变量或配置文件调整

**建议操作**：
1. 支持通过环境变量配置日志级别
2. 支持通过配置文件配置日志输出格式
3. 支持日志文件轮转配置

---

### 3. 测试配置

**优先级**：低

**描述**：测试配置可以更加完善。

**当前状态**：
- pytest.ini 存在但配置简单
- 没有使用测试覆盖率配置文件

**建议操作**：
1. 完善 pytest.ini 配置
2. 添加 .coveragerc 配置文件
3. 配置测试覆盖率阈值

**示例**：
```ini
# .coveragerc
[run]
omit =
    */tests/*
    */venv/*

[report]
fail_under = 80
```

---

## 操作指引

### 1. 如何提升测试覆盖率

**步骤**：
1. 运行测试并生成覆盖率报告：
   ```bash
   pytest --cov=src --cov-report=html
   ```
2. 打开 htmlcov/index.html 查看覆盖率报告
3. 识别覆盖率低的模块
4. 为这些模块编写测试用例
5. 重复步骤 1-4，直到达到目标覆盖率

**相关命令**：
- 运行所有测试：`pytest`
- 运行特定模块测试：`pytest tests/unit/test_validator.py`
- 生成覆盖率报告：`pytest --cov=src --cov-report=html`

---

### 2. 如何配置环境变量

**步骤**：
1. 安装 python-dotenv：
   ```bash
   pip install python-dotenv
   ```
2. 创建 .env 文件：
   ```bash
   # .env
   LOG_LEVEL=INFO
   DOWNLOAD_DIR=./downloads
   ```
3. 在代码中加载环境变量：
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```
4. 使用环境变量：
   ```python
   import os
   log_level = os.getenv("LOG_LEVEL", "INFO")
   ```

**相关文档**：
- python-dotenv 官方文档：https://pypi.org/project/python-dotenv/

---

### 3. 如何配置测试覆盖率

**步骤**：
1. 创建 .coveragerc 文件：
   ```ini
   [run]
   omit =
       */tests/*
       */venv/*

   [report]
   fail_under = 80
   ```
2. 运行测试并检查覆盖率：
   ```bash
   pytest --cov=src --cov-report=term-missing
   ```
3. 如果覆盖率低于阈值，测试将失败

**相关命令**：
- 生成终端覆盖率报告：`pytest --cov=src --cov-report=term-missing`
- 生成 HTML 覆盖率报告：`pytest --cov=src --cov-report=html`
- 生成 XML 覆盖率报告：`pytest --cov=src --cov-report=xml`

---

## 总结

### 已完成
- ✅ 增强 validate_input 函数的异常处理
- ✅ 新增 3 个测试用例
- ✅ 所有测试通过（21/21）
- ✅ validator.py 覆盖率达到 100%

### 待完成
- ⏳ 提升整体测试覆盖率至 80% 以上
- ⏳ 为其他模块增强异常处理
- ⏳ 优化日志记录
- ⏳ 增强用户输入验证
- ⏳ 配置环境变量管理
- ⏳ 完善测试配置

### 优先级建议
1. **高优先级**：提升测试覆盖率
2. **中优先级**：异常处理增强、日志记录优化
3. **低优先级**：用户输入验证增强、环境变量配置、测试配置

---

**最后更新时间**：2026-01-15
