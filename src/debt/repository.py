from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload
from src.settings import get_settings
from src.budget.models import BudgetTransactionModel, BudgetModel
from src.transaction.models import TransactionModel
from .models import DebtModel, DebtPaymentModel
from .schemas import DebtCreateSchema, DebtPaymentCreateSchema


class DebtRepository:

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    async def get_debt_by_id(self, debt_id: str) -> dict:
        return (
            self.db.query(DebtModel)
            .options(selectinload(DebtModel.debt_payments))
            .filter(DebtModel.id == debt_id)
            .first()
        )

    async def get_debts_by_user_id(self, user_id: str) -> dict:
        payment_count_subq = (
            self.db.query(
                DebtPaymentModel.debt_id,
                func.count(DebtPaymentModel.id).label("paid_installments"),
                func.sum(DebtPaymentModel.amount_paid).label("total_paid"),
            )
            .group_by(DebtPaymentModel.debt_id)
            .subquery()
        )

        query = (
            self.db.query(
                DebtModel,
                func.coalesce(payment_count_subq.c.paid_installments, 0).label(
                    "paid_installments"
                ),
                func.coalesce(payment_count_subq.c.total_paid, 0).label("total_paid"),
            )
            .outerjoin(
                payment_count_subq,
                DebtModel.id == payment_count_subq.c.debt_id,
            )
            .outerjoin(
                BudgetTransactionModel,
                DebtModel.id == BudgetTransactionModel.transaction_id,
            )
            .outerjoin(BudgetModel, BudgetTransactionModel.budget_id == BudgetModel.id)
            .filter(DebtModel.user_id == user_id)
            .distinct()
        )
        results = query.all()
        return results

    async def get_debts_by_user_id_and_status(self, user_id: str, status: str) -> dict:
        return (
            self.db.query(DebtModel)
            .filter(DebtModel.user_id == user_id, DebtModel.status == status)
            .all()
        )

    async def get_debts_by_user_id_and_due_date(
        self, user_id: str, due_date: str
    ) -> dict:
        return (
            self.db.query(DebtModel)
            .filter(DebtModel.user_id == user_id, DebtModel.due_date == due_date)
            .all()
        )

    async def create_debt(self, debt: DebtCreateSchema, user_id: str) -> dict:
        new_debt = DebtModel(
            user_id=user_id,
            creditor=debt.creditor,
            amount=debt.amount,
            description=debt.description,
            due_date=debt.due_date,
            status=debt.status,
            installment_count=debt.installment_count,
            minimum_payment=debt.minimum_payment,
        )
        self.db.add(new_debt)
        self.db.commit()
        self.db.refresh(new_debt)
        return new_debt

    async def update_debt(self, debt: DebtModel) -> dict:
        self.db.add(debt)
        self.db.commit()
        self.db.refresh(debt)
        return debt

    async def delete_debt(self, debt_id: str) -> dict:
        debt = self.db.query(DebtModel).filter(DebtModel.id == debt_id).first()
        self.db.delete(debt)
        self.db.commit()
        return debt


class DebtPaymentRepository:

    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    async def get_debt_payment_by_id(self, debt_payment_id: str) -> dict:
        return (
            self.db.query(DebtPaymentModel)
            .filter(DebtPaymentModel.id == debt_payment_id)
            .first()
        )

    async def get_debt_payments_by_debt_id(self, debt_id: str) -> dict:
        return (
            self.db.query(DebtPaymentModel)
            .filter(DebtPaymentModel.debt_id == debt_id)
            .all()
        )

    async def create_debt_payment(
        self, debt_payment: DebtPaymentCreateSchema, transaction_id: str
    ) -> dict:
        new_debt_payment = DebtPaymentModel(
            debt_id=debt_payment.debt_id,
            transaction_id=transaction_id,
            payment_date=debt_payment.payment_date,
            amount_paid=debt_payment.amount_paid,
            installment_number=debt_payment.installment_number,
            status=debt_payment.status,
        )
        self.db.add(new_debt_payment)
        self.db.commit()
        self.db.refresh(new_debt_payment)
        return new_debt_payment

    # async def update_debt_payment(self, debt_payment: DebtPaymentModel) -> dict:
    #     self.db.add(debt_payment)
    #     self.db.commit()
    #     self.db.refresh(debt_payment)
    #     return debt_payment

    # async def delete_debt_payment(self, debt_payment_id: str) -> dict:
    #     debt_payment = (
    #         self.db.query(DebtPaymentModel)
    #         .filter(DebtPaymentModel.id == debt_payment_id)
    #         .first()
    #     )
    #     self.db.delete(debt_payment)
    #     self.db.commit()
    #     return debt_payment
