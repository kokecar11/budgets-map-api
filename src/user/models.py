from datetime import datetime
from sqlalchemy import Column, String, DateTime
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
    created_at = Column(DateTime, nullable=True, default=datetime.now())
    # accounts = relationship("AccountModel", back_populates="user")
    # sessions = relationship("SessionModel", back_populates="user")
    budgets = relationship("BudgetModel", back_populates="user")
    debts = relationship("DebtModel", back_populates="user")
