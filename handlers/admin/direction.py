from typing import Union

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from sqlalchemy.orm import Session

from data.state import AdminStates
from keyboards.admin.adminInterface import AdminInterfaceText
from keyboards.admin.inline.direction import (
    confirm_direction_keyboard,
    get_direction_btn_list,
)
from keyboards.admin.reply.direction import get_direction_management_kb
from services import DirectionService
from utils.access import check_admin_access
from utils.logger import logger

router = Router()


@router.callback_query(F.data == "direction_management")
@router.message(F.text == AdminInterfaceText.AdminMenu.DIRECTION_PANEL)
async def operator_panel_handler(update: Union[CallbackQuery, Message], db: Session):
    logger.info("Управление образовательными программами")
    if not await check_admin_access(update, db):
        return

    message = update.message if isinstance(update, CallbackQuery) else update
    await message.answer(
        "🛠 <b>Управление образовательными программами</b>",
        reply_markup=get_direction_management_kb(),
        parse_mode="HTML",
    )
    if isinstance(update, CallbackQuery):
        await update.answer()


@router.message(F.text == AdminInterfaceText.Direction.ADD)
async def add_direction_handler(
    update: Union[CallbackQuery, Message],
    state: FSMContext,
    db: Session,
):
    logger.info("Добавление направления")
    if not await check_admin_access(update, db):
        return

    message = update.message if isinstance(update, CallbackQuery) else update
    await message.answer(
        text="Для добавления направления отправьте данные в формате:\n\n"
        "<code>Название направления\n"
        "Код направления\n"
        "Необходимые экзамены\n"
        "Кол-во бюджетных мест\n"
        "Кол-во коммерческих мест\n"
        "Минимальный балл\n"
        "Стоимость обучения</code>\n\n"
        "Пример:\n"
        "Компьютерные науки\n"
        "09.03.03\n"
        "Математика, Информатика\n"
        "150\n"
        "220\n"
        "220\n"
        "120000",
        parse_mode="HTML",
    )
    await state.set_state(AdminStates.waiting_new_direction_data)

    if isinstance(update, CallbackQuery):
        await update.answer()


@router.message(AdminStates.waiting_new_direction_data)
async def save_new_direction(message: Message, state: FSMContext, db: Session):
    try:
        data = message.text.split('\n')
        if len(data) != 7:
            raise ValueError("Неверный формат данных")

        name, code, exams, budget, commerce, min_score, price = [
            item.strip() for item in data
        ]

        direction_service = DirectionService(db)
        direction_service.create_direction(
            name=name,
            code=code,
            exams=exams,
            budget=int(budget),
            commerce=int(commerce),
            min_score=int(min_score),
            price=int(price),
        )

        await message.answer(
            f"✅ Направление <b>{name}</b> успешно добавлено!",
            reply_markup=get_direction_management_kb(),
            parse_mode="HTML",
        )
    except ValueError as e:
        await message.answer(f"❌ Ошибка: {str(e)}\nПопробуйте еще раз.")
    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: {str(e)}")
    finally:
        await state.clear()


@router.message(F.text == AdminInterfaceText.Direction.REMOVE)
async def remove_direction_handler(update: Union[CallbackQuery, Message], db: Session):
    logger.info("Удаление направления")
    if not await check_admin_access(update, db):
        return

    direction_service = DirectionService(db)
    message = update.message if isinstance(update, CallbackQuery) else update

    try:
        directions = direction_service.get_all_directions()
        if not directions:
            await message.answer("ℹ️ Нет доступных направлений.")
            return

        await message.answer(
            text="Выберите направление для удаления:",
            reply_markup=await get_direction_btn_list(directions=directions),
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

    if isinstance(update, CallbackQuery):
        await update.answer()


@router.callback_query(F.data == "direction_list")
@router.message(F.text == AdminInterfaceText.Direction.LIST)
async def admin_educational_programs_handler(message: Message, db: Session):
    logger.info("Пользователь запрашивает информацию о направлениях")

    direction_service = DirectionService(db)
    directions = direction_service.get_all_directions()

    if len(directions) == 0:
        await message.answer(
            text="📚 <b>Список образовательных программ пуст</b>",
            parse_mode="HTML",
        )
    else:
        await message.answer(
            text="📚 <b>Список образовательных программ</b>",
            reply_markup=await get_direction_btn_list(
                directions=directions, undecided_btn=False
            ),
            parse_mode="HTML",
        )


async def render_direction_detail(
    message: Message,
    direction,
    is_admin: bool,
    answer: bool = False,
):
    exams_list = ", ".join(exam.strip() for exam in direction.exams.split(','))
    info_text = (
        f"<b>🎓 {direction.name}</b> (<code>{direction.code}</code>)\n\n"
        f"<b>📚 Необходимые экзамены:</b> {exams_list}\n"
        f"<b> Кол-во бюджетных мест: {direction.budget}</b>\n"
        f"<b> Кол-во коммерческих мест: {direction.commerce}</b>\n"
        f"<b>📊 Минимальный балл:</b> {direction.min_score}\n"
        f"<b>💰 Стоимость обучения:</b> {direction.price:,} руб./год\n\n"
    ).replace(",", " ")

    if answer:
        await message.answer(
            info_text,
            reply_markup=confirm_direction_keyboard(direction.name, is_admin),
            parse_mode="HTML",
        )
    else:
        await message.edit_text(
            info_text,
            reply_markup=confirm_direction_keyboard(direction.name, is_admin),
            parse_mode="HTML",
        )


@router.callback_query(F.data.startswith("direction_info_"))
async def show_direction_info(callback: CallbackQuery, db: Session):
    logger.info("Информация о направлении")
    direction_service = DirectionService(db)
    name = callback.data.removeprefix("direction_info_")
    print(name)
    direction = direction_service.get_direction_by_name(name)

    if not direction:
        await callback.answer("❌ Направление не найдено")
        return

    is_admin = await check_admin_access(callback, db)
    await render_direction_detail(callback.message, direction, is_admin)
    await callback.answer()


# Обработчик для кнопки "Удалить"
@router.callback_query(F.data.startswith("direction_delete_"))
async def delete_direction_handler(callback: CallbackQuery, db: Session):
    try:
        name = callback.data.removeprefix("direction_delete_")
        direction_service = DirectionService(db)
        direction = direction_service.get_direction_by_name(name)
        logger.info(
            f"Админ {callback.from_user.id} пытается удалить обр. программу с name: {name} и id: {direction.id}"
        )
        if not direction:
            await callback.answer("❌ Образовательная программа не найдена")
            return

        confirm_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Да, удалить",
                        callback_data=f"confirm_direction_delete_{direction.name}",
                    ),
                    InlineKeyboardButton(
                        text="❌ Отмена",
                        callback_data=f"direction_info_{direction.name}",
                    ),
                ]
            ]
        )

        try:
            await callback.message.edit_text(
                f"⚠️ Вы уверены, что хотите удалить образовательную программу <b>{direction.name}</b>?",
                reply_markup=confirm_kb,
                parse_mode="HTML",
            )
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise
    except Exception as e:
        logger.error(f"Error in delete handler: {e}")
    finally:
        await callback.answer()


