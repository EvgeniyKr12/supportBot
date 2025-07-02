from typing import Union

from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import Session

from models import UserRole
from services import UserService


def is_admin(user):
    return user and user.role in (UserRole.ADMIN, UserRole.SUPER_ADMIN)


async def check_super_admin_access(update: Union[CallbackQuery, Message], db: Session):
    """Проверка прав супер-администратора"""
    user_service = UserService(db)
    user = user_service.get_user(update.from_user.id)
    if not (user and user.role == UserRole.SUPER_ADMIN):
        if isinstance(update, CallbackQuery):
            await update.answer("❌ Только для супер-администратора")
            await update.message.answer("❌ У вас нет доступа.")
        else:
            await update.answer("❌ У вас нет доступа.")
        return False
    return True


async def check_admin_access(update: Union[CallbackQuery, Message], db: Session):
    """Проверка прав администратора"""
    user_service = UserService(db)
    user = user_service.get_user(update.from_user.id)
    if not is_admin(user):
        if isinstance(update, CallbackQuery):
            await update.answer("❌ У вас нет доступа.")
            await update.message.answer("❌ У вас нет доступа.")
        else:
            await update.answer("❌ У вас нет доступа.")
        return False
    return True
