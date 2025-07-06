from aiogram.types import InlineKeyboardMarkup


class UserTypeButtonText:
    SET_APPLICANT = "applicant"
    SET_PARENT = "parent"
    SET_OTHER = "other"


def choose_user_status() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text="Абитуриент", callback_data=UserTypeButtonText.SET_APPLICANT
            ),
            InlineKeyboardButton(
                text="Родитель", callback_data=UserTypeButtonText.SET_PARENT
            ),
            InlineKeyboardButton(
                text="Иное", callback_data=UserTypeButtonText.SET_OTHER
            ),
        ],
    ]

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
