# M3U8 内容获取 403 错误修复 - 对齐文档

## 1. 原始需求

用户在运行项目下载功能时，当执行 Terminal#102-169 操作过程中出现"获取 M3U8 内容失败"错误。具体错误信息：

```
获取 M3U8 内容失败: 403 Client Error: Forbidden for url: https://dtliving-bj.dingtalk.com/live/31a3e1ed-1614-497c-a4c8-6ae262fe735f_normal.m3u8?auth_key=...
```

## 2. 任务范围

**明确任务范围**：
- 修复 M3U8 内容获取时的 403 Forbidden 错误
- 确保 Cookie 和请求头正确传递到 HTTP 请求中
- 验证修复后的功能能够正常下载 M3U8 文件
- 添加必要的错误处理和日志记录

**不包含**：
- 修改 M3U8 链接提取逻辑（已修复）
- 修改视频下载逻辑（使用 FFmpeg）
- 修改浏览器自动化逻辑

## 3. 需求理解

### 3.1 项目特性规范

**技术栈**：
- Python 3.13
- Selenium 4.6.0+（浏览器自动化）
- requests 2.28.0+（HTTP 请求）
- FFmpeg（视频下载）

**架构模式**：
- 模块化设计，分离关注点
- 错误处理和日志记录
- 测试驱动开发

### 3.2 问题分析

**错误类型**: HTTP 403 Forbidden

**错误位置**: `m3u8_utils.py` 中的 `_fetch_m3u8_content_via_requests` 函数

**根本原因**:
1. 原始代码使用浏览器的 `fetch` API 获取 M3U8 内容，自动携带浏览器的 Cookie 和请求头
2. 重构后的代码使用 Python 的 `requests` 库，但只传递了 `m3u8_headers`（请求头），**没有传递 `cookies_data`（Cookie）**
3. 钉钉的 M3U8 文件需要 Cookie 认证，没有 Cookie 就会返回 403 错误

**代码对比**:

原始代码 ([DingTalk-Live-Playback-Download-Tool.py#L403](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/DingTalk-Live-Playback-Download-Tool.py#L403-L406)):
```python
def download_m3u8_file(url, filename, headers):
    global browser
    m3u8_content = browser.execute_script("return fetch(arguments[0], { method: 'GET', headers: arguments[1] }).then(response => response.text())", url)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(m3u8_content)
    return filename
```

重构后的代码 ([m3u8_utils.py#L622](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_download/m3u8_utils.py#L622)):
```python
def _fetch_m3u8_content_via_requests(
    url: str,
    headers: Dict[str, str]
) -> str:
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    m3u8_content = response.text
    return m3u8_content
```

**调用链分析**:

1. `main.py` 调用 `get_browser_cookie()` 获取 `cookies_data` 和 `m3u8_headers`
2. `main.py` 调用 `download_m3u8_file(link, DEFAULT_M3U8_FILENAME, m3u8_headers)`
3. `download_m3u8_file()` 调用 `_fetch_m3u8_content_via_requests(url, headers)`
4. **问题**: `cookies_data` 没有被传递到 `_fetch_m3u8_content_via_requests()` 函数

### 3.3 疑问澄清

**Q1**: 为什么原始代码不需要显式传递 Cookie？
**A**: 原始代码使用浏览器的 `fetch` API，浏览器会自动携带当前页面的所有 Cookie。

**Q2**: requests 库如何传递 Cookie？
**A**: requests 库支持通过 `cookies` 参数传递 Cookie 字典。

**Q3**: 是否需要修改所有调用链？
**A**: 需要修改：
- `_fetch_m3u8_content_via_requests` 函数签名，添加 `cookies` 参数
- `download_m3u8_file` 函数签名，添加 `cookies` 参数
- `main.py` 中调用 `download_m3u8_file` 的地方，传递 `cookies_data`

## 4. 技术实现方案

### 4.1 修复方案

**方案 1**: 修改函数签名，添加 Cookie 参数（推荐）
- 优点：清晰明确，符合函数式编程原则
- 缺点：需要修改多个函数签名和调用点

**方案 2**: 在 headers 中添加 Cookie 字符串
- 优点：不需要修改函数签名
- 缺点：不符合 HTTP 规范，requests 库有专门的 cookies 参数

**选择方案 1**，因为：
1. 更符合 HTTP 规范和 requests 库的最佳实践
2. 代码更清晰，易于维护
3. 便于测试和调试

### 4.2 实现步骤

1. 修改 `_fetch_m3u8_content_via_requests` 函数，添加 `cookies` 参数
2. 修改 `download_m3u8_file` 函数，添加 `cookies` 参数
3. 修改 `main.py` 中所有调用 `download_m3u8_file` 的地方，传递 `cookies_data`
4. 更新相关文档和测试

### 4.3 技术约束

- 必须保持向后兼容性（如果可能）
- 必须遵循现有的代码规范
- 必须添加适当的错误处理和日志记录
- 必须更新相关的文档和测试

## 5. 验收标准

### 5.1 功能验收

- [ ] 能够成功获取 M3U8 文件内容（不再出现 403 错误）
- [ ] 能够正确解析 M3U8 文件内容
- [ ] 能够成功下载视频文件
- [ ] 所有测试用例通过

### 5.2 质量验收

- [ ] 代码符合项目规范
- [ ] 错误处理完善
- [ ] 日志记录详细
- [ ] 文档更新完整

### 5.3 集成验收

- [ ] 与现有系统无冲突
- [ ] 不引入新的技术债务
- [ ] 性能无明显下降

## 6. 风险评估

### 6.1 技术风险

- **风险**: 修改多个函数签名可能导致调用点遗漏
- **缓解**: 使用 IDE 的重构功能，确保所有调用点都被更新

### 6.2 兼容性风险

- **风险**: 如果有外部代码调用这些函数，可能会破坏兼容性
- **缓解**: 使用可选参数，保持向后兼容性

## 7. 决策记录

| 决策 | 理由 |
|------|------|
| 使用方案 1（修改函数签名） | 更符合 HTTP 规范和 requests 库的最佳实践 |
| 添加 cookies 参数而非修改 headers | requests 库有专门的 cookies 参数，更规范 |
| 保持向后兼容性 | 使用可选参数，避免破坏现有代码 |

## 8. 下一步

进入 **Architect（架构阶段）**，设计详细的修复方案和实现细节。
