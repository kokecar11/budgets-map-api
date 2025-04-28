from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from .models import DebtStatus, PaymentFrequency


class DebtCreateSchema(BaseModel):
    creditor: str
    amount: float
    description: Optional[str]
    due_date: datetime
    status: DebtStatus
    installment_count: int
    interest_rate: float
    payment_frequency: Optional[PaymentFrequency] = PaymentFrequency.MONTHLY

    class Config:
        from_attributes = True


class DebtPaymentDetailSchema(BaseModel):
    id: str
    transaction_id: str
    amount_paid: float
    payment_date: Optional[datetime]
    status: DebtStatus
    installment_number: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

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
    total_paid: Optional[float]
    paid_installments: Optional[int]
    next_payment_date: Optional[datetime]
    estimated_completion_date: Optional[datetime]
    interest_rate: float
    payment_frequency: Optional[PaymentFrequency]
    debt_payments: Optional[List[DebtPaymentDetailSchema]]

    class Config:
        from_attributes = True


class DebtResponseSchema(BaseModel):
    debt: DebtDetailSchema

    class Config:
        from_attributes = True


class DebtsResponseSchema(BaseModel):
    debts: List[DebtDetailSchema]

    class Config:
        from_attributes = True


class DebtPaymentCreateSchema(BaseModel):
    debt_id: str
    payment_date: datetime
    amount_paid: float
    installment_number: int
    description: Optional[str] = None
    status: DebtStatus

    class Config:
        from_attributes = True


class DebtPaymentResponseSchema(BaseModel):
    debt_payment: DebtPaymentDetailSchema

    class Config:
        from_attributes = True


class DebtPaymentsResponseSchema(BaseModel):
    debt_payments: List[DebtPaymentDetailSchema]

    class Config:
        from_attributes = True
