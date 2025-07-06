from typing import Union

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import Session

from config.constants import set_new_greeting
from data.state import AdminStates
from keyboards.admin.adminInterface import AdminInterfaceText
from utils.access import check_admin_access
from utils.logger import logger

router = Router()


@router.callback_query(F.data == "change_greeting")
@router.message(F.text == AdminInterfaceText.AdminMenu.CHANGE_GREETING)
@router.message(Command("change_greeting"))
async def change_greeting_message(
    update: Union[CallbackQuery, Message], db: Session, state: FSMContext
):
    logger.info("Обновляем приветствие")
    if not await check_admin_access(update, db):
        return

    await update.answer(text="✏️ Введите новое приветственное сообщение:")
    await state.set_state(AdminStates.waiting_for_new_greeting)


@router.message(AdminStates.waiting_for_new_greeting)
async def save_new_greeting(message: Message, state: FSMContext):
    new_text = message.text.strip()
    try:
        set_new_greeting(new_text)
        await message.answer("✅ Приветственный текст успешно обновлён.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при сохранении: {e}")
    await state.clear()
