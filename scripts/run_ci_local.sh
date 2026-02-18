#!/bin/bash
# 本地 CI/CD 测试脚本 (Linux/macOS)
# 用于在提交前模拟 CI 流程

set -e  # 遇到错误立即退出

echo "========================================"
echo "  Local CI/CD Test Script"
echo "========================================"
echo ""

# Step 1: Install dependencies
echo "[Step 1/6] Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt
echo "[OK] Dependencies installed"
echo ""

# Step 2: Run Black
echo "[Step 2/6] Running Black (code formatter)..."
if black --check src/ tests/; then
    echo "[OK] Black check passed"
else
    echo "[WARN] Black check failed. Run 'black src/ tests/' to fix."
fi
echo ""

# Step 3: Run Flake8
echo "[Step 3/6] Running Flake8 (code quality)..."
flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
echo "[OK] Flake8 check passed"
echo ""

# Step 4: Run Tests
echo "[Step 4/6] Running tests with coverage..."
pytest tests/ -v --cov=src/dingtalk_downloader --cov-report=term-missing --cov-fail-under=80
echo "[OK] All tests passed"
echo ""

# Step 5: Run Security Checks
echo "[Step 5/6] Running security checks..."
if safety check --full-report; then
    echo "[OK] No security vulnerabilities found"
else
    echo "[WARN] Security vulnerabilities found"
fi
echo ""

# Step 6: Run Bandit
echo "[Step 6/6] Running Bandit (security linter)..."
if bandit -r src/ -ll; then
    echo "[OK] No security issues found"
else
    echo "[WARN] Bandit found security issues"
fi
echo ""

echo "========================================"
echo "  CI/CD Check Complete!"
echo "========================================"
echo "All critical checks passed."
echo "Ready to commit!"
