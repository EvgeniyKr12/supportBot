from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


class ReplyButtonText:
    ABOUT_UNIVERSITY = "🏫 Что такое ИСТ «Т-университет»?"
    EDUCATIONAL_PROGRAMS = "📚 Программы обучения"
    CONNECTION = "📞 Контакты"
    ASK_QUESTION = "💬 Задать вопрос"
    ABOUT = "👨‍🎓 О вас"


def get_user_kb():
    buttons = [
        [KeyboardButton(text=ReplyButtonText.ABOUT_UNIVERSITY)],
        [KeyboardButton(text=ReplyButtonText.EDUCATIONAL_PROGRAMS)],
        [KeyboardButton(text=ReplyButtonText.CONNECTION)],
        [KeyboardButton(text=ReplyButtonText.ASK_QUESTION)],
        [KeyboardButton(text=ReplyButtonText.ABOUT)],
    ]

    markup = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder="Выберите интересующий раздел 👇",
    )
    return markup
