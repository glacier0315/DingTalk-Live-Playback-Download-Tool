# BROWSER MODULE KNOWLEDGE BASE

**Parent:** `src/dingtalk_downloader/`

## OVERVIEW

Browser automation layer - abstracts Edge, Chrome, Firefox drivers. Provides unified interface for Selenium operations.

## STRUCTURE

```
browser/
├── __init__.py           # Exports: BrowserFactory
├── browser_driver.py     # ABC - defines interface
├── browser_factory.py    # Factory - creates driver by type
├── edge_driver.py        # Edge implementation
├── chrome_driver.py      # Chrome implementation
└── firefox_driver.py     # Firefox implementation
```

## WHERE TO LOOK

| Task             | File                 | Key Function/Class        |
| ---------------- | -------------------- | ------------------------- |
| Create browser   | `browser_factory.py` | `BrowserFactory.create()` |
| Get interface    | `browser_driver.py`  | `BrowserDriver` (ABC)     |
| Edge-specific    | `edge_driver.py`     | `EdgeDriver`              |
| Chrome-specific  | `chrome_driver.py`   | `ChromeDriver`            |
| Firefox-specific | `firefox_driver.py`  | `FirefoxDriver`           |

## KEY INTERFACE (BrowserDriver)

```python
class BrowserDriver(ABC):
    def get(self, url: str) -> None: ...
    def get_log(self, log_type: str) -> list: ...
    def get_cookies(self) -> list[dict]: ...
    def get_element_by_xpath(self, xpath: str) -> WebElement: ...
    def get_element_by_class_name(self, class_name: str) -> WebElement: ...
    def execute_script(self, script: str) -> Any: ...
    def refresh(self) -> None: ...
    def close(self) -> None: ...
    def extract_m3u8_links_from_logs(self, logs: list, live_uuid: str) -> list[str]: ...
```

## KEY PATTERNS

- **Factory**: `BrowserFactory.create(browser_type)` returns correct driver
- **Strategy**: Each driver implements same interface differently
- **Template method**: Common logic in abstract, specifics in subclasses

## ANTI-PATTERNS (THIS MODULE)

- **NEVER** instantiate drivers directly - use `BrowserFactory`
- **NEVER** bypass `close()` - causes zombie browser processes
- **NEVER** hardcode browser paths - use factory's auto-detection

## BROWSER TYPE CONSTANTS

- `BROWSER_TYPE_EDGE = "edge"` (default)
- `BROWSER_TYPE_CHROME = "chrome"`
- `BROWSER_TYPE_FIREFOX = "firefox"`

## NOTES

- `extract_m3u8_links_from_logs()` parses performance logs for `.m3u8` URLs containing `liveUuid`
- All drivers enable performance logging for M3U8 extraction
- Firefox requires `geckodriver` in PATH or `assets/bin/`
