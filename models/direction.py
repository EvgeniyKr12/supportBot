from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class Direction(Base):
    name: Mapped[str] = mapped_column(unique=True)
    code: Mapped[str] = mapped_column(unique=True)
    exams: Mapped[str] = mapped_column(comment="Необходимые экзамены через запятую")
    min_score: Mapped[int] = mapped_column(comment="Минимальный проходной балл")
    price: Mapped[int] = mapped_column(comment="Стоимость обучения в рублях")

    # Обратная связь с User
    users: Mapped[list["User"]] = relationship(
        back_populates="direction", lazy="dynamic", cascade="all, delete-orphan"
    )
