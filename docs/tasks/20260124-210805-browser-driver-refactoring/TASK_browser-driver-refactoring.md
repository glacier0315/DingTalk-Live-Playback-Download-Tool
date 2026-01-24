# TASK - 浏览器驱动代码重构

## 文档信息

- **任务名称**: browser-driver-refactoring
- **创建时间**: 2026-01-24
- **阶段**: Atomize（原子化）
- **目标**: 将重构任务拆分为原子任务，定义输入输出契约和依赖关系

---

## 一、任务分解

### 1.1 任务列表

| 任务ID | 任务名称 | 优先级 | 预计时间 | 依赖任务 |
|--------|---------|---------|-----------|---------|
| T001 | 在BrowserDriver中添加extract_m3u8_links_from_logs方法 | 高 | 30分钟 | 无 |
| T002 | 在FirefoxDriver中重写extract_m3u8_links_from_logs方法 | 高 | 30分钟 | T001 |
| T003 | 修改M3u8Parser的构造函数 | 高 | 15分钟 | 无 |
| T004 | 修改M3u8Parser的fetch_m3u8_links方法 | 高 | 45分钟 | T001, T002, T003 |
| T005 | 修改M3u8Parser的import语句 | 高 | 10分钟 | T003, T004 |
| T006 | 更新M3u8Parser的测试用例 | 高 | 60分钟 | T004, T005 |
| T007 | 更新Downloader中M3u8Parser的调用 | 中 | 15分钟 | T003, T004 |
| T008 | 运行所有测试并修复问题 | 高 | 45分钟 | T006, T007 |
| T009 | 代码审查和优化 | 中 | 30分钟 | T008 |
| T010 | 更新文档 | 低 | 20分钟 | T009 |

---

## 二、原子任务详细说明

### T001: 在BrowserDriver中添加extract_m3u8_links_from_logs方法

#### 2.1 任务描述

在BrowserDriver抽象基类中添加`extract_m3u8_links_from_logs`方法，提供默认实现，处理Edge和Chrome的日志格式。

#### 2.2 输入

- 无（新增方法）

#### 2.3 输出

- BrowserDriver类新增`extract_m3u8_links_from_logs`方法
- 该方法提供默认实现，处理Edge和Chrome的日志格式

#### 2.4 实施步骤

1. 打开`src/dingtalk_downloader/browser/browser_driver.py`
2. 在BrowserDriver类中添加`extract_m3u8_links_from_logs`方法
3. 实现默认逻辑：
   - 遍历日志列表
   - 检查日志中是否包含"message"字段
   - 如果包含，提取message内容
   - 在message中查找".m3u8"关键字
   - 提取URL（格式：'url":"..."）
   - 返回找到的m3u8链接列表
4. 添加方法文档字符串
5. 添加必要的导入（re模块）

#### 2.5 验收标准

- 方法签名正确
- 默认实现逻辑正确
- 文档字符串完整
- 代码符合项目规范

#### 2.6 风险

- 无

---

### T002: 在FirefoxDriver中重写extract_m3u8_links_from_logs方法

#### 2.1 任务描述

在FirefoxDriver类中重写`extract_m3u8_links_from_logs`方法，处理Firefox特定的日志格式。

#### 2.2 输入

- T001完成的BrowserDriver类

#### 2.3 输出

- FirefoxDriver类重写`extract_m3u8_links_from_logs`方法
- 该方法处理Firefox特定的日志格式

#### 2.4 实施步骤

1. 打开`src/dingtalk_downloader/browser/firefox_driver.py`
2. 在FirefoxDriver类中添加`extract_m3u8_links_from_logs`方法
3. 实现Firefox特定逻辑：
   - 遍历日志列表
   - 将日志转换为字符串
   - 使用正则表达式匹配m3u8链接
   - 清理链接中的特殊字符
   - 返回找到的m3u8链接列表
4. 添加方法文档字符串
5. 添加必要的导入（re模块）

#### 2.5 验收标准

- 方法签名正确
- Firefox特定逻辑正确
- 文档字符串完整
- 代码符合项目规范

#### 2.6 风险

- 正则表达式可能需要调整

---

### T003: 修改M3u8Parser的构造函数

#### 2.1 任务描述

