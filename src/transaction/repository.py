from src.dependecies import db_dependency
from src.budget.models import BudgetModel
from .models import TransactionModel
from .schemas import TransactionCreateSchema


class TransactionRepository:
    def __init__(self, db: db_dependency):
        self.db = db

    async def get_transaction_by_id(self, transaction_id: str):
        return (
            self.db.query(TransactionModel)
            .filter(TransactionModel.id == transaction_id)
            .first()
        )

    async def get_transactions_by_user_id(self, user_id: str):
        return (
            self.db.query(TransactionModel)
            .join(BudgetModel, BudgetModel.id == TransactionModel.budget_id)
            .filter(BudgetModel.user_id == user_id)
            .all()
        )

    async def create_transaction(self, transaction: TransactionCreateSchema):
        new_transaction = TransactionModel(
            budget_id=transaction.budget_id,
            amount=transaction.amount,
            description=transaction.description,
            transaction_date=transaction.transaction_date,
            category=transaction.category,
        )
        self.db.add(new_transaction)
        self.db.commit()
        self.db.refresh(new_transaction)
        return new_transaction
