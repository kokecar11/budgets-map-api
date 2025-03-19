from fastapi import APIRouter, Depends, status
from src.user.dependencies import auth_dependency
from .dependencies import IncomeService, get_income_service
from src.schemas import ResponseNotFound
from .schemas import IncomeResponseSchema, IncomeCreateSchema


IncomeRouter = APIRouter()


@IncomeRouter.get(
    "/income/{budget_id}",
    response_model=IncomeResponseSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": ResponseNotFound}},
)
async def get_income(
    income_id: str,
    current_user: auth_dependency,
    income_service: IncomeService = Depends(get_income_service),
):
    return await income_service.get_income_by_id(income_id)


@IncomeRouter.get("/incomes")
async def get_incomes(
    current_user: auth_dependency,
    income_service: IncomeService = Depends(get_income_service),
):
    return await income_service.get_incomes()


@IncomeRouter.post("/income")
async def create_income(
    income: IncomeCreateSchema,
    current_user: auth_dependency,
    income_service: IncomeService = Depends(get_income_service),
):
    return await income_service.create_income(income)
