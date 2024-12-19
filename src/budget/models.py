import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from src.config import generate_uuid
from src.database import Base
from src.user.models import UserModel


class BudgetModel(Base):
    __tablename__ = "budgets"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    total_amount = Column(Integer, nullable=False, default=0)
    description = Column(String, nullable=True)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )

    user = relationship("UserModel", back_populates="budgets")
    transactions = relationship("TransactionModel", back_populates="budget")
