from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import Session
from data.state import AdminStates
from services.user import (
    get_user_by_username,
    change_user_role,
    get_users_with_role,
    get_user_by_tg_id,
)

router = Router()


def is_admin(user):
    return user and user.role == "super-admin"

@router.callback_query(F.data == "add_admin")
async def add_admin(callback: CallbackQuery, state: FSMContext, db: Session):
    user = await get_user_by_tg_id(callback.from_user.id, db)
    if not is_admin(user):
        await callback.message.answer("❌ У вас нет доступа.")
        await callback.answer()
        return

    await callback.message.answer("Введите username или tg_id пользователя, чтобы назначить его администратором:")
    await state.set_state(AdminStates.waiting_admin_username)
    await callback.answer()


@router.message(AdminStates.waiting_admin_username)
async def save_new_admin(message: Message, state: FSMContext, db: Session):
    input_value = message.text.strip().lstrip("@")

    try:
        if input_value.isdigit():
            user = await get_user_by_tg_id(int(input_value), db)
        else:
            user = await get_user_by_username(input_value, db)

        if not user:
            await message.answer("❌ Пользователь не найден.")
            await state.clear()
            return

        if user.role == "admin":
            await message.answer("⚠️ Этот пользователь уже является администратором.")
            await state.clear()
            return

        await change_user_role(user.tg_id, "admin", db)
        await message.answer(f"✅ Пользователь @{user.username or user.tg_id} теперь администратор.")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    await state.clear()


@router.callback_query(F.data == "remove_admin")
async def ask_admin_to_remove(callback: CallbackQuery, state: FSMContext, db: Session):
    user = await get_user_by_tg_id(callback.from_user.id, db)
    if not is_admin(user):
        await callback.message.answer("❌ У вас нет доступа.")
        await callback.answer()
        return

    try:
        admins = await get_users_with_role("admin", db)
        if not admins:
            await callback.message.answer("⚠️ Нет пользователей с ролью администратора.")
            await callback.answer()
            return

        admin_list = "\n".join(
            [f"@{admin.username or '—'} (ID: {admin.tg_id})" for admin in admins]
        )
        await callback.message.answer(
            f"👑 Администраторы:\n\n{admin_list}\n\n"
            "Введите username (без @) или tg_id администратора, которого хотите понизить до пользователя:"
        )
        await state.set_state(AdminStates.waiting_admin_removal_username)
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при получении списка администраторов: {e}")
    await callback.answer()


@router.message(AdminStates.waiting_admin_removal_username)
async def remove_admin(message: Message, state: FSMContext, db: Session):
    input_value = message.text.strip().lstrip("@")

    try:
        if input_value.isdigit():
            user = await get_user_by_tg_id(int(input_value), db)
        else:
            user = await get_user_by_username(input_value, db)

        if not user:
            await message.answer("❌ Пользователь не найден.")
            await state.clear()
            return

        if user.role != "admin":
            await message.answer("⚠️ Этот пользователь не является администратором.")
            await state.clear()
            return

        await change_user_role(user.tg_id, "user", db)
        await message.answer(f"✅ Пользователь @{user.username or user.tg_id} понижен до пользователя.")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    await state.clear()


@router.callback_query(F.data == "show_admins")
async def get_admins(callback: CallbackQuery, db: Session):
    user = await get_user_by_tg_id(callback.from_user.id, db)
    if not is_admin(user):
        await callback.message.answer("❌ У вас нет доступа.")
        await callback.answer()
        return

    try:
        admins = await get_users_with_role("admin", db)
        if not admins:
            await callback.message.answer("⚠️ Нет пользователей с ролью администратора.")
        else:
            admin_list = "\n".join(
                [f"@{admin.username or '—'} (ID: {admin.tg_id})" for admin in admins]
            )
            await callback.message.answer(f"👑 Администраторы:\n\n{admin_list}")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")
    await callback.answer()