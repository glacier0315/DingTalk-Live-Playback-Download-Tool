# DingTalk-Live-Playback-Download-Tool

钉钉直播回放下载工具：通过 Selenium 自动化浏览器获取 Cookie，解析 m3u8 链接，调用 N_m3u8DL-RE 下载钉钉直播回放视频。

## 环境要求

- Python 3.8+
- 浏览器：Edge / Chrome / Firefox
- `assets/bin/N_m3u8DL-RE.exe`、`assets/bin/ffmpeg.exe`（Windows 平台）

## 安装

```bash
pip install -r requirements.txt
```

## 运行

```bash
python -m src.dingtalk_downloader.main
```

按提示选择下载模式（单个 / 批量），输入钉钉直播回放分享链接，程序会自动打开浏览器、获取登录态、解析 m3u8 并下载视频。

## 目录结构

```text
DingTalk-Live-Playback-Download-Tool/
├── src/dingtalk_downloader/    # 源代码
│   ├── main.py                # 程序入口
│   ├── core/                  # 下载流程、Cookie、M3U8 解析
│   ├── browser/               # Edge/Chrome/Firefox 驱动
│   ├── binary/                # N_m3u8DL-RE 封装
│   ├── config/                # YAML 配置、日志、请求头
│   └── utils/                 # 文件读取、路径、校验、数据模型
├── tests/unit/                # 单元测试
├── config/app.yaml            # 运行时配置
├── assets/bin/                # N_m3u8DL-RE、ffmpeg
├── assets/template/           # 批量下载模板
├── assets/ICO/                # 图标
├── requirements.txt
└── pyproject.toml
```

## 测试

```bash
pip install pytest
pytest tests/unit/ -v
```
