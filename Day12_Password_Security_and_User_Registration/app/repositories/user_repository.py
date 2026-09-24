from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User


class UserRepository:

    def get_by_email(
        self,
        session: Session,
        email: str,
    ) -> User | None:
        statement = select(User).where(
            User.email == email
        )

        return session.scalar(statement)

    def create(
        self,
        session: Session,
        user: User,
    ) -> User:
        session.add(user)

        session.flush()

        return user