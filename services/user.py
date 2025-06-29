from typing import List
from sqlalchemy import select, Result
from sqlalchemy.orm import Session
from models.user import User


async def get_user_by_id(user_id: int, db: Session):
    return db.get(User, user_id)


async def get_users_with_role(role: str, db: Session) -> List[User]:
    stmt = select(User).where(User.role == role).order_by(User.id)
    result: Result = db.execute(stmt)
    users = result.scalars().all()
    return list(users)


async def get_user_by_tg_id(tg_id: int, db: Session) -> User:
    stmt = select(User).where(User.tg_id == tg_id)
    result: Result = db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_username(username: str, db: Session) -> User:
    stmt = select(User).where(User.username == username)
    result: Result = db.execute(stmt)
    return result.scalar_one_or_none()


async def change_user_role(tg_id: int, new_role: str, db: Session):
    user = await get_user_by_tg_id(tg_id, db)

    if user:
        user.role = new_role
        db.add(user)
        db.commit()
    else:
        raise ValueError(f"Пользователь с tg_id={tg_id} не найден.")
