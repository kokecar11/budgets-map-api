from sqlalchemy import MetaData
from src.debt.models import DebtModel, DebtPaymentModel
from src.budget.models import BudgetModel
from src.user.models import UserModel
from src.transaction.models import TransactionModel

metadata = MetaData()

for model in [
    UserModel,
    BudgetModel,
    TransactionModel,
    DebtModel,
    DebtPaymentModel,
]:
    for table in model.metadata.tables.values():
        table.tometadata(metadata)
