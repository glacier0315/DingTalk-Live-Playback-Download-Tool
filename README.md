# DingTalk-Live-Playback-Download-Tool

钉钉直播回放下载工具：通过 Selenium 自动化浏览器获取登录态 Cookie，从性能日志解析 m3u8 链接，再调用本地 `N_m3u8DL-RE.exe` 子进程下载视频。

## 特性

- **两种下载模式**：单条链接 / CSV+Excel 批量（按行号记录 URL，自动跳过空行）
- **3 个浏览器驱动**：Edge / Chrome / Firefox 任选（Selenium 4.40+ 自动管理驱动）
- **智能重试**：auth_key 过期、403、网络瞬断、进程启动失败分类退避，单视频最多 20 次重试、30 分钟超时
- **URL 严格校验**：仅接受 `https://n.dingtalk.com/...?liveUuid=<UUID>` 格式
- **uv 管理依赖**：锁文件 `uv.lock` 跨机器一致，开发用 Python 3.14、生产兼容 3.12+

## 环境要求

| 依赖     | 版本                                                       |
| -------- | ---------------------------------------------------------- |
| Python   | **>= 3.12**（开发环境用 3.14）                             |
| 操作系统 | **Windows 10/11**（自带 `N_m3u8DL-RE.exe` / `ffmpeg.exe`） |
| 浏览器   | Edge / Chrome / Firefox 任一（已登录钉钉账户）             |
| 包管理   | [uv](https://docs.astral.sh/uv/) 0.5+                      |

> 非 Windows 平台需自行编译/下载 N_m3u8DL-RE 与 ffmpeg，修改 `config/app.yaml` 的 `n_m3u8dl_re.executable_path` 与 `ffmpeg.executable_path`。

## 安装

```bash
# 推荐：uv 自动创建 .venv 并安装全部依赖（含 dev）
uv sync --group dev

# 验证
uv run python -c "import dingtalk_downloader; print(dingtalk_downloader.__version__)"
# 预期输出: 1.5.0
```

无 uv 时备选：

```bash
pip install -r requirements.txt
pip install pytest
```

## 依赖管理

本项目以 `pyproject.toml` 为源真值；`uv.lock` 是锁定的依赖图，`requirements.txt` / `requirements-dev.txt` 仅作 `pip` 兼容的 fallback，由 uv 从 `pyproject.toml` 重新生成。

### 从 pyproject.toml 重新生成 requirements 文件

```bash
# 运行时依赖
uv pip compile pyproject.toml -o requirements.txt

# 开发/测试依赖（PEP 735 dependency-group）
uv pip compile --group dev -o requirements-dev.txt
```

修改 `pyproject.toml`（`[project] dependencies` 或 `[dependency-groups] dev`）后跑一次上述命令，把 `pyproject.toml`、`uv.lock`、`requirements.txt`、`requirements-dev.txt` 四个文件一起提交即可保持一致。

> CI / 容器环境若没有 uv，可直接用 `pip install -r requirements.txt -r requirements-dev.txt` 装好所有依赖。

## 快速开始

```bash
# 方式一：控制台脚本（uv 激活 .venv 后）
uv run dingtalk-downloader

# 方式二：模块入口（开发推荐）
uv run python -m src.dingtalk_downloader.main

# 方式三：传统方式（已激活 .venv 时）
python -m src.dingtalk_downloader.main
```

按提示选择模式：

1. **单个下载**：依次输入 URL → 保存模式 → 浏览器类型
2. **批量下载**：输入 CSV/Excel 路径（可拖放文件）→ 程序自动提取所有钉钉链接 → 依次下载

**首次运行**：浏览器弹出后**手动登录钉钉账户**，登录完成后回到终端按 Enter 键继续。后续 Cookie 自动复用。

## 使用说明

### 模式选择

| 选项 | 含义                 |
| ---- | -------------------- |
| `1`  | 单个视频下载（默认） |
| `2`  | 批量下载             |

### 浏览器类型（每个 session 问一次）

| 选项 | 浏览器       |
| ---- | ------------ |
| `1`  | Edge（默认） |
| `2`  | Chrome       |
| `3`  | Firefox      |

### 保存模式

| 选项 | 含义                                                                |
| ---- | ------------------------------------------------------------------- |
| `1`  | 用 `config/app.yaml` 的 `download.default_dir`（默认 `Downloads/`） |
| `2`  | 弹 tkinter 原生窗口手动选目录（**需要桌面 GUI**）                   |

### 批量模板

`assets/template/批量下载模板.xlsx` 8.8 KB，**不依赖特定列名**——把钉钉回放 URL 粘到任意单元格即可，程序会扫描所有 sheet、所有单元格，自动提取以 `https://n.dingtalk.com` 开头的字符串。CSV 同理。

## 配置

`config/app.yaml` 全部键启动时 schema 校验（缺/类型错/超范围 抛 `ConfigValidationError`）。顶层 7 节：

| 段            | 关键键                                                            | 默认                                  |
| ------------- | ----------------------------------------------------------------- | ------------------------------------- |
| `app`         | `name` / `version` / `build_date`                                 | 项目横幅                              |
| `download`    | `default_dir` / `temp_dir` / `max_retry_count`                    | `Downloads` / `temp` / `5`            |
| `browser`     | `default_type` / `headless` / `timeout`                           | `edge` / `false` / `30`               |
| `logging`     | `level` / `dir` / `max_bytes` / `backup_count` / `retention_days` | `INFO` / `logs` / `10MB` / `5` / `30` |
| `headers`     | `user_agent` / `referer` / `accept_*` / `sec_fetch_*`             | 见 YAML                               |
| `n_m3u8dl_re` | `executable_path` / `ui_language` / `temp_dir` / `log_dir`        | `assets/bin/N_m3u8DL-RE.exe`          |
| `ffmpeg`      | `executable_path`                                                 | `assets/bin/ffmpeg.exe`               |

**覆盖配置路径**（优先级高于 `config/app.yaml`）：

```bash
# Windows CMD
set DINGTALK_DOWNLOADER_CONFIG_PATH=D:\path\to\app.yaml
# PowerShell
$env:DINGTALK_DOWNLOADER_CONFIG_PATH="D:\path\to\app.yaml"
# Git Bash / WSL
export DINGTALK_DOWNLOADER_CONFIG_PATH=/path/to/app.yaml
```

## 架构

```text
URL 输入 ──→ CookieHandler (Selenium)
                ↓ 手动登录(首次) / 自动复用(后续)
                ↓ Performance 日志抓 m3u8
              M3u8Parser / M3u8RefreshService
                ↓ UUID 命名的 .m3u8 落到 temp/
              M3u8DLProcess (subprocess.run)
                ↓ 命令: N_m3u8DL-RE.exe <m3u8> --save-name ... -H "Cookie: ..."
                ↓ 失败分类: DownloadFailureKind
              RetryPolicy (max_attempts=20, run_timeout=30min)
                ↓ 成功: mp4 → default_dir / 选目录
                ↓ ABORT: 退出本次
```

**核心模块**（`src/dingtalk_downloader/`）：

| 模块                                                 | 职责                                                                      |
| ---------------------------------------------------- | ------------------------------------------------------------------------- |
| `core/downloader.py`                                 | 外观类，组合各组件                                                        |
| `core/download_orchestrator.py`                      | 单次下载状态机（拉 m3u8 → 启动子进程 → 监控 → 失败刷新 → 续传）           |
| `core/download_session.py`                           | context manager；`with` 出自动关浏览器 + 清理 `temp/*.m3u8`               |
| `core/m3u8dl_process.py`                             | 包装 N_m3u8DL-RE 子进程 + 失败分类（9 种 `DownloadFailureKind`）          |
| `core/retry_policy.py`                               | 纯函数重试决策（auth_key 子上限 50，指数退避 2-15s 区间）                 |
| `core/cookie_handler.py`                             | Selenium 上下文管理器（首次需 `input()` 等登录）                          |
| `core/dependency_factory.py`                         | 工厂 + 单例缓存（cookie*handler*{browser} 等 key）                        |
| `browser/{edge,chrome,firefox}_driver.py`            | 各浏览器实现；Firefox 走 `performance.getEntries()` JS 接口               |
| `binary/n_m3u8dl_re.py`                              | 命令构建（`--save-name/--save-dir/--base-url/--tmp-dir/--log-file-path`） |
| `config/yaml_config.py`                              | YamlConfig 单例（双检锁 + schema 校验）                                   |
| `utils/{file_reader,validator,path_selector,...}.py` | CSV/Excel 读取、URL/输入校验、tkinter 路径选择                            |

## 开发

### 单元测试

```bash
# 跑全部单元测试（15 个 test_*.py，自动覆盖率）
uv run pytest -v

# 仅收集（不执行）
uv run pytest --collect-only
```

默认走 `pyproject.toml` 的 `testpaths = ["tests/unit"]`，自动启用分支覆盖率（`--cov-branch`、`--cov-report=term-missing`、`--cov-report=xml:coverage.xml`）。

### 集成测试

集成测试需要真实 Edge / Chrome 浏览器 + `assets/bin/N_m3u8DL-RE.exe`，CI 默认跳过。

```bash
# 集成测试（需真实环境）
uv run pytest tests/integration/ -v -m integration
```

### 覆盖率报告

`pyproject.toml` 已预置 coverage 配置，常用命令：

```bash
# 控制台 + 缺失行号（默认）
uv run pytest

# HTML 报告（输出到 htmlcov/index.html）
uv run pytest --cov-report=html

# XML 报告（CI 集成用，coverage.xml）
uv run pytest --cov-report=xml

# 阈值闸门（示例：80%）
uv run pytest --cov-fail-under=80
```

### 测试结构

- `tests/unit/`：15 个 `test_*.py`，覆盖 retry_policy / failure_classifier / m3u8dl_process / models / yaml_config / n_m3u8dl_re / download_session / download_orchestrator / file_validator / validator / dependency_factory / video_download_manager / m3u8_refresh_service / exceptions / fake_proc 等核心模块
- `tests/integration/`：3 个端到端测试 + `conftest.py`，需要 `N_m3u8DL-RE.exe` 与真实浏览器环境
- `tests/conftest.py`：`sys.path.insert(0, "src")` 让 `from dingtalk_downloader.xxx import yyy` 工作
- `tests/fixtures/`：共享 fake（`fake_browser` / `fake_proc`）

> 本项目未内置 `ruff` / `mypy` 配置。贡献者本地可在 IDE 启用两者，缓存目录 `.ruff_cache/` / `.mypy_cache/` 已在 `.gitignore`。

## 已知限制

- **Windows-only 二进制**：`assets/bin/*.exe`（N_m3u8DL-RE 16.6 MB / ffmpeg 10.9 MB），其他平台需自行替换并改 YAML
- **首次需 GUI 登录**：第二次以后自动复用 Cookie；保存模式 2 弹 tkinter 窗口（SSH/容器无 GUI 会失败）
- **URL 严格格式**：仅 `https://n.dingtalk.com/...&liveUuid=<UUID>`（`liveUuid` 必须匹配 `^[a-f0-9\-]{36}$`）
- **配置文件所有键必填**：删任意一段都会启动失败；用环境变量 `DINGTALK_DOWNLOADER_CONFIG_PATH` 切换配置
- **m3u8 临时文件**：`temp/<uuid>.m3u8` 在 `DownloadSession.__exit__` 时自动删除；若进程强杀可能残留

## 目录结构

```text
DingTalk-Live-Playback-Download-Tool/
├── src/dingtalk_downloader/   # 源码（main / core / browser / binary / config / utils）
├── tests/{unit,integration}  # 单元 + 集成测试
├── config/app.yaml            # 运行时配置
├── assets/
│   ├── bin/                   # N_m3u8DL-RE.exe + ffmpeg.exe
│   ├── template/批量下载模板.xlsx
│   └── ICO/
├── Downloads/                 # 默认下载输出
├── logs/                      # 运行日志（按日滚动）
├── temp/                      # m3u8 临时文件
├── pyproject.toml             # 项目元数据 + 依赖
├── uv.lock                    # 锁定的依赖图
├── .python-version            # 3.14
├── requirements.txt           # pip 兼容 fallback
└── README.md
```

## License

MIT
