from aiogram.types import ReplyKeyboardMarkup

from keyboards.admin.adminInterface import AdminInterfaceText
from keyboards.base import build_reply_kb


def get_question_management_kb() -> ReplyKeyboardMarkup:
    return build_reply_kb(
        [
            [AdminInterfaceText.Question.ADD, AdminInterfaceText.Question.REMOVE],
            [AdminInterfaceText.Question.LIST, AdminInterfaceText.Question.EDIT],
            [AdminInterfaceText.Question.BACK],
        ],
        placeholder="Выберите действие с вопросами 👇",
    )
