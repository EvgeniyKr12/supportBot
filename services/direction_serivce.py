from sqlalchemy import select
from sqlalchemy.orm import Session

from models.direction import Direction


class DirectionService:
    def __init__(self, db: Session):
        self.db = db

    def get_all_directions(self):
        result = self.db.execute(select(Direction))
        return result.scalars().all()

    def get_direction_by_code(self, code: str):
        result = self.db.execute(select(Direction).where(Direction.code == code))
        return result.scalar_one_or_none()

    @staticmethod
    def get_direction_info(direction: Direction) -> str:
        return (
            f"<b>{direction.name}</b>\n\n"
            f"📝 Экзамены: {direction.exams}\n"
            f"🎯 Минимальный балл: {direction.min_score}\n"
            f"💵 Стоимость в год: {direction.price} руб."
        )
