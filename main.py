import asyncio
import sys
from models.base import Base
from models.user import User
from models.dialog import Dialog
from config.config import token
from handlers import user, operator, admin, super_admin
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from utils.middlewares_db import DbSessionMiddleware
import logging


engine = create_engine("sqlite:///data/database.db")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

bot = Bot(token=token)
dp = Dispatcher(storage=MemoryStorage())

dp.message.middleware(DbSessionMiddleware(SessionLocal))
dp.callback_query.middleware(DbSessionMiddleware(SessionLocal))


dp.include_router(super_admin.router)
dp.include_router(admin.router)
dp.include_router(user.router)
dp.include_router(operator.router)


def print_startup():
    print("\n" + "=" * 50)
    print(" ✅ Бот успешно запущен!")
    print("=" * 50 + "\n")


async def main() -> None:
    print_startup()
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
