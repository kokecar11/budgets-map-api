from fastapi import APIRouter, Depends, status
from src.user.dependencies import auth_dependency
from .dependencies import (
    DebtService,
    DebtPaymentService,
    get_debt_service,
    get_debt_payment_service,
)
from src.schemas import ResponseNotFound
from .schemas import (
    DebtResponseSchema,
    DebtCreateSchema,
    DebtPaymentCreateSchema,
    DebtPaymentResponseSchema,
)

DebtRouter = APIRouter()


@DebtRouter.get(
    "/debt/{debt_id}",
    response_model=DebtResponseSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": ResponseNotFound}},
)
async def get_debt(
    debt_id: str,
    current_user: auth_dependency,
    debt_service: DebtService = Depends(get_debt_service),
):
    return await debt_service.get_debt_by_id(debt_id)


@DebtRouter.get("/debts")
async def get_debts(
    current_user: auth_dependency,
    debt_service: DebtService = Depends(get_debt_service),
):
    return await debt_service.get_debts_by_user_id(current_user.id)


@DebtRouter.post("/debt")
async def create_debt(
    new_debt: DebtCreateSchema,
    current_user: auth_dependency,
    debt_service: DebtService = Depends(get_debt_service),
):
    return await debt_service.create_debt(new_debt, current_user.id)


@DebtRouter.post("/debt-payment")
async def create_debt_payment(
    new_debt_payment: DebtPaymentCreateSchema,
    current_user: auth_dependency,
    debt_payment_service: DebtPaymentService = Depends(get_debt_payment_service),
):
    return await debt_payment_service.create_debt_payment(
        new_debt_payment, current_user.id
    )


@DebtRouter.get(
    "/debt-payment/{debt_payment_id}",
    response_model=DebtPaymentResponseSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": ResponseNotFound}},
)
async def get_debt_payment(
    debt_payment_id: str,
    current_user: auth_dependency,
    debt_payment_service: DebtPaymentService = Depends(get_debt_payment_service),
):
    return await debt_payment_service.get_debt_payment_by_id(debt_payment_id)


@DebtRouter.get("/debt-payments/{debt_id}")
async def get_debt_payments(
    debt_id: str,
    current_user: auth_dependency,
    debt_payment_service: DebtPaymentService = Depends(get_debt_payment_service),
):
    return await debt_payment_service.get_debt_payments_by_debt_id(debt_id)
