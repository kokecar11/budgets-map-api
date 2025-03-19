import datetime
from sqlalchemy import Column, String, DateTime, event
from sqlalchemy.orm import relationship
from src.database import Base


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, index=True)
    fullname = Column(String)
    email = Column(String, unique=True, index=True)
    email_verified = Column(DateTime, nullable=True)
    image = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    budgets = relationship("BudgetModel", back_populates="user")


@event.listens_for(UserModel, "before_insert")
def set_created_at(mapper, connection, target):
    target.created_at = datetime.datetime.now(datetime.timezone.utc)
