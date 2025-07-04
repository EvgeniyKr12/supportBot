from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.orm import Session

from keyboards.user.inlineKeyboard import choose_direction, confirm_direction_keyboard
from services import DirectionService, UserService
from utils.logger import logger

router = Router()


@router.callback_query(F.data.startswith("direction_info_"))
async def show_direction_info(callback: CallbackQuery, db: Session):
    logger.info("Информация о направлении")
    direction_service = DirectionService(db)
    code = callback.data.split("_")[2]
    direction = direction_service.get_direction_by_code(code)
    if not direction:
        await callback.answer("❌ Направление не найдено")
        return
    info_text = direction_service.get_direction_info(direction)
    await callback.message.edit_text(
        info_text,
        reply_markup=confirm_direction_keyboard(direction.code),
        parse_mode="HTML",
    )
    await callback.answer()

@router.callback_query(F.data == "direction_UNDECIDED")
async def direction_undecided(callback: CallbackQuery, db: Session):
    user_service = UserService(db)
    user = user_service.get_user(callback.from_user.id)
    user.direction_id = 0
    db.commit()
    await callback.message.edit_text(
        f"✅ Хорошо, пока не определились с направлением. "
        f"Можете потом изменить это в <b>профиле</b>\n\nТеперь вы "
        f"можете задавать свои вопросы",
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("direction_confirm_"))
async def confirm_direction(callback: CallbackQuery, db: Session):
    logger.info(f"Пользователь {callback.from_user.id} подтверждает направление")
    user_service = UserService(db)
    direction_service = DirectionService(db)
    code = callback.data.split("_")[2]
    direction = direction_service.get_direction_by_code(code)
    if not direction:
        await callback.answer("❌ Направление не найдено")
        return
    user = user_service.get_user(callback.from_user.id)
    user.direction_id = direction.id
    db.commit()
    await callback.message.edit_text(
        f"✅ Вы выбрали направление: <b>{direction.name}</b>\n\nТеперь вы можете задавать свои вопросы", parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "direction_back")
async def back_to_directions(callback: CallbackQuery, db: Session):
    logger.info("Пользователь возвращается назад")
    await callback.message.edit_text(
        "Выберите направление:", reply_markup=await choose_direction(db)
    )
    await callback.answer()
