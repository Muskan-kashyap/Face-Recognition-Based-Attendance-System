from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session, joinedload

from app.db.models.all_models import User


class UserRepository:
    def get_user_with_shift(self, db: Session, *, user_id: int) -> User | None:
        return (
            db.query(User)
            .options(joinedload(User.shift))
            .filter(User.id == user_id)
            .first()
        )


user_repo = UserRepository()

