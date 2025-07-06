from aiogram.types import ReplyKeyboardMarkup

from keyboards.admin.adminInterface import AdminInterfaceText
from keyboards.base import build_reply_kb


def get_direction_management_kb() -> ReplyKeyboardMarkup:
    return build_reply_kb(
        [
            [AdminInterfaceText.Direction.ADD, AdminInterfaceText.Direction.REMOVE],
            [AdminInterfaceText.Direction.LIST],
            [AdminInterfaceText.Direction.BACK],
        ],
        placeholder="Выберите действие 👇",
    )
