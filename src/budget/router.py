from fastapi import APIRouter, Depends, status
from src.user.dependencies import auth_dependency
from .dependencies import BudgetService, get_budget_service
from src.schemas import ResponseNotFound
from .schemas import BudgetResponseSchema, BudgetCreateSchema, BudgetUpdateSchema

BudgetRouter = APIRouter()


@BudgetRouter.get(
    "/budget/{budget_id}",
    response_model=BudgetResponseSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": ResponseNotFound}},
)
async def get_budget(
    budget_id: str,
    current_user: auth_dependency,
    budget_service: BudgetService = Depends(get_budget_service),
):
    return await budget_service.get_budget_by_id(budget_id)


@BudgetRouter.get("/budgets")
async def get_budgets(
    current_user: auth_dependency,
    budget_service: BudgetService = Depends(get_budget_service),
):
    return await budget_service.get_budget_summary(current_user.id)


@BudgetRouter.post("/budget")
async def create_budget(
    new_budget: BudgetCreateSchema,
    current_user: auth_dependency,
    budget_service: BudgetService = Depends(get_budget_service),
):
    return await budget_service.create_budget(new_budget, current_user.id)


@BudgetRouter.post("/budget/generate-current-month")
async def create_budget(
    current_user: auth_dependency,
    budget_service: BudgetService = Depends(get_budget_service),
):
    return await budget_service.auto_create_budget(current_user.id)


@BudgetRouter.delete("/budget/{budget_id}")
async def delete_budget(
    budget_id: str,
    current_user: auth_dependency,
    budget_service: BudgetService = Depends(get_budget_service),
):
    await budget_service.delete_budget(budget_id)
    return {"message": "Budget deleted successfully"}


@BudgetRouter.put("/budget/{budget_id}")
async def update_budget(
    budget_id: str,
    updated_budget: BudgetUpdateSchema,
    current_user: auth_dependency,
    budget_service: BudgetService = Depends(get_budget_service),
):
    return await budget_service.update_budget(budget_id, updated_budget)
