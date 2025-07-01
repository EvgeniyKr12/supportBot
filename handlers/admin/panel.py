from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.orm import Session
from keyboards.admin.inlineKeyboard import get_options_keyboard
from keyboards.admin.replyKeyboard import ReplyButtonText
from models import UserRole
from services import UserService
from utils.access import is_admin


router = Router()

@router.message(Command(ReplyButtonText.ADMIN_PANEL))
@router.message(F.text == ReplyButtonText.ADMIN_PANEL)
async def show_admin_panel(message: Message, db: Session):
    user_service = UserService(db)
    user = user_service.get_user(message.from_user.id)

    if not user or not is_admin(user):
        await message.answer("❌ У вас нет доступа.")
        return

    await message.answer(
        text="Выберите опцию",
        reply_markup=get_options_keyboard(user.role == UserRole.SUPER_ADMIN),
    )
