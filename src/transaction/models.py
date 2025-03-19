import datetime
from sqlalchemy import Column, ForeignKey, String, Text, DateTime, event
from sqlalchemy.orm import relationship
from src.config import generate_uuid
from src.database import Base
from src.budget.models import BudgetModel
from src.income.models import IncomeModel
from src.saving.models import SavingModel
from src.expense.models import ExpenseModel


class TransactionModel(Base):
    __tablename__ = "transactions"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)
    category = Column(String, nullable=False)

    budget_transaction = relationship(
        "BudgetTransactionModel", back_populates="transaction"
    )
    debt_payments = relationship("DebtPaymentModel", back_populates="transaction")
    incomes = relationship("IncomeModel", back_populates="transaction")
    savings = relationship("SavingModel", back_populates="transaction")
    expenses = relationship("ExpenseModel", back_populates="transaction")


@event.listens_for(TransactionModel, "before_update")
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.datetime.now(datetime.timezone.utc)


@event.listens_for(TransactionModel, "before_insert")
def set_created_at(mapper, connection, target):
    target.created_at = datetime.datetime.now(datetime.timezone.utc)
