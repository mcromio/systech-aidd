.PHONY: help install dev run test lint format clean

# Цвета для вывода
GREEN  := \033[0;32m
YELLOW := \033[0;33m
NC     := \033[0m

help: ## Показать справку
	@echo "$(GREEN)Доступные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Установить зависимости
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	uv sync --no-dev

dev: ## Установить зависимости для разработки
	@echo "$(GREEN)Установка dev зависимостей...$(NC)"
	uv sync

run: ## Запустить бота локально
	@echo "$(GREEN)Запуск бота...$(NC)"
	uv run python -m src.main

test: ## Запустить тесты
	@echo "$(GREEN)Запуск тестов...$(NC)"
	uv run pytest tests/ -v --cov=src --cov-report=term-missing

test-quick: ## Быстрые тесты (без coverage)
	@echo "$(GREEN)Быстрые тесты...$(NC)"
	uv run pytest tests/ -v

lint: ## Проверить код линтером
	@echo "$(GREEN)Проверка кода...$(NC)"
	uv run ruff check src/ tests/

type-check: ## Проверка типов с mypy
	@echo "$(GREEN)Проверка типов...$(NC)"
	uv run mypy src/

format: ## Форматировать код
	@echo "$(GREEN)Форматирование кода...$(NC)"
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

clean: ## Очистить временные файлы
	@echo "$(GREEN)Очистка...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/

setup: ## Первоначальная настройка проекта
	@echo "$(GREEN)Настройка проекта...$(NC)"
	uv sync
	@echo "$(GREEN)Проект настроен!$(NC)"
	@echo "Не забудьте создать .env файл на основе .env.example"

check: lint type-check test ## Проверка кода, типов и тесты

all: clean format lint type-check test ## Полная проверка проекта
	@echo "$(GREEN)Все проверки пройдены!$(NC)"

