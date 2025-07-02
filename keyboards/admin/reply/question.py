from aiogram.types import ReplyKeyboardMarkup

from keyboards.admin.base import build_reply_kb
from keyboards.admin.text import ButtonText


def get_question_management_kb() -> ReplyKeyboardMarkup:
    return build_reply_kb(
        [
            [ButtonText.Question.ADD, ButtonText.Question.REMOVE],
            [ButtonText.Question.LIST],
            [ButtonText.Question.BACK],
        ],
        placeholder="Выберите действие с вопросами 👇",
    )
