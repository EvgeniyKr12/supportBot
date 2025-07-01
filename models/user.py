from enum import Enum
from sqlalchemy import Enum as SqlEnum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class UserType(str, Enum):
    APPLICANT = "applicant"
    PARENT = "parent"
    OTHER = "other"


class UserRole(str, Enum):
    USER = "user"
    OPERATOR = "operator"
    ADMIN = "admin"
    SUPER_ADMIN = "super-admin"


class User(Base):
    tg_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(SqlEnum(UserRole), default=UserRole.USER)
    type: Mapped[UserType | None] = mapped_column(SqlEnum(UserType), nullable=True)

    direction_id: Mapped[int | None] = mapped_column(
        ForeignKey("directions.id"),
        nullable=True,
        comment="Связь с выбранным направлением обучения",
    )
    direction: Mapped["Direction"] = relationship(
        back_populates="users", lazy="selectin"
    )
