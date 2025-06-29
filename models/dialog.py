from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Boolean, DateTime
from .base import Base


class Dialog(Base):
    user_id: Mapped[int] = mapped_column(nullable=False)  # ID пользователя в Telegram
    operator_id: Mapped[int | None] = mapped_column(nullable=True)  # ID оператора
    username: Mapped[str | None] = mapped_column(String(50), nullable=True)  # @username
    question: Mapped[str] = mapped_column(String(500))  # Вопрос от пользователя
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # Активен ли диалог
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)  # Дата создания