修改M3u8Parser的构造函数，移除`browser_type`参数，将`browser`参数类型从具体类改为抽象类`BrowserDriver`。

#### 2.2 输入

- 无

#### 2.3 输出

- M3u8Parser构造函数修改完成
- 移除`browser_type`参数
- `browser`参数类型改为`BrowserDriver`

#### 2.4 实施步骤

1. 打开`src/dingtalk_downloader/core/m3u8_parser.py`
2. 修改`__init__`方法签名：
   - 移除`browser_type: str`参数
   - 将`browser`参数类型从`Union[EdgeDriver, ChromeDriver, FirefoxDriver]`改为`BrowserDriver`
   - 移除`self.browser_type = browser_type`赋值语句
3. 修改import语句：
   - 移除`from ..browser.edge_driver import EdgeDriver`
   - 移除`from ..browser.chrome_driver import ChromeDriver`
   - 移除`from ..browser.firefox_driver import FirefoxDriver`
   - 添加`from ..browser.browser_driver import BrowserDriver`
   - 移除浏览器类型常量的导入（`BROWSER_TYPE_EDGE`, `BROWSER_TYPE_CHROME`, `BROWSER_TYPE_FIREFOX`）

#### 2.5 验收标准

- 构造函数签名正确
- 移除了`browser_type`参数
- `browser`参数类型为`BrowserDriver`
- import语句正确

#### 2.6 风险

- 需要确保所有调用M3u8Parser的地方都已更新

---

### T004: 修改M3u8Parser的fetch_m3u8_links方法

#### 2.1 任务描述

修改M3u8Parser的`fetch_m3u8_links`方法，移除浏览器类型判断逻辑，直接调用BrowserDriver的`extract_m3u8_links_from_logs`方法。

#### 2.2 输入

- T001完成的BrowserDriver类
- T002完成的FirefoxDriver类
- T003完成的M3u8Parser构造函数

#### 2.3 输出

- `fetch_m3u8_links`方法重构完成
- 移除浏览器类型判断逻辑
- 调用`browser.extract_m3u8_links_from_logs`方法

#### 2.4 实施步骤

1. 打开`src/dingtalk_downloader/core/m3u8_parser.py`
2. 修改`fetch_m3u8_links`方法：
   - 移除浏览器类型判断逻辑（第100-103行）
   - 直接调用`self.browser.get_log(LOG_TYPE_PERFORMANCE)`
   - 调用`self.browser.extract_m3u8_links_from_logs(logs)`提取m3u8链接
   - 遍历提取的m3u8链接列表
   - 检查每个链接是否包含liveUuid
   - 如果包含，返回该链接
   - 移除第107-116行的Firefox特定逻辑
   - 移除第118-131行的Edge/Chrome特定逻辑
3. 简化代码逻辑，提高可读性

#### 2.5 验收标准

- 移除了所有浏览器类型判断逻辑
- 调用`browser.extract_m3u8_links_from_logs`方法
- 代码逻辑简化
- 代码符合项目规范

#### 2.6 风险

- 需要确保逻辑正确性

---

### T005: 修改M3u8Parser的import语句

#### 2.1 任务描述

修改M3u8Parser的import语句，移除具体浏览器驱动类的导入和浏览器类型常量的导入，只导入BrowserDriver抽象类。

#### 2.2 输入

- T003完成的M3u8Parser构造函数修改

#### 2.3 输出

- import语句修改完成
- 只导入BrowserDriver抽象类

#### 2.4 实施步骤

1. 打开`src/dingtalk_downloader/core/m3u8_parser.py`
2. 修改import语句：
   - 移除`from ..browser.edge_driver import EdgeDriver`
   - 移除`from ..browser.chrome_driver import ChromeDriver`
   - 移除`from ..browser.firefox_driver import FirefoxDriver`
   - 添加`from ..browser.browser_driver import BrowserDriver`
   - 移除浏览器类型常量的导入（`BROWSER_TYPE_EDGE`, `BROWSER_TYPE_CHROME`, `BROWSER_TYPE_FIREFOX`）

#### 2.5 验收标准

- import语句正确
- 只导入BrowserDriver抽象类
- 移除了具体浏览器驱动类的导入

#### 2.6 风险

- 无

---

### T006: 更新M3u8Parser的测试用例

