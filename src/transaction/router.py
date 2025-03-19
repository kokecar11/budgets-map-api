from fastapi import APIRouter, Depends, status
from src.user.dependencies import auth_dependency
from .dependencies import TransactionService, get_transaction_service
from src.schemas import ResponseNotFound
from .schemas import TransactionResponseSchema, TransactionCreateSchema

TransactionRouter = APIRouter()


@TransactionRouter.get(
    "/transaction/{transaction_id}",
    response_model=TransactionResponseSchema,
    responses={status.HTTP_404_NOT_FOUND: {"model": ResponseNotFound}},
)
async def get_transaction(
    transaction_id: str,
    current_user: auth_dependency,
    transaction_service: TransactionService = Depends(get_transaction_service),
):
    return await transaction_service.get_transaction_by_id(transaction_id)


@TransactionRouter.get("/transactions")
async def get_transactions(
    current_user: auth_dependency,
    transaction_service: TransactionService = Depends(get_transaction_service),
):
    return await transaction_service.get_transactions_by_user_id(current_user.id)


@TransactionRouter.get("/summary")
async def get_summary(
    current_user: auth_dependency,
    transaction_service: TransactionService = Depends(get_transaction_service),
):
    return await transaction_service.get_summary_by_user_id(current_user.id)


@TransactionRouter.post("/transaction")
async def create_transaction(
    new_transaction: TransactionCreateSchema,
    current_user: auth_dependency,
    transaction_service: TransactionService = Depends(get_transaction_service),
):
    return await transaction_service.create_transaction_v2(
        new_transaction, current_user.id
    )
