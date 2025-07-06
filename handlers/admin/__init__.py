from aiogram import Router

from .direction import router as direction_router
from .greeting import router as greet_router
from .operator import router as operator_router
from .question import router as question_router

router = Router()

router.include_router(greet_router)
router.include_router(operator_router)
router.include_router(question_router)
router.include_router(direction_router)
