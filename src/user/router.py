from fastapi import APIRouter, Request, Depends
from .dependencies import auth_dependency, AuthService, get_auth_service
from src.schemas import ResponseNotFound
from .schemas import (
    UserCreateSchema,
    UserSignInSchema,
    UserResetPasswordSchema,
    UserUpdatePasswordSchema,
    SignInResponseSchema,
)

AuthRouter = APIRouter()


@AuthRouter.post("/sign-up")
async def sign_up(
    user: UserCreateSchema, auth_service: AuthService = Depends(get_auth_service)
):
    new_user = await auth_service.sign_up(user)
    return new_user


@AuthRouter.post("/sign-in", response_model=SignInResponseSchema)
async def sign_in(
    user: UserSignInSchema, auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.sign_in(user)
    return user


@AuthRouter.post("/reset-password")
async def reset_password(
    user: UserResetPasswordSchema, auth_service: AuthService = Depends(get_auth_service)
):
    user = await auth_service.reset_password(user.email)
    return user


@AuthRouter.post("/update-password")
async def update_password(
    user: UserUpdatePasswordSchema,
    current_user: auth_dependency,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.update_password(user)
    return user


@AuthRouter.get("/sign-out")
async def sign_out(token: str, auth_service: AuthService = Depends(get_auth_service)):
    user = await auth_service.sign_out(token=token)
    return user


@AuthRouter.get("/refresh-session")
async def refresh_session(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.refresh_session(refresh_token)
    return user


@AuthRouter.get("/get-current-user")
async def get_current_user(
    request: Request,
    current_user: auth_dependency,
    auth_service: AuthService = Depends(get_auth_service),
):
    authorization = request.headers.get("Authorization")
    token = authorization.split(" ")[1]
    user = await auth_service.get_current_user(token)
    return user
