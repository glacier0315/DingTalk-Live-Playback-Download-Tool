# CONSENSUS 配置文件读取模块优化

## 明确的需求描述和验收标准

### 需求描述

优化 `yaml_config.py` 模块，实现以下目标：

1. **移除硬编码默认值**:
   - 删除 `_load_default_config()` 方法及其硬编码的默认配置
   - 删除 `default_config` 属性
   - 配置文件不存在时抛出 `ConfigLoadError` 异常

2. **实现配置验证机制**:
   - 定义配置schema，包括必填项、数据类型、取值范围
   - 实现配置验证逻辑
   - 在配置加载时自动验证

3. **改进错误处理**:
   - 提供详细的错误信息（配置项路径、期望值、实际值）
   - 区分不同类型的配置错误
   - 在验证失败时抛出明确的异常

4. **确保明确错误反馈**:
   - 配置文件缺失：抛出 `ConfigLoadError`
   - 必填项缺失：抛出 `ConfigValidationError`
   - 类型不匹配：抛出 `ConfigValueError`
   - 值超出范围：抛出 `ConfigValueError`

### 验收标准

1. **功能验收**:
   - [ ] `_load_default_config()` 方法已删除
   - [ ] `default_config` 属性已删除
   - [ ] 配置文件不存在时抛出 `ConfigLoadError`
   - [ ] 配置验证机制已实现
   - [ ] 错误信息包含配置项路径、期望值、实际值

2. **代码质量验收**:
   - [ ] 代码符合PEP 8规范
   - [ ] 代码缩进使用4个空格
   - [ ] 变量命名使用小驼峰
   - [ ] 类名使用大驼峰
   - [ ] 代码有适当的注释

3. **测试验收**:
   - [ ] 所有现有测试用例通过
   - [ ] 新增配置验证相关测试用例
   - [ ] 测试覆盖率达到80%以上

4. **文档验收**:
   - [ ] 模块文档已更新
   - [ ] API文档已更新
   - [ ] 配置文件示例已更新

## 技术实现方案

### 1. 配置Schema设计

创建配置schema字典，定义每个配置项的验证规则：

```python
CONFIG_SCHEMA = {
    "app": {
        "required": True,
        "type": dict,
        "fields": {
            "name": {"required": True, "type": str},
            "version": {"required": True, "type": str},
        }
    },
    "download": {
        "required": True,
        "type": dict,
        "fields": {
            "default_dir": {"required": True, "type": str},
            "temp_dir": {"required": True, "type": str},
            "max_retry_count": {"required": True, "type": int, "min": 1, "max": 100},
        }
    },
    "browser": {
        "required": True,
        "type": dict,
        "fields": {
            "default_type": {"required": True, "type": str, "choices": ["edge", "chrome", "firefox"]},
            "headless": {"required": True, "type": bool},
            "timeout": {"required": True, "type": int, "min": 1, "max": 300},
        }
    },
    "logging": {
        "required": True,
        "type": dict,
        "fields": {
            "level": {"required": True, "type": str, "choices": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
            "dir": {"required": True, "type": str},
            "max_bytes": {"required": True, "type": int, "min": 1024},
            "backup_count": {"required": True, "type": int, "min": 1, "max": 100},
            "retention_days": {"required": True, "type": int, "min": 1, "max": 365},
        }
    },
    "headers": {
        "required": True,
        "type": dict,
        "fields": {
            "user_agent": {"required": True, "type": str},
            "referer": {"required": True, "type": str},
            "accept": {"required": True, "type": str},
            "accept_language": {"required": True, "type": str},
            "accept_encoding": {"required": True, "type": str},
            "connection": {"required": True, "type": str},
            "sec_fetch_dest": {"required": True, "type": str},
            "sec_fetch_mode": {"required": True, "type": str},
            "sec_fetch_site": {"required": True, "type": str},
            "sec_fetch_user": {"required": True, "type": str},
            "upgrade_insecure_requests": {"required": True, "type": str},
        }
    },
    "n_m3u8dl_re": {
        "required": True,
        "type": dict,
        "fields": {
            "executable_path": {"required": True, "type": str},
            "ui_language": {"required": True, "type": str},
            "temp_dir": {"required": True, "type": str},
            "log_dir": {"required": True, "type": str},
        }
    },
    "ffmpeg": {
        "required": True,
        "type": dict,
        "fields": {
            "executable_path": {"required": True, "type": str},
        }
    },
}
```

### 2. 配置验证实现

实现配置验证方法：