@router.callback_query(F.data.startswith("confirm_direction_delete_"))
async def confirm_delete_direction(callback: CallbackQuery, db: Session):
    logger.info(f"Админ {callback.from_user.id} подтверждает удаление обр. программы")
    try:
        name = callback.data.removeprefix("confirm_direction_delete_")
        direction_service = DirectionService(db)
        direction = direction_service.get_direction_by_name(name)

        if not direction:
            await callback.answer("❌ Образовательная программа не найдена")
            return

        direction_service.delete_direction(direction.id)
        await callback.message.delete()
        await callback.message.answer(
            f"🗑️ Образовательная программа {direction.name} удалено!"
        )
    except Exception as e:
        logger.error(f"Error confirming delete: {e}")
        await callback.answer("❌ Ошибка при удалении")


# Обработчик для кнопки "Изменить"
@router.callback_query(F.data.startswith("direction_edit_"))
async def edit_direction_handler(
    callback: CallbackQuery, state: FSMContext, db: Session
):
    name = callback.data.removeprefix("direction_edit_")
    direction_service = DirectionService(db)
    print(name)
    direction = direction_service.get_direction_by_name(name)

    if not direction:
        await callback.answer("❌ Образовательная программа не найдена")
        return

    logger.info(
        f"Админ {callback.from_user.id} пытается изменить направление {direction.name}"
    )
    # Сохраняем ID направления в состоянии
    await state.update_data(edit_direction_id=direction.id)

    # Формируем сообщение с текущими данными
    current_data = (
        f"{direction.name}\n"
        f"{direction.code}\n"
        f"{direction.exams}\n"
        f"{direction.budget}\n"
        f"{direction.commerce}\n"
        f"{direction.min_score}\n"
        f"{direction.price}"
    )

    back_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="❌ Отмена", callback_data=f"direction_info_{direction.name}"
                )
            ]
        ]
    )

    # Отправляем инструкцию с текущими данными
    await callback.message.edit_text(
        text=f"✏️ Редактирование образовательной программы <b>{direction.name}</b>\n\n"
        "Отправьте новые данные в формате:\n\n"
        "<code>Название направления\n"
        "Код направления\n"
        "Необходимые экзамены\n"
        "Кол-во бюджетных мест\n"
        "Кол-во коммерческих мест\n"
        "Минимальный балл\n"
        "Стоимость обучения</code>\n\n"
        "Текущие данные:\n\n"
        f"{current_data}\n\n"
        "Измените нужные строки и отправьте новую версию",
        reply_markup=back_kb,
        parse_mode="HTML",
    )

    # Устанавливаем состояние ожидания новых данных
    await state.set_state(AdminStates.waiting_edit_direction_data)
    await callback.answer()


# Обработчик для получения новых данных направления
@router.message(AdminStates.waiting_edit_direction_data)
async def save_edited_direction(message: Message, state: FSMContext, db: Session):
    data = await state.get_data()
    direction_id = data.get('edit_direction_id')
    direction_service = DirectionService(db)

    if not direction_id:
        await message.answer("❌ Ошибка: не найден ID направления")
        await state.clear()
        return

    try:
        # Парсим новые данные
        new_data = message.text.split('\n')
        if len(new_data) != 7:
            raise ValueError("Неверный формат данных. Ожидается 7 строк данных.")

        name, code, exams, budget, commerce, min_score, price = [
            item.strip() for item in new_data
        ]

        # Обновляем направление
        direction_service.update_direction(
            direction_id,
            name=name,
            code=code,
            exams=exams,
            budget=int(budget),
            commerce=int(commerce),
            min_score=int(min_score),
            price=int(price),
        )

        # Получаем обновленное направление
        updated_direction = direction_service.get_direction_by_id(direction_id)

        # Показываем обновленную информацию
        is_admin = await check_admin_access(message, db)
        await render_direction_detail(message, updated_direction, is_admin, True)

    except ValueError as e:
        await message.answer(f"❌ Ошибка: {str(e)}\nПопробуйте еще раз.")
    except Exception as e:
        logger.error(f"Ошибка при обновлении направления: {str(e)}")
        await message.answer("❌ Произошла ошибка при обновлении направления.")
    finally:
        await state.clear()
