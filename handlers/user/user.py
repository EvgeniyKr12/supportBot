from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import Session

from handlers.admin.direction import list_directions_handler
from keyboards.admin.inline.inline import get_about_user_inline_kb
from keyboards.user.replyKeyboard import ReplyButtonText
from models import UserType
from services import DirectionService, UserService
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

    await message.answer("💬 Напишите ваш вопрос в чат, и мы ответим как можно скорее.")


@router.message(F.text == "👨‍🎓 О вас")
async def about_user_handler(message: Message, db: Session):
    user_service = UserService(db)
    direction_service = DirectionService(db)

    user = user_service.get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Пользователь не найден.")
        return

    # Тип пользователя
    type_map = {
        UserType.APPLICANT: "Абитуриент",
        UserType.PARENT: "Родитель",
        UserType.OTHER: "Иное",
    }
    user_type_str = type_map.get(user.type, "Не выбран")

    # Направление
    direction = (
        direction_service.get_direction_by_id(user.direction_id)
        if user.direction_id
        else None
    )
    direction_str = direction.name if direction else "Не выбрано"

    text = (
        f"🧾 <b>Информация о вас:</b>\n\n"
        f"Никнейм: {user.username}\n"
        f"👤 Тип: <b>{user_type_str}</b>\n"
        f"🎯 Направление: <b>{direction_str}</b>"
    )

    await message.answer(
        text, reply_markup=get_about_user_inline_kb(), parse_mode="HTML"
    )


@router.callback_query(F.data == "change_type")
async def change_type(callback: CallbackQuery):
    from aiogram.utils.keyboard import InlineKeyboardBuilder

    from keyboards.user.inlineKeyboard import InlineButtonText

    builder = InlineKeyboardBuilder()
    builder.button(text="🎓 Абитуриент", callback_data=InlineButtonText.SET_APPLICANT)
    builder.button(text="👨‍👩‍👧 Родитель", callback_data=InlineButtonText.SET_PARENT)
    builder.button(text="❓ Другое", callback_data=InlineButtonText.SET_OTHER)
    builder.adjust(1)

    await callback.message.edit_text(
        "Пожалуйста, выберите, кто вы:", reply_markup=builder.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data == "change_direction")
async def change_direction(callback: CallbackQuery, db: Session):
    from keyboards.user.inlineKeyboard import choose_direction

    await callback.message.edit_text(
        "Пожалуйста, выберите направление:", reply_markup=await choose_direction(db)
    )
    await callback.answer()
