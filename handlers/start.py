from typing import Union

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import Session

from config.constants import load_greeting_text
from keyboards.admin.reply.admin import get_manager_kb
from keyboards.admin.text import ButtonText
from keyboards.user.replyKeyboard import get_user_kb
from models import UserRole
from services.user_service import UserService
from utils.access import check_admin_access
from utils.logger import logger

router = Router()


@router.message(CommandStart())
async def start(message: Message, db: Session):
    logger.info("Бот запущен")
    user_service = UserService(db)
    user = user_service.get_user(message.from_user.id)

    if user is None:
        user = user_service.create_user(
            message.from_user.id, message.from_user.username
        )

    if user.role != UserRole.USER:
        if user.role == UserRole.ADMIN:
            await message.answer(
                "Добро пожаловать, вы админ", reply_markup=get_manager_kb(False)
            )
        elif user.role == UserRole.SUPER_ADMIN:
            await message.answer(
                text="Добро пожаловать, вы супер-админ",
                reply_markup=get_manager_kb(True),
            )
        elif user.role == UserRole.OPERATOR:
            await message.answer(text="Добро пожаловать, вы оператор. Ожидайте вопрос")
        return
    await message.answer(load_greeting_text(), reply_markup=get_user_kb())


@router.callback_query(F.data == "back")
@router.message(F.text == ButtonText.Operator.BACK)
@router.message(F.text == ButtonText.Admin.BACK)
async def back_handler(update: Union[CallbackQuery, Message], db: Session):
    logger.info("Возврат назад")
    if not await check_admin_access(update, db):
        return

    user_service = UserService(db)
    user = user_service.get_user(update.from_user.id)
    message = update.message if isinstance(update, CallbackQuery) else update

    await message.answer(
        "Главное меню", reply_markup=get_manager_kb(user.role == UserRole.SUPER_ADMIN)
    )

    if isinstance(update, CallbackQuery):
        await update.answer()
