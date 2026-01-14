# 本项目方法已失效，停止更新 2025.03.02

# DingTalk-Live-Playback-Download-Tool
钉钉直播回放下载工具，使用钉钉分享链接一键下载钉钉直播回放视频，现已支持批量下载
![image](https://github.com/user-attachments/assets/0de8822a-fe81-4726-b8fb-8540b9197908)


## 使用方法
- 直接运行 DingTalk-Live-Playback-Download-Tool.exe
- 选择下载方式、保存方式和浏览器后，等待浏览器自动打开
- 首次运行，浏览器加载可能较慢，因为程序在自动下载并载入Webdriver，需耐心等待
- 浏览器打开后，登录钉钉账号，等待页面加载完毕
- 回到程序界面，点击回车即可开始下载

## 批量下载模式
- 将需要下载的钉钉直播分享链接保存至一个CSV或者EXCEL表格，一个单元格放一个链接，不要放在首行
- 运行 DingTalk-Live-Playback-Download-Tool.exe，选择批量下载模式
- 手动输入保存有钉钉直播分享链接表格的路径或者直接将表格文件拖进窗口
- 选择保存方式和浏览器后，等待浏览器自动打开
- 浏览器打开后，登录钉钉账号，等待页面加载完毕
- 回到程序界面，点击回车即可开始批量下载
  

![image](https://github.com/user-attachments/assets/e7b9d376-0814-4649-a334-422deb8cc2b3)

![image](https://github.com/user-attachments/assets/59b7c2e1-a29b-480f-9377-80fc2b6890c2)



## 使用的工具

本项目使用了以下第三方工具：

- [N_m3u8DL-RE](https://github.com/nilaoda/N_m3u8DL-RE)：一个跨平台的DASH/HLS/MSS下载工具，支持点播和直播（DASH/HLS）视频下载。
- [FFmpeg](https://ffmpeg.org/)：一个开源的音视频处理工具，支持多种格式的转换、录制和流媒体处理。

## 开发工具

本项目使用以下开发工具来确保代码质量和一致性：

### Black 代码格式化工具

[Black](https://black.readthedocs.io/) 是 Python 社区广泛使用的代码格式化工具，用于自动统一代码风格。

**安装**：

```bash
pip install -r requirements-dev.txt
```

**使用方法**：

```bash
# 格式化整个项目
python -m black .

# 检查代码格式（不修改文件）
python -m black --check .

# 查看格式化差异
python -m black --diff .
```

**配置**：

Black 的配置位于项目根目录的 `pyproject.toml` 文件中，主要配置包括：

- 行长度：100 字符
- 目标 Python 版本：Python 3.8+
- 排除目录：`.git`、`__pycache__`、`build`、`dist` 等

**开发要求**：

- 所有代码在提交前必须通过 Black 格式化检查
- 不得手动调整格式化后的代码，除非有充分的理由
- 定期运行格式化命令，保持代码风格一致

详细使用说明请参考 [开发指南](docs/development_guide.md)。

### Pytest 测试框架

[Pytest](https://docs.pytest.org/) 是 Python 的测试框架，用于编写和运行测试。

**运行测试**：

```bash
# 运行所有测试
pytest

# 运行指定测试文件
pytest tests/unit/test_downloader.py

# 显示测试覆盖率
pytest --cov=src/dingtalk_downloader
```

详细测试指南请参考 [开发指南](docs/development_guide.md)。

## 项目文档

- [开发规范](docs/development_standard.md)：项目的完整开发规范，包括命名规范、注释规范、项目结构规范等
- [开发指南](docs/development_guide.md)：开发流程、工具使用和代码质量要求的详细说明

## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交代码：`git commit -m "feat: 添加新功能"`
4. 推送到分支：`git push origin feature/your-feature`
5. 创建 Pull Request

**提交前检查**：

- 代码已通过 Black 格式化检查：`python -m black --check .`
- 所有测试通过：`pytest`
- 代码符合项目开发规范

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。
