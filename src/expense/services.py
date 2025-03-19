from src.exceptions import NotFoundError
from .repository import ExpenseRepository
from .schemas import (
    ExpenseCreateSchema,
    ExpenseDetailSchema,
    ExpenseResponseSchema,
    ExpensesResponseSchema,
)


class ExpenseService:
    def __init__(self, expense_repository: ExpenseRepository):
        self.expense_repository = expense_repository

    async def get_expense_by_id(self, expense_id: str) -> dict:
        expense = await self.expense_repository.get_expense(expense_id)
        if not expense:
            raise NotFoundError("Income not found")
        return ExpenseResponseSchema(
            expense=ExpenseDetailSchema.model_validate(expense)
        )

    async def get_expenses(self) -> dict:
        expenses = await self.expense_repository.get_expenses()
        if not expenses:
            return ExpensesResponseSchema(expenses=[])
        return ExpensesResponseSchema(
            expenses=[
                ExpenseDetailSchema.model_validate(expense) for expense in expenses
            ]
        )

    async def create_expense(self, expense: ExpenseCreateSchema) -> dict:
        new_expense = await self.expense_repository.create_expense(expense)
        return ExpenseResponseSchema(
            expense=ExpenseDetailSchema.model_validate(new_expense)
        )
