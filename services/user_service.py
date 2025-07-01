from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from models.user import User, UserRole, UserType


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, tg_id: int) -> Optional[User]:
        return self._get_user_by_tg_id(tg_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        stmt = select(User).where(User.username == username)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def create_user(self, tg_id: int, username: str = None) -> User:
        new_user = User(tg_id=tg_id, username=username, role=UserRole.USER)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def set_user_type(self, tg_id: int, user_type: str) -> str:
        user = self.get_user(tg_id)
        if not user:
            raise ValueError("User not found")

        user.user_type = UserType(user_type.replace("set_", "").upper())
        self.db.commit()
        return str(user.user_type)

    def has_direction(self, tg_id: int) -> bool:
        user = self.get_user(tg_id)
        return user is not None and user.direction_id is not None

    def change_role(self, tg_id: int, new_role: UserRole) -> None:
        user = self.get_user(tg_id)
        if not user:
            raise ValueError(f"User with tg_id={tg_id} not found")

        user.role = new_role
        self.db.commit()

    def get_users_by_role(self, role: UserRole) -> List[User]:
        stmt = select(User).where(User.role == role).order_by(User.id)
        result = self.db.execute(stmt)
        return list(result.scalars())

    def get_privileged_users(self) -> List[User]:
        stmt = select(User).where(User.role != UserRole.USER).order_by(User.id)
        result = self.db.execute(stmt)
        return list(result.scalars())

    def _get_user_by_tg_id(self, tg_id: int) -> Optional[User]:
        stmt = select(User).where(User.tg_id == tg_id)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()
