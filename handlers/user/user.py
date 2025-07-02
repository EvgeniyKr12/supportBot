from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.orm import Session

from keyboards.user.inlineKeyboard import choose_user_status
from keyboards.user.replyKeyboard import ReplyButtonText
from services import UserService

router = Router()


@router.callback_query(F.data == "about_university")
@router.message(F.text == ReplyButtonText.ABOUT_UNIVERSITY)
@router.message(Command("about_university"))
async def about_university_handler(message: Message):
    await message.answer(
        "🏫 ИСТ «Т-университет» — это инновационная образовательная платформа..."
    )


@router.callback_query(F.data == "show_programs")
@router.message(F.text == ReplyButtonText.EDUCATIONAL_PROGRAMS)
@router.message(Command('show_programs'))
async def educational_programs_handler(message: Message):
    await message.answer(
        "📚 Программы обучения:\n- Программа 1\n- Программа 2\n- Программа 3"
    )


@router.message(F.text == ReplyButtonText.CONNECTION)
@router.message(Command(ReplyButtonText.CONNECTION))
async def connection_handler(message: Message):
    await message.answer(
        "📞 Контакты:\nТелефон: +7 (123) 456-78-90\nEmail: info@t-university.ru"
    )


@router.message(F.text == ReplyButtonText.ASK_QUESTION)
@router.message(Command(ReplyButtonText.ASK_QUESTION))
async def ask_question_handler(message: Message, db: Session):
    user_service = UserService(db)
    user = user_service.get_user(message.from_user.id)

    if not user or not user.type:
        await message.answer(
            "Для полноценного использования бота ответьте на вопросы.\n\n"
            "Укажите, кем вы являетесь:",
            reply_markup=choose_user_status(),
        )
        return

    await message.answer("💬 Напишите ваш вопрос, и мы ответим как можно скорее.")
