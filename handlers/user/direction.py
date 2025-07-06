from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import (
    CallbackQuery,
)
from sqlalchemy.orm import Session

from keyboards.admin.inline.direction import (
    get_direction_btn_list,
)
from services import DirectionService, UserService
from utils.logger import logger

router = Router()


# Существующие обработчики (без изменений)
@router.callback_query(F.data == "direction_UNDECIDED")
async def direction_undecided(callback: CallbackQuery, db: Session):
    logger.info(
        f"Пользователь {callback.from_user.id} не определился с желаемым направлением"
    )
    user_service = UserService(db)
    user = user_service.get_user(callback.from_user.id)
    user.direction_id = 0
    db.commit()
    await callback.message.edit_text(
        f"✅ Хорошо, пока не определились с направлением. "
        f"Можете потом изменить это в <b>профиле</b>\n\nТеперь вы "
        f"можете задавать свои вопросы",
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("direction_confirm_"))
async def confirm_direction(callback: CallbackQuery, db: Session):
    logger.info(f"Пользователь {callback.from_user.id} подтверждает направление")
    user_service = UserService(db)
    direction_service = DirectionService(db)
    name = callback.data.removeprefix("direction_confirm_")
    direction = direction_service.get_direction_by_name(name)
    if not direction:
        await callback.answer("❌ Направление не найдено")
        return
    user = user_service.get_user(callback.from_user.id)
    user.direction_id = direction.id
    db.commit()
    await callback.message.edit_text(
        f"✅ Вы выбрали направление: <b>{direction.name}</b>\n\nТеперь вы можете задавать свои вопросы",
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "direction_back")
async def back_to_directions(callback: CallbackQuery, db: Session):
    logger.info("Пользователь возвращается назад")
    try:
        direction_service = DirectionService(db)
        directions = direction_service.get_all_directions()
        await callback.message.edit_text(
            "Выберите направление:",
            reply_markup=await get_direction_btn_list(directions=directions),
        )
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            # Игнорируем попытку редактирования без изменений
            pass
        else:
            raise
    await callback.answer()
