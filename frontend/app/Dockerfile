# Dockerfile для Next.js Frontend
# Node 22 Alpine - минимальный образ для MVP

FROM node:22-alpine

# Метаданные
LABEL maintainer="STSI Team"
LABEL description="LLM Assistant Frontend (Next.js)"

# Установка pnpm глобально
RUN npm install -g pnpm

# Рабочая директория
WORKDIR /app

# Копирование файлов зависимостей
# Важно: build context будет ./frontend/app в docker-compose
COPY package.json pnpm-lock.yaml ./

# Установка зависимостей
RUN pnpm install --frozen-lockfile

# Копирование всего кода
COPY . .

# Сборка Next.js приложения
RUN pnpm build

# Переменные окружения
ENV NODE_ENV=production
ENV PORT=3000

# Порт Frontend
EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Запуск production сервера
CMD ["pnpm", "start"]

