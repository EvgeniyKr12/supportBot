from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session

from keyboards.admin.inline.direction import get_direction_btn_list
from keyboards.admin.inline.profile import get_about_user_inline_kb
from keyboards.user.inline.user_type import UserTypeButtonText
from keyboards.user.userInterface import UserInterfaceText
from models import UserType
from services import DirectionService, UserService
from utils.logger import logger

router = Router()


@router.message(F.text == UserInterfaceText.ABOUT_UNIVERSITY)
async def about_university_handler(message: Message):
    logger.info("Пользователь запрашивает информацию о университете")
    await message.answer(
        "🏫 <b>ИСТ «Т-университет»</b> — это инновационная образовательная платформа, "
        "где студенты получают современные знания и навыки, востребованные в реальном мире.",
        parse_mode="HTML",
    )


@router.message(F.text == UserInterfaceText.EDUCATIONAL_PROGRAMS)
async def educational_programs_handler(message: Message, db: Session):
    logger.info("Пользователь запрашивает информацию о направлениях")
    direction_service = DirectionService(db)
    directions = direction_service.get_all_directions()

    if len(directions) == 0:
        await message.answer(
            text="📚 <b>Список образовательных программ пуст</b>",
            parse_mode="HTML",
        )
    else:
        await message.answer(
            text="📚 <b>Список образовательных программ</b>",
            reply_markup=await get_direction_btn_list(directions),
            parse_mode="HTML",
        )


@router.message(F.text == UserInterfaceText.CONNECTION)
async def connection_handler(message: Message):
    logger.info("Пользователь запрашивает информацию о контактах")
    await message.answer(
        "📞 <b>Контакты:</b>\n"
        "📱 Телефон: +7 (123) 456-78-90\n"
        "✉️ Email: info@t-university.ru",
        parse_mode="HTML",
    )


@router.message(F.text == UserInterfaceText.ASK_QUESTION)
async def ask_question_handler(message: Message):
    logger.info("Пользователь запрашивает информацию о том как задать вопрос")
    await message.answer(
        "💬 <b>Напишите ваш вопрос в чат</b>, и наша команда ответит вам как можно скорее!",
        parse_mode="HTML",
    )


@router.message(F.text == UserInterfaceText.PROFILE)
async def about_user_handler(message: Message, db: Session):
    logger.info("Пользователь запрашивает профиль")
    user_service = UserService(db)
    direction_service = DirectionService(db)

    user = user_service.get_user(message.from_user.id)
    if not user:
        await message.answer("❌ Пользователь не найден.")
        return

    type_map = {
        UserType.APPLICANT: "Абитуриент 🎓",
        UserType.PARENT: "Родитель 👨‍👩‍👧",
        UserType.OTHER: "Иное ❓",
    }
    user_type_str = type_map.get(user.type, "Не выбран")

    direction = (
        direction_service.get_direction_by_id(user.direction_id)
        if user.direction_id
        else None
    )
    direction_str = direction.name if direction else "Не выбрано"

    text = (
        f"🧾 <b>Информация о вас:</b>\n\n"
        f"👤 Никнейм: <b>{user.username}</b>\n"
        f"🎓 Тип: <b>{user_type_str}</b>\n"
        f"🎯 Направление: <b>{direction_str}</b>"
    )

    await message.answer(
        text, reply_markup=get_about_user_inline_kb(), parse_mode="HTML"
    )


@router.callback_query(F.data == "change_type")
async def change_type(callback: CallbackQuery):
    logger.info(f"Пользователь {callback.from_user.id} хочет изменить свой тип")
    builder = InlineKeyboardBuilder()
    builder.button(text="🎓 Абитуриент", callback_data=UserTypeButtonText.SET_APPLICANT)
    builder.button(text="👨‍👩‍👧 Родитель", callback_data=UserTypeButtonText.SET_PARENT)
    builder.button(text="❓ Другое", callback_data=UserTypeButtonText.SET_OTHER)
    builder.adjust(1)

    await callback.message.edit_text(
        text="🔁 Пожалуйста, выберите, кто вы:",
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "change_direction")
async def change_direction(callback: CallbackQuery, db: Session):
    logger.info(f"Пользователь {callback.from_user.id} хочет изменить свое направление")
    direction_service = DirectionService(db)
    directions = direction_service.get_all_directions()

    if len(directions) == 0:
        await callback.answer(
            text="📚 <b>Список образовательных программ пуст</b>",
            parse_mode="HTML",
        )
    else:
        await callback.message.edit_text(
            "📌 Пожалуйста, выберите ваше направление:",
            reply_markup=await get_direction_btn_list(
                directions=directions, undecided_btn=True
            ),
            parse_mode="HTML",
        )
    await callback.answer()
