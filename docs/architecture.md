# 项目架构图和流程图

本文档包含 DingTalk-Live-Playback-Download-Tool 项目的各种架构图和流程图，帮助开发者和用户更好地理解系统结构和工作流程。

## 目录

- [1. 项目整体架构图](#1-项目整体架构图)
- [2. 核心业务流程图](#2-核心业务流程图)
- [3. 批量处理流程图](#3-批量处理流程图)
- [4. 模块依赖关系图](#4-模块依赖关系图)
- [5. 数据流向图](#5-数据流向图)
- [6. Cookie 获取流程图](#6-cookie获取流程图)
- [7. M3U8 解析流程图](#7-m3u8解析流程图)
- [8. 视频下载流程图](#8-视频下载流程图)

---

## 1. 项目整体架构图

```mermaid
graph TB
    subgraph "用户界面层"
        A[用户输入<br/>钉钉链接/Excel文件]
        B[命令行界面<br/>main.py]
    end

    subgraph "核心业务层"
        C[下载器<br/>Downloader]
        D[Cookie处理器<br/>CookieHandler]
        E[M3U8解析器<br/>M3u8Parser]
    end

    subgraph "浏览器自动化层"
        F[浏览器工厂<br/>BrowserFactory]
        G[Edge驱动<br/>EdgeDriver]
        H[Chrome驱动<br/>ChromeDriver]
        I[Firefox驱动<br/>FirefoxDriver]
    end

    subgraph "工具层"
        J[文件读取器<br/>FileReader]
        K[路径工具<br/>PathUtils]
        L[字符串工具<br/>StringUtils]
        M[验证器<br/>Validator]
    end

    subgraph "二进制工具层"
        N[N_m3u8DL-RE<br/>M3U8下载器]
        O[FFmpeg<br/>视频处理工具]
    end

    subgraph "配置层"
        P[常量定义<br/>constants.py]
        Q[配置管理<br/>settings.py]
    end

    subgraph "外部依赖"
        R[钉钉网站]
        S[本地文件系统]
    end

    A --> B
    B --> C
    B --> J

    C --> D
    C --> E
    C --> N
    C --> O

    D --> F
    F --> G
    F --> H
    F --> I
    D --> R

    E --> N

    J --> M
    C --> K
    C --> L

    N --> S
    O --> S

    C --> P
    C --> Q

    style A fill:#e1f5ff
    style B fill:#e1f5ff
    style C fill:#fff4e1
    style D fill:#fff4e1
    style E fill:#fff4e1
    style F fill:#f0e1ff
    style G fill:#f0e1ff
    style H fill:#f0e1ff
    style I fill:#f0e1ff
    style J fill:#e1ffe1
    style K fill:#e1ffe1
    style L fill:#e1ffe1
    style M fill:#e1ffe1
    style N fill:#ffe1e1
    style O fill:#ffe1e1
    style P fill:#ffe1f0
    style Q fill:#ffe1f0
```

### 架构说明

项目采用分层架构设计，共分为 6 个主要层次：

1. **用户界面层**：负责接收用户输入和提供命令行交互
2. **核心业务层**：实现下载、Cookie 处理、M3U8 解析等核心功能
3. **浏览器自动化层**：提供浏览器驱动管理和自动化操作
4. **工具层**：提供文件操作、路径处理、字符串处理等通用功能
5. **二进制工具层**：集成 N_m3u8DL-RE 和 FFmpeg 等专业工具
6. **配置层**：管理项目配置和常量定义

---

## 2. 核心业务流程图

```mermaid
flowchart TD
    Start([开始]) --> Input[用户输入钉钉直播回放链接]
    Input --> ValidateLink{验证链接格式}
    ValidateLink -->|无效| Error1[显示错误信息]
    Error1 --> End([结束])

    ValidateLink -->|有效| CheckCookie{检查Cookie}
    CheckCookie -->|Cookie存在| ParseM3U8[解析M3U8视频流]
    CheckCookie -->|Cookie不存在| GetCookie[获取Cookie]

    GetCookie --> LaunchBrowser[启动浏览器]
    LaunchBrowser --> Navigate[导航到钉钉页面]
    Navigate --> Login{用户登录?}
    Login -->|未登录| WaitLogin[等待用户手动登录]
    WaitLogin --> ExtractCookie[提取Cookie]
    Login -->|已登录| ExtractCookie

    ExtractCookie --> SaveCookie[保存Cookie到本地]
    SaveCookie --> ParseM3U8

    ParseM3U8 --> CheckM3U8{M3U8解析成功?}
    CheckM3U8 -->|失败| Error2[显示解析错误]
    Error2 --> End

    CheckM3U8 -->|成功| DownloadVideo[下载视频]
    DownloadVideo --> UseNM3u8DL[使用N_m3u8DL-RE下载]
    UseNM3u8DL --> CheckDownload{下载完成?}

    CheckDownload -->|失败| Error3[显示下载错误]
    Error3 --> End

    CheckDownload -->|成功| MergeVideo[合并视频片段]
    MergeVideo --> UseFFmpeg[使用FFmpeg合并]
    UseFFmpeg --> CheckMerge{合并成功?}

    CheckMerge -->|失败| Error4[显示合并错误]
    Error4 --> End

    CheckMerge -->|成功| Success[显示下载成功]
    Success --> End

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style Error1 fill:#FFB6C1
    style Error2 fill:#FFB6C1
    style Error3 fill:#FFB6C1
    style Error4 fill:#FFB6C1
    style Success fill:#90EE90
```

### 流程说明

核心业务流程包含以下关键步骤：

1. **输入验证**：验证用户输入的钉钉链接格式是否正确
2. **Cookie 管理**：检查本地 Cookie，如不存在则启动浏览器获取
3. **M3U8 解析**：解析钉钉直播回放的 M3U8 视频流地址
4. **视频下载**：使用 N_m3u8DL-RE 工具下载视频片段
5. **视频合并**：使用 FFmpeg 工具将下载的视频片段合并为完整视频
6. **结果反馈**：向用户显示下载结果或错误信息

---

## 3. 批量处理流程图

```mermaid
flowchart TD
    Start([开始]) --> SelectMode{选择下载模式}

    SelectMode -->|单个链接| SingleLink[输入单个钉钉链接]
    SelectMode -->|批量下载| BatchMode[选择批量下载]

    BatchMode --> SelectFile[选择Excel/CSV文件]
    SelectFile --> ReadFile[读取文件内容]
    ReadFile --> ValidateFile{文件格式验证}

    ValidateFile -->|失败| Error1[显示文件格式错误]
    Error1 --> End([结束])

    ValidateFile -->|成功| ExtractLinks[提取所有链接]
    ExtractLinks --> CountLinks{链接数量}

    CountLinks -->|0| Error2[文件中无有效链接]
    Error2 --> End

    CountLinks -->|>0| ProcessLoop[开始循环处理]

    ProcessLoop --> GetLink[获取下一个链接]
    GetLink --> ValidateLink{验证链接}

    ValidateLink -->|无效| SkipLink[跳过该链接]
    SkipLink --> CheckNext{还有链接?}

    ValidateLink -->|有效| ProcessLink[处理单个链接]
    ProcessLink --> Download[执行下载流程]
    Download --> RecordResult[记录下载结果]
    RecordResult --> CheckNext

    CheckNext -->|是| ProcessLoop
    CheckNext -->|否| GenerateReport[生成批量下载报告]

    GenerateReport --> ShowSummary[显示下载摘要]
    ShowSummary --> End

    SingleLink --> ProcessLink

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style Error1 fill:#FFB6C1
    style Error2 fill:#FFB6C1
    style ShowSummary fill:#90EE90
```

### 流程说明

批量处理流程支持两种模式：

1. **单个链接模式**：直接处理单个钉钉直播回放链接
2. **批量下载模式**：从 Excel/CSV 文件中读取多个链接并批量处理

批量处理特点：

- 支持 Excel 和 CSV 文件格式
- 自动验证文件格式和链接有效性
- 循环处理每个链接
- 记录每个链接的处理结果
- 生成批量下载报告和摘要

---

## 4. 模块依赖关系图

```mermaid
graph TD
    subgraph "主程序"
        MAIN[main.py]
    end

    subgraph "核心模块 core"
        DOWNLOADER[downloader.py]
        COOKIE[cookie_handler.py]
        M3U8[m3u8_parser.py]
    end

    subgraph "浏览器模块 browser"
        FACTORY[browser_factory.py]
        EDGE[edge_driver.py]
        CHROME[chrome_driver.py]
        FIREFOX[firefox_driver.py]
    end

    subgraph "工具模块 utils"
        FILEREADER[file_reader.py]
        PATH[path_helper.py]
        VALIDATOR[validator.py]
    end

    subgraph "二进制模块 binary"
        NM3U8DL[n_m3u8dl_re.py]
        FFMPEG[ffmpeg_wrapper.py]
    end

    subgraph "配置模块 config"
        CONSTANTS[constants.py]
        SETTINGS[settings.py]
    end

    MAIN --> DOWNLOADER
    MAIN --> FILEREADER
    MAIN --> VALIDATOR

    DOWNLOADER --> COOKIE
    DOWNLOADER --> M3U8
    DOWNLOADER --> NM3U8DL
    DOWNLOADER --> FFMPEG
    DOWNLOADER --> PATH

    COOKIE --> FACTORY
    COOKIE --> CONSTANTS

    FACTORY --> EDGE
    FACTORY --> CHROME
    FACTORY --> FIREFOX

    M3U8 --> NM3U8DL

    FILEREADER --> VALIDATOR
    FILEREADER --> PATH

    NM3U8DL --> CONSTANTS
    FFMPEG --> CONSTANTS

    MAIN --> SETTINGS

    style MAIN fill:#FFD700
    style DOWNLOADER fill:#FFA500
    style COOKIE fill:#FFA500
    style M3U8 fill:#FFA500
    style FACTORY fill:#87CEEB
    style EDGE fill:#87CEEB
    style CHROME fill:#87CEEB
    style FIREFOX fill:#87CEEB
    style FILEREADER fill:#98FB98
    style PATH fill:#98FB98
    style VALIDATOR fill:#98FB98
    style NM3U8DL fill:#FF6B6B
    style FFMPEG fill:#FF6B6B
    style CONSTANTS fill:#DDA0DD
    style SETTINGS fill:#DDA0DD
```

### 依赖说明

模块依赖关系遵循以下原则：

1. **单向依赖**：上层模块依赖下层模块，避免循环依赖
2. **核心优先**：核心模块（core）是业务逻辑的核心，被其他模块依赖
3. **工具独立**：工具模块（utils）保持独立性，可被多个模块复用
4. **配置底层**：配置模块（config）作为最底层，被所有模块依赖
5. **浏览器封装**：浏览器模块（browser）通过工厂模式统一管理

---

## 5. 数据流向图

```mermaid
flowchart LR
    subgraph "输入数据"
        A[用户输入<br/>钉钉链接]
        B[Excel/CSV文件<br/>批量链接]
    end

    subgraph "数据处理"
        C[验证器<br/>Validator]
        D[文件读取器<br/>FileReader]
        E[Cookie处理器<br/>CookieHandler]
        F[M3U8解析器<br/>M3u8Parser]
    end

    subgraph "外部交互"
        G[钉钉网站<br/>获取Cookie和M3U8]
        H[浏览器<br/>自动化操作]
    end

    subgraph "工具处理"
        I[N_m3u8DL-RE<br/>下载视频片段]
        J[FFmpeg<br/>合并视频]
    end

    subgraph "输出数据"
        K[视频文件<br/>.mp4/.ts]
        L[下载报告<br/>.txt/.json]
        M[Cookie文件<br/>.txt]
    end

    A --> C
    B --> D
    D --> C

    C --> E
    E --> H
    H --> G
    G --> E
    E --> M

    E --> F
    F --> I
    I --> J
    J --> K

    C --> L

    style A fill:#E6F3FF
    style B fill:#E6F3FF
    style K fill:#FFE6E6
    style L fill:#FFE6E6
    style M fill:#FFE6E6
```

### 数据流说明

数据流向展示了数据从输入到输出的完整过程：

1. **输入阶段**：接收用户输入的单个链接或批量文件
2. **验证阶段**：使用验证器检查数据格式和有效性
3. **Cookie 获取**：通过浏览器自动化从钉钉网站获取 Cookie
4. **M3U8 解析**：解析钉钉直播回放的 M3U8 视频流地址
5. **视频下载**：使用 N_m3u8DL-RE 下载视频片段
6. **视频合并**：使用 FFmpeg 将片段合并为完整视频
7. **输出阶段**：生成视频文件、下载报告和 Cookie 文件

---

## 6. Cookie 获取流程图

```mermaid
flowchart TD
    Start([开始]) --> CheckLocal{检查本地Cookie}

    CheckLocal -->|存在且有效| UseCookie[使用本地Cookie]
    UseCookie --> End([结束])

    CheckLocal -->|不存在或过期| SelectBrowser{选择浏览器}

    SelectBrowser -->|Edge| InitEdge[初始化Edge驱动]
    SelectBrowser -->|Chrome| InitChrome[初始化Chrome驱动]
    SelectBrowser -->|Firefox| InitFirefox[初始化Firefox驱动]

    InitEdge --> LaunchBrowser[启动浏览器]
    InitChrome --> LaunchBrowser
    InitFirefox --> LaunchBrowser

    LaunchBrowser --> Navigate[导航到钉钉页面]
    Navigate --> CheckLogin{检查登录状态}

    CheckLogin -->|已登录| ExtractCookie[提取Cookie]
    CheckLogin -->|未登录| ShowLoginUI[显示登录界面]

    ShowLoginUI --> WaitLogin[等待用户登录]
    WaitLogin --> CheckLogin

    ExtractCookie --> ValidateCookie{验证Cookie有效性}

    ValidateCookie -->|无效| RetryLogin[提示重新登录]
    RetryLogin --> ShowLoginUI

    ValidateCookie -->|有效| SaveCookie[保存Cookie到本地]
    SaveCookie --> CloseBrowser[关闭浏览器]
    CloseBrowser --> End

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style UseCookie fill:#90EE90
    style SaveCookie fill:#90EE90
```

### 流程说明

Cookie 获取流程确保用户能够访问钉钉的直播回放内容：

1. **本地检查**：优先检查本地是否存在有效的 Cookie
2. **浏览器选择**：支持 Edge、Chrome、Firefox 三种主流浏览器
3. **自动化操作**：通过 Selenium 驱动浏览器自动导航
4. **登录处理**：检测登录状态，引导用户完成登录
5. **Cookie 提取**：从浏览器中提取有效的 Cookie
6. **本地存储**：将 Cookie 保存到本地文件，避免重复登录

---

## 7. M3U8 解析流程图

```mermaid
flowchart TD
    Start([开始]) --> InputURL[输入钉钉直播回放URL]
    InputURL --> AddCookie[添加Cookie到请求头]
    AddCookie --> FetchPage[获取页面内容]

    FetchPage --> ParseHTML{解析HTML}
    ParseHTML -->|失败| Error1[HTML解析失败]
    Error1 --> End([结束])

    ParseHTML -->|成功| FindM3U8{查找M3U8链接}

    FindM3U8 -->|未找到| Error2[未找到M3U8链接]
    Error2 --> End

    FindM3U8 -->|找到| ExtractM3U8[提取M3U8链接]
    ExtractM3U8 --> ValidateM3U8{验证M3U8格式}

    ValidateM3U8 -->|无效| Error3[M3U8格式无效]
    Error3 --> End

    ValidateM3U8 -->|有效| FetchM3U8[获取M3U8文件内容]
    FetchM3U8 --> ParseM3U8[解析M3U8文件]

    ParseM3U8 --> CheckType{M3U8类型}

    CheckType -->|主M3U8| ParseMaster[解析主M3U8]
    ParseMaster --> GetQuality{获取视频质量选项}
    GetQuality --> SelectQuality[选择最佳质量]
    SelectQuality --> GetSubM3U8[获取子M3U8链接]
    GetSubM3U8 --> ParseSubM3U8[解析子M3U8]
    ParseSubM3U8 --> ExtractSegments[提取视频片段]

    CheckType -->|子M3U8| ExtractSegments

    ExtractSegments --> ValidateSegments{验证片段列表}

    ValidateSegments -->|无效| Error4[片段列表无效]
    Error4 --> End

    ValidateSegments -->|有效| ReturnResult[返回解析结果]
    ReturnResult --> End

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style Error1 fill:#FFB6C1
    style Error2 fill:#FFB6C1
    style Error3 fill:#FFB6C1
    style Error4 fill:#FFB6C1
    style ReturnResult fill:#90EE90
```

### 流程说明

M3U8 解析流程负责从钉钉直播回放页面提取视频流信息：

1. **页面获取**：使用 Cookie 获取钉钉直播回放页面内容
2. **HTML 解析**：解析 HTML 页面，查找 M3U8 视频流链接
3. **M3U8 验证**：验证 M3U8 链接的格式和有效性
4. **类型识别**：识别 M3U8 文件类型（主 M3U8 或子 M3U8）
5. **质量选择**：对于主 M3U8，选择最佳视频质量
6. **片段提取**：提取所有视频片段的 URL 列表
7. **结果返回**：返回完整的 M3U8 解析结果

---

## 8. 视频下载流程图

```mermaid
flowchart TD
    Start([开始]) --> InputM3U8[输入M3U8解析结果]
    InputM3U8 --> CheckBinary{检查N_m3u8DL-RE}

    CheckBinary -->|不存在| DownloadBinary[下载N_m3u8DL-RE]
    DownloadBinary --> CheckBinary

    CheckBinary -->|存在| PrepareDownload[准备下载参数]
    PrepareDownload --> SetOutput[设置输出路径]

    SetOutput --> SetThreads[设置下载线程数]
    SetThreads --> SetHeaders[设置请求头]
    SetHeaders --> SetCookies[设置Cookie]

    SetCookies --> StartDownload[启动N_m3u8DL-RE]
    StartDownload --> MonitorProgress[监控下载进度]

    MonitorProgress --> CheckProgress{下载进度}

    CheckProgress -->|进行中| UpdateProgress[更新进度显示]
    UpdateProgress --> MonitorProgress

    CheckProgress -->|完成| CheckResult{下载结果}

    CheckResult -->|失败| Error1[下载失败]
    Error1 --> Retry{重试?}

    Retry -->|是| StartDownload
    Retry -->|否| End([结束])

    CheckResult -->|成功| CheckFFmpeg{检查FFmpeg}

    CheckFFmpeg -->|不存在| DownloadFFmpeg[下载FFmpeg]
    DownloadFFmpeg --> CheckFFmpeg

    CheckFFmpeg -->|存在| PrepareMerge[准备合并参数]
    PrepareMerge --> SetInput[设置输入文件]
    SetInput --> SetOutputFile[设置输出文件]

    SetOutputFile --> StartMerge[启动FFmpeg合并]
    StartMerge --> MonitorMerge[监控合并进度]

    MonitorMerge --> CheckMerge{合并结果}

    CheckMerge -->|失败| Error2[合并失败]
    Error2 --> End

    CheckMerge -->|成功| Cleanup[清理临时文件]
    Cleanup --> Success[下载完成]
    Success --> End

    style Start fill:#90EE90
    style End fill:#FFB6C1
    style Error1 fill:#FFB6C1
    style Error2 fill:#FFB6C1
    style Success fill:#90EE90
```

### 流程说明

视频下载流程使用专业工具完成视频片段的下载和合并：

1. **工具检查**：检查 N_m3u8DL-RE 和 FFmpeg 是否可用
2. **参数准备**：设置下载参数（输出路径、线程数、请求头、Cookie）
3. **下载执行**：使用 N_m3u8DL-RE 下载视频片段
4. **进度监控**：实时监控下载进度并显示给用户
5. **错误处理**：下载失败时提供重试机制
6. **视频合并**：使用 FFmpeg 将下载的片段合并为完整视频
7. **清理工作**：删除临时文件，保持目录整洁

---

## 总结

本文档通过多个架构图和流程图，全面展示了 DingTalk-Live-Playback-Download-Tool 项目的系统结构和工作流程。这些图表帮助开发者和用户：

- 理解项目的整体架构和模块关系
- 掌握核心业务流程的实现逻辑
- 了解批量处理的工作方式
- 理解数据在系统中的流动过程
- 掌握关键功能（Cookie 获取、M3U8 解析、视频下载）的详细流程

所有图表均使用 Mermaid 语法编写，可以在支持 Mermaid 的 Markdown 编辑器中直接渲染，也可以导出为图片格式用于文档和演示。
