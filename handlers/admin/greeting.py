from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import Session

from config.constants import set_new_greeting
from data.state import AdminStates
from services import UserService
from utils.access import is_admin


router = Router()


@router.callback_query(F.data == "change_greeting")
async def change_greeting_text(callback: CallbackQuery, db: Session, state: FSMContext):
    user_service = UserService(db)
    user = user_service.get_user(callback.from_user.id)
    if not is_admin(user):
        await callback.message.answer("❌ У вас нет доступа.")
        await callback.answer()
        return

    await callback.message.answer("✏️ Введите новое приветственное сообщение:")
    await state.set_state(AdminStates.waiting_for_new_greeting)
    await callback.answer()


@router.message(AdminStates.waiting_for_new_greeting)
async def save_new_greeting(message: Message, state: FSMContext):
    new_text = message.text.strip()
    try:
        set_new_greeting(new_text)
        await message.answer("✅ Приветственный текст успешно обновлён.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при сохранении: {e}")
    await state.clear()
