from aiogram.types import ReplyKeyboardMarkup

from keyboards.admin.base import build_reply_kb
from keyboards.admin.text import ButtonText


def get_manager_kb(is_super_admin=False) -> ReplyKeyboardMarkup:
    if is_super_admin:
        rows = [
            [ButtonText.AdminMenu.CHANGE_GREETING],
            [ButtonText.AdminMenu.OPERATOR_PANEL, ButtonText.AdminMenu.QUESTION_PANEL],
            [ButtonText.AdminMenu.DIRECTION_PANEL, ButtonText.AdminMenu.ADMIN_PANEL],
        ]
    else:
        rows = [
            [ButtonText.AdminMenu.CHANGE_GREETING],
            [ButtonText.AdminMenu.OPERATOR_PANEL],
            [ButtonText.AdminMenu.QUESTION_PANEL, ButtonText.AdminMenu.DIRECTION_PANEL],
        ]
    return build_reply_kb(rows, placeholder="Выберите действие 👇")


def get_admin_management_kb():
    return build_reply_kb(
        [
            [ButtonText.Admin.ADD, ButtonText.Admin.REMOVE],
            [ButtonText.Admin.LIST],
            [ButtonText.Admin.BACK],
        ],
        placeholder="Выберите действие с оператором 👇",
    )
