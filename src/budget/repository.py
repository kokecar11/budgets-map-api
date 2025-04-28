import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select, case, func
from sqlalchemy.orm import aliased
from src.debt.models import DebtPaymentModel, DebtModel
from src.transaction.models import TransactionModel
from src.income.models import IncomeModel
from src.expense.models import ExpenseModel
from .models import BudgetModel, BudgetTransactionModel
from .schemas import (
    BudgetCreateSchema,
    BudgetUpdateSchema,
    BudgetTransactionCreateSchema,
)


class BudgetRepository:

    def __init__(self, db: Session):
        self.db = db

    async def budget_query(self):
        return self.db.query(BudgetModel).filter(BudgetModel.deleted_at.is_(None))

    async def get_budget(self, budget_id: str):
        query = await self.budget_query()
        return query.filter(BudgetModel.id == budget_id).first()

    async def get_budget_summary(self, user_id: str):
        now = datetime.datetime.now()
        start_of_month = datetime.datetime(now.year, now.month, 1)
        end_of_month = (
            datetime.datetime(now.year, now.month + 1, 1)
            if now.month < 12
            else datetime.datetime(now.year + 1, 1, 1)
        )
        IncomeAlias = aliased(IncomeModel)
        ExpenseAlias = aliased(ExpenseModel)
        DebtPaymentAlias = aliased(DebtPaymentModel)
        DebtAlias = aliased(DebtModel)

        transaction_type_case = case(
            (IncomeAlias.id != None, "Income"),
            (ExpenseAlias.id != None, "Expense"),
            (DebtPaymentAlias.id != None, "DebtPayment"),
            (DebtAlias.id != None, "Debt"),
            else_="Other",
        )

        subquery = select(BudgetModel.id).filter(
            BudgetModel.user_id == user_id,
            BudgetModel.created_at.between(start_of_month, end_of_month),
            BudgetModel.type.in_(["Balanced", "Saving", "Debt"]),
        )

        query = (
            select(
                BudgetModel.id,
                BudgetModel.type,
                BudgetModel.name,
                BudgetModel.description,
                BudgetModel.created_at,
                BudgetModel.updated_at,
                func.sum(
                    case(
                        (
                            transaction_type_case == "Income",
                            BudgetTransactionModel.amount,
                        ),
                        else_=0,
                    )
                ).label("total_income"),
                func.sum(
                    case(
                        (
                            transaction_type_case == "Expense",
                            BudgetTransactionModel.amount,
                        ),
                        else_=0,
                    )
                ).label("total_expense"),
                func.sum(
                    case(
                        (
                            transaction_type_case == "Saving",
                            BudgetTransactionModel.amount,
                        ),
                        else_=0,
                    )
                ).label("total_saving"),
                func.sum(
                    case(
                        (
                            transaction_type_case == "DebtPayment",
                            BudgetTransactionModel.amount,
                        ),
                        else_=0,
                    )
                ).label("total_debt_payment"),
            )
            .outerjoin(
                TransactionModel,
                BudgetTransactionModel.transaction_id == TransactionModel.id,
            )
            .outerjoin(IncomeAlias, TransactionModel.id == IncomeAlias.transaction_id)
            .outerjoin(ExpenseAlias, TransactionModel.id == ExpenseAlias.transaction_id)
            .outerjoin(
                DebtPaymentAlias, TransactionModel.id == DebtPaymentAlias.transaction_id
            )
            .outerjoin(DebtAlias, DebtAlias.id == DebtPaymentAlias.debt_id)
            .join(BudgetModel, BudgetTransactionModel.budget_id == BudgetModel.id)
            .filter(BudgetTransactionModel.budget_id.in_(subquery))
            .group_by(
                BudgetModel.id,
                BudgetModel.type,
                BudgetModel.name,
                BudgetModel.created_at,
                BudgetModel.description,
            )
        )
        return self.db.execute(query).fetchall()

    async def get_budget_with_transaction_types(self, budget_id: str):
        IncomeAlias = aliased(IncomeModel)
        # InvestmentAlias = aliased(InvestmentModel)
        # SavingAlias = aliased(SavingModel)
        DebtPaymentAlias = aliased(DebtPaymentModel)
        DebtAlias = aliased(DebtModel)

        transaction_type_case = case(
            (IncomeAlias.id != None, "Ingreso"),
            # (InvestmentAlias.id != None, "Inversión"),
            # (SavingAlias.id != None, "Ahorro"),
            (DebtPaymentAlias.id != None, "Pago de Deuda"),
            (DebtAlias.id != None, "Deuda"),
            else_="Otro",
        )

        query = (
            select(
                TransactionModel.id,
                TransactionModel.amount,
                TransactionModel.description,
                TransactionModel.created_at,
                TransactionModel.budget_id,
                transaction_type_case.label("category"),
            )
            .outerjoin(IncomeAlias, TransactionModel.id == IncomeAlias.transaction_id)
            # .outerjoin(
            #     InvestmentAlias, TransactionModel.id == InvestmentAlias.transaction_id
            # )
            .outerjoin(
                DebtPaymentAlias, TransactionModel.id == DebtPaymentAlias.transaction_id
            )
            .outerjoin(DebtAlias, DebtAlias.id == DebtPaymentAlias.debt_id)
            .filter(TransactionModel.budget_id == budget_id)
        )

        result = self.db.execute(query)
        transactions = result.fetchall()

        return [
            TransactionModel(
                id=transaction.id,
                amount=transaction.amount,
                description=transaction.description,
                created_at=transaction.created_at,
                budget_id=transaction.budget_id,
                category=transaction.category,
            )
            for transaction in transactions
        ]

    async def get_budgets(self):
        return self.db.query(BudgetModel).all()

    async def create_budget(self, budget: BudgetCreateSchema, user_id: str):
        new_budget = BudgetModel(
            user_id=user_id,
            name=budget.name,
            total_amount=budget.total_amount,
            description=budget.description,
        )
        self.db.add(new_budget)
        self.db.commit()
        self.db.refresh(new_budget)
        return new_budget

    async def create_budget_transanction(self, budget: BudgetTransactionCreateSchema):
        new_budget_transaction = BudgetTransactionModel(
            budget_id=budget.budget_id,
            transaction_id=budget.transaction_id,
            amount=budget.amount,
        )
        self.db.add(new_budget_transaction)
        self.db.commit()
        self.db.refresh(new_budget_transaction)
        return new_budget_transaction

    async def count_budgets_in_date_range(
        self, start_date: datetime.datetime, end_date: datetime.datetime, user_id: str
    ):
        query = await self.budget_query()
        return query.filter(
            BudgetModel.user_id == user_id,
            BudgetModel.created_at.between(start_date, end_date),
            BudgetModel.type.in_(["Balanced", "Saving", "Debt"]),
        ).all()

    async def delete_budget(self, budget_id: str):
        self.db.query(BudgetModel).filter(BudgetModel.id == budget_id).update(
            {"deleted_at": datetime.datetime.now(datetime.timezone.utc)}
        )
        self.db.commit()
        return {"message": "Budget deleted successfully"}

    async def update_budget(self, budget_id: str, update_data: dict):
        self.db.query(BudgetModel).filter(BudgetModel.id == budget_id).update(
            update_data
        )
        self.db.commit()
        return await self.get_budget(budget_id)

    async def bulk_budgets(self, budgets: list, user_id: str):
        new_budgets = [
            BudgetModel(
                # TODO: Revisar si es necesario el id
                user_id=user_id,
                name=budget.name,
                description=budget.description,
                type=budget.type,
            )
            for budget in budgets
        ]
        self.db.bulk_save_objects(new_budgets)
        self.db.commit()
        return new_budgets
