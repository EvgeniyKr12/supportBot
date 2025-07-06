from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.orm import Session

from keyboards.admin.inline.direction import get_direction_btn_list
from keyboards.user.inline.user_type import UserTypeButtonText
from models.user import UserType
from services import UserService
from utils.logger import logger

router = Router()


@router.callback_query(
    F.data.in_(
        [
            UserTypeButtonText.SET_APPLICANT,
            UserTypeButtonText.SET_PARENT,
            UserTypeButtonText.SET_OTHER,
        ]
    )
)
async def set_user_type(
    callback: CallbackQuery,
    db: Session,
):
    logger.info("Пользователь выбрал тип")
    user_service = UserService(db)
    user = user_service.get_user(callback.from_user.id)

    if not user:
        await callback.answer("❌ Пользователь не найден")
        return

    if callback.data == UserTypeButtonText.SET_APPLICANT:
        user.type = UserType.APPLICANT
        response = "✅ Вы выбрали статус: Абитуриент"
    elif callback.data == UserTypeButtonText.SET_PARENT:
        user.type = UserType.PARENT
        response = "✅ Вы выбрали статус: Родитель"
    else:
        user.type = UserType.OTHER
        response = "✅ Вы выбрали статус: Иное"

    db.commit()
    db.refresh(user)
    await callback.answer()
    if user.direction_id is None:
        await callback.message.answer(
            "Выберите направление обучения на которое хотите:",
            reply_markup=await get_direction_btn_list(db),
        )
        return
    else:
        await callback.message.answer(
            f"{response}\n\nТеперь вы можете задавать вопросы!"
        )
