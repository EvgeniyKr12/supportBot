from sqlalchemy import select
from sqlalchemy.orm import Session

from models.direction import Direction


class DirectionService:
    def __init__(self, db: Session):
        self.db = db

    def create_direction(
        self, name: str, code: str, exams: str, min_score: int, price: int
    ):
        direction = Direction(
            name=name, code=code, exams=exams, min_score=min_score, price=price
        )
        self.db.add(direction)
        self.db.commit()
        return direction

    def get_all_directions(self):
        return self.db.query(Direction).all()

    @staticmethod
    def get_direction_info(direction: Direction) -> str:
        """
        Формирует информационное сообщение о направлении обучения в HTML-формате

        :param direction: Объект направления из БД
        :return: Форматированная строка с информацией
        """
        exams_list = ", ".join(exam.strip() for exam in direction.exams.split(','))

        info_text = (
            f"<b>🎓 {direction.name}</b> (<code>{direction.code}</code>)\n\n"
            f"<b>📚 Необходимые экзамены:</b> {exams_list}\n"
            f"<b>📊 Минимальный балл:</b> {direction.min_score}\n"
            f"<b>💰 Стоимость обучения:</b> {direction.price:,} руб./год\n\n"
            f"<i>Выберите '✅ Подтвердить' для выбора этого направления</i>"
        ).replace(
            ",", " "
        )  # Замена обычной запятой на thin space в числах

        return info_text

    def get_direction_by_code(self, code):
        stmt = select(Direction).where(Direction.code == code)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    def get_direction_by_id(self, direction_id: int):
        return self.db.query(Direction).filter(Direction.id == direction_id).first()

    def delete_direction(self, direction_id: int):
        direction = self.get_direction_by_id(direction_id)
        if direction:
            self.db.delete(direction)
            self.db.commit()
            return True
        return False
