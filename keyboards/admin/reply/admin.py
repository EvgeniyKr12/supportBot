from aiogram.types import ReplyKeyboardMarkup

from keyboards.admin.adminInterface import AdminInterfaceText
from keyboards.base import build_reply_kb


def get_manager_kb(is_super_admin=False) -> ReplyKeyboardMarkup:
    if is_super_admin:
        rows = [
            [AdminInterfaceText.AdminMenu.CHANGE_GREETING],
            [
                AdminInterfaceText.AdminMenu.OPERATOR_PANEL,
                AdminInterfaceText.AdminMenu.QUESTION_PANEL,
            ],
            [
                AdminInterfaceText.AdminMenu.DIRECTION_PANEL,
                AdminInterfaceText.AdminMenu.ADMIN_PANEL,
            ],
        ]
    else:
        rows = [
            [AdminInterfaceText.AdminMenu.CHANGE_GREETING],
            [AdminInterfaceText.AdminMenu.OPERATOR_PANEL],
            [
                AdminInterfaceText.AdminMenu.QUESTION_PANEL,
                AdminInterfaceText.AdminMenu.DIRECTION_PANEL,
            ],
        ]
    return build_reply_kb(rows, placeholder="Выберите действие 👇")


def get_admin_management_kb():
    return build_reply_kb(
        [
            [AdminInterfaceText.Admin.ADD, AdminInterfaceText.Admin.REMOVE],
            [AdminInterfaceText.Admin.LIST],
            [AdminInterfaceText.Admin.BACK],
        ],
        placeholder="Выберите действие с оператором 👇",
    )
