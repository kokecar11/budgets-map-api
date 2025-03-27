from src.dependencies import db_dependency
from src.transaction.dependencies import get_transaction_service
from .repository import DebtRepository, DebtPaymentRepository
from .services import DebtService, DebtPaymentService


def get_debt_service(db: db_dependency) -> DebtService:
    return DebtService(DebtRepository(db))


def get_debt_payment_service(db: db_dependency) -> DebtPaymentService:
    return DebtPaymentService(
        DebtPaymentRepository(db),
        get_transaction_service(db),
    )
