# CONSENSUS\_配置动态化

## 明确的需求描述

将代码中硬编码的应用名称、版本和构建日期替换为从配置文件动态读取的方式。

## 验收标准

### 功能验收

- [ ] 程序启动时从配置文件读取并显示应用名称
- [ ] 程序启动时从配置文件读取并显示版本号
- [ ] 程序启动时从配置文件读取并显示构建日期
- [ ] 配置文件不存在时提供友好的错误提示
- [ ] 配置文件格式错误时提供友好的错误提示
- [ ] 配置项缺失时提供友好的错误提示

### 代码质量验收

- [ ] 代码符合项目编码规范(PEP 8, Black格式化)
- [ ] 代码有完整的类型注解
- [ ] 代码有适当的错误处理
- [ ] 代码有适当的日志记录

### 测试验收

- [ ] 单元测试覆盖配置读取功能
- [ ] 集成测试验证程序启动显示
- [ ] 所有测试通过
- [ ] 测试覆盖率不低于80%

## 技术实现方案

### 1. 更新 CONFIG_SCHEMA

在 `src/dingtalk_downloader/config/yaml_config.py` 中,更新 `CONFIG_SCHEMA` 的 `app` 部分,添加 `build_date` 字段验证:

```python
CONFIG_SCHEMA = {
    "app": {
        "required": True,
        "type": dict,
        "fields": {
            "name": {"required": True, "type": str},
            "version": {"required": True, "type": str},
            "build_date": {"required": True, "type": str},  # 新增
        },
    },
    # ... 其他配置
}
```

### 2. 修改 main.py

在 `src/dingtalk_downloader/main.py` 中,修改 `main()` 函数,从配置文件读取应用信息并显示:

```python
def main() -> None:
    """
    主程序入口。

    显示欢迎信息,获取用户输入的下载模式,调用相应的下载函数。

    Raises:
        ConfigLoadError: 配置文件加载失败
        ConfigValidationError: 配置文件验证失败
    """
    from .config.yaml_config import YamlConfig, ConfigLoadError, ConfigValidationError

    LoggerConfig.setup_logging()

    try:
        config = YamlConfig.get_instance()
        config.load()

        app_name = config.get_str("app.name")
        app_version = config.get_str("app.version")
        build_date = config.get_str("app.build_date")

        print("=" * 47)
        print(f"     欢迎使用{app_name} v{app_version}")
        print(f"         构建日期:{build_date}")
        print("=" * 47)

        logger.info("程序启动")

        # ... 其他代码

    except ConfigLoadError as e:
        logger.error(f"配置加载失败: {e}")
        print(f"错误: 配置文件加载失败 - {e}")
        sys.exit(1)
    except ConfigValidationError as e:
        logger.error(f"配置验证失败: {e}")
        print(f"错误: 配置文件验证失败 - {e}")
        sys.exit(1)
```

### 3. 更新测试

在 `tests/unit/test_yaml_config.py` 中,更新 `get_full_test_config()` 函数,添加 `build_date` 字段:

```python
def get_full_test_config():
    """获取完整的测试配置"""
    return {
        "app": {"name": "test_app", "version": "1.0.0", "build_date": "2026年01月26日"},
        # ... 其他配置
    }
```

在 `tests/unit/test_main.py` 中,添加测试验证配置读取功能:

```python
def test_main_config_loading():
    """测试主程序入口 - 配置加载"""
    with patch("builtins.input") as mock_input, patch(
        "dingtalk_downloader.main.YamlConfig"
    ) as mock_yaml_config_class, patch("builtins.print") as mock_print:

        mock_input.side_effect = [""]  # 直接回车,默认选择单个视频下载模式

        mock_config = Mock()
        mock_config.get_str.side_effect = [
            "钉钉直播回放下载工具",
            "1.5.0",
            "2026年01月26日",
        ]
        mock_yaml_config_class.get_instance.return_value = mock_config

        main()

        # 验证配置加载
        mock_yaml_config_class.get_instance.assert_called_once()
        mock_config.load.assert_called_once()

        # 验证配置读取
        mock_config.get_str.assert_any_call("app.name")
        mock_config.get_str.assert_any_call("app.version")
        mock_config.get_str.assert_any_call("app.build_date")

        # 验证欢迎信息显示
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("钉钉直播回放下载工具" in call for call in print_calls)
        assert any("1.5.0" in call for call in print_calls)
        assert any("2026年01月26日" in call for call in print_calls)
```

