from aiogram import Router

from .direction import router as direction_router
from .question import router as question_router
from .type import router as type_router
from .user import router as user_router

router = Router()

router.include_router(user_router)
router.include_router(direction_router)
router.include_router(question_router)
router.include_router(type_router)
