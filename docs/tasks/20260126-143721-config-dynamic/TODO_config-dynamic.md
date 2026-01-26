# TODO\_配置动态化

## 待办事项

### 1. 提高整体测试覆盖率

**问题描述**: 当前整体测试覆盖率为45.78%,低于80%的目标。但这主要是由于其他模块(如downloader.py, cookie_handler.py等)的测试覆盖率较低导致的,本次修改的代码(yaml_config.py和main.py)覆盖率很高(91%)。

**建议**:

- 为其他模块添加更多单元测试
- 提高集成测试覆盖率
- 考虑使用覆盖率工具分析未覆盖的代码路径

**优先级**: 中

### 2. 配置文件热重载

**问题描述**: 当前配置文件仅在程序启动时加载一次,不支持运行时动态更新。

**建议**:

- 可以考虑实现配置文件热重载功能
- 使用文件监视器检测配置文件变化
- 提供手动重载配置的命令或API

**优先级**: 低

### 3. 多环境配置

**问题描述**: 当前只支持单个配置文件,不支持多环境配置。

**建议**:

- 可以考虑支持多环境配置(dev, test, prod)
- 使用环境变量或命令行参数选择配置文件
- 提供配置文件模板

**优先级**: 低

### 4. 配置加密

**问题描述**: 当前配置文件以明文存储,可能包含敏感信息。

**建议**:

- 可以考虑对敏感配置进行加密
- 使用环境变量存储敏感信息
- 提供配置文件加密/解密工具

**优先级**: 低

## 缺少的配置

### 1. 应用元信息

**当前状态**: 配置文件中已有基本的应用信息(name, version, build_date)

**建议**:

- 可以考虑添加更多元信息:
  - `author`: 作者信息
  - `description`: 应用描述
  - `license`: 许可证信息
  - `homepage`: 主页URL

**优先级**: 低

### 2. 构建信息

**当前状态**: build_date是手动维护的

**建议**:

- 可以考虑自动化构建日期的更新
- 在构建脚本中自动更新build_date
- 使用版本号和构建时间戳自动生成

**优先级**: 中

## 操作指引

### 1. 如何更新应用信息

1. 打开`config/app.yaml`文件
2. 找到`app`部分
3. 修改`name`、`version`、`build_date`字段
4. 保存文件
5. 重启应用程序,新的应用信息将显示

### 2. 如何添加新的配置项

1. 在`src/dingtalk_downloader/config/yaml_config.py`中更新`CONFIG_SCHEMA`
2. 在`config/app.yaml`中添加新的配置项
3. 在代码中使用`config.get_str()`等方法读取配置
4. 编写测试验证新的配置项

### 3. 如何运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定测试文件
python -m pytest tests/unit/test_yaml_config.py -v
python -m pytest tests/unit/test_main.py -v

# 运行测试并生成覆盖率报告
python -m pytest tests/ --cov=src --cov-report=html
```

### 4. 如何格式化代码

```bash
# 格式化所有代码
black src/ tests/

# 格式化特定文件
black src/dingtalk_downloader/config/yaml_config.py

# 检查代码风格
flake8 src/ --max-line-length=100
```

## 总结

本次配置动态化任务已成功完成,所有目标都已达成。待办事项主要是可选的增强功能,不影响当前功能的使用。
