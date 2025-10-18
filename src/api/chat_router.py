"""Chat API router для веб-интерфейса."""

import logging
from datetime import datetime

from aiogram import Bot
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.chat_models import (
    Dialog,
    DialogsResponse,
    LastMessage,
    MessageItem,
    MessagesResponse,
    SendMessageRequest,
    SendMessageResponse,
)
from src.config import Config
from src.db.engine import create_engine, get_session_factory
from src.db.models import Message, User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["Chat"])

# Глобальные зависимости (будут инициализированы при старте)
_session_factory = None
_bot = None
_config = None
_llm_client = None


def init_chat_router(config: Config) -> None:
    """Инициализация Chat router с конфигурацией."""
    global _session_factory, _bot, _config, _llm_client
    _config = config
    engine = create_engine(config)
    _session_factory = get_session_factory(engine)
    try:
        _bot = Bot(token=config.telegram_bot_token)
        logger.info("Chat router инициализирован с Telegram Bot")
    except Exception as e:
        logger.warning(
            f"Не удалось инициализировать Telegram Bot: {e}. Отправка сообщений будет недоступна."
        )
        _bot = None

    # Инициализируем LLM клиент
    try:
        from src.llm_client import LLMClient

        _llm_client = LLMClient(config)  # Используем дефолтные tools
        logger.info("LLM Client инициализирован для Chat router")
    except Exception as e:
        logger.warning(f"Не удалось инициализировать LLM Client: {e}")
        _llm_client = None

    logger.info("Chat router инициализирован")


@router.get(
    "/dialogs",
    response_model=DialogsResponse,
    summary="Получить список диалогов",
    description="Возвращает список всех диалогов с пользователями бота",
)
async def get_dialogs() -> DialogsResponse:
    """Получить список всех диалогов."""
    if _session_factory is None:
        raise HTTPException(status_code=500, detail="Chat router not initialized")

    try:
        async with _session_factory() as session:
            session: AsyncSession

            # Получаем всех пользователей с сообщениями
            users_query = select(User).order_by(User.telegram_id)
            result = await session.execute(users_query)
            users = result.scalars().all()

            dialogs = []
            for user in users:
                # Получаем последнее сообщение пользователя
                last_msg_query = (
                    select(Message)
                    .where(Message.user_id == user.id)
                    .order_by(desc(Message.created_at))
                    .limit(1)
                )
                last_msg_result = await session.execute(last_msg_query)
                last_msg = last_msg_result.scalar_one_or_none()

                # Если у пользователя нет сообщений - пропускаем
                if last_msg is None:
                    continue

                # Подсчет сообщений
                count_query = select(func.count(Message.id)).where(Message.user_id == user.id)
                total_messages = await session.scalar(count_query) or 0

                dialog = Dialog(
                    user_id=user.telegram_id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    last_message=LastMessage(
                        text=last_msg.content,
                        timestamp=last_msg.created_at,
                        role=last_msg.role,
                    ),
                    unread_count=0,  # TODO: реализовать отслеживание прочитанных
                    total_messages=total_messages,
                )
                dialogs.append(dialog)

            # Сортируем по времени последнего сообщения
            dialogs.sort(
                key=lambda d: d.last_message.timestamp if d.last_message else datetime.min,
                reverse=True,
            )

            return DialogsResponse(dialogs=dialogs)

    except Exception as e:
        logger.error(f"Ошибка получения диалогов: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch dialogs: {str(e)}") from e


