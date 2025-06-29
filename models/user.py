from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class User(Base):
    tg_id: Mapped[int] = mapped_column(
        nullable=False,
        unique=True,
    )
    username: Mapped[str] = mapped_column(
        unique=True,
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        nullable=False,
        default="user",
    )
