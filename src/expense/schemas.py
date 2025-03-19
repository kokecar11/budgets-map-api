from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


class ExpenseCreateSchema(BaseModel):
    transaction_id: str
    amount: float
    description: Optional[str] = None

    class Config:
        from_attributes = True


class ExpenseDetailSchema(ExpenseCreateSchema):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ExpenseResponseSchema(BaseModel):
    expense: ExpenseDetailSchema

    class Config:
        from_attributes = True


class ExpensesResponseSchema(BaseModel):
    expenses: List[ExpenseDetailSchema]

    class Config:
        from_attributes = True
