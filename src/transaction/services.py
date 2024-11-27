from fastapi import Depends, HTTPException, status
from .repository import TransactionRepository
from .schemas import (
    TransactionCreateSchema,
    TransactionDetailSchema,
)


class TransactionService:
    def __init__(self, transaction_repository: TransactionRepository = Depends()):
        self.transaction_repository = transaction_repository

    async def get_transaction_by_id(self, transaction_id: str) -> dict:
        transaction = await self.transaction_repository.get_transaction_by_id(
            transaction_id
        )
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
            )
        return {
            "transaction": TransactionDetailSchema.model_validate(
                transaction
            ).model_dump()
        }

    async def get_transactions_by_user_id(self, user_id: str) -> dict:
        transactions = await self.transaction_repository.get_transactions_by_user_id(
            user_id
        )
        if not transactions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Transactions not found"
            )
        return {
            "transactions": [
                TransactionDetailSchema.model_validate(transaction).model_dump()
                for transaction in transactions
            ]
        }

    async def create_transaction(self, transaction: TransactionCreateSchema) -> dict:
        new_transaction = await self.transaction_repository.create_transaction(
            transaction
        )
        return {
            "transaction": TransactionDetailSchema.model_validate(
                new_transaction
            ).model_dump()
        }
