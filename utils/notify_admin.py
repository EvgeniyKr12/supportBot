from config.constants import ADMIN_IDS
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def notify_admins(bot, chat_id: int, text: str):
    builder = InlineKeyboardBuilder()
    builder.button(text="📌 Взять в работу", callback_data=f"take_dialog_{chat_id}")

    for admin_id in ADMIN_IDS:
        await bot.send_message(
            admin_id,
            f"🔔 Новый запрос от пользователя {chat_id}:\n\n{text}",
            reply_markup=builder.as_markup()
        )
