.PHONY: help install test lint format security clean build docs

# Variables
PYTHON := python
PIP := pip
PYTEST := pytest
BLACK := black
FLAKE8 := flake8
MYPY := mypy
ISORT := isort

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install all dependencies
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .

install-dev: ## Install development dependencies only
	$(PIP) install -r requirements-dev.txt

test: ## Run all tests with coverage
	$(PYTEST) tests/ -v --cov=src/dingtalk_downloader --cov-report=term-missing --cov-report=html --cov-fail-under=80

test-unit: ## Run unit tests only
	$(PYTEST) tests/unit/ -v --cov=src/dingtalk_downloader --cov-report=term-missing

test-integration: ## Run integration tests only
	$(PYTEST) tests/integration/ -v

test-functional: ## Run functional tests only
	$(PYTEST) tests/functional/ -v

test-fast: ## Run tests without coverage (faster)
	$(PYTEST) tests/ -v --no-cov

lint: ## Run all linting checks
	@echo "Running Black..."
	-$(BLACK) --check --diff src/ tests/
	@echo "Running Flake8..."
	-$(FLAKE8) src/ tests/ --count --statistics
	@echo "Running MyPy..."
	-$(MYPY) src/ --ignore-missing-imports
	@echo "Running isort..."
	-$(ISORT) --check-only --diff src/ tests/

format: ## Format code with Black and isort
	$(BLACK) src/ tests/
	$(ISORT) src/ tests/

security: ## Run security checks
	@echo "Running Safety check..."
	-safety check --full-report
	@echo "Running Bandit..."
	-bandit -r src/ -ll

quality: ## Run complete quality analysis
	@echo "=== Cyclomatic Complexity ==="
	-radon cc src/ -a -s
	@echo ""
	@echo "=== Maintainability Index ==="
	-radon mi src/ -s
	@echo ""
	@echo "=== Raw Metrics ==="
	-radon raw src/ -s

clean: ## Clean up generated files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type f -name "coverage.xml" -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf dist/ build/ .tox/ .cache/

build: ## Build the package
	$(PYTHON) -m build

docs: ## Generate documentation
	@echo "Checking docstrings..."
	-pydocstyle src/

check: lint test security ## Run all checks (lint, test, security)

ci: ## Simulate CI pipeline locally
	@echo "=== Running CI Pipeline Locally ==="
	@echo ""
	@echo "Step 1: Installing dependencies..."
	$(PIP) install -r requirements.txt -r requirements-dev.txt
	@echo ""
	@echo "Step 2: Running linting checks..."
	$(BLACK) --check src/ tests/
	$(FLAKE8) src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
	@echo ""
	@echo "Step 3: Running tests..."
	$(PYTEST) tests/ -v --cov=src/dingtalk_downloader --cov-report=xml --cov-fail-under=80
	@echo ""
	@echo "Step 4: Running security checks..."
	-safety check
	@echo ""
	@echo "=== CI Pipeline Complete ==="
