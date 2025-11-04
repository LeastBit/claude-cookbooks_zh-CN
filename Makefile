.PHONY: help format lint check fix test clean install

# 默认目标
help:
	@echo "可用目标:"
	@echo "  make format        - 使用 ruff 格式化代码"
	@echo "  make lint          - 运行 ruff 代码检查"
	@echo "  make check         - 运行所有检查（格式检查 + 代码检查）"
	@echo "  make fix           - 使用 ruff 自动修复问题"
	@echo "  make test          - 运行测试"
	@echo "  make install       - 安装依赖"
	@echo "  make clean         - 移除缓存文件"

# 使用 ruff 格式化代码
format:
	@echo "使用 ruff 格式化代码..."
	uv run ruff format .

# 检查代码格式但不修改
format-check:
	@echo "检查代码格式..."
	uv run ruff format --check .

# 运行 ruff 代码检查
lint:
	@echo "运行 ruff 代码检查..."
	uv run ruff check .

# 运行所有检查
check: format-check lint
	@echo "所有检查完成!"

# 使用 ruff 自动修复问题
fix:
	@echo "自动修复 ruff 问题..."
	uv run ruff check --fix .
	uv run ruff format .

# 运行测试
test:
	@echo "运行测试..."
	uv run pytest

# 安装依赖
install:
	@echo "安装依赖..."
	uv sync --all-extras

# 清理缓存文件
clean:
	@echo "清理缓存文件..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "缓存已清理!"
