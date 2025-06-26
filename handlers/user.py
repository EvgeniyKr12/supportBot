from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy.orm import Session
from services.matcher import find_answers
from services.dialog_service import DialogService
from utils.notify_admin import notify_admins
from config.constants import GREETING_TEXT, ADMIN_IDS


router = Router()

@router.message(Command("start"))
async def start(message: Message):
    if message.from_user.id in ADMIN_IDS:
        return

    await message.answer(GREETING_TEXT)

@router.message(F.text)
async def handle_question(message: Message, bot, db: Session):
    if message.from_user.id in ADMIN_IDS:
        dialog_service = DialogService(db)
        dialog = dialog_service.get_dialog_by_operator(message.from_user.id)

        if not dialog:
            await message.answer("❌ У вас нет активного диалога.")
            return

        await bot.send_message(dialog.user_id, f"👨💼 Оператор:\n\n{message.text}")
        return

    matches = find_answers(message.text)

    if matches:
        response = "🔍 Вот что я нашел:\n\n" + \
                   "\n\n".join(f"❓ *{m['question']}*\n📢 {m['answer']}" for m in matches)

        await message.answer(response, parse_mode="Markdown")
        return

    dialog_service = DialogService(db)
    dialog = dialog_service.get_dialog_by_user_id(message.from_user.id)

    if dialog and dialog.operator_id:
        await bot.send_message(dialog.operator_id,  f"📨 Новое сообщение от пользователя {message.from_user.id}:\n\n{message.text}")
        return

    if dialog:
        await message.answer("⏳ Ваш вопрос уже в обработке. Ожидайте оператора.")
        return

    try:
        dialog_service.create_dialog(
            user_id=message.from_user.id,
            username=message.from_user.username,
            question=message.text
        )
    except Exception as e:
        print(f"Ошибка при создании диалога: {e}")

    await message.answer('Я не нашёл ответа 😔 Скоро с вами свяжется оператор!')
    await notify_admins(bot=bot, chat_id=message.chat.id, text=message.text)

