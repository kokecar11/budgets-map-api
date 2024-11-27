from fastapi import Depends, HTTPException, status
from .repository import BudgetRepository
from .schemas import (
    BudgetCreateSchema,
    BudgetDetailSchema,
    BudgetResponseSchema,
    BudgetsResponseSchema,
)


class BudgetService:
    def __init__(self, budget_repository: BudgetRepository = Depends()):
        self.budget_repository = budget_repository

    async def get_budget_by_id(self, budget_id: str) -> dict:
        budget = await self.budget_repository.get_budget(budget_id)
        if not budget:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found"
            )
        return {"budget": BudgetDetailSchema.model_validate(budget).model_dump()}

    async def get_budgets(self) -> dict:
        budgets = await self.budget_repository.get_budgets()
        return {
            "budgets": [
                BudgetDetailSchema.model_validate(budget).model_dump()
                for budget in budgets
            ]
        }

    async def create_budget(self, budget: BudgetCreateSchema, user_id: str) -> dict:
        new_budget = await self.budget_repository.create_budget(budget, user_id)
        return {"budget": BudgetDetailSchema.model_validate(new_budget).model_dump()}
