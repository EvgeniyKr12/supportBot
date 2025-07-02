from aiogram import F, Router, Bot
from aiogram.types import Message
from sqlalchemy.orm import Session

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
async def handle_question(message: Message, bot: Bot, db: Session):
    logger.info("Пользователь задает вопрос")
    user_service = UserService(db)
    user = user_service.get_user(message.from_user.id)

    if is_access(user):
        dialog_service = DialogService(db)
        dialog = dialog_service.get_dialog_by_operator(message.from_user.id)

        if not dialog:
            await message.answer("❌ У вас нет активного диалога.")
            return

        await bot.send_message(dialog.user_id, f"👨💼 Оператор:\n\n{message.text}")
        return

    matches = find_answers(message.text)

    if matches:
        response = "🔍 Вот что я нашел:\n\n" + "\n\n".join(
            f"❓ *{m['question']}*\n📢 {m['answer']}" for m in matches
        )

        await message.answer(response, parse_mode="Markdown")
        return

    dialog_service = DialogService(db)
    dialog = dialog_service.get_dialog_by_user_id(message.from_user.id)

    if dialog and dialog.operator_id:
        await bot.send_message(
            dialog.operator_id,
            f"📨 Новое сообщение от пользователя {message.from_user.id}:\n\n{message.text}",
        )
        return

    if dialog:
        await message.answer("⏳ Ваш вопрос уже в обработке. Ожидайте оператора.")
        return

    try:
        dialog_service.create_dialog(
            user_id=message.from_user.id,
            username=message.from_user.username,
            question=message.text,
        )
    except Exception as e:
        print(f"Ошибка при создании диалога: {e}")

    await message.answer('Я не нашёл ответа 😔 Скоро с вами свяжется оператор!')
    await notify_admins(bot=bot, chat_id=message.chat.id, text=message.text, db=db)
