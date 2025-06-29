from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class InlineButtonText:
    CHANGE_START_TEXT = "📝 Изменить приветствие"
    SHOW_OPERATORS = "📋 Показать операторов"
    ADD_OPERATOR = "➕ Добавить оператора"
    REMOVE_OPERATOR = "➖ Удалить оператора"
    SHOW_ADMINS = "📋 Показать администраторов"
    ADD_ADMIN = "➕ Добавить администратора"
    REMOVE_ADMIN = "➖ Удалить администратора"
    SHOW_QUESTIONS = "❓ Показать вопросы"
    ADD_QUESTION = "➕ Добавить вопрос"
    REMOVE_QUESTION = "➖ Удалить вопрос"


def get_options_keyboard(is_super_admin: bool = False) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(
                text=InlineButtonText.CHANGE_START_TEXT,
                callback_data="change_greeting",
            ),
        ],
        [
            InlineKeyboardButton(
                text=InlineButtonText.SHOW_OPERATORS,
                callback_data="show_operators",
            )
        ],
        [
            InlineKeyboardButton(
                text=InlineButtonText.ADD_OPERATOR,
                callback_data="add_operator",
            ),
        ],
        [
            InlineKeyboardButton(
                text=InlineButtonText.REMOVE_OPERATOR,
                callback_data="remove_operator",
            ),
        ],
        # Кнопки для работы с вопросами
        [
            InlineKeyboardButton(
                text=InlineButtonText.SHOW_QUESTIONS,
                callback_data="show_questions",
            ),
        ],
        [
            InlineKeyboardButton(
                text=InlineButtonText.ADD_QUESTION,
                callback_data="add_question",
            ),
        ],
        [
            InlineKeyboardButton(
                text=InlineButtonText.REMOVE_QUESTION,
                callback_data="remove_question",
            ),
        ],
    ]

    if is_super_admin:
        keyboard.extend(
            [
                [
                    InlineKeyboardButton(
                        text=InlineButtonText.SHOW_ADMINS,
                        callback_data="show_admins",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text=InlineButtonText.ADD_ADMIN,
                        callback_data="add_admin",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=InlineButtonText.REMOVE_ADMIN,
                        callback_data="remove_admin",
                    ),
                ],
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
