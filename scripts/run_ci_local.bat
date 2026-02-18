@echo off
REM 本地 CI/CD 测试脚本 (Windows)
REM 用于在提交前模拟 CI 流程

echo ========================================
echo   Local CI/CD Test Script
echo ========================================
echo.

REM Step 1: Install dependencies
echo [Step 1/6] Installing dependencies...
pip install -r requirements.txt
pip install -r requirements-dev.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies
    exit /b 1
)
echo [OK] Dependencies installed
echo.

REM Step 2: Run Black
echo [Step 2/6] Running Black (code formatter)...
black --check src/ tests/
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Black check failed. Run 'black src/ tests/' to fix.
) else (
    echo [OK] Black check passed
)
echo.

REM Step 3: Run Flake8
echo [Step 3/6] Running Flake8 (code quality)...
flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Flake8 found critical errors
    exit /b 1
)
echo [OK] Flake8 check passed
echo.

REM Step 4: Run Tests
echo [Step 4/6] Running tests with coverage...
pytest tests/ -v --cov=src/dingtalk_downloader --cov-report=term-missing --cov-fail-under=80
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Tests failed or coverage below 80%%
    exit /b 1
)
echo [OK] All tests passed
echo.

REM Step 5: Run Security Checks
echo [Step 5/6] Running security checks...
safety check --full-report
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Security vulnerabilities found
) else (
    echo [OK] No security vulnerabilities found
)
echo.

REM Step 6: Run Bandit
echo [Step 6/6] Running Bandit (security linter)...
bandit -r src/ -ll
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] Bandit found security issues
) else (
    echo [OK] No security issues found
)
echo.

echo ========================================
echo   CI/CD Check Complete!
echo ========================================
echo All critical checks passed.
echo Ready to commit!
