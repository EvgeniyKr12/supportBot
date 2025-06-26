from aiogram import Router, F
from sqlalchemy.orm import Session
from config.constants import ADMIN_IDS
from aiogram.types import Message, CallbackQuery
from services.dialog_service import DialogService
from aiogram.utils.keyboard import InlineKeyboardBuilder


router = Router()

@router.callback_query(F.data.startswith("take_dialog_"))
async def take_dialog(callback: CallbackQuery, bot, db: Session):
    user_id = int(callback.data.split("_")[-1])
    operator_id = callback.from_user.id
    dialog_service = DialogService(db)

    dialog = dialog_service.get_dialog_by_user_id(user_id)

    if not dialog:
        await callback.answer("Диалог уже закрыт!", show_alert=True)
        return

    if dialog.operator_id:
        await callback.answer("Диалог уже занят другим оператором!", show_alert=True)
        return

    dialog_service.assign_operator(dialog.id, operator_id)

    builder = InlineKeyboardBuilder()
    builder.button(text="🔒 Закрыть диалог", callback_data=f"close_dialog_{dialog.id}")

    await bot.send_message(user_id,"👨💼 Оператор подключился к диалогу. Можете задавать вопросы!")
    await callback.message.edit_text(
        f"✅ Вы взяли диалог с пользователем ID: {user_id}\n"
        f"Вопрос: {dialog.question}\n\n"
        "Отправляйте сообщения - они будут пересланы пользователю.",
        reply_markup=builder.as_markup()
    )

@router.callback_query(F.data.startswith("close_dialog_"))
async def close_dialog_handler(callback: CallbackQuery, bot, db: Session):
    dialog_id = int(callback.data.split("_")[-1])
    dialog_service = DialogService(db)

    dialog = dialog_service.get_dialog_by_id(dialog_id)
    if not dialog:
        await callback.answer("❌ Диалог не найден", show_alert=True)
        return

    dialog_service.close_dialog(user_id=dialog.user_id)

    await callback.message.edit_text("✅ Диалог успешно закрыт", reply_markup=None)
    await callback.answer()

    await bot.send_message(dialog.user_id, "❌ Диалог с оператором завершен. Если у вас новый вопрос — просто напишите снова.")

@router.message(F.text)
async def operator_response(message: Message, bot, db: Session):
    if message.from_user.id not in ADMIN_IDS:
        return

    dialog_service = DialogService(db)
    dialog = dialog_service.get_dialog_by_operator(message.from_user.id)

    if not dialog:
        await message.answer("❌ У вас нет активного диалога.")
        return

    await bot.send_message(dialog.user_id, f"👨💼 Оператор:\n\n{message.text}")
