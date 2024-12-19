from src.dependecies import db_dependency
from .models import BudgetModel
from .schemas import BudgetCreateSchema


class BudgetRepository:

    def __init__(self, db: db_dependency):
        self.db = db

    async def get_budget(self, budget_id: str):
        return self.db.query(BudgetModel).filter(BudgetModel.id == budget_id).first()

    async def get_budgets(self):
        return self.db.query(BudgetModel).all()

    async def create_budget(self, budget: BudgetCreateSchema, user_id: str):
        new_budget = BudgetModel(
            user_id=user_id,
            name=budget.name,
            total_amount=budget.total_amount,
            description=budget.description,
        )
        self.db.add(new_budget)
        self.db.commit()
        self.db.refresh(new_budget)
        return new_budget
