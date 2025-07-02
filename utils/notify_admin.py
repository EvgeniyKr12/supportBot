import asyncio
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from models import UserType
from services import UserService, DirectionService


async def notify_admins(bot, chat_id: int, text: str, db: Session):
    builder = InlineKeyboardBuilder()
    builder.button(text="📌 Взять в работу", callback_data=f"take_dialog_{chat_id}")
    markup = builder.as_markup()

    user_service = UserService(db)
    direction_service = DirectionService(db)

    user = user_service.get_user(chat_id)
    privileged_users = user_service.get_privileged_users()

    if not user:
        return

    direction = direction_service.get_direction_by_id(user.direction_id) if user.direction_id else None

    if user.type == UserType.PARENT:
        user_type_text = "Родитель"

    if user.type == UserType.APPLICANT:
        user_type_text = "Абитуриент"

    if user.type == UserType.OTHER:
        user_type_text = "Другое"


    # Формируем текст с информацией о пользователе
    user_info = (
        f"🔔 Новый запрос от пользователя:\n"
        f"🆔 ID: {user.tg_id}\n"
        f"👤 Username: @{user.username or '—'}\n"
        f"🎯 Тип: {user_type_text if user.type else 'Не выбран'}\n"
        f"📘 Направление: {direction.name if direction else 'Не выбрано'}\n\n"
        f"💬 Вопрос: {text}"
    )

    await asyncio.gather(
        *[
            bot.send_message(
                admin.tg_id,
                user_info,
                reply_markup=markup,
            )
            for admin in privileged_users
        ]
    )