#### 2.1 任务描述

更新M3u8Parser的测试用例，确保测试用例与重构后的代码一致。

#### 2.2 输入

- T004完成的M3u8Parser重构

#### 2.3 输出

- 所有M3u8Parser测试用例更新完成
- 所有测试通过

#### 2.4 实施步骤

1. 打开`tests/unit/test_m3u8_parser.py`
2. 修改所有测试用例：
   - 移除`browser_type`参数
   - 将`browser`参数类型从具体类改为`BrowserDriver`
   - 更新mock对象，使用`Mock(spec=BrowserDriver)`
   - 更新mock返回值
3. 添加新的测试用例（如果需要）
4. 运行测试，确保所有测试通过

#### 2.5 验收标准

- 所有测试用例更新完成
- 所有测试通过
- 测试覆盖率保持或提升

#### 2.6 风险

- 可能需要添加新的mock逻辑

---

### T007: 更新Downloader中M3u8Parser的调用

#### 2.1 任务描述

更新Downloader中M3u8Parser的调用，移除`browser_type`参数。

#### 2.2 输入

- T003完成的M3u8Parser构造函数修改

#### 2.3 输出

- Downloader中M3u8Parser的调用更新完成
- 移除`browser_type`参数

#### 2.4 实施步骤

1. 打开`src/dingtalk_downloader/core/downloader.py`
2. 搜索所有`M3u8Parser`的调用
3. 修改调用：
   - 移除`browser_type`参数
   - 确保只传递`browser`参数和`max_retries`参数（如果需要）
4. 检查是否有其他地方需要修改

#### 2.5 验收标准

- 所有M3u8Parser的调用更新完成
- 移除了`browser_type`参数
- 代码符合项目规范

#### 2.6 风险

- 可能遗漏某些调用点

---

### T008: 运行所有测试并修复问题

#### 2.1 任务描述

运行所有测试，确保重构后的代码功能正常，修复发现的问题。

#### 2.2 输入

- T006完成的测试用例更新
- T007完成的Downloader更新

#### 2.3 输出

- 所有测试通过
- 发现的问题已修复

#### 2.4 实施步骤

1. 运行所有单元测试：`pytest tests/unit/`
2. 运行所有集成测试：`pytest tests/integration/`
3. 运行所有功能测试：`pytest tests/functional/`
4. 检查测试结果
5. 修复发现的测试失败问题
6. 重新运行测试，确保所有测试通过

#### 2.5 验收标准

- 所有单元测试通过
- 所有集成测试通过
- 所有功能测试通过
- 测试覆盖率保持或提升

#### 2.6 风险

- 可能发现新的bug

---

### T009: 代码审查和优化

#### 2.1 任务描述

对重构后的代码进行审查和优化，确保代码质量。

#### 2.2 输入

- T008完成的测试通过

#### 2.3 输出

- 代码审查完成
- 代码优化完成
- 代码符合项目规范

#### 2.4 实施步骤

1. 审查BrowserDriver的代码
2. 审查FirefoxDriver的代码
3. 审查M3u8Parser的代码
4. 审查Downloader的代码
5. 检查代码是否符合SOLID原则
6. 检查代码是否符合项目规范
7. 优化代码（如果需要）
8. 添加必要的注释

#### 2.5 验收标准

- 代码符合SOLID原则
- 代码符合项目规范
- 代码可读性良好
- 代码注释完整

#### 2.6 风险

- 可能发现需要进一步优化的地方

---

### T010: 更新文档

#### 2.1 任务描述

更新相关文档，确保文档与代码一致。

#### 2.2 输入

- T009完成的代码审查和优化

#### 2.3 输出

- 文档更新完成
- 文档与代码一致

#### 2.4 实施步骤

1. 检查是否有需要更新的文档
2. 更新README文档（如果需要）
3. 更新API文档（如果需要）
4. 更新架构文档（如果需要）
5. 检查文档与代码的一致性

#### 2.5 验收标准

- 文档更新完成
- 文档与代码一致
- 文档可读性良好

#### 2.6 风险

- 可能遗漏某些文档

---

## 三、任务依赖关系图

