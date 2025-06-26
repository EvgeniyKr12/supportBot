import asyncio
from models.dialog import Base
from config.config import token
from handlers import user, operator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from utils.middlewares_db import DbSessionMiddleware


engine = create_engine("sqlite:///data/database.db")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

bot = Bot(token=token)
dp = Dispatcher(storage=MemoryStorage())

dp.message.middleware(DbSessionMiddleware(SessionLocal))
dp.callback_query.middleware(DbSessionMiddleware(SessionLocal))

dp.include_router(user.router)
dp.include_router(operator.router)

def print_startup():
    print("\n" + "=" * 50)
    print(" ✅ Бот успешно запущен!")
    print("=" * 50 + "\n")

async def main():
    print_startup()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
