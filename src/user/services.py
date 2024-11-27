from fastapi import Depends, HTTPException, status
from supabase import create_client
from src.config import oauth2_scheme
from src.settings import get_settings
from .repository import UserRepository
from .schemas import UserCreateSchema, UserSignInSchema, SignInResponseSchema
from gotrue.errors import AuthApiError


class UserService:
    def __init__(self, user_repo: UserRepository = Depends()):
        self.user_repository = user_repo

    async def get_user_by_id(self, user_id: str) -> dict:
        user = await self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_user_by_email(self, email: str) -> dict:
        user = await self.user_repository.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def user_exists(self, email: str) -> bool:
        user = await self.user_repository.get_user_by_email(email)
        return user is not None

    async def create_user(self, user: UserCreateSchema):
        print(user.email)
        existing_user = await self.user_repository.get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
            )
        created_user = await self.user_repository.create_user(user)
        return created_user


class AuthService:
    def __init__(
        self,
        user_service: UserService = Depends(),
    ):
        self.user_service = user_service
        self.settings = get_settings()
        self.supabase = create_client(
            supabase_key=self.settings.SUPABASE_KEY,
            supabase_url=self.settings.SUPABASE_URL,
        )

    async def sign_in(self, user: UserSignInSchema):
        try:
            await self.user_service.get_user_by_email(user.email)
            response = self.supabase.auth.sign_in_with_password(
                {
                    "email": user.email,
                    "password": user.password,
                }
            )
            response = SignInResponseSchema(
                access_token=response.model_dump().get("session")["access_token"],
                refresh_token=response.model_dump().get("session")["refresh_token"],
                expires_in=response.model_dump().get("session")["expires_in"],
                expires_at=response.model_dump().get("session")["expires_at"],
                token_type=response.model_dump().get("session")["token_type"],
            )
        except AuthApiError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=e.message
            )
        return response

    async def sign_up(self, new_user: UserCreateSchema):
        try:
            user = await self.user_service.user_exists(new_user.email)
            if user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already exists",
                )
            response = self.supabase.auth.sign_up(
                {
                    "email": new_user.email,
                    "password": new_user.password,
                }
            )
            new_user = UserCreateSchema(
                id=response.model_dump().get("user")["id"],
                email=new_user.email,
                fullname=new_user.fullname,
                image=new_user.image,
            )
            user = await self.user_service.create_user(new_user)
        except AuthApiError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=e.message
            )
        return user

    async def sign_out(self, token: str):
        try:
            response = self.supabase.auth.get_user(
                jwt=token,
            )
            if not response:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
                )
            self.supabase.auth.sign_out()
        except AuthApiError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=e.message
            )
        return response

    async def get_current_user(self, token: str = Depends(oauth2_scheme)):
        try:
            response = self.supabase.auth.get_user(jwt=token)
            if response.user is None:
                raise HTTPException(
                    status_code=401,
                    detail="Not valid credentialsssss",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            return response.user
        except Exception as e:
            print(e)
            raise HTTPException(
                status_code=401,
                detail="Not valid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
