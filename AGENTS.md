# PROJECT KNOWLEDGE BASE

**Generated:** 2026-03-10
**Commit:** 30a6f58
**Branch:** refactor/20260129

## OVERVIEW

钉钉直播回放下载工具 - Python CLI tool for batch downloading DingTalk live replay videos. Uses Selenium browser automation, M3U8 parsing, and N_m3u8DL-RE for video downloads. Stack: Python 3.8+, Selenium, pytest.

## STRUCTURE

```
DingTalk-Live-Playback-Download-Tool/
├── src/dingtalk_downloader/     # Main package (src layout)
│   ├── core/                    # Business logic: Downloader, CookieHandler, M3u8Parser
│   ├── browser/                 # Browser drivers: Edge, Chrome, Firefox
│   ├── utils/                   # Utilities: validators, file readers, models
│   ├── config/                  # Config: YAML, logging, constants
│   └── binary/                  # External tools: N_m3u8DL-RE wrapper
├── tests/                       # Test suite (pytest)
│   ├── unit/                    # 24 unit test files (mirror src structure)
│   ├── fixtures/                # Test fixtures by domain
│   ├── mocks/                   # Mock utilities
│   └── conftest.py              # Global pytest fixtures
├── assets/bin/                  # External binaries (N_m3u8DL-RE, FFmpeg)
├── docs/tasks/                  # Task lifecycle docs (YYYYMMDD_HHMMSS-task/)
└── pyproject.toml               # Build config, tool settings
```

## WHERE TO LOOK

| Task                 | Location                                         | Notes                                            |
| -------------------- | ------------------------------------------------ | ------------------------------------------------ |
| Entry point          | `src/dingtalk_downloader/main.py`                | CLI entry, `main()` function                     |
| Download logic       | `src/dingtalk_downloader/core/downloader.py`     | Facade for video downloads                       |
| Cookie handling      | `src/dingtalk_downloader/core/cookie_handler.py` | Selenium-based cookie extraction                 |
| M3U8 parsing         | `src/dingtalk_downloader/core/m3u8_parser.py`    | Extract M3U8 from browser logs                   |
| Browser drivers      | `src/dingtalk_downloader/browser/`               | Edge/Chrome/Firefox implementations              |
| Config management    | `src/dingtalk_downloader/config/yaml_config.py`  | Singleton YAML config (531 lines)                |
| Data models          | `src/dingtalk_downloader/utils/models.py`        | Value objects: CookieData, HeadersData, M3u8Link |
| Test fixtures        | `tests/fixtures/`                                | Domain-organized fixtures                        |
| Global pytest config | `tests/conftest.py`                              | Session fixtures, markers                        |

## CODE MAP

| Symbol                 | Type      | Location                         | Role                                     |
| ---------------------- | --------- | -------------------------------- | ---------------------------------------- |
| `Downloader`           | Class     | `core/downloader.py`             | Facade - entry point for downloads       |
| `VideoDownloadManager` | Class     | `core/video_download_manager.py` | Coordinator - orchestrates download flow |
| `CookieHandler`        | Class     | `core/cookie_handler.py`         | Service - extracts cookies via Selenium  |
| `M3u8Parser`           | Class     | `core/m3u8_parser.py`            | Service - parses M3U8 from browser logs  |
| `M3u8DownloadService`  | Class     | `core/m3u8_download_service.py`  | Service - downloads M3U8 files           |
| `DependencyFactory`    | Class     | `core/dependency_factory.py`     | Factory - creates DI instances           |
| `BrowserDriver`        | ABC       | `browser/browser_driver.py`      | Abstract browser driver                  |
| `YamlConfig`           | Class     | `config/yaml_config.py`          | Singleton - config management            |
| `VideoDownloadContext` | DataClass | `utils/models.py`                | DTO for download context                 |
| `NM3u8DLRE`            | Class     | `binary/n_m3u8dl_re.py`          | Wrapper for external binary              |

## CONVENTIONS

- **Source layout**: `src/dingtalk_downloader/` package structure
- **Chinese documentation**: All docstrings, comments, task docs in Chinese
- **File headers**: 12-line docstring with author, dependencies, creation date, modification history
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes
- **Imports**: Standard lib → Third-party → Local (grouped, separated by blank lines)
- **Test naming**: `test_<module>.py` mirrors source module name
- **Line length**: 100 characters (Black config)

## ANTI-PATTERNS (THIS PROJECT)

- **NEVER** suppress type errors with `# type: ignore` or `cast()`
- **NEVER** use `except Exception:` without re-raising specific exceptions
- **NEVER** hardcode browser paths - use `BrowserFactory`
- **NEVER** create browser instances directly - use `DependencyFactory`
- **NEVER** skip resource cleanup - always call `close()` on handlers
- **DO NOT** add new config files without updating `YamlConfig`
- **DO NOT** modify `conftest.py` fixtures without updating all tests

## UNIQUE STYLES

- **Design patterns**: Facade (Downloader), Factory (DependencyFactory, BrowserFactory), Singleton (YamlConfig), Strategy (PathSelector), Value Object (models)
- **Retry mechanism**: Video downloads retry up to 20 times with exponential backoff
- **Browser reuse**: Batch downloads reuse browser instance to reduce overhead
- **Task documentation**: Every task has lifecycle docs in `docs/tasks/YYYYMMDD_HHMMSS-task/`
- **Test markers**: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.browser`, etc.

## COMMANDS

```bash
# Development
python -m src.dingtalk_downloader.main          # Run CLI
pip install -r requirements.txt                  # Install deps
pip install -r requirements-dev.txt              # Install dev deps

# Testing
pytest                                           # Run all tests
pytest tests/unit/                               # Unit tests only
pytest --cov=src --cov-report=html              # Coverage report
pytest -m browser                                # Browser tests only

# Code quality
black src tests                                  # Format code
flake8 src tests --max-line-length=100          # Lint
mypy src --ignore-missing-imports               # Type check

# Build
python -m build                                  # Build package
```

## NOTES

- **Coverage target**: ≥80% (current: ~92%)
- **Python version**: 3.8+ (tested on 3.8-3.11)
- **Browser support**: Edge (default), Chrome, Firefox
- **External dependencies**: N_m3u8DL-RE and FFmpeg in `assets/bin/`
- **Config file**: `config.yaml` must exist for runtime config
- **Test structure**: Tests mirror src structure exactly (`test_downloader.py` → `downloader.py`)
- **Large files**: `yaml_config.py` (531 lines), `test_downloader.py` (864 lines) - complexity hotspots
