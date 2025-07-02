from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.orm import Session

from handlers.admin.direction import list_directions_handler
from keyboards.user.inlineKeyboard import choose_user_status
from keyboards.user.replyKeyboard import ReplyButtonText
from services import UserService
from utils.logger import logger

router = Router()


@router.callback_query(F.data == "about_university")
@router.message(F.text == ReplyButtonText.ABOUT_UNIVERSITY)
@router.message(Command("about_university"))
async def about_university_handler(message: Message):
    logger.info("Пользователь запрашивает информацию о университете")
    await message.answer(
        "🏫 ИСТ «Т-университет» — это инновационная образовательная платформа..."
    )


@router.callback_query(F.data == "show_programs")
@router.message(F.text == ReplyButtonText.EDUCATIONAL_PROGRAMS)
@router.message(Command('show_programs'))
async def educational_programs_handler(message: Message, db: Session):
    logger.info("Пользователь запрашивает информацию о направлениях")
    await list_directions_handler(message, db, False)


@router.message(F.text == ReplyButtonText.CONNECTION)
@router.message(Command(ReplyButtonText.CONNECTION))
async def connection_handler(message: Message):
    logger.info("Пользователь запрашивает информацию о контактах")
    await message.answer(
        "📞 Контакты:\nТелефон: +7 (123) 456-78-90\nEmail: info@t-university.ru"
    )


@router.message(F.text == ReplyButtonText.ASK_QUESTION)
@router.message(Command(ReplyButtonText.ASK_QUESTION))
async def ask_question_handler(message: Message, db: Session):
    logger.info("Пользователь запрашивает информацию о том как задать вопрос")
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
