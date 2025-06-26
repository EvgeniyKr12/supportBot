from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime


Base = declarative_base()

class Dialog(Base):
    __tablename__ = "dialogs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False) # ID пользователя в Telegram
    operator_id = Column(Integer, nullable=True) # ID оператора
    username = Column(String(50), nullable=True)  # @username (опционально)
    question = Column(String(500))  # Вопрос от пользователя
    is_active = Column(Boolean, default=True)  # Активен ли диалог
    created_at = Column(DateTime, default=datetime.now)  # Время создания
