from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import Session

from config.constants import load_questions, save_questions
from data.state import AdminStates
from services import UserService
from utils.access import is_admin


router = Router()


@router.callback_query(F.data == "show_questions")
async def show_questions(callback: CallbackQuery, db: Session):
    user_service = UserService(db)
    user = user_service.get_user(callback.from_user.id)
    if not is_admin(user):
        await callback.message.answer("❌ У вас нет доступа.")
        await callback.answer()
        return

    try:
        questions = load_questions()
        if not questions:
            await callback.message.answer("📭 Вопросы не найдены.")
        else:
            text = "\n\n".join([f"❓ {q}\n💬 {a}" for q, a in questions.items()])
            await callback.message.answer(f"📚 Список вопросов:\n\n{text}")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при загрузке: {e}")
    await callback.answer()


@router.callback_query(F.data == "add_question")
async def ask_new_question(callback: CallbackQuery, state: FSMContext, db: Session):
    user_service = UserService(db)
    user = user_service.get_user(callback.from_user.id)
    if not is_admin(user):
        await callback.message.answer("❌ У вас нет доступа.")
        await callback.answer()
        return

    await callback.message.answer("📝 Отправьте вопрос:")
    await state.set_state(AdminStates.waiting_for_new_question_text)
    await callback.answer()


@router.message(AdminStates.waiting_for_new_question_text)
async def receive_question_text(message: Message, state: FSMContext):
    await state.update_data(question_text=message.text.strip())
    await message.answer("💬 Теперь отправьте ответ на этот вопрос:")
    await state.set_state(AdminStates.waiting_for_new_answer_text)


@router.message(AdminStates.waiting_for_new_answer_text)
async def receive_answer_text(message: Message, state: FSMContext):
    data = await state.get_data()
    question = data.get("question_text")
    answer = message.text.strip()

    try:
        questions = load_questions()
        questions[question] = answer
        save_questions(questions)
        await message.answer("✅ Вопрос и ответ успешно добавлены.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при сохранении: {e}")
    await state.clear()


@router.callback_query(F.data == "remove_question")
async def ask_question_to_remove(
    callback: CallbackQuery, state: FSMContext, db: Session
):
    user_service = UserService(db)
    user = user_service.get_user(callback.from_user.id)
    if not is_admin(user):
        await callback.message.answer("❌ У вас нет доступа.")
        await callback.answer()
        return

    questions = load_questions()
    if not questions:
        await callback.message.answer("⚠️ Нет сохранённых вопросов.")
        await callback.answer()
        return

    question_list = "\n".join([f"• {q}" for q in questions.keys()])
    await callback.message.answer(
        f"📄 Текущие вопросы:\n\n{question_list}\n\n✂️ Отправьте точный текст вопроса, который нужно удалить:"
    )
    await state.set_state(AdminStates.waiting_for_question_removal)
    await callback.answer()


@router.message(AdminStates.waiting_for_question_removal)
async def remove_question(message: Message, state: FSMContext):
    question = message.text.strip()
    try:
        questions = load_questions()
        if question not in questions:
            await message.answer("❌ Вопрос не найден.")
        else:
            del questions[question]
            save_questions(questions)
            await message.answer("✅ Вопрос удалён.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при удалении: {e}")
    await state.clear()
