from typing import Union

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import Session

from config.constants import load_questions, save_questions
from data.state import AdminStates
from keyboards.admin.reply.admin import get_manager_kb
from keyboards.admin.reply.question import get_question_management_kb
from keyboards.admin.text import ButtonText
from utils.access import check_admin_access

router = Router()


@router.callback_query(F.data == "question_management")
@router.message(F.text == ButtonText.AdminMenu.QUESTION_PANEL)
@router.message(Command("questions"))
async def question_panel_handler(update: Union[CallbackQuery, Message], db: Session):
    if not await check_admin_access(update, db):
        return

    message = update.message if isinstance(update, CallbackQuery) else update
    await message.answer(
        "📚 Управление вопросами FAQ", reply_markup=get_question_management_kb()
    )

    if isinstance(update, CallbackQuery):
        await update.answer()


@router.callback_query(F.data == "show_questions")
@router.message(F.text == ButtonText.Question.LIST)
@router.message(Command("list_questions"))
async def show_questions_handler(update: Union[CallbackQuery, Message], db: Session):
    if not await check_admin_access(update, db):
        return

    message = update.message if isinstance(update, CallbackQuery) else update

    try:
        questions = load_questions()
        if not questions:
            await message.answer("ℹ️ В базе нет вопросов.")
            return

        questions_list = "\n\n".join(
            f"❓ {question}\n💬 {answer}" for question, answer in questions.items()
        )
        await message.answer(
            f"📋 Список вопросов:\n\n{questions_list}",
            reply_markup=get_question_management_kb(),
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка загрузки: {str(e)}")

    if isinstance(update, CallbackQuery):
        await update.answer()


@router.callback_query(F.data == "add_question")
@router.message(F.text == ButtonText.Question.ADD)
@router.message(Command("add_question"))
async def add_question_handler(
    update: Union[CallbackQuery, Message], state: FSMContext, db: Session
):
    if not await check_admin_access(update, db):
        return

    message = update.message if isinstance(update, CallbackQuery) else update
    await message.answer("📝 Введите текст нового вопроса:")
    await state.set_state(AdminStates.waiting_for_new_question_text)

    if isinstance(update, CallbackQuery):
        await update.answer()


@router.message(AdminStates.waiting_for_new_question_text)
async def receive_question_text(message: Message, state: FSMContext):
    question = message.text.strip()
    if len(question) < 5:
        await message.answer("⚠️ Вопрос должен содержать минимум 5 символов.")
        return

    await state.update_data(question_text=question)
    await message.answer("💬 Теперь введите ответ на этот вопрос:")
    await state.set_state(AdminStates.waiting_for_new_answer_text)


@router.message(AdminStates.waiting_for_new_answer_text)
async def receive_answer_text(message: Message, state: FSMContext):
    answer = message.text.strip()
    if len(answer) < 5:
        await message.answer("⚠️ Ответ должен содержать минимум 5 символов.")
        return

    data = await state.get_data()
    question = data.get("question_text")

    try:
        questions = load_questions()
        questions[question] = answer
        save_questions(questions)
        await message.answer(
            "✅ Вопрос и ответ успешно добавлены!",
            reply_markup=get_question_management_kb(),
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка сохранения: {str(e)}")
    finally:
        await state.clear()


@router.callback_query(F.data == "remove_question")
@router.message(F.text == ButtonText.Question.REMOVE)
@router.message(Command("remove_question"))
async def remove_question_handler(
    update: Union[CallbackQuery, Message], state: FSMContext, db: Session
):
    if not await check_admin_access(update, db):
        return

    message = update.message if isinstance(update, CallbackQuery) else update

    try:
        questions = load_questions()
        if not questions:
            await message.answer("ℹ️ В базе нет вопросов для удаления.")
            return

        numbered_questions = list(questions.items())
        text_list = "\n\n".join(
            f"{i + 1}. ❓ {q}\n💬 {a}" for i, (q, a) in enumerate(numbered_questions)
        )
        await state.update_data(numbered_questions=numbered_questions)

        await message.answer(
            f"📋 Вопросы:\n\n{text_list}\n\nВведите номер вопроса, который хотите удалить:",
            reply_markup=get_question_management_kb()
        )
        await state.set_state(AdminStates.waiting_for_question_removal)
    except Exception as e:
        await message.answer(f"❌ Ошибка загрузки: {str(e)}")

    if isinstance(update, CallbackQuery):
        await update.answer()


@router.message(AdminStates.waiting_for_question_removal)
async def remove_question(message: Message, state: FSMContext):
    try:
        index = int(message.text.strip()) - 1
    except ValueError:
        await message.answer("⚠️ Введите корректный номер (цифру).")
        return

    data = await state.get_data()
    numbered_questions = data.get("numbered_questions", [])

    if index < 0 or index >= len(numbered_questions):
        await message.answer("❌ Неверный номер вопроса.")
        return

    question_text = numbered_questions[index][0]

    try:
        questions = load_questions()
        if question_text in questions:
            del questions[question_text]
            save_questions(questions)
            await message.answer(
                f"✅ Вопрос №{index + 1} удалён.",
                reply_markup=get_question_management_kb()
            )
        else:
            await message.answer("❌ Вопрос уже удалён или не найден.")
    except Exception as e:
        await message.answer(f"❌ Ошибка удаления: {str(e)}")
    finally:
        await state.clear()

