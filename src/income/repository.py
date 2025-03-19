import datetime
from sqlalchemy.orm import Session
from .models import IncomeModel
from .schemas import IncomeCreateSchema, IncomeDetailSchema


class IncomeRepository:
    def __init__(self, db: Session):
        self.db = db

    async def income_query(self):
        return self.db.query(IncomeModel).filter(IncomeModel.deleted_at.is_(None))

    async def get_incomes(self):
        query = await self.income_query()
        return query.all()

    async def get_income_by_id(self, income_id: str):
        query = await self.income_query()
        return query.filter(IncomeModel.id == income_id).first()

    async def create_income(self, income: IncomeCreateSchema) -> dict:
        new_income = IncomeModel(
            transaction_id=income.transaction_id,
            amount=income.amount,
            source=income.source,
        )
        self.db.add(new_income)
        self.db.commit()
        self.db.refresh(new_income)
        return new_income

    async def delete_income(self, income_id: str):
        self.db.query(IncomeModel).filter(IncomeModel.id == income_id).update(
            {"deleted_at": datetime.datetime.now(datetime.timezone.utc)}
        )
        self.db.commit()
        return {"message": "Income deleted successfully"}

    async def update_income(self, income_id: str, update_data: dict) -> dict:
        self.db.query(IncomeModel).filter(IncomeModel.id == income_id).update(
            update_data
        )
        self.db.commit()
        return await self.get_income_by_id(income_id)
