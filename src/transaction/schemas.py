from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


class TransactionCreateSchema(BaseModel):
    budget_id: str
    amount: float
    description: Optional[str] = None
    transaction_date: datetime
    category: str

    class Config:
        from_attributes = True


class TransactionDetailSchema(TransactionCreateSchema):
    id: str

    class Config:
        from_attributes = True


class TransactionResponseSchema(BaseModel):
    transaction: TransactionDetailSchema

    class Config:
        from_attributes = True


class TransactionsResponseSchema(BaseModel):
    transactions: List[TransactionDetailSchema]

    class Config:
        from_attributes = True
