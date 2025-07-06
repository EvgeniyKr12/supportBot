from sqlalchemy import select
from sqlalchemy.orm import Session

from models.direction import Direction


class DirectionService:
    def __init__(self, db: Session):
        self.db = db

    def create_direction(
        self,
        name: str,
        code: str,
        exams: str,
        budget: int,
        commerce: int,
        min_score: int,
        price: int,
    ):
        direction = Direction(
            name=name,
            code=code,
            exams=exams,
            min_score=min_score,
            price=price,
            budget=budget,
            commerce=commerce,
        )
        self.db.add(direction)
        self.db.commit()
        return direction

    def get_all_directions(self):
        return self.db.query(Direction).all()

    def get_direction_by_name(self, name: str):
        stmt = select(Direction).where(Direction.name == name)
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

    def update_direction(self, direction_id: int, **kwargs) -> bool:
        """
        Обновляет данные направления по его ID

        :param direction_id: ID направления для обновления
        :param kwargs: Параметры для обновления (name, code, exams, budget, commerce, min_score, price)
        :return: True если обновление успешно, False если направление не найдено
        """
        direction = self.get_direction_by_id(direction_id)
        if not direction:
            return False

        # Обновляем только переданные поля
        for key, value in kwargs.items():
            if hasattr(direction, key):
                setattr(direction, key, value)

        self.db.commit()
        return True
