from sqlalchemy.orm import Session
from .models import ExpenseModel
from .schemas import ExpenseCreateSchema


class ExpenseRepository:
    def __init__(self, db: Session):
        self.db = db

    async def expense_query(self):
        return self.db.query(ExpenseModel).filter(ExpenseModel.deleted_at.is_(None))

    async def create_expense(self, expense: ExpenseCreateSchema) -> dict:
        new_expense = ExpenseModel(
            transaction_id=expense.transaction_id,
            amount=expense.amount,
            description=expense.description,  # TODO: Puede que no lo use
        )
        self.db.add(new_expense)
        self.db.commit()
        self.db.refresh(new_expense)
        return new_expense
