# UTILS MODULE KNOWLEDGE BASE

**Parent:** `src/dingtalk_downloader/`

## OVERVIEW

Utility functions and data models. Contains validators, file readers, path helpers, and value objects (DTOs).

## STRUCTURE

```
utils/
├── __init__.py         # Re-exports
├── models.py           # Value objects: CookieData, HeadersData, M3u8Link, VideoDownloadContext
├── validator.py        # URL and input validators
├── file_reader.py      # CSV/Excel/TXT file reader
├── file_validator.py   # File existence and format validation
├── path_helper.py      # Path manipulation utilities
├── path_selector.py    # Strategy pattern - default/custom path selection
└── m3u8_file_manager.py # M3U8 temp file management
```

## WHERE TO LOOK

| Task             | File                | Key Function/Class                                              |
| ---------------- | ------------------- | --------------------------------------------------------------- |
| Validate URL     | `validator.py`      | `validate_dingtalk_url()`                                       |
| Validate file    | `file_validator.py` | `validate_file_path()`                                          |
| Read links file  | `file_reader.py`    | `FileReader.read_links()`                                       |
| Select save path | `path_selector.py`  | `PathSelector.get_save_dir()`                                   |
| Get data models  | `models.py`         | `VideoDownloadContext`, `CookieData`, `HeadersData`, `M3u8Link` |

## KEY PATTERNS

- **Value Object**: `CookieData`, `HeadersData`, `M3u8Link` are frozen `@dataclass` (immutable)
- **DTO**: `VideoDownloadContext` carries all download state between modules
- **Strategy**: `PathSelector` switches behavior based on `save_mode` (default/custom)
- **Factory method**: `FileReader` auto-detects format (CSV/Excel/TXT) by extension

## DATA MODELS

```python
@dataclass(frozen=True)
class CookieData:
    cookies: dict[str, str]

@dataclass(frozen=True)
class HeadersData:
    headers: dict[str, str]

@dataclass(frozen=True)
class M3u8Link:
    url: str
    prefix: str
    local_file_path: str | None

@dataclass
class VideoDownloadContext:
    url: str
    cookie_data: CookieData
    headers_data: HeadersData
    live_name: str
    save_dir: str
    save_mode: str
```

## ANTI-PATTERNS (THIS MODULE)

- **NEVER** mutate `CookieData`, `HeadersData`, `M3u8Link` - they are frozen
- **NEVER** bypass `PathSelector` for save directory logic
- **NEVER** add new value objects without updating `models.py`

## NOTES

- `FileReader` strips first row (assumes header) when reading CSV/Excel
- `validate_dingtalk_url()` checks for `https://n.dingtalk.com` prefix and `liveUuid` param
- `M3u8FileManager` handles temp file cleanup after downloads
