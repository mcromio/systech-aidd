# Настройка GitHub Container Registry (ghcr.io)

> Дата создания: 18.10.2025
> Спринт: D1 - Build & Publish

## Обзор

Эта инструкция описывает процесс настройки GitHub Container Registry для автоматической публикации Docker образов через GitHub Actions.

---

## Шаг 1: Проверка репозитория

Убедитесь что репозиторий настроен правильно:

```bash
git remote -v
# Должно показать: https://github.com/mcromio/systech-aidd.git
```

---

## Шаг 2: Настройка Permissions для GitHub Actions

### 2.1 Workflow Permissions

1. Перейдите в настройки репозитория:
   ```
   GitHub → Ваш репозиторий → Settings
   ```

2. В боковом меню выберите:
   ```
   Settings → Actions → General
   ```

3. Прокрутите вниз до секции **"Workflow permissions"**

4. Выберите:
   ```
   ✅ Read and write permissions
   ```

5. **Обязательно** установите галочку:
   ```
   ✅ Allow GitHub Actions to create and approve pull requests
   ```

6. Нажмите **"Save"**

**Зачем это нужно?**
- Позволяет workflow публиковать образы в ghcr.io
- Используется автоматический `GITHUB_TOKEN` (не нужен Personal Access Token)

---

## Шаг 3: Использование GITHUB_TOKEN

В workflow **НЕ НУЖНО** создавать Personal Access Token!

GitHub автоматически предоставляет `GITHUB_TOKEN` для каждого workflow:

```yaml
- name: Login to GitHub Container Registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}  # Автоматически доступен!
```

**Преимущества GITHUB_TOKEN:**
- ✅ Автоматически создается для каждого workflow
- ✅ Ограниченное время жизни (безопаснее)
- ✅ Не нужно хранить в Secrets
- ✅ Работает из коробки

---

## Шаг 4: (Опционально) Personal Access Token

Если по какой-то причине нужен PAT:

### 4.1 Создание PAT

1. Перейдите в настройки профиля:
   ```
   GitHub → Settings (профиль, не репозиторий)
   ```

2. В боковом меню:
   ```
   Developer settings → Personal access tokens → Tokens (classic)
   ```

3. Нажмите **"Generate new token"** → **"Generate new token (classic)"**

4. Заполните:
   - **Note:** `systech-aidd-ghcr` (описание токена)
   - **Expiration:** `90 days` (или больше)
   - **Scopes:** выберите:
     ```
     ✅ write:packages
     ✅ read:packages
     ✅ delete:packages (опционально)
     ```

5. Нажмите **"Generate token"**

6. **ВАЖНО:** Скопируйте токен - он больше не будет показан!

### 4.2 Добавление PAT в Secrets

1. Перейдите в настройки репозитория:
   ```
   Settings → Secrets and variables → Actions
   ```

2. Нажмите **"New repository secret"**

3. Заполните:
   - **Name:** `GHCR_TOKEN`
   - **Secret:** вставьте скопированный токен

4. Нажмите **"Add secret"**

5. В workflow используйте:
   ```yaml
   password: ${{ secrets.GHCR_TOKEN }}
   ```

---

## Шаг 5: Первая публикация образов

После настройки и запуска workflow:

1. Перейдите на главную страницу вашего профиля GitHub
2. Вкладка **"Packages"**
3. Вы увидите опубликованные образы:
   ```
   systech-aidd-bot
   systech-aidd-api
   systech-aidd-frontend
   ```

По умолчанию образы будут **Private** (требуют авторизацию).

---

## Шаг 6: Сделать образы публичными

Чтобы образы можно было скачать без авторизации:

### 6.1 Для каждого пакета:

1. Перейдите на страницу пакета:
   ```
   GitHub → Your profile → Packages → systech-aidd-bot
   ```

2. Нажмите **"Package settings"** (справа)

3. Прокрутите вниз до секции **"Danger Zone"**

4. Найдите **"Change package visibility"**

5. Нажмите **"Change visibility"**

6. Выберите **"Public"**

7. Введите название пакета для подтверждения

