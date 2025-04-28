import datetime
from sqlalchemy import Column, ForeignKey, Float, String, DateTime, event, func
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
    description = Column(String, nullable=True)
    type = Column(String, nullable=False, default="Balanced")
    created_at = Column(DateTime, nullable=True, server_default=func.now())
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    user = relationship("UserModel", back_populates="budgets")
    budget_transaction = relationship("BudgetTransactionModel", back_populates="budget")


@event.listens_for(BudgetModel, "before_update")
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.datetime.now(datetime.timezone.utc)


@event.listens_for(BudgetModel, "before_insert")
def set_created_at(mapper, connection, target):
    target.created_at = datetime.datetime.now(datetime.timezone.utc)


class BudgetTransactionModel(Base):
    __tablename__ = "budget_transaction"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    budget_id = Column(String, ForeignKey("budgets.id"), nullable=False)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)
    amount = Column(Float, nullable=False)

    budget = relationship("BudgetModel", back_populates="budget_transaction")
    transaction = relationship("TransactionModel", back_populates="budget_transaction")
