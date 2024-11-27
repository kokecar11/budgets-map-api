from supabase import create_client
from fastapi import Depends
from src.dependecies import db_dependency
from src.settings import get_settings
from .models import UserModel
from .schemas import UserCreateSchema


class UserRepository:

    def __init__(self, db: db_dependency):
        self.db = db
        self.settings = get_settings()

    async def get_user_by_id(self, user_id: str) -> dict:
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()

    async def get_user_by_email(self, email: str) -> dict:
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    async def create_user(self, user: UserCreateSchema) -> dict:
        exist_user = await self.get_user_by_email(user.email)
        if not exist_user:
            new_user = UserModel(
                id=user.id,
                fullname=user.fullname,
                email=user.email,
                image=user.image,
            )
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return new_user
        return None

    async def update_user(self, user: UserModel) -> dict:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    async def user_exists(self, email: str) -> bool:
        user = await self.get_user_by_email(email)
        return user is not None

    # async def delete_user(self, user_id: str) -> dict:
    #     user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
    #     self.db.delete(user)
    #     self.db.commit()
    #     return user
