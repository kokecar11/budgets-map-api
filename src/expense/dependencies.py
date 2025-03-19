from src.dependencies import db_dependency
from .repository import ExpenseRepository
from .services import ExpenseService


def get_expense_repository(db: db_dependency) -> ExpenseRepository:
    return ExpenseService(ExpenseRepository(db))
