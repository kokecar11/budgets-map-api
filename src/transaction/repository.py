from sqlalchemy import select, case, func, text
from sqlalchemy.orm import aliased, contains_eager, joinedload, Session
from src.budget.models import BudgetModel, BudgetTransactionModel
from src.debt.models import DebtPaymentModel, DebtModel
from src.income.models import IncomeModel
from src.saving.models import SavingModel
from src.expense.models import ExpenseModel
from .models import TransactionModel
from .schemas import TransactionCreateSchema


class TransactionRepository:
    def __init__(self, db: Session):
        self.db = db

    async def get_transaction_by_id(self, transaction_id: str):
        return (
            self.db.query(TransactionModel)
            .filter(TransactionModel.id == transaction_id)
            .first()
        )

    async def get_transactions_by_user_id(self, user_id: str):
        IncomeAlias = aliased(IncomeModel)
        SavingAlias = aliased(SavingModel)
        ExpenseAlias = aliased(ExpenseModel)
        DebtPaymentAlias = aliased(DebtPaymentModel)

        transaction_type_case = case(
            (IncomeAlias.id != None, "Income"),
            (SavingAlias.id != None, "Saving"),
            (ExpenseAlias.id != None, "Expense"),
            (DebtPaymentAlias.id != None, "DebtPayment"),
            else_="Otro",
        )

        query = (
            self.db.query(
                TransactionModel,
                BudgetTransactionModel.amount,
                transaction_type_case.label("transaction_type"),
            )
            .join(
                BudgetTransactionModel,
                TransactionModel.id == BudgetTransactionModel.transaction_id,
            )
            .join(BudgetModel, BudgetTransactionModel.budget_id == BudgetModel.id)
            .outerjoin(IncomeAlias, TransactionModel.id == IncomeAlias.transaction_id)
            .outerjoin(SavingAlias, TransactionModel.id == SavingAlias.transaction_id)
            .outerjoin(ExpenseAlias, TransactionModel.id == ExpenseAlias.transaction_id)
            .outerjoin(
                DebtPaymentAlias, TransactionModel.id == DebtPaymentAlias.transaction_id
            )
            .filter(BudgetModel.user_id == user_id)
            .options(contains_eager(TransactionModel.budget_transaction))
            .order_by(TransactionModel.created_at.desc())
        )

        return query.all()

    async def get_summary_by_user_id(self, user_id: str):
        current_month = func.date_trunc("month", func.now())

        previous_month = func.date_trunc(
            "month", func.now() - text("INTERVAL '1 month'")
        )
        income_query = (
            self.db.query(
                func.sum(
                    case(
                        (IncomeModel.created_at >= current_month, IncomeModel.amount),
                        else_=0,
                    )
                ).label("current_month_income"),
                func.sum(
                    case(
                        (
                            (IncomeModel.created_at >= previous_month)
                            & (IncomeModel.created_at < current_month),
                            IncomeModel.amount,
                        ),
                        else_=0,
                    )
                ).label("previous_month_income"),
            )
            .join(TransactionModel, IncomeModel.transaction_id == TransactionModel.id)
            .join(
                BudgetTransactionModel,
                TransactionModel.id == BudgetTransactionModel.transaction_id,
            )
            .join(BudgetModel, BudgetTransactionModel.budget_id == BudgetModel.id)
            .filter(BudgetModel.user_id == user_id, BudgetModel.type == "Balanced")
        )

        expense_query = (
            self.db.query(
                func.sum(
                    case(
                        (
                            ExpenseModel.created_at >= current_month,
                            ExpenseModel.amount,
                        ),
                        else_=0,
                    )
                ).label("current_month_expense"),
                func.sum(
                    case(
                        (
                            (ExpenseModel.created_at >= previous_month)
                            & (ExpenseModel.created_at < current_month),
                            ExpenseModel.amount,
                        ),
                        else_=0,
                    )
                ).label("previous_month_expense"),
            )
            .join(TransactionModel, ExpenseModel.transaction_id == TransactionModel.id)
            .join(
                BudgetTransactionModel,
                TransactionModel.id == BudgetTransactionModel.transaction_id,
            )
            .join(BudgetModel, BudgetTransactionModel.budget_id == BudgetModel.id)
            .filter(BudgetModel.user_id == user_id, BudgetModel.type == "Balanced")
        )

        debt_query = select(
            func.sum(
                case(
                    (
                        DebtModel.created_at >= current_month,
                        DebtModel.amount,
                    ),
                    else_=0,
                )
            ).label("current_month_debt"),
            func.sum(
                case(
                    (
                        (DebtModel.created_at >= previous_month)
                        & (DebtModel.created_at < current_month),
                        DebtModel.amount,
                    ),
                    else_=0,
                )
            ).label("previous_month_debt"),
        ).filter(DebtModel.user_id == user_id)

        income = income_query.first()
        expense = expense_query.first()
        debt = self.db.execute(debt_query).first()
        return income, expense, debt

    async def create_transaction(self, transaction: TransactionCreateSchema):
        new_transaction = TransactionModel(
            description=transaction.description,
            category=transaction.category,
        )
        self.db.add(new_transaction)
        self.db.commit()
        self.db.refresh(new_transaction)
        return new_transaction

    async def get_transactions_with_type(self, budget_id: str):
        DebtPaymentAlias = aliased(DebtPaymentModel)

        transaction_type_case = case(
            [
                # (IncomeAlias.id != None, "Ingreso"),
                # (InvestmentAlias.id != None, "Inversión"),
                # (SavingAlias.id != None, "Ahorro"),
                (DebtPaymentAlias.id != None, "Pago de Deuda"),
            ],
            else_="Otro",
        )

        query = (
            select(
                TransactionModel.id.label("transaction_id"),
                TransactionModel.amount,
                TransactionModel.description,
                TransactionModel.transaction_date,
                TransactionModel.budget_id,
                transaction_type_case.label("transaction_type"),
            )
            .outerjoin(
                DebtPaymentAlias, TransactionModel.id == DebtPaymentAlias.transaction_id
            )
            .filter(TransactionModel.budget_id == budget_id)
            .limit(5)
        )

        result = await self.db.execute(query)
        return result.fetchall()
