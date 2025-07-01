from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import Session

from data.state import AdminStates
from models import UserRole
from services import UserService


router = Router()


def is_admin(user):
    return user and user.role == "super-admin"


@router.callback_query(F.data == "add_admin")
async def add_admin(callback: CallbackQuery, state: FSMContext, db: Session):
    user_service = UserService(db)
    user = user_service.get_user(callback.from_user.id)
    if not is_admin(user):
        await callback.message.answer("❌ У вас нет доступа.")
        await callback.answer()
        return

    await callback.message.answer(
        "Чтобы добавить нового оператора(если они еще не "
        "пользовался ботом) - нужно чтобы он написал команду "
        "/start, а после администратор передала сюда"
        "username (@username) или tg_id пользователя, "
        "чтобы назначить его администратором:"
    )
    await state.set_state(AdminStates.waiting_admin_username)
    await callback.answer()


@router.message(AdminStates.waiting_admin_username)
async def save_new_admin(message: Message, state: FSMContext, db: Session):
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

        if user.role == "admin":
            await message.answer("⚠️ Этот пользователь уже является администратором.")
            await state.clear()
            return

        user_service.change_role(user.tg_id, UserRole.ADMIN)
        await message.answer(
            f"✅ Пользователь @{user.username or user.tg_id} теперь администратор."
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    await state.clear()


@router.callback_query(F.data == "remove_admin")
async def ask_admin_to_remove(callback: CallbackQuery, state: FSMContext, db: Session):
    user_service = UserService(db)
    user = user_service.get_user(callback.from_user.id)
    if not is_admin(user):
        await callback.message.answer("❌ У вас нет доступа.")
        await callback.answer()
        return

    try:
        admins = user_service.get_users_by_role(UserRole.ADMIN)
        if not admins:
            await callback.message.answer("⚠️ Нет пользователей с ролью администратора.")
            await callback.answer()
            return

        admin_list = "\n".join(
            [f"@{admin.username or '—'} (ID: {admin.tg_id})" for admin in admins]
        )
        await callback.message.answer(
            f"👑 Администраторы:\n\n{admin_list}\n\n"
            "Введите username с @ или tg_id администратора, которого хотите понизить до пользователя:"
        )
        await state.set_state(AdminStates.waiting_admin_removal_username)
    except Exception as e:
        await callback.message.answer(
            f"❌ Ошибка при получении списка администраторов: {e}"
        )
    await callback.answer()


@router.message(AdminStates.waiting_admin_removal_username)
async def remove_admin(message: Message, state: FSMContext, db: Session):
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

        if user.role != "admin":
            await message.answer("⚠️ Этот пользователь не является администратором.")
            await state.clear()
            return

        user_service.change_role(user.tg_id, UserRole.USER)
        await message.answer(
            f"✅ Пользователь @{user.username or user.tg_id} понижен до пользователя."
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
    await state.clear()


@router.callback_query(F.data == "show_admins")
async def get_admins(callback: CallbackQuery, db: Session):
    user_service = UserService(db)
    user = user_service.get_user(callback.from_user.id)
    if not is_admin(user):
        await callback.message.answer("❌ У вас нет доступа.")
        await callback.answer()
        return

    try:
        admins = user_service.get_users_by_role(UserRole.ADMIN)
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
