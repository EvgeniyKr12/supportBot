from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_about_user_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Изменить тип", callback_data="change_type")
    builder.button(text="✏️ Изменить направление", callback_data="change_direction")
    builder.adjust(1)
    return builder.as_markup()
