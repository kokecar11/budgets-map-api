from fastapi import Depends
from typing import Annotated
from src.dependencies import db_dependency
from src.config import oauth2_scheme
from .repository import UserRepository
from .services import UserService, AuthService


def get_user_service(db: db_dependency):
    return UserService(UserRepository(db))


def get_auth_service(
    db: db_dependency,
):
    user_service = UserService(UserRepository(db))
    return AuthService(user_service=user_service)


async def get_current_user(
    auth_service: AuthService = Depends(get_auth_service),
    token: str = Depends(oauth2_scheme),
):
    return await auth_service.get_current_user(token)


auth_dependency = Annotated[dict, Depends(get_current_user)]
