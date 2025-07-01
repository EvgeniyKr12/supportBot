import asyncio

from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from services import UserService


async def notify_admins(bot, chat_id: int, text: str, db: Session):
    builder = InlineKeyboardBuilder()
    builder.button(text="📌 Взять в работу", callback_data=f"take_dialog_{chat_id}")
    markup = builder.as_markup()

    user_service = UserService(db)

    privileged_users = user_service.get_privileged_users()

    await asyncio.gather(
        *[
            bot.send_message(
                user.tg_id,
                f"🔔 Новый запрос от пользователя {chat_id}:\n\n{text}",
                reply_markup=markup,
            )
            for user in privileged_users
        ]
    )
