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

# === Database команды (S1: Persistent Storage) ===

db-up: ## Запустить PostgreSQL в Docker
	@echo "$(GREEN)Запуск PostgreSQL...$(NC)"
	docker-compose -f docker-compose.dev.yml up -d postgres
	@echo "Ожидание готовности БД..."
	@sleep 5
	@echo "$(GREEN)PostgreSQL запущен$(NC)"

db-down: ## Остановить PostgreSQL
	@echo "$(GREEN)Остановка PostgreSQL...$(NC)"
	docker-compose -f docker-compose.dev.yml down

db-logs: ## Просмотр логов PostgreSQL
	docker-compose -f docker-compose.dev.yml logs -f postgres

db-migrate: ## Применить миграции
	@echo "$(GREEN)Применение миграций...$(NC)"
	uv run alembic upgrade head
	@echo "$(GREEN)Миграции применены$(NC)"

db-rollback: ## Откатить последнюю миграцию
	@echo "$(YELLOW)Откат последней миграции...$(NC)"
	uv run alembic downgrade -1

db-history: ## История миграций
	uv run alembic history

db-current: ## Текущая версия БД
	uv run alembic current

db-reset: ## Сбросить БД и накатить заново
	@echo "$(YELLOW)ВНИМАНИЕ: Все данные будут удалены!$(NC)"
	@read -p "Продолжить? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		uv run alembic downgrade base; \
		uv run alembic upgrade head; \
		echo "$(GREEN)БД пересоздана$(NC)"; \
	fi

db-shell: ## Подключиться к psql
	docker-compose -f docker-compose.dev.yml exec postgres psql -U llm_user -d llm_assistant

db-revision: ## Создать новую миграцию (автогенерация)
	@read -p "Название миграции: " name; \
	uv run alembic revision --autogenerate -m "$$name"

# === Combined команды ===

db-init: db-up db-migrate ## Инициализация БД (запуск + миграции)
	@echo "$(GREEN)БД инициализирована и готова к работе!$(NC)"

db-restart: db-down db-up ## Перезапуск БД

# === PgAdmin (опционально) ===

pgadmin-up: ## Запустить PgAdmin
	@echo "$(GREEN)Запуск PgAdmin...$(NC)"
	docker-compose -f docker-compose.dev.yml --profile with-pgadmin up -d pgadmin
	@echo "$(GREEN)PgAdmin доступен: http://localhost:5050$(NC)"
	@echo "Email: admin@localhost.com, Password: admin"

pgadmin-down: ## Остановить PgAdmin
	docker-compose -f docker-compose.dev.yml --profile with-pgadmin stop pgadmin

# === Mock Stats API команды (FE-S1) ===

api-run: ## Запустить Mock Stats API сервер
	@echo "$(GREEN)Запуск Mock Stats API...$(NC)"
	@echo "API будет доступен на: http://localhost:8000"
	@echo "Swagger UI: http://localhost:8000/docs"
	@echo "ReDoc: http://localhost:8000/redoc"
	uv run python -m src.api_main

api-test: ## Тестировать API endpoints (curl)
	@echo "$(GREEN)Тестирование API endpoints...$(NC)"
	@echo ""
	@echo "$(YELLOW)1. Health check:$(NC)"
	curl -s http://localhost:8000/health | python -m json.tool
	@echo ""
	@echo "$(YELLOW)2. Stats for day:$(NC)"
	curl -s "http://localhost:8000/api/v1/stats?period=day" | python -m json.tool | head -20
	@echo ""
	@echo "$(YELLOW)3. Stats for week:$(NC)"
	curl -s "http://localhost:8000/api/v1/stats?period=week" | python -m json.tool | head -20
	@echo ""
	@echo "$(YELLOW)4. Stats for month:$(NC)"
	curl -s "http://localhost:8000/api/v1/stats?period=month" | python -m json.tool | head -20
	@echo ""
	@echo "$(GREEN)Все endpoints работают!$(NC)"

api-docs: ## Открыть API документацию в браузере
	@echo "$(GREEN)Открытие документации...$(NC)"
	@echo "Swagger UI: http://localhost:8000/docs"
	@echo "ReDoc: http://localhost:8000/redoc"
	@python -m webbrowser -t "http://localhost:8000/docs"

api-test-unit: ## Запустить unit-тесты для API модулей
	@echo "$(GREEN)Запуск unit-тестов API...$(NC)"
	uv run pytest tests/test_mock_stat_collector.py tests/test_api_stats.py -v

api-coverage: ## Проверить покрытие тестами API модулей
	@echo "$(GREEN)Проверка покрытия API модулей...$(NC)"
	uv run pytest tests/test_mock_stat_collector.py tests/test_api_stats.py -v --cov=src/api --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)HTML отчет: htmlcov/index.html$(NC)"

# === Frontend команды (FE-S2) ===

fe-install: ## Установить frontend зависимости
	@echo "$(GREEN)Установка frontend зависимостей...$(NC)"
	cd frontend/app && pnpm install

fe-dev: ## Запустить frontend dev сервер
	@echo "$(GREEN)Запуск frontend dev сервера...$(NC)"
	@echo "Frontend доступен: http://localhost:3000"
	cd frontend/app && pnpm dev

fe-build: ## Собрать frontend для production
	@echo "$(GREEN)Сборка frontend...$(NC)"
	cd frontend/app && pnpm build

fe-start: ## Запустить production сервер frontend
	@echo "$(GREEN)Запуск production frontend...$(NC)"
	cd frontend/app && pnpm start

fe-lint: ## Проверить frontend код линтером
	@echo "$(GREEN)Проверка frontend кода...$(NC)"
	cd frontend/app && pnpm lint

fe-format: ## Форматировать frontend код
	@echo "$(GREEN)Форматирование frontend кода...$(NC)"
	cd frontend/app && pnpm format

fe-type-check: ## Проверить TypeScript типы
	@echo "$(GREEN)Проверка TypeScript типов...$(NC)"
	cd frontend/app && pnpm type-check

fe-quality: fe-lint fe-type-check ## Полная проверка качества frontend
	@echo "$(GREEN)Frontend проверка пройдена!$(NC)"

# === Docker Compose (D1: Build & Publish) ===

compose-build: ## Локальная сборка и запуск всех сервисов
	@echo "$(GREEN)Локальная сборка через docker-compose...$(NC)"
	docker-compose up -d --build

compose-up: ## Запуск сервисов (без rebuild)
	@echo "$(GREEN)Запуск сервисов...$(NC)"
	docker-compose up -d

compose-pull: ## Pull образов из GitHub Container Registry
	@echo "$(GREEN)Загрузка образов из ghcr.io...$(NC)"
	docker-compose -f docker-compose.prod.yml pull

compose-prod: compose-pull ## Запуск из registry образов (с автоматическим pull)
	@echo "$(GREEN)Запуск из registry образов...$(NC)"
	docker-compose -f docker-compose.prod.yml up -d
	@echo "$(GREEN)Все сервисы запущены из registry!$(NC)"

compose-down: ## Остановить все сервисы
	@echo "$(YELLOW)Остановка сервисов...$(NC)"
	docker-compose down 2>/dev/null || true
	docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

compose-logs: ## Просмотр логов всех сервисов
	@echo "$(GREEN)Логи сервисов:$(NC)"
	docker-compose logs -f

compose-ps: ## Статус всех сервисов
	@echo "$(GREEN)Статус сервисов:$(NC)"
	docker-compose ps

