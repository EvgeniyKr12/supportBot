from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from keyboards.user.userInterface import UserInterfaceText


def get_user_kb():
    buttons = [
        [KeyboardButton(text=UserInterfaceText.ABOUT_UNIVERSITY)],
        [KeyboardButton(text=UserInterfaceText.EDUCATIONAL_PROGRAMS)],
        [KeyboardButton(text=UserInterfaceText.CONNECTION)],
        [KeyboardButton(text=UserInterfaceText.ASK_QUESTION)],
        [KeyboardButton(text=UserInterfaceText.PROFILE)],
    ]

    markup = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Выберите интересующий раздел 👇",
    )
    return markup
