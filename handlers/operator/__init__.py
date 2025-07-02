from aiogram import Router

from .operator import router as operator_router

router = Router()

router.include_router(operator_router)
