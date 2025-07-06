from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Direction(Base):
    name: Mapped[str] = mapped_column(unique=True)
    code: Mapped[str] = mapped_column(unique=False)
    exams: Mapped[str] = mapped_column(comment="Необходимые экзамены через запятую")
    budget: Mapped[int] = mapped_column(comment="Кол-во бюджетных мест")
    commerce: Mapped[int] = mapped_column(comment="Кол-во коммерческих мест")
    min_score: Mapped[int] = mapped_column(comment="Минимальный проходной балл")
    price: Mapped[int] = mapped_column(comment="Стоимость обучения в рублях")

    # Обратная связь с User
    users: Mapped[list["User"]] = relationship(
        back_populates="direction", lazy="dynamic", cascade="all, delete-orphan"
    )
