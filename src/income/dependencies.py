from src.dependencies import db_dependency
from .services import IncomeService
from .repository import IncomeRepository


def get_income_service(db: db_dependency) -> IncomeService:
    return IncomeService(IncomeRepository(db))
