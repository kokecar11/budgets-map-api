from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Any
from src.transaction.schemas import TransactionDetailSchema


class BudgetCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    type: Optional[str] = None

    class Config:
        from_attributes = True


class BudgetDetailSchema(BudgetCreateSchema):
    id: str
    type: Optional[str] = None
    total_spent: Optional[float] = None
    percent_spent: Optional[float] = None
    total_income: Optional[float] = None
    total_remaining: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BudgetTransactionCreateSchema(BaseModel):
    budget_id: str
    transaction_id: str
    amount: float

    class Config:
        from_attributes = True


class BudgetTransactionsDetailSchema(BudgetDetailSchema):
    transactions: List[TransactionDetailSchema] = []

    class Config:
        from_attributes = True


class BudgetUpdateSchema(BaseModel):
    name: Optional[str] = None
    total_amount: Optional[float] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True


class BudgetResponseSchema(BaseModel):
    budget: BudgetTransactionsDetailSchema

    class Config:
        from_attributes = True


class BudgetsResponseSchema(BaseModel):
    budgets: List[BudgetDetailSchema]

    class Config:
        from_attributes = True
