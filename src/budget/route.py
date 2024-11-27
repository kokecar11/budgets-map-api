from fastapi import APIRouter, Depends, status
from src.user.dependencies import auth_dependency
from .service import BudgetService
from src.schemas import ResponseNotFound
from .schemas import BudgetResponseSchema, BudgetCreateSchema

BudgetRouter = APIRouter()


@BudgetRouter.get(
    "/budget/{budget_id}",
    response_model=BudgetResponseSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": ResponseNotFound}},
)
async def get_budget(
    budget_id: str,
    current_user: auth_dependency,
    budget_service: BudgetService = Depends(),
):
    budget = await budget_service.get_budget_by_id(budget_id)
    return budget


@BudgetRouter.get("/budgets")
async def get_budgets(
    current_user: auth_dependency,
    budget_service: BudgetService = Depends(),
):
    budgets = await budget_service.get_budgets()
    return budgets


@BudgetRouter.post("/budget")
async def create_budget(
    new_budget: BudgetCreateSchema,
    current_user: auth_dependency,
    budget_service: BudgetService = Depends(),
):
    budget = await budget_service.create_budget(new_budget, current_user.id)
    return budget
