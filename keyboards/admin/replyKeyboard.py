from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


class ReplyButtonText:
    CHANGE_GREETING = "✏️ Изменить приветствие"
    OPERATOR_PANEL = "👨💼 Управление операторами"
    ADMIN_PANEL = "🛡️ Управление админами"
    QUESTION_PANEL = "❓ Управление вопросами"
    DIRECTION_PANEL = "📊 Управление направлениями"


def get_admin_kb(is_super_admin=False):
    if is_super_admin:
        buttons = [
            [KeyboardButton(text=ReplyButtonText.CHANGE_GREETING)],
            [
                KeyboardButton(text=ReplyButtonText.OPERATOR_PANEL),
                KeyboardButton(text=ReplyButtonText.QUESTION_PANEL),
            ],
            [
                KeyboardButton(text=ReplyButtonText.DIRECTION_PANEL),
                KeyboardButton(text=ReplyButtonText.ADMIN_PANEL),
            ],
        ]
    else:
        buttons = [
            [KeyboardButton(text=ReplyButtonText.CHANGE_GREETING)],
            [KeyboardButton(text=ReplyButtonText.OPERATOR_PANEL)],
            [
                KeyboardButton(text=ReplyButtonText.QUESTION_PANEL),
                KeyboardButton(text=ReplyButtonText.DIRECTION_PANEL),
            ],
        ]

    markup = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие 👇",
    )
    return markup
