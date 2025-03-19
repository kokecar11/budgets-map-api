from src.dependencies import db_dependency
from src.budget.dependencies import BudgetService, BudgetRepository
from src.income.services import IncomeService, IncomeRepository
from src.expense.services import ExpenseService, ExpenseRepository
from .repository import TransactionRepository
from .services import TransactionService


def get_transaction_service(db: db_dependency) -> TransactionService:
    return TransactionService(
        TransactionRepository(db),
        BudgetService(BudgetRepository(db)),
        IncomeService(IncomeRepository(db)),
        ExpenseService(ExpenseRepository(db)),
    )
