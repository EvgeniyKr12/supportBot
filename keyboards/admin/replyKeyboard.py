from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


class ReplyButtonText:
    ADMIN_PANEL = "🎛️ Административная панель"


def get_on_start_kb():
    send_image_btn = KeyboardButton(text=ReplyButtonText.ADMIN_PANEL)
    first_row = [send_image_btn]
    markup = ReplyKeyboardMarkup(
        keyboard=[first_row],
        resize_keyboard=True,
    )

    return markup
