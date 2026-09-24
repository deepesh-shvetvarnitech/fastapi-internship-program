from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateUserEmailError
from app.core.security import hash_password
from app.db.models import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserRegisterRequest


class AuthService:

    def __init__(
        self,
        user_repository: UserRepository,
    ):
        self.user_repository = user_repository

    def register_user(
        self,
        session: Session,
        data: UserRegisterRequest,
    ) -> User:
        email = data.email.lower().strip()

        existing_user = self.user_repository.get_by_email(
            session,
            email,
        )

        if existing_user:
            raise DuplicateUserEmailError()

        password_hash = hash_password(
            data.password
        )

        user = User(
            email=email,
            password_hash=password_hash,
        )

        try:
            self.user_repository.create(
                session,
                user,
            )

            session.commit()

            session.refresh(user)

            return user

        except IntegrityError:
            session.rollback()

            raise DuplicateUserEmailError()