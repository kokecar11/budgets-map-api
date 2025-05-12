from fastapi import APIRouter, Depends
from .dependencies import get_ia_service
from src.user.dependencies import auth_dependency
from .service import AIService
from .schemas import PostHumanQueryPayload

AIRouter = APIRouter()


@AIRouter.post("/human-query")
async def get_human_query(
    payload: PostHumanQueryPayload,
    current_user: auth_dependency,
    ai_service: AIService = Depends(get_ia_service),
):
    answer = await ai_service.get_human_query(payload.human_query)
    return {"answer": answer}


@AIRouter.get("/recommendations/{budget_type}")
async def get_budget_recommendations(
    budget_type: str,
    current_user: auth_dependency,
    ai_service: AIService = Depends(get_ia_service),
):

    recommendations = await ai_service.generate_budget_recommendation(
        current_user.id, budget_type
    )
    return {"recommendations": recommendations}
