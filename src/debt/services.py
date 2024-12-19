from fastapi import Depends, HTTPException, status
from src.transaction.repository import TransactionRepository
from src.transaction.schemas import TransactionCreateSchema
from .repository import DebtRepository, DebtPaymentRepository
from .schemas import (
    DebtDetailSchema,
    DebtPaymentDetailSchema,
    DebtCreateSchema,
    DebtPaymentCreateSchema,
)


class DebtService:
    def __init__(self, debt_repo: DebtRepository = Depends()):
        self.debt_repo = debt_repo

    async def get_debt_by_id(self, debt_id: str) -> dict:
        debt = await self.debt_repo.get_debt_by_id(debt_id)
        if not debt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Debt not found"
            )
        debt_payments = [
            DebtPaymentDetailSchema(
                id=payment.id,
                transaction_id=payment.transaction_id,
                amount_paid=payment.amount_paid,
                payment_date=payment.payment_date,
                status=payment.status,
                installment_number=payment.installment_number,
            )
            for payment in debt.debt_payments
        ]
        debt_dict = DebtDetailSchema.model_validate(debt).model_dump()
        debt_dict["debt_payments"] = debt_payments

        return {"debt": debt_dict}

    async def get_debts_by_user_id(self, user_id: str) -> dict:
        debts = await self.debt_repo.get_debts_by_user_id(user_id)
        if not debts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Debts not found"
            )
        return {
            "debts": [
                DebtDetailSchema.model_validate(debt).model_dump() for debt in debts
            ]
        }

    async def get_debts_by_user_id_and_status(self, user_id: str, status: str) -> dict:
        debts = await self.debt_repo.get_debts_by_user_id_and_status(user_id, status)
        if not debts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Debts not found"
            )
        return {
            "debts": [
                DebtDetailSchema.model_validate(debt).model_dump() for debt in debts
            ]
        }

    async def get_debts_by_user_id_and_due_date(
        self, user_id: str, due_date: str
    ) -> dict:
        debts = await self.debt_repo.get_debts_by_user_id_and_due_date(
            user_id, due_date
        )
        if not debts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Debts not found"
            )
        return {
            "debts": [
                DebtDetailSchema.model_validate(debt).model_dump() for debt in debts
            ]
        }

    async def create_debt(self, new_debt: DebtCreateSchema, user_id: str) -> dict:
        debt = await self.debt_repo.create_debt(new_debt, user_id)
        return debt


class DebtPaymentService:
    def __init__(
        self,
        debt_payment_repository: DebtPaymentRepository = Depends(),
        transaction_repository: TransactionRepository = Depends(),
    ):
        self.debt_payment_repository = debt_payment_repository
        self.transaction_repository = transaction_repository

    async def get_debt_payment_by_id(self, debt_payment_id: str) -> dict:
        debt_payment = await self.debt_payment_repository.get_debt_payment_by_id(
            debt_payment_id
        )
        if not debt_payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Debt Payment not found"
            )
        return {
            "debt_payment": DebtPaymentDetailSchema.model_validate(
                debt_payment
            ).model_dump()
        }

    async def get_debt_payments_by_debt_id(self, debt_id: str) -> dict:
        debt_payments = await self.debt_payment_repository.get_debt_payments_by_debt_id(
            debt_id
        )
        if not debt_payments:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Debt Payments not found"
            )
        return {
            "debt_payments": [
                DebtPaymentDetailSchema.model_validate(debt_payment).model_dump()
                for debt_payment in debt_payments
            ]
        }

    async def create_debt_payment(self, debt_payment: DebtPaymentCreateSchema) -> dict:
        transaction = TransactionCreateSchema(
            budget_id=debt_payment.budget_id,
            amount=debt_payment.amount_paid,
            transaction_date=debt_payment.payment_date,
            category="Debt Payment",
            description="Debt Payment",
        )
        transaction = await self.transaction_repository.create_transaction(transaction)
        debt_payment = await self.debt_payment_repository.create_debt_payment(
            debt_payment, transaction.id
        )
        return debt_payment
