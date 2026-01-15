# DESIGN_输入验证错误修复

## 整体架构

### 系统分层

```
┌─────────────────────────────────────────┐
│           main.py (主程序)              │
│         调用 validate_input()           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      validator.py (验证工具)            │
│    validate_input() 函数增强异常处理     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Python 内置 input() 函数            │
│   可能抛出 EOFError, KeyboardInterrupt  │
└─────────────────────────────────────────┘
```

## 核心组件设计

### 1. validate_input 函数增强

**当前实现**：
```python
def validate_input(
    prompt: str, valid_options: List[str], default_option: Optional[str] = None
) -> str:
    while True:
        choice = input(prompt)
        if choice == "" and default_option is not None:
            return default_option
        if choice in valid_options:
            return choice
        print("无效的选择，请重新输入。")
```

**增强后实现**：
```python
def validate_input(
    prompt: str, valid_options: List[str], default_option: Optional[str] = None
) -> str:
    """
    验证用户输入。

    支持默认选项，如果用户直接按 Enter，则返回默认选项。
    增强异常处理，捕获 EOFError 和 KeyboardInterrupt。

    Args:
        prompt: 提示信息
        valid_options: 有效选项列表
        default_option: 默认选项

    Returns:
        用户选择的选项

    Raises:
        ValueError: 输入无效时
        EOFError: 输入流结束时
        KeyboardInterrupt: 用户中断时
    """
    while True:
        try:
            choice = input(prompt)
            if choice == "" and default_option is not None:
                return default_option
            if choice in valid_options:
                return choice
            print("无效的选择，请重新输入。")
        except EOFError:
            # 输入流结束（如 Ctrl+D）
            if default_option is not None:
                print(f"\n输入流结束，使用默认选项: {default_option}")
                return default_option
            raise
        except KeyboardInterrupt:
            # 用户中断（如 Ctrl+C）
            print("\n用户中断输入")
            raise
```

### 2. 异常处理策略

**异常类型**：
- `EOFError`：输入流结束（如 Ctrl+D）
- `KeyboardInterrupt`：用户中断（如 Ctrl+C）
- `ValueError`：输入无效时（保持现有行为）

**处理策略**：
1. `EOFError`：如果有默认选项，返回默认选项；否则重新抛出异常
2. `KeyboardInterrupt`：打印提示信息，重新抛出异常
3. `ValueError`：保持现有行为，在循环中提示用户重新输入

## 模块依赖关系

```
main.py
  └── validator.validate_input()
       └── builtins.input()
```

## 接口契约定义

### validate_input 函数

**输入契约**：
- `prompt: str` - 提示信息
- `valid_options: List[str]` - 有效选项列表
- `default_option: Optional[str]` - 默认选项（可选）

**输出契约**：
- 返回类型：`str`
- 返回值：用户选择的选项或默认选项

**异常契约**：
- `EOFError`：输入流结束且无默认选项时
- `KeyboardInterrupt`：用户中断时
- `ValueError`：输入无效时（保持现有行为）

## 数据流向图

```
用户输入
   │
   ▼
input(prompt)
   │
   ├─→ EOFError ──→ 有默认选项? ──→ 是 ──→ 返回默认选项
   │               │
   │               └─→ 否 ──→ 重新抛出 EOFError
   │
   ├─→ KeyboardInterrupt ──→ 打印提示 ──→ 重新抛出
   │
   └─→ 正常输入
          │
          ├─→ 空字符串 ──→ 有默认选项? ──→ 是 ──→ 返回默认选项
          │               │
          │               └─→ 否 ──→ 继续循环
          │
          └─→ 非空字符串
                 │
                 ├─→ 在有效选项列表中 ──→ 返回该选项
                 │
                 └─→ 不在有效选项列表中 ──→ 打印提示 ──→ 继续循环
```

## 异常处理策略

### 1. EOFError 处理

**场景**：用户按下 Ctrl+D（Unix）或输入流结束

**处理逻辑**：
```python
except EOFError:
    if default_option is not None:
        print(f"\n输入流结束，使用默认选项: {default_option}")
        return default_option
    raise
```

**理由**：
- 如果有默认选项，优雅降级，使用默认选项
- 如果没有默认选项，重新抛出异常，让调用者处理

### 2. KeyboardInterrupt 处理

**场景**：用户按下 Ctrl+C

**处理逻辑**：
```python
except KeyboardInterrupt:
    print("\n用户中断输入")
    raise
```

**理由**：
- 打印友好的提示信息
- 重新抛出异常，让调用者处理（如 main.py 中的异常处理）

### 3. ValueError 处理

**场景**：输入无效（不在有效选项列表中）

**处理逻辑**：
```python
print("无效的选择，请重新输入。")
```

**理由**：
- 保持现有行为
- 在循环中提示用户重新输入

## 设计原则

### 1. 最小修改原则
- 只增强异常处理，不改变现有功能
- 保持函数签名不变
- 保持正常流程不变

### 2. 向后兼容原则
- 现有测试用例无需修改
- 现有调用代码无需修改
- 新增异常处理是透明的

### 3. 用户体验优先
- 提供友好的错误提示
- 优雅降级（使用默认选项）
- 避免程序崩溃

### 4. 代码一致性
- 遵循现有代码风格
- 使用类型注解
- 完整的文档字符串

## 质量门控

- ✅ 架构图清晰准确
- ✅ 接口定义完整
- ✅ 与现有系统无冲突
- ✅ 设计可行性验证
- ✅ 异常处理策略合理
- ✅ 向后兼容性保证
