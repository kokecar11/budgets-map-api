from src.exceptions import NotFoundError
from src.transaction.services import TransactionService
from src.transaction.schemas import TransactionCreateSchema
from .repository import DebtRepository, DebtPaymentRepository
from .schemas import (
    DebtDetailSchema,
    DebtPaymentDetailSchema,
    DebtCreateSchema,
    DebtPaymentCreateSchema,
    DebtResponseSchema,
    DebtsResponseSchema,
    DebtPaymentResponseSchema,
    DebtPaymentsResponseSchema,
)


class DebtService:
    def __init__(self, debt_repository: DebtRepository):
        self.debt_repository = debt_repository

    async def get_debt_by_id(self, debt_id: str) -> dict:
        debt = await self.debt_repository.get_debt_by_id(debt_id)
        if not debt:
            raise NotFoundError("Debt not found")
        return DebtResponseSchema(debt=DebtDetailSchema.model_validate(debt))

    async def get_debts_by_user_id(self, user_id: str) -> dict:
        debts = await self.debt_repository.get_debts_by_user_id(user_id)
        if not debts:
            return DebtsResponseSchema(debts=[])
        return DebtsResponseSchema(
            debts=[
                DebtDetailSchema(
                    id=debt.id,
                    amount=debt.amount,
                    due_date=debt.due_date,
                    minimum_payment=debt.minimum_payment,
                    status=debt.status,
                    creditor=debt.creditor,
                    description=debt.description,
                    installment_count=debt.installment_count,
                    total_paid=total_paid,
                    paid_installments=paid_installments,
                    next_payment_date=debt.next_payment_date,
                    estimated_completion_date=debt.estimated_completion_date,
                    interest_rate=debt.interest_rate,
                    payment_frequency=debt.payment_frequency,
                    debt_payments=[],
                )
                for debt, paid_installments, total_paid in debts
            ]
        )

    async def get_debts_by_user_id_and_status(self, user_id: str, status: str) -> dict:
        debts = await self.debt_repository.get_debts_by_user_id_and_status(
            user_id, status
        )
        if not debts:
            return DebtsResponseSchema(debts=[])
        return DebtsResponseSchema(
            debts=[DebtDetailSchema.model_validate(debt) for debt in debts]
        )

    async def get_debts_by_user_id_and_due_date(
        self, user_id: str, due_date: str
    ) -> dict:
        debts = await self.debt_repository.get_debts_by_user_id_and_due_date(
            user_id, due_date
        )
        if not debts:
            return DebtsResponseSchema(debts=[])
        return DebtsResponseSchema(
            debts=[DebtDetailSchema.model_validate(debt) for debt in debts]
        )

    async def create_debt(self, new_debt: DebtCreateSchema, user_id: str) -> dict:
        debt = await self.debt_repository.create_debt(new_debt, user_id)
        return debt


class DebtPaymentService:
    def __init__(
        self,
        debt_payment_repository: DebtPaymentRepository,
        transaction_service: TransactionService,
    ):
        self.debt_payment_repository = debt_payment_repository
        self.transaction_service = transaction_service

    async def get_debt_payment_by_id(self, debt_payment_id: str) -> dict:
        debt_payment = await self.debt_payment_repository.get_debt_payment_by_id(
            debt_payment_id
        )
        if not debt_payment:
            raise NotFoundError("Debt Payment not found")
        return DebtPaymentResponseSchema(
            debt_payment=DebtPaymentDetailSchema.model_validate(debt_payment)
        )

    async def get_debt_payments_by_debt_id(self, debt_id: str) -> dict:
        debt_payments = await self.debt_payment_repository.get_debt_payments_by_debt_id(
            debt_id
        )
        if not debt_payments:
            return DebtPaymentsResponseSchema(debt_payments=[])
        return DebtPaymentsResponseSchema(
            debt_payments=[
                DebtPaymentDetailSchema.model_validate(debt_payment)
                for debt_payment in debt_payments
            ]
        )

    async def create_debt_payment(
        self, debt_payment: DebtPaymentCreateSchema, user_id: str
    ) -> dict:
        transaction = TransactionCreateSchema(
            amount=debt_payment.amount_paid,
            category="Debt Payment",
            description=debt_payment.description,
            type="debt",
        )
        new_transaction = await self.transaction_service.create_transaction(
            transaction, user_id
        )
        debt_payment = await self.debt_payment_repository.create_debt_payment(
            debt_payment, new_transaction.transaction.id
        )
        return DebtPaymentResponseSchema(
            debt_payment=DebtPaymentDetailSchema.model_validate(debt_payment)
        )
