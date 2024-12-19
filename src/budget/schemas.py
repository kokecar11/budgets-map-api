from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


class BudgetCreateSchema(BaseModel):
    name: str
    total_amount: float
    description: Optional[str]

    class Config:
        from_attributes = True


class BudgetDetailSchema(BudgetCreateSchema):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BudgetResponseSchema(BaseModel):
    budget: BudgetDetailSchema

    class Config:
        from_attributes = True


class BudgetsResponseSchema(BaseModel):
    budgets: List[BudgetDetailSchema]

    class Config:
        from_attributes = True
