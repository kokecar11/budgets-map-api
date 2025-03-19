import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, event
from sqlalchemy.orm import relationship
from src.config import generate_uuid
from src.database import Base


class ExpenseModel(Base):
    __tablename__ = "expenses"
    __table_args__ = {"extend_existing": True}

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)
    amount = Column(Integer, nullable=False, default=0)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    transaction = relationship("TransactionModel", back_populates="expenses")


@event.listens_for(ExpenseModel, "before_update")
def receive_before_update(mapper, connection, target):
    target.updated_at = datetime.datetime.now(datetime.timezone.utc)


@event.listens_for(ExpenseModel, "before_insert")
def set_created_at(mapper, connection, target):
    target.created_at = datetime.datetime.now(datetime.timezone.utc)
