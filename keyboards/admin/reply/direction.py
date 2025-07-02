from keyboards.admin.base import build_reply_kb
from keyboards.admin.text import ButtonText
from aiogram.types import ReplyKeyboardMarkup

def get_direction_management_kb() -> ReplyKeyboardMarkup:
    return build_reply_kb(
        [
            [ButtonText.Direction.ADD, ButtonText.Direction.REMOVE],
            [ButtonText.Direction.LIST],
            [ButtonText.Direction.BACK],
        ],
        placeholder="Выберите действие 👇",
    )