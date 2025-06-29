from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import Session
from config.constants import set_new_greeting, load_questions, save_questions
from data.state import AdminStates
from keyboards.admin.inlineKeyboard import get_options_keyboard
from keyboards.admin.replyKeyboard import ReplyButtonText
from services.user import (
    get_user_by_username,
    change_user_role,
    get_users_with_role,
    get_user_by_tg_id,
)

router = Router()


def is_admin(user):
    return user and user.role in ("admin", "super-admin")


@router.message(Command(ReplyButtonText.ADMIN_PANEL))
@router.message(F.text == ReplyButtonText.ADMIN_PANEL)
async def show_admin_panel(message: Message, db: Session):
    user = await get_user_by_tg_id(message.from_user.id, db)
    if not is_admin(user):
        await message.answer("❌ У вас нет доступа.")
        return

    await message.answer(
        text="Выберите опцию",
        reply_markup=get_options_keyboard(user.role == "super-admin"),
    )


@router.callback_query(F.data == "change_greeting")
async def change_greeting_text(callback: CallbackQuery, db: Session, state: FSMContext):
    user = await get_user_by_tg_id(callback.from_user.id, db)
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


@router.callback_query(F.data == "add_operator")
async def add_operator(callback: CallbackQuery, db: Session, state: FSMContext):
    user = await get_user_by_tg_id(callback.from_user.id, db)
    if not is_admin(user):
        await callback.message.answer("❌ У вас нет доступа.")
        await callback.answer()
        return

    await callback.message.answer(
        "Чтобы добавить нового оператора, попросите пользователя написать боту команду /start "
        "и отправить вам свой username (@username)."
    )
    await state.set_state(AdminStates.waiting_operator_username)
    await callback.answer()


@router.message(AdminStates.waiting_operator_username)
async def save_new_operator(message: Message, state: FSMContext, db: Session):
    username = message.text.strip().lstrip("@")

    try:
        user = await get_user_by_username(username, db)
        if not user:
            await message.answer(f"❌ Пользователь @{username} не найден.")
            await state.clear()
            return

        await change_user_role(user.tg_id, "operator", db)
        await message.answer(f"✅ Пользователь @{username} успешно назначен оператором.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при назначении оператора: {e}")
    await state.clear()


@router.callback_query(F.data == "remove_operator")
async def ask_operator_to_remove(callback: CallbackQuery, state: FSMContext, db: Session):
    user = await get_user_by_tg_id(callback.from_user.id, db)
    if not is_admin(user):
        await callback.message.answer("❌ У вас нет доступа.")
        await callback.answer()
        return

    try:
        operators = await get_users_with_role("operator", db)
        if not operators:
            await callback.message.answer("⚠️ Нет пользователей с ролью оператора.")
            await callback.answer()
            return

        operator_list = "\n".join(
            [f"@{op.username or '—'} (ID: {op.tg_id})" for op in operators]
        )
        await callback.message.answer(
            f"👮‍♂️ Операторы:\n\n{operator_list}\n\n"
            "Введите username (без @) или tg_id оператора, которого хотите понизить до пользователя:"
        )
        await state.set_state(AdminStates.waiting_operator_removal_username)
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при получении списка операторов: {e}")
    await callback.answer()


@router.message(AdminStates.waiting_operator_removal_username)
async def remove_operator(message: Message, state: FSMContext, db: Session):
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

        if user.role != "operator":
            await message.answer(f"⚠️ Пользователь @{user.username or user.tg_id} не является оператором.")
            await state.clear()
            return

        await change_user_role(user.tg_id, "user", db)
        await message.answer(f"✅ Пользователь @{user.username or user.tg_id} понижен до пользователя.")
    except Exception as e:
        await message.answer(f"❌ Ошибка при понижении: {e}")
    await state.clear()


@router.callback_query(F.data == "show_operators")
async def get_operators(callback: CallbackQuery, db: Session):
    user = await get_user_by_tg_id(callback.from_user.id, db)
    if not is_admin(user):
        await callback.message.answer("❌ У вас нет доступа.")
        await callback.answer()
        return

    try:
        operators = await get_users_with_role("operator", db)
        if not operators:
            await callback.message.answer("⚠️ Нет пользователей с ролью оператора.")
        else:
            operator_list = "\n".join(
                [f"@{op.username or '—'} (ID: {op.tg_id})" for op in operators]
            )
            await callback.message.answer(f"👮‍♂️ Операторы:\n\n{operator_list}")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {e}")
    await callback.answer()


@router.callback_query(F.data == "show_questions")
async def show_questions(callback: CallbackQuery, db: Session):
    user = await get_user_by_tg_id(callback.from_user.id, db)
    if not is_admin(user):
        await callback.message.answer("❌ У вас нет доступа.")
        await callback.answer()
        return

    try:
        questions = load_questions()
        if not questions:
            await callback.message.answer("📭 Вопросы не найдены.")
        else:
            text = "\n\n".join(
                [f"❓ {q}\n💬 {a}" for q, a in questions.items()]
            )
            await callback.message.answer(f"📚 Список вопросов:\n\n{text}")
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка при загрузке: {e}")
    await callback.answer()


@router.callback_query(F.data == "add_question")
async def ask_new_question(callback: CallbackQuery, state: FSMContext, db: Session):
    user = await get_user_by_tg_id(callback.from_user.id, db)
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
async def ask_question_to_remove(callback: CallbackQuery, state: FSMContext, db: Session):
    user = await get_user_by_tg_id(callback.from_user.id, db)
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

