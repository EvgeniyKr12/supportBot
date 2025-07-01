from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from sqlalchemy.orm import Session


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event,
        data: Dict[str, Any],
    ) -> Any:
        db: Session = self.session_factory()
        try:
            data["db"] = db
            return await handler(event, data)
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
