from typing import Union
from utils.logger import logger
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.orm import Session

from data.state import AdminStates
from keyboards.admin.base import get_confirmation_kb
from keyboards.admin.inline.inline import get_directions_list_kb
from keyboards.admin.reply.direction import get_direction_management_kb
from keyboards.admin.text import ButtonText
from services import DirectionService
from utils.access import check_admin_access


router = Router()


@router.callback_query(F.data == "direction_management")
@router.message(F.text == ButtonText.AdminMenu.DIRECTION_PANEL)
@router.message(Command("directions"))
async def direction_panel_handler(update: Union[CallbackQuery, Message], db: Session,):
    logger.info("Управление направлениями")
    if not await check_admin_access(update, db):
        return

    message = update.message if isinstance(update, CallbackQuery) else update
    await message.answer(
        text=ButtonText.AdminMenu.DIRECTION_PANEL, reply_markup=get_direction_management_kb()
    )

    if isinstance(update, CallbackQuery):
        await update.answer()


@router.callback_query(F.data == "add_direction")
@router.message(F.text == ButtonText.Direction.ADD)
@router.message(Command("add_direction"))
async def add_direction_handler(
    update: Union[CallbackQuery, Message], state: FSMContext, db: Session,
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
        "Минимальный балл\n"
        "Стоимость обучения</code>\n\n"
        "Пример:\n"
        "<code>Компьютерные науки\n"
        "CS101\n"
        "Математика, Информатика\n"
        "220\n"
        "120000</code>",
        parse_mode="HTML",
    )
    await state.set_state(AdminStates.waiting_new_direction_data)

    if isinstance(update, CallbackQuery):
        await update.answer()


@router.message(AdminStates.waiting_new_direction_data)
async def save_new_direction(message: Message, state: FSMContext, db: Session):
    try:
        data = message.text.split('\n')
        if len(data) != 5:
            raise ValueError("Неверный формат данных")

        name, code, exams, min_score, price = [item.strip() for item in data]

        direction_service = DirectionService(db)
        direction_service.create_direction(
            name=name,
            code=code,
            exams=exams,
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


@router.callback_query(F.data == "remove_direction")
@router.message(F.text == ButtonText.Direction.REMOVE)
@router.message(Command("remove_direction"))
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
            "Выберите направление для удаления:",
            reply_markup=get_directions_list_kb(directions, action="remove"),
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

    if isinstance(update, CallbackQuery):
        await update.answer()


@router.callback_query(F.data.startswith("remove_direction_"))
async def confirm_remove_direction(callback: CallbackQuery, db: Session):
    direction_id = int(callback.data.split('_')[-1])
    direction_service = DirectionService(db)

    try:
        direction = direction_service.get_direction_by_id(direction_id)
        if not direction:
            await callback.answer("❌ Направление не найдено")
            return

        await callback.message.answer(
            f"Вы уверены, что хотите удалить направление <b>{direction.name}</b>?",
            reply_markup=get_confirmation_kb(f"confirm_remove_{direction_id}"),
        )
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {str(e)}")
    finally:
        await callback.answer()


@router.callback_query(F.data.startswith("confirm_remove_"))
async def execute_remove_direction(callback: CallbackQuery, db: Session):
    direction_id = int(callback.data.split('_')[-1])
    direction_service = DirectionService(db)

    try:
        direction = direction_service.get_direction_by_id(direction_id)
        if not direction:
            await callback.answer("❌ Направление не найдено")
            return

        direction_service.delete_direction(direction_id)
        await callback.message.answer(
            f"✅ Направление <b>{direction.name}</b> успешно удалено!",
            reply_markup=get_direction_management_kb(),
        )
    except Exception as e:
        await callback.message.answer(f"❌ Ошибка: {str(e)}")
    finally:
        await callback.answer()


@router.callback_query(F.data == "show_directions")
@router.message(F.text == ButtonText.Direction.LIST)
@router.message(Command("list_directions"))
async def list_directions_handler(update: Union[CallbackQuery, Message], db: Session,):
    logger.info("Список направлений")
    if not await check_admin_access(update, db):
        return

    direction_service = DirectionService(db)
    message = update.message if isinstance(update, CallbackQuery) else update

    try:
        directions = direction_service.get_all_directions()
        if not directions:
            await message.answer("ℹ️ Нет доступных направлений.")
            return

        directions_list = "\n\n".join(
            f"📌 <b>{d.name}</b> ({d.code})\n"
            f"📝 Экзамены: {d.exams}\n"
            f"🎯 Мин. балл: {d.min_score}\n"
            f"💵 Стоимость: {d.price} руб."
            for d in directions
        )

        await message.answer(
            f"📚 Список направлений:\n\n{directions_list}",
            reply_markup=get_direction_management_kb(),
            parse_mode="HTML",
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {str(e)}")

    if isinstance(update, CallbackQuery):
        await update.answer()
