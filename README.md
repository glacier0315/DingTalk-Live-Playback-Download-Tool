# DingTalk-Live-Playback-Download-Tool

钉钉直播回放下载工具：通过 Selenium 自动化浏览器获取 Cookie，解析 m3u8 链接，调用 N_m3u8DL-RE 下载钉钉直播回放视频。

## 环境要求

- Python 3.8+
- 浏览器：Edge / Chrome / Firefox
- `assets/bin/N_m3u8DL-RE.exe`、`assets/bin/ffmpeg.exe`（Windows 平台）

## 安装

需要 [uv](https://docs.astral.sh/uv/) 0.5+（一个超快的 Python 包管理器）。

```bash
# 推荐：用 uv 自动创建 .venv 并安装全部依赖（含 dev）
uv sync --group dev

# 验证安装
uv run python -c "import dingtalk_downloader; print(dingtalk_downloader.__version__)"
```

如果偏好传统 pip：

```bash
# 运行时依赖
pip install -r requirements.txt
# 测试依赖
pip install pytest
```

## 运行

```bash
# 方式一：uv 激活虚拟环境后用控制台脚本
uv run dingtalk-downloader

# 方式二：uv + 模块入口（推荐用于开发）
uv run python -m src.dingtalk_downloader.main

# 方式三：传统方式（已激活 .venv 时）
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
# 跑单元测试（默认跳过 integration）
uv run pytest tests/unit/ -v

# 跑全部测试（含 integration 标记，需真实浏览器 + N_m3u8DL-RE.exe）
uv run pytest -v
```
