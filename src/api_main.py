"""Entrypoint для Mock Stats API сервера."""

import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.chat_router import init_chat_router
from src.api.chat_router import router as chat_router
from src.api.router import router
from src.config import Config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title="LLM Assistant Stats API",
    description="REST API для получения статистики диалогов LLM-ассистента",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Настройка CORS для разработки frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://localhost:5174",  # Vite alternative port
        "http://localhost:8080",  # Альтернативный порт
        "http://89.223.67.136:3003",  # Production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(router)
app.include_router(chat_router)

logger.info("Stats API initialized")


@app.on_event("startup")
async def startup_event() -> None:
    """Событие запуска приложения."""
    # Инициализируем Chat router с конфигурацией
    config = Config()
    init_chat_router(config)

    logger.info("Starting Stats API server...")
    logger.info("API documentation available at: http://localhost:8000/docs")
    logger.info("ReDoc documentation available at: http://localhost:8000/redoc")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Событие остановки приложения."""
    logger.info("Shutting down Stats API server...")


if __name__ == "__main__":
    import uvicorn

    logger.info("Running Stats API with uvicorn...")
    uvicorn.run(
        "src.api_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Hot reload для разработки
        log_level="info",
    )
