from fastapi import APIRouter, Depends, status
from src.user.dependencies import auth_dependency
from .services import TransactionService
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
    transaction_service: TransactionService = Depends(),
):
    transaction = await transaction_service.get_transaction_by_id(transaction_id)
    return transaction


@TransactionRouter.get("/transactions")
async def get_transactions(
    current_user: auth_dependency,
    transaction_service: TransactionService = Depends(),
):
    transactions = await transaction_service.get_transactions_by_user_id(
        current_user.id
    )
    return transactions


@TransactionRouter.post("/transaction")
async def create_transaction(
    new_transaction: TransactionCreateSchema,
    current_user: auth_dependency,
    transaction_service: TransactionService = Depends(),
):
    transaction = await transaction_service.create_transaction(new_transaction)
    return transaction
