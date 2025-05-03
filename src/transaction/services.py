from src.exceptions import BadRequestError, NotFoundError
from src.budget.services import BudgetService
from src.budget.schemas import BudgetTransactionCreateSchema
from src.income.services import IncomeService
from src.income.schemas import IncomeCreateSchema
from src.expense.services import ExpenseService
from src.expense.schemas import ExpenseCreateSchema
from .repository import TransactionRepository
from .schemas import (
    TransactionCreateSchema,
    TransactionDetailSchema,
    TransactionResponseSchema,
    TransactionsResponseSchema,
    SummaryResponseSchema,
    ValueSchema,
)


class TransactionService:
    def __init__(
        self,
        transaction_repository: TransactionRepository,
        budget_service: BudgetService,
        income_service: IncomeService,
        expense_service: ExpenseService,
    ):
        self.transaction_repository = transaction_repository
        self.budget_service = budget_service
        self.income_service = income_service
        self.expense_service = expense_service

    async def get_transaction_by_id(self, transaction_id: str) -> dict:
        transaction = await self.transaction_repository.get_transaction_by_id(
            transaction_id
        )
        if not transaction:
            raise NotFoundError("Transaction not found")
        return TransactionResponseSchema(
            transaction=TransactionDetailSchema.model_validate(transaction)
        )

    async def get_transactions_by_user_id(self, user_id: str) -> dict:
        transactions = await self.transaction_repository.get_transactions_by_user_id(
            user_id
        )
        if not transactions:
            return TransactionsResponseSchema(transactions=[])

        return TransactionsResponseSchema(
            transactions=[
                TransactionDetailSchema(
                    id=transaction.id,
                    created_at=transaction.created_at,
                    description=transaction.description,
                    category=transaction.category,
                    amount=amount,
                    type=transaction_type,
                )
                for transaction, amount, transaction_type in transactions
            ]
        )

    async def get_summary_by_user_id(self, user_id: str) -> dict:
        income, expense, debt = (
            await self.transaction_repository.get_summary_by_user_id(user_id)
        )
        if not income and not expense and not debt:
            return SummaryResponseSchema(
                income=ValueSchema(current_month=0, previous_month=0),
                expense=ValueSchema(current_month=0, previous_month=0),
                saving=ValueSchema(current_month=0, previous_month=0),
                debt=ValueSchema(current_month=0, previous_month=0),
            )

        current_month_income = income.current_month_income or 0
        previous_month_income = income.previous_month_income or 0
        growth_income = 0
        if previous_month_income != 0:
            growth_income = (
                (current_month_income - previous_month_income) / previous_month_income
            ) * 100
        elif current_month_income > 0:
            growth_income = 100

        current_month_expense = expense.current_month_expense or 0
        previous_month_expense = expense.previous_month_expense or 0
        growth_expense = 0
        if previous_month_expense != 0:
            growth_expense = (
                (current_month_expense - previous_month_expense)
                / previous_month_expense
            ) * 100
        elif current_month_expense > 0:
            growth_expense = 100

        current_month_debt = debt.current_month_debt or 0
        previous_month_debt = debt.previous_month_debt or 0
        growth_debt = 0
        if previous_month_debt != 0:
            growth_debt = (
                (current_month_debt - previous_month_debt) / previous_month_debt
            ) * 100
        elif current_month_debt > 0:
            growth_debt = 100

        current_month_saving = current_month_income - current_month_expense
        previous_month_saving = previous_month_income - previous_month_expense
        growth_saving = 0
        if previous_month_saving != 0:
            growth_saving = (
                (current_month_saving - previous_month_saving)
                / abs(previous_month_saving)
            ) * 100
        elif current_month_saving > 0:
            growth_saving = 100
        return SummaryResponseSchema(
            income=ValueSchema(
                current_month=current_month_income,
                previous_month=previous_month_income,
                growth=growth_income,
            ),
            expense=ValueSchema(
                current_month=current_month_expense,
                previous_month=previous_month_expense,
                growth=growth_expense,
            ),
            saving=ValueSchema(
                current_month=current_month_saving,
                previous_month=previous_month_saving,
                growth=growth_saving,
            ),
            debt=ValueSchema(
                current_month=current_month_debt,
                previous_month=previous_month_debt,
                growth=growth_debt,
            ),
        )

    async def create_transaction(
        self, transaction: TransactionCreateSchema, user_id: str
    ) -> dict:
        budgets_this_month = await self.budget_service.count_budgets_in_date_range(
            user_id
        )
        budgets = []
        if len(budgets_this_month) < 3:
            new_budgets = await self.budget_service.auto_create_budget(user_id)
            budgets = new_budgets["budgets"]
        else:
            budgets = budgets_this_month
        new_transaction = await self.transaction_repository.create_transaction(
            transaction
        )
        budget_transaction = [
            BudgetTransactionCreateSchema(
                budget_id=budget.id,
                transaction_id=new_transaction.id,
                amount=transaction.amount,
            )
            for budget in budgets
        ]
        for budget in budget_transaction:
            await self.budget_service.create_budget_transaction(budget)
        return TransactionResponseSchema(
            transaction=TransactionDetailSchema.model_validate(new_transaction)
        )

    async def create_transaction_v2(
        self, transaction: TransactionCreateSchema, user_id: str
    ) -> dict:
        budgets_this_month = await self.budget_service.count_budgets_in_date_range(
            user_id
        )
        budgets = []
        if len(budgets_this_month) < 3:
            new_budgets = await self.budget_service.auto_create_budget(user_id)
            budgets = new_budgets.budgets if hasattr(new_budgets, "budgets") else []
        else:
            budgets = budgets_this_month

        data_transaction = TransactionCreateSchema(
            amount=transaction.amount,
            description=transaction.description,
            category=transaction.category,
        )
        new_transaction = await self.transaction_repository.create_transaction(
            data_transaction
        )

        if transaction.type == "income":
            income = IncomeCreateSchema(
                transaction_id=new_transaction.id,
                amount=transaction.amount,
            )
            await self.income_service.create_income(income)
        elif transaction.type == "expense":
            expense = ExpenseCreateSchema(
                transaction_id=new_transaction.id,
                amount=transaction.amount,
                description=transaction.description,
            )

            await self.expense_service.create_expense(expense)
        else:
            raise BadRequestError("Invalid transaction type")

        budget_transaction = [
            BudgetTransactionCreateSchema(
                budget_id=budget.id,
                transaction_id=new_transaction.id,
                amount=transaction.amount,
            )
            for budget in budgets
        ]
        for budget in budget_transaction:
            await self.budget_service.create_budget_transaction(budget)

        return TransactionResponseSchema(
            transaction=TransactionDetailSchema.model_validate(new_transaction)
        )
