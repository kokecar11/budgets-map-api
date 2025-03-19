from fastapi import Depends
from typing import Annotated
from sqlalchemy.orm import Session
from src.database import get_db

db_dependency = Annotated[Session, Depends(get_db)]