## 任务边界限制

### 包含范围

- 修改 `src/dingtalk_downloader/config/yaml_config.py` 中的 CONFIG_SCHEMA
- 修改 `src/dingtalk_downloader/main.py` 中的 `main()` 函数
- 更新 `tests/unit/test_yaml_config.py` 中的测试配置
- 添加 `tests/unit/test_main.py` 中的配置读取测试

### 不包含范围

- 不修改 `pyproject.toml` 中的版本号和描述
- 不修改其他模块中的硬编码值
- 不修改配置文件格式
- 不实现配置热重载功能

## 明确的实现需求

### 代码修改需求

1. **yaml_config.py**: 更新 CONFIG_SCHEMA,添加 `build_date` 字段验证
2. **main.py**: 修改 `main()` 函数,从配置文件读取并显示应用信息
3. **test_yaml_config.py**: 更新测试配置,添加 `build_date` 字段
4. **test_main.py**: 添加配置读取测试

### 测试需求

1. **单元测试**: 测试 `YamlConfig.get_str()` 方法读取 `app.build_date`
2. **集成测试**: 测试 `main()` 函数从配置文件读取并显示应用信息
3. **异常测试**: 测试配置文件不存在、格式错误、配置项缺失时的错误处理

### 代码质量需求

1. **代码规范**: 遵循 PEP 8 编码规范
2. **格式化**: 使用 Black 格式化工具
3. **类型注解**: 所有函数必须有类型注解
4. **错误处理**: 所有异常必须被捕获和处理
5. **日志记录**: 记录关键操作和错误

## 明确的子任务定义

### 任务1: 更新CONFIG_SCHEMA以包含build_date字段验证

- **输入**: `src/dingtalk_downloader/config/yaml_config.py`
- **输出**: CONFIG_SCHEMA 包含 `build_date` 字段验证
- **约束**: 不修改其他配置项,保持现有验证逻辑

### 任务2: 修改main.py从配置文件读取并显示应用信息

- **输入**: `src/dingtalk_downloader/main.py`
- **输出**: `main()` 函数从配置文件读取应用信息并显示
- **约束**: 使用 `YamlConfig.get_instance()` 和 `get_str()` 方法,添加错误处理

### 任务3: 更新测试配置以包含build_date字段

- **输入**: `tests/unit/test_yaml_config.py`
- **输出**: `get_full_test_config()` 包含 `build_date` 字段
- **约束**: 保持现有测试不变

### 任务4: 添加配置读取测试

- **输入**: `tests/unit/test_main.py`
- **输出**: 添加测试验证配置读取功能
- **约束**: 使用 pytest 和 pytest-mock

### 任务5: 运行测试验证功能

- **输入**: 所有代码修改和测试
- **输出**: 所有测试通过,测试覆盖率不低于80%
- **约束**: 使用 pytest 运行测试

### 任务6: 代码格式化和检查

- **输入**: 所有代码修改
- **输出**: 代码格式化通过,无 lint 错误
- **约束**: 使用 Black 和 flake8

## 明确的边界和限制

### 技术限制

- 仅支持 Python 3.8+
- 仅支持 YAML 格式的配置文件
- 配置文件必须在项目根目录的 `config` 目录下

### 功能限制

- 不支持配置热重载
- 不支持多环境配置
- 不支持配置文件加密

### 依赖限制

- 依赖现有的 `YamlConfig` 单例类
- 依赖现有的 `LoggerConfig` 类
- 依赖 pytest 测试框架

## 明确的验收标准

### 功能验收

- [ ] 程序启动时从配置文件读取并显示应用名称
- [ ] 程序启动时从配置文件读取并显示版本号
- [ ] 程序启动时从配置文件读取并显示构建日期
- [ ] 配置文件不存在时提供友好的错误提示
- [ ] 配置文件格式错误时提供友好的错误提示
- [ ] 配置项缺失时提供友好的错误提示

### 代码质量验收

- [ ] 代码符合项目编码规范(PEP 8, Black格式化)
- [ ] 代码有完整的类型注解
- [ ] 代码有适当的错误处理
- [ ] 代码有适当的日志记录

### 测试验收

- [ ] 单元测试覆盖配置读取功能
- [ ] 集成测试验证程序启动显示
- [ ] 所有测试通过
- [ ] 测试覆盖率不低于80%

## 下一步

基于以上共识,我将进入 **Automate 阶段**,按照任务计划执行代码修改和测试。
