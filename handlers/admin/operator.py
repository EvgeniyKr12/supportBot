from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import Session

from data.state import AdminStates
from models import UserRole
from services import UserService
from utils.access import is_admin

router = Router()


@router.callback_query(F.data == "add_operator")
async def add_operator(callback: CallbackQuery, db: Session, state: FSMContext):
    user_service = UserService(db)
    user = user_service.get_user(callback.from_user.id)
    if not is_admin(user):
        await callback.message.answer("❌ У вас нет доступа.")
        await callback.answer()
        return

    await callback.message.answer(
        "Чтобы добавить нового оператора(если они еще не пользовался ботом) - нужно чтобы он написал команду /start, "
        "а после администратор передала сюда"
        "username (@username)."
    )
    await state.set_state(AdminStates.waiting_operator_username)
    await callback.answer()


@router.message(AdminStates.waiting_operator_username)
async def save_new_operator(message: Message, state: FSMContext, db: Session):
    username = message.text.strip().lstrip("@")

    try:
        user_service = UserService(db)
        user = user_service.get_user_by_username(username)
        if not user:
            await message.answer(f"❌ Пользователь @{username} не найден.")
            await state.clear()
            return

        user_service.change_role(user.tg_id, UserRole.OPERATOR)
        await message.answer(
            f"✅ Пользователь @{username} успешно назначен оператором."
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка при назначении оператора: {e}")
    await state.clear()


@router.callback_query(F.data == "remove_operator")
async def ask_operator_to_remove(
    callback: CallbackQuery, state: FSMContext, db: Session
):
    user_service = UserService(db)
    user = user_service.get_user(callback.from_user.id)
    if not is_admin(user):
        await callback.message.answer("❌ У вас нет доступа.")
        await callback.answer()
        return

    try:
        operators = user_service.get_users_by_role(UserRole.OPERATOR)
        if not operators:
            await callback.message.answer("⚠️ Нет пользователей с ролью оператора.")
            await callback.answer()
            return

        operator_list = "\n".join(
            [f"@{op.username or '—'} (ID: {op.tg_id})" for op in operators]
        )
        await callback.message.answer(
            f"👮‍♂️ Операторы:\n\n{operator_list}\n\n"
            "Введите username или tg_id оператора, которого хотите понизить до пользователя:"
        )
        await state.set_state(AdminStates.waiting_operator_removal_username)
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при получении списка операторов: {e}")
    await callback.answer()


@router.message(AdminStates.waiting_operator_removal_username)
async def remove_operator(message: Message, state: FSMContext, db: Session):
    input_value = message.text.strip().lstrip("@")
    user_service = UserService(db)

    try:
        if input_value.isdigit():
            user = user_service.get_user(int(input_value))
        else:
            user = user_service.get_user_by_username(input_value)

        if not user:
            await message.answer("❌ Пользователь не найден.")
            await state.clear()
            return

        if user.role != "operator":
            await message.answer(
                f"⚠️ Пользователь @{user.username or user.tg_id} не является оператором."
            )
            await state.clear()
            return

        user_service.change_role(user.tg_id, UserRole.USER)
        await message.answer(
            f"✅ Пользователь @{user.username or user.tg_id} понижен до пользователя."
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка при понижении: {e}")
    await state.clear()


@router.callback_query(F.data == "show_operators")
async def get_operators(callback: CallbackQuery, db: Session):
    user_service = UserService(db)
    user = user_service.get_user(callback.from_user.id)
    if not is_admin(user):
        await callback.message.answer("❌ У вас нет доступа.")
        await callback.answer()
        return

    try:
        operators = user_service.get_users_by_role(UserRole.OPERATOR)
        if not operators:
            await callback.message.answer("⚠️ Нет пользователей с ролью оператора.")
        else:
            operator_list = "\n".join(
                [f"@{op.username or '—'} (ID: {op.tg_id})" for op in operators]
            )
            await callback.message.answer(f"👮‍♂️ Операторы:\n\n{operator_list}")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")
    await callback.answer()
