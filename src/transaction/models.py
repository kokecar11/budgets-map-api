from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from src.config import generate_uuid
from src.database import Base
from src.budget.models import BudgetModel


class TransactionModel(Base):
    __tablename__ = "transactions"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    budget_id = Column(String, ForeignKey("budgets.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    transaction_date = Column(DateTime, nullable=False)
    category = Column(String, nullable=False)

    budget = relationship("BudgetModel", back_populates="transactions")
    debt_payments = relationship("DebtPaymentModel", back_populates="transaction")