```
T001: 在BrowserDriver中添加extract_m3u8_links_from_logs方法
  │
  ├─> T002: 在FirefoxDriver中重写extract_m3u8_links_from_logs方法
  │
  └─> T004: 修改M3u8Parser的fetch_m3u8_links方法

T003: 修改M3u8Parser的构造函数
  │
  ├─> T004: 修改M3u8Parser的fetch_m3u8_links方法
  │
  └─> T005: 修改M3u8Parser的import语句

T004: 修改M3u8Parser的fetch_m3u8_links方法
  │
  ├─> T006: 更新M3u8Parser的测试用例
  │
  └─> T007: 更新Downloader中M3u8Parser的调用

T006: 更新M3u8Parser的测试用例
  │
  └─> T008: 运行所有测试并修复问题

T007: 更新Downloader中M3u8Parser的调用
  │
  └─> T008: 运行所有测试并修复问题

T008: 运行所有测试并修复问题
  │
  └─> T009: 代码审查和优化

T009: 代码审查和优化
  │
  └─> T010: 更新文档
```

---

## 四、任务执行顺序

### 4.1 并行任务

以下任务可以并行执行：
- T001 和 T003（无依赖关系）

### 4.2 串行任务

以下任务必须按顺序执行：
- T001 → T002 → T004
- T003 → T004 → T005
- T004 → T006, T007
- T006, T007 → T008
- T008 → T009 → T010

### 4.3 推荐执行顺序

1. **第一批（并行）**: T001, T003
2. **第二批（串行）**: T002, T004, T005
3. **第三批（串行）**: T006, T007
4. **第四批（串行）**: T008, T009, T010

---

## 五、输入输出契约

### 5.1 T001: 在BrowserDriver中添加extract_m3u8_links_from_logs方法

**输入**:
- 无

**输出**:
- BrowserDriver类新增`extract_m3u8_links_from_logs`方法
- 方法签名: `def extract_m3u8_links_from_logs(self, logs: List[dict]) -> List[str]`
- 方法提供默认实现，处理Edge和Chrome的日志格式

**契约**:
- 方法接受日志列表作为输入
- 方法返回m3u8链接列表
- 方法处理Edge和Chrome的日志格式
- 方法可以被子类重写

### 5.2 T002: 在FirefoxDriver中重写extract_m3u8_links_from_logs方法

**输入**:
- T001完成的BrowserDriver类

**输出**:
- FirefoxDriver类重写`extract_m3u8_links_from_logs`方法
- 方法签名: `def extract_m3u8_links_from_logs(self, logs: List[dict]) -> List[str]`
- 方法处理Firefox特定的日志格式

**契约**:
- 方法接受日志列表作为输入
- 方法返回m3u8链接列表
- 方法处理Firefox的日志格式
- 方法使用正则表达式匹配m3u8链接

### 5.3 T003: 修改M3u8Parser的构造函数

**输入**:
- 无

**输出**:
- M3u8Parser构造函数修改完成
- 构造函数签名: `def __init__(self, browser: BrowserDriver, max_retries: int = MAX_RETRY_COUNT)`
- 移除`browser_type`参数

**契约**:
- 构造函数接受BrowserDriver实例作为输入
- 构造函数接受max_retries参数（可选）
- 构造函数不再接受browser_type参数

### 5.4 T004: 修改M3u8Parser的fetch_m3u8_links方法

**输入**:
- T001完成的BrowserDriver类
- T002完成的FirefoxDriver类
- T003完成的M3u8Parser构造函数

**输出**:
- `fetch_m3u8_links`方法重构完成
- 方法签名: `def fetch_m3u8_links(self, url: str) -> Optional[List[str]]`
- 移除浏览器类型判断逻辑

**契约**:
- 方法接受URL作为输入
- 方法返回m3u8链接列表或None
- 方法调用`browser.extract_m3u8_links_from_logs`方法
- 方法不进行浏览器类型判断

### 5.5 T005: 修改M3u8Parser的import语句

**输入**:
- T003完成的M3u8Parser构造函数修改

**输出**:
- import语句修改完成
- 只导入BrowserDriver抽象类

**契约**:
- 导入BrowserDriver抽象类
- 不导入具体浏览器驱动类
- 不导入浏览器类型常量

### 5.6 T006: 更新M3u8Parser的测试用例

**输入**:
- T004完成的M3u8Parser重构

