# DevOps Roadmap - MVP Approach

> Фокус на простоте и скорости. Путь от локального запуска к удаленному серверу с автоматическим развертыванием.

## Обзор спринтов

| Спринт | Описание | Статус | План |
|--------|---------|--------|------|
| [D0](#спринт-d0-basic-docker-setup) | Basic Docker Setup | ✅ Completed | [План D0](plans/d0-basic-docker-setup.md) |
| [D1](#спринт-d1-build--publish) | Build & Publish | ✅ Completed | [План D1](plans/d1-build-publish.md) |
| [D2](#спринт-d2-развертывание-на-сервер) | Развертывание на сервер | ✅ Completed | [План D2](plans/d2-manual-deploy.md) |
| [D3](#спринт-d3-auto-deploy) | Auto Deploy | ⏳ Pending | - |

---

## Спринт D0: Basic Docker Setup

**Цель:** Запустить все сервисы локально через `docker-compose` одной командой.

### Состав работ
- Создать Dockerfile для Bot (Python + UV)
- Создать Dockerfile для API (Python + UV)
- Создать Dockerfile для Frontend (Next.js + pnpm)
- Создать `docker-compose.yml` с 4 сервисами: PostgreSQL, Bot, API, Frontend
- Создать `.dockerignore` файлы для оптимизации сборки
- Обновить `README.md` с инструкциями по запуску

---

## Спринт D1: Build & Publish

**Цель:** Автоматическая сборка и публикация Docker образов в GitHub Container Registry.

### Состав работ
- Создать GitHub Actions workflow `.github/workflows/build.yml`
- Настроить сборку и публикацию в ghcr.io с тегом `latest`
- Добавить инструкцию по настройке permissions в GitHub Actions
- Обновить `README.md` с badges статуса сборки

---

## Спринт D2: Развертывание на сервер

**Цель:** Развернуть приложение на удаленном сервере вручную (пошаговая инструкция).

### Состав работ
- Создать пошаговую инструкцию по ручному деплою на сервер
- Подготовить `.env.production` шаблон с документацией
- Создать скрипт проверки работоспособности (`scripts/deploy-check.sh`)
- Описать процесс: SSH подключение → копирование конфигов → docker login → docker-compose up

---

## Спринт D3: Auto Deploy

**Цель:** Автоматическое развертывание на сервер через GitHub Actions по кнопке.

### Состав работ
- Создать GitHub Actions workflow `.github/workflows/deploy.yml`
- Настроить SSH подключение к серверу с помощью GitHub Secrets
- Автоматический pull новых образов и перезапуск сервисов
- Добавить инструкцию по настройке GitHub Secrets (SSH_KEY, HOST, USER)
- Обновить `README.md` с кнопкой Deploy
