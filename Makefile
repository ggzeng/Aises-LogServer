.PHONY: help install dev-install run dev start stop restart logs test test-cov lint format clean check all

# 默认目标
.DEFAULT_GOAL := help

# 项目配置
PROJECT_NAME := log-server
PYTHON_VERSION := python3.11
VENV_DIR := .venv
HOST := 0.0.0.0
PORT := 8000

# 颜色定义
COLOR_RESET := \033[0m
COLOR_BOLD := \033[1m
COLOR_GREEN := \033[32m
COLOR_YELLOW := \033[33m
COLOR_BLUE := \033[34m

##@ 帮助信息

help: ## 显示此帮助信息
	@echo '$(COLOR_BOLD)$(PROJECT_NAME) - 可用命令:$(COLOR_RESET)'
	@echo ''
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(COLOR_BLUE)%-20s$(COLOR_RESET) %s\n", $$1, $$2}'
	@echo ''

##@ 环境设置

install: ## 安装项目依赖（使用 uv）
	@echo "$(COLOR_GREEN)安装依赖...$(COLOR_RESET)"
	uv sync

dev-install: ## 安装开发依赖
	@echo "$(COLOR_GREEN)安装开发依赖...$(COLOR_RESET)"
	uv sync --group dev

check-uv: ## 检查 uv 是否已安装
	@command -v uv >/dev/null 2>&1 || { echo "$(COLOR_YELLOW)未找到 uv，正在安装...$(COLOR_RESET)"; curl -LsSf https://astral.sh/uv/install.sh | sh; }

##@ 运行服务

run: ## 启动服务器（生产模式）
	@echo "$(COLOR_GREEN)启动服务器在 http://$(HOST):$(PORT)$(COLOR_RESET)"
	uvicorn main:app --host $(HOST) --port $(PORT)

dev: ## 启动服务器（开发模式，支持热重载，应用 debug 日志）
	@echo "$(COLOR_GREEN)启动开发服务器在 http://$(HOST):$(PORT)$(COLOR_RESET)"
	LOG_LEVEL=debug uvicorn main:app --host $(HOST) --port $(PORT) --reload --log-level info

dev-host: ## 启动开发服务器（仅监听 localhost，应用 debug 日志）
	@echo "$(COLOR_GREEN)启动开发服务器在 http://localhost:$(PORT)$(COLOR_RESET)"
	LOG_LEVEL=debug uvicorn main:app --host localhost --port $(PORT) --reload --log-level info

start: ## 后台启动服务器（日志保存到 logs/ 目录）
	@echo "$(COLOR_GREEN)后台启动服务器...$(COLOR_RESET)"
	@mkdir -p logs
	@nohup uvicorn main:app --host $(HOST) --port $(PORT) > logs/server-$(shell date +%Y%m%d-%H%M%S).log 2>&1 &
	@echo "$(COLOR_GREEN)服务器已在后台启动，PID: $$!$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)使用 'make stop' 停止服务器$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)使用 'make logs' 查看日志$(COLOR_RESET)"

stop: ## 停止后台运行的服务器
	@echo "$(COLOR_YELLOW)停止服务器...$(COLOR_RESET)"
	@pkill -f "uvicorn main:app" || echo "$(COLOR_YELLOW)未找到运行中的服务器$(COLOR_RESET)"
	@echo "$(COLOR_GREEN)服务器已停止$(COLOR_RESET)"

restart: stop start ## 重启服务器

logs: ## 查看最新的日志文件
	@echo "$(COLOR_GREEN)最新日志文件:$(COLOR_RESET)"
	@ls -lt logs/*.log 2>/dev/null | head -1 || echo "$(COLOR_YELLOW)未找到日志文件$(COLOR_RESET)"
	@echo ''
	@echo "$(COLOR_GREEN)日志内容:$(COLOR_RESET)"
	@tail -f $$(ls -t logs/*.log 2>/dev/null | head -1) 2>/dev/null || echo "$(COLOR_YELLOW)未找到日志文件$(COLOR_RESET)"

##@ 测试

test: ## 运行所有测试
	@echo "$(COLOR_GREEN)运行测试...$(COLOR_RESET)"
	uv run pytest -v

test-cov: ## 运行测试并生成覆盖率报告
	@echo "$(COLOR_GREEN)运行测试并生成覆盖率报告...$(COLOR_RESET)"
	uv run pytest --cov=. --cov-report=html --cov-report=term

test-cov-xml: ## 运行测试并生成 XML 覆盖率报告（用于 CI）
	@echo "$(COLOR_GREEN)运行测试并生成 XML 覆盖率报告...$(COLOR_RESET)"
	uv run pytest --cov=. --cov-report=xml --cov-report=term

test-one: ## 运行单个测试文件（使用: make test-one TEST=tests/test_log_api.py）
	@echo "$(COLOR_GREEN)运行测试: $(TEST)$(COLOR_RESET)"
	uv run pytest $(TEST) -v

test-watch: ## 监视文件变化并自动运行测试
	@echo "$(COLOR_GREEN)监视模式: 文件变化时自动运行测试$(COLOR_RESET)"
	uv run pytest-watch

##@ 代码质量

lint: ## 运行代码检查（使用 ruff）
	@echo "$(COLOR_GREEN)运行代码检查...$(COLOR_RESET)"
	uv run ruff check .

format: ## 格式化代码（使用 ruff）
	@echo "$(COLOR_GREEN)格式化代码...$(COLOR_RESET)"
	uv run ruff format .

format-check: ## 检查代码格式（不修改文件）
	@echo "$(COLOR_GREEN)检查代码格式...$(COLOR_RESET)"
	uv run ruff format --check .

lint-fix: ## 自动修复代码问题
	@echo "$(COLOR_GREEN)自动修复代码问题...$(COLOR_RESET)"
	uv run ruff check --fix .

##@ 数据库与配置

clean-config: ## 清除配置文件（重置为默认）
	@echo "$(COLOR_YELLOW)清除配置文件...$(COLOR_RESET)"
	@if [ -f config.yaml ]; then rm config.yaml; echo "已删除 config.yaml"; fi

##@ 清理

clean: ## 清理临时文件和缓存
	@echo "$(COLOR_YELLOW)清理临时文件...$(COLOR_RESET)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(COLOR_GREEN)清理完成$(COLOR_RESET)"

clean-all: clean ## 深度清理（包括虚拟环境）
	@echo "$(COLOR_YELLOW)深度清理...$(COLOR_RESET)"
	rm -rf $(VENV_DIR)
	@echo "$(COLOR_GREEN)深度清理完成$(COLOR_RESET)"

##@ 开发工具

shell: ## 在虚拟环境中启动 Python shell
	@echo "$(COLOR_GREEN)启动 Python shell...$(COLOR_RESET)"
	uv run python

ipython: ## 在虚拟环境中启动 IPython
	@echo "$(COLOR_GREEN)启动 IPython...$(COLOR_RESET)"
	uv run ipython

db-shell: ## 启动数据库 shell（如果使用数据库）
	@echo "$(COLOR_YELLOW)此项目未使用数据库$(COLOR_RESET)"

##@ CI/CD

check: lint test-cov ## 运行所有检查（代码检查 + 测试 + 覆盖率）
	@echo "$(COLOR_GREEN)所有检查完成！$(COLOR_RESET)"

all: clean install format lint test ## 完整工作流：清理、安装、格式化、检查、测试

##@ 示例与文档

docs: ## 打开项目文档（FastAPI 自动生成）
	@echo "$(COLOR_GREEN)打开文档: http://localhost:$(PORT)/docs$(COLOR_RESET)"
	@echo "$(COLOR_YELLOW)请先启动服务器: make dev$(COLOR_RESET)"

example-client: ## 运行示例客户端
	@echo "$(COLOR_GREEN)运行示例客户端...$(COLOR_RESET)"
	@if [ -f examples/send_logs.py ]; then \
		uv run python examples/send_logs.py; \
	else \
		echo "$(COLOR_YELLOW)未找到示例客户端文件$(COLOR_RESET)"; \
	fi

test-api: ## 测试日志 API（可以指定 URL: make test-api URL=http://192.168.3.194:8000）
	@echo "$(COLOR_GREEN)测试日志 API...$(COLOR_RESET)"
	@uv run python scripts/test_log_api.py $(URL)

diagnose: ## 诊断 API 连接问题（可以指定 URL: make diagnose URL=http://192.168.3.194:8000）
	@echo "$(COLOR_GREEN)诊断 API 连接...$(COLOR_RESET)"
	@uv run python scripts/diagnose_request.py $(URL)

##@ 信息

info: ## 显示项目信息
	@echo "$(COLOR_BOLD)项目信息:$(COLOR_RESET)"
	@echo "  项目名称: $(PROJECT_NAME)"
	@echo "  Python 版本: $(PYTHON_VERSION)"
	@echo "  虚拟环境: $(VENV_DIR)"
	@echo "  服务器地址: http://$(HOST):$(PORT)"
	@echo ''
	@echo "$(COLOR_BOLD)Git 信息:$(COLOR_RESET)"
	@git remote -v 2>/dev/null || echo "  未初始化 Git 仓库"
	@git status -sb 2>/dev/null || echo "  无 Git 信息"

deps: ## 显示依赖树
	@echo "$(COLOR_GREEN)项目依赖:$(COLOR_RESET)"
	uv pip list

deps-update: ## 更新所有依赖
	@echo "$(COLOR_YELLOW)更新依赖...$(COLOR_RESET)"
	uv sync --upgrade
