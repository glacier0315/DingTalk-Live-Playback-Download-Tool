# CONSENSUS_yaml-config-refactor

## 任务概述
- **任务名称**: yaml-config-refactor
- **创建时间**: 2026-01-21 14:07:06
- **时间戳**: 20260121-140706

## 最终共识

### 配置系统架构设计

#### 1. 配置文件结构
采用分层配置结构，将配置分为以下几类：

```yaml
# 应用配置
app:
  name: "钉钉直播回放下载工具"
  version: "1.5.0"
  
# 下载配置
download:
  default_dir: "Downloads"
  temp_m3u8_file: "output.m3u8"
  max_retry_count: 5
  
# 浏览器配置
browser:
  default_type: "edge"  # edge, chrome, firefox
  headless: false
  timeout: 30
  
# 日志配置
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  dir: "logs"
  max_bytes: 10485760  # 10MB
  backup_count: 5
  retention_days: 30
  
# 请求头配置
headers:
  user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  referer: "https://n.dingtalk.com/"
  accept: "application/vnd.apple.mpegurl, text/plain, */*"
  accept_language: "zh-CN,zh;q=0.9,en;q=0.8"
  accept_encoding: "gzip, deflate, br"
  
# N_m3u8DL-RE配置
n_m3u8dl_re:
  executable_path: "assets/bin/N_m3u8DL-RE.exe"
  ui_language: "zh-CN"
  
# FFmpeg配置
ffmpeg:
  executable_path: "assets/bin/ffmpeg.exe"
```

#### 2. 配置管理类设计

**YamlConfig类**：
- 继承或替代现有的Settings类
- 支持YAML格式配置文件的加载和保存
- 提供配置项的获取和设置接口
- 支持配置缓存，避免重复读取文件
- 提供配置验证功能

**配置加载优先级**：
1. 用户配置文件（~/.dingtalk_downloader/config.yaml）
2. 项目默认配置文件（config.yaml.example）
3. 代码中的默认值

#### 3. 常量管理策略

**保留在constants.py中的常量**：
- 浏览器类型枚举（BROWSER_TYPE_EDGE, BROWSER_TYPE_CHROME, BROWSER_TYPE_FIREFOX）
- 下载模式枚举（DOWNLOAD_MODE_SINGLE, DOWNLOAD_MODE_BATCH）
- 保存模式枚举（SAVE_MODE_DEFAULT, SAVE_MODE_MANUAL）
- 映射字典（BROWSER_OPTION_MAP, DOWNLOAD_MODE_MAP, SAVE_MODE_MAP）

**迁移到YAML的配置**：
- 默认下载目录
- 最大重试次数
- 临时文件名
- 日志级别和配置
- 请求头配置
- 二进制工具路径

#### 4. 日志系统集成

**LoggerConfig类改造**：
- 从YAML配置文件读取日志级别
- 从YAML配置文件读取日志目录
- 从YAML配置文件读取日志文件大小和备份数量
- 保持现有日志格式和功能不变

### 实现方案

#### 1. 新增依赖
在requirements.txt中添加：
```
PyYAML>=6.0
```

#### 2. 文件结构
```
src/dingtalk_downloader/config/
├── __init__.py
├── constants.py              # 保留，只包含枚举常量
├── settings.py               # 重构，支持YAML格式
├── yaml_config.py            # 新增，YAML配置管理类
├── logger_config.py          # 改造，从YAML读取配置
└── config.yaml.example       # 新增，默认配置文件模板
```

#### 3. 核心类设计

**YamlConfig类**：
```python
class YamlConfig:
    def __init__(self, config_file: Optional[str] = None)
    def load(self) -> None
    def save(self) -> None
    def get(self, key: str, default: Any = None) -> Any
    def set(self, key: str, value: Any) -> None
    def get_nested(self, keys: List[str], default: Any = None) -> Any
    def set_nested(self, keys: List[str], value: Any) -> None
    def reload(self) -> None
```

**Settings类改造**：
- 保持现有API不变，向后兼容
- 内部使用YamlConfig实现
- 提供从JSON到YAML的迁移功能

