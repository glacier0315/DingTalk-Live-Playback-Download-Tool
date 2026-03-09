# CORE MODULE KNOWLEDGE BASE

**Parent:** `src/dingtalk_downloader/`

## OVERVIEW

Core business logic layer - coordinates Cookie extraction, M3U8 parsing, and video downloads. Uses Facade and Factory patterns.

## STRUCTURE

```
core/
├── __init__.py              # Exports: CookieHandler, M3u8Parser, Downloader
├── downloader.py            # Facade - single/batch download entry point
├── video_download_manager.py # Coordinator - orchestrates download flow
├── cookie_handler.py        # Service - Selenium cookie extraction
├── m3u8_parser.py           # Service - extracts M3U8 from browser logs
├── m3u8_download_service.py # Service - downloads and validates M3U8 files
├── dependency_factory.py    # Factory - creates DI instances
├── exceptions.py            # Custom exceptions hierarchy
└── user_interaction_controller.py # UI input handling
```

## WHERE TO LOOK

| Task                | File                        | Key Function/Class                               |
| ------------------- | --------------------------- | ------------------------------------------------ |
| Start download      | `downloader.py`             | `Downloader.download_single_video()`             |
| Coordinate flow     | `video_download_manager.py` | `VideoDownloadManager.process_video()`           |
| Get cookies         | `cookie_handler.py`         | `CookieHandler.get_cookie()`                     |
| Parse M3U8          | `m3u8_parser.py`            | `M3u8Parser.fetch_m3u8_link()`                   |
| Create dependencies | `dependency_factory.py`     | `DependencyFactory.get_*()`                      |
| Handle exceptions   | `exceptions.py`             | `DownloadError`, `CookieError`, `M3u8ParseError` |

## KEY PATTERNS

- **Facade**: `Downloader` hides `VideoDownloadManager`, `CookieHandler`, `M3u8Parser` complexity
- **Factory**: `DependencyFactory` creates and caches service instances
- **Retry**: Video downloads retry up to 20 times with exponential backoff (3-10s wait)
- **Browser reuse**: `repeat_get_cookie()` and `repeat_get_context()` reuse browser instance

## ANTI-PATTERNS (THIS MODULE)

- **NEVER** create services directly - use `DependencyFactory`
- **NEVER** skip `close()` on handlers - causes browser process leaks
- **NEVER** catch `Exception` without re-raising specific types from `exceptions.py`

## DATA FLOW

```
URL → CookieHandler.get_cookie()
    → M3u8Parser.fetch_m3u8_link()
    → M3u8DownloadService.fetch_and_download_m3u8()
    → PathSelector.get_save_dir()
    → NM3u8DLRE.download()
```

## NOTES

- `VideoDownloadManager.process_video()` is the retry loop entry point
- `VideoDownloadContext` (DTO) carries state between stages
- Exception hierarchy: `DownloadError` → `CookieError`, `M3u8ParseError`, `BrowserError`, `NetworkError`