@router.get(
    "/dialogs/{user_id}/messages",
    response_model=MessagesResponse,
    summary="Получить историю сообщений",
    description="Возвращает историю сообщений с указанным пользователем",
)
async def get_messages(
    user_id: int,
    limit: int = Query(50, ge=1, le=100, description="Количество сообщений"),
    offset: int = Query(0, ge=0, description="Смещение для пагинации"),
) -> MessagesResponse:
    """Получить историю сообщений с пользователем."""
    if _session_factory is None:
        raise HTTPException(status_code=500, detail="Chat router not initialized")

    async with _session_factory() as session:
        session: AsyncSession

        # Проверяем существование пользователя
        user_query = select(User).where(User.telegram_id == user_id)
        user = await session.scalar(user_query)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Получаем общее количество сообщений
        count_query = select(func.count(Message.id)).where(Message.user_id == user.id)
        total = await session.scalar(count_query) or 0

        # Получаем сообщения
        messages_query = (
            select(Message)
            .where(Message.user_id == user.id)
            .order_by(Message.created_at)
            .limit(limit)
            .offset(offset)
        )

        result = await session.execute(messages_query)
        messages = result.scalars().all()

        message_items = [
            MessageItem(
                id=msg.id,
                text=msg.content,
                role=msg.role,
                timestamp=msg.created_at,
            )
            for msg in messages
        ]

        return MessagesResponse(
            user_id=user_id,
            messages=message_items,
            total=total,
        )


@router.post(
    "/dialogs/{user_id}/messages",
    response_model=SendMessageResponse,
    summary="Отправить сообщение пользователю",
    description="Отправляет сообщение от администратора пользователю через Telegram бота",
)
async def send_message(user_id: int, request: SendMessageRequest) -> SendMessageResponse:
    """Отправить сообщение пользователю (через LLM)."""
    if _session_factory is None or _llm_client is None:
        raise HTTPException(status_code=500, detail="Chat router not initialized")

    async with _session_factory() as session:
        session: AsyncSession

        # Проверяем существование пользователя
        user_query = select(User).where(User.telegram_id == user_id)
        user = await session.scalar(user_query)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Сохраняем сообщение админа как user (НЕ отправляем в Telegram)
        admin_message = Message(
            user_id=user.id,
            role="user",
            content=request.text,
            created_at=datetime.now(),
            content_length=len(request.text),
        )
        session.add(admin_message)
        await session.commit()

        logger.info(
            f"Сообщение админа сохранено для пользователя {user_id}, генерируем ответ через LLM..."
        )

        # Генерируем ответ через LLM
        try:
            from src.context_manager import Message as ContextMessage

            # Получаем историю сообщений для контекста
            history_query = (
                select(Message)
                .where(Message.user_id == user.id)
                .order_by(Message.created_at)
                .limit(_config.max_context_messages)
            )
            history_result = await session.execute(history_query)
            history_messages = history_result.scalars().all()

            # Преобразуем в формат для LLM
            context_messages = []
            for msg in history_messages:
                context_messages.append(ContextMessage(role=msg.role, content=msg.content))

            llm_response = await _llm_client.get_response(context_messages)

            # Сохраняем ответ LLM в БД
            assistant_message = Message(
                user_id=user.id,
                role="assistant",
                content=llm_response,
                created_at=datetime.now(),
                content_length=len(llm_response),
            )
            session.add(assistant_message)
            await session.commit()
            await session.refresh(assistant_message)

            # Отправляем ответ LLM в Telegram
            sent_to_telegram = False
            if _bot is not None:
                try:
                    await _bot.send_message(chat_id=user_id, text=llm_response)
                    sent_to_telegram = True
                    logger.info(f"Ответ LLM отправлен пользователю {user_id} через Telegram")
                except Exception as e:
                    logger.error(f"Ошибка отправки в Telegram для {user_id}: {e}")
            else:
                logger.warning("Telegram Bot недоступен, ответ сохранен только в БД")

            return SendMessageResponse(
                id=assistant_message.id,
                text=assistant_message.content,
                role=assistant_message.role,
                timestamp=assistant_message.created_at,
                sent_to_telegram=sent_to_telegram,
            )

        except Exception as e:
            logger.error(f"Ошибка генерации ответа LLM для {user_id}: {e}")
            raise HTTPException(
                status_code=500, detail=f"Failed to generate LLM response: {str(e)}"
            ) from e