**输出**:
- 所有M3u8Parser测试用例更新完成
- 所有测试通过

**契约**:
- 测试用例与重构后的代码一致
- 测试用例使用BrowserDriver抽象类
- 测试用例不使用browser_type参数

### 5.7 T007: 更新Downloader中M3u8Parser的调用

**输入**:
- T003完成的M3u8Parser构造函数修改

**输出**:
- Downloader中M3u8Parser的调用更新完成
- 移除`browser_type`参数

**契约**:
- M3u8Parser的调用不传递browser_type参数
- M3u8Parser的调用只传递browser参数

### 5.8 T008: 运行所有测试并修复问题

**输入**:
- T006完成的测试用例更新
- T007完成的Downloader更新

**输出**:
- 所有测试通过
- 发现的问题已修复

**契约**:
- 所有单元测试通过
- 所有集成测试通过
- 所有功能测试通过
- 测试覆盖率保持或提升

### 5.9 T009: 代码审查和优化

**输入**:
- T008完成的测试通过

**输出**:
- 代码审查完成
- 代码优化完成
- 代码符合项目规范

**契约**:
- 代码符合SOLID原则
- 代码符合项目规范
- 代码可读性良好
- 代码注释完整

### 5.10 T010: 更新文档

**输入**:
- T009完成的代码审查和优化

**输出**:
- 文档更新完成
- 文档与代码一致

**契约**:
- 文档更新完成
- 文档与代码一致
- 文档可读性良好

---

## 六、风险评估

### 6.1 技术风险

| 风险项 | 可能性 | 影响 | 缓解措施 | 相关任务 |
|-------|-------|------|---------|---------|
| 正则表达式可能需要调整 | 中 | 中 | 充分测试FirefoxDriver | T002 |
| 可能遗漏某些调用点 | 低 | 高 | 全面搜索和测试 | T007 |
| 可能发现新的bug | 中 | 高 | 充分测试 | T008 |
| 可能需要进一步优化 | 低 | 低 | 代码审查 | T009 |

### 6.2 进度风险

| 风险项 | 可能性 | 影响 | 缓解措施 |
|-------|-------|------|---------|
| 任务时间估计不准确 | 中 | 中 | 预留缓冲时间 |
| 依赖任务延迟 | 低 | 高 | 密切监控依赖任务进度 |

---

## 七、质量检查清单

### 7.1 代码质量检查

- [ ] 代码符合SOLID原则
- [ ] 代码符合项目规范
- [ ] 代码可读性良好
- [ ] 代码注释完整
- [ ] 无重复代码
- [ ] 无魔法数字
- [ ] 异常处理完善
- [ ] 日志记录完善

### 7.2 测试质量检查

- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 所有功能测试通过
- [ ] 测试覆盖率≥80%
- [ ] 测试用例覆盖正常场景
- [ ] 测试用例覆盖边界条件
- [ ] 测试用例覆盖异常情况

### 7.3 文档质量检查

- [ ] 文档更新完成
- [ ] 文档与代码一致
- [ ] 文档可读性良好
- [ ] 文档包含必要的示例

---

## 八、成功标准

### 8.1 功能成功标准

- [ ] M3u8Parser不再直接使用BROWSER_TYPE_*常量
- [ ] M3u8Parser的所有浏览器操作都通过BrowserDriver接口进行
- [ ] 所有现有测试用例通过
- [ ] 重构后功能与重构前完全一致

### 8.2 代码质量成功标准

- [ ] 符合SOLID原则
- [ ] 代码覆盖率保持或提升
- [ ] 代码可读性良好
- [ ] 遵循项目代码规范

### 8.3 文档成功标准

- [ ] 更新相关代码注释
- [ ] 更新相关文档（如果需要）

---

## 九、下一步行动

1. ✅ 分析现有浏览器操作代码
2. ✅ 识别代码中重复的浏览器类型判断逻辑
3. ✅ 生成ALIGNMENT文档
4. ✅ 生成CONSENSUS文档
5. ✅ 设计重构架构（Architect阶段）
6. ✅ 拆分原子任务（Atomize阶段，当前）
7. ⏳ 执行质量检查（Approve阶段）
8. ⏳ 实现代码重构（Automate阶段）
9. ⏳ 质量评估与交付确认（Assess阶段）
