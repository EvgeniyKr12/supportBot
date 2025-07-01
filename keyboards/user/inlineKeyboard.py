from aiogram.types import InlineKeyboardMarkup
from sqlalchemy.orm.session import Session

from services.direction_serivce import DirectionService


class InlineButtonText:
    SET_APPLICANT = "applicant"
    SET_PARENT = "parent"
    SET_OTHER = "other"


def choose_user_status() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Абитуриент", callback_data=InlineButtonText.SET_APPLICANT
            ),
            InlineKeyboardButton(
                text="Родитель", callback_data=InlineButtonText.SET_PARENT
            ),
            InlineKeyboardButton(text="Иное", callback_data=InlineButtonText.SET_OTHER),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def choose_direction(db: Session):
    direction_service = DirectionService(db)

    directions = direction_service.get_all_directions()

    buttons = []
    for direction in directions:
        buttons.append(
            [
                InlineKeyboardButton(
                    text=direction.name,
                    callback_data=f"direction_info_{direction.code}",
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                text="❌ Не определился", callback_data="direction_UNDECIDED"
            )
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def confirm_direction_keyboard(direction_code: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Выбрать это направление",
                    callback_data=f"direction_confirm_{direction_code}",
                ),
                InlineKeyboardButton(
                    text="🔙 Назад к списку", callback_data="direction_back"
                ),
            ]
        ]
    )
