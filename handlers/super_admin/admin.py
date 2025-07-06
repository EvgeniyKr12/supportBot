from typing import Union

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import Session

from data.state import AdminStates
from keyboards.admin.adminInterface import AdminInterfaceText
from keyboards.admin.reply.admin import get_admin_management_kb
from models import UserRole
from services import UserService
from utils.access import check_super_admin_access
from utils.logger import logger

router = Router()


@router.callback_query(F.data == "admin_management")
@router.message(F.text == AdminInterfaceText.AdminMenu.ADMIN_PANEL)
@router.message(Command("admin_management"))
async def admin_panel_handler(update: Union[CallbackQuery, Message], db: Session):
    logger.info("Управление админами")
    if not await check_super_admin_access(update, db):
        return

    message = update.message if isinstance(update, CallbackQuery) else update
    await message.answer(
        "👑 Управление администраторами", reply_markup=get_admin_management_kb()
    )

    if isinstance(update, CallbackQuery):
        await update.answer()


@router.callback_query(F.data == "add_admin")
@router.message(F.text == AdminInterfaceText.Admin.ADD)
@router.message(Command("add_admin"))
async def add_admin_handler(
    update: Union[CallbackQuery, Message], state: FSMContext, db: Session
):
    logger.info("Добавляем админа")
    if not await check_super_admin_access(update, db):
        return

    message = update.message if isinstance(update, CallbackQuery) else update
    await message.answer(
        "Для добавления администратора:\n\n"
        "1. Пользователь должен написать /start боту\n"
        "2. Отправьте сюда его username (@username) или ID"
    )
    await state.set_state(AdminStates.waiting_admin_username)

    if isinstance(update, CallbackQuery):
        await update.answer()


@router.message(AdminStates.waiting_admin_username)
async def save_new_admin(message: Message, state: FSMContext, db: Session):
    input_data = message.text.strip().lstrip("@")
    user_service = UserService(db)

    try:
        user = (
            user_service.get_user_by_username(input_data)
            if not input_data.isdigit()
            else user_service.get_user(int(input_data))
        )

        if not user:
            await message.answer("❌ Пользователь не найден.")
            await state.clear()
            return

        if user.role == UserRole.ADMIN:
            await message.answer("⚠️ Этот пользователь уже администратор.")
            await state.clear()
            return

        user_service.change_role(user.tg_id, UserRole.ADMIN)
        await message.answer(
            f"✅ Пользователь @{user.username or user.tg_id} назначен администратором.",
            reply_markup=get_admin_management_kb(),
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
    finally:
        await state.clear()


@router.callback_query(F.data == "remove_admin")
@router.message(F.text == AdminInterfaceText.Admin.REMOVE)
@router.message(Command("remove_admin"))
async def remove_admin_handler(
    update: Union[CallbackQuery, Message], state: FSMContext, db: Session
):
    logger.info("Удаляем админа")
    if not await check_super_admin_access(update, db):
        return

    user_service = UserService(db)
    message = update.message if isinstance(update, CallbackQuery) else update

    try:
        admins = user_service.get_users_by_role(UserRole.ADMIN)
        if not admins:
            await message.answer("ℹ️ Нет администраторов в системе.")
            return

        admin_list = "\n".join(
            f"👤 @{admin.username or admin.tg_id}" for admin in admins
        )
        await message.answer(
            f"Список администраторов:\n\n{admin_list}\n\n"
            "Отправьте username или ID для удаления:"
        )
        await state.set_state(AdminStates.waiting_admin_removal_username)
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

    if isinstance(update, CallbackQuery):
        await update.answer()


@router.message(AdminStates.waiting_admin_removal_username)
async def remove_admin(message: Message, state: FSMContext, db: Session):
    input_data = message.text.strip().lstrip("@")
    user_service = UserService(db)

    try:
        user = (
            user_service.get_user_by_username(input_data)
            if not input_data.isdigit()
            else user_service.get_user(int(input_data))
        )

        if not user:
            await message.answer("❌ Пользователь не найден.")
            await state.clear()
            return

        if user.role != UserRole.ADMIN:
            await message.answer("⚠️ Этот пользователь не администратор.")
            await state.clear()
            return

        user_service.change_role(user.tg_id, UserRole.USER)
        await message.answer(
            f"✅ Пользователь @{user.username or user.tg_id} понижен до пользователя.",
            reply_markup=get_admin_management_kb(),
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
    finally:
        await state.clear()


@router.callback_query(F.data == "show_admins")
@router.message(F.text == AdminInterfaceText.Admin.LIST)
@router.message(Command("list_admins"))
async def list_admins_handler(update: Union[CallbackQuery, Message], db: Session):
    logger.info("Список админов")
    if not await check_super_admin_access(update, db):
        return

    user_service = UserService(db)
    message = update.message if isinstance(update, CallbackQuery) else update

    try:
        admins = user_service.get_users_by_role(UserRole.ADMIN)
        if not admins:
            await message.answer("ℹ️ Нет администраторов в системе.")
            return

        admin_list = "\n".join(
            f"👑 @{admin.username or admin.tg_id}" for admin in admins
        )
        await message.answer(
            f"Активные администраторы:\n\n{admin_list}",
            reply_markup=get_admin_management_kb(),
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

    if isinstance(update, CallbackQuery):
        await update.answer()
