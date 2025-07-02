from aiogram import Bot, F, Router
from aiogram.types import Message
from sqlalchemy.orm import Session
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from data.state import UserDataForm
from keyboards.user.inlineKeyboard import InlineButtonText, choose_direction
from models import UserRole
from services import UserService
from services.dialog_service import DialogService
from services.matcher import find_answers
from utils.logger import logger
from utils.notify_admin import notify_admins

router = Router()


def is_access(user):
    return user and user.role in (
        UserRole.ADMIN,
        UserRole.SUPER_ADMIN,
        UserRole.OPERATOR,
    )


@router.message(F.text)
async def handle_question(message: Message, bot: Bot, db: Session, state: FSMContext):
    user_service = UserService(db)
    user = user_service.get_user(message.from_user.id)

    if user is None:
        user = user_service.create_user(message.from_user.id, message.from_user.username)

    if is_access(user):
        dialog_service = DialogService(db)
        dialog = dialog_service.get_dialog_by_operator(message.from_user.id)
        if not dialog:
            await message.answer("❌ У вас нет активного диалога.")
        else:
            await bot.send_message(dialog.user_id, f"👨💼 Оператор:\n\n{message.text}")
        return

    # Сохраняем вопрос
    dialog_service = DialogService(db)
    dialog = dialog_service.get_dialog_by_user_id(message.from_user.id)

    if user.type is None:
        builder = InlineKeyboardBuilder()
        builder.button(text="🎓 Абитуриент", callback_data=InlineButtonText.SET_APPLICANT)
        builder.button(text="👨‍👩‍👧 Родитель", callback_data=InlineButtonText.SET_PARENT)
        builder.button(text="❓ Другое", callback_data=InlineButtonText.SET_OTHER)
        builder.adjust(1)
        await message.answer("Пожалуйста, выберите, кто вы:", reply_markup=builder.as_markup())
        await state.set_state(UserDataForm.waiting_for_type)
        return

    if user.direction_id is None:
        await message.answer(
            "Пожалуйста, выберите направление обучения:",
            reply_markup=await choose_direction(db)
        )
        await state.set_state(UserDataForm.waiting_for_direction)
        return

    # Создание или обновление диалога
    try:
        if not dialog:
            dialog_service.create_dialog(
                user_id=message.from_user.id,
                username=message.from_user.username,
                question=message.text,
            )
            await notify_admins(bot=bot, chat_id=message.chat.id, text=message.text, db=db)
        elif dialog.operator_id:
            await bot.send_message(
                dialog.operator_id,
                f"📨 Новое сообщение от пользователя {message.from_user.id}:\n\n{message.text}",
            )
            return
    except Exception as e:
        logger.error(f"Ошибка при обработке диалога: {e}")
        await message.answer("⚠️ Произошла ошибка. Попробуйте позже.")
        return

    # Ответ пользователю
    await message.answer("⏳ Ваш вопрос уже в обработке. Ожидайте оператора.")
    matches = find_answers(message.text)
    if matches:
        response = "🔍 Вот что я нашел:\n\n" + "\n\n".join(
            f"❓ *{m['question']}*\n📢 {m['answer']}" for m in matches
        )
        await message.answer(response, parse_mode="Markdown")