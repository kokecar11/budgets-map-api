from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.settings import Settings
from src.ai.route import AIRouter
from src.debt.route import DebtRouter
from src.transaction.route import TransactionRouter
from src.budget.route import BudgetRouter
from src.user.route import AuthRouter

settings = Settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
)

origins = settings.ALLOWED_HOSTS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(AuthRouter, prefix="/api/v1", tags=["Authentication"])
app.include_router(AIRouter, prefix="/api/v1", tags=["IA"])
app.include_router(DebtRouter, prefix="/api/v1", tags=["Debts"])
app.include_router(BudgetRouter, prefix="/api/v1", tags=["Budgets"])
app.include_router(TransactionRouter, prefix="/api/v1", tags=["Transactions"])