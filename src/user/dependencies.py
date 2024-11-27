from fastapi import Depends
from typing import Annotated
from src.user.services import AuthService

auth_service = AuthService()

auth_dependency = Annotated[dict, Depends(auth_service.get_current_user)]
