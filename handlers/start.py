from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.orm import Session

from config.constants import load_greeting_text
from keyboards.admin.replyKeyboard import get_admin_kb
from keyboards.user.replyKeyboard import get_user_kb
from models import User, UserRole
from services.user_service import UserService

router = Router()


@router.message(CommandStart())
async def start(message: Message, db: Session):
    user_service = UserService(db)
    user = user_service.get_user(message.from_user.id)

    if user is None:
        new_user = User(
            tg_id=message.from_user.id,
            username=message.from_user.username,
            role=UserRole.USER,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user = new_user

    if user.role != UserRole.USER:
        if user.role == UserRole.ADMIN:
            await message.answer(
                "Добро пожаловать, вы админ",
                reply_markup=get_admin_kb()
            )
        elif user.role == UserRole.SUPER_ADMIN:
            await message.answer(
                text="Добро пожаловать, вы супер-админ",
                reply_markup=get_admin_kb(True)
            )
        elif user.role == UserRole.OPERATOR:
            await message.answer(
                text="Добро пожаловать, вы оператор. Ожидайте вопрос"
            )
        return
    await message.answer(load_greeting_text(), reply_markup=get_user_kb())