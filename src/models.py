from sqlalchemy import MetaData
from src.debt.models import DebtModel, DebtPaymentModel
from src.budget.models import BudgetModel, BudgetTransactionModel
from src.user.models import UserModel
from src.transaction.models import TransactionModel
from src.income.models import IncomeModel
from src.saving.models import SavingModel
from src.expense.models import ExpenseModel

metadata = MetaData()

for model in [
    UserModel,
    BudgetModel,
    TransactionModel,
    BudgetTransactionModel,
    DebtModel,
    DebtPaymentModel,
    IncomeModel,
    SavingModel,
    ExpenseModel,
]:
    for table in model.metadata.tables.values():
        table.tometadata(metadata)
