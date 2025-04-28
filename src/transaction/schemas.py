from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


class TransactionCreateSchema(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    category: str
    type: Optional[str] = None

    class Config:
        from_attributes = True


class TransactionDetailSchema(TransactionCreateSchema):
    id: str
    created_at: datetime
    description: Optional[str] = None
    category: str

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


class ValueSchema(BaseModel):
    current_month: float
    previous_month: float
    growth: Optional[float] = None

    class Config:
        from_attributes = True


class SummaryResponseSchema(BaseModel):
    income: ValueSchema
    expense: Optional[ValueSchema]
    saving: Optional[ValueSchema]
    debt: Optional[ValueSchema]

    class Config:
        from_attributes = True
