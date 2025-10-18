# Тестирование GitHub Actions Workflow

> Дата создания: 18.10.2025
> Спринт: D1 - Build & Publish

## Обзор

Эта инструкция описывает процесс тестирования GitHub Actions workflow для сборки и публикации Docker образов.

---

## Способ 1: Ручной запуск через GitHub UI (Рекомендуется для MVP)

### Шаг 1: Commit и Push workflow

```bash
# Убедитесь что workflow файл закоммичен
git add .github/workflows/build.yml
git commit -m "feat(devops): add GitHub Actions workflow for building Docker images"
git push origin devops
```

### Шаг 2: Запуск workflow

1. Перейдите в репозиторий на GitHub
2. Откройте вкладку **"Actions"**
3. В списке слева выберите **"Build and Push Docker Images"**
4. Нажмите кнопку **"Run workflow"** (справа вверху)
5. Выберите ветку: **devops**
6. Нажмите зеленую кнопку **"Run workflow"**

### Шаг 3: Мониторинг выполнения

1. Workflow появится в списке запусков
2. Кликните на название запуска (например, "feat(devops): add GitHub Actions...")
3. Откроется страница с job'ом **"build-and-push"**
4. Кликните на job чтобы увидеть детальные логи

**Что смотреть в логах:**

- ✅ **Checkout code** - репозиторий склонирован
- ✅ **Set up Docker Buildx** - Docker настроен
- ✅ **Log in to GitHub Container Registry** - авторизация успешна
- ✅ **Extract metadata** - теги сгенерированы
- ✅ **Build and push Docker image** - образ собран и опубликован
- ✅ **Security check** - проверка безопасности пройдена
- ✅ **Image summary** - информация об образе

### Шаг 4: Проверка результатов

После успешного завершения:

1. Перейдите на главную страницу вашего профиля GitHub
2. Вкладка **"Packages"**
3. Должны появиться 3 пакета:
   - `systech-aidd-bot`
   - `systech-aidd-api`
   - `systech-aidd-frontend`

---

## Способ 2: Автоматический trigger при push

### Тестирование trigger на push:

```bash
# Сделайте любое изменение в коде
echo "# Test workflow trigger" >> src/main.py

# Commit и push в devops ветку
git add src/main.py
git commit -m "test: trigger workflow"
git push origin devops
```

Workflow запустится автоматически!

### Trigger при изменении Dockerfile:

```bash
# Изменить Dockerfile (например, добавить комментарий)
echo "# Updated" >> Dockerfile.bot

git add Dockerfile.bot
git commit -m "chore: update Dockerfile"
git push origin devops
```

---

## Способ 3: Локальное тестирование с Act (Опционально)

**Act** - инструмент для запуска GitHub Actions локально.

### Установка Act:

**Windows (через Chocolatey):**
```bash
choco install act-cli
```

**Windows (через Scoop):**
```bash
scoop install act
```

**Linux/macOS:**
```bash
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash
```

### Использование Act:

```bash
# Список workflows
act -l

# Запуск workflow с событием push
act push

# Запуск конкретного job
act -j build-and-push

# Dry run (без выполнения)
act push --dryrun
```

**Примечание:**
- Act использует Docker для эмуляции GitHub runners
- Может не работать с secrets и ghcr.io авторизацией
- Хорош для базовой проверки синтаксиса

---

## Проверка опубликованных образов

### Шаг 1: Pull образов

После успешной публикации:

```bash
# Убедитесь что Docker запущен
docker --version

# Pull образов (без авторизации, если packages публичные)
docker pull ghcr.io/mcromio/systech-aidd-bot:latest
docker pull ghcr.io/mcromio/systech-aidd-api:latest
docker pull ghcr.io/mcromio/systech-aidd-frontend:latest
```

**Если образы private:**
```bash
# Login
echo $GITHUB_TOKEN | docker login ghcr.io -u mcromio --password-stdin

# Затем pull
docker pull ghcr.io/mcromio/systech-aidd-bot:latest
```

### Шаг 2: Проверка образов

```bash
# Список загруженных образов
docker images | grep systech-aidd

# Инспекция образа
docker image inspect ghcr.io/mcromio/systech-aidd-bot:latest

# Проверка размера
docker image ls ghcr.io/mcromio/systech-aidd-bot:latest

# Запуск контейнера для тестирования
docker run --rm ghcr.io/mcromio/systech-aidd-bot:latest python --version
```

### Шаг 3: Security audit (проверка секретов)