#### 4. 配置文件位置
- 用户配置文件：`~/.dingtalk_downloader/config.yaml`
- 默认配置模板：`src/dingtalk_downloader/config/config.yaml.example`
- 项目根目录配置：`config.yaml`（可选，用于开发环境）

### 验收标准

#### 功能验收
1. ✅ YAML配置文件能够正确加载和解析
2. ✅ 配置项的获取和设置功能正常
3. ✅ 支持嵌套配置项的访问（如`download.default_dir`）
4. ✅ 配置文件不存在时使用默认值
5. ✅ 配置文件格式错误时有友好的错误提示
6. ✅ 配置变更后能够正确保存
7. ✅ 日志系统能够从YAML读取配置
8. ✅ 现有功能不受影响（单个下载、批量下载）

#### 性能验收
1. ✅ 配置加载性能：首次加载时间<100ms
2. ✅ 配置读取性能：缓存命中时<1ms
3. ✅ 配置保存性能：保存时间<50ms

#### 代码质量验收
1. ✅ 代码符合PEP 8规范
2. ✅ 代码通过flake8检查
3. ✅ 代码通过black格式化
4. ✅ 代码通过mypy类型检查
5. ✅ 代码覆盖率≥80%

#### 文档验收
1. ✅ config.yaml.example包含详细的中文注释
2. ✅ 更新README.md说明新的配置系统
3. ✅ 更新config模块的README.md
4. ✅ 代码注释清晰完整

#### 测试验收
1. ✅ 单元测试覆盖所有核心功能
2. ✅ 测试用例包括正常场景、边界条件、异常情况
3. ✅ 所有测试通过
4. ✅ 集成测试验证配置系统与现有模块的兼容性

### 风险控制

#### 技术风险
1. **风险**：YAML配置文件格式错误导致程序崩溃
   - **应对**：添加配置验证和错误处理，提供友好的错误提示

2. **风险**：配置迁移过程中数据丢失
   - **应对**：保留JSON配置文件的备份，提供自动迁移功能

3. **风险**：性能下降
   - **应对**：实现配置缓存机制，避免重复读取文件

#### 兼容性风险
1. **风险**：现有代码无法使用新配置系统
   - **应对**：保持Settings类API不变，内部实现切换到YAML

2. **风险**：用户配置文件迁移困难
   - **应对**：提供自动迁移脚本，将JSON配置转换为YAML

### 交付物清单

#### 代码文件
1. ✅ src/dingtalk_downloader/config/yaml_config.py
2. ✅ src/dingtalk_downloader/config/settings.py（重构）
3. ✅ src/dingtalk_downloader/config/logger_config.py（改造）
4. ✅ src/dingtalk_downloader/config/config.yaml.example
5. ✅ tests/unit/test_yaml_config.py
6. ✅ tests/unit/test_settings.py（更新）

#### 文档文件
1. ✅ docs/tasks/20260121-140648-yaml-config-refactor/ALIGNMENT_yaml-config-refactor.md
2. ✅ docs/tasks/20260121-140648-yaml-config-refactor/CONSENSUS_yaml-config-refactor.md
3. ✅ docs/tasks/20260121-140648-yaml-config-refactor/DESIGN_yaml-config-refactor.md
4. ✅ docs/tasks/20260121-140648-yaml-config-refactor/TASK_yaml-config-refactor.md
5. ✅ docs/tasks/20260121-140648-yaml-config-refactor/ACCEPTANCE_yaml-config-refactor.md
6. ✅ docs/tasks/20260121-140648-yaml-config-refactor/FINAL_yaml-config-refactor.md
7. ✅ docs/tasks/20260121-140648-yaml-config-refactor/TODO_yaml-config-refactor.md
8. ✅ README.md（更新）
9. ✅ src/dingtalk_downloader/config/README.md（更新）

#### 配置文件
1. ✅ requirements.txt（添加PyYAML依赖）
2. ✅ src/dingtalk_downloader/config/config.yaml.example

### 时间规划
- **Align阶段**：已完成
- **Architect阶段**：进行中
- **Atomize阶段**：待开始
- **Approve阶段**：待开始
- **Automate阶段**：待开始
- **Assess阶段**：待开始

预计总耗时：2-3小时
