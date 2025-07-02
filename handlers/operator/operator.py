from aiogram import F, Router, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.orm import Session
from html import escape
from services import DialogService, UserService
from utils.logger import logger

router = Router()


@router.callback_query(F.data.startswith("take_dialog_"))
async def take_dialog(callback: CallbackQuery, bot, db: Session):
    logger.info("Оператор берет диалог")
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

    await bot.send_message(
        user_id, "👨💼 Оператор подключился к диалогу. Можете задавать вопросы!"
    )
    await callback.message.edit_text(
        f"✅ Вы взяли диалог с пользователем ID: {user_id}\n"
        f"Вопрос: {dialog.question}\n\n"
        "Отправляйте сообщения - они будут пересланы пользователю.",
        reply_markup=builder.as_markup(),
    )


@router.callback_query(F.data.startswith("close_dialog_"))
async def close_dialog_handler(callback: CallbackQuery, bot, db: Session):
    logger.info("Оператор закрывает диалог")
    dialog_id = int(callback.data.split("_")[-1])
    dialog_service = DialogService(db)

    dialog = dialog_service.get_dialog_by_id(dialog_id)
    if not dialog:
        await callback.answer("❌ Диалог не найден", show_alert=True)
        return

    dialog_service.close_dialog(user_id=dialog.user_id)

    await callback.message.edit_text("✅ Диалог успешно закрыт", reply_markup=None)
    await callback.answer()

    await bot.send_message(
        dialog.user_id,
        "❌ Диалог с оператором завершен. Если у вас новый вопрос — просто напишите снова.",
    )


@router.message(F.text)
async def operator_response(message: Message, bot: Bot, db: Session):
    try:
        logger.info(f"Оператор отвечает, сообщение: {message.text}")

        user_service = UserService(db)
        privileged_users = user_service.get_privileged_users()

        if message.from_user.id not in [u.id for u in privileged_users]:
            logger.debug(f"Пользователь {message.from_user.id} не является оператором")
            return

        dialog_service = DialogService(db)
        dialog = dialog_service.get_dialog_by_operator(message.from_user.id)

        if not dialog or not hasattr(dialog, 'user_id'):
            logger.error(f"Диалог не найден для оператора {message.from_user.id}")
            await message.answer("❌ У вас нет активного диалога.")
            return

        try:
            await bot.send_message(
                chat_id=dialog.user_id,
                text=f"👨💼 Оператор:\n\n{escape(message.text)}",
                parse_mode="HTML"
            )
            await message.answer("✅ Сообщение отправлено пользователю")
        except Exception as e:
            logger.error(f"Ошибка отправки пользователю {dialog.user_id}: {e}")
            await message.answer("❌ Не удалось отправить сообщение пользователю")

    except Exception as e:
        logger.error(f"Ошибка в operator_response: {e}", exc_info=True)
        await message.answer("⚠️ Произошла внутренняя ошибка при обработке сообщения")