import datetime
from src.exceptions import NotFoundError, BadRequestError
from .repository import BudgetRepository
from .schemas import (
    BudgetCreateSchema,
    BudgetDetailSchema,
    BudgetResponseSchema,
    BudgetsResponseSchema,
    BudgetUpdateSchema,
    BudgetTransactionsDetailSchema,
    BudgetTransactionCreateSchema,
)


class BudgetService:
    def __init__(self, budget_repository: BudgetRepository):
        self.budget_repository = budget_repository
        # self.scheduler = BackgroundScheduler()
        # self.jobs = {}

    async def get_budget_by_id(self, budget_id: str) -> dict:
        budget = await self.budget_repository.get_budget(budget_id)
        buget_transactions = (
            await self.budget_repository.get_budget_with_transaction_types(budget_id)
        )
        if not budget:
            raise NotFoundError("Budget not found")
        budget.transactions = buget_transactions
        total_spent = sum(transaction.amount for transaction in budget.transactions)
        percent_spent = (total_spent / budget.total_amount) * 100
        budget.total_spent = total_spent
        budget.percent_spent = percent_spent
        return BudgetResponseSchema(
            budget=BudgetTransactionsDetailSchema.model_validate(budget)
        )

    async def get_budgets(self) -> dict:
        budgets = await self.budget_repository.get_budgets()
        if not budgets:
            return BudgetsResponseSchema(budgets=[])
        for b in budgets:
            print(b)
        return BudgetsResponseSchema(
            budgets=[BudgetDetailSchema.model_validate(budget) for budget in budgets]
        )

    async def get_budget_summary(self, user_id: str) -> dict:
        budgets = await self.budget_repository.get_budget_summary(user_id)
        if not budgets:
            return BudgetsResponseSchema(budgets=[])
        return BudgetsResponseSchema(
            budgets=[
                BudgetDetailSchema(
                    id=budget.id,
                    name=budget.name,
                    description=budget.description,
                    type=budget.type,
                    total_income=budget.total_income,
                    total_spent=(budget.total_expense + budget.total_debt_payment),
                    total_remaining=(
                        budget.total_income
                        - budget.total_expense
                        - budget.total_debt_payment
                    ),
                    percent_spent=((budget.total_expense) / budget.total_income) * 100,
                    created_at=budget.created_at,
                    updated_at=budget.updated_at,
                )
                for budget in budgets
            ]
        )

    async def count_budgets_in_date_range(self, user_id: str) -> int:
        now = datetime.datetime.now()
        start_of_month = datetime.datetime(now.year, now.month, 1)
        end_of_month = (
            datetime.datetime(now.year, now.month + 1, 1)
            if now.month < 12
            else datetime.datetime(now.year + 1, 1, 1)
        )
        return await self.budget_repository.count_budgets_in_date_range(
            start_of_month, end_of_month, user_id
        )

    async def create_budget(self, budget: BudgetCreateSchema, user_id: str) -> dict:
        new_budget = await self.budget_repository.create_budget(budget, user_id)
        return BudgetResponseSchema(
            budget=BudgetDetailSchema.model_validate(new_budget)
        )

    async def auto_create_budget(self, user_id: str) -> dict:
        # next_month = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime(
        #     "%B %Y"
        # )
        current_month = datetime.datetime.now().strftime("%B %Y")
        type_budgets = ["Balanced", "Saving", "Debt"]
        data_budgets = [
            BudgetCreateSchema(
                name="Budget for " + current_month,
                type=type,
                description=f"{current_month} Spending Summary",
            )
            for type in type_budgets
        ]
        new_budgets = await self.budget_repository.bulk_budgets(data_budgets, user_id)
        return BudgetsResponseSchema(
            budgets=[
                BudgetDetailSchema.model_validate(budget) for budget in new_budgets
            ]
        )

    async def create_budget_transaction(
        self, budget_transaction: BudgetTransactionCreateSchema
    ) -> dict:
        new_budget_transaction = (
            await self.budget_repository.create_budget_transanction(budget_transaction)
        )
        return True  # TODO: Revisar que devolver

    async def delete_budget(self, budget_id: str) -> None:
        await self.budget_repository.delete_budget(budget_id)

    async def update_budget(self, budget_id: str, budget: BudgetUpdateSchema) -> dict:
        update_data = budget.model_dump(exclude_unset=True)
        updated_budget = await self.budget_repository.update_budget(
            budget_id, update_data
        )
        total_spent = sum(
            transaction.amount for transaction in updated_budget.transactions
        )
        percent_spent = (total_spent / updated_budget.total_amount) * 100
        updated_budget.total_spent = total_spent
        updated_budget.percent_spent = percent_spent
        return BudgetResponseSchema(
            budget=BudgetTransactionsDetailSchema.model_validate(updated_budget)
        )

    # TODO: Implementar la creación automática de presupuestos
    # from apscheduler.schedulers.background import BackgroundScheduler
    # def start_auto_create_budget(self, user_id: str):
    #     if user_id not in self.jobs:
    #         job = self.scheduler.add_job(self.create_next_month_budget, 'cron', month='1-12', day=1, hour=0, minute=0, args=[user_id])
    #         self.jobs[user_id] = job
    #         self.scheduler.start()
    #         # Actualiza el estado en la base de datos
    #         user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
    #         user.auto_create_budget = True
    #         self.db.commit()

    # def stop_auto_create_budget(self, user_id: str):
    #     if user_id in self.jobs:
    #         self.jobs[user_id].remove()
    #         del self.jobs[user_id]
    #         # Actualiza el estado en la base de datos
    #         user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
    #         user.auto_create_budget = False
    #         self.db.commit()
