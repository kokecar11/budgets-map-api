import enum
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Enum, event
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
    creditor = Column(String, nullable=False)
    amount = Column(Integer, nullable=False, default=0)
    description = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=False)
    status = Column(Enum(DebtStatus), nullable=False, default=DebtStatus.PENDING)
    installment_count = Column(Integer, nullable=False, default=0)
    minimum_payment = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    debt_payments = relationship("DebtPaymentModel", back_populates="debt")


@event.listens_for(DebtModel, "before_update")
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.datetime.now(datetime.timezone.utc)


@event.listens_for(DebtModel, "before_insert")
def set_created_at(mapper, connection, target):
    target.created_at = datetime.datetime.now(datetime.timezone.utc)


class DebtPaymentModel(Base):
    __tablename__ = "debt_payments"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    debt_id = Column(String, ForeignKey("debts.id"), nullable=False)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)
    payment_date = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    amount_paid = Column(Integer, nullable=False, default=0)
    installment_number = Column(Integer, nullable=False, default=0)
    status = Column(Enum(DebtStatus), nullable=False, default=DebtStatus.PENDING)
    created_at = Column(
        DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc)
    )
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    debt = relationship("DebtModel", back_populates="debt_payments")
    transaction = relationship("TransactionModel", back_populates="debt_payments")


@event.listens_for(DebtPaymentModel, "before_update")
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.datetime.now(datetime.timezone.utc)


@event.listens_for(DebtPaymentModel, "before_insert")
def set_created_at(mapper, connection, target):
    target.created_at = datetime.datetime.now(datetime.timezone.utc)
