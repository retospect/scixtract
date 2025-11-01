# Makefile for AI PDF Extractor Package
# Professional Python package development workflow

SHELL := /bin/bash
PYTHON := python3
PACKAGE_NAME := scixtract
SRC_DIR := src
TESTS_DIR := tests
EXAMPLES_DIR := examples

# Virtual environment
VENV := venv
VENV_BIN := $(VENV)/bin
PYTHON_VENV := $(VENV_BIN)/python
PIP_VENV := $(VENV_BIN)/pip

# Package files
PACKAGE_FILES := $(shell find $(SRC_DIR) -name "*.py")
TEST_FILES := $(shell find $(TESTS_DIR) -name "*.py")
ALL_PYTHON_FILES := $(PACKAGE_FILES) $(TEST_FILES)

.PHONY: help setup clean test lint format type-check security install build upload docs examples

# Default target
all: setup lint format type-check test

help: ## Show this help message
	@echo "AI PDF Extractor - Development Commands"
	@echo "======================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Environment setup
setup: $(VENV) ## Create virtual environment and install dependencies
	@echo "✅ Virtual environment ready"

$(VENV):
	@echo "🔧 Creating virtual environment..."
	$(PYTHON) -m venv $(VENV)
	$(PIP_VENV) install --upgrade pip setuptools wheel
	$(PIP_VENV) install -e ".[dev,test]"

install: setup ## Install package in development mode
	@echo "📦 Installing package in development mode..."
	$(PIP_VENV) install -e .

# Code quality
format: setup ## Format code with black and isort
	@echo "🎨 Formatting code..."
	$(VENV_BIN)/black $(SRC_DIR) $(TESTS_DIR) $(EXAMPLES_DIR)
	$(VENV_BIN)/isort $(SRC_DIR) $(TESTS_DIR) $(EXAMPLES_DIR)

format-check: setup ## Check code formatting
	@echo "🔍 Checking code formatting..."
	$(VENV_BIN)/black --check $(SRC_DIR) $(TESTS_DIR) $(EXAMPLES_DIR)
	$(VENV_BIN)/isort --check-only $(SRC_DIR) $(TESTS_DIR) $(EXAMPLES_DIR)

lint: setup ## Run linting with flake8
	@echo "🔍 Running linting..."
	$(VENV_BIN)/flake8 $(SRC_DIR) $(TESTS_DIR) $(EXAMPLES_DIR)

type-check: setup ## Run type checking with mypy
	@echo "🔍 Running type checking..."
	$(VENV_BIN)/mypy $(SRC_DIR)

security: setup ## Run security scanning with bandit
	@echo "🔒 Running security scan..."
	$(VENV_BIN)/bandit -r $(SRC_DIR)

# Testing
test: setup ## Run tests with pytest
	@echo "🧪 Running tests..."
	$(VENV_BIN)/pytest $(TESTS_DIR) -v

test-cov: setup ## Run tests with coverage
	@echo "🧪 Running tests with coverage..."
	$(VENV_BIN)/pytest $(TESTS_DIR) --cov=$(PACKAGE_NAME) --cov-report=term-missing --cov-report=html --cov-report=xml

test-fast: setup ## Run tests without coverage (faster)
	@echo "🧪 Running fast tests..."
	$(VENV_BIN)/pytest $(TESTS_DIR) -x --no-cov

# Examples
examples: setup ## Run example scripts
	@echo "📚 Running examples..."
	@cd $(EXAMPLES_DIR) && $(PYTHON_VENV) basic_extraction.py
	@echo "✅ Basic extraction example completed"

test-examples: setup ## Test that examples run without errors
	@echo "📚 Testing examples..."
	@cd $(EXAMPLES_DIR) && $(PYTHON_VENV) -c "import basic_extraction; print('✅ basic_extraction imports successfully')"
	@cd $(EXAMPLES_DIR) && $(PYTHON_VENV) -c "import batch_processing; print('✅ batch_processing imports successfully')"

# Package building
build: setup clean-build ## Build package distributions
	@echo "📦 Building package..."
	$(PYTHON_VENV) -m build

clean-build: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/

# Documentation
docs: setup ## Generate documentation
	@echo "📚 Generating documentation..."
	@if [ ! -d "docs" ]; then \
		mkdir docs; \
		$(VENV_BIN)/sphinx-quickstart -q -p "AI PDF Extractor" -a "Reto Stamm" --ext-autodoc --ext-viewcode --makefile --no-batchfile docs; \
	fi
	@cd docs && $(VENV_BIN)/sphinx-apidoc -o . ../$(SRC_DIR)
	@cd docs && make html
	@echo "📖 Documentation generated in docs/_build/html/"

# Cleanup
clean: ## Clean temporary files
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .tox/

clean-all: clean clean-build ## Clean everything including virtual environment
	@echo "🧹 Cleaning everything..."
	rm -rf $(VENV)

# Development tools
shell: setup ## Start interactive Python shell with package loaded
	@echo "🐍 Starting Python shell..."
	@cd $(SRC_DIR) && $(PYTHON_VENV) -c "from $(PACKAGE_NAME) import *; print('📦 Package loaded. Available: AdvancedPDFProcessor, KnowledgeTracker, OllamaAIProcessor'); import code; code.interact(local=locals())"

install-hooks: setup ## Install pre-commit hooks
	@echo "🪝 Installing pre-commit hooks..."
	$(VENV_BIN)/pre-commit install

# Package management
check: setup format-check lint type-check test ## Run all quality checks
	@echo "✅ All quality checks passed!"

pre-commit: check ## Run pre-commit checks (for CI)
	@echo "✅ Pre-commit checks completed"

# Release management
version: ## Show current version
	@$(PYTHON_VENV) -c "from $(SRC_DIR).$(PACKAGE_NAME) import __version__; print(f'Current version: {__version__}')"

# Status and information
status: ## Show project status
	@echo "📊 AI PDF Extractor - Project Status"
	@echo "===================================="
	@echo "🐍 Python: $(shell $(PYTHON) --version)"
	@echo "📦 Virtual env: $(shell [ -d $(VENV) ] && echo '✅ Active' || echo '❌ Not created')"
	@echo "📁 Package files: $(shell echo $(PACKAGE_FILES) | wc -w | tr -d ' ')"
	@echo "🧪 Test files: $(shell echo $(TEST_FILES) | wc -w | tr -d ' ')"
	@if [ -d $(VENV) ]; then \
		echo "📋 Installed packages: $(shell $(PIP_VENV) list --format=freeze | wc -l | tr -d ' ')"; \
	fi

# CI/CD helpers
ci-setup: ## Setup for CI environment
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	$(PYTHON) -m pip install -e ".[dev,test]"

ci-test: ## Run tests in CI environment
	pytest $(TESTS_DIR) --cov=$(PACKAGE_NAME) --cov-report=xml --cov-report=term

ci-quality: ## Run quality checks in CI environment
	black --check $(SRC_DIR) $(TESTS_DIR)
	isort --check-only $(SRC_DIR) $(TESTS_DIR)
	flake8 $(SRC_DIR) $(TESTS_DIR)
	mypy $(SRC_DIR)
	bandit -r $(SRC_DIR)
