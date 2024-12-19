from fastapi import APIRouter, Depends, status
from .services import UserService, AuthService
from src.schemas import ResponseNotFound
from .schemas import (
    UserCreateSchema,
    UserSignInSchema,
    SignInResponseSchema,
    SignOutSchema,
    VerifyTokenSchema,
)

AuthRouter = APIRouter()


# @AuthRouter.get(
#     "/signup",
#     response_model=DebtResponseSchema,
#     responses={status.HTTP_404_NOT_FOUND: {"model": ResponseNotFound}},
# )
# async def get_debt(debt_id: str, debt_service: UserService = Depends()):
#     debt = await debt_service.get_debt_by_id(debt_id)
#     return debt


# @AuthRouter.get("/signin")
# async def get_debts(user_id: str, debt_service: UserService = Depends()):
#     # user = await debt_service.get_user_by_id(user_id)
#     debts = await debt_service.get_debts_by_user_id(user_id)
#     return debts


@AuthRouter.post("/signup")
async def create_debt(user: UserCreateSchema, auth_service: AuthService = Depends()):
    new_user = await auth_service.sign_up(user)
    return new_user


@AuthRouter.post("/signin", response_model=SignInResponseSchema)
async def create_debt(user: UserSignInSchema, auth_service: AuthService = Depends()):
    new_user = await auth_service.sign_in(user)
    return new_user


@AuthRouter.get("/signout")
async def create_debt(token: str, auth_service: AuthService = Depends()):
    new_user = await auth_service.sign_out(token=token)
    return new_user


# @AuthRouter.post("/verify")
# async def verify_token(
#     verify_token: VerifyTokenSchema, auth_service: AuthService = Depends()
# ):
#     try:
#         response = await auth_service.get_current_user(verify_token.token)
#         return response
#     except Exception as e:
#         return {"error": str(e)}