```bash
# Проверка что нет .env файлов
docker run --rm ghcr.io/mcromio/systech-aidd-bot:latest find / -name ".env*" 2>/dev/null

# Инспекция ENV переменных
docker image inspect ghcr.io/mcromio/systech-aidd-bot:latest --format='{{json .Config.Env}}' | jq

# Список файлов в образе
docker run --rm ghcr.io/mcromio/systech-aidd-bot:latest ls -la /app
```

**Должно быть:**
- ✅ Нет .env файлов
- ✅ Нет hardcoded секретов в ENV
- ✅ Только необходимые файлы приложения

---

## Запуск через docker-compose.prod.yml

### Шаг 1: Подготовка

```bash
# Убедитесь что есть .env файл
ls -la .env

# Если нет - скопировать из примера
cp .env.example .env

# Отредактировать переменные
nano .env  # или notepad .env на Windows
```

### Шаг 2: Остановить локальные контейнеры

```bash
# Остановить локальную сборку
docker-compose down
```

### Шаг 3: Запуск из registry

```bash
# Pull и запуск
make compose-prod

# Или вручную
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d
```

### Шаг 4: Проверка работоспособности

```bash
# Статус сервисов
docker-compose -f docker-compose.prod.yml ps

# Логи
docker-compose -f docker-compose.prod.yml logs -f

# Проверка API
curl http://localhost:8000/health

# Проверка Frontend
curl http://localhost:3000
```

**Ожидаемый результат:**
```
NAME                     STATUS           PORTS
llm-assistant-db         Up (healthy)     5432
llm-assistant-bot        Up (healthy)     -
llm-assistant-api        Up (healthy)     8000
llm-assistant-frontend   Up (healthy)     3000
```

---

## Troubleshooting

### Ошибка: "denied: permission_denied"

**Проблема:** Workflow не может публиковать образы

**Решение:**
1. Проверить Workflow permissions в Settings
2. Выбрать "Read and write permissions"
3. Перезапустить workflow

---

### Ошибка: "image not found" при pull

**Проблема:** Образ еще не опубликован или private

**Решение:**
1. Проверить статус workflow - успешно ли завершился
2. Проверить Packages в GitHub профиле
3. Если private - сделать public (см. github-registry-setup.md)

---

### Ошибка: "unauthorized: unauthenticated"

**Проблема:** Образы private, нужна авторизация

**Решение:**
```bash
echo $GITHUB_TOKEN | docker login ghcr.io -u mcromio --password-stdin
docker pull ghcr.io/mcromio/systech-aidd-bot:latest
```

---

### Ошибка в security check step

**Проблема:** Найдены .env файлы или секреты в образе

**Решение:**
1. Проверить `.dockerignore` - должен содержать `.env`
2. Проверить что в коде нет hardcoded секретов
3. Пересобрать образ локально:
   ```bash
   docker build -f Dockerfile.bot -t test .
   docker run --rm test find / -name ".env*" 2>/dev/null
   ```

---

### Workflow зависает на build step

**Проблема:** Недостаточно ресурсов или сетевые проблемы

**Решение:**
1. Подождать 10-15 минут (первая сборка долгая)
2. Проверить Docker Hub rate limits
3. Отменить и перезапустить workflow

---

## Полезные команды

```bash
# Просмотр всех запусков workflow
gh run list --workflow=build.yml

# Просмотр логов последнего запуска
gh run view --log

# Отмена запущенного workflow
gh run cancel <run-id>

# Перезапуск failed workflow
gh run rerun <run-id>
```

---

## Checklist успешного тестирования

- [ ] Workflow запустился без ошибок
- [ ] Все 3 job'а (bot, api, frontend) завершились успешно
- [ ] Security check пройден для всех образов
- [ ] Packages появились в GitHub профиле
- [ ] Packages сделаны публичными
- [ ] Образы можно pull без авторизации
- [ ] docker-compose.prod.yml запускает все сервисы
- [ ] API отвечает на http://localhost:8000
- [ ] Frontend доступен на http://localhost:3000
- [ ] Bot работает (видны логи)

---

## Следующие шаги

1. ✅ Workflow протестирован
2. ✅ Образы опубликованы
3. ✅ Сервисы запущены из registry
4. ➡️ Обновить документацию: README.md
5. ➡️ Использовать образы в production: [using-registry-images.md](using-registry-images.md)

---

## Полезные ссылки

- [GitHub Actions Logs](https://github.com/mcromio/systech-aidd/actions)
- [GitHub Packages](https://github.com/users/mcromio/packages?repo_name=systech-aidd)
- [Act Documentation](https://github.com/nektos/act)

