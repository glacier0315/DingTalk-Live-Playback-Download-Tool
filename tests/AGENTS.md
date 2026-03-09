# TESTS MODULE KNOWLEDGE BASE

**Parent:** Project root

## OVERVIEW

Test suite using pytest with 92% coverage. Mirrors src structure. Uses fixtures organized by domain.

## STRUCTURE

```
tests/
├── conftest.py              # Global fixtures, pytest hooks, markers
├── unit/                    # 24 unit test files (mirror src structure)
│   ├── test_downloader.py   # 864 lines, 24+ test cases
│   ├── test_yaml_config.py  # 577 lines
│   └── ...                  # test_<module>.py → <module>.py
├── integration/             # Integration tests
├── fixtures/                # Domain-organized test fixtures
│   ├── browser_fixtures.py  # Browser driver mocks
│   ├── cookie_fixtures.py   # Cookie data samples
│   ├── file_fixtures.py     # CSV/Excel/M3U8 files
│   └── mock_fixtures.py     # HTTP, subprocess, logger mocks
└── mocks/                   # Mock utility classes
    ├── mock_browser.py      # BrowserDriver mock
    ├── mock_network.py      # Network response mock
    └── mock_binary.py       # Binary tool mock
```

## WHERE TO LOOK

| Task             | File                           | Notes                           |
| ---------------- | ------------------------------ | ------------------------------- |
| Global fixtures  | `conftest.py`                  | Session/function scope fixtures |
| Mock browser     | `mocks/mock_browser.py`        | `MockBrowserDriver` class       |
| Browser fixtures | `fixtures/browser_fixtures.py` | Driver instances with behavior  |
| Test markers     | `conftest.py:346-359`          | Custom pytest markers           |

## TEST FILE TEMPLATE

```python
"""
钉钉直播回放下载工具 - <module_name> 单元测试

本模块测试<module_description>类。

作者：项目团队
依赖：pytest, pytest-mock
创建日期：YYYY-MM-DD
修改历史：
- YYYY-MM-DD: 初始版本
"""

import sys
from unittest.mock import MagicMock, Mock, patch
import pytest

sys.path.insert(0, "src")
```

## FIXTURE NAMING CONVENTIONS

| Pattern    | Example                   | Purpose         |
| ---------- | ------------------------- | --------------- |
| `sample_*` | `sample_cookies`          | Test data       |
| `mock_*`   | `mock_edge_driver`        | Mock objects    |
| `*_with_*` | `sample_csv_with_headers` | Variants        |
| `*_error`  | `mock_network_error`      | Error scenarios |

## PYTEST MARKERS

```python
@pytest.mark.unit          # Unit tests
@pytest.mark.integration   # Integration tests
@pytest.mark.browser       # Browser-related tests
@pytest.mark.network       # Network-related tests
@pytest.mark.slow          # Slow tests
```

## ANTI-PATTERNS (THIS MODULE)

- **NEVER** modify `conftest.py` without updating all dependent tests
- **NEVER** use `Mock(spec=None)` - always specify spec for type safety
- **NEVER** skip teardown in browser tests - causes process leaks

## NOTES

- Tests mirror src: `test_downloader.py` tests `downloader.py`
- Coverage target: ≥80% (current: ~92%)
- Use `pytest -m unit` for fast unit test runs
- Large files: `test_downloader.py` (864 lines), `test_yaml_config.py` (577 lines)
