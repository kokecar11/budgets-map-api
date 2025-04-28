from src.schemas import BaseModel
from typing import Optional


class UserCreateSchema(BaseModel):
    id: Optional[str] = None
    fullname: str
    email: str
    image: Optional[str] = None
    password: Optional[str] = None


class UserSignInSchema(BaseModel):
    email: str
    password: str


class UserResetPasswordSchema(BaseModel):
    email: str


class UserUpdatePasswordSchema(BaseModel):
    password: str


class SignInResponseSchema(BaseModel):
    id: str
    email: str
    fullname: str
    image: Optional[str] = None
    access_token: str
    refresh_token: str
    expires_in: int
    expires_at: int
    token_type: str


class RefreshSessionSchema(SignInResponseSchema):
    pass


class SignOutSchema(BaseModel):
    token: str


class VerifyTokenSchema(BaseModel):
    token: str
