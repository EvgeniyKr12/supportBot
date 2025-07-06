from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from models import Direction


async def get_direction_btn_list(
    directions: List[Direction],
    undecided_btn: bool = False,
) -> InlineKeyboardMarkup:
    buttons = []
    for direction in directions:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=direction.name,
                    callback_data=f"direction_info_{direction.name}",
                )
            ]
        )

        if undecided_btn:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text="❌ Не определился", callback_data="direction_UNDECIDED"
                    )
                ]
            )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_direction_keyboard(
    direction_name: str, is_admin: bool = False
) -> InlineKeyboardMarkup:
    if is_admin:
        keyboard = [
            [
                InlineKeyboardButton(
                    text="✏️ Изменить", callback_data=f"direction_edit_{direction_name}"
                ),
                InlineKeyboardButton(
                    text="🗑️ Удалить", callback_data=f"direction_delete_{direction_name}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад к списку", callback_data="direction_back"
                )
            ],
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton(
                    text="✅ Выбрать это направление",
                    callback_data=f"direction_confirm_{direction_name}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад к списку", callback_data="direction_back"
                )
            ],
        ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
