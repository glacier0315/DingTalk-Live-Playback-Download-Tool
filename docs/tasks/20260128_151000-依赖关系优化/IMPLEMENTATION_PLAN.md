# 依赖关系优化 - 实施计划

**创建时间**: 2026-01-28  
**任务范围**: 6.1.2 依赖关系复杂  
**推荐方案**: 方案1 - 依赖注入（结合方案2 - 工厂模式）

---

## 一、实施概述

### 1.1 核心目标

使用依赖注入和工厂模式降低模块间耦合度，提高代码可测试性和可维护性。

### 1.2 实施范围

1. 创建DependencyFactory类
2. 重构VideoDownloadManager类，添加依赖注入
3. 重构Downloader类，使用DependencyFactory
4. 编写单元测试
5. 运行测试验证
6. 生成改进报告

---

## 二、实施步骤

### 2.1 创建DependencyFactory类

**文件**: `src/dingtalk_downloader/core/dependency_factory.py`

**核心方法**:
```python
class DependencyFactory:
    """
    依赖工厂类。
    
    负责创建和管理各种依赖实例。
    """
    
    def __init__(self):
        """初始化依赖工厂。"""
        self._instances = {}
    
    def get_cookie_handler(self, browser_type: str) -> CookieHandler:
        """获取Cookie处理器实例。"""
        key = f"cookie_handler_{browser_type}"
        if key not in self._instances:
            from .cookie_handler import CookieHandler
            self._instances[key] = CookieHandler(browser_type)
        return self._instances[key]
    
    def get_m3u8_parser(self, browser_driver) -> M3u8Parser:
        """获取m3u8解析器实例。"""
        key = f"m3u8_parser_{id(browser_driver)}"
        if key not in self._instances:
            from .m3u8_parser import M3u8Parser
            self._instances[key] = M3u8Parser(browser_driver)
        return self._instances[key]
    
    def get_path_selector(self, save_mode: str) -> PathSelector:
        """获取路径选择器实例。"""
        key = f"path_selector_{save_mode}"
        if key not in self._instances:
            from ..utils.path_selector import PathSelector
            self._instances[key] = PathSelector(save_mode)
        return self._instances[key]
    
    def get_n_m3u8dl_re(self) -> NM3u8DLRE:
        """获取NM3u8DLRE实例。"""
        key = "n_m3u8dl_re"
        if key not in self._instances:
            from ..binary.n_m3u8dl_re import NM3u8DLRE
            self._instances[key] = NM3u8DLRE()
        return self._instances[key]
    
    def get_m3u8_download_service(self, m3u8_parser) -> M3u8DownloadService:
        """获取m3u8下载服务实例。"""
        key = f"m3u8_download_service_{id(m3u8_parser)}"
        if key not in self._instances:
            from .m3u8_download_service import M3u8DownloadService
            self._instances[key] = M3u8DownloadService(m3u8_parser)
        return self._instances[key]
```

### 2.2 重构VideoDownloadManager类

**文件**: `src/dingtalk_downloader/core/video_download_manager.py`

**构造函数修改**:
```python
def __init__(
    self,
    browser_type: str,
    save_mode: str,
    cookie_handler: Optional[CookieHandler] = None,
    m3u8_parser: Optional[M3u8Parser] = None,
    m3u8_download_service: Optional[M3u8DownloadService] = None,
    path_selector: Optional[PathSelector] = None,
    n_m3u8dl_re: Optional[NM3u8DLRE] = None,
):
    """
    初始化视频下载管理器。

    Args:
        browser_type: 浏览器类型
        save_mode: 保存模式
        cookie_handler: Cookie处理器（可选）
        m3u8_parser: m3u8解析器（可选）
        m3u8_download_service: m3u8下载服务（可选）
        path_selector: 路径选择器（可选）
        n_m3u8dl_re: NM3u8DLRE实例（可选）
    """
    self.browser_type = browser_type
    self.save_mode = save_mode

    # 使用注入的依赖，如果没有注入则创建默认实例
    self.cookie_handler = cookie_handler
    self.m3u8_parser = m3u8_parser
    self.m3u8_download_service = m3u8_download_service
    self.path_selector = path_selector
    self.n_m3u8dl_re = n_m3u8dl_re

    logger.debug(f"视频下载管理器初始化 - 浏览器类型: {browser_type}")
```

### 2.3 重构Downloader类

**文件**: `src/dingtalk_downloader/core/downloader.py`

**构造函数修改**:
```python
def __init__(
    self,
    browser_type: str,
    save_mode: str,
    user_controller: UserInteractionController,
    dependency_factory: Optional[DependencyFactory] = None,
):
    """
    初始化下载器。

    Args:
        browser_type: 浏览器类型
        save_mode: 保存模式
        user_controller: 用户交互控制器
        dependency_factory: 依赖工厂（可选）
    """
    self.browser_type = browser_type
    self.save_mode = save_mode
    self.user_controller = user_controller

    # 创建依赖工厂
    self.dependency_factory = dependency_factory or DependencyFactory()

    # 使用依赖工厂创建依赖实例
    cookie_handler = self.dependency_factory.get_cookie_handler(browser_type)
    path_selector = self.dependency_factory.get_path_selector(save_mode)
    n_m3u8dl_re = self.dependency_factory.get_n_m3u8dl_re()

    # 创建视频下载管理器
    self.video_manager = VideoDownloadManager(
        browser_type,
        save_mode,
        cookie_handler=cookie_handler,
        path_selector=path_selector,
        n_m3u8dl_re=n_m3u8dl_re,
    )

    logger.info(f"下载器初始化完成 - 浏览器类型: {browser_type}, 保存模式: {save_mode}")
```

### 2.4 编写单元测试

**文件**: 
- `tests/test_dependency_factory.py`
- `tests/test_video_download_manager.py`
- `tests/test_downloader.py`

**测试覆盖目标**: 不低于80%

### 2.5 运行测试验证

**命令**:
```bash
python -m pytest tests/ --cov=src --cov-report=html --cov-report=term
```

### 2.6 生成改进报告

**文件**: `docs/review/dependency_optimization_improvement_report.md`

**报告内容**:
- 问题分析
- 实施步骤
- 测试结果
- 性能对比
- 结论和建议

---

## 三、预期成果

### 3.1 技术成果

1. DependencyFactory类创建成功
2. VideoDownloadManager类实施依赖注入
3. Downloader类使用DependencyFactory重构成功
4. 模块间耦合度降低
5. 代码可测试性显著提升

### 3.2 质量成果

1. 测试覆盖率不低于80%
2. 所有测试通过
3. 无明显的性能下降
4. 代码符合项目规范

### 3.3 业务成果

1. 程序功能与重构前完全一致
2. 用户体验无明显变化
3. 代码可维护性显著提升

---

## 四、时间安排

### 4.1 预计时间

- 创建DependencyFactory类：2-3小时
- 重构VideoDownloadManager类：2-3小时
- 重构Downloader类：2-3小时
- 编写单元测试：3-4小时
- 运行测试验证：1-2小时
- 生成改进报告：1-2小时

**总预计时间**: 10-17小时

### 4.2 实施顺序

1. 创建DependencyFactory类
2. 重构VideoDownloadManager类
3. 重构Downloader类
4. 编写单元测试
5. 运行测试验证
6. 生成改进报告

---

## 五、风险提示

### 5.1 技术风险

- 重构可能引入新的bug
- 依赖注入可能增加复杂度

### 5.2 应对策略

- 充分的单元测试
- 逐步重构，每步都进行测试
- 准备回滚方案

---

**实施计划创建时间**: 2026-01-28  
**实施计划版本**: 1.0
