from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from .models import DebtStatus


class DebtCreateSchema(BaseModel):
    creditor: str
    amount: float
    description: Optional[str]
    due_date: datetime
    status: DebtStatus
    installment_count: int
    minimum_payment: float

    class Config:
        from_attributes = True


class DebtPaymentDetailSchema(BaseModel):
    id: str
    transaction_id: str
    amount_paid: float
    payment_date: Optional[datetime]
    status: DebtStatus
    installment_number: int

    class Config:
        from_attributes = True


class DebtDetailSchema(BaseModel):
    id: str
    amount: float
    due_date: Optional[datetime]
    minimum_payment: float
    status: DebtStatus
    creditor: str
    description: Optional[str]
    installment_count: int
    debt_payments: Optional[List[DebtPaymentDetailSchema]]

    class Config:
        from_attributes = True


class DebtResponseSchema(BaseModel):
    debt: DebtDetailSchema

    class Config:
        from_attributes = True


class DebtPaymentCreateSchema(BaseModel):
    debt_id: str
    budget_id: str
    amount_paid: float
    payment_date: datetime
    installment_number: int
    amount_paid: float
    status: DebtStatus

    class Config:
        from_attributes = True


class DebtPaymentResponseSchema(BaseModel):
    debt_payment: DebtPaymentDetailSchema

    class Config:
        from_attributes = True
