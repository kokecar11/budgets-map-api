from src.exceptions import NotFoundError
from .repository import IncomeRepository
from .schemas import (
    IncomeDetailSchema,
    IncomeResponseSchema,
    IncomesResponseSchema,
    IncomeCreateSchema,
)


class IncomeService:
    def __init__(self, income_repository: IncomeRepository):
        self.income_repository = income_repository

    async def get_income_by_id(self, income_id: str) -> dict:
        income = await self.income_repository.get_income(income_id)
        if not income:
            raise NotFoundError("Income not found")
        return IncomeResponseSchema(income=IncomeDetailSchema.model_validate(income))

    async def get_incomes(self) -> dict:
        incomes = await self.income_repository.get_incomes()
        if not incomes:
            return IncomesResponseSchema(incomes=[])
        return IncomesResponseSchema(
            incomes=[IncomeDetailSchema.model_validate(income) for income in incomes]
        )

    async def create_income(self, income: IncomeCreateSchema) -> dict:
        new_income = await self.income_repository.create_income(income)
        return IncomeResponseSchema(
            income=IncomeDetailSchema.model_validate(new_income)
        )
