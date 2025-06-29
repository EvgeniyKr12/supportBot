from models.dialog import Dialog
from sqlalchemy.orm import Session


class DialogService:
    def __init__(self, session: Session):
        self.session = session

    def create_dialog(self, user_id: int, question: str, username: str = None):
        """Добавляет новый диалог в БД"""
        try:
            dialog = Dialog(
                user_id=user_id,
                username=username,
                question=question,
                is_active=True
            )
            self.session.add(dialog)
            self.session.commit()
            print(f"✅ Диалог создан: ID {dialog.id}")
            return dialog
        except Exception as e:
            print(f"❌ Ошибка: {e} - create_dialog")
            self.session.rollback()
            raise

    def get_dialog_by_operator(self, operator_id: int):
        """Возвращает активный диалог оператора"""
        try:
            return self.session.query(Dialog).filter(
                Dialog.operator_id == operator_id,
                Dialog.is_active == True
            ).first()
        except Exception as e:
            print(f"❌ Ошибка: {e} - get_dialog_by_operator")
            raise

    def get_active_dialogs(self) -> list[type[Dialog]]:
        """Возвращает все активные диалоги"""
        try:
            return self.session.query(Dialog).filter(Dialog.is_active == True).all()
        except Exception as e:
            print(f"❌ Ошибка: {e} - get_active_dialogs")
            raise

    def get_dialog_by_id(self, dialog_id: int):
        """Получает диалог по ID"""
        try:
            return self.session.query(Dialog).filter(Dialog.id == dialog_id).first()
        except Exception as e:
            print(f"❌ Ошибка при получении диалога: {e}")
            self.session.rollback()
            raise

    def get_dialog_by_user_id(self, user_id: int):
        """Получает активный диалог по ID пользователя"""
        try:
            return self.session.query(Dialog).filter(
                Dialog.user_id == user_id,
                Dialog.is_active == True
            ).first()
        except Exception as e:
            print(f"❌ Ошибка при получении диалога пользователя: {e}")
            self.session.rollback()
            raise

    def close_dialog(self, user_id: int):
        """Закрывает диалог по user_id"""
        try:
            dialog = self.session.query(Dialog).filter(
                Dialog.user_id == user_id,
                Dialog.is_active == True
            ).first()
            if dialog:
                dialog.is_active = False
                dialog.operator_id = None
                self.session.commit()
                print(f"✅ Диалог закрыт: ID {dialog.id}")
        except Exception as e:
            print(f"❌ Ошибка: {e} - close_dialog")
            self.session.rollback()
            raise

    def assign_operator(self, dialog_id: int, operator_id: int):
        """Назначение оператора на диалог"""
        try:
            dialog = self.session.get(Dialog, dialog_id)
            if dialog:
                dialog.operator_id = operator_id
                self.session.commit()
                print(f"✅ Оператор назначен: ID {operator_id} на диалог {dialog_id}")
        except Exception as e:
            print(f"❌ Ошибка: {e} - assign_operator")
            self.session.rollback()
            raise
