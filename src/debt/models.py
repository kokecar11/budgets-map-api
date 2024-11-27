import enum
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from src.config import generate_uuid
from src.database import Base
from src.transaction.models import TransactionModel


class DebtStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"


class DebtModel(Base):
    __tablename__ = "debts"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    creditor = Column(String, nullable=False)
    amount = Column(Integer, nullable=False, default=0)
    description = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=False)
    status = Column(Enum(DebtStatus), nullable=False, default=DebtStatus.PENDING)
    installment_count = Column(Integer, nullable=False, default=0)
    minimum_payment = Column(Integer, nullable=False, default=0)

    debt_payments = relationship("DebtPaymentModel", back_populates="debt")
    user = relationship("UserModel", back_populates="debts")


class DebtPaymentModel(Base):
    __tablename__ = "debt_payments"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    debt_id = Column(String, ForeignKey("debts.id"), nullable=False)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)
    paymente_date = Column(
        DateTime, nullable=False
    )  # TODO: Cambiar a payment_date y agregar default=datetime.now
    amount_paid = Column(Integer, nullable=False, default=0)
    installment_number = Column(Integer, nullable=False, default=0)
    status = Column(Enum(DebtStatus), nullable=False, default=DebtStatus.PENDING)

    debt = relationship("DebtModel", back_populates="debt_payments")
    transaction = relationship("TransactionModel", back_populates="debt_payments")
