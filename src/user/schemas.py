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


class SignInResponseSchema(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    expires_at: int
    token_type: str


class SignOutSchema(BaseModel):
    token: str


class VerifyTokenSchema(BaseModel):
    token: str
