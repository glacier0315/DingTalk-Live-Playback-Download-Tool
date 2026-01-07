# 原始代码与重构代码对比分析报告

## 问题概述

根据终端日志 Terminal#449-500，程序在 5 次尝试后仍然无法获取 M3U8 链接。每次尝试都获取到了日志（3150、167、236、223、210 条），但都没有找到包含 M3U8 的请求链接。

## 关键差异分析

### 1. 浏览器配置差异

#### 原始代码（DingTalk-Live-Playback-Download-Tool.py 第 104-115 行）

```python
edge_options = webdriver.EdgeOptions()
edge_options.add_argument('--disable-usb-device-event-log')
edge_options.add_argument('--ignore-certificate-errors')
edge_options.add_argument('--disable-logging')          # ⚠️ 禁用日志
edge_options.add_argument('--disable_ssl_verification')
edge_options.add_argument('--log-level=3')               # ⚠️ 日志级别设置为 3
edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
edge_options.set_capability("ms:loggingPrefs", {"performance": "ALL"})  # ✅ 启用性能日志
```

#### 重构后代码（browser.py 第 282-290 行）

```python
edge_options = webdriver.EdgeOptions()
edge_options.add_argument('--disable-usb-device-event-log')
edge_options.add_argument('--ignore-certificate-errors')
edge_options.add_argument('--disable-logging')          # ⚠️ 禁用日志
edge_options.add_argument('--disable_ssl_verification')
edge_options.add_argument('--log-level=3')               # ⚠️ 日志级别设置为 3
edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
edge_options.set_capability("ms:loggingPrefs", {"performance": "ALL"})  # ✅ 启用性能日志
```

**分析**：浏览器配置完全一致，不是问题所在。

### 2. 日志获取方式差异

#### 原始代码（DingTalk-Live-Playback-Download-Tool.py 第 328-342 行）

```python
for attempt in range(5):
    try:
        if browser_type == 'chrome' or browser_type == 'edge':
            logs = browser.get_log("performance")  # ✅ 直接获取性能日志
        elif browser_type == 'firefox':
            logs = browser.execute_script("""
                var performance = window.performance || window.mozPerformance || 
                                  window.msPerformance || window.webkitPerformance || {};
                var network = performance.getEntries() || {};
                return network;
            """)
        
        for log in logs:
            # 处理日志...
```

#### 重构后代码（m3u8_utils.py 第 360-405 行）

```python
for attempt in range(MAX_RETRY_ATTEMPTS):
    try:
        logs = _get_browser_logs(browser_instance, browser_type)  # ✅ 通过函数获取日志
        
        for idx, log in enumerate(logs):
            m3u8_url = _process_log_entry(log, browser_type, live_uuid)
            # 处理日志...
```

**分析**：日志获取方式基本一致，重构后代码通过函数封装，逻辑更清晰。

### 3. 日志解析逻辑差异

#### 原始代码（DingTalk-Live-Playback-Download-Tool.py 第 353-373 行）

```python
for log in logs:
    try:
        if browser_type == 'firefox':
            # Firefox 处理逻辑
            log_message = str(log)
            pattern = r'https://[^,\'"]+\.m3u8\?[^\'"]+'
            found_links = re.findall(pattern, log_message)
            
            if found_links:
                cleaned_link = re.sub(r'[\]\s\\\'"]+$', '', found_links[0])
                m3u8_links.append(cleaned_link)
                print(f"获取到m3u8链接: {cleaned_link}")
                return m3u8_links
        
        else:  # Chrome 和 Edge
            if 'message' in log:
                log_message = log['message']
            else:
                log_message = str(log)
            
            if '.m3u8' in log_message:
                start_idx = log_message.find("url:\"") + len("url:\"")
                end_idx = log_message.find("\"", start_idx)
                m3u8_url = log_message[start_idx:end_idx]
                
                if live_uuid in m3u8_url:
                    print(f"获取到m3u8链接: {m3u8_url}")
                    m3u8_links.append(m3u8_url)
                    return m3u8_links
```

#### 重构后代码（m3u8_utils.py 第 259-316 行）

```python
def _parse_chrome_edge_log(log_message: str, live_uuid: str) -> Optional[str]:
    if M3U8_FILE_EXTENSION not in log_message:
        return None
    
    try:
        start_idx = log_message.find("url:\"")
        
        if start_idx == -1:
            logger.debug("日志消息中未找到 'url:\\\"' 模式")
            return None
        
        start_idx += len("url:\"")
        end_idx = log_message.find("\"", start_idx)
        
        if end_idx == -1 or end_idx <= start_idx:
            logger.debug(f"无法找到有效的 URL 结束位置，start_idx={start_idx}, end_idx={end_idx}")
            return None
        
        m3u8_url = log_message[start_idx:end_idx]
        
        if live_uuid in m3u8_url:
            logger.info(f"从 Chrome/Edge 日志中提取到 M3U8 链接: {m3u8_url}")
            return m3u8_url
        else:
            logger.debug(f"找到的 M3U8 链接不包含 liveUuid: {live_uuid}")
            return None
```

**分析**：重构后的代码增加了更多的错误检查和日志，但核心逻辑是一致的。

## 根本原因分析

### 问题 1：日志中可能没有 M3U8 请求