```python
def _validate_config(self, config: Dict[str, Any], schema: Dict[str, Any], path: str = "") -> None:
    """
    验证配置是否符合schema定义。

    Args:
        config: 配置字典
        schema: 配置schema
        path: 当前配置路径（用于错误信息）

    Raises:
        ConfigValidationError: 配置验证失败
    """
    for key, field_schema in schema.items():
        current_path = f"{path}.{key}" if path else key

        # 检查必填项
        if field_schema.get("required", False) and key not in config:
            raise ConfigValidationError(f"缺少必填配置项: {current_path}")

        if key not in config:
            continue

        value = config[key]

        # 检查类型
        expected_type = field_schema.get("type")
        if expected_type and not isinstance(value, expected_type):
            raise ConfigValueError(
                f"配置项类型错误: {current_path}, 期望类型: {expected_type.__name__}, 实际类型: {type(value).__name__}",
                current_path
            )

        # 检查取值范围
        if "min" in field_schema and value < field_schema["min"]:
            raise ConfigValueError(
                f"配置值过小: {current_path}, 最小值: {field_schema['min']}, 实际值: {value}",
                current_path
            )

        if "max" in field_schema and value > field_schema["max"]:
            raise ConfigValueError(
                f"配置值过大: {current_path}, 最大值: {field_schema['max']}, 实际值: {value}",
                current_path
            )

        # 检查选项
        if "choices" in field_schema and value not in field_schema["choices"]:
            raise ConfigValueError(
                f"配置值无效: {current_path}, 可选值: {field_schema['choices']}, 实际值: {value}",
                current_path
            )

        # 递归验证嵌套配置
        if "fields" in field_schema and isinstance(value, dict):
            self._validate_config(value, field_schema["fields"], current_path)
```

### 3. 修改load()方法

修改 `load()` 方法，移除默认值逻辑，添加配置验证：

```python
def load(self) -> None:
    """
    加载配置文件。

    从配置文件中加载配置项，如果配置文件不存在则抛出异常。
    加载完成后自动验证配置有效性。
    线程安全，确保只加载一次。
    """
    with self._lock:
        if self._loaded:
            logger.debug("配置已加载，跳过重复加载")
            return

        logger.info(f"开始加载配置文件: {self.config_file}")

        if not os.path.exists(self.config_file):
            error_msg = f"配置文件不存在: {self.config_file}"
            logger.error(error_msg)
            raise ConfigLoadError(error_msg)

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
            logger.info(f"配置文件加载成功: {self.config_file}")
        except yaml.YAMLError as e:
            error_msg = f"配置文件格式错误: {e}"
            logger.error(error_msg)
            raise ConfigLoadError(error_msg) from e
        except IOError as e:
            error_msg = f"读取配置文件失败: {e}"
            logger.error(error_msg)
            raise ConfigLoadError(error_msg) from e

        # 验证配置
        self._validate_config(self.config, CONFIG_SCHEMA)

        self._loaded = True
        logger.info("配置加载完成")
```

### 4. 修改_initialize()方法

修改 `_initialize()` 方法，移除 `default_config` 初始化：

```python
def _initialize(self, config_file: Optional[str] = None) -> None:
    """
    初始化实例属性。

    Args:
        config_file: 配置文件路径
    """
    self.config: Dict[str, Any] = {}
    self._loaded: bool = False

    if config_file is None:
        self.config_file = CONFIG_FILE_PATH
    else:
        self.config_file = config_file

    logger.debug(f"YamlConfig初始化完成，配置文件路径: {self.config_file}")
```

### 5. 删除_merge_configs()方法

删除 `_merge_configs()` 方法，因为不再需要合并用户配置和默认配置。

### 6. 修改validate()方法

修改 `validate()` 方法，使用新的配置验证机制：

```python
def validate(self) -> bool:
    """
    验证配置有效性。

    Returns:
        验证结果，True表示配置有效

    Raises:
        ConfigValidationError: 配置验证失败
    """
    if not self._loaded:
        self.load()

    self._validate_config(self.config, CONFIG_SCHEMA)
    logger.info("配置验证通过")
    return True
```

## 任务边界限制

1. **不修改的内容**:
   - 配置文件格式（app.yaml）保持不变
   - 其他模块的配置使用方式保持不变
   - 单例模式和线程安全机制保持不变
   - 公开API接口（get, get_str, get_int等）保持不变

2. **修改的内容**:
   - 删除 `_load_default_config()` 方法
   - 删除 `default_config` 属性
   - 删除 `_merge_configs()` 方法
   - 修改 `load()` 方法
   - 修改 `_initialize()` 方法
   - 修改 `validate()` 方法
   - 新增 `_validate_config()` 方法
   - 新增 `CONFIG_SCHEMA` 常量

3. **测试更新**:
   - 更新 `test_yaml_config_load_nonexistent_file()` 测试用例
   - 更新 `test_yaml_config_default_config()` 测试用例
   - 更新 `test_yaml_config_merge_configs()` 测试用例
   - 新增配置验证相关测试用例
