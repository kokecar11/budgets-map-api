from src.dependencies import db_dependency
from .services import BudgetService
from .repository import BudgetRepository


def get_budget_service(db: db_dependency) -> BudgetService:
    return BudgetService(BudgetRepository(db))
