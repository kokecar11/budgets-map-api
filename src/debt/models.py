import enum
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Enum, Float, event
from sqlalchemy.orm import relationship
from src.config import generate_uuid
from src.database import Base
from src.transaction.models import TransactionModel


class DebtStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"


class PaymentFrequency(enum.Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class DebtModel(Base):
    __tablename__ = "debts"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    creditor = Column(String, nullable=False)
    amount = Column(Integer, nullable=False, default=0)
    description = Column(String, nullable=True)
    due_date = Column(DateTime, nullable=False)
    status = Column(Enum(DebtStatus), nullable=False, default=DebtStatus.PENDING)
    installment_count = Column(Integer, nullable=False, default=0)
    minimum_payment = Column(Integer, nullable=False, default=0)
    interest_rate = Column(Float, nullable=False, default=0.0, server_default="0.0")
    payment_frequency = Column(
        Enum(PaymentFrequency), nullable=True, default=PaymentFrequency.MONTHLY
    )
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    debt_payments = relationship("DebtPaymentModel", back_populates="debt")
    user = relationship("UserModel", back_populates="debts")

    @property
    def next_payment_date(self):
        if self.status == DebtStatus.PAID:
            return None

        if self.debt_payments:
            last_payment = sorted(
                self.debt_payments, key=lambda p: p.payment_date, reverse=True
            )[0]
            last_payment_date = last_payment.payment_date
            last_installment = last_payment.installment_number
        else:
            return self.due_date

        if last_installment >= self.installment_count:
            return None

        days_to_add = 30

        if self.payment_frequency is not None:
            if self.payment_frequency == PaymentFrequency.WEEKLY:
                days_to_add = 7
            elif self.payment_frequency == PaymentFrequency.BIWEEKLY:
                days_to_add = 15
            elif self.payment_frequency == PaymentFrequency.MONTHLY:
                days_to_add = 30
            elif self.payment_frequency == PaymentFrequency.QUARTERLY:
                days_to_add = 90
            elif self.payment_frequency == PaymentFrequency.YEARLY:
                days_to_add = 365

        next_date = last_payment_date + datetime.timedelta(days=days_to_add)
        return next_date

    @property
    def estimated_completion_date(self):
        if self.status == DebtStatus.PAID:
            if self.debt_payments:
                return sorted(
                    self.debt_payments, key=lambda p: p.payment_date, reverse=True
                )[0].payment_date
            return None

        if self.installment_count <= 0:
            return None

        installments_paid = 0
        if self.debt_payments:
            installments_paid = max(
                payment.installment_number for payment in self.debt_payments
            )

        remaining_installments = self.installment_count - installments_paid

        if remaining_installments <= 0:
            return None

        if self.debt_payments:
            last_payment = sorted(
                self.debt_payments, key=lambda p: p.payment_date, reverse=True
            )[0]
            start_date = last_payment.payment_date
        else:
            start_date = self.due_date

        days_per_payment = 30

        if self.payment_frequency is not None:
            if self.payment_frequency == PaymentFrequency.WEEKLY:
                days_per_payment = 7
            elif self.payment_frequency == PaymentFrequency.BIWEEKLY:
                days_per_payment = 15
            elif self.payment_frequency == PaymentFrequency.MONTHLY:
                days_per_payment = 30
            elif self.payment_frequency == PaymentFrequency.QUARTERLY:
                days_per_payment = 90
            elif self.payment_frequency == PaymentFrequency.YEARLY:
                days_per_payment = 365

        days_to_add = remaining_installments * days_per_payment
        completion_date = start_date + datetime.timedelta(days=days_to_add)

        return completion_date


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
    payment_date = Column(DateTime, nullable=False)
    amount_paid = Column(Integer, nullable=False, default=0)
    installment_number = Column(Integer, nullable=False, default=0)
    status = Column(Enum(DebtStatus), nullable=False, default=DebtStatus.PENDING)
    created_at = Column(DateTime, nullable=False)
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