根据终端日志，程序获取到了大量日志（3150、167、236、223、210 条），但没有找到包含 M3U8 的请求链接。这可能是因为：

1. **视频还没有开始加载**：用户登录后，视频可能还没有开始播放，因此没有 M3U8 请求
2. **日志配置问题**：虽然启用了性能日志，但可能某些网络请求没有被捕获
3. **日志时机问题**：获取日志的时机可能太早，视频请求还没有发生

### 问题 2：原始代码的注释显示有被禁用的日志配置

原始代码中有被注释掉的日志配置：

```python
# 启用浏览器日志，获取网络请求
# edge_options.set_capability("ms:loggingPrefs", {
#     'browser': 'ALL',       # 启用浏览器日志
#     'performance': 'ALL'    # 启用性能日志
# })
```

这表明原始代码的作者可能尝试过不同的日志配置，最终只启用了 `performance` 日志。

### 问题 3：日志格式可能不同

重构后的代码假设日志格式是：
```json
{
  "message": "{\"message\":{\"method\":\"Network.requestWillBeSent\",\"params\":{\"request\":{\"url\":\"...\"}}}}"
}
```

但实际的日志格式可能不同，导致无法正确解析。

## 解决方案

### 方案 1：添加日志保存功能

在获取日志后，将日志保存到文件中，便于分析：

```python
def _save_logs_for_debugging(logs: List, browser_type: str, attempt: int) -> None:
    """保存日志到文件用于调试。"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"Logs/browser_logs_{browser_type}_attempt{attempt}_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
        logger.info(f"日志已保存到: {filename}")
    except Exception as e:
        logger.error(f"保存日志失败: {e}")
```

### 方案 2：增加日志详细程度

在 `_process_log_entry` 函数中添加更详细的日志：

```python
def _process_log_entry(log: Dict, browser_type: str, live_uuid: str) -> Optional[str]:
    try:
        if browser_type == 'firefox':
            log_message = str(log)
            logger.debug(f"处理 Firefox 日志条目，长度: {len(log_message)}")
            
            # 添加：显示前 100 个字符
            if len(log_message) > 0:
                logger.debug(f"日志内容前 100 字符: {log_message[:100]}")
            
            return _parse_firefox_log(log_message)
        else:
            if isinstance(log, dict) and 'message' in log:
                log_message = log['message']
                logger.debug(f"处理 Chrome/Edge 日志条目，message 长度: {len(log_message)}")
                
                # 添加：显示前 100 个字符
                if len(log_message) > 0:
                    logger.debug(f"日志内容前 100 字符: {log_message[:100]}")
            else:
                log_message = str(log)
                logger.debug(f"处理 Chrome/Edge 日志条目（非字典），长度: {len(log_message)}")
            
            return _parse_chrome_edge_log(log_message, live_uuid)
    
    except Exception as e:
        logger.warning(f"处理日志条目时发生错误: {e}")
        return None
```

### 方案 3：添加等待时间

在获取日志之前，添加等待时间，确保视频已经开始加载：

```python
def fetch_m3u8_links(
    browser_instance: browser.webdriver.Remote,
    browser_type: str,
    dingtalk_url: str
) -> Optional[List[str]]:
    # ... 前面的代码 ...
    
    for attempt in range(MAX_RETRY_ATTEMPTS):
        try:
            # 添加：等待视频开始加载
            logger.info("等待视频开始加载...")
            time.sleep(5)  # 等待 5 秒
            
            logs = _get_browser_logs(browser_instance, browser_type)
            # ... 后面的代码 ...
```

### 方案 4：尝试点击播放按钮

在获取日志之前，尝试点击播放按钮：

```python
def _click_play_button(browser_instance: browser.webdriver.Remote) -> bool:
    """尝试点击播放按钮。"""
    try:
        # 尝试多种方式找到播放按钮
        play_button = browser_instance.find_element(By.CSS_SELECTOR, "video")
        browser_instance.execute_script("arguments[0].play();", play_button)
        logger.info("成功点击播放按钮")
        return True
    except Exception as e:
        logger.warning(f"点击播放按钮失败: {e}")
        return False
```

## 推荐的修复步骤

1. **添加日志保存功能**：将获取到的日志保存到文件，便于分析
2. **增加日志详细程度**：在处理日志时输出更多调试信息
3. **添加等待时间**：在获取日志前等待一段时间，确保视频已经开始加载
4. **尝试点击播放按钮**：主动触发视频播放，确保 M3U8 请求发生
5. **分析实际日志格式**：使用调试工具分析实际获取到的日志格式

## 相关文件

- [DingTalk-Live-Playback-Download-Tool.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/DingTalk-Live-Playback-Download-Tool.py)
- [m3u8_utils.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_download/m3u8_utils.py)
- [browser.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/src/dingtalk_download/browser.py)

## 调试工具

已创建以下调试工具：

1. **[analyze_browser_logs.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/bin/analyze_browser_logs.py)**：分析浏览器日志格式和内容
2. **[debug_m3u8.py](file:///d:/dev/works/git/github/DingTalk-Live-Playback-Download-Tool/bin/debug_m3u8.py)**：测试 M3U8 链接获取功能

## 下一步行动

1. 运行 `python bin/analyze_browser_logs.py` 分析实际日志格式
2. 根据分析结果调整日志解析逻辑
3. 实施推荐的修复方案
4. 测试验证修复效果
