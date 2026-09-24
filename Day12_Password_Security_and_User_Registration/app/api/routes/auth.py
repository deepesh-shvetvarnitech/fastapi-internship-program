from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


def get_auth_service() -> AuthService:
    return AuthService(
        user_repository=UserRepository()
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
def register(
    data: UserRegisterRequest,
    session: Session = Depends(get_session),
    auth_service: AuthService = Depends(
        get_auth_service
    ),
):
    return auth_service.register_user(
        session,
        data,
    )