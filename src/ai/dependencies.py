from src.dependencies import db_dependency
from .service import AIService, AIRepository
from src.transaction.dependencies import get_transaction_service


def get_ia_service(db: db_dependency) -> AIService:
    return AIService(AIRepository(db), get_transaction_service(db))