8. Нажмите **"I understand the consequences, change package visibility"**

### 6.2 Повторите для всех трех пакетов:

- `systech-aidd-bot`
- `systech-aidd-api`
- `systech-aidd-frontend`

**После этого:**

```bash
# Образы доступны без docker login!
docker pull ghcr.io/mcromio/systech-aidd-bot:latest
docker pull ghcr.io/mcromio/systech-aidd-api:latest
docker pull ghcr.io/mcromio/systech-aidd-frontend:latest
```

---

## Шаг 7: Проверка доступности образов

### 7.1 Без авторизации:

```bash
# Попробовать pull без логина
docker logout ghcr.io
docker pull ghcr.io/mcromio/systech-aidd-bot:latest
```

Должно работать без ошибок!

### 7.2 Просмотр информации:

```bash
# Список тегов образа
docker images | grep systech-aidd

# Инспекция образа
docker image inspect ghcr.io/mcromio/systech-aidd-bot:latest
```

---

## Безопасность

### ⚠️ ВАЖНО: Public packages

**Когда пакеты публичные:**

- ✅ Любой может скачать образы
- ✅ Образы доступны без токена
- ⚠️ **КОД ПРИЛОЖЕНИЯ ВИДЕН ВСЕМ**
- ⚠️ **Нельзя хранить секреты в образах!**

### 🔒 Защита секретов:

1. **Проверьте `.dockerignore`:**
   ```
   .env
   .env.local
   .env.production
   *.key
   *.pem
   secrets/
   ```

2. **Никогда не используйте hardcoded секреты:**
   ```python
   # ❌ ПЛОХО
   API_KEY = "sk-abc123..."

   # ✅ ХОРОШО
   API_KEY = os.getenv("OPENAI_API_KEY")
   ```

3. **Проверка образов после публикации:**
   ```bash
   # Скачать образ
   docker pull ghcr.io/mcromio/systech-aidd-bot:latest

   # Инспекция (не должно быть .env файлов)
   docker image inspect ghcr.io/mcromio/systech-aidd-bot:latest

   # Список файлов в образе
   docker run --rm ghcr.io/mcromio/systech-aidd-bot:latest ls -la
   ```

---

## Переход на Private packages (в будущем)

Если позже нужно сделать пакеты приватными:

1. Change visibility → Private
2. На сервере для pull понадобится авторизация:
   ```bash
   echo $GHCR_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
   docker pull ghcr.io/mcromio/systech-aidd-bot:latest
   ```

---

## Troubleshooting

### Ошибка: "denied: permission_denied"

**Проблема:** Workflow не может публиковать образы

**Решение:**
1. Проверьте Workflow permissions (Шаг 2)
2. Убедитесь что выбрано "Read and write permissions"

---

### Ошибка: "package does not exist"

**Проблема:** Первая публикация еще не прошла

**Решение:**
1. Запустите workflow через GitHub UI
2. Дождитесь успешного завершения
3. Пакеты появятся в профиле

---

### Образы не видны в profile

**Проблема:** Пакеты привязаны к репозиторию, а не к профилю

**Решение:**
1. Перейдите в репозиторий → Packages
2. Или используйте прямую ссылку:
   ```
   https://github.com/users/mcromio/packages/container/systech-aidd-bot
   ```

---

## Полезные команды

```bash
# Login в ghcr.io (если нужно)
echo $GITHUB_TOKEN | docker login ghcr.io -u mcromio --password-stdin

# Logout
docker logout ghcr.io

# Список локальных образов из ghcr.io
docker images | grep ghcr.io

# Удалить локальный образ
docker rmi ghcr.io/mcromio/systech-aidd-bot:latest

# Pull конкретного тега
docker pull ghcr.io/mcromio/systech-aidd-bot:sha-abc1234
```

---

## Следующие шаги

1. ✅ Настроить permissions
2. ✅ Запустить workflow
3. ✅ Сделать packages публичными
4. ➡️ Протестировать pull образов: [testing-workflow.md](testing-workflow.md)
5. ➡️ Использовать образы: [using-registry-images.md](using-registry-images.md)

