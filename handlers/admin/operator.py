from typing import Union

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import Session

from data.state import AdminStates
from keyboards.admin.adminInterface import AdminInterfaceText
from keyboards.admin.reply.operator import get_operator_management_kb
from models import UserRole
from services import UserService
from utils.access import check_admin_access
from utils.logger import logger

router = Router()


@router.callback_query(F.data == "operator_management")
@router.message(F.text == AdminInterfaceText.AdminMenu.OPERATOR_PANEL)
@router.message(Command("operators"))
async def operator_panel_handler(update: Union[CallbackQuery, Message], db: Session):
    logger.info("Управление операторами")
    if not await check_admin_access(update, db):
        return

    message = update.message if isinstance(update, CallbackQuery) else update
    await message.answer(
        "Управление операторами", reply_markup=get_operator_management_kb()
    )

    if isinstance(update, CallbackQuery):
        await update.answer()


@router.callback_query(F.data == "add_operator")
@router.message(F.text == AdminInterfaceText.Operator.ADD)
@router.message(Command("add_operator"))
async def add_operator_handler(
    update: Union[CallbackQuery, Message], db: Session, state: FSMContext
):
    logger.info("Добавление оператора")
    if not await check_admin_access(update, db):
        return

    message = update.message if isinstance(update, CallbackQuery) else update
    await message.answer(
        "Чтобы добавить оператора:\n\n"
        "1. Пользователь должен написать /start боту\n"
        "2. Отправьте сюда его username (@username) или ID"
    )
    await state.set_state(AdminStates.waiting_operator_username)

    if isinstance(update, CallbackQuery):
        await update.answer()


@router.callback_query(F.data == "remove_operator")
@router.message(F.text == AdminInterfaceText.Operator.REMOVE)
@router.message(Command("remove_operator"))
async def remove_operator_handler(
    update: Union[CallbackQuery, Message], db: Session, state: FSMContext
):
    logger.info("Удаление оператора")
    if not await check_admin_access(update, db):
        return

    user_service = UserService(db)
    message = update.message if isinstance(update, CallbackQuery) else update

    try:
        operators = user_service.get_users_by_role(UserRole.OPERATOR)
        if not operators:
            await message.answer("ℹ️ Нет операторов в системе.")
            return

        operator_list = "\n".join(f"👤 @{op.username or op.tg_id}" for op in operators)
        await message.answer(
            f"Список операторов:\n\n{operator_list}\n\n"
            "Отправьте username или ID для удаления:"
        )
        await state.set_state(AdminStates.waiting_operator_removal_username)

    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

    if isinstance(update, CallbackQuery):
        await update.answer()


@router.message(AdminStates.waiting_operator_username)
async def save_new_operator(message: Message, state: FSMContext, db: Session):
    input_data = message.text.strip().lstrip("@")
    user_service = UserService(db)

    try:
        # Пробуем найти по username или ID
        user = (
            user_service.get_user_by_username(input_data)
            if not input_data.isdigit()
            else user_service.get_user(int(input_data))
        )

        if not user:
            await message.answer("❌ Пользователь не найден.")
            await state.clear()
            return

        user_service.change_role(user.tg_id, UserRole.OPERATOR)
        await message.answer(
            f"✅ Пользователь @{user.username or user.tg_id} назначен оператором.",
            reply_markup=get_operator_management_kb(),
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
    finally:
        await state.clear()


@router.message(AdminStates.waiting_operator_removal_username)
async def remove_operator(message: Message, state: FSMContext, db: Session):
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

        if user.role != UserRole.OPERATOR:
            await message.answer("⚠️ Этот пользователь не оператор.")
            await state.clear()
            return

        user_service.change_role(user.tg_id, UserRole.USER)
        await message.answer(
            f"✅ Пользователь @{user.username or user.tg_id} понижен до пользователя.",
            reply_markup=get_operator_management_kb(),
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")
    finally:
        await state.clear()


@router.callback_query(F.data == "show_operators")
@router.message(F.text == AdminInterfaceText.Operator.LIST)
@router.message(Command("list_operators"))
async def list_operators_handler(update: Union[CallbackQuery, Message], db: Session):
    logger.info("Список операторов")
    if not await check_admin_access(update, db):
        return

    user_service = UserService(db)
    message = update.message if isinstance(update, CallbackQuery) else update

    try:
        operators = user_service.get_users_by_role(UserRole.OPERATOR)
        if not operators:
            await message.answer("ℹ️ Нет операторов в системе.")
            return

        operator_list = "\n".join(f"👤 @{op.username or op.tg_id}" for op in operators)
        await message.answer(
            f"Активные операторы:\n\n{operator_list}",
            reply_markup=get_operator_management_kb(),
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

    if isinstance(update, CallbackQuery):
        await update.answer()
