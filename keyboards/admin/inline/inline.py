from aiogram.types import InlineKeyboardMarkup

from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.admin.base import build_list_inline_kb


def get_operators_list_kb(operators: list) -> InlineKeyboardMarkup:
    return build_list_inline_kb(
        items=operators,
        label_getter=lambda o: f"@{o.username}" if o.username else f"ID: {o.tg_id}",
        callback_prefix="remove_operator",
        back_callback="operator_management_back",
    )


def get_directions_list_kb(directions: list, action="show") -> InlineKeyboardMarkup:
    return build_list_inline_kb(
        items=directions,
        label_getter=lambda d: f"{d.name} ({d.code})",
        callback_prefix=f"{action}_direction",
        back_callback="direction_management",
    )

def get_about_user_inline_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Изменить тип", callback_data="change_type")
    builder.button(text="✏️ Изменить направление", callback_data="change_direction")
    builder.adjust(1)
    return builder.as_markup()
