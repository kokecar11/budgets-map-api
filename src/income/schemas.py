from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional


class IncomeCreateSchema(BaseModel):
    transaction_id: str
    amount: float
    source: Optional[str] = None

    class Config:
        from_attributes = True


class IncomeDetailSchema(IncomeCreateSchema):
    id: str
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class IncomeResponseSchema(BaseModel):
    income: IncomeDetailSchema

    class Config:
        from_attributes = True


class IncomesResponseSchema(BaseModel):
    incomes: List[IncomeDetailSchema]

    class Config:
        from_attributes = True
