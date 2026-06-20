# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

钉钉直播回放下载工具：Selenium 自动化浏览器抓取登录态 Cookie，从浏览器性能日志中解析 m3u8 链接，再调用本地 `N_m3u8DL-RE.exe` 子进程下载视频。核心数据流：`URL → Cookie → m3u8 → N_m3u8DL-RE → mp4`。

## 环境要求

- **Python 3.12+**（开发钉 3.14，见 `.python-version`）
- 浏览器：Edge / Chrome / Firefox（任选其一，需已登录 DingTalk 账户）
- Windows 平台依赖（已随仓库打包在 `assets/bin/`）：
  - `assets/bin/N_m3u8DL-RE.exe`
  - `assets/bin/ffmpeg.exe`
- **包管理**：[uv](https://docs.astral.sh/uv/) 0.5+（推荐），CI 也可走 `pip install -r requirements.txt -r requirements-dev.txt`

## 常用命令

```bash
# 推荐：uv 自动创建 .venv 并安装全部依赖（含 dev）
uv sync --group dev

# 启动程序（入口在 src/dingtalk_downloader/main.py 的 main()）
uv run python -m src.dingtalk_downloader.main
# 或激活 .venv 后：
python -m src.dingtalk_downloader.main

# 跑单元测试（默认走 tests/unit/，自动覆盖率）
uv run pytest -v

# 跑集成测试（需要 N_m3u8DL-RE.exe + 真实浏览器）
uv run pytest tests/integration/ -v -m integration

# 切换/覆盖配置文件路径
export DINGTALK_DOWNLOADER_CONFIG_PATH=/path/to/app.yaml
```

`rtk` 代理只对 `git/ls/du/wc/read/find` 等读操作生效；构建与运行没有特殊封装。

## 依赖管理

源真值在 `pyproject.toml`：

- `[project] dependencies` 段：运行时依赖（selenium / pandas / openpyxl / PyYAML）
- `[dependency-groups] dev` 段（PEP 735）：开发/测试依赖（pytest / pytest-cov）
- `uv.lock`：锁定的依赖图，跨机器一致

`requirements.txt` / `requirements-dev.txt` 是 `pip` 兼容的 fallback，由 uv 重新生成：

```bash
uv pip compile pyproject.toml -o requirements.txt
uv pip compile --group dev -o requirements-dev.txt
```

修改 `pyproject.toml` 后跑一次上述命令，把 `pyproject.toml`、`uv.lock`、`requirements.txt`、`requirements-dev.txt` 四个文件一起提交。

## 架构（src/dingtalk_downloader/）

入口与顶层流程：

- `main.py` — 解析模式（1 单个 / 2 批量），调用 `single_mode` 或 `batch_mode`，统一捕获 `CookieError / M3u8ParseError / FileReaderError` 与 `KeyboardInterrupt`。
- `core/downloader.py` — `Downloader` 外观类，组合 `DependencyFactory` 注入的依赖，循环调用 `VideoDownloadManager.process_video`。
- `core/video_download_manager.py` — 单视频完整流程编排（`initialize_download` → `process_video` → 内嵌 `VIDEO_DOWNLOAD_MAX_RETRIES=20` 次重试，每次重试前随机等待 `VIDEO_DOWNLOAD_RETRY_WAIT_MIN..MAX` 秒）。
- `core/download_orchestrator.py` — 单次下载状态机（拉 m3u8 → 启动子进程 → 监控日志 → 失败刷新 → 续传）。
- `core/download_session.py` — context manager；`with` 出自动关浏览器 + 清理 `temp/*.m3u8`。
- `core/dependency_factory.py` — 工厂 + 单例缓存（按 `cookie_handler_{browser_type}` 等 key 复用实例，便于测试用 `clear_instances()` 重置）。

抓取与解析：

- `core/cookie_handler.py` — Selenium 上下文管理器；首次访问需用户在弹出的浏览器中手动登录并按 Enter。
- `core/m3u8_parser.py` — 从 URL 提取 `liveUuid`，通过 `browser.get_log("performance")` 抓性能日志，过滤含 liveUuid 的 `.m3u8` URL；重试 `MAX_RETRY_COUNT=5` 次。
- `core/m3u8_download_service.py` — 组合 `M3u8Parser` + `M3u8RefreshService` + `M3u8FileManager`，把 m3u8 文件下载到 `temp/` 下用 UUID 命名的临时文件，完成后清理。

浏览器层（Selenium 抽象）：

- `browser/browser_driver.py` — 抽象基类 `BrowserDriver`，统一 `apply_common_options`（`COMMON_BROWSER_ARGS`：禁用 USB 事件日志、忽略证书错误、禁用日志）；`extract_m3u8_links_from_logs` 默认实现适配 Edge/Chrome 的日志格式。
- `browser/{edge,chrome,firefox}_driver.py` — 各浏览器只实现 `create_driver` 与 `get_log`；Firefox 重写 `extract_m3u8_links_from_logs`（性能日志走 `performance.getEntries()` JS 接口）。
- `browser/browser_factory.py` — 按字符串 `edge/chrome/firefox` 选择具体驱动。

下载执行：

- `binary/n_m3u8dl_re.py` — `NM3u8DLRE.download` 通过 `subprocess.run` 调用外部 exe；命令参数 `--save-name/--save-dir/--base-url/--tmp-dir/--log-file-path/--ui-language`，cookie 通过 `-H "Cookie: ..."` 注入。
- `core/m3u8dl_process.py` — 包装 N_m3u8DL-RE 子进程 + 失败分类（9 种 `DownloadFailureKind`）。
- `core/retry_policy.py` — 纯函数重试决策（auth_key 子上限 50，指数退避 2-15s 区间）。

配置与日志：

- `config/yaml_config.py` — `YamlConfig` 单例（双检锁 + `threading.RLock`），`CONFIG_SCHEMA` 定义所有键、类型、可选范围与必填项；`load()` 自动 `_validate_config`。提供 `get / get_str / get_int / get_float / get_bool / get_list / get_dict / get_nested` 类型安全访问。
- `config/constants.py` — `CONFIG_FILE_PATH`（可用 `DINGTALK_DOWNLOADER_CONFIG_PATH` 环境变量覆盖）、浏览器/下载/保存模式常量、`LIVE_NAME_SELECTORS`（直播标题 XPath/CSS 选择器列表）、`MAX_FILE_SIZE=100MB`。
- `config/logger_config.py` — `LoggerConfig.setup_logging()` 幂等；按日生成 `logs/dingtalk_downloader_YYYY-MM-DD.log`，使用 `RotatingFileHandlerWithCleanup`；`clean_old_logs(days)` 按 `logging.retention_days` 删除过期文件。
- `config/header_manager.py` — `HeaderManager` 缓存 YAML 中的 `headers.*`，支持运行时 `_override_headers` 覆盖。

工具与值对象：

- `utils/models.py` — 不可变 dataclass 值对象：`CookieData`、`HeadersData`、`M3u8Link`、`VideoDownloadContext`（后续流程的传参载体）。
- `utils/validator.py` — `validate_dingtalk_url`（校验协议 + 域名 `n.dingtalk.com` + `liveUuid` 必须匹配 `^[a-f0-9\-]{36}$`）、`validate_input`（带默认值的菜单选择）、`validate_required_input`（必填循环）。
- `utils/file_validator.py` — 文件读取前的安全校验：扩展名（`.csv/.xlsx/.xls`）、`MAX_FILE_SIZE`、路径遍历防护（必须在 `Path.cwd()` 内、禁止 `..`）。
- `utils/file_reader.py` — `FileReader.read_links()` 用 pandas 读取 CSV（按 `utf-8/gbk/gb18030/utf-8-sig` 顺序试编码）或 Excel（遍历所有 sheet），提取以 `https://n.dingtalk.com` 开头的字符串，返回 `{row_index: url}`。
- `utils/path_selector.py` — `SAVE_MODE_DEFAULT`（用 `download.default_dir`）或 `SAVE_MODE_MANUAL`（`tkinter.filedialog.askdirectory` 弹窗选目录）。
- `utils/m3u8_file_manager.py` — `download.temp_dir` 解析（绝对路径直接用，相对路径拼 `os.getcwd()`），生成 `{uuid}.m3u8` 临时文件名。
- `utils/path_helper.py` — `clean_file_path`（去引号空格）、`ensure_dir_exists`。

异常集中在 `core/exceptions.py`：`DownloadError / CookieError / M3u8ParseError / FileReaderError / ConfigLoadError / ConfigValidationError / BrowserError / NetworkError / ValidationError`。

## 测试

- 单元测试在 `tests/unit/`（15 个 `test_*.py`），默认 `uv run pytest` 跑全部并出覆盖率
- 集成测试在 `tests/integration/`（3 个端到端测试 + `conftest.py`），需要真实 Edge/Chrome + `assets/bin/N_m3u8DL-RE.exe`，必须显式 `uv run pytest tests/integration/ -v -m integration`
- pytest 配置在 `pyproject.toml:61-77`，`testpaths = ["tests/unit"]`、自动 `--cov-branch`、`--cov-report=term-missing`、`--cov-report=xml:coverage.xml`
- 覆盖率配置在 `pyproject.toml:80-103`，自动从 `src/dingtalk_downloader/**/*.py` 收集；`omit` 排除入口/驱动/logger
- pytest marker `integration` 已在 `pyproject.toml:75-77` 注册；`--strict-markers` 防止拼写错误
- `tests/conftest.py`：`sys.path.insert(0, "src")` 让 `from dingtalk_downloader.xxx import yyy` 工作
- `tests/fixtures/`：共享 fake（`fake_browser` / `fake_proc`）

## 运行流程简图

```
main → single_mode/batch_mode
  ↓
Downloader (core/downloader.py)
  ↓ DependencyFactory 注入
VideoDownloadManager.initialize_download
  ├─ CookieHandler.get_cookie       → Selenium 访问 URL，首次要求手动登录按 Enter
  ├─ HeaderManager.get_headers      ← 来自 config/app.yaml
  └─ M3u8Parser + M3u8DownloadService(M3u8RefreshService) → 从性能日志找 .m3u8，浏览器 JS fetch 拉到 temp/
DownloadOrchestrator.process_video (重试最多 20 次)
  ├─ M3u8DLProcess.run               → subprocess 调 assets/bin/N_m3u8DL-RE.exe
  ├─ RetryPolicy                     → auth_key 子上限 50，指数退避 2-15s
  └─ 成功: mp4 → default_dir / tkinter 弹窗
```

## 修改时的注意事项

- 配置变更需同步修改 `CONFIG_SCHEMA`（类型/必填/范围），否则 `YamlConfig.load()` 会抛 `ConfigValidationError`。
- 依赖变更需同步修改 `pyproject.toml`（`[project] dependencies` 或 `[dependency-groups] dev`）后跑 `uv pip compile` 重新生成 `requirements.txt` / `requirements-dev.txt`，4 个文件一起提交。
- 加新浏览器：实现 `BrowserDriver` 子类并把分支加入 `BrowserFactory`；Firefox 的 m3u8 日志走 `performance.getEntries()`，Edge/Chrome 走 `driver.get_log("performance")`，`extract_m3u8_links_from_logs` 必要时重写。
- `liveUuid` 的 UUID 格式正则（`^[a-f0-9\-]{36}$`）写在 `utils/validator.py`，Selenium 抓日志时也用它过滤无关请求。
- 临时文件由 `M3u8FileManager` 命名（UUID），`DownloadSession.__exit__` 与 `VideoDownloadManager.process_video` 的 `finally` 块都会清理；新流程如复用 m3u8 文件需自行管理生命周期。
- `assets/bin/` 下的 exe 在 Windows 下随仓库发布；非 Windows 平台需自行提供 `n_m3u8dl_re.executable_path` 与 `ffmpeg.executable_path`，命令构建逻辑不区分平台。
- 测试新增：单元测试放 `tests/unit/`，集成测试放 `tests/integration/` 并加 `@pytest.mark.integration`；`pyproject.toml` 的 `testpaths` 默认指向 unit，集成需显式 `-m integration`。
- 基础设施状态：`pyproject.toml`（PEP 735 + hatchling 后端）、`uv.lock`、`tests/{unit,integration,fixtures}/`、`pyproject.toml` 中的 pytest 与 coverage 配置**全部齐全**。
